#!/usr/bin/env python3
"""Cell-independent H_U producer for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

The released V1.2 policy supplies only finite stage semantics/cap/dps.
The parent is reconstructed from the Component-1 geometry receipt; policy.parent
is ignored for production. Runtime bytes are content-SHA256 pinned against one
immutable runtime baseline, and the source tree must remain clean at one
explicitly pinned execution HEAD.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, sys
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode = True

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_GEOM = REL_DIR + "/hu_domain_v1_2_tube_geometry.py"
REL_RUNNER = REL_DIR + "/hu_domain_v1_2_production_producer.py"
REL_BT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
REL_V23 = REL_BT + "/dependencies/blocal_v23_source"
POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
GEOMETRY_MODULE_SHA256 = "b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300"
KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
RUNTIME_BASELINE_HEAD = "7d3b8e8b0e41d913f6b3bd7944914fd0119e0824"
RUNTIME_CONTENT_PATHS = (
    REL_V23 + "/blocal_phase4_model.py",
    REL_V23 + "/blocal_v22_model.py",
    REL_V23 + "/blocal_arb_adapter.py",
    REL_V23 + "/blocal_v22_boundary.py",
    REL_V23 + "/blocal_v23_boundary.py",
    REL_V23 + "/blocal_v22_policy.py",
    REL_V23 + "/blocal_v22_symbolic_audit.py",
    REL_V23 + "/config.blocal-v2.2-run.json",
    REL_V23 + "/BLOCAL_V23_ROUTE_CONFIG.fragment.json",
    REL_V23 + "/blocal_v23_flambda_kernel.py",
    REL_BT + "/calibration_context.py",
    REL_BT + "/affine_geometry.py",
    REL_BT + "/numeric_schema.py",
    REL_BT + "/calibration_config.py",
    REL_BT + "/calibration_runner.py",
    REL_BT + "/exact_lambda_transport.py",
)
# Independent known content-SHA256 cross-checks inherited from the F_lambda
# precheck/released dependency manifests.  Every runtime path, including those
# without a separate historical constant here, is pinned by SHA256 of the bytes
# at RUNTIME_BASELINE_HEAD and compared with the working-tree bytes.
KNOWN_CONTENT_SHA256 = {
    REL_V23 + "/blocal_phase4_model.py": "92bc9010cbaf7e3c61a79aa6bb05e2f717a99486e1faac416e0f3dd3ee5f327a",
    REL_V23 + "/blocal_v22_model.py": "8e9bcb0d9519cd6feb2375486985dddde43735dcb327cded28e96a33c61acb16",
    REL_V23 + "/blocal_arb_adapter.py": "99e640fba88cfe353ea360190a03df7a9de8840637922f9f56fa6b7168d94e66",
    REL_V23 + "/blocal_v22_boundary.py": "aea768c02644fdb08c8c32455207efe7424c7dc34efe378ad545c3ab9418abf9",
    REL_V23 + "/blocal_v23_boundary.py": "8aa6647cc93026afee113cc2435fd7af858c93dc17fd1c79a5db2754f246218c",
    REL_V23 + "/blocal_v22_policy.py": "d8bac8535f5146f22906e8cdc604640edd909709998a41d7f377c9802ca7cc65",
    REL_V23 + "/blocal_v22_symbolic_audit.py": "b75ce97c8ff1342c6472a744cf2b64bf3413a3112190a5ff6fed73f60b40d0a1",
    REL_V23 + "/config.blocal-v2.2-run.json": "dab371fa62ed10a00029cd31b0002e503952277ef072fb8f5d7fd5222965d469",
    REL_V23 + "/BLOCAL_V23_ROUTE_CONFIG.fragment.json": "93a511c33b8b68443b8ee7a56d0cfbd1f7cb023f54e0fddba6926c1dd96b5f30",
    REL_V23 + "/blocal_v23_flambda_kernel.py": "26d3357132fee064293932df51208acd445e8bd14200d70862a2ee62ba4cc086",
    REL_BT + "/exact_lambda_transport.py": "adee7587a7519e8c0274470a63ddda6c82f4b8ebd4117c18fcab1ce77fb0ce80",
}
REFINABLE = {"UNRESOLVED_SIGN", "ABORT_BUDGET", "ABORT_INCOMPLETE_COVER"}
HARD_FAIL = {"ABORT_NONFINITE", "ABORT_INTERNAL"}

def fail(code: str) -> None: raise SystemExit("STOP:" + code)
def sha_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def sha(path: Path) -> str: return sha_bytes(path.read_bytes())
def git(repo: Path, *args: str) -> str: return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def git_show_bytes(repo: Path, ref: str, rel: str) -> bytes: return subprocess.check_output(["git","-C",str(repo),"show",f"{ref}:{rel}"])
def fstr(q: Fraction) -> str: return f"{q.numerator}/{q.denominator}"

def precheck(repo: Path, expected_head: str) -> dict[str,str]:
    if len(expected_head)!=40 or git(repo,"rev-parse","HEAD")!=expected_head: fail("HEAD_PIN_MISMATCH")
    if git(repo,"status","--porcelain"): fail("SOURCE_TREE_PRE_DIRTY")
    if subprocess.run(["git","-C",str(repo),"cat-file","-e",RUNTIME_BASELINE_HEAD+"^{commit}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode!=0:
        fail("RUNTIME_BASELINE_HEAD_MISSING")
    if sha(repo/REL_POLICY)!=POLICY_SHA256: fail("POLICY_SHA")
    if sha(repo/REL_GEOM)!=GEOMETRY_MODULE_SHA256: fail("GEOMETRY_MODULE_SHA")
    actual={}
    for rel in RUNTIME_CONTENT_PATHS:
        path=repo/rel
        if not path.is_file(): fail("RUNTIME_FILE_MISSING:"+rel)
        expected_sha=sha_bytes(git_show_bytes(repo,RUNTIME_BASELINE_HEAD,rel))
        known=KNOWN_CONTENT_SHA256.get(rel)
        if known is not None and expected_sha!=known: fail("RUNTIME_BASELINE_KNOWN_SHA256_MISMATCH:"+rel)
        got=sha(path); actual[rel]=got
        if got!=expected_sha: fail("RUNTIME_CONTENT_SHA256_MISMATCH:"+rel)
    return actual

class Box:
    def __init__(self,bid,r0,r1,l0,l1,g=0,parent=None):
        self.box_id,self.r_lo,self.r_hi,self.lambda_lo,self.lambda_hi,self.generation,self.parent_id=bid,r0,r1,l0,l1,g,parent
    def record(self):
        return {"box_id":self.box_id,"parent_id":self.parent_id,"generation":self.generation,
                "r_lo":fstr(self.r_lo),"r_hi":fstr(self.r_hi),"lambda_lo":fstr(self.lambda_lo),"lambda_hi":fstr(self.lambda_hi)}
def split_r(b):
    m=(b.r_lo+b.r_hi)/2
    return [Box(b.box_id+"/r0",b.r_lo,m,b.lambda_lo,b.lambda_hi,b.generation+1,b.box_id),Box(b.box_id+"/r1",m,b.r_hi,b.lambda_lo,b.lambda_hi,b.generation+1,b.box_id)]
def split_l(b,n,tag):
    w=(b.lambda_hi-b.lambda_lo)/n
    return [Box(f"{b.box_id}/{tag}{k}",b.r_lo,b.r_hi,b.lambda_lo+k*w,b.lambda_lo+(k+1)*w,b.generation+1,b.box_id) for k in range(n)]

def classify_failure(reason: object) -> tuple[str,str]:
    text=str(reason)
    upper=text.upper()
    if "BUDGET" in upper: return "ABORT_BUDGET","ANGULAR_EVALUATION_BUDGET"
    if any(token in upper for token in ("NONFINITE","NAN","INFINITE","INF")): return "ABORT_NONFINITE",text
    return "ABORT_INTERNAL",text

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,required=True)
    ap.add_argument("--expected-head",required=True)
    ap.add_argument("--tube-geometry",type=Path,required=True)
    ap.add_argument("--box-id",required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ns=ap.parse_args(); repo=ns.repo.resolve()
    if os.environ.get("PYTHONDONTWRITEBYTECODE")!="1" or not sys.dont_write_bytecode: fail("BYTECODE_SUPPRESSION")
    if platform.python_version()!="3.13.14": fail("PYTHON_VERSION")
    runtime_actual=precheck(repo,ns.expected_head)
    policy=json.loads((repo/REL_POLICY).read_text())
    if policy.get("contract_id")!="PRODUCTION_HU_DOMAIN_CONTRACT_V1_2": fail("POLICY_CONTRACT")
    if policy.get("dps")!=60 or policy.get("per_box_cap")!=24000: fail("POLICY_DPS_CAP")
    geom_path=ns.tube_geometry.resolve(); geom=json.loads(geom_path.read_text())
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
    bcfg=json.loads((v23/"config.blocal-v2.2-run.json").read_text()); frag=json.loads((v23/"BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
    bcfg["route_policies"].update(frag["route_policies"])

    terminal={}; evaluated=[]; ledger=[]; total_eval=0; current=[]; status_counts={k:0 for k in ["PASS_POS",*sorted(REFINABLE)]}
    def evaluate(b):
        nonlocal total_eval
        u0=Fraction(1)-b.r_hi; u1=Fraction(1)-b.r_lo; s0=b.lambda_lo-model.LAMBDA_PLUS; s1=b.lambda_hi-model.LAMBDA_PLUS
        rec=b.record()|{"status":None,"required_sign":"POS","effective_evaluation_cap":24000,"lo":None,"hi":None,"width":None,"evaluation_count":0,"proof_id":None,"abort_reason":None,"complete_closed_cover":None}
        try:
            iv,proof=route.base.enclose_hu(raw_kernel,adapter,acb,arb,fmpq,bcfg,u0,u1,s0,s1,required_sign="POS",accept=None,evaluation_cap=24000)
            lo,hi=model.interval_fractions(iv,b.box_id); ev=int(proof["evaluation_count"]); total_eval+=ev
            complete=bool(proof.get("complete_closed_cover"))
            status="PASS_POS" if complete and lo>0 else ("UNRESOLVED_SIGN" if complete else "ABORT_INCOMPLETE_COVER")
            rec.update(status=status,lo=fstr(lo),hi=fstr(hi),width=fstr(hi-lo),evaluation_count=ev,proof_id=proof.get("proof_id"),complete_closed_cover=complete,route_id=proof.get("route_id"))
            if status=="ABORT_INCOMPLETE_COVER": rec["abort_reason"]="INCOMPLETE_ANGULAR_COVER"
        except route.base.EnclosureFailure as exc:
            ev=int(exc.evaluations); total_eval+=ev; status,reason=classify_failure(exc.reason)
            if status in HARD_FAIL: fail(status+":"+reason)
            rec.update(status=status,evaluation_count=ev,abort_reason=reason,complete_closed_cover=False)
        return rec

    stages=policy["stages"]
    expected_ids=["S0_BASE","S1_R1","S2_R2","S3_R3","S4_R4","S5_R5","S6_R6","S7_L32","S8_R_POST_L32_1","S9_R_POST_L32_2","S10_L128"]
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
        before=total_eval; next_unresolved=[]; passed=0; stage_counts={k:0 for k in status_counts}
        for child in children:
            rec=evaluate(child); status_counts[rec["status"]]+=1; stage_counts[rec["status"]]+=1; evaluated.append(rec|{"stage_id":stage["stage_id"]})
            if rec["status"]=="PASS_POS": terminal[child.box_id]=rec; passed+=1
            elif rec["status"] in REFINABLE: next_unresolved.append(child)
            else: fail("UNDECLARED_STATUS:"+str(rec["status"]))
        ledger.append({"stage_id":stage["stage_id"],"op":stage["op"],"unresolved_parent_count":len(parents),"new_child_count":len(children),"per_box_cap":24000,"declared_stage_max_eval":len(children)*24000,"actual_stage_eval":total_eval-before,"pass_count":passed,"unresolved_count_after_stage":len(next_unresolved),"status_counts":stage_counts})
        current=next_unresolved
        if not current: break

    verdict="UNRESOLVED" if current else "PRODUCTION_CANDIDATE_PASS"
    lo_pairs=[(Fraction(r["lo"]),bid) for bid,r in terminal.items() if r.get("lo")]; margin=min(lo_pairs) if lo_pairs else None
    post_head=git(repo,"rev-parse","HEAD"); post_clean=not bool(git(repo,"status","--porcelain"))
    if post_head!=ns.expected_head: fail("HEAD_CHANGED_DURING_RUN")
    if not post_clean: fail("SOURCE_TREE_POST_DIRTY")
    receipt={"schema":"production-hu-domain-v1.2-production-raw-v2","contract_id":"PRODUCTION_HU_DOMAIN_CONTRACT_V1_2","evidence_class":"PRODUCTION_CANDIDATE","binding_use_authorized":False,"policy_sha256":POLICY_SHA256,"runner_sha256":sha(repo/REL_RUNNER),"geometry_source_sha256":sha(geom_path),"geometry_module_sha256":GEOMETRY_MODULE_SHA256,"execution_head":ns.expected_head,"runtime_baseline_head":RUNTIME_BASELINE_HEAD,"runtime_pin_algorithm":"SHA256_CONTENT_BYTES_ONLY","source_tree_pre_clean":True,"source_tree_post_clean":True,"head_unchanged_during_run":True,"runtime_dependency_sha256":runtime_actual,"quantity":"H_U","required_sign":"POS","dps":60,"per_box_cap":24000,"parent":parent.record(),"stage_ledger":ledger,"evaluated_boxes":evaluated,"status_counts":status_counts,"terminal_leaves":sorted(terminal.values(),key=lambda r:r["box_id"]),"final_unresolved":[b.record() for b in current],"terminal_leaf_count":len(terminal),"final_unresolved_count":len(current),"total_eval":total_eval,"cover_checks":{},"all_terminal_lo_positive":bool(terminal) and all(Fraction(r["lo"])>0 for r in terminal.values()),"certified_cover_margin_exact":None if margin is None else fstr(margin[0]),"certified_cover_margin_box_id":None if margin is None else margin[1],"cover_margin_is_true_minimum":False,"verdict":verdict}
    receipt["cover_checks"]={"r_endpoints_exact":not current,"lambda_endpoints_exact":not current,"no_gaps":not current,"no_interior_overlaps":not current,"union_equals_parent":not current}
    ns.out_json.parent.mkdir(parents=True,exist_ok=True); ns.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("RUNTIME_PIN_ALGORITHM=SHA256_CONTENT_BYTES_ONLY"); print("RUNTIME_BASELINE_HEAD="+RUNTIME_BASELINE_HEAD)
    print("SOURCE_TREE_PRE=CLEAN"); print("SOURCE_TREE_POST=CLEAN"); print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE"); print("BINDING_USE_AUTHORIZED=FALSE"); print("VERDICT="+verdict)
    return 0 if not current else 2
if __name__=="__main__": raise SystemExit(main())
