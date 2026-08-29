#!/usr/bin/env python3
"""Cell-independent production checker for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

The H_U parent rectangle is never trusted from policy or receipt.  It is
reconstructed exactly from MONOTONE_TUBE_V1.1 Component-1 candidate inputs and
compared with receipt.parent before shared semantic reconstruction.
"""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode = True

RELEASE_TAG="hu-domain-v1.2"
RELEASE_SHA="6d705c6fbf37ae77d35232a40842692a3e92713e"
POLICY_SHA256="ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
REPLAY_PRODUCER_SHA256="e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
PRODUCTION_PRODUCER_SHA256="3d7847c97139a0779695b90ef9b93485e263c5db"
FROZEN_POSITIVE_CONTROL_CHECKER_SHA256="d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
CORE_SHA256="1075d0fefe31117a0cebe99b24321e9cb4e011590102011fb4d1873fcd2af4b2"
GEOMETRY_MODULE_SHA256="b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300"

REL_DIR="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY=REL_DIR+"/hu_domain_v1_2_stage_policy.json"
REL_REPLAY_PRODUCER=REL_DIR+"/hu_domain_v1_2_cell0_positive_control.py"
REL_PRODUCTION_PRODUCER=REL_DIR+"/hu_domain_v1_2_production_producer.py"
REL_FROZEN_CHECKER=REL_DIR+"/hu_domain_v1_2_independent_checker.py"
REL_CONTRACT=REL_DIR+"/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
REL_CORE=REL_DIR+"/hu_domain_v1_2_checker_core.py"
REL_GEOMETRY=REL_DIR+"/hu_domain_v1_2_tube_geometry.py"

def fail(code:str)->None: raise SystemExit("FAIL:"+code)
def git(repo:Path,*args:str)->str: return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()
def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def commit_exists(repo:Path,commit:object)->bool:
    if not isinstance(commit,str) or re.fullmatch(r"[0-9a-f]{40}",commit) is None: return False
    return subprocess.run(["git","-C",str(repo),"cat-file","-e",commit+"^{commit}"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",type=Path,required=True); ap.add_argument("--receipt",type=Path,required=True); ap.add_argument("--production-attestation",type=Path,required=True); ap.add_argument("--tube-geometry",type=Path,required=True); ns=ap.parse_args()
    repo=ns.repo.resolve(); receipt_path=ns.receipt.resolve(); att_path=ns.production_attestation.resolve(); geom_path=ns.tube_geometry.resolve()
    paths={"policy":repo/REL_POLICY,"replay_producer":repo/REL_REPLAY_PRODUCER,"production_producer":repo/REL_PRODUCTION_PRODUCER,"frozen_checker":repo/REL_FROZEN_CHECKER,"contract":repo/REL_CONTRACT,"core":repo/REL_CORE,"geometry_module":repo/REL_GEOMETRY,"receipt":receipt_path,"attestation":att_path,"tube_geometry":geom_path}
    for name,path in paths.items():
        if not path.is_file(): fail("MISSING_"+name.upper())
    if git(repo,"rev-parse",RELEASE_TAG+"^{commit}")!=RELEASE_SHA: fail("RELEASE_TAG_SHA_MISMATCH")
    checks={"policy":POLICY_SHA256,"replay_producer":REPLAY_PRODUCER_SHA256,"production_producer":PRODUCTION_PRODUCER_SHA256,"frozen_checker":FROZEN_POSITIVE_CONTROL_CHECKER_SHA256,"core":CORE_SHA256,"geometry_module":GEOMETRY_MODULE_SHA256}
    for name,expected in checks.items():
        if sha(paths[name])!=expected: fail("FILE_SHA_MISMATCH:"+name)
    contract=json.loads(paths["contract"].read_text()); pins=contract.get("pins",{})
    if contract.get("contract_id")!="PRODUCTION_HU_DOMAIN_CONTRACT_V1_2": fail("CONTRACT_ID")
    if contract.get("release_status")!="RELEASED_AFTER_POSITIVE_CONTROL_PASS": fail("RELEASE_STATUS")
    if pins.get("stage_policy_sha256")!=POLICY_SHA256: fail("CONTRACT_POLICY_PIN")
    if pins.get("producer_runner_sha256")!=REPLAY_PRODUCER_SHA256: fail("CONTRACT_REPLAY_PRODUCER_PIN")
    if pins.get("independent_checker_sha256")!=FROZEN_POSITIVE_CONTROL_CHECKER_SHA256: fail("CONTRACT_FROZEN_CHECKER_PIN")

    receipt=json.loads(receipt_path.read_text()); att=json.loads(att_path.read_text()); geometry=json.loads(geom_path.read_text()); raw_sha=sha(receipt_path)
    if att.get("contract_id")!="PRODUCTION_HU_DOMAIN_CONTRACT_V1_2": fail("ATTESTATION_CONTRACT_ID")
    if att.get("evidence_class")!="PRODUCTION_CANDIDATE": fail("ATTESTATION_EVIDENCE_CLASS")
    if att.get("binding_use_authorized") is not False: fail("ATTESTATION_BINDING_STATE")
    if att.get("raw_result_sha256")!=raw_sha: fail("ATTESTATION_RAW_SHA")
    if att.get("checker_status")!="PENDING": fail("ATTESTATION_CHECKER_STATUS")
    geometry_sha=sha(geom_path)
    if att.get("tube_geometry_receipt_sha256")!=geometry_sha: fail("ATTESTATION_GEOMETRY_RECEIPT_SHA")
    if receipt.get("policy_sha256")!=POLICY_SHA256: fail("RECEIPT_POLICY_SHA")

    observed_producer=receipt.get("runner_sha256")
    if observed_producer==REPLAY_PRODUCER_SHA256:
        role="CELL0_REPLAY_PRODUCER"
        if att.get("positive_control_receipt_reused") is not False or att.get("fresh_reexecution") is not True: fail("REPLAY_ATTESTATION_PROVENANCE")
        if att.get("released_producer_sha256")!=REPLAY_PRODUCER_SHA256: fail("REPLAY_ATTESTATION_PRODUCER_PIN")
        if att.get("released_checker_sha256")!=FROZEN_POSITIVE_CONTROL_CHECKER_SHA256: fail("REPLAY_ATTESTATION_FROZEN_CHECKER_PIN")
    elif observed_producer==PRODUCTION_PRODUCER_SHA256:
        role="CELL_INDEPENDENT_PRODUCTION_PRODUCER"
        if att.get("production_producer_sha256")!=PRODUCTION_PRODUCER_SHA256: fail("PRODUCTION_ATTESTATION_PRODUCER_PIN")
    else: fail("RECEIPT_PRODUCER_NOT_ALLOWLISTED")

    receipt_head=receipt.get("execution_head")
    if not commit_exists(repo,receipt_head): fail("RECEIPT_EXECUTION_HEAD_NOT_GIT_COMMIT")
    if att.get("producer_execution_head")!=receipt_head: fail("ATTESTATION_PRODUCER_HEAD_MISMATCH")
    sys.path.insert(0,str(repo/REL_DIR))
    try:
        from hu_domain_v1_2_tube_geometry import GeometryError, derive_parent
        from hu_domain_v1_2_checker_core import ValidationError, validate_semantics
    except Exception as exc: fail("IMPORT:"+type(exc).__name__)
    try: derived=derive_parent(geometry)
    except GeometryError as exc: fail(str(exc))
    parent=receipt.get("parent")
    if not isinstance(parent,dict): fail("RECEIPT_PARENT")
    for key in ("r_lo","r_hi","lambda_lo","lambda_hi"):
        if parent.get(key)!=derived[key]: fail("DERIVED_PARENT_MISMATCH:"+key)
    if observed_producer==PRODUCTION_PRODUCER_SHA256:
        if receipt.get("geometry_source_sha256")!=geometry_sha: fail("RECEIPT_GEOMETRY_SOURCE_SHA")
        if receipt.get("geometry_module_sha256")!=GEOMETRY_MODULE_SHA256: fail("RECEIPT_GEOMETRY_MODULE_SHA")
    policy=json.loads(paths["policy"].read_text()); c=geometry.get("candidate_inputs",{})
    if c.get("cell_index")==0:
        pc=policy.get("parent",{})
        for key in ("r_lo","r_hi","lambda_lo","lambda_hi"):
            if pc.get(key)!=derived[key]: fail("CELL0_POLICY_PARENT_CROSSCHECK:"+key)

    semantic_receipt=receipt
    if observed_producer==REPLAY_PRODUCER_SHA256:
        semantic_receipt=json.loads(json.dumps(receipt))
        for rec in semantic_receipt.get("evaluated_boxes",[]):
            if rec.get("status")=="ABORT" and rec.get("abort_reason")=="ANGULAR_EVALUATION_BUDGET":
                rec["status"]="ABORT_BUDGET"; rec["complete_closed_cover"]=False
            elif rec.get("status")=="ABORT": fail("LEGACY_REPLAY_ABORT_NOT_NORMALIZABLE:"+str(rec.get("box_id")))
    try: result=validate_semantics(policy,semantic_receipt)
    except ValidationError as exc: fail(str(exc))
    print("CHECKER_ID=PRODUCTION_HU_DOMAIN_V1_2_PRODUCTION_CHECKER_V3")
    print("LEGACY_REPLAY_STATUS_ADAPTER="+("APPLIED" if observed_producer==REPLAY_PRODUCER_SHA256 else "NOT_APPLICABLE"))
    print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE"); print("PRODUCER_ROLE="+role); print("PRODUCER_SHA256="+observed_producer)
    print("PARENT_SOURCE=MONOTONE_TUBE_V1_1_COMPONENT1_RECONSTRUCTED"); print("RECEIPT_PARENT_EXACT_MATCH=TRUE"); print("CELL0_POLICY_PARENT_ROLE=POSITIVE_CONTROL_CROSSCHECK_ONLY")
    print("STAGE_ORDER=PASS"); print("FIRST_PASSING=PASS"); print("RESOLVED_LEAF_IMMUTABLE=PASS"); print("RAW_EVALUATED_BOX_ACCOUNTING=PASS"); print("BUDGET_ACCOUNTING=PASS")
    print("REFINABLE_STATUS_COUNTS="+json.dumps(result["refinable_status_counts"],sort_keys=True,separators=(",",":")))
    print("UNION_EQUALS_PARENT=TRUE"); print("ALL_TERMINAL_LO_POSITIVE=TRUE"); print("CERTIFIED_COVER_MARGIN_EXACT="+result["margin_exact"]); print("CERTIFIED_COVER_MARGIN_POSITIVE=TRUE"); print("COVER_MARGIN_IS_TRUE_MINIMUM=NO"); print("PRODUCTION_CHECKER_VERDICT=PASS")
    return 0
if __name__=="__main__": raise SystemExit(main())
