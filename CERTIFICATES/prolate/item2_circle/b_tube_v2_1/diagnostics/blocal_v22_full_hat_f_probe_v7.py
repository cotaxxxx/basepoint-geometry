#!/usr/bin/env python3
"""Diagnostic-only v7: full regular-hat F route with intersected D=q/rho^2."""
from __future__ import annotations
import collections,heapq,json,sys,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
import blocal_v22_model as model,blocal_v22_policy as policy,blocal_v22_readiness_test as readiness
PI_LO=Fraction(333,106);PI_HI=Fraction(355,113);HALF_PI=PI_HI/2

def main():
 cfg=model.parse_canonical_json((HERE/"config.blocal-v2.2-readiness-ephemeral.json").read_bytes());model.validate_config(cfg)
 from flint import acb,arb,ctx,fmpq
 ctx.prec=cfg["precision"]["bits"];route,adapter,kernel=readiness.load(cfg);route.validate_helper_lemmas(arb,fmpq,cfg)
 ex=lambda q:route._arb_exact(arb,fmpq,q);inter=lambda a,b:route._arb_interval(arb,fmpq,a,b)
 def can(x,w):return route._canonical(adapter,x,w)
 def scale(x,lo,hi,w):
  a=x*lo;b=x*hi;can(a,w+".a");can(b,w+".b");z=a.union(b);can(z,w+".u");return z
 def clip(x,lo,hi,w):
  a,b=model.interval_fractions(can(x,w),w);a=max(a,lo);b=min(b,hi)
  if a>b:raise route.SplitRequired(w+":EMPTY")
  return inter(a,b)
 def divp(x,dlo,dhi,w):return scale(x,arb(1)/ex(dhi),arb(1)/ex(dlo),w)
 def src(cell,eps):
  if cell.region=="R1":return eps+(1-eps)*cell.a0,eps+(1-eps)*cell.a1,PI_LO*cell.b0,PI_HI*cell.b1
  return eps*cell.a0,eps*cell.a1,eps+(PI_LO-eps)*cell.b0,eps+(PI_HI-eps)*cell.b1
 def regular_f(kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps):
  r=route._r_ball(arb_type,fmpq_type,u0,u1);lam=route._lambda_ball(arb_type,fmpq_type,s0,s1);one=arb_type(1);pi=arb_type.pi();ea=ex(eps);a=inter(cell.a0,cell.a1);b=inter(cell.b0,cell.b1)
  if cell.region=="R1":cc=ea+(one-ea)*a;phi=pi*b;measure=(one-ea)*pi
  else:cc=ea*a;phi=ea+(pi-ea)*b;measure=ea*(pi-ea)
  c0,c1,p0,p1=src(cell,eps);rho2lo=c0*c0+p0*p0;rho2hi=c1*c1+p1*p1;rl=ex(rho2lo).sqrt();rh=ex(rho2hi).sqrt();irl=arb(1)/rh;irh=arb(1)/rl
  if cell.region=="R1":
   t=divp(phi,c0,c1,"t");k=divp(phi.sin(),c0,c1,"k");den=one+t*t;dl,dh=model.interval_fractions(can(den,"den"),"den");dl=max(Fraction(1),dl);A=divp(lam*lam-one,dl,dh,"Ahat");B=divp(k*k+phi.cos()*phi.cos(),dl,dh,"Bhat")
  else:
   t=divp(cc,p0,p1,"t");si=divp(phi.sin(),p0,p1,"sinc");den=one+t*t;dl,dh=model.interval_fractions(can(den,"den"),"den");dl=max(Fraction(1),dl);A=divp((lam*lam-one)*t*t,dl,dh,"Ahat");B=divp(si*si+t*t*phi.cos()*phi.cos(),dl,dh,"Bhat")
  A=clip(A,Fraction(0),Fraction(8),"A");B=clip(B,Fraction(0),Fraction(1),"B");g=route._geometry(adapter_,arb_type,fmpq_type,r,lam,cc,phi);u=inter(u0,u1)
  if p1<=HALF_PI:
   dd=one+g["U"];dla,dha=model.interval_fractions(can(dd,"1+U"),"1+U");dla=max(Fraction(1),dla);rhoB=scale(B,rl,rh,"rhoB");term=divp(rhoB,dla,dha,"term");uor=scale(u,irl,irh,"uor");Wh=uor+r*term;Vh=-uor+term
  else:Wh=scale(g["W"],irl,irh,"Wh");Vh=scale(r-g["U"],irl,irh,"Vh")
  Wh=clip(Wh,Fraction(0),Fraction(2048),"Whc");Vh=clip(Vh,Fraction(-2048),Fraction(2048),"Vhc")
  D1=Wh*Wh+A+r*r*B;D2=Vh*Vh+B+A;l1,h1=model.interval_fractions(can(D1,"D1"),"D1");l2,h2=model.interval_fractions(can(D2,"D2"),"D2");Dlo=max(l1,l2);Dhi=min(h1,h2)
  # Also use positive component lower endpoints. All are rigorous enclosures of nonnegative summands.
  al,_=model.interval_fractions(can(A,"A.lower"),"A.lower");bl,_=model.interval_fractions(can(B,"B.lower"),"B.lower");Dlo=max(Dlo,al,bl,Fraction(0))
  if Dlo<=0 or Dlo>Dhi:raise route.SplitRequired("D_INTERSECTION_NOT_STRICT")
  zlo=arb(1)/ex(Dhi).sqrt();zhi=arb(1)/ex(Dlo).sqrt();z=clip(zlo.union(zhi),Fraction(0),model.interval_fractions(can(zhi,"zhi"),"zhi")[1],"z")
  y=clip(scale(Wh,zlo,zhi,"y"),Fraction(0),Fraction(1),"yc");gamma=clip(g["L"]*y,Fraction(0),Fraction(1),"gam");M=g["U"]*A+r*B;h,hp,_,gs=route._angle_union(kernel_,adapter_,acb_type,arb_type,gamma,False,False);val=-g["U"]*h-g["L"]*hp*M*y*z*z;out=val*measure*ex((cell.a1-cell.a0)*(cell.b1-cell.b0));can(out,"out")
  return out,{"v7":True,"D_lo":model.rational_json(Dlo),"D_hi":model.rational_json(Dhi),"gamma_fallback_used":bool(gs)}
 route._regular_eval=lambda q,*args: regular_f(*args) if q=="F" else route._regular_eval(q,*args)
 original_cell=route._cell_eval
 def cell_eval(q,*args):
  cell=args[5]
  if q=="F" and cell.region in ("R1","R2"):return regular_f(*args)
  return original_cell(q,*args)
 route._cell_eval=cell_eval
 def enc(r0,r1,l0,l1,sign):
  u0,u1=1-r1,1-r0;s0,s1=l0-model.LAMBDA_PLUS,l1-model.LAMBDA_PLUS;pc=cfg["route_policies"]["F_ROUTE"];eps=model.fraction_from_dyadic(cfg["geometry"]["eps"]);active={};heap=[];SL=Fraction(0);SH=Fraction(0);ev=0
  def diag():
   norm=model.normalize_interval(model.outward_dyadic(SL,SH));tops=sorted([(v[5]-v[4],v[0].region,k,v[0].depth,v[6].get("D_lo")) for k,v in active.items()],reverse=True)[:8];return {"evaluations":ev,"normalized":norm,"regions":dict(collections.Counter(v[0].region for v in active.values())),"tops":[{"width":model.rational_json(w),"region":rg,"path":p,"depth":d,"D_lo":dl} for w,rg,p,d,dl in tops]}
  def add(cell):
   nonlocal SL,SH,ev
   if cell.depth<pc["min_depth"]:
    for ch in route._split(cell):add(ch)
    return
   if ev>=pc["max_evaluations"]:raise RuntimeError("BUDGET "+json.dumps(diag(),sort_keys=True,separators=(",",":")))
   try:ball,det=cell_eval("F",kernel,adapter,acb,arb,fmpq,cell,u0,u1,s0,s1,eps)
   except route.SplitRequired as e:
    if cell.depth>=pc["max_depth"]:raise RuntimeError("DEPTH "+e.reason)
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
   if item is None:raise RuntimeError("NOSPLIT "+json.dumps(diag(),sort_keys=True,separators=(",",":")))
   ce,ba,ci,_,lo,hi,de=item;del active[ce.path];SL-=lo;SH-=hi
   for ch in route._split(ce):add(ch)
 s=model.fraction_from_dyadic(cfg["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s;um=model.fraction_from_dyadic(cfg["u_max_candidates"][0]);tests=[("initial",1-um,1-um,lam,lam,"POS"),("l2",1-um,1-um,model.LAMBDA_PLUS-model.S_NEG,lam,"POS"),("l3",Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG")];res=[]
 for n,r0,r1,l0,l1,sg in tests:
  t=time.perf_counter()
  try:x,e=enc(r0,r1,l0,l1,sg);res.append({"phase":n,"status":"PASS","elapsed":f"{time.perf_counter()-t:.6f}","enclosure":x,"evaluations":e})
  except Exception as er:res.append({"phase":n,"status":"FAIL","elapsed":f"{time.perf_counter()-t:.6f}","error":str(er),"error_type":type(er).__name__})
 out={"schema":"blocal-v22-full-hat-f-probe-v7","certificate_evidence":False,"results":res,"all_pass":all(x["status"]=="PASS" for x in res)};print(json.dumps(out,sort_keys=True,separators=(",",":")));return 0 if out["all_pass"] else 1
if __name__=="__main__":raise SystemExit(main())
