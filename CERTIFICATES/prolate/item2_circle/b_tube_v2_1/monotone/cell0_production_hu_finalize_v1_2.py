#!/usr/bin/env python3
"""Finalize cell-0 H_U production evidence after geometry-derived checker PASS.

The cell-0 raw replay must remain bit-identical to the historical positive
control as a determinism cross-check. Binding use remains Judge-gated.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, subprocess, sys
from fractions import Fraction
from pathlib import Path
sys.dont_write_bytecode=True

RELEASE_TAG="hu-domain-v1.2"
RELEASE_SHA="6d705c6fbf37ae77d35232a40842692a3e92713e"
POLICY_SHA256="ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
REPLAY_PRODUCER_SHA256="e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
FROZEN_CHECKER_SHA256="d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
PRODUCTION_CHECKER_GIT_BLOB_SHA1="f4f86afa659bdce1ac9578178c43de5863ade342"
CHECKER_CORE_SHA256="1075d0fefe31117a0cebe99b24321e9cb4e011590102011fb4d1873fcd2af4b2"
GEOMETRY_MODULE_SHA256="b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300"
POSITIVE_CONTROL_RESULT_SHA256="f4f9320678aa14a8f7b169580d3b1783c4aacb48b73822b4647323d731650043"
REL_DIR="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_CHECKER=REL_DIR+"/hu_domain_v1_2_production_checker.py"
REL_GEOM=REL_DIR+"/hu_domain_v1_2_tube_geometry.py"
REL_RUNNER="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/cell0_production_hu_finalize_v1_2.py"

def fail(c): raise SystemExit("STOP:"+c)
def git(repo,*args): return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def frac(v,w):
    if not isinstance(v,str): fail("BAD_FRACTION:"+w)
    q=Fraction(v)
    if v!=f"{q.numerator}/{q.denominator}": fail("NONCANONICAL_FRACTION:"+w)
    return q

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,required=True); ap.add_argument("--raw-result",type=Path,required=True); ap.add_argument("--production-attestation",type=Path,required=True); ap.add_argument("--tube-geometry",type=Path,required=True); ap.add_argument("--checker-log",type=Path,required=True); ap.add_argument("--out-json",type=Path,required=True); ns=ap.parse_args()
    repo=ns.repo.resolve(); raw=ns.raw_result.resolve(); att=ns.production_attestation.resolve(); geom=ns.tube_geometry.resolve(); log=ns.checker_log.resolve(); out=ns.out_json.resolve()
    if git(repo,"status","--porcelain"): fail("SOURCE_TREE_PRE_DIRTY")
    head=git(repo,"rev-parse","HEAD")
    if git(repo,"rev-parse",RELEASE_TAG+"^{commit}")!=RELEASE_SHA: fail("RELEASE_TAG")
    if platform.python_version()!="3.13.14": fail("PYTHON_VERSION")
    if os.environ.get("PYTHONDONTWRITEBYTECODE")!="1" or not sys.dont_write_bytecode: fail("BYTECODE_SUPPRESSION")
    if not all(p.is_file() for p in (raw,att,geom)): fail("MISSING_INPUT")
    if git(repo,"rev-parse",head+":"+REL_CHECKER)!=PRODUCTION_CHECKER_GIT_BLOB_SHA1: fail("PRODUCTION_CHECKER_BLOB")
    if sha(repo/REL_GEOM)!=GEOMETRY_MODULE_SHA256: fail("GEOMETRY_MODULE_SHA")
    raw_sha=sha(raw); geometry_sha=sha(geom)
    if raw_sha!=POSITIVE_CONTROL_RESULT_SHA256: fail("CELL0_DETERMINISM_CROSSCHECK_MISMATCH")
    a=json.loads(att.read_text())
    if a.get("evidence_class")!="PRODUCTION_CANDIDATE" or a.get("binding_use_authorized") is not False: fail("ATTESTATION_STATE")
    if a.get("positive_control_receipt_reused") is not False or a.get("fresh_reexecution") is not True: fail("ATTESTATION_PROVENANCE")
    if a.get("raw_result_sha256")!=raw_sha or a.get("checker_status")!="PENDING": fail("ATTESTATION_LINK")
    if a.get("tube_geometry_receipt_sha256")!=geometry_sha: fail("ATTESTATION_GEOMETRY_RECEIPT_SHA")
    cmd=[sys.executable,str(repo/REL_CHECKER),"--repo",str(repo),"--receipt",str(raw),"--production-attestation",str(att),"--tube-geometry",str(geom)]
    env=dict(os.environ); env["PYTHONDONTWRITEBYTECODE"]="1"
    proc=subprocess.run(cmd,cwd=repo,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    log.parent.mkdir(parents=True,exist_ok=True); log.write_text(proc.stdout)
    if proc.returncode!=0 or "PRODUCTION_CHECKER_VERDICT=PASS" not in proc.stdout: fail("PRODUCTION_CHECKER_FAIL")
    r=json.loads(raw.read_text()); all_pos=r.get("all_terminal_lo_positive") is True; union=r.get("cover_checks",{}).get("union_equals_parent") is True; margin_text=r.get("certified_cover_margin_exact"); margin=frac(margin_text,"margin")
    if not all_pos or not union or margin<=0: fail("NARROW_INTERFACE_CANDIDATE")
    post_head=git(repo,"rev-parse","HEAD"); post_clean=not bool(git(repo,"status","--porcelain"))
    if post_head!=head: fail("HEAD_CHANGED")
    if not post_clean: fail("SOURCE_TREE_POST_DIRTY")
    receipt={"schema":"production-hu-domain-v1.2-cell0-production-receipt-v4","contract_id":"PRODUCTION_HU_DOMAIN_CONTRACT_V1_2","evidence_class":"PRODUCTION_CANDIDATE","binding_use_authorized":False,"release_sha":RELEASE_SHA,"release_tag":RELEASE_TAG,"released_policy_sha256":POLICY_SHA256,"replay_producer_sha256":REPLAY_PRODUCER_SHA256,"frozen_positive_control_checker_sha256":FROZEN_CHECKER_SHA256,"production_checker_git_blob_sha1":PRODUCTION_CHECKER_GIT_BLOB_SHA1,"checker_core_sha256":CHECKER_CORE_SHA256,"geometry_module_sha256":GEOMETRY_MODULE_SHA256,"component1_geometry_receipt_sha256":geometry_sha,"execution_head":head,"finalizer_sha256":sha(repo/REL_RUNNER),"production_attestation_sha256":sha(att),"raw_result_sha256":raw_sha,"checker_log_sha256":sha(log),"checker_verdict":"PASS","promotion_status":"READY_FOR_JUDGE_PROMOTION","judge_signature_status":"PENDING","positive_control_receipt_reused":False,"fresh_reexecution":True,"cell0_determinism_crosscheck":{"reference_sha256":POSITIVE_CONTROL_RESULT_SHA256,"bit_identical":True,"role":"CELL0_ONLY_REPRODUCIBILITY_CROSSCHECK_NOT_PRODUCTION_CHECKER_CONDITION"},"parent":r.get("parent"),"parent_source":"MONOTONE_TUBE_V1_1_COMPONENT1_RECONSTRUCTED_AND_CHECKED","cross_component_rectangle_identity":"REQUIRES_SAME_COMPONENT1_GEOMETRY_RECEIPT_SHA_IN_F_LAMBDA_AND_JOIN_RECEIPTS","narrow_interface_candidate":{"ALL_TERMINAL_LO_POSITIVE":all_pos,"UNION_EQUALS_PARENT":union,"CERTIFIED_COVER_MARGIN_EXACT":margin_text,"CERTIFIED_COVER_MARGIN_POSITIVE":True,"COVER_MARGIN_IS_TRUE_MINIMUM":False},"monotone_narrow_interface_authorized":False,"source_tree_pre_clean":True,"source_tree_post_clean":post_clean,"head_unchanged_during_run":True,"verdict":"CELL0_PRODUCTION_HU_CHECKER_PASS_READY_FOR_JUDGE_PROMOTION"}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("PRODUCTION_CHECKER_VERDICT=PASS"); print("COMPONENT1_GEOMETRY_RECEIPT_SHA256="+geometry_sha); print("PARENT_SOURCE=MONOTONE_TUBE_V1_1_COMPONENT1_RECONSTRUCTED_AND_CHECKED"); print("CELL0_DETERMINISM_CROSSCHECK=PASS"); print("BINDING_USE_AUTHORIZED=FALSE"); print("PROMOTION_STATUS=READY_FOR_JUDGE_PROMOTION"); print("JUDGE_SIGNATURE_STATUS=PENDING"); print("PRODUCTION_RECEIPT_SHA256="+sha(out)); return 0
if __name__=="__main__": raise SystemExit(main())
