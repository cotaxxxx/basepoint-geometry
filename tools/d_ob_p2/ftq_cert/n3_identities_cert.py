"""Exact certificates for contracts 44 and 46 (FT_q north far, N3 route).  Polynomial identity checks + rational Bernstein.

CONTRACT 44 -- symbols and sources (no collision with FT_q symbols v = D_+ D_-, q = b^2):
  Base point on the segment: (xi, 0, z), xi in [-rho, rho], z = lambda m.  Surface point x(mu, phi), a^2 = 1 - mu^2,
  b = a cos phi, mu = m - s, rho^2 = 1 - m^2.  P1 (design note SHA-256 2c304ee6..., Lemma 3.1/3.3/3.4; pinned producer
  dff79bc4..., kernel_point(second=True)):
    h = lambda (1 - xi b) - z mu,                 D^2 = (b - xi)^2 + a^2 sin^2 phi + L s^2,   w^2 = mu^2 + L a^2,
    gamma = h/(w D),   R = R(gamma) in [1, pi/2],   R_gamma in [-1, 0],
    gamma_rho = -lambda b/(w D) + h (b - xi)/(w D^3),
    gamma_rhorho = (-2 lambda b (b - xi) - h)/(w D^3) + 3 h (b - xi)^2/(w D^5),
    F_rhorho = 4 lambda b R gamma_rho - 2 h (R_gamma gamma_rho^2 + R gamma_rhorho).
  New symbols:  nu := lambda b / w,   kappa := (b - xi)/D   (|kappa| <= 1).
  Identities certified below (all as exact polynomial identities after clearing denominators, with the relations
  D^2 = (b-xi)^2 + a^2 - b^2 + L s^2 and rho^2 = 1 - m^2 applied by polynomial remainder):
   (44.1) gamma_rho = (gamma kappa - nu)/D,   gamma_rhorho = (3 gamma kappa^2 - gamma - 2 nu kappa)/D^2
   (44.2) -F_rhorho - 2 h R_gamma gamma_rho^2 = (2 R w/D) Phi,   Phi := 2 (nu - gamma kappa)^2 - gamma^2 (1 - kappa^2)
          i.e. -F_rhorho = (2 R w/D) Phi + 2 h R_gamma gamma_rho^2; the last term is <= 0 (h >= 0, R_gamma <= 0), hence
          -F_rhorho <= (2 R w/D) Phi   (N1);  [-F_rhorho]_+ <= (pi w/D) [Phi]_+   (N2)
   (44.3) nu - gamma kappa = N/(w D^2),   N = lambda [ b s (m - (1-L) s) - xi (b^2 - rho^2 - m s) ]
   (44.4) (w/D) Phi = [ 2 N^2 - h^2 (a^2 sin^2 phi + L s^2) ] / (w D^5)
   (44.5) a^2 = rho^2 + 2 m s - s^2,   1 - m mu = rho^2 + m s
CONTRACT 46 -- on north far (s >= rho, 0 < s <= 1/2, m in [112/113, 1]):  a - rho >= (51/100) sqrt(s).
  a - rho = s(2m - s)/(a + rho) > 0;  (a + rho)^2 <= 2(a^2 + rho^2) = 2(2 rho^2 + 2 m s - s^2) <= 2(s^2 + 2 m s) (rho <= s);
  so (a - rho)^2 >= s (2m - s)^2 / (2 (s + 2m)), and it suffices that (2m - s)^2 - 2 c^2 (s + 2m) > 0, c = 51/100
  (Bernstein on m in [112/113, 1], s in [0, 1/2]).
"""
from fractions import Fraction as Q
from itertools import product
from math import comb
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

lam, L, m, rho, s, b, xi, w, D, R, Rg = sp.symbols('lambda L m rho s b xi w D R R_gamma')
mu = m - s
a2 = 1 - mu**2
D2 = (b - xi)**2 + (a2 - b**2) + L*s**2
h = lam*(1 - xi*b) - lam*m*mu
gamma = h/(w*D); nu = lam*b/w; kappa = (b - xi)/D
g_r = -lam*b/(w*D) + h*(b - xi)/(w*D**3)
g_rr = (-2*lam*b*(b - xi) - h)/(w*D**3) + 3*h*(b - xi)**2/(w*D**5)
Frr = 4*lam*b*R*g_r - 2*h*(Rg*g_r**2 + R*g_rr)
Phi = 2*(nu - gamma*kappa)**2 - gamma**2*(1 - kappa**2)
N = lam*(b*s*(m - (1 - L)*s) - xi*(b**2 - rho**2 - m*s))

def is_identity(expr):
    """expr == 0 modulo D^2 = D2 and rho^2 = 1 - m^2 (denominators are products of w, D: cleared first)."""
    num = sp.numer(sp.together(expr))
    num = sp.expand(num)
    num = sp.rem(sp.Poly(num, D), sp.Poly(D**2 - D2, D)).as_expr()          # reduce powers of D
    num = sp.rem(sp.Poly(sp.expand(num), rho), sp.Poly(rho**2 - (1 - m**2), rho)).as_expr()
    return sp.expand(num) == 0

check("(44.1a) gamma_rho == (gamma kappa - nu)/D", is_identity(g_r - (gamma*kappa - nu)/D))
check("(44.1b) gamma_rhorho == (3 gamma kappa^2 - gamma - 2 nu kappa)/D^2", is_identity(g_rr - (3*gamma*kappa**2 - gamma - 2*nu*kappa)/D**2))
check("(44.2) -F_rhorho - 2 h R_gamma gamma_rho^2 == (2 R w/D) Phi", is_identity(-Frr - 2*h*Rg*g_r**2 - (2*R*w/D)*Phi))
check("(44.3) nu - gamma kappa == N/(w D^2)", is_identity((nu - gamma*kappa) - N/(w*D**2)))
check("(44.4) (w/D) Phi == [2N^2 - h^2(a^2 sin^2 + L s^2)]/(w D^5)", is_identity((w/D)*Phi - (2*N**2 - h**2*(a2 - b**2 + L*s**2))/(w*D**5)))
check("(44.5) a^2 == rho^2 + 2ms - s^2;  1 - m mu == rho^2 + m s", is_identity(a2 - (rho**2 + 2*m*s - s**2)) and is_identity((1 - m*mu) - (rho**2 + m*s)))

def bern_min(expr, box):
    ts = sp.symbols('t0:%d' % len(box))
    sb = {v: sp.Rational(lo.numerator, lo.denominator) + sp.Rational((hi-lo).numerator, (hi-lo).denominator)*t for (v, lo, hi), t in zip(box, ts)}
    P = sp.Poly(sp.expand(expr.subs(sb)), *ts); degs = P.degree_list()
    a = {k: Q(int(sp.fraction(c)[0]), int(sp.fraction(c)[1])) for k, c in zip(P.monoms(), P.coeffs())}
    mn = None
    for idx in product(*[range(dd+1) for dd in degs]):
        sm = Q(0)
        for k, c in a.items():
            if all(ki <= ii for ki, ii in zip(k, idx)):
                wgt = Q(1)
                for ki, ii, dd in zip(k, idx, degs): wgt *= Q(comb(ii, ki), comb(dd, ki))
                sm += wgt*c
        mn = sm if mn is None else min(mn, sm)
    return mn

c = sp.Rational(51, 100)
check("(46.0) a^2 - rho^2 == s(2m - s)", is_identity(a2 - rho**2 - s*(2*m - s)))
mn = bern_min(sp.expand((2*m - s)**2 - 2*c**2*(s + 2*m)), [(m, Q(112, 113), Q(1)), (s, Q(0), Q(1, 2))])
check("(46.1) (2m - s)^2 - 2(51/100)^2 (s + 2m) > 0 on m in [112/113,1], s in [0,1/2]", mn > 0, f"min Bernstein coeff = {mn}")
print("Hence on north far (rho <= s <= 1/2): (a - rho)^2 = s^2 (2m-s)^2/(a+rho)^2 >= s^2 (2m-s)^2/(2 s (s + 2m)) > (51/100)^2 s.")
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED")
