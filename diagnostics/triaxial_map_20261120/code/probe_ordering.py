"""Exploratory probe (outside the fixed plan; reported as such).
 (A) ordering of kappa_i = E_i/q_i on the closed first octant:  kappa_1 <= kappa_2 <= kappa_3
     (reference normalisation), with equality only when the two semi-axes coincide.
 (A') the same in the physical normalisation E_i/(l_i^2 q_i).
 (B) on each axis, kappa_i(r) = g_i(r)/r is decreasing:  r E_ii - E_i < 0.
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np, json, sys
import triax
from census import nq
S = [1.0, 1.05, 1.2, 1.5, 2.0, 2.6, 3.3, 4.0]
T = [1.0, 1.05, 1.3, 1.8, 2.3, 3.0, 4.0, 5.0, 6.5, 8.0]
r = np.append(np.sin(np.pi*np.arange(1, 11)/22.0), [0.999, 1.0])
an = (np.arange(8) + 0.5)*(np.pi/2)/8
R, TH, PH = np.meshgrid(r, an, an, indexing="ij")
Q3 = np.stack([R*np.sin(TH)*np.cos(PH), R*np.sin(TH)*np.sin(PH), R*np.cos(TH)], -1).reshape(-1, 3)
ra = np.sin(np.pi*np.arange(1, 40)/80.0)
rows = []
for s in S:
    for t in T:
        l = np.array([1, s, s*t]); n = nq(l)
        o = triax.ev(l, Q3, n); k = o[:, 1:4]/Q3
        kp = k/l**2
        d = dict(s=s, t=t, d21=float((k[:, 1] - k[:, 0]).min()), d32=float((k[:, 2] - k[:, 1]).min()),
                 d31=float((k[:, 2] - k[:, 0]).min()),
                 p21=float((kp[:, 1] - kp[:, 0]).min()), p32=float((kp[:, 2] - kp[:, 1]).min()),
                 p31=float((kp[:, 2] - kp[:, 0]).min()))
        for i in range(3):
            oa = triax.ev(l, ra[:, None]*np.eye(3)[i], n)
            d["B%d" % (i + 1)] = float(((ra*oa[:, 4 + i] - oa[:, 1 + i])/ra**3).max())
        rows.append(d)
        print("s=%.2f t=%.2f | ref: k2-k1>=%.4f k3-k2>=%.4f k3-k1>=%.4f | phys: %.4f %.4f %.4f | max (rE_ii-E_i)/r^3: %.4f %.4f %.4f" % (
            s, t, d["d21"], d["d32"], d["d31"], d["p21"], d["p32"], d["p31"], d["B1"], d["B2"], d["B3"]), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
