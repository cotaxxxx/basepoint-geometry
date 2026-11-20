"""Run E addendum: where does the order h_1 < h_2 of the centre eigenvalues reverse (far from the window)?
h_2 - h_1 = (s - 1/s) C_12(0), so this is the zero set of the shear cofactor C_12 at the centre:
beyond it hypothesis (H12) of Proposition 4 fails.  Not a bifurcation curve.
Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np
from scipy.optimize import brentq
import triax


def d(s, t, mult=1.0):
    l = np.array([1.0, s, s*t]); a = s*t
    n = int(mult*(768 if a <= 60 else 1536 if a <= 130 else 3072 if a <= 260 else 6144))
    o = triax.ev_big(l, np.zeros(3), (n, n))
    return o[5] - o[4]


rows = []
for s, lo, hi in ((6.0, 16.0, 48.0), (8.0, 16.0, 32.0), (12.0, 12.0, 32.0), (16.0, 12.0, 32.0), (24.0, 8.0, 20.0), (32.0, 8.0, 16.0)):
    flo, fhi = d(s, lo), d(s, hi)
    if flo*fhi > 0:
        rows.append(dict(s=s, bracket=[lo, hi], note="no sign change", f_lo=flo, f_hi=fhi)); print(rows[-1], flush=True); continue
    t = brentq(lambda t: d(s, t), lo, hi, xtol=1e-6)
    chk = d(s, t, 1.5)
    slope = (d(s, t*1.01) - d(s, t/1.01))/(t*1.01 - t/1.01)
    rows.append(dict(s=s, t=t, residual_at_1p5_nodes=chk, quad_shift=abs(chk/slope)))
    print(rows[-1], flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
