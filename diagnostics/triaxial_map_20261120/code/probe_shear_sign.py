"""Exploratory probe (outside the fixed plan): signs of the shear cofactors
     T_12/(q_1 q_2) on the plane q_3 = 0     (candidate lemma H12, no degeneration at s = 1)
     T_13/(q_1 q_3), T_23/(q_2 q_3) in the ball (alternative to H3)
on a coarse shape grid INCLUDING the edges s = 1 and t = 1.   DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np, json, sys
from shear import shear_tensor
S = [1.0, 1.2, 1.6, 2.4, 4.0]
T = [1.0, 1.3, 2.0, 3.0, 4.7, 8.0]
r = [0.15, 0.4, 0.65, 0.85, 0.97, 1.0]
an = (np.arange(4) + 0.5)*(np.pi/2)/4
rows = []
for s in S:
    for t in T:
        l = np.array([1, s, s*t]); a = s*t
        n = 128 if a <= 4 else 192 if a <= 10 else 288 if a <= 20 else 400
        c12 = []; c13 = []; c23 = []
        for rr in r:
            for ps in an:
                q = rr*np.array([np.cos(ps), np.sin(ps), 0.0])
                c12.append(shear_tensor(l, q, (n, n))[0, 1]/(q[0]*q[1]))
            for th in an[::2]:
                for ph in an[::2]:
                    q = rr*np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
                    Tm = shear_tensor(l, q, (n, n))
                    c13.append(Tm[0, 2]/(q[0]*q[2])); c23.append(Tm[1, 2]/(q[1]*q[2]))
        d = dict(s=s, t=t, c12_min=float(min(c12)), c12_max=float(max(c12)), c13_min=float(min(c13)), c13_max=float(max(c13)),
                 c23_min=float(min(c23)), c23_max=float(max(c23)))
        rows.append(d)
        print("s=%.1f t=%.1f  T12/(q1q2) on plane in [%.4f, %.4f]   T13/(q1q3) in [%.4f, %.4f]   T23/(q2q3) in [%.4f, %.4f]" % (
            s, t, d["c12_min"], d["c12_max"], d["c13_min"], d["c13_max"], d["c23_min"], d["c23_max"]), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
