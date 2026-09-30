#!/usr/bin/env python3
"""D-OB P2 SPEC V3 candidate comparison full driver draft.
DIAGNOSTIC / NOT_EVIDENCE. No formal RUN_DIR. Check-only is the audit path;
execution is blocked unless the frozen addendum token is supplied explicitly.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,os,socket,sys,time
from fractions import Fraction as Q
from pathlib import Path

LABEL="DIAGNOSTIC / NOT_EVIDENCE"
BASE_SHA="dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b"
DERIVED_SHA="b7ad3fbf7ca41539b43959fd3645a2e34d397decb175cf7511daa127cb6297d2"
C1_SHA="6ad29461e42c265ce136e8df114400072e939335d72e2033b79741461e93fa90"
C2_SHA="ea166df49d8d0486fe836088fdbc13acbd0154811c882ae98b2a3f92275a8b9c"
C3_SHA="361db4a7c5fbe3bc6c8afc335282af8b26a1bf653dd5edf1dde56d08e634b4e0"
C4_SHA="85d6146ac1b92d50fac85a6560b2679f7aa74fa89afd904f5d3838309ccca360"
C5_SHA="0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8"
C4J_SHA="0a1ac7708a462868597bc94de38899bb381dd226514ff693c187dc52927d52ee"
R0,T0,L0=Q(7,8),Q(7,8),Q(2,5); WR,WT,WL=Q(1,128),Q(1,128),Q(13,3200)
C4_R=[Q(1,100),Q(7,500),Q(9,500),Q(11,500),Q(3,100),Q(3,50),Q(1,10)]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit("INVALID "+s)
def q(s): return Q(str(s).strip())
def centre(key):
 i,j,k=key; return R0+WR*Q(2*i+1,2),T0+WT*Q(2*j+1,2),L0+WL*Q(2*k+1,2)
def rho_z(r,t,l): return r*(1-t*t)/(1+t*t),l*r*2*t/(1+t*t)
def g4_770(r,t,l): return Q(7,8)<=r<=1 and Q(7,8)<=t<=1 and Q(2,5)<=l<=Q(93,200)
def rows(path):
 with open(path,newline="",encoding="utf-8") as f: return list(csv.DictReader((x for x in f if not x.startswith("#")),delimiter="\t"))

def load_c1(path):
 if sha(path)!=C1_SHA: die("C1_PIN")
 x=rows(path)
 if len(x)!=192: die(f"C1_COUNT_{len(x)}")
 out=[]
 for a in x:
  key=(int(a["i_r"]),int(a["i_t"]),int(a["i_lambda"])); r,t,l=centre(key)
  if not g4_770(r,t,l): die(f"C1_G4_{key}")
  out.append(("C1",key,r,t,l,a))
 return out

def load_c2(path):
 if sha(path)!=C2_SHA: die("C2_PIN")
 out=[]; counts={"A":0,"N":0}
 for raw in Path(path).read_text().splitlines():
  f=raw.split("\t"); cls=f[0]; key=tuple(map(int,f[1].strip("()").split(",")))
  if cls not in counts: die(f"C2_CLASS_{cls}")
  r,t,l=centre(key); rho,z=rho_z(r,t,l)
  if not g4_770(r,t,l): die(f"C2_G4_{key}")
  # TSV float rho/z/lambda are reference-only; compare at loose serialization tolerance, never ingest as exact input.
  refs={v.split("=")[0]:float(v.split("=")[1]) for v in f[2:5]}
  if abs(refs["rho"]-float(rho))>5e-7 or abs(refs["z"]-float(z))>5e-7 or abs(refs["lam"]-float(l))>5e-7: die(f"C2_FLOAT_REF_{key}")
  counts[cls]+=1; out.append(("C2",key,r,t,l,{"class":cls,"source":raw}))
 if len(out)!=9 or counts!={"A":2,"N":7}: die(f"C2_COMPOSITION_{len(out)}_{counts}")
 return out

def load_c3(path):
 if sha(path)!=C3_SHA: die("C3_PIN")
 x=rows(path)
 if len(x)!=44 or any(a.get("label")!="POSITIVE" for a in x): die("C3_P0A")
 return x

def load_c4(path):
 if sha(path)!=C4_SHA: die("C4_PIN")
 x=rows(path)
 got=[q(a["r"]) for a in x]
 if len(x)!=7 or got!=C4_R: die(f"C4_TARGETS_{got}")
 for a in x:
  if q(a["tau"])!=Q(1,64) or q(a["lam"])!=Q(251,400): die("C4_G4")
 return x

def inside(x,lo,hi,global_hi): return lo<=x<=hi if hi==global_hi else lo<=x<hi
def load_c5(path,c1,c4):
 if sha(path)!=C5_SHA: die("C5_PIN")
 m=rows(path); parsed=[]
 for a in m:
  parsed.append((a,(q(a["r0"]),q(a["r1"]),q(a["t0"]),q(a["t1"]),q(a["l0"]),q(a["l1"]))))
 targets=[("C1",r,t,l,"7,7,0",12) for _,_,r,t,l,_ in c1]+[("C4",q(a["r"]),q(a["tau"]),q(a["lam"]),"0,0,3",None) for a in c4]
 out=[]
 for src,r,t,l,ib,required_depth in targets:
  hit=[]
  for a,b in parsed:
   if a["box"]!=ib or a["decision"]=="split" or (required_depth is not None and int(a["depth"])!=required_depth): continue
   r0,r1,t0,t1,l0,l1=b
   if inside(r,r0,r1,Q(1)) and inside(t,t0,t1,Q(1)) and inside(l,l0,l1,Q(33,50)): hit.append((a,b))
  if len(hit)!=1: die(f"C5_EXACTLY_ONE_{src}_{r}_{t}_{l}_{len(hit)}")
  out.append((src,r,t,l,hit[0]))
 return out

def load_module(path,name,expected):
 if sha(path)!=expected: die(f"PRODUCER_PIN_{name}")
 sp=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(sp); sys.modules[name]=m; sp.loader.exec_module(m); return m

def type_precheck(m):
 # A2-type precheck: exact rational override must be producer's Fraction type; resource globals remain ints.
 if type(m.RHO0) is not type(Q(1,8)) or not all(type(getattr(m,k)) is int for k in ("MAX_CELL_COUNT","MAX_CELL_DEPTH","MAX_BOX_DEPTH")): die("A2_TYPE_PRECHECK")
 return "A2_TYPE_PRECHECK_OK"

EXPECTED_COLUMNS=[
 "candidate_id","candidate_status","code_config_identity","used_producer_sha256","set_id","initial_box_index","r","t","lambda","c5_box_bounds","accepted","unresolved","cut_cells","regular_cells","L","B_cut","independent_J","c5_center_J_flag","upper_sum","enclosure_width","J_minus_L","SumUpper_minus_J","cell_count","max_cell_depth","max_box_depth","runtime_cpu","resource_settings","failure_reason","missing_reason"]

def schema_precheck():
 if len(EXPECTED_COLUMNS)!=len(set(EXPECTED_COLUMNS)): die("SCHEMA_DUPLICATE")
 required={"candidate_id","used_producer_sha256","L","B_cut","independent_J","upper_sum","enclosure_width","J_minus_L","SumUpper_minus_J","missing_reason"}
 if not required<=set(EXPECTED_COLUMNS): die("SCHEMA_MISSING")
 return "SECTION9_SCHEMA_OK"

def arb_lo(x): return float(x.lower())
def arb_hi(x): return float(x.upper())
def load_c4j(path):
 if sha(path)!=C4J_SHA: die("C4J_PIN")
 x=rows(path)
 if len(x)!=7: die("C4J_COUNT")
 return {Q(a["r"]):float(a["J_h1e5"]) for a in x}
def load_cfg(path):
 sp=importlib.util.spec_from_file_location("candidate_cfg",path); m=importlib.util.module_from_spec(sp); sys.modules[sp.name]=m; sp.loader.exec_module(m); m.validate_one_change(); return m
def configure(m,c):
 m.MAX_CELL_COUNT=c.max_cell_count; m.MAX_CELL_DEPTH=c.max_cell_depth; m.MAX_BOX_DEPTH=c.max_box_depth; m.RHO0=c.rho0

def run_one(m,c,cid,set_id,initial,r,t,l,B,indJ,c5flag):
 t0=time.process_time(); cells,data=m.refine_cells(B); cpu=time.process_time()-t0
 current=[x[0] for x in data["regular"]]+list(data["cut"])
 L=arb_lo(data["L"]); bcut=arb_hi(data["Bcut"])
 upper=sum(arb_hi(cell.area()*kval) for cell,kval,_ in data["regular"])+bcut
 width=upper-L; miss=[]
 if indJ is None: miss.append("independent_J_unavailable_for_frozen_set")
 if set_id!="C5": miss.append("box_depth_not_evaluated_outside_C5")
 return {"candidate_id":cid,"candidate_status":"DIAGNOSTIC","code_config_identity":"frozen-v2-config",
  "used_producer_sha256":sha(m.__file__),"set_id":set_id,"initial_box_index":initial,"r":str(r),"t":str(t),"lambda":str(l),
  "c5_box_bounds":"" if set_id!="C5" else "|".join(map(str,(B.r0,B.r1,B.t0,B.t1,B.l0,B.l1))),
  "accepted":bool(data["accepted"]),"unresolved":not bool(data["accepted"]),"cut_cells":len(data["cut"]),"regular_cells":len(data["regular"]),
  "L":L,"B_cut":bcut,"independent_J":indJ,"c5_center_J_flag":c5flag,"upper_sum":upper,"enclosure_width":width,
  "J_minus_L":None if indJ is None else indJ-L,"SumUpper_minus_J":None if indJ is None else upper-indJ,"cell_count":len(current),
  "max_cell_depth":max((x.depth for x in current),default=0),"max_box_depth":B.depth if set_id=="C5" else None,"runtime_cpu":cpu,
  "resource_settings":json.dumps({"MAX_CELL_COUNT":c.max_cell_count,"MAX_CELL_DEPTH":c.max_cell_depth,"MAX_BOX_DEPTH":c.max_box_depth,"RHO0":str(c.rho0),"regular":f"{c.regular_num}/{c.regular_den}"},sort_keys=True),
  "failure_reason":"" if data["accepted"] else "refine_cells_not_accepted","missing_reason":";".join(miss)}

def contains_point(B,r,t,l):
 return inside(r,B.r0,B.r1,Q(1)) and inside(t,B.t0,B.t1,Q(1)) and inside(l,B.l0,B.l1,Q(33,50))
def walk_c5_target(m,c,cid,initial,r,t,l,B):
 """Run the producer box-tree decision from the frozen C5 terminal box.
 C0 at depth 12 is therefore terminal exactly as frozen; C-box-depth=13 can split once.
 Only the unique descendant containing the frozen target supplies point metrics; achieved
 box depth is recorded, not the configured ceiling.
 """
 leaves=[]
 def walk(X):
  col=X.column()
  if col=="straddle":
   if X.depth>=c.max_box_depth: leaves.append((X,None,None,"unresolved_straddle")); return
   for ch in X.split(): walk(ch)
   return
  cells,data=m.refine_cells(X)
  if cells is not None: leaves.append((X,cells,data,"accepted")); return
  if X.depth>=c.max_box_depth: leaves.append((X,cells,data,"unresolved")); return
  for ch in X.split(): walk(ch)
 walk(B)
 hit=[z for z in leaves if contains_point(z[0],r,t,l)]
 if len(hit)!=1: die(f"C5_WALK_EXACTLY_ONE_{cid}_{r}_{t}_{l}_{len(hit)}")
 X,cells,data,state=hit[0]
 if data is None:
  return {"candidate_id":cid,"candidate_status":"DIAGNOSTIC","code_config_identity":"frozen-v2-config","used_producer_sha256":sha(m.__file__),"set_id":"C5","initial_box_index":initial,"r":str(r),"t":str(t),"lambda":str(l),"c5_box_bounds":"|".join(map(str,(X.r0,X.r1,X.t0,X.t1,X.l0,X.l1))),"accepted":False,"unresolved":True,"cut_cells":None,"regular_cells":None,"L":None,"B_cut":None,"independent_J":None,"c5_center_J_flag":"true_reference_only","upper_sum":None,"enclosure_width":None,"J_minus_L":None,"SumUpper_minus_J":None,"cell_count":None,"max_cell_depth":None,"max_box_depth":X.depth,"runtime_cpu":None,"resource_settings":json.dumps({"MAX_CELL_COUNT":c.max_cell_count,"MAX_CELL_DEPTH":c.max_cell_depth,"MAX_BOX_DEPTH":c.max_box_depth,"RHO0":str(c.rho0),"regular":f"{c.regular_num}/{c.regular_den}"},sort_keys=True),"failure_reason":state,"missing_reason":"independent_J_unavailable_for_frozen_set;bounds_unavailable_for_straddle"}
 return run_one(m,c,cid,"C5",initial,r,t,l,X,None,"true_reference_only")

def execute_set(a,cfg,cid,c1,c2,c3,c4,c5,c4j):
 c=cfg.CONFIGS[cid]; mpath=a.derived_producer if cid=="C-regular" else a.base_producer; expected=DERIVED_SHA if cid=="C-regular" else BASE_SHA
 m=load_module(mpath,"run_"+cid.replace("-","_"),expected); type_precheck(m); configure(m,c)
 todo=[]
 if a.set_id=="C1":
  for _,_,r,t,l,raw in c1: todo.append(("C1","7,7,0",r,t,l,m.PBox(r,r,t,t,l,l,12),None,"false"))
 elif a.set_id=="C2":
  for _,_,r,t,l,raw in c2:
   hb=float([z.split("=")[1] for z in raw["source"].split("\t") if z.startswith("H_B=")][0]); todo.append(("C2","7,7,0",r,t,l,m.PBox(r,r,t,t,l,l,12),2*math.pi*float(l)*hb,"false"))
 elif a.set_id=="C3":
  for raw in c3:
   r,t,l=q(raw["r"]),q(raw["t"]),q(raw["lambda"]); todo.append(("C3","7,7,0",r,t,l,m.PBox(r,r,t,t,l,l,12),float(raw["J_B_standard"]),"false"))
 elif a.set_id=="C4":
  for raw in c4:
   r,t,l=q(raw["r"]),q(raw["tau"]),q(raw["lam"]); todo.append(("C4","0,0,3",r,t,l,m.PBox(r,r,t,t,l,l,12),c4j[r],"false"))
 elif a.set_id=="C5":
  out=[]
  for src,r,t,l,hit in c5:
   raw,b=hit; out.append(walk_c5_target(m,c,cid,raw["box"],r,t,l,m.PBox(*b,int(raw["depth"]))))
 else: die("SET_ID")
 if a.set_id!="C5":
  out=[]
  for z in todo: out.append(run_one(m,c,cid,*z))
 Path(a.out).parent.mkdir(parents=True,exist_ok=True)
 with open(a.out,"w",newline="") as f:
  f.write("# DIAGNOSTIC / NOT_EVIDENCE\n"); w=csv.DictWriter(f,fieldnames=EXPECTED_COLUMNS,delimiter="\t"); w.writeheader(); w.writerows(out)
 print(f"EXECUTION_COMPLETE candidate={cid} set={a.set_id} rows={len(out)} output={a.out}")
 return 0

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--config",required=True); ap.add_argument("--base-producer",required=True); ap.add_argument("--derived-producer",required=True)
 for n in ("c1","c2","c3","c4","c4j","c5"): ap.add_argument("--"+n,required=True)
 ap.add_argument("--check-only",action="store_true"); ap.add_argument("--execute-token"); ap.add_argument("--candidate"); ap.add_argument("--set-id",choices=["C1","C2","C3","C4","C5"]); ap.add_argument("--out")
 a=ap.parse_args(); cfg=load_cfg(a.config); c1=load_c1(a.c1); c2=load_c2(a.c2); c3=load_c3(a.c3); c4=load_c4(a.c4); c4j=load_c4j(a.c4j); c5=load_c5(a.c5,c1,c4)
 b=load_module(a.base_producer,"dobp2_base",BASE_SHA); d=load_module(a.derived_producer,"dobp2_creg",DERIVED_SHA)
 checks=[type_precheck(b),type_precheck(d),schema_precheck()]
 report={"label":LABEL,"host":socket.gethostname(),"counts":{"C1":len(c1),"C2":len(c2),"C3":len(c3),"C4":len(c4),"C5":len(c5)},"C2_classes":{"A":sum(x[5]["class"]=="A" for x in c2),"N":sum(x[5]["class"]=="N" for x in c2)},"producer_sha":{"base":sha(a.base_producer),"C-regular":sha(a.derived_producer)},"checks":checks,"baseline_row":"C0 is an explicit executable candidate","alias":"D-rho-1-8 -> C0"}
 print(json.dumps(report,sort_keys=True))
 if a.check_only: print("CHECK_ONLY_OK"); return 0
 if a.execute_token!="AUDITED_ADDENDUM_REQUIRED": die("EXECUTION_BLOCKED")
 if not a.candidate or not a.set_id or not a.out: die("EXECUTION_ARGS")
 if a.candidate not in cfg.CONFIGS: die("CANDIDATE")
 return execute_set(a,cfg,a.candidate,c1,c2,c3,c4,c5,c4j)
if __name__=="__main__": raise SystemExit(main())
