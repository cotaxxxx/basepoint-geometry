#!/usr/bin/env python3
"""Diagnostic-only full regular-hat probe v6.

Keeps rho and 1/rho as separate positive endpoint factors; no wide rho Arb hull
is formed.  Not certificate evidence.
"""
from __future__ import annotations
import collections,heapq,json,sys,time
from fractions import Fraction
from pathlib import Path

HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
import blocal_v22_model as model, blocal_v22_policy as policy, blocal_v22_readiness_test as readiness
CONFIG=HERE/"config.blocal-v2.2-readiness-ephemeral.json"
PI_LO=Fraction(333,106);PI_HI=Fraction(355,113);HALF_PI_HI=PI_HI/2

def main()->int:
 c=model.parse_canonical_json(CONFIG.read_bytes());model.validate_config(c)
 from flint import acb,arb,ctx,fmpq
 ctx.prec=c["precision"]["bits"];route,adapter,kernel=readiness.load(c);route.validate_helper_lemmas(arb,fmpq,c)
 def exact(q):return route._arb_exact(arb,fmpq,q)
 def iv(lo,hi):return route._arb_interval(arb,fmpq,lo,hi)
 def can(x,w):return route._canonical(adapter,x,w)
 def scale(x,fl,fh,w):
  a=x*fl;b=x*fh;can(a,w+".lo");can(b,w+".hi");z=a.union(b);can(z,w+".hull");return z
 def clip(x,lo,hi,w):
  a,b=model.interval_fractions(can(x,w),w);a=max(a,lo);b=min(b,hi)
  if a>b:raise route.SplitRequired(w+":EMPTY")
  return iv(a,b)
 def invpair(x,floor,w):
  _,hi=model.interval_fractions(can(x,w+".x"),w+".x");model.need(0<floor<=hi,w+" floor")
  lo=arb(1)/exact(hi);up=arb(1)/exact(floor);can(lo,w+".lo");can(up,w+".hi");return lo,up,hi
 def src(cell,eps):
  if cell.region=="R1":return eps+(1-eps)*cell.a0,eps+(1-eps)*cell.a1,PI_LO*cell.b0,PI_HI*cell.b1
  return eps*cell.a0,eps*cell.a1,eps+(PI_LO-eps)*cell.b0,eps+(PI_HI-eps)*cell.b1
 def div_positive(num,dlo,dhi,w):
  return scale(num,arb(1)/exact(dhi),arb(1)/exact(dlo),w)
 def full(cell,r,lam,cc,phi,u0,u1,s0,eps):
  c0,c1,p0,p1=src(cell,eps);one=arb(1)
  rho2lo=c0*c0+p0*p0;rho2hi=c1*c1+p1*p1;model.need(rho2lo>0,"rho2")
  rlo=exact(rho2lo).sqrt();rhi=exact(rho2hi).sqrt();can(rlo,"rho.lo");can(rhi,"rho.hi")
  irlo=arb(1)/rhi;irhi=arb(1)/rlo;can(irlo,"irho.lo");can(irhi,"irho.hi")
  if cell.region=="R1":
   t=div_positive(phi,c0,c1,"R1.t");k=div_positive(phi.sin(),c0,c1,"R1.k");d=one+t*t;di0,di1,_=invpair(d,Fraction(1),"R1.d")
   Ahat=scale(lam*lam-one,di0,di1,"R1.A");Bhat=scale(k*k+phi.cos()*phi.cos(),di0,di1,"R1.B")
  else:
   t=div_positive(cc,p0,p1,"R2.t");sinc=div_positive(phi.sin(),p0,p1,"R2.sinc");d=one+t*t;di0,di1,_=invpair(d,Fraction(1),"R2.d")
   Ahat=scale((lam*lam-one)*t*t,di0,di1,"R2.A");Bhat=scale(sinc*sinc+t*t*phi.cos()*phi.cos(),di0,di1,"R2.B")
  Ahat=clip(Ahat,Fraction(0),Fraction(8),"A.clip");Bhat=clip(Bhat,Fraction(0),Fraction(1),"B.clip")
  g=route._geometry(adapter,arb,fmpq,r,lam,cc,phi);u=iv(u0,u1)
  if p1<=HALF_PI_HI:
   den=one+g["U"];da,db=model.interval_fractions(can(den,"1+U"),"1+U");da=max(Fraction(1),da);invden0=arb(1)/exact(db);invden1=arb(1)/exact(da)
   rhoB=scale(Bhat,rlo,rhi,"rhoB");term=scale(rhoB,invden0,invden1,"rhoB/den");uor=scale(u,irlo,irhi,"u/rho")
   What=uor+r*term;Vhat=-uor+term
  else:
   What=scale(g["W"],irlo,irhi,"W/rho");Vhat=scale(r-g["U"],irlo,irhi,"V/rho")
  What=clip(What,Fraction(0),Fraction(2048),"What");Vhat=clip(Vhat,Fraction(-2048),Fraction(2048),"Vhat")
  D1=What*What+Ahat+r*r*Bhat;D2=Vhat*Vhat+Bhat+Ahat;i1=can(D1,"D1");i2=can(D2,"D2");a1,b1=model.interval_fractions(i1,"D1");a2,b2=model.interval_fractions(i2,"D2");D=D1 if b1-a1<=b2-a2 else D2
  r2w=None
  if cell.region=="R2":r2w,_=route._r2_w_lower(adapter,arb,fmpq,cell,u0,eps)
  qlo=route._regular_q_lo(cell.region,cell,model.LAMBDA_PLUS+s0,eps,r2w);Dfloor=qlo/rho2hi;z0,z1,Dhi=invpair(D,Dfloor,"Dinvroot")
  z=clip(z0.union(z1),Fraction(0),max(model.interval_fractions(can(z1,"z1"),"z1")),"z")
  y=clip(scale(What,z0,z1,"y"),Fraction(0),Fraction(1),"y");v=clip(scale(Vhat,z0,z1,"v"),Fraction(-1),Fraction(1),"v");gamma=clip(g["L"]*y,Fraction(0),Fraction(1),"gamma");M=g["U"]*Ahat+r*Bhat
  return g,Ahat,Bhat,M,y,v,z,gamma,(rlo,rhi),(irlo,irhi),{"rho2lo":rho2lo,"rho2hi":rho2hi,"Dfloor":Dfloor,"Dhi":Dhi}
 def reg(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps):
  r=route._r_ball(arb_type,fmpq_type,u0,u1);lam=route._lambda_ball(arb_type,fmpq_type,s0,s1);pi=arb_type.pi();one=arb_type(1);ea=exact(eps);a=iv(cell.a0,cell.a1);b=iv(cell.b0,cell.b1)
  if cell.region=="R1":cc=ea+(one-ea)*a;phi=pi*b;measure=(one-ea)*pi
  else:cc=ea*a;phi=ea+(pi-ea)*b;measure=ea*(pi-ea)
  g,Ahat,Bhat,M,y,v,z,gamma,rhop,irp,meta=full(cell,r,lam,cc,phi,u0,u1,s0,eps);h,h1,h2,gs=route._angle_union(kernel_,adapter_,acb_type,arb_type,gamma,False,quantity=="H_U")
  if quantity=="F":val=-g["U"]*h-g["L"]*h1*M*y*z*z
  else:
   # rho appears only in this one J term; apply endpoint factors there.
   rho_term=scale(-Bhat*y*z*z,rhop[0],rhop[1],"rho-term")
   J=g["L"]*(arb_type(2)*g["U"]*h1*M*z**3+g["L"]*h2*M*M*y*z**5+h1*(rho_term+arb_type(3)*M*y*v*z**3))
   val=-scale(J,irp[0],irp[1],"J/rho")
  out=val*measure*exact((cell.a1-cell.a0)*(cell.b1-cell.b0));can(out,"regcon")
  return out,{"v6_full_hat":True,"gamma_fallback_used":bool(gs),"gamma_subdivisions":gs,"D_floor":model.rational_json(meta["Dfloor"])}
 route._regular_eval=reg
 # Use original Duffy evaluator. Priority + incremental exact root sum.
 def enc(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cfg,u0,u1,s0,s1,required_sign=None):
  pc=cfg["route_policies"]["F_ROUTE" if quantity=="F" else "K_ROUTE"];eps=model.fraction_from_dyadic(cfg["geometry"]["eps"]);active={};heap=[];sl=Fraction(0);sh=Fraction(0);ev=0
  def diagnostic(reason):
   norm=model.normalize_interval(model.outward_dyadic(sl,sh));cnt=collections.Counter(v[0].region for v in active.values());tops=sorted([(v[5]-v[4],v[0].region,k,v[0].depth,v[6].get("gamma_fallback_used"),v[6].get("D_floor")) for k,v in active.items()],reverse=True)[:8]
   return {"reason":reason,"evaluations":ev,"leaves":len(active),"regions":dict(cnt),"normalized":norm,"tops":[{"width":model.rational_json(w),"region":r,"path":p,"depth":d,"gamma_fallback":gf,"D_floor":df} for w,r,p,d,gf,df in tops]}
  def add(cell):
   nonlocal sl,sh,ev
   if cell.depth<pc["min_depth"]:
    for ch in route._split(cell):add(ch)
    return
   if ev>=pc["max_evaluations"]:raise RuntimeError("BUDGET "+json.dumps(diagnostic("MAX_EVALUATIONS"),sort_keys=True,separators=(",",":")))
   try:ball,det=route._cell_eval(quantity,kernel_,adapter_,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps)
   except route.SplitRequired as e:
    if cell.depth>=pc["max_depth"]:raise RuntimeError("DEPTH "+json.dumps(diagnostic(e.reason),sort_keys=True,separators=(",",":"))) from e
    for ch in route._split(cell):add(ch)
    return
   ev+=1;ci=can(ball,"child");lo,hi=model.interval_fractions(ci,"child");active[cell.path]=(cell,ball,ci,None,lo,hi,det);sl+=lo;sh+=hi
   if cell.depth<pc["max_depth"]:heapq.heappush(heap,(-(hi-lo),policy.REGION_ORDER[cell.region],cell.path))
  for root in route._root_initial():add(root)
  while True:
   norm=model.normalize_interval(model.outward_dyadic(sl,sh));lo,hi=model.interval_fractions(norm,"root");ok=required_sign is None or required_sign=="POS" and lo>0 or required_sign=="NEG" and hi<0 or required_sign=="NONZERO" and (lo>0 or hi<0)
   if ok:return norm,{"proof_id":"DIAG","evaluation_count":ev}
   item=None
   while heap:
    _,_,p=heapq.heappop(heap);x=active.get(p)
    if x is not None and x[0].depth<pc["max_depth"]:item=x;break
   if item is None:raise RuntimeError("NOSPLIT "+json.dumps(diagnostic("NO_SPLIT"),sort_keys=True,separators=(",",":")))
   cell,ball,ci,_,lo,hi,det=item;del active[cell.path];sl-=lo;sh-=hi
   for ch in route._split(cell):add(ch)
 route.enclose_route=enc
 s=model.fraction_from_dyadic(c["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s;um=model.fraction_from_dyadic(c["u_max_candidates"][0])
 def run(n,fn):
  t=time.perf_counter()
  try:x,p=fn();return {"phase":n,"status":"PASS","elapsed":f"{time.perf_counter()-t:.6f}","enclosure":x,"evaluations":p["evaluation_count"]}
  except Exception as e:return {"phase":n,"status":"FAIL","elapsed":f"{time.perf_counter()-t:.6f}","error_type":type(e).__name__,"error":str(e)}
 res=[run("initial_pos",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,c,1-um,1-um,lam,lam,"POS")),run("l3",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,c,Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG")),run("l2",lambda:route.enclose_f(kernel,adapter,acb,arb,fmpq,c,1-um,1-um,model.LAMBDA_PLUS-model.S_NEG,lam,"POS")),run("l1",lambda:route.enclose_hu(kernel,adapter,acb,arb,fmpq,c,Fraction(1,1<<9),Fraction(1,1<<8),-model.S_NEG,s,"POS"))]
 out={"schema":"blocal-v22-full-hat-probe-v6","certificate_evidence":False,"results":res,"all_pass":all(x["status"]=="PASS" for x in res)};print(json.dumps(out,sort_keys=True,separators=(",",":")),flush=True);return 0 if out["all_pass"] else 1
if __name__=="__main__":raise SystemExit(main())
