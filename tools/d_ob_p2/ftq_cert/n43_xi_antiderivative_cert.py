"""Contract 43, step (C3) preparation: closed-form xi-antiderivatives, certified by DIFFERENTIATION ONLY.

Scope (chat authorization 2026-10-09): algebraic identity verification of antiderivatives.  NO definite-integral evaluation,
NO majorant certification, NO budget comparison is performed here.

Setting: p := b - xi (so dxi = -dp, the xi-range |xi| <= rho is p in [b - rho, b + rho]), e^2 := a^2 sin^2 phi + L s^2 held fixed
during the xi-integration, D^2 = p^2 + e^2, e > 0 (e = 0 only on the null set sin phi = 0, s = 0).
The two xi-structures that appear in the retained chain (C1)-(C3) of the predeclare draft are D^{-5} and p^2 D^{-5}.

 (C3.1)  d/dp [ p (2 p^2 + 3 e^2) / ( 3 e^4 (p^2 + e^2)^{3/2} ) ]  =  (p^2 + e^2)^{-5/2}
 (C3.2)  d/dp [ p^3 / ( 3 e^2 (p^2 + e^2)^{3/2} ) ]                 =  p^2 (p^2 + e^2)^{-5/2}
 (C3.3)  both antiderivatives are odd in p; the integrands are nonnegative for e > 0 (so the antiderivatives are increasing).
         No bound on the definite integrals is asserted here.
"""
import sympy as sp
ok = True
def check(name, cond):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'}", flush=True)
p = sp.symbols('p', real=True); e = sp.symbols('e', positive=True)
F1 = p*(2*p**2 + 3*e**2)/(3*e**4*(p**2 + e**2)**sp.Rational(3, 2))
F2 = p**3/(3*e**2*(p**2 + e**2)**sp.Rational(3, 2))
check("(C3.1) d/dp F1 == (p^2+e^2)^(-5/2)", sp.simplify(sp.diff(F1, p) - (p**2 + e**2)**sp.Rational(-5, 2)) == 0)
check("(C3.2) d/dp F2 == p^2 (p^2+e^2)^(-5/2)", sp.simplify(sp.diff(F2, p) - p**2*(p**2 + e**2)**sp.Rational(-5, 2)) == 0)
check("(C3.3) F1, F2 odd in p", sp.simplify(F1.subs(p, -p) + F1) == 0 and sp.simplify(F2.subs(p, -p) + F2) == 0)
check("(C3.3) p^2 + e^2 > 0 for e > 0 (so (p^2+e^2)^(-5/2) > 0 and p^2 (p^2+e^2)^(-5/2) >= 0)", sp.ask(sp.Q.positive(p**2 + e**2)) is True)
print("ALL CERTIFICATES PASS" if ok else "SOME CERTIFICATE FAILED"); raise SystemExit(0 if ok else 1)
