"""Run D: neighbourhood of the sphere (PLAN.md).  Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np, mpmath as mp
import triax
from census import census

out = {}
# sphere: radial profile vs the closed form of Kakuron I 1-1 (eq. Eprime-closed)
def Ep_closed(a):
    a = mp.mpf(a)
    chi2 = (mp.polylog(2, a) - mp.polylog(2, -a))/2
    return (1 - 3*a*a/4)*chi2 + (1 - a*a)*(7*a*a - 5)/(16*a*a)*mp.atanh(a) + 5*(1 - a*a)/(16*a)
rr = [0.05, 0.2, 0.4, 0.6, 0.8, 0.95, 0.999]
num = triax.ev([1, 1, 1], np.array(rr)[:, None]*np.array([1.0, 0, 0]), (200, 200))[:, 1]
out["sphere_profile"] = [dict(r=r, numeric=float(v), closed=float(Ep_closed(r)), diff=float(v - Ep_closed(r))) for r, v in zip(rr, num)]
out["sphere_boundary_trace"] = dict(numeric=float(triax.ev([1, 1, 1], [1.0, 0, 0], (200, 200))[1]), closed=float(mp.pi**2/32))
print(out["sphere_profile"], out["sphere_boundary_trace"])
# 9x9 grid near the sphere: census + radial monotonicity q.grad E > 0
vals = [1.0 + 0.03125*i for i in range(9)]
r = np.append(np.sin(np.pi*np.arange(1, 13)/26.0), [0.999, 1.0])
an = (np.arange(9) + 0.5)*(np.pi/2)/9
an = np.concatenate([[0.0], an, [np.pi/2]])
R, TH, PH = np.meshgrid(r, an, an, indexing="ij")
Q = np.stack([R*np.sin(TH)*np.cos(PH), R*np.sin(TH)*np.sin(PH), R*np.cos(TH)], -1).reshape(-1, 3)
rows = []
for s in vals:
    for t in vals:
        c = census(s, t)
        o = triax.ev(triax.shape(s, t), Q, (128, 128))
        rad = np.einsum("ab,ab->a", o[:, 1:4], Q)/np.einsum("ab,ab->a", Q, Q)
        rows.append(dict(s=s, t=t, n_noncentral=len(c["points"]), h=c["h"], pole_trace=c["pole_trace"],
                         morse_sum=c["morse_sum"], min_radial=float(rad.min())))
        print("s=%.4f t=%.4f noncentral=%d min q.gradE/|q|^2=%.4f h=%s" % (s, t, len(c["points"]), rad.min(), np.round(c["h"], 4)), flush=True)
out["grid"] = rows
json.dump(out, open(sys.argv[1], "w"), indent=1)
