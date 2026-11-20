"""shear.py -- the shape-variation ("shear") tensor
      T(q; L) = < 2 k alpha cot(alpha) ( u (x) u  -  nu (x) nu ) >        (symmetric, traceless)
   u = L(xi-q)/|L(xi-q)| (unit chord direction), nu = L^{-1}xi/|L^{-1}xi| (unit outer normal), cos(alpha) = u.nu.
 Identities (exact; derived in REPORT.md section 1.5):
   (S1)  d/de E((I + e Delta) L; q)|_{e=0} = tr(T Delta^T)   for every 3x3 matrix Delta      (q fixed)
   (S2)  dE/dl_i = T_ii / l_i                                 (q fixed)
   (S3)  q_i E_j - q_j E_i = (l_j/l_i - l_i/l_j) T_ij          (rotation covariance)
 Pure numpy, same log-chord quadrature as triax_kernel.c, written independently of the C kernel's
 gradient code.  Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np


def shear_tensor(l, q, n=(160, 160)):
    l = np.asarray(l, float); q = np.asarray(q, float)
    r = np.linalg.norm(q)
    x, w = np.polynomial.legendre.leggauss(n[0])
    ph = 2*np.pi*(np.arange(n[1]) + 0.5)/n[1]
    if r < 1e-12:
        qh = np.array([0, 0, 1.0])
    else:
        qh = q/r
    m = np.argmin(np.abs(qh)); e1 = np.eye(3)[m] - qh[m]*qh; e1 /= np.linalg.norm(e1); e2 = np.cross(qh, e1)
    if r >= 1 - 1e-13:
        th = 0.25*np.pi*(x + 1); mu = np.cos(th); rho = 2*mu; wv = mu
        wg = w*0.25*np.pi*mu*np.sin(th)/np.pi*(2*np.pi/n[1])
    elif r < 1e-9:
        mu = x; rho = 1 + r*mu; wv = np.ones_like(x); wg = w*rho**2/(2*n[1])
    else:
        T = np.arctanh(r); tau = T*x; se = np.sqrt(1 - r*r)
        rho = se*np.exp(tau); wv = se*np.cosh(tau); mu = se*np.sinh(tau)/r
        wg = w*(T/r)*rho**2/(2*n[1])
    mu = np.clip(mu, -1, 1); st = np.sqrt((1 - mu)*(1 + mu))
    om = -mu[:, None, None]*qh + st[:, None, None]*(np.cos(ph)[None, :, None]*e1 + np.sin(ph)[None, :, None]*e2)
    xi = q + rho[:, None, None]*om
    d = l*om; nn = xi/l
    dn = np.linalg.norm(d, axis=-1); sB = np.linalg.norm(nn, axis=-1)
    u = d/dn[..., None]; nu = nn/sB[..., None]
    cr = np.linalg.norm(np.cross(d, nn), axis=-1)
    W = np.broadcast_to(wv[:, None], cr.shape)
    al = np.arctan2(cr, W)
    with np.errstate(divide="ignore", invalid="ignore"):
        acot = np.where(al > 1e-6, al*W/np.where(cr > 0, cr, 1.0), 1.0 - al*al/3)
    k = rho[:, None]*W
    f = (wg[:, None]*2*k*acot)[..., None, None]
    return np.sum(f*(u[..., :, None]*u[..., None, :] - nu[..., :, None]*nu[..., None, :]), axis=(0, 1))


if __name__ == "__main__":
    import json, sys
    import triax
    rng = np.random.default_rng(20261120)
    worst = dict(S2=0.0, S3=0.0, trace=0.0)
    rows = []
    for trial in range(10):
        s = 1 + 2.5*rng.random(); t = 1 + 3*rng.random(); l = np.array([1, s, s*t])
        v = rng.normal(size=3); v /= np.linalg.norm(v); q = v*rng.random()**(1/3)*0.97
        if trial >= 8:
            q = v            # boundary point: (S3) for the gradient trace
        T = shear_tensor(l, q, (240, 240))
        o = triax.ev(l, q, (240, 240)); g = o[1:4]
        e3 = max(abs((q[i]*g[j] - q[j]*g[i]) - (l[j]/l[i] - l[i]/l[j])*T[i, j]) for i, j in ((0, 1), (0, 2), (1, 2)))
        e2 = 0.0
        if trial < 8:
            h = 1e-5
            for i in range(3):
                dl = np.zeros(3); dl[i] = h
                fd = (triax.ev(l + dl, q, (240, 240))[0] - triax.ev(l - dl, q, (240, 240))[0])/(2*h)
                e2 = max(e2, abs(fd - T[i, i]/l[i]))
        worst["S2"] = max(worst["S2"], e2); worst["S3"] = max(worst["S3"], e3); worst["trace"] = max(worst["trace"], abs(np.trace(T)))
        rows.append(dict(s=s, t=t, q=q.tolist(), T=T.tolist(), err_S2=e2, err_S3=e3, trace=float(np.trace(T))))
    print(worst)
    if len(sys.argv) > 1:
        json.dump(dict(worst=worst, rows=rows), open(sys.argv[1], "w"), indent=1)
