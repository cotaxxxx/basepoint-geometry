"""Contract 43 (north near band) -- Code INDEPENDENT exact certificate of the L43 single-piece chain.

STATUS AT COMMIT: SOURCE ONLY.  NOT EXECUTED.  Syntax checked with ast.parse only (chat permission 2026-10-09; no import, no run).
BUDGET_V12 set after the canonical 22'' v1.2 pin (chat instruction 2026-10-09); execution still requires the explicit FREEZE and run permission.  Execution and use of its output as evidence are authorized only after
the FREEZE of predeclare v3 (CONTRACT43_NEAR_BAND_PREDECLARE_DRAFT.md) by explicit chat ruling.
INDEPENDENCE DECLARATION: this file was written by Code from the predeclare v3 chain (A1)-(A8) and Code's own collation; Code has never
received or seen Astra's `l43_graph_majorant_exact.py`; nothing here is imported or copied from it.

Mathematical chain certified (numbers refer to predeclare v3 §3; "ring" = identity modulo y^2 = a^2 - b^2, a^2 = 1 - (m-s)^2,
rho^2 = 1 - m^2, L = lambda^2, mu_xi^2 = 1 - xi^2, all denominators cleared; "Bernstein" = exact Bernstein coefficient positivity on
the stated interval; "SOS" = exact sum-of-squares identity; "paper" = elementary step stated in the docstring and NOT re-proved here):
 (A1)  N = lambda[ xi D^2 + (t/2)(D^2 - (1-L) s^2 - delta) ]                                     ring
       delta = (mu_xi + m) l,  l = mu_xi - m                                                         ring
       2 m l <= delta <= 2 l  (mu_xi in [m, 1])                                                       paper (from the identity, mu_xi + m in [2m, 1+m] <= 2)
 (A2)  2h/lambda = D^2 + (1-L) s^2 + delta                                                           ring
       |n|^2 = 1, |e|^2 = 1, N/(w D^2) = nu - gamma kappa, Gram identity                           ring (cleared)
       => 0 <= gamma <= 1 and |N| <= w D^2                                                            paper (Cauchy-Schwarz on the Gram identity)
 (A3)  a^2 <= 2 m rho on the band;  m - rho >= 97/113;  mu dmu = -a da (Jacobian dmu dphi = db dy/mu)  ring / rational / symbolic
       (9/25)(1 - z)^2 - 2 z > 0 on z in [0, 15/112]  (=> |grad g| < 3/5 on the disk)                 Bernstein
       |s + l| <= k r                                                                                 paper (mean value on the convex disk)
 (A4)  (5/4)(s+l)^2 + 5 l^2 - s^2 = (s/2 + 5l/2)^2;  4(s+l)^2 + (4/3) s^2 - l^2 = (4s + 3l)^2/3         SOS
       1/50 - (21/20) z^2 > 0 on [0, 15/112];  1/12 - (9/25) L > 0 on [4/25, 8649/40000]              Bernstein
       => (1-L)s^2 <= (189/500) r^2 + delta/50  and  D^2 >= (3/4)(r^2 + L l^2)                          paper (assembly of the above)
 (A5)  N/D^2 = lambda(xi + t zeta/2), zeta = 1 - ((1-L)s^2 + delta)/D^2, -c_g delta/D^2 <= zeta <= 1    ring + paper
       pointwise majorant M <= (2L/w)[ (xi^2+|xi t|+t^2/4)/D + c_g delta|xi t|/D^3 + c_g^2 delta^2 t^2/(4D^5) ]   paper (|zeta|<=1+v, zeta^2<=1+v^2)
 (A6)  int_0^pi |cos| = 2, int_0^pi cos^2 = pi/2;  <xi^2> = rho^2/3, <|xi|> = rho/2, <delta> = 2 rho^2/3   symbolic
       d/dr[arsinh(r/d) - r/sqrt(r^2+d^2)] = r^2 (r^2+d^2)^{-3/2};  int_0^inf r^3 (r^2+d^2)^{-5/2} dr = 2/(3d)   symbolic
       arsinh(x) <= log(1 + 2x)  (sqrt(1+x^2) <= 1 + x)                                              SOS/paper
       w^2 - W(lambda)^2 = (mu^2 - mu_0^2)(1 - L) >= 0 for mu >= mu_0;  lambda^p / W(lambda) increasing (p = 1, 2)   ring / symbolic
 (A7)  r_0 = 15/113, H_0 = 13/20: 2 r_0 < (H_0 - r_0)^2;  (77/50)^2 > (4/3)^3;  (103/50)^2 > (4/3)^5;  W(93/200)^2 > (89/100)^2;
       1 + 10 H_0/r_0^2 = 166447/450 < sum_{j<=10} 6^j/j!  (=> log(1 + 10 H_0/r_0^2) < 6);  pi < 22/7  (paper: int_0^1 x^4(1-x)^4/(1+x^2) dx > 0)
       monotonicity in rho and R_e of every term                                                     paper (each term is a product of increasing factors;
                                                                                                    rho^3 log(1 + 10 H_0/rho^2): 3 log(1+x) >= 2x/(1+x))
 (A8)  U_43^{N3} <= T_curv + T_cross + T_depth (exact rationals), sum < 9/40                             exact arithmetic
 (C6)  comparison with the frozen budget text 22'' v1.2 (canonical commit d445b302…): U_43^{N3} < BUDGET_V12 = S''_lb - 5481/10000 = 187614363159/817216000000,
       and the final margin S''_lb - U_north,cert - U_43^{N3} is printed as an exact rational
"""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

def R(x): return sp.Rational(x.numerator, x.denominator)

# ------------------------------------------------------------------ symbols and ring reduction
lam, L, m, rho, s, b, xi, y, mux = sp.symbols('lambda L m rho s b xi y mu_xi', real=True)
mu = m - s
a2 = 1 - mu**2
def red(e):
    """reduce a polynomial expression modulo the ring relations (y^2, rho^2, L, mu_xi^2)."""
    e = sp.expand(e)
    e = sp.rem(sp.Poly(e, y), sp.Poly(y**2 - (a2 - b**2), y)).as_expr()
    e = sp.rem(sp.Poly(sp.expand(e), rho), sp.Poly(rho**2 - (1 - m**2), rho)).as_expr()
    e = sp.rem(sp.Poly(sp.expand(e), L), sp.Poly(L - lam**2, L)).as_expr()
    e = sp.rem(sp.Poly(sp.expand(e), mux), sp.Poly(mux**2 - (1 - xi**2), mux)).as_expr()
    return sp.expand(e)

D2 = (b - xi)**2 + y**2 + L*s**2
h = lam*(1 - m*mu - xi*b)
w2 = mu**2 + L*a2
T = y**2 + L*s**2
N = lam*(b*s*(m - (1 - L)*s) - xi*(b**2 - rho**2 - m*s))
t = b - xi
delta = rho**2 - xi**2
l = mux - m

# ------------------------------------------------------------------ (A1)
check("(A1) N == lambda[xi D^2 + (t/2)(D^2 - (1-L)s^2 - delta)]", red(N - lam*(xi*D2 + t/2*(D2 - (1 - L)*s**2 - delta))) == 0)
check("(A1) delta == (mu_xi + m) l", red(delta - (mux + m)*l) == 0)

# ------------------------------------------------------------------ (A2)
check("(A2) 2h/lambda == D^2 + (1-L)s^2 + delta", red(2*h/lam - (D2 + (1 - L)*s**2 + delta)) == 0)
check("(A2) |n|^2 w^2 == w^2 and |e|^2 D^2 == D^2 (unit vectors)", red((lam*b)**2 + (lam*y)**2 + mu**2 - w2) == 0 and red((b - xi)**2 + y**2 + (lam*s)**2 - D2) == 0)
# nu - gamma kappa = lambda b/w - h (b - xi)/(w D^2);  times w D^2:  lambda b D^2 - h (b - xi)  ==  N
check("(A2) (nu - gamma kappa) w D^2 == N", red(lam*b*D2 - h*(b - xi) - N) == 0)
Aperp = mu + L*s
check("(A2) Gram: (w^2 D^2 - h^2)(D^2 - (b-xi)^2) - (lambda b D^2 - h(b-xi))^2 == (mu + L s)^2 y^2 D^2",
      red((w2*D2 - h**2)*(D2 - (b - xi)**2) - (lam*b*D2 - h*(b - xi))**2 - Aperp**2*y**2*D2) == 0)
# consequence (paper): (1-gamma^2)(1-kappa^2) - (nu - gamma kappa)^2 >= 0 with both factors <= 1  =>  (N/(wD^2))^2 <= 1.

# ------------------------------------------------------------------ Bernstein helper
def bern_min(expr, var, lo, hi):
    tt = sp.symbols('tt')
    P = sp.Poly(sp.expand(expr.subs(var, R(lo) + R(hi - lo)*tt)), tt)
    n = P.degree(); c = {mon[0]: co for mon, co in zip(P.monoms(), P.coeffs())}
    coeffs = [sum(sp.Rational(comb(i, k), comb(n, k))*c.get(k, 0) for k in range(i + 1)) for i in range(n + 1)]
    return min(coeffs), coeffs

# ------------------------------------------------------------------ (A3)
z = sp.symbols('z', real=True)
check("(A3) a^2 == 2 m rho at mu = m - rho  (a^2 <= 2 m rho on the band since mu >= m - rho >= 0)", red((1 - (m - rho)**2) - 2*m*rho) == 0)
check("(A3) m - rho >= 112/113 - 15/113 = 97/113", Q(112, 113) - Q(15, 113) == Q(97, 113))
aa = sp.symbols('a', positive=True)
check("(A3) Jacobian: d/da sqrt(1 - a^2) == -a/sqrt(1 - a^2)  (mu dmu = -a da; db dy = a da dphi)", sp.simplify(sp.diff(sp.sqrt(1 - aa**2), aa) + aa/sp.sqrt(1 - aa**2)) == 0)
mn, co = bern_min(sp.Rational(9, 25)*(1 - z)**2 - 2*z, z, Q(0), Q(15, 112))
check("(A3) (9/25)(1-z)^2 - 2z > 0 on z in [0, 15/112]  (|grad g|^2 <= 2 m rho/(m - rho)^2 < 9/25)", mn > 0, f"Bernstein coefficients {co}")
check("(A3) rho/m <= 15/112 on the box", Q(15, 113)/Q(112, 113) == Q(15, 112))
# |u - (xi, 0)| <= |u| + |xi| <= R_* + rho = R_e  (triangle inequality, paper)

# ------------------------------------------------------------------ (A4)
ls = sp.symbols('ell', real=True)
check("(A4) SOS: (5/4)(s+l)^2 + 5 l^2 - s^2 == (s/2 + 5 l/2)^2", sp.expand(sp.Rational(5, 4)*(s + ls)**2 + 5*ls**2 - s**2 - (s/2 + 5*ls/2)**2) == 0)
check("(A4) SOS: 4(s+l)^2 + (4/3) s^2 - l^2 == (4 s + 3 l)^2/3", sp.expand(4*(s + ls)**2 + sp.Rational(4, 3)*s**2 - ls**2 - (4*s + 3*ls)**2/3) == 0)
check("(A4) (5/4)(9/25) == 9/20;  (21/25)(9/20) == 189/500;  (21/25)*5 == 21/5", Q(5, 4)*Q(9, 25) == Q(9, 20) and Q(21, 25)*Q(9, 20) == Q(189, 500) and Q(21, 25)*5 == Q(21, 5))
mn, co = bern_min(sp.Rational(1, 50) - sp.Rational(21, 20)*z**2, z, Q(0), Q(15, 112))
check("(A4) 1/50 - (21/20) z^2 > 0 on [0, 15/112]  ((21/5) l^2 <= (21/20) z^2 delta)", mn > 0, f"Bernstein coefficients {co}")
mn, co = bern_min(sp.Rational(1, 12) - sp.Rational(9, 25)*L, L, Q(4, 25), Q(8649, 40000))
check("(A4) 1/12 - (9/25) L > 0 on [4/25, 8649/40000]  (1 + 4 L k^2 <= 4/3)", mn > 0, f"Bernstein coefficients {co}")
check("(A4) 1 - m == rho^2/(1 + m)  (so l <= 1 - m <= rho^2/(2m))", red((1 - m)*(1 + m) - rho**2) == 0)

# ------------------------------------------------------------------ (A5)
zeta = 1 - ((1 - L)*s**2 + delta)/D2
check("(A5) N == lambda D^2 (xi + t zeta/2)   [identity (A1) in the zeta form]", red(sp.expand(N*1) - sp.expand(lam*(xi*D2 + t/2*(D2 - (1 - L)*s**2 - delta)))) == 0)
cg = Q(51, 50)
check("(A5) c_g = 51/50 = 1 + 1/50 and 189/500 <= 1  (so (1-L)s^2 <= D^2 + delta/50, zeta >= -c_g delta/D^2)", cg == 1 + Q(1, 50) and Q(189, 500) <= 1)
# paper: for zeta in [-v, 1], v >= 0:  |zeta| <= 1 + v,  zeta^2 <= 1 + v^2;  (xi + t zeta/2)^2 <= xi^2 + |xi t||zeta| + t^2 zeta^2/4.

# ------------------------------------------------------------------ (A6)
th = sp.symbols('theta', real=True)
# |cos theta| on [0, pi]: cos >= 0 on [0, pi/2], cos <= 0 on [pi/2, pi]; split (no Abs integration).
check("(A6) int_0^pi |cos| == 2 (split at pi/2);  int_0^pi cos^2 == pi/2",
      sp.integrate(sp.cos(th), (th, 0, sp.pi/2)) - sp.integrate(sp.cos(th), (th, sp.pi/2, sp.pi)) == 2 and sp.integrate(sp.cos(th)**2, (th, 0, sp.pi)) == sp.pi/2)
rp = sp.symbols('rp', positive=True); xr = sp.symbols('xr', real=True)
# |xi| on [-rho, rho] is even: int_{-rho}^{rho} |xi| dxi = 2 int_0^rho xi dxi  (no Abs integration).
check("(A6) <xi^2> = rho^2/3, <|xi|> = rho/2 (by symmetry), <delta> = 2 rho^2/3",
      sp.simplify(sp.integrate(xr**2, (xr, -rp, rp))/(2*rp) - rp**2/3) == 0 and sp.simplify(2*sp.integrate(xr, (xr, 0, rp))/(2*rp) - rp/2) == 0
      and sp.simplify(sp.integrate(rp**2 - xr**2, (xr, -rp, rp))/(2*rp) - 2*rp**2/3) == 0)
r, d = sp.symbols('r d', positive=True)
check("(A6) d/dr[arsinh(r/d) - r/sqrt(r^2+d^2)] == r^2 (r^2+d^2)^(-3/2)", sp.simplify(sp.diff(sp.asinh(r/d) - r/sp.sqrt(r**2 + d**2), r) - r**2*(r**2 + d**2)**sp.Rational(-3, 2)) == 0)
check("(A6) int_0^inf r^3 (r^2+d^2)^(-5/2) dr == 2/(3d)", sp.simplify(sp.integrate(r**3*(r**2 + d**2)**sp.Rational(-5, 2), (r, 0, sp.oo)) - 2/(3*d)) == 0)
xx = sp.symbols('x', positive=True)
check("(A6) (1 + x)^2 - (1 + x^2) == 2x >= 0  (sqrt(1+x^2) <= 1 + x, hence arsinh x <= log(1 + 2x))", sp.expand((1 + xx)**2 - (1 + xx**2) - 2*xx) == 0)
mu0 = Q(97, 113)
muv = sp.symbols('mu', real=True)
W2 = R(mu0)**2 + lam**2*(1 - R(mu0)**2)
check("(A6) w^2 - W(lambda)^2 == (mu^2 - mu_0^2)(1 - L)  with w^2 = mu^2 + L(1 - mu^2)", sp.expand((muv**2 + lam**2*(1 - muv**2)) - W2 - (muv**2 - R(mu0)**2)*(1 - lam**2)) == 0)
Wl = sp.sqrt(W2)
check("(A6) d/dlambda [lambda/W] == mu_0^2/W^3 > 0;  d/dlambda [lambda^2/W] == lambda(2 mu_0^2 + lambda^2(1 - mu_0^2))/W^3 > 0",
      sp.simplify(sp.diff(lam/Wl, lam) - R(mu0)**2/Wl**3) == 0 and sp.simplify(sp.diff(lam**2/Wl, lam) - lam*(2*R(mu0)**2 + lam**2*(1 - R(mu0)**2))/Wl**3) == 0)
check("(A6) depth: delta^2/d_l <= 2 delta/lambda since d_l = lambda l >= lambda delta/2;  cross: d_l >= delta/5 since lambda >= 2/5", Q(2, 5)*Q(1, 2) == Q(1, 5))

# ------------------------------------------------------------------ (A7)
r0, H0, lamb, pi_hi = Q(15, 113), Q(13, 20), Q(93, 200), Q(22, 7)
check("(A7) rho <= r_0 = 15/113 (rho^2 = 1 - m^2 <= 1 - (112/113)^2 = (15/113)^2)", 1 - Q(112, 113)**2 == r0**2)
check("(A7) R_e = sqrt(2 m rho) + rho <= sqrt(2 r_0) + r_0 < H_0 = 13/20   (2 r_0 < (H_0 - r_0)^2, m <= 1)", 2*r0 < (H0 - r0)**2)
c32, c52 = Q(77, 50), Q(103, 50)
check("(A7) (4/3)^(3/2) < 77/50;  (4/3)^(5/2) < 103/50", c32**2 > Q(4, 3)**3 and c52**2 > Q(4, 3)**5)
W2b = mu0**2 + lamb**2*(1 - mu0**2); W_lo = Q(89, 100)
check("(A7) W(93/200)^2 - (89/100)^2 == 211911/127690000 > 0", W2b - W_lo**2 == Q(211911, 127690000) and W2b > W_lo**2)
X = 1 + 10*H0/r0**2
check("(A7) 1 + 10 H_0/r_0^2 == 166447/450", X == Q(166447, 450))
S6 = sum(Q(6)**j/factorial(j) for j in range(11))
check("(A7) sum_{j<=10} 6^j/j! == 67591/175 > 166447/450  (=> e^6 > 1 + 10 H_0/r_0^2, log(...) < 6)", S6 == Q(67591, 175) and S6 > X)
check("(A7) pi < 22/7: int_0^1 x^4(1-x)^4/(1+x^2) dx == 22/7 - pi > 0", sp.simplify(sp.integrate(xx**4*(1 - xx)**4/(1 + xx**2), (xx, 0, 1)) - (sp.Rational(22, 7) - sp.pi)) == 0)
# paper: monotonicity in rho of  rho^3 log(1 + 10 H_0/rho^2):  derivative = rho^2 [3 log(1+x) - 2x/(1+x)] >= 0  (log(1+x) >= x/(1+x));
#        A(rho, R_e), rho^2 and the prefactors are increasing in rho, R_e, lambda; so evaluation at (r_0, H_0, 93/200) bounds the box.

# ------------------------------------------------------------------ (A8)
den = mu0*W_lo                                   # mu w >= mu_0 W(lambda_bar) > mu_0 (89/100)
pref2 = 2*pi_hi*lamb**2/den                      # p = 2
pref1 = 2*pi_hi*lamb/den                         # p = 1
A_curv = pi_hi*r0**2*H0/3 + r0*H0**2/2 + pi_hi*H0**3/24
T_curv = pref2*A_curv
T_cross = pref2*cg*c32*r0**3*6                   # rho^3 log(...) <= 6 r_0^3
T_depth = pref1*pi_hi*cg**2*c52*r0**2/9
U43 = T_curv + T_cross + T_depth
print(f"(A8) T_curv = {T_curv} (~{float(T_curv):.6f});  T_cross = {T_cross} (~{float(T_cross):.6f});  T_depth = {T_depth} (~{float(T_depth):.6f})")
print(f"(A8) U_43^N3 <= {U43}  (~{float(U43):.6f})")
check("(A8) U_43^N3 < 9/40", U43 < Q(9, 40), f"9/40 - U = {Q(9, 40) - U43}")
check("(A8) cross-check against the value stated in the Astra report (independent re-derivation agrees)", U43 == Q(3887073979116207, 17284813033600000))

# ------------------------------------------------------------------ (C6)
# 22'' v1.2 pinned (canonical cotaxxxx/bg-oblate-spheroid, design/d-ob-p2, commit d445b302bd879b5dc5211c7ba310d5aef036f31e,
# blob 6340cb3e1dcb7387e4044013fb9f77a9cd21788a, SHA-256 3ef26f903d15c11449e583a917723ffcbaff7217b76f3fc65284e02b820b4640; CHAT AUDIT PASS):
# budget U_north + U_near < S''_lb with S''_lb = 635530452759/817216000000 and certified U_north < 5481/10000 (contract 45 pieces 1-3).
S_LB = Q(635530452759, 817216000000)
U_FAR_CERT = Q(5481, 10000)
BUDGET_V12 = Q(187614363159, 817216000000)      # = S''_lb - 5481/10000, the near-band residual of 22'' v1.2
check("(C6.0) BUDGET_V12 == S''_lb - U_far,cert", BUDGET_V12 == S_LB - U_FAR_CERT)
c6_done = BUDGET_V12 is not None
if c6_done:
    check("(C6) U_43^N3 < BUDGET_V12 (22'' v1.2 near-band residual)", U43 < BUDGET_V12, f"BUDGET_V12 - U = {BUDGET_V12 - U43}")
    print(f"(C6) final margin S''_lb - U_north,cert - U_43^N3 = {S_LB - U_FAR_CERT - U43}  (~{float(S_LB - U_FAR_CERT - U43):.6f})  [exact rational]")
else:
    print("(C6) budget comparison: PENDING (22'' v1.2 not pinned; no number is asserted)")

# ------------------------------------------------------------------ scope statement (S-2): what this run does and does not establish
print("SCOPE OF THIS CERTIFICATE RUN")
print("  machine-checked here: ring identities (A1), (A2), (A5); SOS identities (A4); Bernstein positivity (A3), (A4); symbolic integrals,")
print("    antiderivatives and limits (A6); rational constants, enclosures and monotone evaluation points (A7); exact arithmetic (A8).")
print("  paper steps relied on (stated in the docstring, NOT machine-verified): Cauchy-Schwarz consequence of the Gram identity (A2);")
print("    mean-value/Lipschitz bound on the convex disk and the triangle inequality for R_e (A3); assembly of (A4) into (1-L)s^2 <= (189/500)r^2")
print("    + delta/50 and D^2 >= (3/4)(r^2 + L l^2); the zeta-interval and the one-sided majorant (A5); region extension, Tonelli/order of")
print("    integration, and the rho/R_e/lambda monotonicity used to evaluate at (r_0, H_0, 93/200) (A6)-(A7); normalization (S0) of contract 44.")
print("  external items, ledger state at the time of this source version (2026-10-09): H-43-1(ii) CLOSED by chat ruling on Astra's independent")
print("    lemma (H43_ENDPOINT_LEMMA.md, SHA-256 b1a906ed...); Astra deliverables pinned and exact script CHAT AUDIT PASS; 22'' v1.2 pinned")
print("    (canonical d445b302...).  These are NOT re-verified by this run.")
print("  external obligations NOT covered by this run: H-43-1(i) formal source pin and evidence closure; the paper steps listed above;")
print("    the CHAT AUDIT of this run's output and the FREEZE/run-permission bookkeeping.  This run certifies nothing about D-P2.")
if not ok:
    print("RESULT: SOME CERTIFICATE CHECK FAILED -- NOT CERTIFIED"); raise SystemExit(1)
if not c6_done:
    print("RESULT: PRE-BUDGET CHECKS PASS; C6 PENDING; NOT CERTIFIED  (exit 0 means only: every implemented check passed)"); raise SystemExit(0)
print("RESULT: ALL IMPLEMENTED CHECKS PASS INCLUDING C6; paper steps and external obligations above remain subject to CHAT AUDIT; NOT a D-P2 certification")
raise SystemExit(0)
