#!/usr/bin/env python3
"""B-LOCAL v2.2 Taylor2 method-selection diagnostic, revision 4.

C1-only structural q and per-cell S floors implementing the byte-pinned
C1_STRUCTURAL_FLOOR_SPEC_V1. All other charts, formulas, gamma adaptation,
budgets, and v3 bounded-record/artifact mechanics remain unchanged.
Design evidence only; never certificate evidence.
"""
from __future__ import annotations
import contextlib,hashlib,io,json,os
from fractions import Fraction
from pathlib import Path
from typing import Any
import blocal_v22_method_taylor2_probe_v3 as v3

PROTOTYPE_ID="BLOCAL_V22_TAYLOR2_METHOD_SELECTION_V4_C1_STRUCTURAL_FLOOR"
SPEC_PATH=Path(__file__).with_name("C1_STRUCTURAL_FLOOR_SPEC_V1.md")
SPEC_SHA256="8492755d298ace4c09f5118993eb2f2fa968d55ae5d04b81ff20c2c856fc90d3"
V3_SHA256="dcb09f614369ee10a49b9eecb71bd184cd0565dc23c79857347bfae762573824"
PI_LO=Fraction(333,106);PI_HI=Fraction(355,113);HALF=Fraction(1,2)
_REGISTRY:dict[str,dict[str,Any]]={}
_STATS={"C1_floor_calls":0,"W2_component_dropped":0,"RB_component_dropped":0}
base=v3.v2.base
_ORIG_GEOMETRY_JET=base.geometry_jet

def canonical(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def clamp0(x:Fraction)->Fraction:return max(Fraction(0),x)
def rj(x:Fraction):return base.model.rational_json(x)
def interval_bounds(x,w):return base.fracs(x,w)

def endpoint_ball(b:Fraction):
 return base.iv(PI_LO*b,PI_HI*b)

def c1_floor(cell,r,s0,eps):
 _STATS["C1_floor_calls"]+=1
 c0=eps+(HALF-eps)*cell.a0;c1=eps+(HALF-eps)*cell.a1
 lamlo=base.model.LAMBDA_PLUS+s0;A=(lamlo*lamlo-1)*c0*c0
 if A<=0:raise base.DiagnosticFailure("C1_A_LO_NONPOSITIVE")
 rlo,rhi=interval_bounds(r.v,"C1.r")
 dropped=[];W2=Fraction(0);RB=Fraction(0);u_max=None;r_endpoint=None
 try:
  _,chi=interval_bounds(endpoint_ball(cell.b0).cos(),"C1.cos_left")
  cmax=min(chi,Fraction(1));Slo=clamp0(1-c1*c1)
  u_max=cmax if cmax>=0 else Slo*cmax
  if u_max>=0:ruse=rhi;r_endpoint="r_hi"
  else:ruse=rlo;r_endpoint="r_lo"
  Wlo=1-ruse*u_max;W2=clamp0(Wlo)*clamp0(Wlo)
 except Exception as e:
  _STATS["W2_component_dropped"]+=1;dropped.append("W2_lo:"+type(e).__name__);W2=Fraction(0)
 try:
  sl,_=interval_bounds(endpoint_ball(cell.b0).sin(),"C1.sin_left")
  sr,_=interval_bounds(endpoint_ball(cell.b1).sin(),"C1.sin_right")
  sinmin=clamp0(min(sl,sr));straddle=cell.b0<HALF<cell.b1
  if straddle:cos2=Fraction(0)
  elif cell.b1<=HALF:
   m,_=interval_bounds(endpoint_ball(cell.b1).cos(),"C1.cos_right");cos2=clamp0(m)**2
  elif cell.b0>=HALF:
   _,m=interval_bounds(endpoint_ball(cell.b0).cos(),"C1.cos_left_negative");cos2=clamp0(-m)**2
  else:raise base.DiagnosticFailure("C1_B_HALF_CASE_INDETERMINATE")
  Blo=sinmin*sinmin+c0*c0*cos2;RB=rlo*rlo*clamp0(Blo)
 except Exception as e:
  _STATS["RB_component_dropped"]+=1;dropped.append("RB_lo:"+type(e).__name__);RB=Fraction(0)
 qfloor=clamp0(A)+clamp0(W2)+clamp0(RB)
 if qfloor<=0:raise base.DiagnosticFailure("C1_Q_FLOOR_NONPOSITIVE")
 S2=max(Fraction(3,4),1-c1*c1)
 if S2<Fraction(3,4):raise base.DiagnosticFailure("C1_S2_FLOOR_BELOW_THREE_QUARTERS")
 rec={"region":"C1","path":cell.path,"depth":cell.depth,
  "cell":{"a0":rj(cell.a0),"a1":rj(cell.a1),"b0":rj(cell.b0),"b1":rj(cell.b1)},
  "q_floor_source":"C1_A_W2_B" if not dropped else "C1_A_W2_B_COMPONENT_DROPPED",
  "component_dropped":dropped,"A_lo":rj(A),"W2_lo":rj(W2),"RB_lo":rj(RB),
  "U_max":None if u_max is None else rj(u_max),"r_endpoint":r_endpoint,
  "r_interval":{"lo":rj(rlo),"hi":rj(rhi)},
  "pi_half_straddle":cell.b0<HALF<cell.b1,"S2_floor":rj(S2),"q_floor":rj(qfloor)}
 dig=hashlib.sha256(canonical(rec)).hexdigest();prior=_REGISTRY.get(dig)
 if prior is not None and prior!=rec:raise RuntimeError("C1_FLOOR_RECORD_HASH_COLLISION")
 _REGISTRY[dig]=rec
 return qfloor,S2,dig,rec

def geometry_jet(region,a,b,r,lam,cell,u0,s0,eps,quantity,w):
 if region!="C1":return _ORIG_GEOMETRY_JET(region,a,b,r,lam,cell,u0,s0,eps,quantity,w)
 pi=base.arb.pi();ea=base.exact(eps);c=ea+base.exact(HALF-eps)*a;phi=pi*b
 qfloor,S2,digest,frec=c1_floor(cell,r,s0,eps)
 S=base.jsqrt(1-c*c,S2,w+".S");density=base.asj(base.arb(1),a.v)
 U=S*base.jcos(phi);A=(lam*lam-1)*c*c;B=1-U*U;W=1-r*U;q=W*W+A+r*r*B
 w2=lam*lam*S*S+c*c;L=lam*base.qpow(w2,Fraction(1),1,w+".w2")
 N=-U*A-r*B;Nr=U*U-1
 qm1=base.qpow(q,qfloor,1,w+".qm1");qm3=base.qpow(q,qfloor,3,w+".qm3");qm5=base.qpow(q,qfloor,5,w+".qm5")
 gamma=L*W*qm1;gr=L*N*qm3;grr=L*(Nr*q-3*N*(r-U))*qm5
 h=base.hcompose(gamma,0,w+".h");h1=base.hcompose(gamma,1,w+".h1")
 if quantity=="F":out=-U*h+W*h1*gr
 elif quantity=="H_U":
  h2=base.hcompose(gamma,2,w+".h2");out=-(-2*U*h1*gr+W*(h2*gr*gr+h1*grr))
 else:raise ValueError(quantity)
 return density*out,{"chart":"C1","q_floor":rj(qfloor),"q_floor_source":frec["q_floor_source"],
  "c1_floor_record_sha256":digest,"S2_floor":rj(S2),"taylor_order":2,
  "gamma_lemma":"SOS_GAMMA_IN_0_1"}

def main()->int:
 if hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()!=SPEC_SHA256:raise RuntimeError("C1_SPEC_SHA256_MISMATCH")
 if hashlib.sha256(Path(v3.__file__).read_bytes()).hexdigest()!=V3_SHA256:raise RuntimeError("V3_PROTOTYPE_SHA256_MISMATCH")
 base.geometry_jet=geometry_jet
 capture=io.StringIO()
 with contextlib.redirect_stdout(capture):rc=v3.main()
 path=Path(os.environ.get("BLOCAL_V22_FULL_RECORD",v3.DEFAULT_RECORD))
 record=json.loads(path.read_bytes())
 record["c1_structural_floor_v4"]={"prototype_id":PROTOTYPE_ID,"spec_path":SPEC_PATH.name,
  "spec_sha256":SPEC_SHA256,"v3_sha256":V3_SHA256,"registry_count":len(_REGISTRY),
  "registry":{k:_REGISTRY[k] for k in sorted(_REGISTRY)},"counters":_STATS,
  "applies_to":["C1"],"unchanged_charts":["TH","R2","T1","T2"],"certificate_evidence":False}
 payload=canonical(record)+b"\n";path.write_bytes(payload)
 results=record.get("results",[])
 summary={"schema":"BLOCAL_V22_SECTION_6_5_SUMMARY_V4","full_record_path":str(path),
  "full_record_bytes":len(payload),"full_record_sha256":hashlib.sha256(payload).hexdigest(),
  "prototype_id":PROTOTYPE_ID,"prototype_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  "spec_sha256":SPEC_SHA256,"git_source_head":record.get("git_source_head"),
  "declared_budgets":record.get("declared_budgets"),"c1_floor_registry_count":len(_REGISTRY),
  "c1_floor_counters":_STATS,"all_six_conditions_pass":record.get("all_six_conditions_pass"),
  "method_selection_gate":record.get("method_selection_gate"),"total_elapsed_seconds":record.get("total_elapsed_seconds"),
  "phases":[v3.phase_summary(x) for x in results],"certificate_evidence":False}
 print(json.dumps(summary,sort_keys=True,separators=(",",":")),flush=True)
 return rc

if __name__=="__main__":raise SystemExit(main())
