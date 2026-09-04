#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

RELEASE_TAG = "hu-domain-v1.2"
RELEASE_SHA = "6d705c6fbf37ae77d35232a40842692a3e92713e"

POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
PRODUCTION_PRODUCER_SHA256 = "d5d54e31daa6aa45c75782b54f40db92a7075c24f567d1d9acf7b481021e22d8"
PRODUCTION_CHECKER_SHA256 = "9d8ad733677826411635fd266cc5ad052aca8f9aaa6e9c3f65c16a4ff808dbaa"
CHECKER_CORE_SHA256 = "1075d0fefe31117a0cebe99b24321e9cb4e011590102011fb4d1873fcd2af4b2"
GEOMETRY_MODULE_SHA256 = "b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300"

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_PRODUCER = REL_DIR + "/hu_domain_v1_2_production_producer.py"
REL_CHECKER = REL_DIR + "/hu_domain_v1_2_production_checker.py"
REL_CORE = REL_DIR + "/hu_domain_v1_2_checker_core.py"
REL_GEOM = REL_DIR + "/hu_domain_v1_2_tube_geometry.py"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_RUNNER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/hu_domain_v1_2_production_finalize.py"

def fail(code: str):
    raise SystemExit("STOP:" + code)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True
    ).strip()

def canonical_fraction(value, field):
    if not isinstance(value, str):
        fail("BAD_FRACTION:" + field)
    q = Fraction(value)
    if value != f"{q.numerator}/{q.denominator}":
        fail("NONCANONICAL_FRACTION:" + field)
    return q

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--raw-result", type=Path, required=True)
    ap.add_argument("--production-attestation", type=Path, required=True)
    ap.add_argument("--tube-geometry", type=Path, required=True)
    ap.add_argument("--checker-log", type=Path, required=True)
    ap.add_argument("--cell-id", required=True)
    ap.add_argument("--cell-index", type=int, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    raw_p = ns.raw_result.resolve()
    att_p = ns.production_attestation.resolve()
    geom_p = ns.tube_geometry.resolve()
    log_p = ns.checker_log.resolve()
    out_p = ns.out_json.resolve()

    if ns.cell_index < 0:
        fail("BAD_CELL_INDEX")

    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE_DIRTY")

    head = git(repo, "rev-parse", "HEAD")

    if git(repo, "rev-parse", RELEASE_TAG + "^{commit}") != RELEASE_SHA:
        fail("RELEASE_TAG")

    if platform.python_version() != "3.13.14":
        fail("PYTHON_VERSION")

    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1" or not sys.dont_write_bytecode:
        fail("BYTECODE_SUPPRESSION")

    for p in (raw_p, att_p, geom_p):
        if not p.is_file():
            fail("MISSING_INPUT")

    if sha(repo / REL_PRODUCER) != PRODUCTION_PRODUCER_SHA256:
        fail("PRODUCTION_PRODUCER_SHA256")
    if sha(repo / REL_CHECKER) != PRODUCTION_CHECKER_SHA256:
        fail("PRODUCTION_CHECKER_SHA256")
    if sha(repo / REL_CORE) != CHECKER_CORE_SHA256:
        fail("CHECKER_CORE_SHA256")
    if sha(repo / REL_GEOM) != GEOMETRY_MODULE_SHA256:
        fail("GEOMETRY_MODULE_SHA256")
    if sha(repo / REL_POLICY) != POLICY_SHA256:
        fail("POLICY_SHA256")

    raw = json.loads(raw_p.read_text())
    att = json.loads(att_p.read_text())
    geom = json.loads(geom_p.read_text())

    cmd = [
        sys.executable,
        str(repo / REL_CHECKER),
        "--repo", str(repo),
        "--receipt", str(raw_p),
        "--production-attestation", str(att_p),
        "--tube-geometry", str(geom_p),
    ]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        cmd,
        cwd=repo,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_p.parent.mkdir(parents=True, exist_ok=True)
    log_p.write_text(proc.stdout)
    log = proc.stdout

    if proc.returncode != 0:
        fail("PRODUCTION_CHECKER_FAIL")

    raw_sha = sha(raw_p)
    att_sha = sha(att_p)
    geom_sha = sha(geom_p)
    log_sha = sha(log_p)

    if raw.get("schema") != "production-hu-domain-v1.2-production-raw-v2":
        fail("RAW_SCHEMA")
    if raw.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("RAW_CONTRACT")
    if raw.get("evidence_class") != "PRODUCTION_CANDIDATE":
        fail("RAW_EVIDENCE_CLASS")
    if raw.get("binding_use_authorized") is not False:
        fail("RAW_BINDING_STATE")
    if raw.get("runner_sha256") != PRODUCTION_PRODUCER_SHA256:
        fail("RAW_PRODUCER_SHA")
    if raw.get("geometry_source_sha256") != geom_sha:
        fail("RAW_GEOMETRY_SHA")
    if raw.get("verdict") != "PRODUCTION_CANDIDATE_PASS":
        fail("RAW_VERDICT")
    if raw.get("quantity") != "H_U" or raw.get("required_sign") != "POS":
        fail("RAW_QUANTITY_SIGN")

    if att.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("ATTESTATION_CONTRACT")
    if att.get("evidence_class") != "PRODUCTION_CANDIDATE":
        fail("ATTESTATION_EVIDENCE_CLASS")
    if att.get("binding_use_authorized") is not False:
        fail("ATTESTATION_BINDING_STATE")
    if att.get("raw_result_sha256") != raw_sha:
        fail("ATTESTATION_RAW_SHA")
    if att.get("tube_geometry_receipt_sha256") != geom_sha:
        fail("ATTESTATION_GEOMETRY_SHA")
    if att.get("production_producer_sha256") != PRODUCTION_PRODUCER_SHA256:
        fail("ATTESTATION_PRODUCER_SHA")
    if att.get("producer_execution_head") != raw.get("execution_head"):
        fail("ATTESTATION_EXECUTION_HEAD")
    if att.get("checker_status") != "PENDING":
        fail("ATTESTATION_CHECKER_STATUS")

    if geom.get("schema") != "monotone-tube-v1.1-component1-geometry-receipt-v1":
        fail("GEOMETRY_SCHEMA")
    if geom.get("binding_use_authorized") is not False:
        fail("GEOMETRY_BINDING_STATE")
    if geom.get("cell_id") != ns.cell_id:
        fail("CELL_ID_MISMATCH")
    if geom.get("candidate_inputs", {}).get("cell_index") != ns.cell_index:
        fail("CELL_INDEX_MISMATCH")

    if "PRODUCTION_CHECKER_VERDICT=PASS" not in log:
        fail("CHECKER_LOG_VERDICT")
    if "RECEIPT_PARENT_EXACT_MATCH=TRUE" not in log:
        fail("CHECKER_LOG_PARENT")
    if "UNION_EQUALS_PARENT=TRUE" not in log:
        fail("CHECKER_LOG_UNION")
    if "ALL_TERMINAL_LO_POSITIVE=TRUE" not in log:
        fail("CHECKER_LOG_POSITIVITY")
    if "CERTIFIED_COVER_MARGIN_POSITIVE=TRUE" not in log:
        fail("CHECKER_LOG_MARGIN")

    if raw.get("final_unresolved_count") != 0:
        fail("FINAL_UNRESOLVED")

    all_pos = raw.get("all_terminal_lo_positive") is True
    union = raw.get("cover_checks", {}).get("union_equals_parent") is True
    margin_text = raw.get("certified_cover_margin_exact")
    margin = canonical_fraction(margin_text, "certified_cover_margin_exact")

    if not all_pos or not union or margin <= 0:
        fail("NARROW_INTERFACE_CANDIDATE")

    post_head = git(repo, "rev-parse", "HEAD")
    post_clean = not bool(git(repo, "status", "--porcelain"))

    if post_head != head:
        fail("HEAD_CHANGED")
    if not post_clean:
        fail("SOURCE_TREE_POST_DIRTY")

    receipt = {
        "schema": "production-hu-domain-v1.2-cell-production-receipt-v1",
        "contract_id": "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2",
        "cell_id": ns.cell_id,
        "cell_index": ns.cell_index,
        "evidence_class": "PRODUCTION_CANDIDATE",
        "binding_use_authorized": False,
        "monotone_narrow_interface_authorized": False,
        "release_tag": RELEASE_TAG,
        "release_sha": RELEASE_SHA,
        "released_policy_sha256": POLICY_SHA256,
        "production_producer_sha256": PRODUCTION_PRODUCER_SHA256,
        "production_checker_sha256": PRODUCTION_CHECKER_SHA256,
        "checker_core_sha256": CHECKER_CORE_SHA256,
        "geometry_module_sha256": GEOMETRY_MODULE_SHA256,
        "component1_geometry_receipt_sha256": geom_sha,
        "raw_result_sha256": raw_sha,
        "production_attestation_sha256": att_sha,
        "checker_log_sha256": log_sha,
        "execution_head": head,
        "producer_execution_head": raw.get("execution_head"),
        "finalizer_sha256": sha(repo / REL_RUNNER),
        "checker_verdict": "PASS",
        "promotion_status": "READY_FOR_JUDGE_PROMOTION",
        "judge_signature_status": "PENDING",
        "parent": raw.get("parent"),
        "parent_source": "MONOTONE_TUBE_V1_1_COMPONENT1_RECONSTRUCTED_AND_CHECKED",
        "cross_component_rectangle_identity":
            "REQUIRES_SAME_COMPONENT1_GEOMETRY_RECEIPT_SHA_IN_F_LAMBDA_AND_JOIN_RECEIPTS",
        "narrow_interface_candidate": {
            "ALL_TERMINAL_LO_POSITIVE": True,
            "UNION_EQUALS_PARENT": True,
            "CERTIFIED_COVER_MARGIN_EXACT": margin_text,
            "CERTIFIED_COVER_MARGIN_POSITIVE": True,
            "COVER_MARGIN_IS_TRUE_MINIMUM": False,
        },
        "source_tree_pre_clean": True,
        "source_tree_post_clean": True,
        "head_unchanged_during_run": True,
        "verdict": "CELL_PRODUCTION_HU_CHECKER_PASS_READY_FOR_JUDGE_PROMOTION",
    }

    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    print("PRODUCTION_CHECKER_VERDICT=PASS")
    print("CELL_ID=" + ns.cell_id)
    print("CELL_INDEX=" + str(ns.cell_index))
    print("COMPONENT1_GEOMETRY_RECEIPT_SHA256=" + geom_sha)
    print("BINDING_USE_AUTHORIZED=FALSE")
    print("PROMOTION_STATUS=READY_FOR_JUDGE_PROMOTION")
    print("PRODUCTION_RECEIPT_SHA256=" + sha(out_p))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
