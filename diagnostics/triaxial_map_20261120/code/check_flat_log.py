"""Sanity check of the leading-log flat-limit claim  E(0) = pi^2/4 - (ln s/s) Lambda(0) + O(1/s),
Lambda(0; t) = (1/2) Int dpsi / sqrt(cos^2 psi + t^2 sin^2 psi)   (= pi at t = 1),
and  s h_2 / ln s -> -Lambda_xx(0; t)  (= pi/2 at t = 1).   Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np
import triax
from flat_limit import Lam, Lam_xx0
rows = []
for t in (1.0, 2.0):
    for s in (8, 16, 32, 64, 128):
        l = np.array([1.0, s, s*t]); a = s*t
        n = 512 if a <= 20 else 1024 if a <= 70 else 2048 if a <= 140 else 4096
        o = triax.ev_big(l, np.zeros(3), (n, n)); o2 = triax.ev_big(l, np.zeros(3), (int(1.5*n), int(1.5*n)))
        rows.append(dict(t=t, s=s, E0=o[0], h2=o[5], quad_diff=float(abs(o - o2)[[0, 5]].max()),
                         ratio_E=float((np.pi**2/4 - o[0])*s/np.log(s)), Lam0=float(Lam(0, 0, t)),
                         ratio_h2=float(o[5]*s/np.log(s)), minus_Lam_xx0=float(-Lam_xx0(t))))
        r = rows[-1]
        print("t=%g s=%4d  (pi^2/4-E0) s/ln s = %.4f (Lambda(0) = %.4f)   h2 s/ln s = %.4f (-Lambda_xx = %.4f)   quad %.0e" % (
            t, s, r["ratio_E"], r["Lam0"], r["ratio_h2"], r["minus_Lam_xx0"], r["quad_diff"]), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
