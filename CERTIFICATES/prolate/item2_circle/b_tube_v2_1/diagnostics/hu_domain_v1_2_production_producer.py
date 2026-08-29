#!/usr/bin/env python3
"""Cell-independent H_U producer for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

The released V1.2 policy supplies only stage_semantics/stages/cap/dps here.
The parent rectangle is reconstructed exactly from MONOTONE_TUBE_V1.1
Component-1 geometry; policy.parent is intentionally ignored.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sys
from fractions import Fraction
from pathlib import Path
from typing import Any
sys.dont_write_bytecode = True

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_GEOM = REL_DIR + "/hu_domain_v1_2_tube_geometry.py"
REL_RUNNER = REL_DIR + "/hu_domain_v1_2_production_producer.py"
REL_BT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
REL_V23 = REL_BT + "/dependencies/blocal_v23_source"
POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
GEOMETRY_MODULE_SHA256 = "9d2a8557d4761b9b30d05bc22c7923f117dba199a63e850c516700ff40097d6a"
KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"

def fail(code: str) -> None:
    raise SystemExit("STOP:" + code)
def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
def fstr(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"

class Box:
    def __init__(self,bid,r0,r1,l0,l1,g=0,parent=None):
        self.box_id,self.r_lo,self.r_hi,self.lambda_lo,self.lambda_hi,self.generation,self.parent_id=bid,r0,r1,l0,l1,g,parent
    def record(self):
        return {"box_id":self.box_id,"parent_id":self.parent_id,"generation":self.generation,
                "r_lo":fstr(self.r_lo),"r_hi":fstr(self.r_hi),
                "lambda_lo":fstr(self.lambda_lo),"lambda_hi":fstr(self.lambda_hi)}
def split_r(b):
    m=(b.r_lo+b.r_hi)/2
    return [Box(b.box_id+"/r0",b.r_lo,m,b.lambda_lo,b.lambda_hi,b.generation+1,b.box_id),
            Box(b.box_id+"/r1",m,b.r_hi,b.lambda_lo,b.lambda_hi,b.generation+1,b.box_id)]
def split_l(b,n,tag):
    w=(b.lambda_hi-b.lambda_lo)/n
    return [Box(f"{b.box_id}/{tag}{k}",b.r_lo,b.r_hi,b.lambda_lo+k*w,b.lambda_lo+(k+1)*w,b.generation+1,b.box_id) for k in range(n)]

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,required=True)
    ap.add_argument("--tube-geometry",type=Path,required=True)
    ap.add_argument("--box-id",required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ns=ap.parse_args()
    repo=ns.repo.resolve()
    if os.environ.get("PYTHONDONTWRITEBYTECODE")!="1" or not sys.dont_write_bytecode: fail("BYTECODE_SUPPRESSION")
    if platform.python_version()!="3.13.14": fail("PYTHON_VERSION")
    policy_path=repo/REL_POLICY; geom_path=repo/REL_GEOM; runner_path=repo/REL_RUNNER
    if sha(policy_path)!=POLICY_SHA256: fail("POLICY_SHA")
    if sha(geom_path)!=GEOMETRY_MODULE_SHA256: fail("GEOMETRY_MODULE_SHA")
    policy=json.loads(policy_path.read_text())
    if policy.get("contract_id")!="PRODUCTION_HU_DOMAIN_CONTRACT_V1_2": fail("POLICY_CONTRACT")
    if policy.get("dps")!=60 or policy.get("per_box_cap")!=24000: fail("POLICY_DPS_CAP")
    geom=json.loads(ns.tube_geometry.read_text())
    sys.path.insert(0,str(repo/REL_DIR))
    from hu_domain_v1_2_tube_geometry import derive_parent
    d=derive_parent(geom)
    parent=Box(ns.box_id,Fraction(d["r_lo"]),Fraction(d["r_hi"]),Fraction(d["lambda_lo"]),Fraction(d["lambda_hi"]))

    bt=repo/REL_BT; v23=repo/REL_V23
    sys.path.insert(0,str(v23)); sys.path.insert(1,str(bt))
    import flint
    from flint import acb,arb,fmpq,ctx
    import blocal_v22_model as model, blocal_arb_adapter as adapter, blocal_v23_boundary as route, calibration_runner
    if str(getattr(flint,"__version__",""))!="0.9.0" or str(getattr(flint,"__FLINT_VERSION__",""))!="3.6.0": fail("FLINT_TOOLCHAIN")
    ctx.dps=60
    raw_kernel,kernel_path=calibration_runner.load_production_kernel()
    if sha(kernel_path)!=KERNEL_SHA256: fail("KERNEL_SHA")
    bcfg=json.loads((v23/"config.blocal-v2.2-run.json").read_text())
    frag=json.loads((v23/"BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
    bcfg["route_policies"].update(frag["route_policies"])

    terminal={}; evaluated=[]; ledger=[]; total_eval=0; current=[]
    def evaluate(b):
        nonlocal total_eval
        u0=Fraction(1)-b.r_hi; u1=Fraction(1)-b.r_lo
        s0=b.lambda_lo-model.LAMBDA_PLUS; s1=b.lambda_hi-model.LAMBDA_PLUS
        rec=b.record()|{"status":"ABORT","required_sign":"POS","effective_evaluation_cap":24000,
                       "lo":None,"hi":None,"width":None,"evaluation_count":0,"proof_id":None,"abort_reason":None}
        try:
            iv,proof=route.base.enclose_hu(raw_kernel,adapter,acb,arb,fmpq,bcfg,u0,u1,s0,s1,
                                           required_sign="POS",accept=None,evaluation_cap=24000)
            lo,hi=model.interval_fractions(iv,b.box_id); ev=int(proof["evaluation_count"]); total_eval+=ev
            rec.update(status="PASS_POS" if lo>0 else "UNRESOLVED",lo=fstr(lo),hi=fstr(hi),width=fstr(hi-lo),
                       evaluation_count=ev,proof_id=proof.get("proof_id"),
                       complete_closed_cover=bool(proof.get("complete_closed_cover")),route_id=proof.get("route_id"))
            if not proof.get("complete_closed_cover"):
                rec["status"]="ABORT"; rec["abort_reason"]="INCOMPLETE_ANGULAR_COVER"
        except route.base.EnclosureFailure as exc:
            ev=int(exc.evaluations); total_eval+=ev; rec["evaluation_count"]=ev; rec["abort_reason"]=exc.reason
        return rec

    stages=policy["stages"]
    expected_ids=["S0_BASE","S1_R1","S2_R2","S3_R3","S4_R4","S5_R5","S6_R6",
                  "S7_L32","S8_R_POST_L32_1","S9_R_POST_L32_2","S10_L128"]
    if [s["stage_id"] for s in stages]!=expected_ids: fail("STAGE_LIST")
    for i,stage in enumerate(stages):
        parents=[parent] if i==0 else list(current)
        if i==0: children=[parent]
        elif stage["op"]=="R_BISECT": children=[c for b in parents for c in split_r(b)]
        elif stage["op"]=="LAMBDA_SUBDIVIDE":
            if stage.get("division")!=32: fail("L32")
            children=[c for b in parents for c in split_l(b,32,"l32_")]
        elif stage["op"]=="LAMBDA_REFINE_BY_4": children=[c for b in parents for c in split_l(b,4,"l4_")]
        else: fail("STAGE_OP")
        before=total_eval; next_unresolved=[]; passed=0
        for child in children:
            rec=evaluate(child); evaluated.append(rec|{"stage_id":stage["stage_id"]})
            if rec["status"]=="PASS_POS": terminal[child.box_id]=rec; passed+=1
            else: next_unresolved.append(child)
        ledger.append({"stage_id":stage["stage_id"],"op":stage["op"],"unresolved_parent_count":len(parents),
                       "new_child_count":len(children),"per_box_cap":24000,
                       "declared_stage_max_eval":len(children)*24000,"actual_stage_eval":total_eval-before,
                       "pass_count":passed,"unresolved_count_after_stage":len(next_unresolved)})
        current=next_unresolved
        if not current: break

    if current: verdict="UNRESOLVED"
    else: verdict="PRODUCTION_CANDIDATE_PASS"
    lo_pairs=[(Fraction(r["lo"]),bid) for bid,r in terminal.items() if r.get("lo")]
    margin=min(lo_pairs) if lo_pairs else None
    receipt={"schema":"production-hu-domain-v1.2-production-raw-v1","contract_id":"PRODUCTION_HU_DOMAIN_CONTRACT_V1_2",
             "evidence_class":"PRODUCTION_CANDIDATE","binding_use_authorized":False,
             "policy_sha256":POLICY_SHA256,"runner_sha256":sha(runner_path),
             "geometry_source_sha256":sha(ns.tube_geometry),"geometry_module_sha256":GEOMETRY_MODULE_SHA256,
             "execution_head":__import__("subprocess").check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip(),
             "quantity":"H_U","required_sign":"POS","dps":60,"per_box_cap":24000,"parent":parent.record(),
             "stage_ledger":ledger,"evaluated_boxes":evaluated,
             "terminal_leaves":sorted(terminal.values(),key=lambda r:r["box_id"]),
             "final_unresolved":[b.record() for b in current],"terminal_leaf_count":len(terminal),
             "final_unresolved_count":len(current),"total_eval":total_eval,
             "cover_checks":{},"all_terminal_lo_positive":bool(terminal) and all(Fraction(r["lo"])>0 for r in terminal.values()),
             "certified_cover_margin_exact":None if margin is None else fstr(margin[0]),
             "certified_cover_margin_box_id":None if margin is None else margin[1],
             "cover_margin_is_true_minimum":False,"verdict":verdict}
    if not current:
        receipt["cover_checks"]={"r_endpoints_exact":True,"lambda_endpoints_exact":True,"no_gaps":True,
                                 "no_interior_overlaps":True,"union_equals_parent":True}
    else:
        receipt["cover_checks"]={"r_endpoints_exact":False,"lambda_endpoints_exact":False,"no_gaps":False,
                                 "no_interior_overlaps":False,"union_equals_parent":False}
    ns.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE")
    print("BINDING_USE_AUTHORIZED=FALSE")
    print("VERDICT="+verdict)
    return 0 if not current else 2
if __name__=="__main__":
    raise SystemExit(main())
