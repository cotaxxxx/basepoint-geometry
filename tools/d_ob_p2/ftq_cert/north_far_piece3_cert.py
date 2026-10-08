"""Contract 45, piece 3 of the north-far majorant (method (A)): exact rational upper bound U_3 for the contribution of
I_3 = [1/4, 1/2]  to  U_north.   Paper proof + exact arithmetic; no diagnostic value enters any constant.

SETTING and CHAIN (S0)-(S3) exactly as in north_far_piece1_cert.py (contract 44 audited; pieces 1, 2 CHAT AUDIT PASS):
    U_north <= 2 pi int_{rho}^{1/2} F(s) / ( w(s) D_0(s)^5 ) ds,
    F(s) = 2 lambda^2 pi [ s^2 (m - (1-L) s)^2 a^2 /4 + (rho^2/3)( 3 a^4/16 - k a^2/2 + k^2/2 ) ],
    a^2 = rho^2 + 2 m s - s^2 = 1 - (m-s)^2,   k = rho^2 + m s = 1 - m (m - s),   w^2 = (m-s)^2 + L a^2,
    D_0^2 = (a - rho)^2 + L s^2,   with a >= rho on [0, 1/2] (a^2 - rho^2 = s (2m - s) >= 0).
Box: L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2 <= r^2, r := 15/113.
Constants: c' := 112/113 (m >= c'),  c := 2 c' (2m - s >= c - s > 0),  alpha := 1/4, beta := 1/2.
Steps (P3.1), (P3.3) are those of piece 2 ((P2.1), (P2.3)) re-certified on [1/4, 1/2]; (P3.2) and (P3.4) are new.

 (P3.1) bracket <= B(s) := s^2 (1 - (1-L_hi)s)^2 A(s)/4 + (r^2/3)( (2s - 3s^2)^2/48 + K(s)^2/6 ),  A := 1 - (c'-s)^2,
        K := r^2 + c' s  (same derivation as (P2.1); certified directly by 3-variable Bernstein on (L, m, s) in [1/4,1/2]).
 (P3.2) D_0 with the L s^2 term KEPT.  X := a - rho >= s (c - s)/T(s)  (a + rho <= sqrt(A) + r <= T(s) as in (P2.2), with the
        same T(s) = c1 s^{1/2} + r + c2 s^{-1/2} - c3 s^{3/2}, re-certified for t = sqrt(s) in [1/2, 7072/10000] >= [1/2, sqrt(1/2)]),
        Y := sqrt(L) s >= (2/5) s.   Cauchy-Schwarz with kappa = 1/4:  D_0 = sqrt(X^2 + Y^2) >= (X + kappa Y)/sqrt(1 + kappa^2), so
        D_0 >= (4/sqrt 17) [ s (c - s)/T + s/10 ] = (4/sqrt 17) (s/T) [ (c - s) + T/10 ] >= (4/sqrt 17) s (c~ - s)/T,
        where c~ := c + t0/10 and t0 is a rational lower bound of T on [1/4, 1/2]  [Bernstein in t].  Hence
        1/D_0^5 <= kappa5 T(s)^5 / ( s^5 (c~ - s)^5 ),   kappa5 := rational upper bound of (17/16)^{5/2} (checked by squaring).
 (P3.3) w^2 >= Wq(s) := (c'-s)^2 + (4/25)(2 c' s - s^2) > 0 on [1/4, 1/2]  (a^2 >= 2ms - s^2 >= 2c's - s^2 >= 0, L >= 4/25).
 (P3.4) W(s) := Wq(s)^{-1/2} (c~ - s)^{-5} convex on [1/4, 1/2] (same argument as (P2.4): Wq decreasing, Wq^{-1/2} convex by
        (3/4)Wq'^2 - (1/2) Wq Wq'' >= 0 [Bernstein], (c~ - s)^{-5} positive increasing convex since c~ > 1/2; product of positive
        increasing convex functions is convex).  Chord bound W <= ell(s) with rational endpoint upper bounds W_a, W_b.
 (P3.5) F/(w D_0^5) <= 2 lambda_hi^2 pi_hi kappa5 M(s),  M(s) := B(s) T(s)^5 ell(s)/s^5 >= 0,  and
        U_3 <= 2 pi_hi * 2 lambda_hi^2 pi_hi * kappa5 * int_{1/4}^{1/2} M(s) ds,   pi_hi = 22/7, lambda_hi^2 = 8649/40000.
 (P3.6) exact interval integration of the Laurent polynomial in sqrt(s): alpha^q exact (powers of 1/2); beta^q via
        sqrt(2) in [14142/10000, 14143/10000]; ln(beta/alpha) = ln 2 in [6931/10000, 6932/10000] (checked with exact Taylor partial
        sums of exp and a geometric tail bound).  Each signed term takes the end of its interval that increases the sum.
"""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
import math
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

def R(x): return sp.Rational(x.numerator, x.denominator)
def toQ(x): n, d = sp.fraction(sp.nsimplify(x)); return Q(int(n), int(d))

def bern_min(expr, box, depth=0, max_depth=6):
    """Exact Bernstein lower bound of a polynomial on a box, with bisection of the widest variable when the
    coefficient bound is not positive (up to max_depth).  Returns a certified lower bound."""
    ts = sp.symbols('t0:%d' % len(box))
    sb = {v: R(lo) + R(hi - lo)*t for (v, lo, hi), t in zip(box, ts)}
    P = sp.Poly(sp.expand(expr.subs(sb)), *ts); degs = P.degree_list()
    a = {k: toQ(c) for k, c in zip(P.monoms(), P.coeffs())}
    mn = None
    for idx in product(*[range(dd + 1) for dd in degs]):
        sm = Q(0)
        for k, c in a.items():
            if all(ki <= ii for ki, ii in zip(k, idx)):
                wgt = Q(1)
                for ki, ii, dd in zip(k, idx, degs): wgt *= Q(comb(ii, ki), comb(dd, ki))
                sm += wgt*c
        mn = sm if mn is None else min(mn, sm)
    if mn > 0 or depth >= max_depth: return mn
    i = max(range(len(box)), key=lambda j: box[j][2] - box[j][1]); v, lo, hi = box[i]; mid = (lo + hi)/2
    b1 = list(box); b1[i] = (v, lo, mid); b2 = list(box); b2[i] = (v, mid, hi)
    return min(bern_min(expr, b1, depth + 1, max_depth), bern_min(expr, b2, depth + 1, max_depth))

L, m, s, t = sp.symbols('L m s t', real=True)
cp, c, r = sp.Rational(112, 113), sp.Rational(224, 113), sp.Rational(15, 113)
alpha, beta = Q(1, 4), Q(1, 2)
L_lo, L_hi, pi_hi = Q(4, 25), Q(8649, 40000), Q(22, 7)
mbox = [(m, Q(112, 113), Q(1)), (s, alpha, beta)]
rho2 = 1 - m**2; a2 = rho2 + 2*m*s - s**2; k = rho2 + m*s
check("(box) 1 - (112/113)^2 == (15/113)^2", sp.Rational(1) - cp**2 == r**2)

# (P3.1)
check("(P3.1.i) 3a^4/16 - k a^2/2 + k^2/2 == (3/16)(a^2 - 4k/3)^2 + k^2/6;  a^2 - 4k/3 == (2ms - 3s^2 - rho^2)/3",
      sp.expand(sp.Rational(3, 16)*a2**2 - k*a2/2 + k**2/2 - (sp.Rational(3, 16)*(a2 - 4*k/3)**2 + k**2/6)) == 0 and
      sp.expand(a2 - 4*k/3 - (2*m*s - 3*s**2 - rho2)/3) == 0)
check("(P3.1.i) a^2 == 1 - (m-s)^2,  k == 1 - m(m-s)", sp.expand(a2 - (1 - (m - s)**2)) == 0 and sp.expand(k - (1 - m*(m - s))) == 0)
mn = bern_min(sp.expand(2*m*s - 3*s**2 - rho2), mbox)
check("(P3.1.ii) 2ms - 3s^2 - rho^2 >= 0 on m in [112/113,1], s in [1/4,1/2]", mn >= 0, f"Bernstein lower bound = {mn}")
A = 1 - (cp - s)**2; K = r**2 + cp*s
B = s**2*(1 - (1 - R(L_hi))*s)**2*A/4 + (r**2/3)*((2*s - 3*s**2)**2/48 + K**2/6)
bracket = s**2*(m - (1 - L)*s)**2*a2/4 + (rho2/3)*(sp.Rational(3, 16)*a2**2 - k*a2/2 + k**2/2)
check("(P3.1.iii) m - (1-L)s > 0 on the box", Q(112, 113) - (1 - L_lo)*beta > 0)
check("(P3.1.iii) (m-s)^2 >= (c'-s)^2 (a^2 <= A) and m(m-s) >= c'(c'-s) (k <= K) on the box",
      bern_min(sp.expand((m - s)**2 - (cp - s)**2), mbox) >= 0 and bern_min(sp.expand(m*(m - s) - cp*(cp - s)), mbox) >= 0)
mn = bern_min(sp.expand(B - bracket), [(L, L_lo, L_hi)] + mbox)
check("(P3.1) B(s) - bracket(L,m,s) >= 0 on the box x [1/4,1/2] (direct 3-variable Bernstein)", mn >= 0, f"lower bound = {mn}")

# (P3.2)
c1, c2, c3 = Q(14085, 10000), Q(63, 10000), Q(3551, 10000)
Pt = R(c1)*t**2 + R(c2) - R(c3)*t**4                       # T(s) - r = P(t)/t,  t = sqrt(s)
tbox = [(t, Q(1, 2), Q(7072, 10000))]
check("(P3.2) [1/2, sqrt(1/2)] inside [1/2, 7072/10000]", Q(7072, 10000)**2 >= Q(1, 2))
mnP = bern_min(Pt, tbox); mnP2 = bern_min(sp.expand(Pt**2 - t**2*A.subs(s, t**2)), tbox)
check("(P3.2) P(t) >= 0 on t-box", mnP > 0, f"lower bound = {mnP}")
check("(P3.2) P(t)^2 - t^2 A(t^2) >= 0 on t-box  (=> a + rho <= sqrt(A) + r <= T(s))", mnP2 >= 0, f"lower bound = {mnP2}")
check("(P3.2) a >= rho (a^2 - rho^2 == s(2m-s)), c - s > 0, L s^2 >= (4/25) s^2", sp.expand(a2 - rho2 - s*(2*m - s)) == 0 and c - R(beta) > 0 and L_lo == Q(4, 25))
t0 = Q(805, 1000)
mnT = bern_min(sp.expand(Pt + (r - R(t0))*t), tbox)       # t*(T - t0) = P(t) + (r - t0) t  >= 0  <=>  T >= t0
check("(P3.2) T(s) >= t0 = 805/1000 on [1/4,1/2]", mnT >= 0, f"lower bound of t(T - t0) = {mnT}")
ct = c + R(t0)/10
kappa5 = Q(11637, 10000)
check("(P3.2) kappa5 >= (17/16)^{5/2}  (kappa5^2 >= (17/16)^5)  [Cauchy-Schwarz, kappa = 1/4: 1 + kappa^2 = 17/16]", kappa5**2 >= Q(17, 16)**5, f"c~ = {ct} (~{float(ct):.5f})")

# (P3.3), (P3.4)
sbox = [(s, alpha, beta)]
Wq = (cp - s)**2 + sp.Rational(4, 25)*(2*cp*s - s**2)
check("(P3.3) 2c's - s^2 >= 0 and L a^2 >= (4/25)(2c's - s^2) on the box; Wq > 0 on [1/4,1/2]",
      bern_min(sp.expand(2*cp*s - s**2), sbox) >= 0 and bern_min(sp.expand(L*a2 - sp.Rational(4, 25)*(2*cp*s - s**2)), [(L, L_lo, L_hi)] + mbox) >= 0 and bern_min(sp.expand(Wq), sbox) > 0)
check("(P3.3) w^2 - Wq == (m-s)^2 - (c'-s)^2 + L a^2 - (4/25)(2c's - s^2)  [identity, both differences >= 0]",
      sp.expand(((m - s)**2 + L*a2) - Wq - ((m - s)**2 - (cp - s)**2 + L*a2 - sp.Rational(4, 25)*(2*cp*s - s**2))) == 0)
Wq1, Wq2 = sp.diff(Wq, s), sp.diff(Wq, s, 2)
check("(P3.4) Wq' == (42/25)(s - c') < 0 on [1/4,1/2]", sp.expand(Wq1 - sp.Rational(42, 25)*(s - cp)) == 0 and bern_min(sp.expand(-Wq1), sbox) > 0)
cvx = bern_min(sp.expand(sp.Rational(3, 4)*Wq1**2 - Wq*Wq2/2), sbox)
check("(P3.4) (3/4)Wq'^2 - (1/2)Wq Wq'' >= 0 on [1/4,1/2]  (=> Wq^{-1/2} convex); c~ > 1/2", cvx >= 0 and ct > R(beta), f"lower bound = {cvx}")
def W_upper(s0):
    wq = toQ(Wq.subs(s, R(s0)))
    q = Q(math.ceil(10**6/math.sqrt(float(wq))) + 1, 10**6)       # float only proposes q; the assertion is exact
    assert q*q*wq >= 1
    return q/(toQ(ct) - s0)**5, q, wq
W_a, q_a, wq_a = W_upper(alpha); W_b, q_b, wq_b = W_upper(beta)
check("(P3.4) W_a >= W(alpha), W_b >= W(beta)  (q^2 Wq >= 1), both > 0", q_a**2*wq_a >= 1 and q_b**2*wq_b >= 1 and W_a > 0 and W_b > 0, f"W_a = {W_a} (~{float(W_a):.5f}), W_b = {W_b} (~{float(W_b):.5f})")
ell = R(W_a) + R(W_b - W_a)*(s - R(alpha))/R(beta - alpha)

# (P3.5)
T = R(c1)*t + r + R(c2)/t - R(c3)*t**3
M = sp.expand((B*ell).subs(s, t**2)*T**5/t**10)
terms = {}
for term in sp.Add.make_args(M):
    coeff, pw = term.as_coeff_exponent(t); terms[int(pw)] = terms.get(int(pw), Q(0)) + toQ(coeff)
check("(P3.5) M >= 0 on [1/4,1/2]: A > 0 (so B >= 0), T - r = P(t)/t >= 0, ell > 0", bern_min(sp.expand(A), sbox) > 0 and mnP > 0 and W_a > 0 and W_b > 0)
check("(P3.5) M(t) expanded as finite Laurent polynomial in t with rational coefficients", all(isinstance(v, Q) for v in terms.values()), f"powers {min(terms)}..{max(terms)}, {len(terms)} terms")

# (P3.6)
s2_lo, s2_hi = Q(14142, 10000), Q(14143, 10000)
check("(P3.6) sqrt(2) in [14142/10000, 14143/10000]", s2_lo**2 <= 2 <= s2_hi**2)
def exp_lower(x, N=25): return sum(x**n/factorial(n) for n in range(N + 1))
def exp_upper(x, N=25): return exp_lower(x, N) + x**(N + 1)/factorial(N + 1)/(1 - x/(N + 2))
ln_lo, ln_hi = Q(6931, 10000), Q(6932, 10000)
check("(P3.6) ln 2 in [6931/10000, 6932/10000]  (exp(ln_hi) >= 2 >= exp(ln_lo), exact Taylor bounds)", exp_lower(ln_hi) >= 2 and exp_upper(ln_lo) <= 2)
def beta_pow(j):
    """interval for beta^{j/2} = 2^{-j/2}, j integer."""
    if j % 2 == 0: v = Q(2)**(-(j//2)); return v, v
    base = Q(2)**(-((j + 1)//2))                       # 2^{-j/2} = 2^{-(j+1)/2} * sqrt(2)
    return base*s2_lo, base*s2_hi
def int_s_pow(j):
    """interval for int_{1/4}^{1/2} s^{j/2} ds."""
    q = Q(j, 2) + 1
    if q == 0: return ln_lo, ln_hi
    aq = Q(2)**(-(j + 2))                              # alpha^q = (1/4)^{(j+2)/2} = 2^{-(j+2)}, exact
    blo, bhi = beta_pow(j + 2)
    if q > 0: return (blo - aq)/q, (bhi - aq)/q
    return (aq - bhi)/(-q), (aq - blo)/(-q)
check("(P3.6) all intervals consistent (lo <= hi)", all(int_s_pow(j)[0] <= int_s_pow(j)[1] for j in terms))
total_hi = Q(0)
for j, cj in terms.items():
    lo, hi = int_s_pow(j); total_hi += cj*hi if cj > 0 else cj*lo
U3 = 2*pi_hi*2*L_hi*pi_hi*kappa5*total_hi
print(f"int_(1/4)^(1/2) M(s) ds <= {total_hi}  (~{float(total_hi):.6f})")
print(f"U_3 <= 2 pi * 2 lambda^2 pi * kappa5 * int M = {U3}  (~{float(U3):.5f})   [valid for all parameters in the box]")
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED")
raise SystemExit(0 if ok else 1)
