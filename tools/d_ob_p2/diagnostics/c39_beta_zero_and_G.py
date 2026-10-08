"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.
"""
import numpy as np, sys, math
sys.path.insert(0,"..")
exec(open("scan.py").read().split("Ls=np.linspace")[0])
from scipy.optimize import brentq
# beta zero mu*(L,m) and monotonicity check
zs=[]; nonmono=0
for L in np.linspace(4/25,8649/40000,9):
  for m in np.linspace(112/113,1,9):
    f=lambda x: beta_terms(L,m,x)[0]
    z=brentq(f,-0.25,0.4,xtol=1e-10); zs.append((z,L,m))
    xs=np.linspace(-0.25,z,200); vs=[f(x) for x in xs]
    nonmono+=int(np.any(np.diff(vs)>0))
zs.sort(); print("min zero mu*: %.6f at L=%.5f m=%.5f   max zero: %.6f"%(zs[0][0],zs[0][1],zs[0][2],zs[-1][0]))
print("grid cells where beta not decreasing on (-1/4,mu*):",nonmono)
# true G(mu) on J using exact pair integrand
sys.path.insert(0,"/tmp/claude-0/-home-user-basepoint-geometry/4a60cb89-631e-55a2-bf10-b766d91409bc/scratchpad")
from regions import integrand, muC
from scipy.integrate import quad
for L,m in ((8649/40000,112/113),(4/25,1-1e-9),(4/25,112/113)):
    mc=muC(L,m); print(f"L={L:.4f} m={m:.4f} mu_C={mc:.4f}")
    for x in np.linspace(-0.25,mc-1e-3,8):
        G=quad(lambda ph: integrand(x,ph,L,m),0,math.pi,limit=200)[0]
        print(f"   mu={x:+.3f} G_true={G:+.5f}  lam2s/w*beta={L*(m-x)/math.sqrt(x*x+L*(1-x*x))*beta_terms(L,m,x)[0]:+.5f}")
