#!/usr/bin/env python3
"""D-OB P2 loss decomposition diagnostic v1.
DIAGNOSTIC / NOT_EVIDENCE. User-direct execution only after chat countersign.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys
from fractions import Fraction as Q
from pathlib import Path
import mpmath as mp
import ld_config_v1 as C

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit("INVALID "+s)
def load_prod(path):
    if sha(path)!=C.PRODUCER_SHA256: die("PRODUCER_PIN")
    sp=importlib.util.spec_from_file_location("ld_prod",path)
    m=importlib.util.module_from_spec(sp); sys.modules[sp.name]=m; sp.loader.exec_module(m)
    m.MAX_CELL_COUNT=C.MAX_CELL_COUNT; m.MAX_CELL_DEPTH=C.MAX_CELL_DEPTH
    m.MAX_BOX_DEPTH=C.MAX_BOX_DEPTH; m.RHO0=C.RHO0
    return m
def qstr(x): return str(x)
def arbpair(x): return (str(x.lower()),str(x.upper()))
def widthf(x): return float(x.upper())-float(x.lower())
def midpoint(a,b): return (a+b)/2
def fracmp(q): return mp.mpf(q.numerator)/q.denominator
def rhoz(r,t,l): return r*(1-t*t)/(1+t*t),l*r*2*t/(1+t*t)

def partition_bytes(cells):
    rows=[]
    for c in sorted(cells,key=lambda x:(x.m0,x.m1,x.p0,x.p1,x.depth)):
        rows.append("\t".join(map(str,(c.m0,c.m1,c.p0,c.p1,c.depth))))
    return ("\n".join(rows)+"\n").encode()

def driver_identity(m,data):
    L=str(float(data["L"].lower()))
    U=sum(float((cell.area()*kval).upper()) for cell,kval,_ in data["regular"])+float(data["Bcut"].upper())
    return L,str(U)

def mp_frr(s,z,mu,phi,lam):
    a=mp.sqrt(1-mu*mu); b=a*mp.cos(phi); sp=mp.sin(phi)
    w=mp.sqrt(lam*lam*(1-mu*mu)+mu*mu)
    D=mp.sqrt((b-s)**2+(a*sp)**2+(lam*mu-z)**2)
    h=lam*(1-s*b)-z*mu; g=h/(w*D)
    g=min(mp.mpf(1),max(mp.mpf(0),g))
    u=1-g*g
    if abs(u)<mp.eps*100:
        R=mp.mpf(1); Rg=-mp.mpf(1)/3
    else:
        R=mp.acos(g)/mp.sqrt(u); Rg=(g*R-1)/u
    gr=-lam*b/(w*D)+h*(b-s)/(w*D**3)
    grr=(-2*lam*b*(b-s)-h)/(w*D**3)+3*h*(b-s)**2/(w*D**5)
    T1=4*lam*b*R*gr
    T2=-2*h*Rg*gr*gr
    T3=-2*h*R*grr
    return T1+T2+T3,(D,h,g,R,Rg,gr,grr,T1,T2,T3)

def golden_extreme(f,a,b,maximize):
    gr=(mp.sqrt(5)-1)/2; c=b-gr*(b-a); d=a+gr*(b-a); fc=f(c); fd=f(d)
    for _ in range(C.RANGE_REFINE_STEPS):
        take=(fc<fd) if maximize else (fc>fd)
        if take: a,c,fc=c,d,fd; d=a+gr*(b-a); fd=f(d)
        else: b,d,fd=d,c,fc; c=b-gr*(b-a); fc=f(c)
    x=(a+b)/2; return f(x)

def line_refs(rho,z,mu,phi,lam,dps):
    mp.mp.dps=dps; rr=fracmp(rho); zz=fracmp(z); mm=fracmp(mu); pp=mp.pi*fracmp(phi); ll=fracmp(lam)
    f=lambda s: mp_frr(s,zz,mm,pp,ll)[0]
    avg=mp.quad(f,[-rr,rr],method="tanh-sinh",maxdegree=C.QUAD_MAXDEGREE)/(2*rr)
    n=C.RANGE_GRID_N; xs=[-rr+(2*rr*i)/(n-1) for i in range(n)]; ys=[f(x) for x in xs]
    imin=min(range(n),key=ys.__getitem__); imax=max(range(n),key=ys.__getitem__)
    def bracket(i): return xs[max(0,i-1)],xs[min(n-1,i+1)]
    lo=golden_extreme(f,*bracket(imin),False) if 0<imin<n-1 else ys[imin]
    hi=golden_extreme(f,*bracket(imax),True) if 0<imax<n-1 else ys[imax]
    return avg,lo,hi

def stable_refs(rho,z,mu,phi,lam):
    a=line_refs(rho,z,mu,phi,lam,C.MP_DPS_PRIMARY)
    b=line_refs(rho,z,mu,phi,lam,C.MP_DPS_TIGHT)
    tol=mp.mpf(C.REFERENCE_STABILITY_ABS)
    ok=all(abs(x-y)<=tol for x,y in zip(a,b))
    return b,ok,max(abs(x-y) for x,y in zip(a,b))

def line_avg_only(rho,z,mu,phi,lam,dps):
    mp.mp.dps=dps; rr=fracmp(rho); zz=fracmp(z); mm=fracmp(mu); pp=mp.pi*fracmp(phi); ll=fracmp(lam)
    f=lambda s: mp_frr(s,zz,mm,pp,ll)[0]
    return mp.quad(f,[-rr,rr],method="tanh-sinh",maxdegree=C.QUAD_MAXDEGREE)/(2*rr)

def stable_avg(rho,z,mu,phi,lam):
    a=line_avg_only(rho,z,mu,phi,lam,C.MP_DPS_PRIMARY)
    b=line_avg_only(rho,z,mu,phi,lam,C.MP_DPS_TIGHT)
    return b,abs(a-b)<=mp.mpf(C.REFERENCE_STABILITY_ABS),abs(a-b)

def primitives(m,cell,B,midpoint_surface):
    if midpoint_surface:
        muq=midpoint(cell.m0,cell.m1); phiq=midpoint(cell.p0,cell.p1)
        mu=m.aq(muq); phi=m.PI*m.aq(phiq)
        a=m.aq(1-muq*muq).sqrt(); cp=phi.cos(); sp=phi.sin(); lam=m.aq(B.l0)
    else:
        mu,a,cp,sp,lam=m.surface_intervals(cell,B)
    rho,_,z0,z1=B.bounds(); rs=m.boxq(-rho,rho); z=m.boxq(z0,z1)
    b=a*cp; w2=lam*lam*(m.arb(1)-m.sq_nonnegative(mu))+m.sq_nonnegative(mu); w=w2.sqrt()
    D2=m.sq_nonnegative(b-rs)+m.sq_nonnegative(a*sp)+m.sq_nonnegative(lam*mu-z); D=D2.sqrt()
    h=lam*(m.arb(1)-rs*b)-z*mu; Dw=m.pos_mul(D,w); D3w=m.pos_mul(m.pos_pow(D,3),w)
    g=m.intersect(h/Dw,Q(0),Q(1)); R,Rg,_=m.chart(g)
    gr=-lam*b/Dw+h*(b-rs)/D3w
    wD3=m.pos_mul(w,m.pos_pow(D,3)); wD5=m.pos_mul(w,m.pos_pow(D,5))
    grr=(-2*lam*b*(b-rs)-h)/wD3+3*h*m.sq_nonnegative(b-rs)/wD5
    T1=4*lam*b*R*gr; T2=-2*h*Rg*m.sq_nonnegative(gr); T3=-2*h*R*grr
    return dict(D=D,h=h,gamma=g,R=R,R_gamma=Rg,gamma_rho=gr,gamma_rhorho=grr,T1=T1,T2=T2,T3=T3,F=T1+T2+T3,
                b=b,w=w,rs=rs)

def normalized(m,P,clip):
    D,h,g,R,Rg,b,w,rs=P["D"],P["h"],P["gamma"],P["R"],P["R_gamma"],P["b"],P["w"],P["rs"]
    q=(b-rs)/D; v=m.aq(CURRENT_LAM)*b/w
    if clip:
        q=m.intersect(q,Q(-1),Q(1)); v=m.intersect(v,Q(-1),Q(1))
    return w/D*(4*v*R*(g*q-v)-2*g*Rg*m.sq_nonnegative(g*q-v)-2*g*R*(3*g*m.sq_nonnegative(q)-g-2*v*q))

def cap_floor(m,B):
    rho,_,z0,z1=B.bounds(); z=(z0+z1)/2; lam=B.l0
    # point-box near case; analytic quadratic minimum over mu in [-1,1]
    A=1-lam*lam
    cand=[Q(-1),Q(1)]
    if A!=0:
        mu0=-lam*z/A
        if Q(-1)<=mu0<=Q(1): cand.append(mu0)
    def d2(mu): return 1+z*z-2*lam*z*mu-A*mu*mu
    mn=min(d2(x) for x in cand); R=m.centre_radius(B,"near")[2]
    if mn>=4*R*R: return mp.mpf("0"),False
    mp.mp.dps=C.MP_DPS_TIGHT
    ll,zz,RR=map(fracmp,(lam,z,R)); aa=1-ll*ll
    # solve d2(mu)=4R^2; cap adjacent to mu=1 for these fixed north-side targets
    roots=mp.polyroots([aa,2*ll*zz,4*RR*RR-1-zz*zz])
    inside=[x.real for x in roots if abs(x.imag)<mp.mpf("1e-70") and -1<=x.real<=1]
    if not inside: return mp.mpf("0"),False
    mu0=max(inside); dstar=1-mu0
    C2=9*mp.pi+8
    floor=4*mp.pi*C2/ll*mp.sqrt(dstar)
    return floor,True

def run_target(m,t,out):
    global CURRENT_LAM
    CURRENT_LAM=t["lam"]
    B=m.PBox(t["r"],t["r"],t["t"],t["t"],t["lam"],t["lam"],12)
    cells,data=m.refine_cells(B)
    leaves=[x[0] for x in data["regular"]]+list(data["cut"])
    L,U=driver_identity(m,data)
    ident={"target":t["id"],"r":str(t["r"]),"t":str(t["t"]),"lambda":str(t["lam"]),"L":L,"U":U,
           "expected_L":t["expected_L"],"expected_U":t["expected_U"]}
    if L!=t["expected_L"] or U!=t["expected_U"]:
        ident["status"]="INVALID_IDENTITY"; (out/"identity.json").write_text(json.dumps(ident,indent=2)+"\n"); return ident
    ident["status"]="PASS"
    pb=partition_bytes(leaves); (out/"partition.tsv").write_bytes(pb); ident["partition_sha256"]=hashlib.sha256(pb).hexdigest()
    (out/"identity.json").write_text(json.dumps(ident,indent=2)+"\n")
    rho,_,z0,z1=B.bounds(); z=(z0+z1)/2
    fields=["D","h","gamma","R","R_gamma","gamma_rho","gamma_rhorho","T1","T2","T3"]
    totals=dict(W1=0.0,W2=0.0,W3=0.0,norm_raw=0.0,norm_clip=0.0,area=0.0,unresolved_ref=0,kh_sum=mp.mpf("0"),kh_abs=mp.mpf("0"))
    rows=[]
    for n,(cell,kval,_) in enumerate(data["regular"]):
        Pfull=primitives(m,cell,B,False); Pmid=primitives(m,cell,B,True)
        mu=midpoint(cell.m0,cell.m1); phi=midpoint(cell.p0,cell.p1)
        refs,ok,stab=stable_refs(rho,z,mu,phi,t["lam"])
        W1=float(refs[2]-refs[1]); W2=widthf(Pmid["F"]); W3=widthf(Pfull["F"])
        raw=normalized(m,Pfull,False); clipped=normalized(m,Pfull,True)
        area=float(cell.area()); totals["area"]+=area
        totals["W1"]+=area*W1; totals["W2"]+=area*W2; totals["W3"]+=area*W3
        totals["norm_raw"]+=area*widthf(raw); totals["norm_clip"]+=area*widthf(clipped)
        if not ok: totals["unresolved_ref"]+=1
        amp=mp.mpf(str(area)); totals["kh_sum"]+=amp*refs[0]; totals["kh_abs"]+=amp*abs(refs[0])
        mp.mp.dps=C.MP_DPS_TIGHT
        _,point_terms=mp_frr(mp.mpf("0"),fracmp(z),fracmp(mu),mp.pi*fracmp(phi),fracmp(t["lam"]))
        denom=abs(point_terms[7]+point_terms[8]+point_terms[9])
        local_ratio="ZERO_DENOMINATOR" if denom==0 else str((abs(point_terms[7])+abs(point_terms[8])+abs(point_terms[9]))/denom)
        row={"cell":n,"m0":str(cell.m0),"m1":str(cell.m1),"p0":str(cell.p0),"p1":str(cell.p1),"depth":cell.depth,
             "area":area,"ref_status":"PASS" if ok else "UNRESOLVED_REFERENCE","ref_stability":str(stab),
             "line_average":str(refs[0]),"local_cancellation_ratio_s0":local_ratio,
             "true_range_lo":str(refs[1]),"true_range_hi":str(refs[2]),
             "W1_true_range":W1,"W2_point_interval":W2,"W3_full_cell_interval":W3,
             "loss_average_to_range":W1,"loss_dependency":W2-W1,"loss_surface":W3-W2,
             "normalized_raw_width":widthf(raw),"normalized_clipped_width":widthf(clipped)}
        for f in fields: row[f+"_lo"],row[f+"_hi"]=arbpair(Pfull[f])
        rows.append(row)
    with open(out/"cells.tsv","w",newline="") as f:
        cols=list(rows[0]) if rows else ["cell"]; wr=csv.DictWriter(f,fieldnames=cols,delimiter="\t"); wr.writeheader(); wr.writerows(rows)
    # C_int reference: composite midpoint quadrature on every frozen leaf,
    # including cut leaves. This is a non-interval reference approximation.
    for cell in data["cut"]:
        mu=midpoint(cell.m0,cell.m1); phi=midpoint(cell.p0,cell.p1)
        av,ok,_=stable_avg(rho,z,mu,phi,t["lam"])
        if not ok: totals["unresolved_ref"]+=1
        area=mp.mpf(str(float(cell.area()))); totals["kh_sum"]+=area*av; totals["kh_abs"]+=area*abs(av)
    cint="ZERO_DENOMINATOR" if totals["kh_sum"]==0 else str(totals["kh_abs"]/abs(totals["kh_sum"]))
    floor,cap=cap_floor(m,B); bcut=float(data["Bcut"].upper())
    summary={"label":C.LABEL,"target":t["id"],"identity":"PASS","regular_cells":len(data["regular"]),"cut_cells":len(data["cut"]),
             "aggregate_W1":totals["W1"],"aggregate_W2":totals["W2"],"aggregate_W3":totals["W3"],
             "aggregate_average_to_range":totals["W1"],"aggregate_dependency":totals["W2"]-totals["W1"],
             "aggregate_surface":totals["W3"]-totals["W2"],"normalized_raw_width_area_sum":totals["norm_raw"],
             "normalized_clipped_width_area_sum":totals["norm_clip"],"C_int_composite_midpoint_reference":cint,"unresolved_reference_cells":totals["unresolved_ref"],
             "B_cut":bcut,"true_cap":cap,"B_cut_floor":str(floor),"B_cut_resolution_excess":str(mp.mpf(bcut)-floor)}
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    return summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--producer",required=True); ap.add_argument("--results192",required=True)
    ap.add_argument("--p003",required=True); ap.add_argument("--out",required=True); ap.add_argument("--execute-token",required=True); a=ap.parse_args()
    if a.execute_token!=C.EXECUTION_TOKEN: die("EXECUTION_TOKEN")
    if sha(a.results192)!=C.RESULTS192_SHA256 or sha(a.p003)!=C.P003_SHA256: die("INPUT_PIN")
    out=Path(a.out).resolve()
    forbidden=[Path(a.producer).resolve().parent.parent,Path(__file__).resolve().parents[1]/"comparison_runs"]
    if any(str(out).startswith(str(x)) for x in forbidden): die("OUTPUT_PATH")
    if out.exists() and any(out.iterdir()): die("OUTPUT_NOT_EMPTY")
    out.mkdir(parents=True,exist_ok=True); m=load_prod(a.producer)
    manifest={"label":C.LABEL,"producer_sha256":sha(a.producer),"results192_sha256":sha(a.results192),"p003_sha256":sha(a.p003),
              "script_sha256":sha(__file__),"config_sha256":sha(Path(__file__).with_name("ld_config_v1.py")),"targets":[]}
    for t in C.TARGETS:
        td=out/t["id"]; td.mkdir(); manifest["targets"].append(run_target(m,t,td))
    files={}
    for p in sorted(out.rglob("*")):
        if p.is_file(): files[str(p.relative_to(out))]=sha(p)
    manifest["artifact_sha256"]=files
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
if __name__=="__main__": main()
