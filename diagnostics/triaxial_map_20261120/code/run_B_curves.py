"""Run B / Run E: bifurcation curves traced independently of the grid (PLAN.md).
   Z_i : h_i(s,t) = 0  (centre eigenvalue),   D_i : E_i(e_i; s,t) = 0  (pole trace).
Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np
from scipy.optimize import brentq
import triax


def nfor(l, mult=1.0):
    a = max(l)/min(l)
    n = 192 if a <= 6 else 320 if a <= 14 else 512 if a <= 32 else 1024 if a <= 80 else 2048 if a <= 180 else 4096
    n = int(n*mult)
    return (n, n)


def val(kind, i, s, t, mult=1.0):
    l = np.array([1.0, s, s*t])
    if kind == "Z":
        return triax.ev_big(l, np.zeros(3), nfor(l, mult))[4 + i]
    return triax.ev_big(l, np.eye(3)[i], nfor(l, mult))[1 + i]


def solve_t(kind, i, s, lo, hi):
    f = lambda t: val(kind, i, s, t)
    if f(lo)*f(hi) > 0:
        return None
    t = brentq(f, lo, hi, xtol=1e-12, rtol=1e-13)
    # quadrature check: residual at 1.5x nodes, converted to a root shift through the local slope
    r15 = val(kind, i, s, t, 1.5)
    slope = (val(kind, i, s, t*1.0005) - val(kind, i, s, t/1.0005))/(t*1.0005 - t/1.0005)
    return dict(s=s, t=t, quad_shift=abs(r15/slope), slope_t=slope)


def solve_s(kind, i, t, lo, hi):
    f = lambda s: val(kind, i, s, t)
    if f(lo)*f(hi) > 0:
        return None
    s = brentq(f, lo, hi, xtol=1e-12, rtol=1e-13)
    r15 = val(kind, i, s, t, 1.5)
    slope = (val(kind, i, s*1.0005, t) - val(kind, i, s/1.0005, t))/(s*1.0005 - s/1.0005)
    return dict(s=s, t=t, quad_shift=abs(r15/slope), slope_s=slope)


out = {}
far = [1.0, 1.01, 1.02, 1.05, 1.1, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 16.0, 24.0, 32.0]
# Z1: h_1 = 0, from (1, lambda_c^pro) to (1/lambda_c^ob, 1)
out["Z1_t_of_s"] = [solve_t("Z", 0, s, 1.0, 5.5) for s in np.concatenate([[1.0, 1.01, 1.02, 1.05], np.linspace(1.1, 2.4, 14), [2.43, 2.45]])]
out["Z1_s_of_t"] = [solve_s("Z", 0, t, 1.0, 3.0) for t in [1.0, 1.01, 1.02, 1.05, 1.1, 1.2, 1.4, 1.7, 2.0]]
print("Z1 done", flush=True)
# D1: pole trace on e_1, from (1, lambda_b^pro) to (1/lambda_d^ob, 1)
out["D1_t_of_s"] = [solve_t("D", 0, s, 1.0, 2.6) for s in np.concatenate([[1.0, 1.01, 1.02, 1.05], np.linspace(1.1, 1.5, 9), [1.53, 1.55]])]
out["D1_s_of_t"] = [solve_s("D", 0, t, 1.0, 2.0) for t in [1.0, 1.01, 1.02, 1.05, 1.1, 1.2, 1.4]]
print("D1 done", flush=True)
# Z2 and D2 (run to large s: Run E)
out["Z2_t_of_s"] = [solve_t("Z", 1, s, 2.5, 8.0) for s in far]
print("Z2 done", flush=True)
out["D2_t_of_s"] = [solve_t("D", 1, s, 1.2, 3.0) for s in far]
print("D2 done", flush=True)
# signs of h_3 and of the e_3 pole trace on a coarse far grid (no zero curve expected)
rows = []
for s in (1, 1.5, 2.5, 4, 8, 16, 32):
    for t in (1, 1.5, 2.5, 4, 8, 16, 32):
        l = np.array([1.0, s, s*t])
        c = triax.ev_big(l, np.zeros(3), nfor(l)); p3 = triax.ev_big(l, np.eye(3)[2], nfor(l))[3]
        c15 = triax.ev_big(l, np.zeros(3), nfor(l, 1.5))
        rows.append(dict(s=s, t=t, h=c[4:7].tolist(), pole3=float(p3), quad_diff=float(np.abs(c - c15)[4:7].max())))
out["far_grid"] = rows
json.dump(out, open(sys.argv[1], "w"), indent=1)
print("done")
