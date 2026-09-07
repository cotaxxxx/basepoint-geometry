import numpy as np, sys, io, json, time
_o=sys.stdout; sys.stdout=io.StringIO()
from meridian_census import grad_rz
sys.stdout=_o
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def bisect(f, lo, hi, it=34):
    flo=f(lo)
    for _ in range(it):
        m=(lo+hi)/2; fm=f(m)
        if flo*fm<=0: hi=m
        else: lo,flo=m,fm
    return (lo+hi)/2
def root_on(f, xs):
    v=[f(x) for x in xs]
    for k in range(len(xs)-1):
        if v[k]*v[k+1]<0: return bisect(f, xs[k], xs[k+1])
    return None
t0=time.time()
# 境界進入の近似（r→1⁻ / z→a⁻ を複数の近接値で）
print("扁長側 赤道進入 a_entry の近似（∂_rE(r0,a)=0）:")
for r0 in (0.998,):
    print(f"   r0={r0}: a ≈ {bisect(lambda a: grad_rz(r0,0.0,a)[0], 1.9, 2.6):.4f}")
print("扁平側 極進入 λ_entry の近似（∂_zE(0,z0·a,a)=0）:")
for f0 in (0.998,):
    print(f"   z0/a={f0}: a ≈ {bisect(lambda a: grad_rz(0.0,f0*a,a)[1], 0.55, 0.75):.4f}   （bg-oblate の候補値 0.64355）")
# 枝の追跡
ax_a=np.linspace(0.41,0.64,24); ax_z=[]
for a in ax_a:
    z=root_on(lambda z: grad_rz(0.0,z,a)[1], np.linspace(0.01,0.99*a,80)); ax_z.append(z/a if z else np.nan)
eq_a=np.linspace(2.17,4.72,26); eq_r=[]
for a in eq_a:
    r=root_on(lambda r: grad_rz(r,0.0,a)[0], np.linspace(0.01,0.99,80)); eq_r.append(r if r else np.nan)
print(f"[{time.time()-t0:.0f}s] 枝追跡完了")
json.dump({"axial_branch":{"a":ax_a.tolist(),"z_over_a":ax_z},"equatorial_branch":{"a":eq_a.tolist(),"r":eq_r},
           "a_z":0.407958860300946364,"a_c":4.72438340452113340672,"lambda_entry_ob_candidate":0.6435457703666799690435,
           "a_entry_pro_linear_extrapolation":2.066,"note":"DIAGNOSTIC_ONLY double precision"}, open("family_bifurcation_branches.json","w"), indent=1)
# 図
fig,ax=plt.subplots(figsize=(9,4.8))
L=np.log
ax.axvspan(L(0.6435),L(2.066),color="#f2f2f2",zorder=0); ax.text((L(0.6435)+L(2.066))/2,0.5,"center only\n(quiet zone)",ha="center",va="center",fontsize=9,color="#555")
ax.plot(L(ax_a),ax_z,color="#9467bd",lw=2.2,label="axial pair  $\\pm z^*/a$  (oblate)")
ax.plot(L(eq_a),eq_r,color="#1f77b4",lw=2.2,label="equatorial circle  $r^*$  (prolate)")
ax.plot([L(0.05),L(8)],[0,0],color="k",lw=1.2,label="center (always stationary)")
for x,lab,m in [(L(0.4079588603),"$a_z$ (absorption)","s"),(L(0.6435457704),"$\\lambda_{entry}$ (pole entry)","^"),(L(2.066),"$a_{entry}$ (equator entry, extrapolated ≈2.07)","^"),(L(4.7243834045),"$a_c$ (absorption)","o")]:
    ax.axvline(x,color="k",ls=":",lw=0.8); ax.text(x,1.04,lab,rotation=0,ha="center",fontsize=8)
ax.plot([L(0.4079588603),L(4.7243834045)],[0,0],"ko",ms=6); ax.plot([L(0.6435457704),L(2.066)],[1,1],"k^",ms=7)
ax.set_xlim(L(0.3),L(6.5)); ax.set_ylim(-0.05,1.12); ax.set_xlabel("$\\ln a$   (a = polar/equatorial axis ratio;  oblate < 0 < prolate)")
ax.set_ylabel("position of nontrivial orbit (1 = boundary)"); ax.set_title("Constant-volume spheroids: global stationary structure along the family (diagnostic)",fontsize=10)
ax.legend(loc="center left",fontsize=8,framealpha=0.95); ax.grid(alpha=0.25)
for a in (0.3,0.4,0.5,0.7,1,1.5,2,3,4,5,6): ax.text(L(a),-0.11,str(a),ha="center",fontsize=7,color="#444")
plt.tight_layout(); plt.savefig("spheroid_family_bifurcation_diagram.png",dpi=140); print("figure saved")
