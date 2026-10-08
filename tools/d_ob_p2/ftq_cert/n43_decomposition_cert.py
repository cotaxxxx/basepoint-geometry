"""Contract 43 preliminaries (near band): exact decomposition of N and a rho-uniform pointwise bound |N| <= C D^2.

Symbols as in n3_identities_cert.py (contract 44, commit 79588e2): a^2 = rho^2 + 2ms - s^2, b = a cos phi,
D^2 = (b - xi)^2 + a^2 sin^2 phi + L s^2,  N = lambda [ b s (m - (1-L) s) - xi (b^2 - rho^2 - m s) ].
New local symbols:  p := b - xi,  q := a sin phi   (so D^2 = p^2 + q^2 + L s^2;  these p, q are NOT the FT_q p, q).

 (43.1)  N = lambda [ b (q^2 + L s^2) + p ( s (m - s) - q^2 ) ]          [exact identity, certified below]
 (43.2)  pointwise, for every (s, xi, phi) with D > 0 and every parameter (valid on the WHOLE mu-range, s in [m-1, 1+m]):
         |N| <= lambda |b| (q^2 + L s^2) + lambda |p| |s| |m - s| + lambda |p| q^2
             <= lambda |b| D^2 + lambda |m - s| D^2/(2 sqrt L) + lambda (|q|/2) D^2          (AM-GM: |p||s| sqrt L <= D^2/2, |p| q^2 <= |q| D^2/2)
             =  C D^2,   C := lambda |b| + |m - s|/2 + lambda |q|/2  <=  (3/2) lambda a + |m - s|/2.
         In particular N/D^2 is uniformly bounded in rho (answer to Astra Q1, pointwise version).  This bound is NOT
         sufficient for the integral (the chain 2C^2/(wD) is diagnostically ~4, see diagnostics/near_band_majorant_forms.py).
 (43.3)  at phi = 0 (q = 0):  N = lambda s [ (a - xi)(m - s) + a L s ],  D^2 = (a - xi)^2 + L s^2;  at xi = a:  N/D^2 = lambda a.
"""
import sympy as sp
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'}", flush=True)
lam, L, m, rho, s, xi, phi = sp.symbols('lambda L m rho s xi phi', real=True)
a = sp.symbols('a', positive=True)
b = a*sp.cos(phi); q = a*sp.sin(phi); p = b - xi
N = lam*(b*s*(m - (1 - L)*s) - xi*(b**2 - rho**2 - m*s))
N_dec = lam*(b*(q**2 + L*s**2) + p*(s*(m - s) - q**2))
# use a^2 = rho^2 + 2ms - s^2 (eliminate rho^2) and sin^2 = 1 - cos^2
d = sp.expand((N - N_dec).subs(rho**2, a**2 - 2*m*s + s**2).rewrite(sp.cos))
d = sp.simplify(sp.expand_trig(d))
check("(43.1) N == lambda[b(q^2+Ls^2) + p(s(m-s)-q^2)]", d == 0)
check("(43.1') D^2 == p^2 + q^2 + L s^2 with q = a sin phi (a^2 - b^2 = q^2)", sp.simplify((p**2 + q**2 + L*s**2) - ((b - xi)**2 + (a**2 - b**2) + L*s**2)) == 0)
N0 = N.subs(phi, 0); check("(43.3) phi = 0: N == lambda s[(a - xi)(m - s) + a L s]", sp.simplify(sp.expand(N0.subs(rho**2, a**2 - 2*m*s + s**2) - lam*s*((a - xi)*(m - s) + a*L*s))) == 0)
check("(43.3) phi = 0, xi = a: N/D^2 == lambda a", sp.simplify(N0.subs(rho**2, a**2 - 2*m*s + s**2).subs(xi, a)/(L*s**2) - lam*a) == 0)
# AM-GM steps used in (43.2), as polynomial identities / nonnegativity:
P, Qs, S = sp.symbols('P Q S', real=True)  # P=|p|, Q=|q|, S=sqrt(L)|s|
check("(43.2) D^2/2 - |p| sqrt(L)|s| == (|p| - sqrt(L)|s|)^2/2 + q^2/2 >= 0", sp.expand((P**2 + Qs**2 + S**2)/2 - P*S - ((P - S)**2/2 + Qs**2/2)) == 0)
check("(43.2) |q| D^2/2 - |p| q^2 == |q|(|p| - |q|)^2/2 + |q| S^2/2 >= 0", sp.expand(Qs*(P**2 + Qs**2 + S**2)/2 - P*Qs**2 - (Qs*(P - Qs)**2/2 + Qs*S**2/2)) == 0)
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED"); raise SystemExit(0 if ok else 1)
