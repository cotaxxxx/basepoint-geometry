"""Cross-check of the figures quoted in the Codex summary (pasted by the user, 2026-11-20) against this
directory's independent implementation.  Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np
from scipy.optimize import brentq, fsolve
import triax
from shear import shear_tensor
out = {}
# (1) t = 3: circle radius and the cos(2 phi) coefficient over the band 13/16 <= r <= 27/32
l = np.array([1.0, 1.0, 3.0]); N = (320, 320)
r0 = brentq(lambda r: triax.ev(l, [r, 0, 0], N)[1], 0.5, 0.95, xtol=1e-14)
band = np.linspace(13/16, 27/32, 9)
B = []
for r in list(band) + [r0]:
    T = shear_tensor(l, np.array([r, 0, 0]), (320, 320))
    B.append(0.5*(T[1, 1] - T[0, 0]))          # B = (1/2)(dE/dl_2 - dE/dl_1) at q = (r,0,0)
out["t3"] = dict(r0=r0, in_band=bool(13/16 < r0 < 27/32), band_r=band.tolist(), B_band=B[:-1], B_at_r0=B[-1],
                 B_min=min(B[:-1]), B_max=max(B[:-1]))
print("t=3: r0 = %.9f (13/16 = 0.8125, 27/32 = 0.84375)" % r0)
print("     B(r) on the band:", np.round(B[:-1], 6), " B(r0) = %.6f" % B[-1])
# (2) the point where h_1 = 0 and E_2(e_2) = 0 simultaneously
def F(x):
    s, t = x; ll = np.array([1.0, s, s*t])
    return [triax.ev_big(ll, np.zeros(3), (320, 320))[4], triax.ev_big(ll, np.array([0, 1.0, 0]), (320, 320))[2]]
sol = fsolve(F, [1.567, 2.297], xtol=1e-13)
out["Z1_cross_D2"] = dict(s=float(sol[0]), t=float(sol[1]), residual=[float(v) for v in F(sol)])
print("Z1 x D2: s = %.6f, t = %.6f, residual %s" % (sol[0], sol[1], F(sol)))
# (3) (s,t) = (1.25, 32): sign of E_2/q_2 - E_1/q_1 and of E_3/q_3 near the boundary
ll = np.array([1.0, 1.25, 40.0]); n = (1536, 1536)
rows = []
for r in (0.5, 0.9, 0.99, 0.999):
    for th, ph in ((np.pi/2, np.pi/4), (np.pi/3, np.pi/4), (np.pi/6, np.pi/4), (np.pi/3, np.pi/8), (np.pi/3, 3*np.pi/8)):
        q = r*np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
        o = triax.ev_big(ll, q, n)
        rows.append(dict(r=r, theta=th, phi=ph, d21=float(o[2]/q[1] - o[1]/q[0]), k3=(float(o[3]/q[2]) if abs(q[2]) > 1e-9 else float(o[6]))))
out["s1p25_t32"] = rows
neg = [x for x in rows if x["d21"] < 0]
print("(1.25, 32): %d of %d sample points have E2/q2 - E1/q1 < 0; min = %.5f; min E3/q3 (or E_33 on the plane) = %.5f" % (
    len(neg), len(rows), min(x["d21"] for x in rows), min(x["k3"] for x in rows)))
for x in rows: print("   r=%.3f th=%.3f ph=%.3f  d21=%+.5f  k3=%.5f" % (x["r"], x["theta"], x["phi"], x["d21"], x["k3"]))
json.dump(out, open(sys.argv[1], "w"), indent=1)
