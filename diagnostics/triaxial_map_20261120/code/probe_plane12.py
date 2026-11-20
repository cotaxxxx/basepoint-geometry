"""Exploratory probe (outside the fixed plan): in the plane q_3 = 0 (two shorter axes),
sign of  W_beta = E_2/(l_2^beta q_2) - E_1/(l_1^beta q_1)  for beta = 0 (reference) and beta = 2 (physical),
divided by (s-1).  The physical one equals (l_2^2 - l_1^2) dE/dM[e1e2+e2e1]/(p_1 p_2) exactly (rotation covariance).
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np, json, sys
import triax
from census import nq
S = [1.02, 1.05, 1.2, 1.5, 2.0, 2.6, 3.3, 4.0]
T = [1.0, 1.05, 1.3, 1.8, 2.3, 3.0, 4.0, 5.0, 6.5, 8.0]
r = np.append(np.sin(np.pi*np.arange(1, 17)/34.0), [0.999, 1.0])
an = (np.arange(12) + 0.5)*(np.pi/2)/12
R2, PS = np.meshgrid(r, an, indexing="ij")
Q2 = np.stack([R2*np.cos(PS), R2*np.sin(PS), 0*R2], -1).reshape(-1, 3)
rows = []
for s in S:
    for t in T:
        l = np.array([1, s, s*t]); n = nq(l)
        o = triax.ev(l, Q2, n)
        w0 = (o[:, 2]/Q2[:, 1] - o[:, 1]/Q2[:, 0])/(s - 1)
        w2 = (o[:, 2]/(s*s*Q2[:, 1]) - o[:, 1]/Q2[:, 0])/(s - 1)
        rows.append(dict(s=s, t=t, ref_min=float(w0.min()), ref_max=float(w0.max()), phys_min=float(w2.min()), phys_max=float(w2.max())))
        print("s=%.2f t=%.2f  ref/(s-1) in [%.4f, %.4f]   phys/(s-1) in [%.4f, %.4f]" % (s, t, w0.min(), w0.max(), w2.min(), w2.max()), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
