"""Run C: splitting near the edges (PLAN.md).  Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE.
 prolate edge s = 1:  stationary circle |q'| = r0(t) in the plane q_3 = 0.
   first-order splitting (reduced function on the circle):  Phi_s(phi) = Phi_1 + (s-1)[const + B cos 2phi] + O((s-1)^2)
   B(t) = (1/2)(a_2 - a_1),  a_i = dE/dl_i at q = (r0,0,0), l = (1,1,t).
   predictions:  E_22 at the e_1-point = -4 B (s-1)/r0^2,  E_11 at the e_2-point = +4 B (s-1)/r0^2,
                 E(e_1-point) - E(e_2-point) = 2 B (s-1)."""
import json, sys
import numpy as np
from scipy.optimize import brentq
import triax

N = (320, 320)


def axis_root(l, i, lo=1e-3, hi=1 - 1e-9):
    f = lambda r: triax.ev(l, r*np.eye(3)[i], N)[1 + i]
    rr = np.linspace(lo, hi, 400)
    v = triax.ev(l, rr[:, None]*np.eye(3)[i], N)[:, 1 + i]
    roots = [brentq(f, rr[j], rr[j + 1], xtol=1e-14) for j in range(len(rr) - 1) if v[j]*v[j + 1] < 0]
    return roots


out = {"prolate": [], "oblate": []}
for t in (2.1, 2.2, 2.5, 3.0, 3.5, 4.0, 4.5, 4.7):
    l0 = np.array([1.0, 1.0, t])
    r0 = axis_root(l0, 0)
    if len(r0) != 1:
        out["prolate"].append(dict(t=t, note="roots on the edge: %r" % (r0,))); continue
    r0 = r0[0]; q0 = np.array([r0, 0, 0])
    o0 = triax.ev(l0, q0, N)
    h = 1e-4
    a = [(triax.ev(l0 + h*np.eye(3)[i], q0, N)[0] - triax.ev(l0 - h*np.eye(3)[i], q0, N)[0])/(2*h) for i in range(3)]
    B = 0.5*(a[1] - a[0])
    row = dict(t=t, r0=r0, E_rr=o0[4], E_tt=o0[5], E_33=o0[6], a=a, B=B, split=[])
    for d in (1e-3, 3e-3, 1e-2, 3e-2):
        l = np.array([1.0, 1 + d, (1 + d)*t])
        r1 = axis_root(l, 0); r2 = axis_root(l, 1)
        e = dict(delta=d, r1=r1, r2=r2)
        if len(r1) == 1 and len(r2) == 1:
            o1 = triax.ev(l, [r1[0], 0, 0], N); o2 = triax.ev(l, [0, r2[0], 0], N)
            e.update(E22_at_e1=o1[5], pred_E22=-4*B*d/r0**2, E11_at_e2=o2[4], pred_E11=4*B*d/r0**2,
                     dE=o1[0] - o2[0], pred_dE=2*B*d,
                     hdiag_e1=o1[4:7].tolist(), hdiag_e2=o2[4:7].tolist(),
                     index_e1=int((o1[4:7] < 0).sum()), index_e2=int((o2[4:7] < 0).sum()))
        row["split"].append(e)
    out["prolate"].append(row)
    print("t=%.2f r0=%.6f B=%.6f | " % (t, r0, B) + " ; ".join(
        "d=%g E22@e1 %.3e (pred %.3e) E11@e2 %.3e (pred %.3e) idx %s/%s" % (
            e["delta"], e.get("E22_at_e1", np.nan), e.get("pred_E22", np.nan), e.get("E11_at_e2", np.nan),
            e.get("pred_E11", np.nan), e.get("index_e1"), e.get("index_e2")) for e in row["split"]), flush=True)
# oblate edge t = 1: axis pair on e_1 for 1/lambda_d < s < 1/lambda_c ; transverse eigenvalues split for t > 1
for s in (1.6, 1.8, 2.0, 2.2, 2.4):
    row = dict(s=s, split=[])
    for d in (0.0, 1e-3, 1e-2, 3e-2):
        l = np.array([1.0, s, s*(1 + d)])
        r1 = axis_root(l, 0)
        e = dict(delta=d, r1=r1)
        if len(r1) == 1:
            o1 = triax.ev(l, [r1[0], 0, 0], N)
            e.update(hdiag=o1[4:7].tolist(), index=int((o1[4:7] < 0).sum()))
        e["r2"] = axis_root(l, 1); e["r3"] = axis_root(l, 2)
        row["split"].append(e)
    out["oblate"].append(row)
    print("s=%.2f | " % s + " ; ".join("d=%g r1=%s hdiag=%s" % (e["delta"], np.round(e["r1"], 6), np.round(e.get("hdiag", []), 5)) for e in row["split"]), flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
