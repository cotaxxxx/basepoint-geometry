#!/usr/bin/env python3
"""Symbolic + numeric audit for the F_rr extension kernel.

(S1) gamma_r, gamma_rr, gamma_rrr closed forms equal successive r-derivatives
(S2) dFint and d2Fint integrands equal successive r-derivatives of Fint
     (h abstract, so the identities are independent of h's realization)
(N1) h3 hypergeometric closed form equals the direct 3rd derivative of
     acos(c)^2 at 50 dps on endpoint-near and random points; h3(1) = -8/15
Report: item3_frr_symbolic_audit.json (no trailing newline). Exit 0/1.
"""
import json, random, sys
from pathlib import Path

def main() -> int:
    import sympy as sp
    r, lam, u = sp.symbols("r lam u", real=True)
    s_, ell, w, x = sp.symbols("s ell w x", real=True, positive=True)
    hf = sp.Function("h")
    q = ell - 2*r*u + r**2
    W = 1 - r*u
    gamma = lam*W/(w*sp.sqrt(q))
    N = u*(1-ell) + r*(u**2-1); N_r = u**2-1
    g1 = (lam/w)*N/q**sp.Rational(3,2)
    M = N_r*q - 3*N*(r-u); M_r = -N_r*(r-u) - 3*N
    g2 = (lam/w)*M/q**sp.Rational(5,2)
    g3 = (lam/w)*(M_r*q - 5*M*(r-u))/q**sp.Rational(7,2)
    res = {}
    res["g1"] = str(sp.simplify(sp.diff(gamma, r) - g1))
    res["g2"] = str(sp.simplify(sp.diff(g1, r) - g2))
    res["g3"] = str(sp.simplify(sp.diff(g2, r) - g3))
    h0 = hf(gamma)
    h1 = sp.diff(hf(x), x).subs(x, gamma)
    h2 = sp.diff(hf(x), x, 2).subs(x, gamma)
    h3 = sp.diff(hf(x), x, 3).subs(x, gamma)
    Fint   = s_*(-u*h0 + W*h1*g1)
    dFint  = s_*(-2*u*h1*g1 + W*(h2*g1**2 + h1*g2))
    d2Fint = s_*(-3*u*(h2*g1**2 + h1*g2) + W*(h3*g1**3 + 3*h2*g1*g2 + h1*g3))
    res["dFint"]  = str(sp.simplify(sp.diff(Fint, r) - dFint))
    res["d2Fint"] = str(sp.simplify(sp.diff(dFint, r) - d2Fint))
    sym_ok = all(v == "0" for v in res.values())

    from mpmath import mp, acos, diff, hyper, mpf
    mp.dps = 50
    random.seed(20260726)
    def h3_closed(c):
        h = acos(c)**2; xx = -h/4
        S  = hyper([], [mpf(3)/2], xx)
        P2 = hyper([], [mpf(5)/2], xx)
        P3 = hyper([], [mpf(7)/2], xx)
        return mpf(2)/15*(S*P3 - 5*P2**2)/S**5
    pts = [mpf(1)-mpf(10)**(-k) for k in (2,4,6)] + \
          [mpf(random.uniform(-0.95, 0.99)) for _ in range(17)]
    worst = mpf(0)
    for c in pts:
        worst = max(worst, abs(h3_closed(c) - diff(lambda t: acos(t)**2, c, 3)))
    end_ok = abs(h3_closed(mpf(1)) - mpf(-8)/15) < mpf(10)**(-45)
    num_ok = bool(worst < mpf(10)**(-30)) and end_ok
    verdict = "PASS" if (sym_ok and num_ok) else "FAIL"
    Path("item3_frr_symbolic_audit.json").write_bytes(json.dumps(
        {"label":"item3_Frr_audit","symbolic_residuals":res,
         "h3_numeric_max_err":str(worst),"h3_endpoint_exact":end_ok,
         "n_numeric_points":20,"seed":20260726,"dps":50,
         "verdict":verdict}, separators=(",",":")).encode())
    print(verdict)
    return 0 if verdict == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
