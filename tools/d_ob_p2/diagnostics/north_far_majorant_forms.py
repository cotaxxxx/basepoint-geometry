"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.

North far (mu_C, m-rho), P units, phi in [0,pi]: integrals of candidate rigorous majorants of [-K_H]_+ :
  (a) pi * mean_xi [2N^2 - h^2(a^2 sin^2 + L s^2)]_+ /(w D^5)      (= N3, exact algebraic form)
  (b) pi * mean_xi  2N^2/(w D^5)                                     (favorable term dropped)
  (c) pi * mean_xi  2(lam^2 b^2/(w D) + h^2/(w D^3))                 (N^2 <= max(...)^2 split)
"""
import math, numpy as np
XI,WXI=np.polynomial.legendre.leggauss(16)
def muC(L,m):
    f=lambda x:(L-1)*x**3-L*m*x*x+(2-L)*x-m*(1-L); lo,hi=0.0,m
    for _ in range(100):
        c=(lo+hi)/2; lo,hi=((c,hi) if f(c)<0 else (lo,c))
    return lo
def run(L,m):
    lam=math.sqrt(L); rho=math.sqrt(max(0,1-m*m)); mc=muC(L,m)
    mu=np.linspace(mc,m-rho,1201); mum=(mu[1:]+mu[:-1])/2; dmu=np.diff(mu)
    t=np.linspace(0,1,601)**2; ph=np.pi*t; phm=(ph[1:]+ph[:-1])/2; dph=np.diff(ph)
    out=np.zeros(3)
    for i0 in range(0,len(mum),32):
        M=mum[i0:i0+32][:,None,None]; W=dmu[i0:i0+32][:,None]*dph[None,:]
        xi=rho*XI[None,None,:]; s=m-M; a2=1-M*M; b=np.sqrt(a2)*np.cos(phm[None,:,None]); w=np.sqrt(L*a2+M*M)
        D2=(b-xi)**2+(a2-b*b)+L*s*s; D=np.sqrt(D2); h=lam*(rho*rho+m*s-xi*b)
        N=lam*(b*s*(m-(1-L)*s)-xi*(b*b-rho*rho-m*s))
        fa=np.maximum(0,2*N*N-h*h*(a2-b*b+L*s*s))/(w*D**5); fb=2*N*N/(w*D**5); fc=2*(L*b*b/(w*D)+h*h/(w*D**3))
        for k,f in enumerate((fa,fb,fc)): out[k]+=math.pi*((f*WXI).sum(-1)/2*W).sum()
    return out
for L,tau in ((4/25,7/8),(8649/40000,7/8),(8649/40000,0.95),(8649/40000,0.99),(8649/40000,0.999),(4/25,0.999)):
    m=2*tau/(1+tau*tau); a,b,c=run(L,m); print(f"L={L:.4f} tau={tau}: (a) N3 exact={a:.4f}  (b) drop favorable={b:.4f}  (c) split={c:.4f}")
