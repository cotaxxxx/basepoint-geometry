# 回転楕円体 K_a={x²+y²+z²/a²≤1} の子午面 (r,z), r≥0, z≥0 における E の停留点を全数探索（診断・倍精度）
import numpy as np, sys, io, time
_o=sys.stdout; sys.stdout=io.StringIO()
from triaxial_center_scan import E
sys.stdout=_o
def grad_rz(r,z,a,h=1e-4):
    A=(1.0,1.0,a)
    gr=(E(np.array([r+h,0,z]),A)-E(np.array([r-h,0,z]),A))/(2*h)
    gz=(E(np.array([r,0,z+h]),A)-E(np.array([r,0,z-h]),A))/(2*h)
    return np.array([gr,gz])
def newton(r,z,a,it=25):
    for _ in range(it):
        g=grad_rz(r,z,a); h=1e-4
        J=np.column_stack([(grad_rz(r+h,z,a)-grad_rz(r-h,z,a))/(2*h),(grad_rz(r,z+h,a)-grad_rz(r,z-h,a))/(2*h)])
        try: d=np.linalg.solve(J,-g)
        except np.linalg.LinAlgError: return None
        r,z=r+d[0],z+d[1]
        if r<-1e-3 or z<-1e-3 or r*r+(z/a)**2>0.985: return None
        if np.linalg.norm(d)<1e-10: break
    return (max(r,0.0),max(z,0.0)) if np.linalg.norm(grad_rz(r,z,a))<1e-7 else None
def census(a, n=28, margin=0.97):
    rs=np.linspace(0,margin,n); zs=np.linspace(0,margin*a,n)
    G=np.full((n,n,2),np.nan)
    for i,r in enumerate(rs):
        for j,z in enumerate(zs):
            if r*r+(z/a)**2<=margin**2: G[i,j]=grad_rz(r,z,a)
    seeds=set()
    for i in range(n-1):
        for j in range(n-1):
            cell=G[i:i+2,j:j+2]
            if np.isnan(cell).any(): continue
            # 各成分に符号変化（または零）があるセルを種にする（軸上・赤道上は対称性で片成分が恒等零）
            sr=(np.sign(cell[...,0]).min()<=0<=np.sign(cell[...,0]).max()); sz=(np.sign(cell[...,1]).min()<=0<=np.sign(cell[...,1]).max())
            if sr and sz: seeds.add((rs[i]+rs[i+1])/2 if True else 0, ) if False else seeds.add(((rs[i]+rs[i+1])/2,(zs[j]+zs[j+1])/2))
    found=[]
    for s in seeds:
        p=newton(*s,a)
        if p and not any(abs(p[0]-q[0])<2e-3 and abs(p[1]-q[1])<2e-3 for q in found): found.append(p)
    return sorted(found)
def classify(p,a):
    r,z=p
    if r<2e-3 and z<2e-3: return "center"
    if r<2e-3: return f"axis  z={z:.4f} (z/a={z/a:.3f})"
    if z<2e-3: return f"equatorial circle r={r:.4f}"
    return f"OFF-AXIS (r,z)=({r:.4f},{z:.4f})"
t0=time.time()
for a in [0.30,0.45,0.60,0.80,1.00,1.50,2.50,3.50,4.50,6.00]:
    pts=census(a)
    print(f"a={a:4.2f}: "+" | ".join(classify(p,a) for p in pts)+f"    [{time.time()-t0:.0f}s]"); sys.stdout.flush()
