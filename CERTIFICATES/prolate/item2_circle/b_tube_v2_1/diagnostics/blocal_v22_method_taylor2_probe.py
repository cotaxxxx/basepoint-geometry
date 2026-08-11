#!/usr/bin/env python3
"""Diagnostic-only B-LOCAL v2.2 method-selection probe.

Regular smooth cells use a rigorous second-order two-variable Taylor integral
form in normalized source coordinates.  T1/T2 reuse the audited Duffy route.
This file is design evidence only and never certificate evidence.
"""
from __future__ import annotations

import hashlib, heapq, json, platform, subprocess, sys, time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import blocal_v22_model as model
import blocal_v22_readiness_test as readiness

CONFIG_PATH=HERE/"config.blocal-v2.2-readiness-ephemeral.json"
RESET_COMMIT="039ce0392c3bcb3499570f6df412583935ea15a4"
PROTOTYPE_ID="BLOCAL_V22_TAYLOR2_CHARTED_METHOD_SELECTION_V1"
BUDGET={
 "max_cell_evaluations_per_enclosure":24000,
 "max_depth":14,
 "max_active_cells":16000,
 "max_total_wall_seconds":900,
 "j_start_max_bisections":40,
 "j_start_max_outer_evaluations":96,
}
HALF=Fraction(1,2)
route=adapter=kernel=acb=arb=fmpq=CONFIG=None

class DiagnosticFailure(RuntimeError): pass

@dataclass(frozen=True)
class J2:
 v:Any; ga:Any; gb:Any; haa:Any; hab:Any; hbb:Any
 def __add__(self,o):
  o=asj(o,self.v);return J2(self.v+o.v,self.ga+o.ga,self.gb+o.gb,self.haa+o.haa,self.hab+o.hab,self.hbb+o.hbb)
 __radd__=__add__
 def __neg__(self):return J2(-self.v,-self.ga,-self.gb,-self.haa,-self.hab,-self.hbb)
 def __sub__(self,o):return self+(-asj(o,self.v))
 def __rsub__(self,o):return asj(o,self.v)-self
 def __mul__(self,o):
  o=asj(o,self.v)
  return J2(self.v*o.v,
   self.ga*o.v+self.v*o.ga,
   self.gb*o.v+self.v*o.gb,
   self.haa*o.v+2*self.ga*o.ga+self.v*o.haa,
   self.hab*o.v+self.ga*o.gb+self.gb*o.ga+self.v*o.hab,
   self.hbb*o.v+2*self.gb*o.gb+self.v*o.hbb)
 __rmul__=__mul__
 def __truediv__(self,o):return self*jinv(asj(o,self.v))
 def __rtruediv__(self,o):return asj(o,self.v)*jinv(self)
 def __pow__(self,n:int):
  if n==0:return asj(1,self.v)
  if n<0:return jinv(self**(-n))
  out=None;base=self;k=n
  while k:
   if k&1:out=base if out is None else out*base
   base=base*base;k>>=1
  return out

def asj(x,like):
 if isinstance(x,J2):return x
 z=like*0;return J2(x,z,z,z,z,z)
def jvar(v,axis):
 z=v*0;one=z+1;return J2(v,one if axis==0 else z,one if axis==1 else z,z,z,z)
def junary(x,f0,f1,f2):
 return J2(f0,f1*x.ga,f1*x.gb,f2*x.ga*x.ga+f1*x.haa,f2*x.ga*x.gb+f1*x.hab,f2*x.gb*x.gb+f1*x.hbb)
def can(x,w):return route._canonical(adapter,x,w)
def fracs(x,w):return model.interval_fractions(can(x,w),w)
def exact(q):return route._arb_exact(arb,fmpq,q)
def iv(lo,hi):return route._arb_interval(arb,fmpq,lo,hi)

def finite_real(z,w):
 if not bool(0 in z.imag):raise route.SplitRequired(w+":IMAGINARY")
 return route._finite_real(adapter,z.real,w)

def jinv(x):
 lo,hi=fracs(x.v,"jinv.x")
 if lo<=0<=hi:raise route.SplitRequired("JINV_DENOM_CONTAINS_ZERO")
 f0=arb(1)/x.v;f1=-arb(1)/(x.v*x.v);f2=arb(2)/(x.v*x.v*x.v)
 can(f0,"jinv.f0");can(f1,"jinv.f1");can(f2,"jinv.f2")
 return junary(x,f0,f1,f2)

def jsqrt(x,floor,w):
 model.need(floor>0,w+":floor")
 _,hi=fracs(x.v,w+".x");model.need(hi>=floor,w+":hi")
 vlo=exact(floor).sqrt();vhi=exact(hi).sqrt();f0=vlo.union(vhi)
 inv=(arb(1)/vhi).union(arb(1)/vlo);f1=inv/2
 p3a=(arb(1)/exact(floor))*(arb(1)/vlo);p3b=(arb(1)/exact(hi))*(arb(1)/vhi)
 f2=-(p3a.union(p3b))/4
 can(f0,w+".f0");can(f1,w+".f1");can(f2,w+".f2")
 return junary(x,f0,f1,f2)
def jsin(x):
 s=x.v.sin();c=x.v.cos();can(s,"sin");can(c,"cos");return junary(x,s,c,-s)
def jcos(x):
 s=x.v.sin();c=x.v.cos();can(s,"sin");can(c,"cos");return junary(x,c,-s,-c)

def half_power_at(q,odd):
 model.need(q>0 and odd>=1 and odd%2==1,"half power")
 qa=exact(q);inv=arb(1)/qa;out=arb(1)/qa.sqrt()
 for _ in range((odd-1)//2):out*=inv
 can(out,f"pow.{odd}");return out

def qpow(x,floor,odd,w):
 model.need(floor>0,w+":floor");_,hi=fracs(x.v,w+".x");model.need(hi>=floor,w+":hi")
 a0=half_power_at(hi,odd);b0=half_power_at(floor,odd);f0=a0.union(b0)
 coef1=-(arb(odd)/2);a1=coef1*half_power_at(hi,odd+2);b1=coef1*half_power_at(floor,odd+2);f1=a1.union(b1)
 coef2=exact(Fraction(odd*(odd+2),4));a2=coef2*half_power_at(hi,odd+4);b2=coef2*half_power_at(floor,odd+4);f2=a2.union(b2)
 can(f0,w+".f0");can(f1,w+".f1");can(f2,w+".f2")
 return junary(x,f0,f1,f2)

def clip_gamma(g,w):
 lo,hi=fracs(g,w);lo=max(Fraction(0),lo);hi=min(Fraction(1),hi)
 if lo>hi:raise route.SplitRequired(w+":GAMMA_EMPTY")
 return iv(lo,hi)

def angle4_one(gb,w):
 c=acb(gb);one=acb(1);z=(one-c)/2
 H=z.hypgeom_2f1(one/2,one/2,acb(3)/2);h=4*z*H*H;x=-h/4
 S=x.hypgeom_0f1(acb(3)/2);T=x.hypgeom_0f1(acb(5)/2);V=x.hypgeom_0f1(acb(7)/2);Q=x.hypgeom_0f1(acb(9)/2)
 h1=-2/S;h2=(acb(2)/3)*T/S**3
 B=(acb(4)/15)*V/S**3-(acb(4)/3)*T*T/S**4
 h3=(-h1/4)*B
 Bx=(acb(8)/105)*Q/S**3-(acb(8)/5)*T*V/S**4+(acb(32)/9)*T**3/S**5
 h4=(-h2/4)*B+(h1*h1/16)*Bx
 return tuple(finite_real(v,w+f".h{k}") for k,v in enumerate((h,h1,h2,h3,h4)))

def angle4_union(g,w):
 gb=clip_gamma(g,w+".clip");lo,hi=fracs(gb,w+".clip");cuts=[lo]
 if lo<HALF<hi:cuts.append(HALF)
 cuts.append(hi);outs=[None]*5
 for i,(a,b) in enumerate(zip(cuts,cuts[1:])):
  vals=angle4_one(iv(a,b),w+f".bin{i}")
  for k,v in enumerate(vals):outs[k]=v if outs[k] is None else outs[k].union(v)
 for k,v in enumerate(outs):can(v,w+f".h{k}.hull")
 return tuple(outs)
def hcompose(g,which,w):
 hs=angle4_union(g.v,w)
 if which==0:f0,f1,f2=hs[0],hs[1],hs[2]
 elif which==1:f0,f1,f2=hs[1],hs[2],hs[3]
 elif which==2:f0,f1,f2=hs[2],hs[3],hs[4]
 else:raise ValueError(which)
 return junary(g,f0,f1,f2)

def chart_q_floor(region,cell,u0,s0,eps):
 lamlo=model.LAMBDA_PLUS+s0;coef=lamlo*lamlo-1;model.need(coef>0,"lambda coef")
 if region=="C1":
  c0=eps+(HALF-eps)*cell.a0;q=coef*c0*c0;model.need(q>0,"C1 q");return q,"A_FLOOR_C1"
 if region=="TH":
  q=coef/Fraction(4);model.need(q>0,"TH q");return q,"A_FLOOR_C_GE_HALF"
 if region=="R2":
  p=route.Cell("R2",cell.path,cell.depth,cell.a0,cell.a1,cell.b0,cell.b1);wlo,_=route._r2_w_lower(adapter,arb,fmpq,p,u0,eps)
  q=route._regular_q_lo("R2",p,lamlo,eps,wlo);model.need(q>0,"R2 q");return q,"R2_CHILD_STRUCTURAL_FLOOR"
 raise ValueError(region)

def geometry_jet(region,a,b,r,lam,cell,u0,s0,eps,quantity,w):
 pi=arb.pi();ea=exact(eps)
 if region=="C1":
  c=ea+exact(HALF-eps)*a;phi=pi*b;S=jsqrt(1-c*c,Fraction(3,4),w+".S");density=asj(arb(1),a.v)
 elif region=="TH":
  theta=(pi/3)*a;phi=pi*b;S=jsin(theta);c=jcos(theta);density=S
 elif region=="R2":
  c=ea*a;phi=ea+(pi-ea)*b;S=jsqrt(1-c*c,Fraction(1)-eps*eps,w+".S");density=asj(arb(1),a.v)
 else:raise ValueError(region)
 U=S*jcos(phi);A=(lam*lam-1)*c*c;B=1-U*U;W=1-r*U;q=W*W+A+r*r*B
 w2=lam*lam*S*S+c*c;L=lam*qpow(w2,Fraction(1),1,w+".w2")
 N=-U*A-r*B;Nr=U*U-1;qfloor,qsource=chart_q_floor(region,cell,u0,s0,eps)
 qm1=qpow(q,qfloor,1,w+".qm1");qm3=qpow(q,qfloor,3,w+".qm3");qm5=qpow(q,qfloor,5,w+".qm5")
 gamma=L*W*qm1;gr=L*N*qm3;grr=L*(Nr*q-3*N*(r-U))*qm5
 h=hcompose(gamma,0,w+".h");h1=hcompose(gamma,1,w+".h1")
 if quantity=="F":base=-U*h+W*h1*gr
 elif quantity=="H_U":
  h2=hcompose(gamma,2,w+".h2");K=-2*U*h1*gr+W*(h2*gr*gr+h1*grr);base=-K
 else:raise ValueError(quantity)
 return density*base,{"chart":region,"q_floor":model.rational_json(qfloor),"q_floor_source":qsource,"taylor_order":2,"gamma_lemma":"SOS_GAMMA_IN_0_1"}

def taylor_cell(quantity,cell,u0,u1,s0,s1,eps):
 rball=route._r_ball(arb,fmpq,u0,u1);lball=route._lambda_ball(arb,fmpq,s0,s1);z=arb(0);rj=J2(rball,z,z,z,z,z);lj=J2(lball,z,z,z,z,z)
 am=(cell.a0+cell.a1)/2;bm=(cell.b0+cell.b1)/2
 fc,detail=geometry_jet(cell.region,jvar(exact(am),0),jvar(exact(bm),1),rj,lj,cell,u0,s0,eps,quantity,f"{cell.region}:{cell.path}:center")
 fb,_=geometry_jet(cell.region,jvar(iv(cell.a0,cell.a1),0),jvar(iv(cell.b0,cell.b1),1),rj,lj,cell,u0,s0,eps,quantity,f"{cell.region}:{cell.path}:box")
 da=cell.a1-cell.a0;db=cell.b1-cell.b0;area=da*db;caa=area*da*da/Fraction(24);cbb=area*db*db/Fraction(24);cab=area*da*db/Fraction(16)
 hlo,hhi=fracs(fb.hab,f"{cell.region}:{cell.path}:Hab");crossrad=max(abs(hlo),abs(hhi))*cab
 src=fc.v*exact(area)+fb.haa*exact(caa)+fb.hbb*exact(cbb)+iv(-crossrad,crossrad)
 if cell.region=="C1":factor=exact(HALF-eps)*arb.pi()
 elif cell.region=="TH":factor=(arb.pi()/3)*arb.pi()
 else:factor=exact(eps)*(arb.pi()-exact(eps))
 out=src*factor;can(out,f"{cell.region}:{cell.path}:out")
 aa0,aa1=fracs(fb.haa,"Haa");bb0,bb1=fracs(fb.hbb,"Hbb")
 detail.update({"_score_a":max(abs(aa0),abs(aa1))*caa+crossrad/Fraction(2),"_score_b":max(abs(bb0),abs(bb1))*cbb+crossrad/Fraction(2),"remainder_rule":"diag area*w^2/24 + cross supabs*area*wa*wb/16"})
 return out,detail

ORDER={"T1":0,"T2":1,"R2":2,"C1":3,"TH":4}
def roots():return [route.Cell(r,r,0,Fraction(0),Fraction(1),Fraction(0),Fraction(1)) for r in ORDER]
def split_cell(cell,detail=None):
 if detail and cell.region in ("R2","C1","TH"):axis="a" if detail["_score_a"]>=detail["_score_b"] else "b"
 else:axis="a" if cell.a1-cell.a0>=cell.b1-cell.b0 else "b"
 if axis=="a":m=(cell.a0+cell.a1)/2;bs=[(cell.a0,m,cell.b0,cell.b1),(m,cell.a1,cell.b0,cell.b1)]
 else:m=(cell.b0+cell.b1)/2;bs=[(cell.a0,cell.a1,cell.b0,m),(cell.a0,cell.a1,m,cell.b1)]
 return [route.Cell(cell.region,cell.path+str(i),cell.depth+1,*b) for i,b in enumerate(bs)]
def cover_ok(active):
 for rg in ORDER:
  cs=[v[0] for v in active.values() if v[0].region==rg]
  if sum((c.a1-c.a0)*(c.b1-c.b0) for c in cs)!=1:return False
  for i,c in enumerate(cs):
   for d in cs[:i]:
    if max(c.a0,d.a0)<min(c.a1,d.a1) and max(c.b0,d.b0)<min(c.b1,d.b1):return False
 return True

def eval_cell(quantity,cell,u0,u1,s0,s1,eps):
 if cell.region in ("T1","T2"):return route._duffy_eval(quantity,kernel,adapter,acb,arb,fmpq,cell,u0,u1,s0,s1,eps)
 return taylor_cell(quantity,cell,u0,u1,s0,s1,eps)
def sign(ivd):
 lo,hi=model.interval_fractions(ivd,"sign");return "POS" if lo>0 else "NEG" if hi<0 else "UNRESOLVED"

def enclose(quantity,u0,u1,s0,s1,mode,run_start,accept:Callable[[dict[str,Any]],bool]|None=None):
 eps=model.fraction_from_dyadic(CONFIG["geometry"]["eps"]);active={};heap=[];SL=Fraction(0);SH=Fraction(0);ev=0;counts={k:0 for k in ORDER};splits=0
 def timed():
  if time.perf_counter()-run_start>BUDGET["max_total_wall_seconds"]:raise DiagnosticFailure("TOTAL_WALL_TIME_BUDGET")
 def add(cell):
  nonlocal SL,SH,ev,splits
  timed()
  if ev>=BUDGET["max_cell_evaluations_per_enclosure"]:raise DiagnosticFailure("CELL_EVALUATION_BUDGET")
  try:v,d=eval_cell(quantity,cell,u0,u1,s0,s1,eps)
  except route.SplitRequired as ex:
   if cell.depth>=BUDGET["max_depth"]:raise DiagnosticFailure("DEPTH:"+cell.region+":"+cell.path+":"+ex.reason)
   splits+=1
   for ch in split_cell(cell):add(ch)
   return
  ev+=1;counts[cell.region]+=1;ci=can(v,"child");lo,hi=model.interval_fractions(ci,"child");active[cell.path]=(cell,lo,hi,d);SL+=lo;SH+=hi
  if cell.depth<BUDGET["max_depth"]:heapq.heappush(heap,(-(hi-lo),ORDER[cell.region],cell.path))
  if len(active)>BUDGET["max_active_cells"]:raise DiagnosticFailure("ACTIVE_CELL_BUDGET")
 for r in roots():add(r)
 while True:
  timed();root=model.normalize_interval(model.outward_dyadic(SL,SH));sg=sign(root)
  ok=(mode=="POS" and sg=="POS") or (mode=="NEG" and sg=="NEG") or (mode=="NONZERO" and sg in ("POS","NEG")) or (mode=="CUSTOM" and accept is not None and accept(root))
  if ok:
   if not cover_ok(active):raise DiagnosticFailure("INCOMPLETE_COVER")
   return root,{"cell_evaluations":ev,"region_evaluations":counts,"active_leaves":len(active),"max_depth_used":max(x[0].depth for x in active.values()),"split_count":splits,"complete_closed_cover":True,"direct_pinned_integrator_called":False}
  chosen=None
  while heap:
   _,_,p=heapq.heappop(heap)
   if p in active and active[p][0].depth<BUDGET["max_depth"]:chosen=active[p];break
  if chosen is None:raise DiagnosticFailure("PREDICATE_UNRESOLVED_AT_DEPTH_LIMIT")
  cell,lo,hi,d=chosen;del active[cell.path];SL-=lo;SH-=hi;splits+=1
  for ch in split_cell(cell,d):add(ch)

def f_enclose(r0,r1,l0,l1,mode,start,accept=None):return enclose("F",1-r1,1-r0,l0-model.LAMBDA_PLUS,l1-model.LAMBDA_PLUS,mode,start,accept)
def hu_enclose(u0,u1,s0,s1,mode,start):return enclose("H_U",u0,u1,s0,s1,mode,start)

def preflight():
 vals=angle4_one(exact(Fraction(1)),"preflight")
 exp={1:Fraction(-2),2:Fraction(2,3),3:Fraction(-8,15),4:Fraction(24,35)}
 for k,q in exp.items():lo,hi=fracs(vals[k],f"pre.h{k}");model.need(lo<=q<=hi,f"h{k}(1)")
 return {"h_endpoint_exact":{f"h{k}":model.rational_json(q) for k,q in exp.items()},"taylor_integral_remainder":"diag area*w^2/24; cross supabs*area*wa*wb/16","partition":"T1+T2 Duffy [0,eps]^2; R2 [0,eps]x[eps,pi]; C1 [eps,1/2]x[0,pi]; TH theta[0,pi/3]x[0,pi]","status":"PASS"}

def phase(name,domain,pred,fn):
 t=time.perf_counter()
 try:
  enc,d=fn();return {"phase":name,"tested_domain":domain,"final_enclosure":enc,"strict_predicate":pred,"predicate_result":True,"evaluation_subdivision_counts":d,"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":None,"certificate_evidence":False}
 except Exception as e:return {"phase":name,"tested_domain":domain,"final_enclosure":None,"strict_predicate":pred,"predicate_result":False,"evaluation_subdivision_counts":None,"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":f"{type(e).__name__}:{e}","certificate_evidence":False}

def jstart(lam,um,start,initial):
 t=time.perf_counter();outer=0;pts=[];left=1-um;right=Fraction(1)
 try:
  if initial is None:fleft,lr=f_enclose(left,left,lam,lam,"POS",start);outer+=1
  else:fleft=initial;lr={"reused":"J_START_INITIAL_F"}
  pts.append({"r":model.rational_json(left),"sign":"POS","enclosure":fleft,"role":"INITIAL_LEFT"})
  neg=None
  for _ in range(BUDGET["j_start_max_bisections"]):
   if outer>=BUDGET["j_start_max_outer_evaluations"]:raise DiagnosticFailure("J_OUTER_BUDGET")
   m=(left+right)/2;fm,_=f_enclose(m,m,lam,lam,"NONZERO",start);outer+=1;sg=sign(fm);rec={"r":model.rational_json(m),"sign":sg,"enclosure":fm,"role":"BISECTION_MIDPOINT"};pts.append(rec)
   if sg=="NEG":right=m;neg=fm;rec["role"]="RETAINED_RIGHT";break
   if sg=="POS":left=m;fleft=fm;rec["role"]="RETAINED_LEFT";continue
   raise DiagnosticFailure("BISECTION_UNRESOLVED")
  if neg is None or right>=1:raise DiagnosticFailure("NO_INTERIOR_NEGATIVE_RIGHT")
  u0,u1=1-right,1-left;s=lam-model.LAMBDA_PLUS;hu,hd=hu_enclose(u0,u1,s,s,"POS",start);outer+=1;D=model.interval_negate(hu);dlo,dhi=model.interval_fractions(D,"D");model.need(dhi<0,"Fr negative")
  cond5={"phase":"J_START_DERIVATIVE_BRACKET","tested_domain":{"r_interval":model.interval_json(left,right),"u_interval":model.interval_json(u0,u1),"lambda_start":model.rational_json(lam)},"final_enclosure":D,"H_u":hu,"exact_relation":"F_r=-H_u","strict_predicate":"0 notin F_r and sup(F_r)<0","predicate_result":True,"evaluation_subdivision_counts":hd,"elapsed_seconds":None,"failure_reason":None,"certificate_evidence":False}
  mid=(left+right)/2
  def accept(Fm):
   qlo,qhi=model.interval_divide_negative_denominator(Fm,D);nlo,nhi=mid-qhi,mid-qlo;return left<nlo<=nhi<right
  Fm,md=f_enclose(mid,mid,lam,lam,"CUSTOM",start,accept);outer+=1;qlo,qhi=model.interval_divide_negative_denominator(Fm,D);N=model.outward_dyadic(mid-qhi,mid-qlo);nlo,nhi=model.interval_fractions(N,"N");model.need(left<nlo<=nhi<right,"Newton contain")
  path={"phase":"J_START_COMPLETE_PATH","tested_domain":{"initial_bracket":model.interval_json(1-um,Fraction(1)),"lambda_start":model.rational_json(lam)},"strict_predicate":"strict bisection signs + F_r<0 + strict interval-Newton self-containment","predicate_result":True,"ordered_bisection":pts,"derivative":cond5,"newton":{"bracket":model.interval_json(left,right),"midpoint":model.rational_json(mid),"F_m":Fm,"D":D,"quotient":model.outward_dyadic(qlo,qhi),"newton_image":N,"strict_self_containment":True,"evaluation_subdivision_counts":md},"outer_evaluations":outer,"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":None,"certificate_evidence":False}
  return path,cond5
 except Exception as e:return {"phase":"J_START_COMPLETE_PATH","tested_domain":{"initial_bracket":model.interval_json(1-um,Fraction(1)),"lambda_start":model.rational_json(lam)},"strict_predicate":"strict bisection signs + F_r<0 + strict interval-Newton self-containment","predicate_result":False,"ordered_bisection":pts,"outer_evaluations":outer,"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":f"{type(e).__name__}:{e}","certificate_evidence":False},None

def main():
 global route,adapter,kernel,acb,arb,fmpq,CONFIG
 start=time.perf_counter();CONFIG=model.parse_canonical_json(CONFIG_PATH.read_bytes());model.validate_config(CONFIG)
 from flint import acb as A,arb as R,ctx,fmpq as Q
 import flint
 acb,arb,fmpq=A,R,Q;ctx.prec=CONFIG["precision"]["bits"];route,adapter,kernel=readiness.load(CONFIG)
 eps=model.fraction_from_dyadic(CONFIG["geometry"]["eps"]);model.need(eps==Fraction(1,256),"eps")
 pf=preflight();s1=model.fraction_from_dyadic(CONFIG["lambda_candidates"][0]);um=model.fraction_from_dyadic(CONFIG["u_max_candidates"][0]);lam=model.LAMBDA_PLUS+s1
 proto=Path(__file__).read_bytes();head=subprocess.run(["git","-C",str(ROOT),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
 common={"prototype_id":PROTOTYPE_ID,"prototype_sha256":hashlib.sha256(proto).hexdigest(),"prototype_bytes":len(proto),"git_source_head":head,"design_reset_commit":RESET_COMMIT,"runtime_environment":{"python":sys.version.split()[0],"platform":platform.platform(),"python_flint":getattr(flint,"__version__","UNKNOWN"),"precision_bits":CONFIG["precision"]["bits"]},"exact_values":{"eps":model.dyadic_json(eps),"lambda_plus":model.rational_json(model.LAMBDA_PLUS),"s_first":model.dyadic_json(s1),"lambda_start":model.rational_json(lam),"u_max":model.dyadic_json(um),"s_neg":model.dyadic_json(model.S_NEG)},"declared_budgets":BUDGET,"preflight":pf,"certificate_evidence":False}
 res=[]
 p1=phase("J_START_INITIAL_F",{"r":model.rational_json(1-um),"lambda":model.rational_json(lam)},"F_lo>0",lambda:f_enclose(1-um,1-um,lam,lam,"POS",start));res.append(p1);initial=p1["final_enclosure"] if p1["predicate_result"] else None
 res.append(phase("L2_FIRST_FACE",{"r":model.rational_json(1-um),"s_interval":model.interval_json(-model.S_NEG,s1)},"F_lo>0",lambda:f_enclose(1-um,1-um,model.LAMBDA_PLUS-model.S_NEG,lam,"POS",start)))
 res.append(phase("L3_FIRST_FACE",{"r":model.rational_json(Fraction(1)),"s_interval":model.interval_json(Fraction(0),s1)},"F_hi<0",lambda:f_enclose(Fraction(1),Fraction(1),model.LAMBDA_PLUS,lam,"NEG",start)))
 res.append(phase("L1_REPRESENTATIVE_TILE",{"u_interval":model.interval_json(Fraction(1,512),Fraction(1,256)),"s_interval":model.interval_json(-model.S_NEG,s1)},"H_u_lo>0",lambda:hu_enclose(Fraction(1,512),Fraction(1,256),-model.S_NEG,s1,"POS",start)))
 jp,c5=jstart(lam,um,start,initial);res.append(c5 if c5 is not None else {"phase":"J_START_DERIVATIVE_BRACKET","tested_domain":None,"final_enclosure":None,"strict_predicate":"0 notin F_r and sup(F_r)<0","predicate_result":False,"evaluation_subdivision_counts":None,"elapsed_seconds":None,"failure_reason":"NOT_REACHED_OR_NOT_CERTIFIED","certificate_evidence":False});res.append(jp)
 req=["J_START_INITIAL_F","L2_FIRST_FACE","L3_FIRST_FACE","L1_REPRESENTATIVE_TILE","J_START_DERIVATIVE_BRACKET","J_START_COMPLETE_PATH"];by={x["phase"]:x for x in res};ok=all(by[n]["predicate_result"] for n in req)
 out=common|{"schema":"blocal-v22-method-selection-feasibility-v1","mandatory_conditions":req,"results":res,"all_six_conditions_pass":ok,"method_selection_gate":"PASS" if ok else "FAIL","total_elapsed_seconds":f"{time.perf_counter()-start:.6f}"}
 print(json.dumps(out,sort_keys=True,separators=(",",":")),flush=True);return 0 if ok else 1
if __name__=="__main__":raise SystemExit(main())
