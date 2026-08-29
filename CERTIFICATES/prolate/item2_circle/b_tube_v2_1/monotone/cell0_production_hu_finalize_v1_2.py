#!/usr/bin/env python3
"""Finalize fresh cell-0 production H_U evidence after production-checker PASS.

Cell 0 additionally requires bit identity with the historical positive-control
raw result as a deterministic-replay cross-check.  That identity is cell-0
specific and is not a condition of the cell-independent production checker.

This finalizer never authorizes binding use.  It emits a PRODUCTION_CANDIDATE
receipt with CHECKER_PASS and READY_FOR_JUDGE_PROMOTION only.
"""
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
PRODUCER_SHA256 = "e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
FROZEN_POSITIVE_CONTROL_CHECKER_SHA256 = "d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
PRODUCTION_CHECKER_SHA256 = "34add1065baad6fbc35bfd557ccbdbc0de498b99762c984c3b902fc403e79f2d"
CHECKER_CORE_SHA256 = "16a8ab78fef3cbd6754d17b015ea8b90059af1145beec8c5ca3316ca0d33f628"
POSITIVE_CONTROL_RESULT_SHA256 = "f4f9320678aa14a8f7b169580d3b1783c4aacb48b73822b4647323d731650043"

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_PRODUCER = REL_DIR + "/hu_domain_v1_2_cell0_positive_control.py"
REL_FROZEN_CHECKER = REL_DIR + "/hu_domain_v1_2_independent_checker.py"
REL_PRODUCTION_CHECKER = REL_DIR + "/hu_domain_v1_2_production_checker.py"
REL_CORE = REL_DIR + "/hu_domain_v1_2_checker_core.py"
REL_CONTRACT = REL_DIR + "/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
REL_RUNNER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/cell0_production_hu_finalize_v1_2.py"


def fail(code: str) -> None:
    raise SystemExit("STOP:" + code)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_fraction(value: object, where: str) -> Fraction:
    if not isinstance(value, str):
        fail("BAD_FRACTION:" + where)
    try:
        q = Fraction(value)
    except Exception:
        fail("BAD_FRACTION:" + where)
    if value != f"{q.numerator}/{q.denominator}":
        fail("NONCANONICAL_FRACTION:" + where)
    return q


def require_files(repo: Path) -> None:
    if git(repo, "rev-parse", RELEASE_TAG + "^{commit}") != RELEASE_SHA:
        fail("RELEASE_TAG_SHA_MISMATCH")
    expected = {
        REL_POLICY: POLICY_SHA256,
        REL_PRODUCER: PRODUCER_SHA256,
        REL_FROZEN_CHECKER: FROZEN_POSITIVE_CONTROL_CHECKER_SHA256,
        REL_PRODUCTION_CHECKER: PRODUCTION_CHECKER_SHA256,
        REL_CORE: CHECKER_CORE_SHA256,
    }
    for relpath, expected_sha in expected.items():
        path = repo / relpath
        if not path.is_file() or sha256_file(path) != expected_sha:
            fail("FILE_SHA_MISMATCH:" + relpath)
    contract = json.loads((repo / REL_CONTRACT).read_text())
    if contract.get("release_status") != "RELEASED_AFTER_POSITIVE_CONTROL_PASS":
        fail("RELEASE_STATUS")
    pins = contract.get("pins", {})
    if pins.get("stage_policy_sha256") != POLICY_SHA256:
        fail("CONTRACT_POLICY_PIN")
    if pins.get("producer_runner_sha256") != PRODUCER_SHA256:
        fail("CONTRACT_PRODUCER_PIN")
    if pins.get("independent_checker_sha256") != FROZEN_POSITIVE_CONTROL_CHECKER_SHA256:
        fail("CONTRACT_FROZEN_CHECKER_PIN")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--raw-result", type=Path, required=True)
    ap.add_argument("--production-attestation", type=Path, required=True)
    ap.add_argument("--checker-log", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    raw_path = ns.raw_result.expanduser().resolve()
    att_path = ns.production_attestation.expanduser().resolve()
    checker_log = ns.checker_log.expanduser().resolve()
    out_json = ns.out_json.expanduser().resolve()

    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE_DIRTY")
    head = git(repo, "rev-parse", "HEAD")
    require_files(repo)
    if platform.python_version() != "3.13.14":
        fail("PYTHON_VERSION")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1" or not sys.dont_write_bytecode:
        fail("BYTECODE_SUPPRESSION")
    if not raw_path.is_file() or not att_path.is_file():
        fail("MISSING_INPUT")

    raw_sha = sha256_file(raw_path)
    bit_identical = raw_sha == POSITIVE_CONTROL_RESULT_SHA256
    if not bit_identical:
        fail("CELL0_DETERMINISM_CROSSCHECK_MISMATCH")

    att = json.loads(att_path.read_text())
    if att.get("evidence_class") != "PRODUCTION_CANDIDATE":
        fail("ATTESTATION_EVIDENCE_CLASS")
    if att.get("binding_use_authorized") is not False:
        fail("ATTESTATION_BINDING_STATE")
    if att.get("positive_control_receipt_reused") is not False:
        fail("ATTESTATION_REUSE_FLAG")
    if att.get("fresh_reexecution") is not True:
        fail("ATTESTATION_FRESH_FLAG")
    if att.get("raw_result_sha256") != raw_sha:
        fail("ATTESTATION_RAW_SHA")
    if att.get("bit_identical_to_positive_control") is not True:
        fail("ATTESTATION_BIT_IDENTITY")
    if att.get("checker_status") != "PENDING":
        fail("ATTESTATION_CHECKER_STATE")

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    checker_cmd = [
        sys.executable,
        str(repo / REL_PRODUCTION_CHECKER),
        "--repo", str(repo),
        "--receipt", str(raw_path),
        "--production-attestation", str(att_path),
    ]
    proc = subprocess.run(
        checker_cmd,
        cwd=repo,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    checker_log.parent.mkdir(parents=True, exist_ok=True)
    checker_log.write_text(proc.stdout)
    if proc.returncode != 0:
        fail("PRODUCTION_CHECKER_NONZERO")
    if "PRODUCTION_CHECKER_VERDICT=PASS" not in proc.stdout:
        fail("PRODUCTION_CHECKER_VERDICT_MISSING")

    raw = json.loads(raw_path.read_text())
    all_pos = raw.get("all_terminal_lo_positive") is True
    cover = raw.get("cover_checks", {})
    union_parent = cover.get("union_equals_parent") is True
    margin_text = raw.get("certified_cover_margin_exact")
    margin = parse_fraction(margin_text, "certified_cover_margin_exact")
    margin_positive = margin > 0
    if not all_pos:
        fail("ALL_TERMINAL_LO_POSITIVE_FALSE")
    if not union_parent:
        fail("UNION_EQUALS_PARENT_FALSE")
    if not margin_positive:
        fail("MARGIN_NONPOSITIVE")

    post_head = git(repo, "rev-parse", "HEAD")
    post_clean = not bool(git(repo, "status", "--porcelain"))
    head_unchanged = post_head == head
    if not head_unchanged:
        fail("HEAD_CHANGED_DURING_RUN")
    if not post_clean:
        fail("SOURCE_TREE_POST_DIRTY")

    checker_log_sha = sha256_file(checker_log)
    receipt = {
        "schema": "production-hu-domain-v1.2-cell0-production-receipt-v2",
        "contract_id": "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2",
        "evidence_class": "PRODUCTION_CANDIDATE",
        "binding_use_authorized": False,
        "release_sha": RELEASE_SHA,
        "release_tag": RELEASE_TAG,
        "released_policy_sha256": POLICY_SHA256,
        "released_producer_sha256": PRODUCER_SHA256,
        "frozen_positive_control_checker_sha256": FROZEN_POSITIVE_CONTROL_CHECKER_SHA256,
        "production_checker_sha256": PRODUCTION_CHECKER_SHA256,
        "checker_core_sha256": CHECKER_CORE_SHA256,
        "execution_head": head,
        "finalizer_sha256": sha256_file(repo / REL_RUNNER),
        "production_attestation_sha256": sha256_file(att_path),
        "raw_result_sha256": raw_sha,
        "checker_log_sha256": checker_log_sha,
        "checker_verdict": "PASS",
        "promotion_status": "READY_FOR_JUDGE_PROMOTION",
        "judge_signature_status": "PENDING",
        "positive_control_receipt_reused": False,
        "fresh_reexecution": True,
        "cell0_determinism_crosscheck": {
            "reference_sha256": POSITIVE_CONTROL_RESULT_SHA256,
            "bit_identical": bit_identical,
            "role": "CELL0_ONLY_REPRODUCIBILITY_CROSSCHECK_NOT_PRODUCTION_CHECKER_CONDITION",
        },
        "parent": raw.get("parent"),
        "lambda_start_in_parent": raw.get("parent", {}).get("lambda_lo") == "3307749/1600000",
        "narrow_interface_candidate": {
            "ALL_TERMINAL_LO_POSITIVE": all_pos,
            "UNION_EQUALS_PARENT": union_parent,
            "CERTIFIED_COVER_MARGIN_EXACT": margin_text,
            "CERTIFIED_COVER_MARGIN_POSITIVE": margin_positive,
            "COVER_MARGIN_IS_TRUE_MINIMUM": False,
        },
        "monotone_narrow_interface_authorized": False,
        "source_tree_pre_clean": True,
        "source_tree_post_clean": post_clean,
        "head_unchanged_during_run": head_unchanged,
        "verdict": "CELL0_PRODUCTION_HU_CHECKER_PASS_READY_FOR_JUDGE_PROMOTION",
    }
    if receipt["lambda_start_in_parent"] is not True:
        fail("LAMBDA_START_NOT_PARENT_ENDPOINT")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    print("CONTRACT_ID=PRODUCTION_HU_DOMAIN_CONTRACT_V1_2")
    print("EVIDENCE_CLASS=PRODUCTION_CANDIDATE")
    print("PRODUCTION_CHECKER_SHA256=" + PRODUCTION_CHECKER_SHA256)
    print("PRODUCTION_CHECKER_VERDICT=PASS")
    print("ALL_TERMINAL_LO_POSITIVE=TRUE")
    print("UNION_EQUALS_PARENT=TRUE")
    print("CERTIFIED_COVER_MARGIN_EXACT=" + margin_text)
    print("CERTIFIED_COVER_MARGIN_POSITIVE=TRUE")
    print("CELL0_DETERMINISM_CROSSCHECK=PASS")
    print("LAMBDA_START_IN_PARENT=TRUE")
    print("BINDING_USE_AUTHORIZED=FALSE")
    print("MONOTONE_NARROW_INTERFACE_AUTHORIZED=FALSE")
    print("PROMOTION_STATUS=READY_FOR_JUDGE_PROMOTION")
    print("JUDGE_SIGNATURE_STATUS=PENDING")
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=CELL0_PRODUCTION_HU_CHECKER_PASS_READY_FOR_JUDGE_PROMOTION")
    print("PRODUCTION_RECEIPT=" + str(out_json))
    print("PRODUCTION_RECEIPT_SHA256=" + sha256_file(out_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
