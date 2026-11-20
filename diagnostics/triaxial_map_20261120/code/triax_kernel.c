/* triax_kernel.c  --  DIAGNOSTIC_ONLY / NOT_EVIDENCE  (non-interval floating point)
 *
 * Cone-volume-weighted radial-normal angle functional on the ellipsoid K = L(B^3),
 * L = diag(l1,l2,l3), written on the reference ball:
 *     q in B^3, xi in S^2,
 *     k = 1 - q.xi,  D = |L(xi-q)|,  B = |L^{-1} xi|^2,  gamma = k/(D sqrt(B)) = cos(alpha),
 *     E(q) = < k alpha^2 >                       (<.> = mean over S^2)
 *     E_i  = < xi_i J - l_i sqrt(B) u_i K >,     u = L(xi-q)/D
 *     E_ij = < -xi_i xi_j A/k + (xi_i l_j u_j + l_i u_i xi_j) A/D
 *              - l_i l_j u_i u_j sqrt(B) (gamma A + K)/D + delta_ij l_i^2 sqrt(B) K/D >
 *     J = -alpha^2 + 2 alpha cot(alpha),  K = 2 alpha cos^2(alpha)/sin(alpha),
 *     A = gamma dJ/dgamma = dK/dgamma = 2 cot(alpha) (alpha + alpha/sin^2(alpha) - cot(alpha)).
 *
 * Quadrature ("log-chord" coordinates about the axis qhat = q/|q|):
 *     xi = q + rho*omega,  rho = sqrt(1-|q|^2) e^tau,  tau in [-T,T], T = atanh|q|,
 *     mu = -qhat.omega = sqrt(1-|q|^2) sinh(tau)/|q|,
 *     dsigma(xi) = rho^2 dtau dphi / |q|,   omega.xi = w = sqrt(1-|q|^2) cosh(tau).
 *   Gauss-Legendre in tau, trapezoid in phi.  The integrand is analytic in tau for every
 *   |q|<1 (the near-singularity at xi ~ qhat is resolved by tau = log rho).
 * Boundary |q| = 1 (trace of E and of the full gradient):
 *     rho = 2 mu, mu = cos(theta), theta in [0,pi/2],  dsigma = 4 mu dmu dphi,  w = mu.
 *   Gauss-Legendre in theta, trapezoid in phi.  (Hessian is not returned on the boundary.)
 *
 * out[10] = E, E_1, E_2, E_3, E_11, E_22, E_33, E_12, E_13, E_23
 */
#include <math.h>
#include <stddef.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static inline void kernel_funcs(double al, double s, double c, double *J, double *K, double *A)
{
    if (al < 0.15) {
        double x = al * al;
        *J = 2.0 + x*(-5.0/3 + x*(-2.0/45 + x*(-4.0/945 + x*(-2.0/4725 + x*(-4.0/93555
             + x*(-2764.0/638512875 + x*(-8.0/18243225)))))));
        *K = 2.0 + x*(-5.0/3 + x*(67.0/180 + x*(-19.0/1512 + x*(247.0/302400 + x*(89.0/2395008
             + x*(1430857.0/326918592000.0 + x*(1637.0/3736212480.0)))))));
        *A = 10.0/3 + x*(-14.0/15 + x*(-34.0/315 + x*(-76.0/4725 + x*(-122.0/51975
             + x*(-69908.0/212837625 + x*(-28244.0/638512875 + x*(-62632.0/10854718875.0)))))));
    } else {
        double cot = c / s;
        *J = -al*al + 2.0*al*cot;
        *K = 2.0*al*c*c/s;
        *A = 2.0*cot*(al + al/(s*s) - cot);
    }
}

/* one item: l[3], q[3]; gauss nodes x[nt], weights wt[nt] on [-1,1]; nphi trapezoid nodes */
static void eval_one(const double *l, const double *q, int nt, const double *x, const double *wt,
                     int nphi, const double *cph, const double *sph, double *out)
{
    double acc[10];
    for (int i = 0; i < 10; i++) acc[i] = 0.0;
    double r2 = q[0]*q[0] + q[1]*q[1] + q[2]*q[2];
    double r = sqrt(r2);
    double qh[3], e1[3], e2[3];
    if (r < 1e-12) { qh[0] = 0; qh[1] = 0; qh[2] = 1; }
    else { qh[0] = q[0]/r; qh[1] = q[1]/r; qh[2] = q[2]/r; }
    /* orthonormal frame */
    {
        int m = 0; double am = fabs(qh[0]);
        if (fabs(qh[1]) < am) { m = 1; am = fabs(qh[1]); }
        if (fabs(qh[2]) < am) { m = 2; }
        double t[3] = {0, 0, 0}; t[m] = 1.0;
        double d = t[0]*qh[0] + t[1]*qh[1] + t[2]*qh[2];
        for (int i = 0; i < 3; i++) e1[i] = t[i] - d*qh[i];
        double n = sqrt(e1[0]*e1[0] + e1[1]*e1[1] + e1[2]*e1[2]);
        for (int i = 0; i < 3; i++) e1[i] /= n;
        e2[0] = qh[1]*e1[2] - qh[2]*e1[1];
        e2[1] = qh[2]*e1[0] - qh[0]*e1[2];
        e2[2] = qh[0]*e1[1] - qh[1]*e1[0];
    }
    int boundary = (r2 >= 1.0 - 1e-13);
    double eps = 1.0 - r2, se = boundary ? 0.0 : sqrt(eps);
    double T = boundary ? 0.0 : atanh(r);
    double li[3] = {1.0/l[0], 1.0/l[1], 1.0/l[2]};

    for (int it = 0; it < nt; it++) {
        double rho, w, mu, wgt;
        if (boundary) {
            double th = 0.25*M_PI*(x[it] + 1.0);
            mu = cos(th); rho = 2.0*mu; w = mu;
            /* dsigma/(4pi) = 4 mu dmu dphi/(4pi) = mu sin(th) dth dphi / pi */
            wgt = wt[it]*0.25*M_PI * mu*sin(th)/M_PI * (2.0*M_PI/nphi);
        } else if (r < 1e-9) {
            mu = x[it]; rho = 1.0 + r*mu; w = 1.0;
            wgt = wt[it] * rho*rho/(2.0*nphi);
        } else {
            double tau = T*x[it];
            double et = exp(tau);
            rho = se*et; w = se*cosh(tau); mu = se*sinh(tau)/r;
            wgt = wt[it]*(T/r) * rho*rho/(2.0*nphi);
        }
        if (mu > 1.0) mu = 1.0;
        if (mu < -1.0) mu = -1.0;
        double st = sqrt((1.0 - mu)*(1.0 + mu));
        for (int ip = 0; ip < nphi; ip++) {
            double om[3], xi[3], d[3], n[3];
            for (int i = 0; i < 3; i++) {
                om[i] = -mu*qh[i] + st*(cph[ip]*e1[i] + sph[ip]*e2[i]);
                xi[i] = q[i] + rho*om[i];
                d[i] = l[i]*om[i];           /* L omega  (chord direction, unnormalised) */
                n[i] = li[i]*xi[i];          /* L^{-1} xi (outer normal, unnormalised)   */
            }
            double d2 = d[0]*d[0] + d[1]*d[1] + d[2]*d[2];
            double B = n[0]*n[0] + n[1]*n[1] + n[2]*n[2];
            double dn = sqrt(d2), sB = sqrt(B);
            double cx = d[1]*n[2] - d[2]*n[1], cy = d[2]*n[0] - d[0]*n[2], cz = d[0]*n[1] - d[1]*n[0];
            double cr = sqrt(cx*cx + cy*cy + cz*cz);
            /* d.n = omega.xi = w  exactly */
            double al = atan2(cr, w);
            double hyp = dn*sB;
            double s = cr/hyp, c = w/hyp;
            /* renormalise (s,c) against rounding */
            double nn = sqrt(s*s + c*c); s /= nn; c /= nn;
            double J, K, A;
            kernel_funcs(al, s, c, &J, &K, &A);
            double k = rho*w, D = rho*dn;
            double u[3] = {d[0]/dn, d[1]/dn, d[2]/dn};
            acc[0] += wgt * k*al*al;
            double lu[3] = {l[0]*u[0], l[1]*u[1], l[2]*u[2]};
            for (int i = 0; i < 3; i++) acc[1+i] += wgt*(xi[i]*J - lu[i]*sB*K);
            if (!boundary) {
                double Ak = A/k, AD = A/D, G = sB*(c*A + K)/D, KD = sB*K/D;
                acc[4] += wgt*(-xi[0]*xi[0]*Ak + 2.0*xi[0]*lu[0]*AD - lu[0]*lu[0]*G + l[0]*l[0]*KD);
                acc[5] += wgt*(-xi[1]*xi[1]*Ak + 2.0*xi[1]*lu[1]*AD - lu[1]*lu[1]*G + l[1]*l[1]*KD);
                acc[6] += wgt*(-xi[2]*xi[2]*Ak + 2.0*xi[2]*lu[2]*AD - lu[2]*lu[2]*G + l[2]*l[2]*KD);
                acc[7] += wgt*(-xi[0]*xi[1]*Ak + (xi[0]*lu[1] + lu[0]*xi[1])*AD - lu[0]*lu[1]*G);
                acc[8] += wgt*(-xi[0]*xi[2]*Ak + (xi[0]*lu[2] + lu[0]*xi[2])*AD - lu[0]*lu[2]*G);
                acc[9] += wgt*(-xi[1]*xi[2]*Ak + (xi[1]*lu[2] + lu[1]*xi[2])*AD - lu[1]*lu[2]*G);
            }
        }
    }
    for (int i = 0; i < 10; i++) out[i] = acc[i];
    if (boundary) for (int i = 4; i < 10; i++) out[i] = NAN;
}

/* batch: n items, each with its own l (3) and q (3) */
void triax_eval_many(int n, const double *l, const double *q, int nt, const double *x,
                     const double *wt, int nphi, const double *cph, const double *sph, double *out)
{
#pragma omp parallel for schedule(dynamic, 4)
    for (int i = 0; i < n; i++)
        eval_one(l + 3*(size_t)i, q + 3*(size_t)i, nt, x, wt, nphi, cph, sph, out + 10*(size_t)i);
}
