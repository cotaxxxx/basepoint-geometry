#!/usr/bin/env python3
"""B-LOCAL v2.2 Taylor2 method-selection diagnostic, revision 5.

Byte-pinned implementation of the six effective-floor sites, Duffy local
geometry reconstruction, and the strengthened Duffy Z lower bound specified
by BLOCAL_V22_METHOD_SELECTION_V5_SPEC. Design evidence only.
"""
from __future__ import annotations
import contextlib,hashlib,io,json,os
from fractions import Fraction
from pathlib import Path
from typing import Any
import blocal_v22_method_taylor2_probe_v4 as v4

PROTOTYPE_ID="BLOCAL_V22_TAYLOR2_METHOD_SELECTION_V5_EFFECTIVE_FLOORS"
SPEC_PATH=Path(__file__).with_name("BLOCAL_V22_METHOD_SELECTION_V5_SPEC.md")
SPEC_SHA256="42a9b79865a4f5f4388542cc9a52720513b1e9196debdd882f7c1a8f9b1e0cb6"
V4_SHA256="12a172b24bcdadf3a06ddaf582390400a249b411692f1fe3c9ec1d40ac0f694d"
V3_SHA256="dcb09f614369ee10a49b9eecb71bd184cd0565dc23c79857347bfae762573824"
base=v4.base
HALF=Fraction(1,2)
_REGISTRY:dict[str,dict[str,Any]]={}
_STATS={"effective_floor_calls":0,"natural_selected":0,"structural_selected":0,
 "natural_fallbacks":0,"duffy_calls":0,"duffy_corner_calls":0,
 "duffy_noncorner_calls":0,"gamma_fallback_corner":0,"gamma_fallback_noncorner":0,
 "duffy_what_component_dropped":0}

def canonical(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def rj(x:Fraction):return base.model.rational_json(x)
def clamp0(x:Fraction)->Fraction:return max(Fraction(0),x)

def intern(rec:dict[str,Any])->str:
 dig=hashlib.sha256(canonical(rec)).hexdigest();prior=_REGISTRY.get(dig)
 if prior is not None and prior!=rec:raise RuntimeError("V5_FLOOR_RECORD_HASH_COLLISION")
 _REGISTRY[dig]=rec;return dig

def natural_lower(x:Any,w:str)->tuple[Fraction|None,str|None]:
 try:
  lo,_=base.fracs(x,w)
  if lo<=0:return None,"NATURAL_LOWER_NONPOSITIVE"
  return lo,None
 except Exception as e:return None,"NATURAL_LOWER_UNAVAILABLE:"+type(e).__name__

def effective(site:str,structural:Fraction,x:Any,w:str,region:str,scope:str,
              cell:Any)->tuple[Fraction,str]:
 base.model.need(structural>=0,w+":STRUCTURAL_FLOOR_NEGATIVE")
 natural,reason=natural_lower(x,w+".natural")
 if natural is None:
  eff=structural;source="structural";_STATS["natural_fallbacks"]+=1
 else:
  eff=max(structural,natural);source="natural" if natural>structural else "structural"
 _STATS["effective_floor_calls"]+=1;_STATS[source+"_selected"]+=1
 rec={"site":site,"chart":region,"scope":scope,"path":cell.path,
  "structural":rj(structural),"natural":None if natural is None else rj(natural),
  "effective":rj(eff),"selected_source":source,"fallback_reason":reason,
  "shared_by":["f0","f1","f2"]}
 return eff,intern(rec)

def geometry_jet(region,a,b,r,lam,cell,u0,s0,eps,quantity,w):
 pi=base.arb.pi();ea=base.exact(eps);scope="center" if w.endswith(":center") else "box"
 floor_ids=[]
 if region=="C1":
  c=ea+base.exact(HALF-eps)*a;phi=pi*b
  qstruct,Sstruct,c1dig,c1rec=v4.c1_floor(cell,r,s0,eps)
  S2=1-c*c;Sfloor,Sdig=effective("ORDINARY_S2",Sstruct,S2.v,w+".S2",region,scope,cell)
  S=base.jsqrt(S2,Sfloor,w+".S");density=base.asj(base.arb(1),a.v);floor_ids.append(Sdig)
 elif region=="TH":
  theta=(pi/3)*a;phi=pi*b;S=base.jsin(theta);c=base.jcos(theta);density=S
  qstruct,qsource=base.chart_q_floor(region,cell,u0,s0,eps);c1dig=None;c1rec=None
 elif region=="R2":
  c=ea*a;phi=ea+(pi-ea)*b;S2=1-c*c;Sstruct=1-eps*eps
  Sfloor,Sdig=effective("ORDINARY_S2",Sstruct,S2.v,w+".S2",region,scope,cell)
  S=base.jsqrt(S2,Sfloor,w+".S");density=base.asj(base.arb(1),a.v);floor_ids.append(Sdig)
  qstruct,qsource=base.chart_q_floor(region,cell,u0,s0,eps);c1dig=None;c1rec=None
 else:raise ValueError(region)
 U=S*base.jcos(phi);A=(lam*lam-1)*c*c;B=1-U*U;W=1-r*U;q=W*W+A+r*r*B
 w2=lam*lam*S*S+c*c
 wfloor,Wdig=effective("ORDINARY_W2",Fraction(1),w2.v,w+".w2",region,scope,cell)
 L=lam*base.qpow(w2,wfloor,1,w+".w2");floor_ids.append(Wdig)
 N=-U*A-r*B;Nr=U*U-1
 qfloor,Qdig=effective("ORDINARY_Q",qstruct,q.v,w+".q",region,scope,cell);floor_ids.append(Qdig)
 qm1=base.qpow(q,qfloor,1,w+".qm1");qm3=base.qpow(q,qfloor,3,w+".qm3");qm5=base.qpow(q,qfloor,5,w+".qm5")
 gamma=L*W*qm1;gr=L*N*qm3;grr=L*(Nr*q-3*N*(r-U))*qm5
 h=base.hcompose(gamma,0,w+".h");h1=base.hcompose(gamma,1,w+".h1")
 if quantity=="F":out=-U*h+W*h1*gr
 elif quantity=="H_U":
  h2=base.hcompose(gamma,2,w+".h2");out=-(-2*U*h1*gr+W*(h2*gr*gr+h1*grr))
 else:raise ValueError(quantity)
 detail={"chart":region,"q_floor":rj(qfloor),"q_floor_source":"V5_EFFECTIVE",
  "effective_floor_record_sha256":floor_ids,"taylor_order":2,"gamma_lemma":"SOS_GAMMA_IN_0_1"}
 if c1dig is not None:detail.update({"c1_floor_record_sha256":c1dig,"c1_q_floor_source":c1rec["q_floor_source"]})
 return density*out,detail

def safe_eff_sqrt(route,adapter,arb,fmpq,x,structural,w,site,region,scope,cell,
                  nonnegative=False):
 floor,dig=effective(site,structural,x,w,region,scope,cell)
 if nonnegative and natural_lower(x,w+".choice")[0] is None:
  out=route._safe_nonnegative_sqrt(adapter,arb,fmpq,x,w+".fallback")
 else:out=route._safe_positive_sqrt(adapter,arb,fmpq,x,floor,w+".effective")
 return out,dig,floor

def duffy_eval(quantity,kernel,adapter,acb,arb,fmpq,cell,u0,u1,s0,s1,eps):
 route=base.route;policy=route.policy;_STATS["duffy_calls"]+=1
 corner=cell.a0==0;_STATS["duffy_corner_calls" if corner else "duffy_noncorner_calls"]+=1
 r=route._r_ball(arb,fmpq,u0,u1);lam=route._lambda_ball(arb,fmpq,s0,s1)
 x=route._arb_interval(arb,fmpq,cell.a0,cell.a1);yd=route._arb_interval(arb,fmpq,cell.b0,cell.b1)
 epsa=route._arb_exact(arb,fmpq,eps);one=arb(1);ids=[]
 if cell.region=="T1":c=epsa*x;phi=epsa*x*yd;Ahat=(lam*lam-one)/(one+yd*yd)
 elif cell.region=="T2":phi=epsa*x;c=epsa*x*yd;Ahat=(lam*lam-one)*yd*yd/(one+yd*yd)
 else:raise ValueError("Duffy region")
 S2=one-c*c;S,Sdig,Sfloor=safe_eff_sqrt(route,adapter,arb,fmpq,S2,Fraction(0),"Duffy.S2","DUFFY_S2",cell.region,"box",cell,True);ids.append(Sdig)
 U=S*phi.cos();A=(lam*lam-one)*c*c;B=one-U*U;W=one-r*U;q=W*W+A+r*r*B
 w2=lam*lam*S2+c*c;w,Wdig,wfloor=safe_eff_sqrt(route,adapter,arb,fmpq,w2,Fraction(1),"Duffy.w2","DUFFY_W2",cell.region,"box",cell);ids.append(Wdig);L=lam/w
 bhlo=route._bhat_lower(eps);Bhat=route._arb_interval(arb,fmpq,bhlo,Fraction(1));M=U*Ahat+r*Bhat
 lamlo=base.model.LAMBDA_PLUS+s0;rlo=1-u1
 if cell.region=="T1":ahatlo=(lamlo*lamlo-1)/(1+cell.b1*cell.b1)
 else:ahatlo=(lamlo*lamlo-1)*cell.b0*cell.b0/(1+cell.b0*cell.b0)
 rblo=rlo*rlo*bhlo;rho2hi=eps*eps*cell.a1*cell.a1*(1+cell.b1*cell.b1)
 base.model.need(rho2hi>0,"V5_DUFFY_RHO2_HI_NONPOSITIVE")
 dropped=[]
 try:what=u0*u0/rho2hi
 except Exception as e:what=Fraction(0);dropped.append("WHAT:"+type(e).__name__);_STATS["duffy_what_component_dropped"]+=1
 zden=clamp0(ahatlo)+clamp0(rblo)+clamp0(what);base.model.need(zden>0,"V5_DUFFY_Z_LO_NONPOSITIVE")
 zhi=arb(1)/route._arb_exact(arb,fmpq,zden).sqrt();route._canonical(adapter,zhi,"V5.Duffy.z_hi")
 g2=one+yd*yd;gy,Gdig,gfloor=safe_eff_sqrt(route,adapter,arb,fmpq,g2,Fraction(1),"Duffy.g2","DUFFY_G2",cell.region,"box",cell);ids.append(Gdig)
 rho=epsa*x*gy;qhi_rec=None
 if corner:
  yh=arb(0).union(arb(1));v=arb(-1).union(arb(1));z=arb(0).union(zhi);gamma=arb(0).union(arb(1))
 else:
  rho2lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0);qlo=rho2lo*zden
  _,invsqrtq,qhi=route._positive_inverse_factors(adapter,arb,fmpq,q,qlo,f"{cell.region}:{cell.path}:V5.Duffy")
  qhi_rec=rj(qhi);yh=(W*invsqrtq).max(arb(0)).min(arb(1));v=(r-U)*invsqrtq
  z=(rho*invsqrtq).max(arb(0)).min(zhi);gamma=(L*yh).max(arb(0)).min(arb(1))
 h,h1,h2,gsplits=route._angle_union(kernel,adapter,acb,arb,gamma,corner,quantity=="H_U")
 if gsplits:_STATS["gamma_fallback_corner" if corner else "gamma_fallback_noncorner"]+=1
 if quantity=="F":transformed=epsa*rho*(-U*h-L*h1*M*yh*z*z)/gy
 else:
  assert h2 is not None
  J=L*(arb(2)*U*h1*M*z**3+L*h2*M*M*yh*z**5+h1*(-Bhat*yh*rho*z**2+arb(3)*M*yh*v*z**3))
  transformed=-epsa*J/gy
 area=route._arb_exact(arb,fmpq,(cell.a1-cell.a0)*(cell.b1-cell.b0));contribution=transformed*area
 route._canonical(adapter,contribution,"V5 Duffy contribution")
 rho2lo=eps*eps*cell.a0*cell.a0*(1+cell.b0*cell.b0)
 zrec={"chart":cell.region,"path":cell.path,"corner":corner,"Ahat_lo":rj(ahatlo),
  "r_lo2_Bhat_lo":rj(rblo),"u0_2_over_rho2_hi":rj(what),"rho2_lo":rj(rho2lo),
  "rho2_hi":rj(rho2hi),"Z_lo":rj(zden),"q_lo":rj(rho2lo*zden),
  "component_dropped":dropped,"effective_floor_record_sha256":ids,
  "S2_eff":rj(Sfloor),"w2_eff":rj(wfloor),"g2_eff":rj(gfloor),
  "local_geometry":["S","U","W","B","q"]}
 zdig=intern(zrec)
 detail={"Z_DEN_LO":rj(zden),"v5_z_record_sha256":zdig,"gamma_policy":policy.GAMMA_POLICY_ID,
  "gamma_subdivisions":gsplits,"gamma_fallback_used":bool(gsplits),"gamma_fallback_class":"corner" if corner else "non_corner",
  "sqrt_policy":"V5_EFFECTIVE_FLOOR","bounded_extensions":{"y_h":"[0,1]" if corner else "CHILD_DIRECT","v":"[-1,1]" if corner else "CHILD_DIRECT","z":"[0,1/sqrt(Z_lo)]" if corner else "CHILD_DIRECT"},
  "duffy_id":policy.DUFFY_ID,"measure_identity":policy.MEASURE_ID,"triangle_substitution":cell.region}
 if not corner:detail.update({"denominator_policy":policy.DENOMINATOR_POLICY_ID,"q_hi":qhi_rec})
 return contribution,detail

def eval_cell(quantity,cell,u0,u1,s0,s1,eps):
 if cell.region in ("T1","T2"):return duffy_eval(quantity,base.kernel,base.adapter,base.acb,base.arb,base.fmpq,cell,u0,u1,s0,s1,eps)
 return base.taylor_cell(quantity,cell,u0,u1,s0,s1,eps)

def main()->int:
 if hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()!=SPEC_SHA256:raise RuntimeError("V5_SPEC_SHA256_MISMATCH")
 if hashlib.sha256(Path(v4.__file__).read_bytes()).hexdigest()!=V4_SHA256:raise RuntimeError("V4_PROTOTYPE_SHA256_MISMATCH")
 if hashlib.sha256(Path(v4.v3.__file__).read_bytes()).hexdigest()!=V3_SHA256:raise RuntimeError("V3_PROTOTYPE_SHA256_MISMATCH")
 v4.geometry_jet=geometry_jet;base.eval_cell=eval_cell
 v4.v3.v2.BUDGET["max_depth"]=16
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):rc=v4.main()
 path=Path(os.environ.get("BLOCAL_V22_FULL_RECORD",v4.v3.DEFAULT_RECORD));record=json.loads(path.read_bytes())
 record["effective_floors_v5"]={"prototype_id":PROTOTYPE_ID,"spec_path":SPEC_PATH.name,"spec_sha256":SPEC_SHA256,
  "v4_sha256":V4_SHA256,"v3_sha256":V3_SHA256,"registry_count":len(_REGISTRY),
  "registry":{k:_REGISTRY[k] for k in sorted(_REGISTRY)},"counters":_STATS,
  "call_sites":["ORDINARY_Q","ORDINARY_W2","ORDINARY_S2","DUFFY_W2","DUFFY_G2","DUFFY_S2"],
  "probe_budget_override":{"max_depth":16,"committed_contract_budget":False},"certificate_evidence":False}
 payload=canonical(record)+b"\n";path.write_bytes(payload);results=record.get("results",[])
 summary={"schema":"BLOCAL_V22_SECTION_6_5_SUMMARY_V5","full_record_path":str(path),"full_record_bytes":len(payload),
  "full_record_sha256":hashlib.sha256(payload).hexdigest(),"prototype_id":PROTOTYPE_ID,
  "prototype_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"spec_sha256":SPEC_SHA256,
  "git_source_head":record.get("git_source_head"),"declared_budgets":record.get("declared_budgets"),
  "v5_registry_count":len(_REGISTRY),"v5_counters":_STATS,"all_six_conditions_pass":record.get("all_six_conditions_pass"),
  "method_selection_gate":record.get("method_selection_gate"),"total_elapsed_seconds":record.get("total_elapsed_seconds"),
  "phases":[v4.v3.phase_summary(x) for x in results],"certificate_evidence":False}
 print(json.dumps(summary,sort_keys=True,separators=(",",":")),flush=True);return rc

if __name__=="__main__":raise SystemExit(main())
