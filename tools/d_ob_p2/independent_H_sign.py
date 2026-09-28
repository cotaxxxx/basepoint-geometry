"""DIAGNOSTIC / NOT_EVIDENCE (floating-point, non-interval). Independent sign check of H(rho,z;lambda) from P1 definitions only (no producer code).
Route B: J = int int K_H dphi dmu, K_H = [F_rho(rho)-F_rho(-rho)]/(2 rho), F_rho per P1 Lemma 3.3/3.4.
Route A: derivative-free, E via F = h alpha^2, H = E_rho/rho by central difference.
H = J/(2 pi lambda)  (I = 2J, H = I/(4 pi lambda))."""
import math, sys
from fractions import Fraction as Q
from scipy.integrate import quad
from multiprocessing import Pool

def geom(mu, phi, rho, z, lam):
    a = math.sqrt(max(0.0, 1 - mu*mu)); b = a*math.cos(phi)
    h = lam*(1 - rho*b) - z*mu
    w = math.sqrt(lam*lam*a*a + mu*mu)
    D = math.sqrt((b - rho)**2 + (a*math.sin(phi))**2 + (lam*mu - z)**2)
    g = min(1.0, max(0.0, h/(w*D)))
    return a, b, h, w, D, g

def F(mu, phi, rho, z, lam):
    a, b, h, w, D, g = geom(mu, phi, rho, z, lam)
    return h*math.acos(g)**2

def Frho(mu, phi, rho, z, lam):
    a, b, h, w, D, g = geom(mu, phi, rho, z, lam)
    al = math.acos(g); s = math.sqrt(max(0.0, 1 - g*g))
    R = al/s if s > 1e-12 else 1.0
    hv = -lam*b; Dv = -(b - rho)/D
    gv = hv/(w*D) - g*Dv/D
    return hv*al*al - 2*h*R*gv

def mu_int(f, fphi_args):
    # mu in [-1,0] plain; mu in [0,1] via mu = 1 - s^2, dmu = 2 s ds (resolves the pole)
    inner = lambda mu: quad(lambda ph: f(mu, ph, *fphi_args), 0, math.pi, epsabs=1e-13, epsrel=1e-12, limit=200)[0]
    lo = quad(inner, -1, 0, epsabs=1e-12, epsrel=1e-11, limit=200)[0]
    pts = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    hi = quad(lambda s: inner(1 - s*s)*2*s, 0, 1, epsabs=1e-12, epsrel=1e-11, limit=400, points=pts)[0]
    return lo + hi

def routeB(rho, z, lam):
    KH = lambda mu, ph, rho, z, lam: (Frho(mu, ph, rho, z, lam) - Frho(mu, ph, -rho, z, lam))/(2*rho)
    return mu_int(KH, (rho, z, lam))/(2*math.pi*lam)

def routeA(rho, z, lam, d):
    E = lambda r: mu_int(F, (r, z, lam))/(2*math.pi*lam)   # E = (1/4pi lam)*2*int_0^pi
    return (E(rho + d) - E(rho - d))/(2*d)/rho

def point(args):
    tag, ir, it, il = args
    r = Q(7,8) + Q(2*ir+1, 256); t = Q(7,8) + Q(2*it+1, 256); lam = Q(2,5) + Q(13,3200)*Q(2*il+1, 2)
    rho = float(r*(1-t*t)/(1+t*t)); z = float(lam*r*2*t/(1+t*t)); lam = float(lam)
    HB = routeB(rho, z, lam)
    HA = routeA(rho, z, lam, 1e-4*rho)
    return f"{tag}\t({ir},{it},{il})\trho={rho:.6f}\tz={z:.6f}\tlam={lam:.6f}\tlam-z={lam-z:.6f}\tH_B={HB:+.6e}\tH_A={HA:+.6e}"

if __name__ == "__main__":
    pts = [("A", 9,15,0), ("N", 10,15,0), ("N", 12,15,0), ("A", 5,14,0), ("N", 6,14,0), ("N", 8,14,0),
           ("N", 0,13,0), ("N", 7,13,0), ("N", 13,13,0)]
    with Pool(4) as p:
        for line in p.imap(point, pts):
            print(line, flush=True)
