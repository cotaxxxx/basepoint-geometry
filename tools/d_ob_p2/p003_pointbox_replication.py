import sys, math, time
from fractions import Fraction as Q
import pinned_producer as P  # copy of producer, SHA-256 dff79bc4...; verify before use
import independent_H_sign as hsign
from flint import arb
r = Q(sys.argv[1]); t = Q(1,64); lam = Q(sys.argv[2]) if len(sys.argv) > 2 else (Q(119,200)+Q(33,50))/2
B = P.PBox(r, r, t, t, lam, lam, 12)
rho = float(r*(1-t*t)/(1+t*t)); z = float(lam*r*2*t/(1+t*t)); lf = float(lam)
t0 = time.time(); cells, d = P.refine_cells(B)
up = arb(0)
for c, k, _ in d["regular"]: up += (c.area()*k).upper()
J = hsign.routeB(rho, z, lf)*2*math.pi*lf
print(f"r={sys.argv[1]} cut={len(d['cut'])} stop={'accepted' if cells is not None else 'max_or_empty'} "
      f"L={float(d['L'].lower()):+.6f} J={J:+.6f} SumUp={float(up):+.6f} {time.time()-t0:.0f}s", flush=True)
