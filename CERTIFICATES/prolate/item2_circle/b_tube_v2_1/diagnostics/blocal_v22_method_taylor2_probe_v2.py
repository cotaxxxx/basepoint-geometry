#!/usr/bin/env python3
"""B-LOCAL v2.2 Taylor2 method-selection diagnostic, revision 2.

Only V1 diagnostic binding/record mechanics change: gamma is deterministically
bisected until h..h'''' are finite, exact adaptive cuts are recorded, and every
fail-closed route preserves evaluation/subdivision counters.  Taylor2 formulas,
charts, Duffy route, and the main 24k/depth14/16k/900s budget are unchanged.
Design evidence only; never certificate evidence.
"""
from __future__ import annotations
import hashlib,json,time
from fractions import Fraction
from pathlib import Path
from typing import Any,Callable
import blocal_v22_method_taylor2_probe as base

PROTOTYPE_ID="BLOCAL_V22_TAYLOR2_CHARTED_METHOD_SELECTION_V2_ADAPTIVE_GAMMA"
BASE_SHA256="7d6b75aa420de3844e0ad9c12e0a42655ebc8d644a83825dae2d0d861d94e644"
_BASE_FILE=base.__file__
_ORIG_PREFLIGHT=base.preflight
_ORIG_JSTART=base.jstart
BUDGET=dict(base.BUDGET)
BUDGET.update({"max_gamma_bin_depth":8,"max_gamma_bin_evaluations_per_enclosure":1000000})
_TRACE:dict[str,Any]|None=None
_LAST_COUNTS:dict[str,Any]|None=None
_HISTORY:list[dict[str,Any]]=[]

class Failure(base.DiagnosticFailure):
 def __init__(self,reason:str,counts:dict[str,Any]):super().__init__(reason);self.counts=counts

def rj(q:Fraction):return base.model.rational_json(q)
def qs(q:Fraction):return f"{q.numerator}/{q.denominator}"
def new_trace():return {"cell_evaluation_attempts":0,"cell_evaluations":0,"region_evaluations":{k:0 for k in base.ORDER},"spatial_split_count":0,"gamma_angle_calls":0,"gamma_bin_evaluations":0,"gamma_bin_split_count":0,"gamma_adaptive_calls":0,"gamma_max_bin_depth_used":0,"gamma_partition_counts":{},"gamma_terminal_failures":0,"last_gamma_failure":None,"last_cell":None}
def gamma_records(t):
 out=[]
 for _,x in sorted(t["gamma_partition_counts"].items()):
  out.append({"initial_interval":{"lo":rj(x["lo"]),"hi":rj(x["hi"])},"cuts":[rj(y) for y in x["cuts"]],"bin_count":len(x["cuts"])-1,"max_bin_depth":x["max_depth"],"use_count":x["count"]})
 return out
def snap(t,active=None,reason=None,started=None,quantity=None,mode=None):
 depths=[] if active is None else [x[0].depth for x in active.values()]
 return {"quantity":quantity,"mode":mode,"cell_evaluation_attempts":t["cell_evaluation_attempts"],"cell_evaluations":t["cell_evaluations"],"region_evaluations":dict(t["region_evaluations"]),"active_leaves":None if active is None else len(active),"max_spatial_depth_used":max(depths) if depths else 0,"spatial_split_count":t["spatial_split_count"],"gamma_angle_calls":t["gamma_angle_calls"],"gamma_bin_evaluations":t["gamma_bin_evaluations"],"gamma_bin_split_count":t["gamma_bin_split_count"],"gamma_adaptive_calls":t["gamma_adaptive_calls"],"gamma_max_bin_depth_used":t["gamma_max_bin_depth_used"],"gamma_partition_records":gamma_records(t),"gamma_terminal_failures":t["gamma_terminal_failures"],"last_gamma_failure":t["last_gamma_failure"],"last_cell":t["last_cell"],"complete_closed_cover":False,"failure_reason":reason,"elapsed_seconds":None if started is None else f"{time.perf_counter()-started:.6f}","direct_pinned_integrator_called":False}

def angle4_union(g,w):
 t=_TRACE;gb=base.clip_gamma(g,w+".clip");lo,hi=base.fracs(gb,w+".clip")
 if t is not None:t["gamma_angle_calls"]+=1
 leaves=[]
 def rec(a,b,d,path):
  if t is not None:
   if t["gamma_bin_evaluations"]>=BUDGET["max_gamma_bin_evaluations_per_enclosure"]:raise Failure("GAMMA_BIN_EVALUATION_BUDGET",snap(t))
   t["gamma_bin_evaluations"]+=1;t["gamma_max_bin_depth_used"]=max(t["gamma_max_bin_depth_used"],d)
  try:leaves.append((a,b,d,base.angle4_one(base.iv(a,b),w+".abin"+path)));return
  except (base.route.SplitRequired,ValueError,ArithmeticError) as e:
   if d>=BUDGET["max_gamma_bin_depth"] or a==b:
    if t is not None:t["gamma_terminal_failures"]+=1;t["last_gamma_failure"]={"interval":{"lo":rj(a),"hi":rj(b)},"depth":d,"where":w,"reason":f"{type(e).__name__}:{e}"}
    raise base.route.SplitRequired(f"ANGLE4_ADAPTIVE_BIN_DEPTH:{w}:{qs(a)}:{qs(b)}:{type(e).__name__}:{e}") from e
   m=(a+b)/2
   if t is not None:t["gamma_bin_split_count"]+=1
   rec(a,m,d+1,path+"0");rec(m,b,d+1,path+"1")
 rec(lo,hi,0,"R");leaves.sort(key=lambda x:(x[0],x[1]));cuts=[leaves[0][0]]+[x[1] for x in leaves]
 if t is not None and len(leaves)>1:
  t["gamma_adaptive_calls"]+=1;k=json.dumps([qs(lo),qs(hi),[qs(x) for x in cuts]],separators=(",",":"));z=t["gamma_partition_counts"].get(k)
  if z is None:t["gamma_partition_counts"][k]={"lo":lo,"hi":hi,"cuts":cuts,"max_depth":max(x[2] for x in leaves),"count":1}
  else:z["count"]+=1;z["max_depth"]=max(z["max_depth"],max(x[2] for x in leaves))
 out=[None]*5
 for *_,vals in leaves:
  for i,v in enumerate(vals):out[i]=v if out[i] is None else out[i].union(v)
 for i,v in enumerate(out):base.can(v,w+f".h{i}.adaptive_hull")
 return tuple(out)

def enclose(quantity,u0,u1,s0,s1,mode,run_start,accept:Callable[[dict[str,Any]],bool]|None=None):
 global _TRACE,_LAST_COUNTS
 started=time.perf_counter();eps=base.model.fraction_from_dyadic(base.CONFIG["geometry"]["eps"]);active={};heap=[];SL=Fraction(0);SH=Fraction(0);t=new_trace();old=_TRACE;_TRACE=t
 def snapshot(reason=None):return snap(t,active,reason,started,quantity,mode)
 def fail(reason):
  global _LAST_COUNTS
  z=snapshot(reason);_LAST_COUNTS=z;_HISTORY.append(z);raise Failure(reason,z)
 def timed():
  if time.perf_counter()-run_start>BUDGET["max_total_wall_seconds"]:fail("TOTAL_WALL_TIME_BUDGET")
 def add(cell):
  nonlocal SL,SH
  timed();t["last_cell"]={"region":cell.region,"path":cell.path,"depth":cell.depth}
  if t["cell_evaluation_attempts"]>=BUDGET["max_cell_evaluations_per_enclosure"]:fail("CELL_EVALUATION_BUDGET")
  t["cell_evaluation_attempts"]+=1
  try:v,d=base.eval_cell(quantity,cell,u0,u1,s0,s1,eps)
  except Failure:raise
  except base.route.SplitRequired as e:
   if cell.depth>=BUDGET["max_depth"]:fail("DEPTH:"+cell.region+":"+cell.path+":"+e.reason)
   t["spatial_split_count"]+=1
   for ch in base.split_cell(cell):add(ch)
   return
  except Exception as e:fail("CELL_EXCEPTION:"+cell.region+":"+cell.path+":"+type(e).__name__+":"+str(e))
  t["cell_evaluations"]+=1;t["region_evaluations"][cell.region]+=1;ci=base.can(v,"child");lo,hi=base.model.interval_fractions(ci,"child");active[cell.path]=(cell,lo,hi,d);SL+=lo;SH+=hi
  if cell.depth<BUDGET["max_depth"]:
   import heapq;heapq.heappush(heap,(-(hi-lo),base.ORDER[cell.region],cell.path))
  if len(active)>BUDGET["max_active_cells"]:fail("ACTIVE_CELL_BUDGET")
 try:
  for r in base.roots():add(r)
  import heapq
  while True:
   timed();root=base.model.normalize_interval(base.model.outward_dyadic(SL,SH));sg=base.sign(root);ok=(mode=="POS" and sg=="POS") or (mode=="NEG" and sg=="NEG") or (mode=="NONZERO" and sg in ("POS","NEG")) or (mode=="CUSTOM" and accept is not None and accept(root))
   if ok:
    if not base.cover_ok(active):fail("INCOMPLETE_COVER")
    z=snapshot();z["complete_closed_cover"]=True;z["root_sign"]=sg;_LAST_COUNTS=z;_HISTORY.append(z);return root,z
   chosen=None
   while heap:
    _,_,p=heapq.heappop(heap)
    if p in active and active[p][0].depth<BUDGET["max_depth"]:chosen=active[p];break
   if chosen is None:fail("PREDICATE_UNRESOLVED_AT_DEPTH_LIMIT")
   cell,lo,hi,d=chosen;del active[cell.path];SL-=lo;SH-=hi;t["spatial_split_count"]+=1
   for ch in base.split_cell(cell,d):add(ch)
 finally:_TRACE=old

def phase(name,domain,pred,fn):
 global _HISTORY
 t=time.perf_counter();_HISTORY=[]
 try:enc,d=fn();z={"phase":name,"tested_domain":domain,"final_enclosure":enc,"strict_predicate":pred,"predicate_result":True,"evaluation_subdivision_counts":d,"enclosure_sequence":list(_HISTORY),"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":None,"certificate_evidence":False}
 except Failure as e:z={"phase":name,"tested_domain":domain,"final_enclosure":None,"strict_predicate":pred,"predicate_result":False,"evaluation_subdivision_counts":e.counts,"enclosure_sequence":list(_HISTORY),"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":f"{type(e).__name__}:{e}","certificate_evidence":False}
 except Exception as e:z={"phase":name,"tested_domain":domain,"final_enclosure":None,"strict_predicate":pred,"predicate_result":False,"evaluation_subdivision_counts":_LAST_COUNTS or {"unhandled_before_snapshot":True},"enclosure_sequence":list(_HISTORY),"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":f"{type(e).__name__}:{e}","certificate_evidence":False}
 return z

def jstart(lam,um,start,initial):
 global _HISTORY
 t=time.perf_counter();_HISTORY=[];path,c5=_ORIG_JSTART(lam,um,start,initial);seq=list(_HISTORY)
 if path is not None:path["evaluation_subdivision_counts"]={"outer_evaluations":path.get("outer_evaluations",0),"enclosure_sequence":seq};path["elapsed_seconds"]=path.get("elapsed_seconds") or f"{time.perf_counter()-t:.6f}"
 der=next((x for x in seq if x.get("quantity")=="H_U"),None)
 if c5 is None:c5={"phase":"J_START_DERIVATIVE_BRACKET","tested_domain":None,"final_enclosure":None,"strict_predicate":"0 notin F_r and sup(F_r)<0","predicate_result":False,"evaluation_subdivision_counts":der or {"not_reached":True,"enclosure_sequence":seq},"elapsed_seconds":f"{time.perf_counter()-t:.6f}","failure_reason":"NOT_REACHED_OR_NOT_CERTIFIED","certificate_evidence":False}
 else:c5["evaluation_subdivision_counts"]=der or c5.get("evaluation_subdivision_counts") or {"enclosure_sequence":seq};c5["elapsed_seconds"]=c5.get("elapsed_seconds") or (der or {}).get("elapsed_seconds") or f"{time.perf_counter()-t:.6f}"
 return path,c5

def preflight():
 global _TRACE
 out=dict(_ORIG_PREFLIGHT());base_bytes=Path(_BASE_FILE).read_bytes();base.model.need(hashlib.sha256(base_bytes).hexdigest()==BASE_SHA256,"V1 prototype dependency hash");t=new_trace();old=_TRACE;_TRACE=t
 try:
  vals=angle4_union(base.iv(Fraction(0),Fraction(1)),"preflight.gamma01")
  for i,v in enumerate(vals):base.can(v,f"preflight.gamma01.h{i}")
 finally:_TRACE=old
 out.update({"gamma_policy":"DETERMINISTIC_MIDPOINT_SPLIT_UNTIL_H0_H4_FINITE","gamma_max_bin_depth":BUDGET["max_gamma_bin_depth"],"adaptive_gamma_preflight":{"domain":base.model.interval_json(Fraction(0),Fraction(1)),"status":"PASS","counts":snap(t)},"prototype_dependency":{"prototype_id":base.PROTOTYPE_ID,"path":Path(_BASE_FILE).name,"bytes":len(base_bytes),"sha256":BASE_SHA256}});return out

def main():
 base.BUDGET=BUDGET;base.PROTOTYPE_ID=PROTOTYPE_ID;base.angle4_union=angle4_union;base.enclose=enclose;base.phase=phase;base.jstart=jstart;base.preflight=preflight;base.__file__=__file__
 return base.main()

if __name__=="__main__":raise SystemExit(main())