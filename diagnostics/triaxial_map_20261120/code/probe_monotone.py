"""Exploratory probe (not part of the fixed plan; reported as such): candidate monotonicity lemmas.
 (M3) E_3(q)/q_3 > 0 on the open ball minus {q_3=0}        (longest axis)
 (MA) sign of (q_1 E_2 - q_2 E_1)/(q_1 q_2) on the plane q_3 = 0   (angular derivative / (q1 q2))
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np, json, sys
import triax
from census import nq
S = [1.0, 1.05, 1.2, 1.5, 2.0, 2.6, 3.3, 4.0]
T = [1.0, 1.05, 1.3, 1.8, 2.3, 3.0, 4.0, 5.0, 6.5, 8.0]
r = np.sin(np.pi*np.arange(1, 17)/34.0); r = np.append(r, [0.999, 0.9999])
an = (np.arange(12) + 0.5)*(np.pi/2)/12
R, TH, PH = np.meshgrid(r, an, an, indexing="ij")
Q3 = np.stack([R*np.sin(TH)*np.cos(PH), R*np.sin(TH)*np.sin(PH), R*np.cos(TH)], -1).reshape(-1, 3)
R2, PS = np.meshgrid(r, an, indexing="ij")
Q2 = np.stack([R2*np.cos(PS), R2*np.sin(PS), 0*R2], -1).reshape(-1, 3)
rows = []
for s in S:
    for t in T:
        l = [1, s, s*t]; n = nq(l)
        o = triax.ev(l, Q3, n); m3 = o[:, 3]/Q3[:, 2]
        m2 = o[:, 2]/Q3[:, 1]; m1 = o[:, 1]/Q3[:, 0]
        o2 = triax.ev(l, Q2, n); A = (Q2[:, 0]*o2[:, 2] - Q2[:, 1]*o2[:, 1])/(Q2[:, 0]*Q2[:, 1])
        rows.append(dict(s=s, t=t, E3_over_q3_min=float(m3.min()), E3_over_q3_max=float(m3.max()),
                         E2_over_q2_min=float(m2.min()), E2_over_q2_max=float(m2.max()),
                         E1_over_q1_min=float(m1.min()), E1_over_q1_max=float(m1.max()),
                         ang_min=float(A.min()), ang_max=float(A.max())))
        print("s=%.2f t=%.2f  E3/q3 in [%.4f, %.4f]  E2/q2 in [%.4f, %.4f]  E1/q1 in [%.4f, %.4f]  ang in [%.4f, %.4f]" % (
            s, t, m3.min(), m3.max(), m2.min(), m2.max(), m1.min(), m1.max(), A.min(), A.max()), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
