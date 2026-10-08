"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.
"""
# DIAGNOSTIC / NOT_EVIDENCE: signed region contributions of 2*pi*lambda*H on the boundary face
import sys, math
sys.path.insert(0,"/home/user/basepoint-geometry/tools/d_ob_p2")
import independent_H_sign as hs
from scipy.integrate import quad
def R(g):
    g=min(1.0,max(0.0,g)); u=1-g*g
    return math.acos(g)/math.sqrt(u) if u>1e-14 else 1.0
def integrand(mu,ph,L,m):
    lam=math.sqrt(L); rho=math.sqrt(1-m*m)
    a=math.sqrt(max(1-mu*mu,0)); b=a*math.cos(ph); q=b*b; s=m-mu
    d0=a*a+rho*rho+L*s*s; Dp=math.sqrt(max(d0-2*rho*b,1e-300)); Dm=math.sqrt(d0+2*rho*b); v=Dp*Dm; u=Dp+Dm
    w=math.sqrt(L*a*a+mu*mu); hp=lam*(1-m*mu-rho*b); hm=lam*(1-m*mu+rho*b)
    Rp,Rm=R(hp/(w*Dp)),R(hm/(w*Dm)); Rb=(Rp+Rm)/2; dR=(Rp-Rm)/2
    B1=L*m*m*mu-L*m*mu*mu-L*m+L*mu+m*m*mu+m*mu*mu-2*mu
    C0=-L*m*mu*mu+L*m+L*mu**3-L*mu-m-mu**3+2*mu
    E=m*q+C0; S3=u*(2*d0-v); LD=(2*d0+v)/u
    F=Rb*(E*S3+4*B1*q*LD)+b*(dR/rho)*(4*rho*rho*E*LD+B1*S3)
    return -L*s*F/(w*v**3)
def region(lo,hi,L,m):
    f=lambda mu: quad(lambda ph: integrand(mu,ph,L,m),0,math.pi,limit=400,points=[0.0] if False else None,epsabs=1e-11,epsrel=1e-9)[0]
    pts=[x for x in (m,) if lo<x<hi]
    return quad(f,lo,hi,limit=400,points=pts or None,epsabs=1e-10,epsrel=1e-8)[0]
def muC(L,m):
    f=lambda mu:-L*m*mu*mu+L*m+L*mu**3-L*mu-m-mu**3+2*mu
    lo,hi=0.0,m
    for _ in range(200):
        c=(lo+hi)/2; (lo,hi)=(c,hi) if f(c)<0 else (lo,c)
    return lo
for L,tau in ((4/25,7/8),(8649/40000,7/8),(0.18,0.95),(4/25,0.99)):
    m=2*tau/(1+tau*tau); rho=(1-tau*tau)/(1+tau*tau); lam=math.sqrt(L); mc=muC(L,m)
    parts={"K[-1,-1/4]":region(-1,-0.25,L,m),"ext_south(-1/4,muC)":region(-0.25,mc,L,m),
           "north(muC,m)":region(mc,m,L,m),"cap(m,1]":region(m,1,L,m)}
    tot=sum(parts.values()); ref=hs.routeB(rho,lam*m,lam)*2*math.pi*lam
    print(f"L={L:.4f} tau={tau} rho={rho:.4f}: total={tot:.6f} routeB_ref={ref:.6f}")
    for k,v in parts.items(): print(f"    {k:22s} {v:+.6f}")
