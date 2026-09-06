# 体積一定三軸楕円体族 {x²/a1²+y²/a2²+z²/a3² ≤ 1, a1a2a3=1} における中心 Hessian の主係数
# Q_i = ∂²E/∂x_i²(0) を形状平面上で走査する（DIAGNOSTIC_ONLY, 倍精度, 5点差分）。
import numpy as np, json, time, sys
NT, NP = 96, 192
xg, wg = np.polynomial.legendre.leggauss(NT)
th = (xg+1)*np.pi/2; wth = wg*np.pi/2
ph = np.arange(NP)*2*np.pi/NP; wph = 2*np.pi/NP
TH, PH = np.meshgrid(th, ph, indexing='ij')
S, C = np.sin(TH), np.cos(TH); CP, SP = np.cos(PH), np.sin(PH)
W = (wth[:,None]*wph)

def E(p, a):
    a1,a2,a3 = a
    X = np.stack([a1*S*CP, a2*S*SP, a3*C], -1)              # surface points
    n = np.stack([X[...,0]/a1**2, X[...,1]/a2**2, X[...,2]/a3**2], -1)
    # area element |r_θ × r_φ| = a1a2a3 sinθ sqrt(sum (x_i/a_i²)²)  (楕円体の標準公式)
    dA = a1*a2*a3*S*np.sqrt((n**2).sum(-1))
    nu = n/np.sqrt((n**2).sum(-1))[...,None]
    d = X - p
    dn = (d*nu).sum(-1); dl = np.sqrt((d*d).sum(-1))
    g = np.clip(dn/dl, -1.0, 1.0)
    V = 4*np.pi*a1*a2*a3/3
    return (W*np.arccos(g)**2*dn/(3*V)*dA).sum()

def Qdir(a, i, h=0.01):
    e = np.zeros(3); e[i]=1
    f = lambda k: E(k*h*e, a)
    return (-f(2)+16*f(1)-30*f(0)+16*f(-1)-f(-2))/(12*h*h)

def cv_spheroid(ar):            # 軸比 ar (極/赤道) の体積一定回転楕円体
    s = ar**(-1/3); return (s, s, s*ar)

t0=time.time()
print("== 検算 ==")
print("球: Q =", [round(Qdir((1,1,1),i),6) for i in range(3)], " (期待 4/3 =", 4/3, ")")
for ar,lab in [(0.407958860300946,'a_z'),(4.724383404521133,'a_c')]:
    a=cv_spheroid(ar); q=[Qdir(a,i) for i in range(3)]
    print(f"{lab}: axis ratio {ar:.6f}, semiaxes {tuple(round(x,4) for x in a)}, Q =", [f"{v:+.2e}" for v in q])
print("  (a_z で Q_z≈0, a_c で Q_x=Q_y≈0 が期待; 体積一定スケールで係数は ar^(2/3) 倍されるが零点は不変)")
sys.stdout.flush()

# == 形状平面走査 ==  u_i = ln a_i, Σu_i = 0.  座標 (p,q): u1=p/√2 - q/√6, u2=-p/√2 - q/√6, u3=2q/√6
N = 41; L = 1.8
ps = np.linspace(-L, L, N); qs = np.linspace(-L, L, N)
Q = np.full((3, N, N), np.nan)
for iq,qv in enumerate(qs):
    for ip,pv in enumerate(ps):
        u1 = pv/np.sqrt(2) - qv/np.sqrt(6); u2 = -pv/np.sqrt(2) - qv/np.sqrt(6); u3 = 2*qv/np.sqrt(6)
        a = (np.exp(u1), np.exp(u2), np.exp(u3))
        if max(a)/min(a) > 60: continue
        for i in range(3): Q[i,iq,ip] = Qdir(a, i)
    if iq % 8 == 0: print(f"  row {iq}/{N}  t={time.time()-t0:.0f}s"); sys.stdout.flush()
np.savez("triaxial_center_Q.npz", ps=ps, qs=qs, Q=Q)
print("done", round(time.time()-t0), "s")
