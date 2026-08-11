#!/usr/bin/env python3
"""Diagnostic-only v8 structural-D full-hat F probe.

All strict lower bounds used for D=q/rho^2 are exact rational structural
bounds, never Arb ball lower endpoints.  Not certificate evidence.
"""
from __future__ import annotations
import collections,heapq,json,sys,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
import blocal_v22_model as model,blocal_v22_policy as policy,blocal_v22_readiness_test as readiness
PI_LO=Fraction(333,106);PI_HI=Fraction(355,113);HALF_PI_HI=PI_HI/2

def main()->int:
 cfg=model.parse_canonical_json((HERE/"config.blocal-v2.2-readiness-ephemeral.json").read_bytes());model.validate_config(cfg)
 from flint import acb,arb,ctx,fmpq
 ctx.prec=cfg["precision"]["bits"];route,adapter,kernel=readiness.load(cfg);route.validate_helper_lemmas(arb,fmpq,cfg)
 def ex(q):return route._arb_exact(arb,fmpq,q)
 def iv(lo,hi):return route._arb_interval(arb,fmpq,lo,hi)
 def can(x,w):return route._canonical(adapter,x,w)
 def scale(x,lo,hi,w):
  a=x*lo;b=x*hi;can(a,w+".a");can(b,w+".b");z=a.union(b);can(z,w+".u");return z
 def clip(x,lo,hi,w):
  a,b=model.interval_fractions(can(x,w),w);a=max(a,lo);b=min(b,hi)
  if a>b:raise route.SplitRequired(w+":EMPTY")
  return iv(a,b)
 def divp(x,dlo,dhi,w):
  if not (Fraction(0)<dlo<=dhi):raise route.SplitRequired(w+":NONPOS_DEN")
  return scale(x,arb(1)/ex(dhi),arb(1)/ex(dlo),w)
 def src(cell,eps):
  if cell.region=="R1":return eps+(1-eps)*cell.a0,eps+(1-eps)*cell.a1,PI_LO*cell.b0,PI_HI*cell.b1
  return eps*cell.a0,eps*cell.a1,eps+(PI_LO-eps)*cell.b0,eps+(PI_HI-eps)*cell.b1
 def structural_floor(cell,eps,u1,s0,c0,c1,p0,p1):
  lamlo=model.LAMBDA_PLUS+s0;coef=lamlo*lamlo-1;model.need(coef>0,"lambda structural coef")
  if cell.region=="R1":
   thi=p1/c0
   af=coef/(1+thi*thi)
   return af,{"A_floor":af,"B_floor":Fraction(0),"V2_floor":Fraction(0),"floor_source":"R1_AHAT"}
  # R2 t=c/phi. Ahat lower is positive whenever c0>0.
  tlo=c0/p1;thi=c1/p0
  af=coef*tlo*tlo/(1+thi*thi)
  bf=Fraction(0);vf=Fraction(0);sources=[]
  if af>0:sources.append("A")
  # sin(x)/x >= 1-x^2/6 for x>=0.  Use only when positive.
  sinc_lo=Fraction(1)-p1*p1/Fraction(6)
  if sinc_lo>0:
   bf=sinc_lo*sinc_lo/(1+thi*thi);sources.append("B_SINC_TAYLOR")
  # If phi lower is above a rational upper bound for pi/2, cos(phi)<=0,
  # so U<=0 and |r-U|>=r_lo.  Hence Vhat^2 >= r_lo^2/rho_hi^2.
  if p0>=HALF_PI_HI:
   rlo=Fraction(1)-u1;rho2hi=c1*c1+p1*p1
   if rlo>0:
    vf=rlo*rlo/rho2hi;sources.append("V_LARGE_PHI")
  total=af+bf+vf
  if total<=0:raise route.SplitRequired("STRUCTURAL_D_FLOOR_UNRESOLVED")
  return total,{"A_floor":af,"B_floor":bf,"V2_floor":vf,"floor_source":"+".join(sources)}
 def regular_f(kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps):
  r=route._r_ball(arb_type,fmpq_type,u0,u1);lam=route._lambda_ball(arb_type,fmpq_type,s0,s1);one=arb_type(1);pi=arb_type.pi();ea=ex(eps);a=iv(cell.a0,cell.a1);b=iv(cell.b0,cell.b1)
  if cell.region=="R1":cc=ea+(one-ea)*a;phi=pi*b;measure=(one-ea)*pi
  else:cc=ea*a;phi=ea+(pi-ea)*b;measure=ea*(pi-ea)
  c0,c1,p0,p1=src(cell,eps);rho2lo=c0*c0+p0*p0;rho2hi=c1*c1+p1*p1;model.need(rho2lo>0,"rho2 positive")
  rl=ex(rho2lo).sqrt();rh=ex(rho2hi).sqrt();irl=arb(1)/rh;irh=arb(1)/rl
  if cell.region=="R1":
   t=divp(phi,c0,c1,"R1.t");k=divp(phi.sin(),c0,c1,"R1.k");den=one+t*t;dl,dh=model.interval_fractions(can(den,"R1.den"),"R1.den");dl=max(Fraction(1),dl);A=divp(lam*lam-one,dl,dh,"R1.A");B=divp(k*k+phi.cos()*phi.cos(),dl,dh,"R1.B")
  else:
   t=divp(cc,p0,p1,"R2.t");si=divp(phi.sin(),p0,p1,"R2.sinc");den=one+t*t;dl,dh=model.interval_fractions(can(den,"R2.den"),"R2.den");dl=max(Fraction(1),dl);A=divp((lam*lam-one)*t*t,dl,dh,"R2.A");B=divp(si*si+t*t*phi.cos()*phi.cos(),dl,dh,"R2.B")
  A=clip(A,Fraction(0),Fraction(8),"A.clip");B=clip(B,Fraction(0),Fraction(1),"B.clip");g=route._geometry(adapter_,arb_type,fmpq_type,r,lam,cc,phi);u=iv(u0,u1)
  if p1<=HALF_PI_HI:
   denu=one+g["U"];du0,du1=model.interval_fractions(can(denu,"1+U"),"1+U");du0=max(Fraction(1),du0);rhoB=scale(B,rl,rh,"rhoB");term=divp(rhoB,du0,du1,"rhoB/(1+U)");uor=scale(u,irl,irh,"u/rho");Wh=uor+r*term;Vh=-uor+term
  else:
   Wh=scale(g["W"],irl,irh,"W/rho");Vh=scale(r-g["U"],irl,irh,"V/rho")
  Wh=clip(Wh,Fraction(0),Fraction(2048),"Wh.clip");Vh=clip(Vh,Fraction(-2048),Fraction(2048),"Vh.clip")
  D1=Wh*Wh+A+r*r*B;D2=Vh*Vh+B+A
  _,h1=model.interval_fractions(can(D1,"D1"),"D1");_,h2=model.interval_fractions(can(D2,"D2"),"D2");Dhi=min(h1,h2)
  Dlo,fd=structural_floor(cell,eps,u1,s0,c0,c1,p0,p1)
  if Dhi<Dlo:raise route.SplitRequired("STRUCTURAL_D_INCONSISTENT")
  zlo=arb(1)/ex(Dhi).sqrt();zhi=arb(1)/ex(Dlo).sqrt();can(zlo,"zlo");can(zhi,"zhi")
  z=zlo.union(zhi);can(z,"z.hull")
  y=clip(scale(Wh,zlo,zhi,"y"),Fraction(0),Fraction(1),"y.clip");gamma=clip(g["L"]*y,Fraction(0),Fraction(1),"gamma")
  M=g["U"]*A+r*B;h,hp,_,gs=route._angle_union(kernel_,adapter_,acb_type,arb_type,gamma,False,False);val=-g["U"]*h-g["L"]*hp*M*y*z*z
  out=val*measure*ex((cell.a1-cell.a0)*(cell.b1-cell.b0));can(out,"out")
  return out,{"v8":True,"D_floor":model.rational_json(Dlo),"D_hi":model.rational_json(Dhi),"A_floor":model.rational_json(fd["A_floor"]),"B_floor":model.rational_json(fd["B_floor"]),"V2_floor":model.rational_json(fd["V2_floor"]),"floor_source":fd["floor_source"],"gamma_fallback_used":bool(gs)}
 original=route._cell_eval
 def ce(q,*args):
  cell=args[5]
  if q=="F" and cell.region in ("R1","R2"):return regular_f(*args)
  return original(q,*args)
 def enc(r0,r1,l0,l1,sign):
  u0,u1=1-r1,1-r0;s0,s1=l0-model.LAMBDA_PLUS,l1-model.LAMBDA_PLUS;pc=cfg["route_policies"]["F_ROUTE"];eps=model.fraction_from_dyadic(cfg["geometry"]["eps"]);active={};heap=[];SL=Fraction(0);SH=Fraction(0);ev=0
  def diag(reason):
   norm=model.normalize_interval(model.outward_dyadic(SL,SH));tops=sorted([(v[5]-v[4],v[0].region,k,v[0].depth,v[6].get("D_floor"),v[6].get("floor_source")) for k,v in active.items()],reverse=True)[:10]
   return {"reason":reason,"evaluations":ev,"normalized":norm,"regions":dict(collections.Counter(v[0].region for v in active.values())),"tops":[{"width":model.rational_json(w),"region":rg,"path":p,"depth":d,"D_floor":df,"floor_source":fs} for w,rg,p,d,df,fs in tops]}
  def add(cell):
   nonlocal SL,SH,ev
   if cell.depth<pc["min_depth"]:
    for ch in route._split(cell):add(ch)
    return
   if ev>=pc["max_evaluations"]:raise RuntimeError("BUDGET "+json.dumps(diag("MAX_EVALUATIONS"),sort_keys=True,separators=(",",":")))
   try:ball,det=ce("F",kernel,adapter,acb,arb,fmpq,cell,u0,u1,s0,s1,eps)
   except route.SplitRequired as e:
    if cell.depth>=pc["max_depth"]:raise RuntimeError("DEPTH "+cell.region+":"+cell.path+":"+e.reason)
    for ch in route._split(cell):add(ch)
    return
   ev+=1;ci=can(ball,"child");lo,hi=model.interval_fractions(ci,"child");active[cell.path]=(cell,ball,ci,None,lo,hi,det);SL+=lo;SH+=hi
   if cell.depth<pc["max_depth"]:heapq.heappush(heap,(-(hi-lo),policy.REGION_ORDER[cell.region],cell.path))
  for z in route._root_initial():add(z)
  while True:
   norm=model.normalize_interval(model.outward_dyadic(SL,SH));lo,hi=model.interval_fractions(norm,"root");ok=lo>0 if sign=="POS" else hi<0
   if ok:return norm,ev
   item=None
   while heap:
    _,_,p=heapq.heappop(heap);x=active.get(p)
    if x is not None and x[0].depth<pc["max_depth"]:item=x;break
   if item is None:raise RuntimeError("NOSPLIT "+json.dumps(diag("NO_SPLIT"),sort_keys=True,separators=(",",":")))
   cell,ball,ci,_,lo,hi,det=item;del active[cell.path];SL-=lo;SH-=hi
   for ch in route._split(cell):add(ch)
 s=model.fraction_from_dyadic(cfg["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s;um=model.fraction_from_dyadic(cfg["u_max_candidates"][0]);tests=[("initial",1-um,1-um,lam,lam,"POS"),("l2",1-um,1-um,model.LAMBDA_PLUS-model.S_NEG,lam,"POS"),("l3",Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG")];res=[]
 for n,r0,r1,l0,l1,sg in tests:
  t=time.perf_counter()
  try:x,e=enc(r0,r1,l0,l1,sg);res.append({"phase":n,"status":"PASS","elapsed":f"{time.perf_counter()-t:.6f}","enclosure":x,"evaluations":e})
  except Exception as er:res.append({"phase":n,"status":"FAIL","elapsed":f"{time.perf_counter()-t:.6f}","error":str(er),"error_type":type(er).__name__})
 out={"schema":"blocal-v22-structural-D-probe-v8","certificate_evidence":False,"results":res,"all_pass":all(x["status"]=="PASS" for x in res)};print(json.dumps(out,sort_keys=True,separators=(",",":")),flush=True);return 0 if out["all_pass"] else 1
if __name__=="__main__":raise SystemExit(main())
