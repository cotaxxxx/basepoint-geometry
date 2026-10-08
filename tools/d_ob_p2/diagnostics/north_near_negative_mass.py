"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.

Grid (midpoint-rule) diagnostic, P units, phi in [0,pi]:
  signed  = int int K_H,  negpart = int int [-K_H]_+,
  majPhi  = int int mean_xi [(2Rw/D)Phi]_+,  majPi (N3) = int int mean_xi [(pi w/D)Phi]_+,
  majSq   = int int mean_xi 4Rw(v-gq)^2/D,   with Phi = 2(v-gq)^2 - g^2(1-q^2).
Regions (contract 21'' v1.1): north far = (mu_C, m-rho), near band = [m-rho, 1] (cap included).
"""
import math, numpy as np
XI, WXI = np.polynomial.legendre.leggauss(16)


def muC(L, m):
    f = lambda x: (L-1)*x**3 - L*m*x*x + (2-L)*x - m*(1-L); lo, hi = 0.0, m
    for _ in range(100):
        c = (lo+hi)/2; lo, hi = ((c, hi) if f(c) < 0 else (lo, c))
    return lo


def Rf(g):
    g = np.clip(g, 0, 1); u = 1-g*g
    return np.where(u > 1e-14, np.arccos(g)/np.sqrt(np.maximum(u, 1e-300)), 1.0)


def kernels(mu, ph, xi, lam, rho, z):
    a2 = 1-mu*mu; a = np.sqrt(np.maximum(a2, 0)); b = a*np.cos(ph); w = np.sqrt(lam*lam*a2 + mu*mu)
    D = np.sqrt((b-xi)**2 + (a*np.sin(ph))**2 + (lam*mu-z)**2); h = lam*(1-xi*b) - z*mu
    g = np.clip(h/(w*D), 0, 1); R = Rf(g); u = 1-g*g
    Rg = np.where(u > 1e-10, (g*R-1)/np.maximum(u, 1e-300), -2/3)
    q = (b-xi)/D; v = lam*b/w; gr = (g*q-v)/D; grr = (3*g*q*q - g - 2*v*q)/(D*D)
    Frr = 4*lam*b*R*gr - 2*h*(Rg*gr*gr + R*grr)
    Phi = 2*(v-g*q)**2 - g*g*(1-q*q)
    return Frr, np.maximum(0, 2*R*w/D*Phi), np.maximum(0, np.pi*w/D*Phi), 4*R*w*(v-g*q)**2/D


def region(lo, hi, L, m, nmu, nph, focus=None):
    lam = math.sqrt(L); rho = math.sqrt(max(0, 1-m*m)); z = lam*m
    if focus is None:
        mu = np.linspace(lo, hi, nmu+1)
    else:
        k = nmu//2; t1 = np.linspace(0, 1, k+1)**3; t2 = np.linspace(0, 1, nmu-k+1)**3
        e1 = focus - (focus-lo)*t1[::-1]; e2 = focus + (hi-focus)*t2
        mu = np.concatenate([e1, e2[1:]])
    mum = (mu[1:]+mu[:-1])/2; dmu = np.diff(mu)
    t = np.linspace(0, 1, nph+1)**2; ph = np.pi*t; phm = (ph[1:]+ph[:-1])/2; dph = np.diff(ph)
    out = dict(signed=0.0, neg=0.0, majPhi=0.0, majPi=0.0, majSq=0.0)
    for i0 in range(0, len(mum), 32):
        M = mum[i0:i0+32][:, None, None]; W = dmu[i0:i0+32][:, None]*dph[None, :]
        Frr, mP, mPi, mS = kernels(M, phm[None, :, None], rho*XI[None, None, :], lam, rho, z)
        KH = (Frr*WXI).sum(-1)/2
        out["signed"] += (KH*W).sum(); out["neg"] += (np.maximum(0, -KH)*W).sum()
        out["majPhi"] += ((mP*WXI).sum(-1)/2*W).sum(); out["majPi"] += ((mPi*WXI).sum(-1)/2*W).sum()
        out["majSq"] += ((mS*WXI).sum(-1)/2*W).sum()
    return out


if __name__ == "__main__":
    for L, tau in ((4/25, 7/8), (8649/40000, 7/8), (0.18, 0.95), (4/25, 0.99), (8649/40000, 0.999)):
        m = 2*tau/(1+tau*tau); rho = (1-tau*tau)/(1+tau*tau); mc = muC(L, m)
        far = region(mc, m-rho, L, m, 1200, 600); near = region(m-rho, 1.0, L, m, 2000, 800, focus=m)
        print(f"L={L:.4f} tau={tau} rho={rho:.4f} mu_C={mc:.4f}")
        for nm, r in (("north far", far), ("near band", near)):
            print(f"   {nm:10s} signed={r['signed']:+.5f} negpart={r['neg']:.5f}  majPhi={r['majPhi']:.4f} majPi(N3)={r['majPi']:.4f} majSq={r['majSq']:.4f}", flush=True)
