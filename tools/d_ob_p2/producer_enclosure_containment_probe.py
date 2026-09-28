"""Soundness probe of the pinned producer near-column enclosure at point boxes. DIAGNOSTIC / NOT_EVIDENCE."""
import math, sys, time
from fractions import Fraction as Q
import pinned_producer as P  # copy of producer/d_ob_p2_producer.py, SHA-256 dff79bc4...; verify before use
import independent_H_sign as hsign
from flint import arb

def run(ir, it, il):
    r = Q(7,8)+Q(2*ir+1,256); t = Q(7,8)+Q(2*it+1,256); lam = Q(2,5)+Q(13,3200)*Q(2*il+1,2)
    B = P.PBox(r, r, t, t, lam, lam, 12)
    rho = float(r*(1-t*t)/(1+t*t)); z = float(lam*r*2*t/(1+t*t)); lf = float(lam)
    t0 = time.time()
    cells, data = P.refine_cells(B)
    stop = "accepted" if cells is not None else "not_accepted"
    reg, cut = data["regular"], data["cut"]
    sum_up = arb(0); sum_lo = arb(0); viol = 0; worst = 0.0
    for cell, k, _ in reg:
        a = cell.area() * k
        sum_up += a.upper(); sum_lo += a.lower()
        mu = float((cell.m0+cell.m1)/2); ph = math.pi*float((cell.p0+cell.p1)/2)
        v = (hsign.Frho(mu, ph, rho, z, lf) - hsign.Frho(mu, ph, -rho, z, lf))/(2*rho)
        lo, hi = float(k.lower()), float(k.upper())
        tol = 1e-9*max(1.0, abs(v))
        if not (lo - tol <= v <= hi + tol):
            viol += 1; worst = max(worst, min(abs(v-lo), abs(v-hi)))
    J_true = hsign.routeB(rho, z, lf) * 2*math.pi*lf
    print(f"({ir},{it},{il}) stop={stop} regular={len(reg)} cut={len(cut)} "
          f"L={float(data['L'].lower()):+.4e} Bcut={float(data['Bcut'].upper()):.4e} "
          f"SumUp={float(sum_up):+.4e} J_true={J_true:+.6e} containment_violations={viol} worst={worst:.3e} "
          f"{time.time()-t0:.0f}s", flush=True)

if __name__ == "__main__":
    ir, it, il = map(int, sys.argv[1:4]); run(ir, it, il)
