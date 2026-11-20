"""Formula checks (non-interval).  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np, json, sys
import triax
from ref_physical import E_physical
rng = np.random.default_rng(20261120)
res = {"checks": []}
worst = dict(phys=0, grad=0, hess=0, conv=0, bnd=0)
for trial in range(12):
    s = 1 + 2.5*rng.random(); t = 1 + 3.0*rng.random()
    l = np.array([1, s, s*t]); a = l/np.prod(l)**(1/3)      # volume-normalised physical semi-axes
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    q = v*rng.random()**(1/3)*0.97
    o = triax.ev(l, q, (160, 160)); o2 = triax.ev(l, q, (96, 96))
    Ep, mass = E_physical(a, a*q, 500)
    h = 1e-4
    g_fd = np.array([(triax.ev(l, q + h*e, (160, 160))[0] - triax.ev(l, q - h*e, (160, 160))[0])/(2*h) for e in np.eye(3)])
    H_fd = np.array([(triax.ev(l, q + h*e, (160, 160))[1:4] - triax.ev(l, q - h*e, (160, 160))[1:4])/(2*h) for e in np.eye(3)])
    H = triax.hess_matrix(o)
    d = dict(s=s, t=t, q=q.tolist(), E=o[0], E_phys=Ep, mass_minus_1=mass - 1,
             dE_phys=o[0] - Ep, dgrad_fd=float(np.abs(g_fd - o[1:4]).max()),
             dhess_fd=float(np.abs(H_fd - H).max()), dconv_96_160=float(np.abs(o - o2).max()))
    worst["phys"] = max(worst["phys"], abs(d["dE_phys"])); worst["grad"] = max(worst["grad"], d["dgrad_fd"])
    worst["hess"] = max(worst["hess"], d["dhess_fd"]); worst["conv"] = max(worst["conv"], d["dconv_96_160"])
    res["checks"].append(d)
# boundary trace: gradient at |q|=1 vs interior limit
for trial in range(6):
    s = 1 + 2.5*rng.random(); t = 1 + 3.0*rng.random(); l = np.array([1, s, s*t])
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    gb = triax.ev(l, v, (200, 200))[:4]
    seq = [triax.ev(l, v*(1 - 10.0**-m), (200, 200))[:4] for m in (3, 4, 5, 6)]
    errs = [float(np.abs(x - gb).max()) for x in seq]
    worst["bnd"] = max(worst["bnd"], errs[-1])
    res["checks"].append(dict(kind="boundary_trace", s=s, t=t, v=v.tolist(), trace=gb.tolist(), err_1e3_to_1e6=errs))
res["worst"] = worst
json.dump(res, open(sys.argv[1], "w"), indent=1)
print(worst)
for c in res["checks"][-6:]: print(c["err_1e3_to_1e6"])
