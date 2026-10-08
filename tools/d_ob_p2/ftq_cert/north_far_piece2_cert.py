"""Contract 45, piece 2 of the north-far majorant (method (A)): exact rational upper bound U_2 for the contribution of
I_2 = [max(rho, 1/10), 1/4]  to  U_north.   Paper proof + exact arithmetic; no diagnostic value enters any constant.

SETTING and CHAIN (S0)-(S3) exactly as in north_far_piece1_cert.py (contract 44 audited, piece 1 CHAT AUDIT PASS):
    U_north <= 2 pi int_{rho}^{1/2} F(s) / ( w(s) D_0(s)^5 ) ds,
    F(s) = 2 lambda^2 pi [ s^2 (m - (1-L) s)^2 a^2 /4 + (rho^2/3)( 3 a^4/16 - k a^2/2 + k^2/2 ) ],
    a^2 = rho^2 + 2 m s - s^2 = 1 - (m-s)^2,   k = rho^2 + m s = 1 - m (m - s),   w^2 = (m-s)^2 + L a^2,
    D_0^2 = (a - rho)^2 + L s^2,   with a >= rho on [0, 1/2] (a^2 - rho^2 = s (2m - s) >= 0).
Box: L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2 <= r^2, r := 15/113 (exact: 1 - (112/113)^2 = (15/113)^2).
Constants: c' := 112/113 (m >= c'),  c := 2 c' = 224/113 (2m - s >= c - s > 0),  alpha := 1/10, beta := 1/4.

PIECE 2, s in I_2 = [s_lo, 1/4], s_lo := max(rho, 1/10) >= 1/10 (I_2 is never empty since r < 1/4).  All bounds below
hold for every s in [1/10, 1/4] and every parameter in the box (they do not use rho <= s), so the integrand majorant
M(s) >= 0 can be integrated over [1/10, 1/4] >= I_2 (one-sided).

 (P2.1) bracket upper bound.  (i) 3a^4/16 - k a^2/2 + k^2/2 = (3/16)(a^2 - 4k/3)^2 + k^2/6  and  a^2 - 4k/3 = (2ms - 3s^2 - rho^2)/3
        [identities].  (ii) 0 <= 2ms - 3s^2 - rho^2 <= 2s - 3s^2 on the box x [1/10,1/4]  [Bernstein for the lower bound;
        the upper bound is m <= 1, rho^2 >= 0], so (a^2 - 4k/3)^2 <= (2s - 3s^2)^2/9.  (iii) a^2 = 1 - (m-s)^2 <= 1 - (c'-s)^2 =: A(s),
        k = 1 - m(m-s) <= 1 - c'(c'-s) = r^2 + c' s =: K(s),  rho^2 <= r^2,  0 < m - (1-L)s <= 1 - (1-L_hi) s, L_hi = 8649/40000.
        => F(s) <= 2 lambda^2 pi B(s),   B(s) := s^2 (1 - (1-L_hi)s)^2 A(s)/4 + (r^2/3)( (2s - 3s^2)^2/48 + K(s)^2/6 ).
        [B - bracket >= 0 is ALSO certified directly by 3-variable Bernstein on (L, m, s).]
 (P2.2) D_0 >= a - rho = s (2m - s)/(a + rho) >= s (c - s) / T(s),   where  a + rho <= sqrt(A(s)) + r <= T(s),
        T(s) := c1 s^{1/2} + r + c2 s^{-1/2} - c3 s^{3/2},  c1 = 14085/10000, c2 = 63/10000, c3 = 3551/10000
        (motivation: tangent line of sqrt at 2c's: sqrt(A) <= sqrt(2c's) + (r^2 - s^2)/(2 sqrt(2c's)); certified directly:
        with t = sqrt(s) in [3162/10000, 1/2] >= [sqrt(1/10), 1/2],  P(t) := c1 t^2 + c2 - c3 t^4 >= 0 and P(t)^2 - t^2 A(t^2) >= 0
        [Bernstein in t], i.e. sqrt(A) <= P(t)/t = T - r.)   Hence  1/D_0^5 <= T(s)^5 / ( s^5 (c - s)^5 ).
 (P2.3) w^2 = (m-s)^2 + L a^2 >= (c'-s)^2 + (4/25)(2 c' s - s^2) =: Wq(s) > 0   (a^2 >= 2ms - s^2 >= 2c's - s^2 >= 0, L >= 4/25).
 (P2.4) W(s) := Wq(s)^{-1/2} (c - s)^{-5} is convex on [alpha, beta]:  Wq is decreasing (Wq' = (42/25)(s - c') < 0) so Wq^{-1/2}
        is positive increasing, and convex since (3/4) Wq'^2 - (1/2) Wq Wq'' >= 0 there [Bernstein]; (c-s)^{-5} is positive,
        increasing, convex (c > beta); a product of positive increasing convex functions is convex ((fg)'' = f''g + 2f'g' + fg'').
        Therefore W(s) <= ell(s) := W_a + (W_b - W_a)(s - alpha)/(beta - alpha) on [alpha, beta], with rational W_a >= W(alpha),
        W_b >= W(beta)  (checked by squaring; the chord is a convex combination so upper endpoint values are one-sided).
 (P2.5) F/(w D_0^5) <= 2 lambda_hi^2 pi_hi M(s),  M(s) := B(s) T(s)^5 ell(s) / s^5  (Laurent polynomial in sqrt(s)),  and
        U_2 <= 2 pi_hi * 2 lambda_hi^2 pi_hi * int_{1/10}^{1/4} M(s) ds,   pi_hi = 22/7, lambda_hi^2 = 8649/40000.
 (P2.6) int_{1/10}^{1/4} s^{q-1} ds = (beta^q - alpha^q)/q for q != 0 and = ln(5/2) for q = 0, evaluated in exact interval
        arithmetic: beta^q exact (powers of 1/2), alpha^q via sqrt(10) in [31622/10000, 31623/10000] (checked by squaring),
        ln(5/2) in [9162/10000, 9163/10000] (checked with exact Taylor partial sums of exp and a geometric tail bound).
        Each signed term takes the end of its interval that increases the sum.
"""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

def R(x): return sp.Rational(x.numerator, x.denominator)
def toQ(x): n, d = sp.fraction(sp.nsimplify(x)); return Q(int(n), int(d))

def bern_min(expr, box, depth=0, max_depth=6):
    """Exact Bernstein lower bound of a polynomial on a box (list of (sym, lo, hi) Fractions), with bisection on the
    widest variable when the coefficient bound is not positive, up to max_depth.  Returns a certified lower bound."""
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
alpha, beta = Q(1, 10), Q(1, 4)
L_lo, L_hi, pi_hi = Q(4, 25), Q(8649, 40000), Q(22, 7)
rho2 = 1 - m**2; a2 = rho2 + 2*m*s - s**2; k = rho2 + m*s
check("(box) 1 - (112/113)^2 == (15/113)^2  and  r < 1/4", sp.Rational(1) - cp**2 == r**2 and r < sp.Rational(1, 4))

# (P2.1)
check("(P2.1.i) 3a^4/16 - k a^2/2 + k^2/2 == (3/16)(a^2 - 4k/3)^2 + k^2/6", sp.expand(sp.Rational(3, 16)*a2**2 - k*a2/2 + k**2/2 - (sp.Rational(3, 16)*(a2 - 4*k/3)**2 + k**2/6)) == 0)
check("(P2.1.i) a^2 - 4k/3 == (2ms - 3s^2 - rho^2)/3", sp.expand(a2 - 4*k/3 - (2*m*s - 3*s**2 - rho2)/3) == 0)
check("(P2.1.i) a^2 == 1 - (m-s)^2,  k == 1 - m(m-s)", sp.expand(a2 - (1 - (m - s)**2)) == 0 and sp.expand(k - (1 - m*(m - s))) == 0)
mn = bern_min(sp.expand(2*m*s - 3*s**2 - rho2), [(m, Q(112, 113), Q(1)), (s, alpha, beta)])
check("(P2.1.ii) 2ms - 3s^2 - rho^2 >= 0 on m in [112/113,1], s in [1/10,1/4]", mn >= 0, f"Bernstein lower bound = {mn}")
A = 1 - (cp - s)**2; K = r**2 + cp*s
B = s**2*(1 - (1 - R(L_hi))*s)**2*A/4 + (r**2/3)*((2*s - 3*s**2)**2/48 + K**2/6)
bracket = s**2*(m - (1 - L)*s)**2*a2/4 + (rho2/3)*(sp.Rational(3, 16)*a2**2 - k*a2/2 + k**2/2)
check("(P2.1.iii) m - (1-L)s > 0 on the box (so the square is monotone)", Q(112, 113) - (1 - L_lo)*beta > 0)
mn = bern_min(sp.expand(B - bracket), [(L, L_lo, L_hi), (m, Q(112, 113), Q(1)), (s, alpha, beta)])
check("(P2.1) B(s) - bracket(L,m,s) >= 0 on the box x [1/10,1/4] (direct 3-variable Bernstein)", mn >= 0, f"lower bound = {mn}")

# (P2.2)
c1, c2, c3 = Q(14085, 10000), Q(63, 10000), Q(3551, 10000)
Pt = R(c1)*t**2 + R(c2) - R(c3)*t**4
tbox = [(t, Q(3162, 10000), Q(1, 2))]
check("(P2.2) [sqrt(1/10), 1/2] inside [3162/10000, 1/2]", Q(3162, 10000)**2 <= Q(1, 10))
mnP = bern_min(Pt, tbox); mnP2 = bern_min(sp.expand(Pt**2 - t**2*A.subs(s, t**2)), tbox)
check("(P2.2) P(t) >= 0 on t-box", mnP > 0, f"lower bound = {mnP}")
check("(P2.2) P(t)^2 - t^2 A(t^2) >= 0 on t-box  (=> sqrt(A) <= P(t)/t = T(s) - r)", mnP2 >= 0, f"lower bound = {mnP2}")
check("(P2.2) c - s > 0 and a >= rho: a^2 - rho^2 == s(2m-s)", c - R(beta) > 0 and sp.expand(a2 - rho2 - s*(2*m - s)) == 0)
check("(P2.2) (m-s)^2 >= (c'-s)^2 on the box (so a^2 <= A), and k <= K: 1 - m(m-s) <= 1 - c'(c'-s)",
      bern_min(sp.expand((m - s)**2 - (cp - s)**2), [(m, Q(112, 113), Q(1)), (s, alpha, beta)]) >= 0 and
      bern_min(sp.expand(m*(m - s) - cp*(cp - s)), [(m, Q(112, 113), Q(1)), (s, alpha, beta)]) >= 0)

# (P2.3), (P2.4)
Wq = (cp - s)**2 + sp.Rational(4, 25)*(2*cp*s - s**2)
check("(P2.3) w^2 - Wq == (m-s)^2 - (c'-s)^2 + L a^2 - (4/25)(2c's - s^2)  [identity]; Wq > 0 on [1/10,1/4]",
      sp.expand(((m - s)**2 + L*a2) - Wq - ((m - s)**2 - (cp - s)**2 + L*a2 - sp.Rational(4, 25)*(2*cp*s - s**2))) == 0 and bern_min(sp.expand(Wq), [(s, alpha, beta)]) > 0)
check("(P2.3) 2 c' s - s^2 >= 0 on [1/10,1/4], L a^2 >= (4/25)(2c's - s^2)", bern_min(sp.expand(2*cp*s - s**2), [(s, alpha, beta)]) >= 0 and bern_min(sp.expand(L*a2 - sp.Rational(4, 25)*(2*cp*s - s**2)), [(L, L_lo, L_hi), (m, Q(112, 113), Q(1)), (s, alpha, beta)]) >= 0)
Wq1, Wq2 = sp.diff(Wq, s), sp.diff(Wq, s, 2)
check("(P2.4) Wq' == (42/25)(s - c') < 0 on [1/10,1/4]", sp.expand(Wq1 - sp.Rational(42, 25)*(s - cp)) == 0 and bern_min(sp.expand(-Wq1), [(s, alpha, beta)]) > 0)
check("(P2.4) (3/4)Wq'^2 - (1/2)Wq Wq'' >= 0 on [1/10,1/4]  (=> Wq^{-1/2} convex)", bern_min(sp.expand(sp.Rational(3, 4)*Wq1**2 - Wq*Wq2/2), [(s, alpha, beta)]) >= 0,
      f"lower bound = {bern_min(sp.expand(sp.Rational(3, 4)*Wq1**2 - Wq*Wq2/2), [(s, alpha, beta)])}")
def W_upper(s0):
    """rational upper bound of Wq(s0)^{-1/2} (c - s0)^{-5}: find q with q^2 Wq(s0) >= 1."""
    wq = toQ(Wq.subs(s, R(s0)))
    import math
    q = Q(math.ceil(10**6/math.sqrt(float(wq))) + 1, 10**6)
    assert q*q*wq >= 1
    return q/(toQ(c) - s0)**5, q, wq
W_a, q_a, wq_a = W_upper(alpha); W_b, q_b, wq_b = W_upper(beta)
check("(P2.4) W_a >= W(alpha), W_b >= W(beta)  (q^2 Wq >= 1)", q_a**2*wq_a >= 1 and q_b**2*wq_b >= 1, f"W_a = {W_a} (~{float(W_a):.5f}), W_b = {W_b} (~{float(W_b):.5f})")
ell = R(W_a) + R(W_b - W_a)*(s - R(alpha))/R(beta - alpha)

# (P2.5) majorant M(s) as Laurent polynomial in t = sqrt(s)
T = R(c1)*t + r + R(c2)/t - R(c3)*t**3
M = sp.expand((B*ell).subs(s, t**2)*T**5/t**10)
terms = {}
for term in sp.Add.make_args(M):
    coeff, pw = term.as_coeff_exponent(t); terms[int(pw)] = terms.get(int(pw), Q(0)) + toQ(coeff)
check("(P2.5) M >= 0 on [1/10,1/4]: A > 0 (so B >= 0), T - r = P(t)/t >= 0, W_a, W_b > 0 (so ell > 0)",
      bern_min(sp.expand(A), [(s, alpha, beta)]) > 0 and mnP > 0 and W_a > 0 and W_b > 0)
check("(P2.5) M(t) expanded as finite Laurent polynomial in t with rational coefficients", all(isinstance(v, Q) for v in terms.values()), f"powers {min(terms)}..{max(terms)}, {len(terms)} terms")

# (P2.6) exact interval integration
s10_lo, s10_hi = Q(31622, 10000), Q(31623, 10000)
check("(P2.6) sqrt(10) in [31622/10000, 31623/10000]", s10_lo**2 <= 10 <= s10_hi**2)
def exp_lower(x, N=25): return sum(x**n/factorial(n) for n in range(N + 1))
def exp_upper(x, N=25): return exp_lower(x, N) + x**(N + 1)/factorial(N + 1)/(1 - x/(N + 2))
ln_lo, ln_hi = Q(9162, 10000), Q(9163, 10000)
check("(P2.6) ln(5/2) in [9162/10000, 9163/10000]  (exp(ln_hi) >= 5/2 >= exp(ln_lo), exact Taylor bounds)", exp_lower(ln_hi) >= Q(5, 2) and exp_upper(ln_lo) <= Q(5, 2))
def alpha_pow(j):
    """interval for alpha^{j/2} = 10^{-j/2}, j integer."""
    if j % 2 == 0: v = Q(10)**(-(j//2)); return v, v
    base = Q(10)**(-((j + 1)//2))                    # 10^{-j/2} = 10^{-(j+1)/2} * sqrt(10)
    return base*s10_lo, base*s10_hi
def int_s_pow(j):
    """interval for int_{1/10}^{1/4} s^{j/2} ds."""
    q = Q(j, 2) + 1
    if q == 0: return ln_lo, ln_hi
    bq = Q(1, 4)**q if q.denominator == 1 else Q(1, 2)**int(2*q)   # beta^q = 2^{-2q}
    alo, ahi = alpha_pow(j + 2)                                    # alpha^q = alpha^{(j+2)/2}
    if q > 0: return (bq - ahi)/q, (bq - alo)/q
    return (alo - bq)/(-q), (ahi - bq)/(-q)
total_hi = Q(0)
for j, cj in terms.items():
    lo, hi = int_s_pow(j); total_hi += cj*hi if cj > 0 else cj*lo
check("(P2.6) all intervals consistent (lo <= hi)", all(int_s_pow(j)[0] <= int_s_pow(j)[1] for j in terms))
U2 = 2*pi_hi*2*L_hi*pi_hi*total_hi
print(f"int_(1/10)^(1/4) M(s) ds <= {total_hi}  (~{float(total_hi):.6f})")
print(f"U_2 <= 2 pi * 2 lambda^2 pi * int M = {U2}  (~{float(U2):.5f})   [valid for all parameters in the box]")
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED")
raise SystemExit(0 if ok else 1)
