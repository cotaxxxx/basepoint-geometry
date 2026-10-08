"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.

Near band (s in [m-1, rho], all phi, |xi|<=rho): sizes of candidate majorant forms
based on N = lam[b(q^2+Ls^2) + p(s(m-s)-q^2)], p=b-xi, q=a sin phi, D^2=p^2+q^2+Ls^2.
  N3     : mean_xi pi[2N^2 - h^2 T]_+/(w D^5)
  SQ     : mean_xi pi 2N^2/(w D^5)                       (positive part dropped)
  M1     : mean_xi pi 2 C^2/(w D),  C = lam|b| + lam a/2 + (m-s)/2   (pointwise |N|/D^2 <= C)
  M2     : mean_xi pi 4 lam^2 [ b^2 (q^2+Ls^2)^2 + p^2 (s(m-s)-q^2)^2 ]/(w D^5)   (termwise 2(x+y)^2<=4x^2+4y^2)
"""
import numpy as np, math
XI, WXI = np.polynomial.legendre.leggauss(48)
def run(L, tau, ns=1500, nph=800):
    lam=math.sqrt(L); m=2*tau/(1+tau*tau); rho=(1-tau*tau)/(1+tau*tau)
    # s grid: concentrate near s=0 (singular point) from both sides
    t=np.linspace(0,1,ns+1)**3; s_neg=(m-1)*t[::-1]; s_pos=rho*t
    s=np.concatenate([s_neg[:-1], s_pos]); sm=(s[1:]+s[:-1])/2; ds=np.diff(s)
    t=np.linspace(0,1,nph+1)**3; ph=np.pi*t; phm=(ph[1:]+ph[:-1])/2; dph=np.diff(ph)   # concentrate near phi=0
    out=dict(N3=0.,SQ=0.,M1=0.,M2=0.,A2=0.,B2=0.,B2x=0.)
    for i0 in range(0,len(sm),64):
        S=sm[i0:i0+64][:,None,None]; W=ds[i0:i0+64][:,None]*dph[None,:]
        PH=phm[None,:,None]; XIv=rho*XI[None,None,:]
        a2=rho*rho+2*m*S-S*S; a=np.sqrt(np.maximum(a2,0)); b=a*np.cos(PH); q=a*np.sin(PH); p=b-XIv
        D2=p*p+q*q+L*S*S; D=np.sqrt(D2); h=lam*(rho*rho+m*S-XIv*b); w=np.sqrt((m-S)**2+L*a2)
        N=lam*(b*(q*q+L*S*S)+p*(S*(m-S)-q*q)); T=q*q+L*S*S
        pre=np.pi/(w*D**5)
        f={ 'N3': pre*np.maximum(0,2*N*N-h*h*T), 'SQ': pre*2*N*N,
            'M1': np.pi*2*(lam*np.abs(b)+lam*a/2+(m-S)/2)**2/(w*D),
            'M2': pre*4*lam*lam*(b*b*(q*q+L*S*S)**2+p*p*(S*(m-S)-q*q)**2),
            'A2': np.pi*4*lam*lam*b*b/(w*D), 'B2': np.pi*4*lam*lam*(S*(m-S)-q*q)**2/(w*D**3),
            'B2x': np.pi*4*lam*lam*p*p*(S*(m-S)-q*q)**2/(w*D**5) }
        for k,v in f.items(): out[k]+=(((v*WXI).sum(-1)/2)*W).sum()
    return rho, out
for L,tau in ((8649/40000,7/8),(4/25,7/8),(0.18,0.95),(0.16,0.99)):
    rho,o=run(L,tau); print(f"L={L:.4f} tau={tau} rho={rho:.4f}  "+"  ".join(f"{k}={v:.5f}" for k,v in o.items()), flush=True)
