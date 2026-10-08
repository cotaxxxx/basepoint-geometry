"""Contract 45, piece 1 of the north-far majorant (method (A)): exact rational upper bound U_1 for the contribution of
I_1 = [rho, max(rho, 1/10)]  to  U_north.   Paper proof + exact arithmetic; no diagnostic value enters any constant.

SETTING (P units, contract 21'' v1.1): north far = { mu in (mu_C, m - rho) } = { s := m - mu in (rho, m - mu_C) } subset (rho, 1/2]
(1/2 < mu_C).  Enlarging the s-range to [rho, 1/2] only increases the one-sided bound below (integrand >= 0).
Pieces (predeclared, approved): I_1 = [rho, max(rho,1/10)],  I_2 = [max(rho,1/10), 1/4],  I_3 = [1/4, 1/2]; no phi split.
Symbols as in n3_identities_cert.py (contract 44): a^2 = rho^2 + 2ms - s^2, b = a cos phi, k := rho^2 + m s, h = lambda(k - xi b),
D^2 = (b-xi)^2 + a^2 - b^2 + L s^2, w^2 = (m-s)^2 + L a^2, N = N_0 - xi N_1 with N_0 = lambda b s (m - (1-L) s), N_1 = lambda (b^2 - k).
Box: L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2 in [0, (15/113)^2].

CHAIN (every step one-sided, direction stated):
 (S0) [-K_H]_+ <= (pi/(2 rho)) int_{-rho}^{rho} M dxi,  M := [2N^2 - h^2 T]_+/(w D^5) <= 2 N^2/(w D^5)   (N3 = contract 44, audited).
      U_north <= int_s int_0^pi (mean_xi pi M) dphi ds = 2 int_s int_0^{pi/2} (mean_xi pi M) dphi ds,  by the pairing
      (xi, phi) -> (-xi, pi - phi), under which M is invariant (b -> -b, xi -> -xi: N -> -N, D, h, w unchanged).
 (S1) D^2 >= D_0^2 := (a - rho)^2 + L s^2 for ALL |xi| <= rho and all phi (requires a >= rho, true on north far since
      a^2 - rho^2 = s(2m - s) >= 0).  Proof: D^2 - L s^2 = a^2 - 2 b xi + xi^2.  If |b| >= rho: >= a^2 - 2|b| rho + rho^2 and
      a^2 - 2|b|rho + rho^2 - (a-rho)^2 = 2 rho (a - |b|) >= 0.  If |b| < rho: >= a^2 - b^2 and a^2 - b^2 - (a-rho)^2 = 2 a rho - rho^2 - b^2
      >= 2 rho (a - rho) >= 0.   D_0 does not depend on xi or phi; it is substituted BEFORE the xi-average.
 (S2) mean_xi N^2 = N_0^2 + (rho^2/3) N_1^2  (exact; N linear in xi, odd cross term integrates to 0).  Hence
      mean_xi 2N^2/(w D^5) <= 2 (N_0^2 + rho^2 N_1^2/3)/(w D_0^5).
 (S3) phi-integrals on [0, pi/2] (b = a cos phi): int b^2 = pi a^2/4, int b^4 = 3 pi a^4/16, int 1 = pi/2, so
      F(s) := int_0^{pi/2} 2(N_0^2 + rho^2 N_1^2/3) dphi
            = 2 lambda^2 [ s^2 (m-(1-L)s)^2 a^2 pi/4 + (rho^2/3)(3 pi a^4/16 - pi k a^2/2 + pi k^2/2) ],
      and  U_north <= 2 pi int_{rho}^{1/2} F(s)/(w(s) D_0(s)^5) ds.   (w, D_0, F depend on s only.)
 PIECE 1, s in I_1:
 (P1.1) If rho >= 1/10, I_1 is empty and U_1 = 0.  Otherwise rho < 1/10, so m^2 = 1 - rho^2 > 99/100 > (99/100)^2, m > 99/100.
 (P1.2) Upper bounds valid for rho <= s <= 1/10 (one-sided, using rho <= s, m <= 1, L <= 1):
        a^2 <= rho^2 + 2 m s <= s^2 + 2 s;  k <= s^2 + s;  rho^2 <= s^2;  (m - (1-L)s)^2 <= m^2 <= 1;  -pi k a^2/2 <= 0 dropped.
        => F(s) <= 2 lambda^2 pi s^3 P(s),  P(s) := (s+2)/4 + (s/3)( 3(s+2)^2/16 + (s+1)^2/2 ).
 (P1.3) Lower bounds: w >= m - s >= 99/100 - 1/10 = 89/100;  D_0 >= a - rho = s(2m - s)/(a + rho)  with
        2m - s >= 198/100 - 1/10 = 47/25 and a + rho <= sqrt(s^2 + 2s) + s = sqrt(s)(sqrt(s+2) + sqrt(s)),  so
        D_0^5 >= s^5 (47/25)^5 / ( s^{5/2} (sqrt(s+2)+sqrt(s))^5 ).
 (P1.4) Therefore F/(w D_0^5) <= C * sqrt(s) * P(s) * (sqrt(s+2) + sqrt(s))^5,  C := 2 lambda^2 pi / ((89/100)(47/25)^5),
        and (sqrt(s+2)+sqrt(s))^5 is increasing, <= K_1 := (sqrt(21/10) + sqrt(1/10))^5 on I_1.
 (P1.5) U_1 <= 2 pi * C * K_1 * int_0^{1/10} sqrt(s) P(s) ds   (extending the lower limit rho -> 0 is one-sided).
        The integral is closed-form: int_0^{t} s^{j+1/2} ds = t^{j+3/2}/(j + 3/2).  Rational upper bounds used: pi <= 22/7,
        lambda^2 <= 8649/40000, sqrt(1/10) <= 3163/10000, sqrt(21/10) <= 14492/10000  (each checked by squaring).
"""
from fractions import Fraction as Q
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

# --- exact identities (S2), (S3), (S1) case algebra -------------------------------------------------------------
lam, L, m, rho, s, b, xi, phi = sp.symbols('lambda L m rho s b xi phi', real=True)
k = rho**2 + m*s
N0 = lam*b*s*(m - (1 - L)*s); N1 = lam*(b**2 - k); N = N0 - xi*N1
mean = sp.integrate(N**2, (xi, -rho, rho))/(2*rho)
check("(S2) mean_xi N^2 == N_0^2 + rho^2 N_1^2/3", sp.expand(mean - (N0**2 + rho**2*N1**2/3)) == 0)
a = sp.symbols('a', positive=True)
I2 = sp.integrate((a*sp.cos(phi))**2, (phi, 0, sp.pi/2)); I4 = sp.integrate((a*sp.cos(phi))**4, (phi, 0, sp.pi/2))
check("(S3) int_0^{pi/2} b^2 = pi a^2/4, int b^4 = 3 pi a^4/16", sp.simplify(I2 - sp.pi*a**2/4) == 0 and sp.simplify(I4 - 3*sp.pi*a**4/16) == 0)
bb = sp.symbols('b', real=True)
check("(S1) case |b|>=rho: a^2 - 2|b|rho + rho^2 - (a-rho)^2 == 2 rho (a - |b|)", sp.expand(a**2 - 2*bb*rho + rho**2 - (a - rho)**2 - 2*rho*(a - bb)) == 0)
check("(S1) case |b|<rho: a^2 - b^2 - (a-rho)^2 == 2 a rho - rho^2 - b^2", sp.expand(a**2 - bb**2 - (a - rho)**2 - (2*a*rho - rho**2 - bb**2)) == 0)
Fs = 2*lam**2*(s**2*(m - (1 - L)*s)**2*a**2*sp.pi/4 + (rho**2/3)*(3*sp.pi*a**4/16 - sp.pi*k*a**2/2 + sp.pi*k**2/2))
Fdirect = sp.integrate(2*(N0**2 + rho**2*N1**2/3).subs(b, a*sp.cos(phi)), (phi, 0, sp.pi/2))
check("(S3) F(s) closed form equals the phi-integral", sp.simplify(sp.expand(Fdirect - Fs)) == 0)

# --- piece-1 rational constants (P1.1)-(P1.5) -----------------------------------------------------------------
check("(P1.1) (99/100)^2 < 99/100  (so rho < 1/10 => m > 99/100)", Q(99, 100)**2 < Q(99, 100))
check("(P1.3) w lower bound 99/100 - 1/10 = 89/100 and 2m - s >= 198/100 - 1/10 = 47/25", Q(99, 100) - Q(1, 10) == Q(89, 100) and Q(198, 100) - Q(1, 10) == Q(47, 25))
r10, r21 = Q(3163, 10000), Q(14492, 10000)
check("(P1.5) sqrt(1/10) <= 3163/10000, sqrt(21/10) <= 14492/10000", r10**2 >= Q(1, 10) and r21**2 >= Q(21, 10))
K1 = (r21 + r10)**5
pi_hi, lam2_hi = Q(22, 7), Q(8649, 40000)
C_hi = 2*lam2_hi*pi_hi/(Q(89, 100)*Q(47, 25)**5)
# P(s) = (s+2)/4 + (s/3)(3(s+2)^2/16 + (s+1)^2/2) as polynomial coefficients; int_0^{1/10} sqrt(s) P(s) ds
Ps = sp.Poly(sp.expand((s + 2)/4 + (s/3)*(3*(s + 2)**2/16 + (s + 1)**2/2)), s)
coeffs = {int(mon[0]): Q(int(sp.fraction(c)[0]), int(sp.fraction(c)[1])) for mon, c in zip(Ps.monoms(), Ps.coeffs())}
check("(P1.2) P(s) has nonnegative coefficients (so P increasing, bounds one-sided)", all(c >= 0 for c in coeffs.values()), f"P = {dict(sorted(coeffs.items()))}")
t = Q(1, 10)
# int_0^t s^{j+1/2} ds = t^{j+3/2}/(j+3/2) = t^{j+1} * sqrt(t) / (j+3/2)  <= t^{j+1} * r10 / (j+3/2)
I_up = sum(c*t**(j + 1)*r10/(Q(j) + Q(3, 2)) for j, c in coeffs.items())
U1 = 2*pi_hi*C_hi*K1*I_up
print(f"K_1 upper = {K1} (~{float(K1):.4f});  C upper = {C_hi} (~{float(C_hi):.5f});  int_0^(1/10) sqrt(s)P(s) ds <= {I_up} (~{float(I_up):.6f})")
print(f"U_1 <= 2 pi C K_1 I = {U1}  (~{float(U1):.5f})   [valid for all parameters; U_1 = 0 when rho >= 1/10]")
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED")
raise SystemExit(0 if ok else 1)
