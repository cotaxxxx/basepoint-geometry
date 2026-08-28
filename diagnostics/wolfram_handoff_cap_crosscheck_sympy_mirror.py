"""SymPy mirror of diagnostics/wolfram_handoff_cap_crosscheck.wl.

Evidence class:   SYMBOLIC_CROSSCHECK / NOT_BINDING
Derivation class: EXACT for the symbolic identities;
                  HIGH_PRECISION (60 working digits, 50 reported digits)
                  for the direct sample residuals.

This runs the same eight load-bearing checks as the Wolfram hand-off script,
in the same order and under the same labels, through a different computer
algebra system. It exists so that the hand-off can be checked without a
Wolfram kernel, and so that a disagreement between the two systems is visible.

It is not a substitute for the Wolfram run requested by
`wolfram_handoff_cap_crosscheck.md`: two systems agreeing is the point.
It certifies no interval, replaces no interval checker, and promotes no
numerical value.

Requires SymPy. Run from the repository root:

    python3 diagnostics/wolfram_handoff_cap_crosscheck_sympy_mirror.py

Expected exit status is zero and the expected final line is failure_count=0.
"""
import sympy as sp
from sympy import Rational as R

mu, t, lam, symR, symSign, ang, at, att, z, u = sp.symbols(
    'mu t lam symR symSign ang at att z u')
fails = []
def report(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok: fails.append(label)

aFn  = lambda m, tv, l: 1 - tv*m
qFn  = lambda m, tv, l: 1 - m**2 + l**2*(m - tv)**2
w2Fn = lambda m, tv, l: l**2*(1 - m**2) + m**2
cFn  = lambda m, tv, l: (1 - l**2)*m + l**2*tv
nFn  = lambda m, tv, l: -m*qFn(m,tv,l) - aFn(m,tv,l)*l**2*(tv - m)
gamFn= lambda m, tv, l: l*aFn(m,tv,l)/(sp.sqrt(w2Fn(m,tv,l))*sp.sqrt(qFn(m,tv,l)))
alFn = lambda m, tv, l: sp.acos(gamFn(m,tv,l))

symA, symQ, symW2, symC, symN = (aFn(mu,t,lam), qFn(mu,t,lam), w2Fn(mu,t,lam),
                                 cFn(mu,t,lam), nFn(mu,t,lam))
rels = [symR**2 - (1 - mu**2), symSign**2 - 1]
def clear_and_reduce(e):
    num = sp.expand(sp.numer(sp.together(sp.expand(e))))
    return sp.expand(sp.reduced(num, rels, [symR, symSign])[1])

report("check1_N_equals_minus_one_minus_mu2_times_C",
       sp.expand(symN + (1-mu**2)*symC) == 0)
report("check2_complement_identity_w2q_minus_lam2A2",
       sp.expand(symW2*symQ - lam**2*symA**2 - (1-mu**2)*symC**2) == 0)

aT  = lam*symR*symSign/symQ
aTT = -2*lam**3*symR*symSign*(t - mu)/symQ**2
report("check3_gamma_t_equals_lam_N_over_w_q_three_halves",
       sp.simplify(sp.diff(gamFn(mu,t,lam), t)
                   - lam*symN/(sp.sqrt(symW2)*symQ**sp.Rational(3,2))) == 0)
cleared = -(symR*symSign*symC)*aT*symQ - lam*symN
report("check3_alpha_t_cleared_polynomial_identity", clear_and_reduce(cleared) == 0)
report("check3_alpha_tt_is_t_derivative_of_alpha_t",
       clear_and_reduce(sp.diff(aT, t) - aTT) == 0)
for sv, lab in ((1,"C_positive"), (-1,"C_negative")):
    sub = {symSign: sv, symR: sp.sqrt(1-mu**2)}
    report(f"check3_branch_{lab}_alpha_t", sp.simplify(cleared.subs(sub)) == 0)
    report(f"check3_branch_{lab}_alpha_tt",
           sp.simplify((sp.diff(aT,t) - aTT).subs(sub)) == 0)

f = sp.Function('f')
prod = sp.expand(sp.diff(symA*f(t)**2, t, 2).doit().subs(
    {sp.Derivative(f(t),(t,2)): att, sp.Derivative(f(t),t): at, f(t): ang}))
P = sp.Poly(prod, ang, at, att)
def coef(i,j,k): return sp.expand(P.coeff_monomial(ang**i * at**j * att**k))
report("check4_cross_coefficient_equals_minus_4_mu", coef(1,1,0) + 4*mu == 0)
report("check4_alpha_t_squared_coefficient_equals_2A",
       sp.expand(coef(0,2,0) - 2*symA) == 0)
report("check4_alpha_alpha_tt_coefficient_equals_2A",
       sp.expand(coef(1,0,1) - 2*symA) == 0)

tanB = symR*symSign*symC/(lam*symA)
left  = -4*mu*ang*aT + 2*symA*aT**2 + 2*symA*ang*aTT
right = 2*symA*lam**2*symR**2/symQ**2*(1 - 2*ang*tanB)
report("check5_compact_second_derivative_polynomial_identity",
       clear_and_reduce(left - right) == 0)
for sv, lab in ((1,"C_positive"), (-1,"C_negative")):
    sub = {symSign: sv, symR: sp.sqrt(1-mu**2)}
    report(f"check5_branch_{lab}", sp.simplify((left-right).subs(sub)) == 0)

samples = [(R(1,2),R(1,2),R(3,5)), (R(-1,2),R(1,2),R(3,5)), (R(4,5),R(-3,4),R(2,5)),
           (R(-9,10),R(9,10),R(1,2)), (R(-3,10),R(1,3),R(7,10)),
           (R(1,10),R(-9,10),R(1,4)), (R(-7,10),R(-1,2),R(33,50)), (R(3,5),R(7,10),R(5,8))]
W, RD, TOL = 60, 50, sp.Rational(1,10**45)
direct = sp.diff(symA*alFn(mu,t,lam)**2, t, 2)
d1 = sp.diff(alFn(mu,t,lam), t); d2 = sp.diff(alFn(mu,t,lam), t, 2)
rows = []
for m0,t0,l0 in samples:
    sub = {mu:m0, t:t0, lam:l0}
    cv = cFn(m0,t0,l0); sv = sp.sign(cv); lab = "C>0" if sv>0 else "C<0"
    rv, qv, av = sp.sqrt(1-m0**2), qFn(m0,t0,l0), aFn(m0,t0,l0)
    alv = alFn(m0,t0,l0)
    r1 = abs(sp.N(d1.subs(sub), W) - sp.N(l0*rv*sv/qv, W))
    r2 = abs(sp.N(d2.subs(sub), W) - sp.N(-2*l0**3*rv*sv*(t0-m0)/qv**2, W))
    r3 = abs(sp.N(direct.subs(sub), W)
             - sp.N(2*av*l0**2*(1-m0**2)/qv**2*(1-2*alv*sp.tan(alv)), W))
    rows.append((m0,t0,l0,lab,r1,r2,r3))
    report(f"check6_sample_mu_{m0}_t_{t0}_lam_{l0}_{lab}",
           r1 < TOL and r2 < TOL and r3 < TOL)
report("check6_both_sign_branches_sampled",
       any(r[3]=="C>0" for r in rows) and any(r[3]=="C<0" for r in rows))
print("direct_second_derivative_residuals=")
for r in rows:
    print(f"  mu={r[0]} t={r[1]} lam={r[2]} branch={r[3]} "
          f"alpha_t_residual={sp.N(r[4],RD)} alpha_tt_residual={sp.N(r[5],RD)} "
          f"second_derivative_residual={sp.N(r[6],RD)}")
print("  max_second_derivative_residual=", sp.N(max(r[6] for r in rows), RD))

order = 8
phi = sp.asin(sp.sqrt(u))**2
poly = sp.expand(sp.series(phi, u, 0, order+1).removeO())
report("check7_phi_series_is_polynomial_in_u", sp.Poly(poly, u).is_univariate)
report("check7_phi_series_vanishes_at_zero", sp.simplify(poly.subs(u,0)) == 0)
coeffs = [poly.coeff(u, n) for n in range(order+1)]
expected = [0] + [R(4**n, 2*n**2*sp.binomial(2*n,n)) for n in range(1,order+1)]
report("check7_phi_coefficients_match_closed_form",
       all(sp.simplify(a-b) == 0 for a,b in zip(coeffs, expected)))
tp = R(1,1000)
tr = abs(sp.N(phi.subs(u,tp), W) - sp.N(poly.subs(u,tp), W))
report("check7_phi_truncation_residual_is_order_u_nine", tr < R(1,10**26))
print("phi_series=", poly)
print("phi_series_coefficients=", coeffs)
print("phi_truncation_residual=", sp.N(tr, RD))

mf = z/(1+z**2)**2; amax = 1/sp.sqrt(3); mmax = 9/(16*sp.sqrt(3))
report("check8_argmax_is_critical_point", sp.simplify(sp.diff(mf,z).subs(z,amax)) == 0)
report("check8_value_at_argmax", sp.simplify(mf.subs(z,amax) - mmax) == 0)
report("check8_global_bound_factorization",
       sp.simplify(sp.expand(9*(1+z**2)**2 - 16*sp.sqrt(3)*z
                   - sp.expand((z-amax)**2*(9*z**2+6*sp.sqrt(3)*z+27)))) == 0)
report("check8_cofactor_is_positive_definite",
       sp.simplify((6*sp.sqrt(3))**2 - 4*9*27) == -864)
report("check8_maxvalue_agrees",
       sp.simplify(sp.maximum(mf, z, sp.Interval(0, sp.oo)) - mmax) == 0)
zz = lam*(t-mu)/symR
report("check8_alpha_tt_majorant_form",
       clear_and_reduce(aTT + 2*lam**2*symSign*zz/(symR**2*(1+zz**2)**2)) == 0)
print("majorant_maximum=", mmax, "=", sp.N(mmax, RD))
print("failure_count=", len(fails))

import sys
sys.exit(0 if not fails else 1)
