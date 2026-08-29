#!/usr/bin/env python3
"""Cell-independent production checker for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

Unlike the frozen release checker, this checker has no positive-control result
SHA or positive-control execution-head pin.  It validates production attestation
provenance, released policy/producer pins, existence of the receipt execution
commit, and then delegates all finite-stage semantic reconstruction to the
shared checker core.

No numerical H_U reevaluation is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

RELEASE_TAG = "hu-domain-v1.2"
RELEASE_SHA = "6d705c6fbf37ae77d35232a40842692a3e92713e"
POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
PRODUCER_SHA256 = "e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
FROZEN_POSITIVE_CONTROL_CHECKER_SHA256 = "d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
CORE_SHA256 = "16a8ab78fef3cbd6754d17b015ea8b90059af1145beec8c5ca3316ca0d33f628"

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_PRODUCER = REL_DIR + "/hu_domain_v1_2_cell0_positive_control.py"
REL_FROZEN_CHECKER = REL_DIR + "/hu_domain_v1_2_independent_checker.py"
REL_CONTRACT = REL_DIR + "/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
REL_CORE = REL_DIR + "/hu_domain_v1_2_checker_core.py"


def fail(code: str) -> None:
    raise SystemExit("FAIL:" + code)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def commit_exists(repo: Path, commit: object) -> bool:
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        return False
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", commit + "^{commit}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--production-attestation", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    receipt_path = ns.receipt.expanduser().resolve()
    att_path = ns.production_attestation.expanduser().resolve()

    paths = {
        "policy": repo / REL_POLICY,
        "producer": repo / REL_PRODUCER,
        "frozen_checker": repo / REL_FROZEN_CHECKER,
        "contract": repo / REL_CONTRACT,
        "core": repo / REL_CORE,
        "receipt": receipt_path,
        "attestation": att_path,
    }
    for name, path in paths.items():
        if not path.is_file():
            fail("MISSING_" + name.upper())

    if git(repo, "rev-parse", RELEASE_TAG + "^{commit}") != RELEASE_SHA:
        fail("RELEASE_TAG_SHA_MISMATCH")
    if sha256_file(paths["policy"]) != POLICY_SHA256:
        fail("POLICY_SHA_MISMATCH")
    if sha256_file(paths["producer"]) != PRODUCER_SHA256:
        fail("PRODUCER_SHA_MISMATCH")
    if sha256_file(paths["frozen_checker"]) != FROZEN_POSITIVE_CONTROL_CHECKER_SHA256:
        fail("FROZEN_CHECKER_SHA_MISMATCH")
    if sha256_file(paths["core"]) != CORE_SHA256:
        fail("CORE_SHA_MISMATCH")

    contract = json.loads(paths["contract"].read_text())
    if contract.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("CONTRACT_ID")
    if contract.get("release_status") != "RELEASED_AFTER_POSITIVE_CONTROL_PASS":
        fail("RELEASE_STATUS")
    pins = contract.get("pins", {})
    if pins.get("stage_policy_sha256") != POLICY_SHA256:
        fail("CONTRACT_POLICY_PIN")
    if pins.get("producer_runner_sha256") != PRODUCER_SHA256:
        fail("CONTRACT_PRODUCER_PIN")
    if pins.get("independent_checker_sha256") != FROZEN_POSITIVE_CONTROL_CHECKER_SHA256:
        fail("CONTRACT_FROZEN_CHECKER_PIN")

    raw_sha = sha256_file(receipt_path)
    receipt = json.loads(receipt_path.read_text())
    att = json.loads(att_path.read_text())

    if att.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("ATTESTATION_CONTRACT_ID")
    if att.get("evidence_class") != "PRODUCTION_CANDIDATE":
        fail("ATTESTATION_EVIDENCE_CLASS")
    if att.get("binding_use_authorized") is not False:
        fail("ATTESTATION_BINDING_STATE")
    if att.get("positive_control_receipt_reused") is not False:
        fail("ATTESTATION_REUSE_FLAG")
    if att.get("fresh_reexecution") is not True:
        fail("ATTESTATION_FRESH_FLAG")
    if att.get("released_policy_sha256") != POLICY_SHA256:
        fail("ATTESTATION_POLICY_PIN")
    if att.get("released_producer_sha256") != PRODUCER_SHA256:
        fail("ATTESTATION_PRODUCER_PIN")
    if att.get("released_checker_sha256") != FROZEN_POSITIVE_CONTROL_CHECKER_SHA256:
        fail("ATTESTATION_FROZEN_CHECKER_PIN")
    if att.get("raw_result_sha256") != raw_sha:
        fail("ATTESTATION_RAW_SHA")
    if att.get("checker_status") != "PENDING":
        fail("ATTESTATION_CHECKER_STATUS")

    if receipt.get("policy_sha256") != POLICY_SHA256:
        fail("RECEIPT_POLICY_SHA")
    if receipt.get("runner_sha256") != PRODUCER_SHA256:
        fail("RECEIPT_PRODUCER_SHA")
    receipt_head = receipt.get("execution_head")
    if not commit_exists(repo, receipt_head):
        fail("RECEIPT_EXECUTION_HEAD_NOT_GIT_COMMIT")
    if att.get("producer_execution_head") != receipt_head:
        fail("ATTESTATION_PRODUCER_HEAD_MISMATCH")

    sys.path.insert(0, str(repo / REL_DIR))
    try:
        from hu_domain_v1_2_checker_core import ValidationError, validate_semantics
    except Exception as exc:
        fail("CORE_IMPORT:" + type(exc).__name__)

    policy = json.loads(paths["policy"].read_text())
    try:
        result = validate_semantics(policy, receipt)
    except ValidationError as exc:
        fail(str(exc))

    print("CHECKER_ID=PRODUCTION_HU_DOMAIN_V1_2_PRODUCTION_CHECKER_V1")
    print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE")
    print("NUMERICAL_REEVALUATION=NO")
    print("POSITIVE_CONTROL_RESULT_SHA_PIN=NONE")
    print("POSITIVE_CONTROL_EXECUTION_HEAD_PIN=NONE")
    print("POLICY_SHA256=" + POLICY_SHA256)
    print("PRODUCER_SHA256=" + PRODUCER_SHA256)
    print("CORE_SHA256=" + CORE_SHA256)
    print("RECEIPT_EXECUTION_HEAD_GIT_EXISTS=TRUE")
    print("STAGE_ORDER=PASS")
    print("FIRST_PASSING=PASS")
    print("RESOLVED_LEAF_IMMUTABLE=PASS")
    print("RAW_EVALUATED_BOX_ACCOUNTING=PASS")
    print("BUDGET_ACCOUNTING=PASS")
    print("EVALUATED_BOX_COUNT=" + str(result["evaluated_box_count"]))
    print("ABORT_COUNT=" + str(result["abort_count"]))
    print("TERMINAL_LEAF_COUNT=" + str(result["terminal_leaf_count"]))
    print("TOTAL_EVAL=" + str(result["total_eval"]))
    print("UNION_EQUALS_PARENT=TRUE")
    print("ALL_TERMINAL_LO_POSITIVE=TRUE")
    print("CERTIFIED_COVER_MARGIN_EXACT=" + result["margin_exact"])
    print("CERTIFIED_COVER_MARGIN_POSITIVE=TRUE")
    print("COVER_MARGIN_IS_TRUE_MINIMUM=NO")
    print("PRODUCTION_CHECKER_VERDICT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
