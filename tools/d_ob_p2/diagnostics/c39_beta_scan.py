"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.
"""
# DIAGNOSTIC / NOT_EVIDENCE: counterexample search for beta(mu) > 0 on (-1/4, mu_dagger)
import numpy as np
def beta_terms(L,m,mu,nphi=4001):
    rho=np.sqrt(max(1-m*m,0.0)); a2=1-mu*mu; a=np.sqrt(a2); s=m-mu
    d=a2+rho*rho+L*s*s
    wmin=2*(d+2*rho*a)**-1.5; wmax=2*(d-2*rho*a)**-1.5
    ph=np.linspace(0,np.pi,nphi); b=a*np.cos(ph); q=b*b
    C0=(L-1)*mu**3-L*m*mu**2+(2-L)*mu-m*(1-L)
    B1=m*(1-L)*mu**2+((1+L)*m*m+L-2)*mu-L*m
    E=m*q+C0; Dp=np.sqrt(d-2*rho*b); Dm=np.sqrt(d+2*rho*b); v=Dp*Dm; u=Dp+Dm
    th=4*((2*d+v)/u)/(u*(2*d-v))
    tr=lambda f: np.trapezoid(f,ph)
    Em=tr(np.maximum(-E,0)); Ep=tr(np.maximum(E,0)); Bq=tr(th*max(B1,0)*q)
    t1=wmin*Em; t2=np.pi/2*wmax*Ep; t3=np.pi/2*wmax*Bq; t4=np.pi/10*wmax
    return t1-t2-t3-t4,(t1,t2,t3,t4,C0,B1)
Ls=np.linspace(4/25,8649/40000,9); ms=np.concatenate([np.linspace(112/113,1,9)])
mus=np.linspace(-0.25,0.4,651)
worst={}
for L in Ls:
  for m in ms:
    vals=np.array([beta_terms(L,m,x)[0] for x in mus])
    neg=mus[vals<=0]
    first=neg.min() if neg.size else None
    worst[(L,m)]=(first,vals.min())
firsts=[v[0] for v in worst.values() if v[0] is not None]
print("parameter cells with some beta<=0 on (-1/4,2/5]:",len(firsts),"of",len(worst))
print("smallest mu with beta<=0 over all params: ",min(firsts) if firsts else None)
k=min(worst,key=lambda k: (worst[k][0] if worst[k][0] is not None else 9))
print("attained at (L,m)=",k)
L,m=k
for x in (-0.25,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4):
    bv,t=beta_terms(L,m,x); print(f"  mu={x:+.3f} beta={bv:+.5f} terms(wminEm,wmaxEp,B+,sec)={tuple(round(z,5) for z in t[:4])} C0={t[4]:+.4f} B1={t[5]:+.4f}")
