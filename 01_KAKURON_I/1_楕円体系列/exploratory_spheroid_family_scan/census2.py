import numpy as np, sys, io, time
_o=sys.stdout; sys.stdout=io.StringIO()
from meridian_census import grad_rz, newton, classify
sys.stdout=_o
def census2(a, n=34, margin=0.985):
    rs=np.linspace(0,margin,n); zs=np.linspace(0,margin*a,n)
    N=np.full((n,n),np.inf)
    for i,r in enumerate(rs):
        for j,z in enumerate(zs):
            if r*r+(z/a)**2<=margin**2: N[i,j]=np.linalg.norm(grad_rz(r,z,a))
    seeds=[]
    for i in range(n):
        for j in range(n):
            if not np.isfinite(N[i,j]): continue
            nb=N[max(i-1,0):i+2, max(j-1,0):j+2]
            if N[i,j]<=nb.min()+1e-15: seeds.append((rs[i],zs[j]))
    found=[]
    for s in seeds:
        p=newton(*s,a)
        if p and not any(abs(p[0]-q[0])<2e-3 and abs(p[1]-q[1])<2e-3 for q in found): found.append(p)
    return sorted(found)
t0=time.time()
print("== 子午面 census（|∇E| 局所最小を種に Newton、margin 0.985）==")
for a in [0.45,0.60,0.62,1.00,1.50,2.00,2.20,2.50,4.72]:
    pts=census2(a); print(f"a={a:4.2f}: "+(" | ".join(classify(p,a) for p in pts) or "(none)")+f"   [{time.time()-t0:.0f}s]"); sys.stdout.flush()
print("\n== 扁長側：赤道停留円の半径 r*(a) と境界進入 ==")
def geq(r,a): return grad_rz(r,0.0,a)[0]
def rstar(a):
    rs=np.linspace(0.02,0.985,120); g=np.array([geq(r,a) for r in rs])
    for k in range(len(rs)-1):
        if g[k]*g[k+1]<0:
            lo,hi=rs[k],rs[k+1]
            for _ in range(40):
                m=(lo+hi)/2
                if geq(lo,a)*geq(m,a)<=0: hi=m
                else: lo=m
            return (lo+hi)/2
    return None
print("   a     r*(a)      ∂_rE(0.985,a)")
for a in [4.6,4.0,3.5,3.0,2.6,2.4,2.3,2.2,2.1,2.0,1.9]:
    r=rstar(a); print(f"  {a:4.2f}   {('%.4f'%r) if r else '  none '}     {geq(0.985,a):+.5f}")
# 境界進入 a_entry: ∂_rE(0.985,a)=0 の a を二分法（境界極限の近似）
lo,hi=1.9,2.6
for _ in range(30):
    m=(lo+hi)/2
    if geq(0.985,lo)*geq(0.985,m)<=0: hi=m
    else: lo=m
print(f"\n  ∂_rE(r=0.985, a)=0 となる a ≈ {(lo+hi)/2:.4f}  （r→1 の境界極限の近似値。扁平側の λ_entry_ob=0.6435 の赤道版）")
