"""audit_margins.py -- floating-point values of the quantities for which the Codex report states
rigorous lower bounds on the rectangle R = [1, 16/5] x [1, 6]; shows how much slack the bounds have.
Non-interval, grid minima only (not bounds).   DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import numpy as np
import triax
from shear import shear_tensor
out = {}
I, J = np.meshgrid(np.arange(97), np.arange(129), indexing="ij")
S = 2.1 + 1.1*np.cos(np.pi*I/96); T = 3.5 + 2.5*np.cos(np.pi*J/128)
L = np.stack([np.ones_like(S), S, S*T], -1).reshape(-1, 3)
a = L.max(1)
o = np.empty((len(L), 10)); p3 = np.empty(len(L))
for lo, hi, n in ((0, 6, 256), (6, 12, 384), (12, 99, 576)):
    m = (a > lo) & (a <= hi)
    o[m] = triax.ev(L[m], np.zeros(3), (n, n)); p3[m] = triax.ev(L[m], np.array([0, 0, 1.0]), (n, n))[:, 3]
s = L[:, 1]
k = int(np.argmin(o[:, 6])); out["min_h3"] = dict(value=float(o[k, 6]), s=float(s[k]), t=float(L[k, 2]/s[k]), codex_bound=0.6714)
m = s > 1 + 1e-9
r = (o[m, 5] - o[m, 4])/(s[m] - 1/s[m]); k = int(np.argmin(r))
out["min_(h2-h1)/(s-1/s)"] = dict(value=float(r[k]), s=float(s[m][k]), t=float(L[m][k, 2]/s[m][k]), codex_bound=1/32)
k = int(np.argmin(p3)); out["min_b3"] = dict(value=float(p3[k]), s=float(s[k]), t=float(L[k, 2]/s[k]), codex_bound=2.22e-5)
# long axis outer part 11/16 <= r <= 1 : E_3(r e_3)/r on a coarser shape grid
ss = np.linspace(1, 3.2, 12); tt = np.linspace(1, 6, 21); rr = np.linspace(11/16, 1.0, 11)
best = (9, 0, 0, 0)
for sv in ss:
    for tv in tt:
        v = triax.ev([1, sv, sv*tv], rr[:, None]*np.array([0, 0, 1.0]), (384, 384))[:, 3]/rr
        j = int(np.argmin(v))
        if v[j] < best[0]:
            best = (float(v[j]), float(sv), float(tv), float(rr[j]))
out["min_E3(r e3)/r_on_11/16<=r<=1"] = dict(value=best[0], s=best[1], t=best[2], r=best[3], codex_bound=0.0002149)
# tau = T11 - T22 at r e_1, s = 1, on [3/8, 1] x [2, 5]; and C12 = tau/r^2 on the whole disc
best = (9, 0, 0); bestc = (9, 0, 0)
for tv in np.linspace(2, 5, 25):
    for rv in np.concatenate([np.linspace(0.05, 0.375, 6), np.linspace(0.375, 1.0, 21)]):
        Tm = shear_tensor([1.0, 1.0, tv], np.array([rv, 0, 0]), (192, 192)); tau = Tm[0, 0] - Tm[1, 1]
        if rv >= 0.375 and tau < best[0]:
            best = (float(tau), float(tv), float(rv))
        if tau/rv**2 < bestc[0]:
            bestc = (float(tau/rv**2), float(tv), float(rv))
out["min_tau_on_r>=3/8"] = dict(value=best[0], t=best[1], r=best[2], codex_bound=0.00018254)
out["min_C12_on_disc_s=1"] = dict(value=bestc[0], t=bestc[1], r=bestc[2], codex_bound=0.00018)
json.dump(out, open(sys.argv[1], "w"), indent=1)
for kk, vv in out.items(): print(kk, vv)
