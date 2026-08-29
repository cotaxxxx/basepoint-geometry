#!/usr/bin/env python3
"""Fresh cell-0 production replay under released PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

The released producer bytes are replayed unchanged in a detached worktree. The
fresh raw result must be bit-identical to the historical positive control. The
production attestation additionally pins the Component-1 geometry receipt SHA;
that geometry does not alter the replay calculation and is checked later by the
production checker against the replay receipt parent.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode = True

RELEASE_TAG="hu-domain-v1.2"
RELEASE_SHA="6d705c6fbf37ae77d35232a40842692a3e92713e"
PRODUCER_EXECUTION_HEAD="0e3d8954ccd97adf1522088233e65c9729030b4f"
POSITIVE_CONTROL_RESULT_SHA256="f4f9320678aa14a8f7b169580d3b1783c4aacb48b73822b4647323d731650043"
POLICY_SHA256="ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
PRODUCER_SHA256="e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
CHECKER_SHA256="d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
GEOMETRY_MODULE_SHA256="b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300"
REL_DIR="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY=REL_DIR+"/hu_domain_v1_2_stage_policy.json"
REL_PRODUCER=REL_DIR+"/hu_domain_v1_2_cell0_positive_control.py"
REL_CHECKER=REL_DIR+"/hu_domain_v1_2_independent_checker.py"
REL_GEOM=REL_DIR+"/hu_domain_v1_2_tube_geometry.py"
REL_CONTRACT=REL_DIR+"/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
REL_RUNNER="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/cell0_production_hu_run_v1_2.py"

def fail(code): raise SystemExit("STOP:"+code)
def git(repo,*args): return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def sha(path): return sha_bytes(path.read_bytes())
def git_show_bytes(repo,ref,relpath): return subprocess.check_output(["git","-C",str(repo),"show",f"{ref}:{relpath}"])

def require_release_pins(repo):
    if git(repo,"rev-parse",RELEASE_TAG+"^{commit}")!=RELEASE_SHA: fail("RELEASE_TAG_SHA_MISMATCH")
    head=git(repo,"rev-parse","HEAD")
    try:
        subprocess.check_call(["git","-C",str(repo),"merge-base","--is-ancestor",RELEASE_SHA,head],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError: fail("RELEASE_SHA_NOT_ANCESTOR")
    expected={REL_POLICY:POLICY_SHA256,REL_PRODUCER:PRODUCER_SHA256,REL_CHECKER:CHECKER_SHA256}
    for relpath,expected_sha in expected.items():
        if sha_bytes(git_show_bytes(repo,RELEASE_TAG,relpath))!=expected_sha: fail("RELEASE_FILE_SHA_MISMATCH:"+relpath)
        current=repo/relpath
        if not current.is_file() or sha(current)!=expected_sha: fail("CURRENT_RELEASE_FILE_SHA_MISMATCH:"+relpath)
    contract=json.loads((repo/REL_CONTRACT).read_text()); pins=contract.get("pins",{})
    if contract.get("release_status")!="RELEASED_AFTER_POSITIVE_CONTROL_PASS": fail("RELEASE_STATUS")
    if pins.get("stage_policy_sha256")!=POLICY_SHA256: fail("CONTRACT_POLICY_PIN")
    if pins.get("producer_runner_sha256")!=PRODUCER_SHA256: fail("CONTRACT_PRODUCER_PIN")
    if pins.get("independent_checker_sha256")!=CHECKER_SHA256: fail("CONTRACT_CHECKER_PIN")

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",type=Path,required=True)
    ap.add_argument("--tube-geometry",type=Path,required=True)
    ap.add_argument("--raw-result",type=Path,required=True)
    ap.add_argument("--raw-log",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ns=ap.parse_args(); repo=ns.repo.resolve(); geom=ns.tube_geometry.resolve()
    raw_out=ns.raw_result.expanduser().resolve(); log_out=ns.raw_log.expanduser().resolve(); out=ns.out_json.expanduser().resolve()
    if git(repo,"status","--porcelain"): fail("SOURCE_TREE_PRE_DIRTY")
    execution_head=git(repo,"rev-parse","HEAD"); require_release_pins(repo)
    if platform.python_version()!="3.13.14": fail("PYTHON_VERSION")
    if os.environ.get("PYTHONDONTWRITEBYTECODE")!="1" or not sys.dont_write_bytecode: fail("BYTECODE_SUPPRESSION")
    if not geom.is_file(): fail("TUBE_GEOMETRY_MISSING")
    if sha(repo/REL_GEOM)!=GEOMETRY_MODULE_SHA256: fail("GEOMETRY_MODULE_SHA")
    sys.path.insert(0,str(repo/REL_DIR))
    try:
        from hu_domain_v1_2_tube_geometry import derive_parent
        derive_parent(json.loads(geom.read_text()))
    except Exception as exc:
        fail("TUBE_GEOMETRY_GATE:"+type(exc).__name__)
    geometry_sha=sha(geom)
    for p in (raw_out.parent,log_out.parent,out.parent): p.mkdir(parents=True,exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cell0-hu-v12-production-") as td:
        td_path=Path(td); worktree=td_path/"producer-worktree"; fresh_raw=td_path/"fresh_raw.json"; added=False
        try:
            subprocess.check_call(["git","-C",str(repo),"worktree","add","--detach",str(worktree),PRODUCER_EXECUTION_HEAD],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            added=True; producer=worktree/REL_PRODUCER; policy=worktree/REL_POLICY
            if sha(producer)!=PRODUCER_SHA256: fail("DETACHED_PRODUCER_SHA")
            if sha(policy)!=POLICY_SHA256: fail("DETACHED_POLICY_SHA")
            if git(worktree,"status","--porcelain"): fail("DETACHED_WORKTREE_PRE_DIRTY")
            env=dict(os.environ); env["PYTHONDONTWRITEBYTECODE"]="1"
            proc=subprocess.run([sys.executable,str(producer),"--repo",str(worktree),"--out-json",str(fresh_raw)],cwd=worktree,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            log_out.write_text(proc.stdout)
            if not fresh_raw.is_file(): fail("FRESH_RAW_RESULT_MISSING")
            shutil.copyfile(fresh_raw,raw_out)
            if proc.returncode!=0: fail("RELEASED_PRODUCER_NONZERO")
            if git(worktree,"status","--porcelain"): fail("DETACHED_WORKTREE_POST_DIRTY")
        finally:
            if added: subprocess.run(["git","-C",str(repo),"worktree","remove","--force",str(worktree)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

    raw_sha=sha(raw_out)
    if raw_sha!=POSITIVE_CONTROL_RESULT_SHA256: fail("BIT_IDENTITY_MISMATCH")
    raw=json.loads(raw_out.read_text())
    if raw.get("contract_id")!="PRODUCTION_HU_DOMAIN_CONTRACT_V1_2": fail("RAW_CONTRACT_ID")
    if raw.get("policy_sha256")!=POLICY_SHA256: fail("RAW_POLICY_SHA")
    if raw.get("runner_sha256")!=PRODUCER_SHA256: fail("RAW_PRODUCER_SHA")
    if raw.get("execution_head")!=PRODUCER_EXECUTION_HEAD: fail("RAW_EXECUTION_HEAD")
    if raw.get("verdict")!="POSITIVE_CONTROL_PASS": fail("RAW_RELEASED_PRODUCER_VERDICT")
    post_head=git(repo,"rev-parse","HEAD"); post_clean=not bool(git(repo,"status","--porcelain")); head_unchanged=post_head==execution_head
    if not head_unchanged: fail("HEAD_CHANGED_DURING_RUN")
    if not post_clean: fail("SOURCE_TREE_POST_DIRTY")

    receipt={"schema":"production-hu-domain-v1.2-cell0-production-attestation-v2","contract_id":"PRODUCTION_HU_DOMAIN_CONTRACT_V1_2","evidence_class":"PRODUCTION_CANDIDATE","binding_use_authorized":False,"positive_control_receipt_reused":False,"fresh_reexecution":True,"released_policy_sha256":POLICY_SHA256,"released_producer_sha256":PRODUCER_SHA256,"released_checker_sha256":CHECKER_SHA256,"release_sha":RELEASE_SHA,"release_tag":RELEASE_TAG,"producer_execution_head":PRODUCER_EXECUTION_HEAD,"execution_head":execution_head,"runner_sha256":sha(repo/REL_RUNNER),"tube_geometry_receipt_sha256":geometry_sha,"geometry_provenance_role":"REPRODUCIBILITY_ONLY_NOT_LOAD_BEARING","rectangle_identity_role":"LOAD_BEARING_CROSS_COMPONENT_SAME_GEOMETRY_RECEIPT_SHA","raw_result_path":str(raw_out),"raw_result_sha256":raw_sha,"raw_log_path":str(log_out),"raw_log_sha256":sha(log_out),"bit_identity_reference_sha256":POSITIVE_CONTROL_RESULT_SHA256,"bit_identical_to_positive_control":True,"raw_receipt_evidence_class":raw.get("evidence_class"),"raw_receipt_verdict":raw.get("verdict"),"checker_status":"PENDING","monotone_narrow_interface_authorized":False,"source_tree_pre_clean":True,"source_tree_post_clean":post_clean,"head_unchanged_during_run":head_unchanged,"verdict":"PRODUCTION_REPLAY_COMPLETE_CHECKER_PENDING"}
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("CONTRACT_ID=PRODUCTION_HU_DOMAIN_CONTRACT_V1_2"); print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE")
    print("COMPONENT1_GEOMETRY_RECEIPT_SHA256="+geometry_sha); print("POSITIVE_CONTROL_RECEIPT_REUSED=FALSE")
    print("FRESH_REEXECUTION=TRUE"); print("RAW_RESULT_SHA256="+raw_sha); print("BIT_IDENTICAL_TO_POSITIVE_CONTROL=TRUE")
    print("CHECKER_STATUS=PENDING"); print("SOURCE_TREE_PRE=CLEAN"); print("SOURCE_TREE_POST=CLEAN"); print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=PRODUCTION_REPLAY_COMPLETE_CHECKER_PENDING"); print("PRODUCTION_ATTESTATION_SHA256="+sha(out))
    return 0
if __name__=="__main__": raise SystemExit(main())
