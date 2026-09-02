#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BASE = HERE.parent
V23 = BASE / "dependencies/blocal_v23_source"

BOUNDARY = V23 / "blocal_v23_boundary.py"
REPLAY = BASE / "diagnostics/blocal_v23_native_flambda_replay.py"
HARNESS = HERE / "flambda_gate_unit_harness_v1_11.py"
CHECKER = BASE / "flambda_transport_checker_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC32_REQUIRED_SIGN_MISSING_GATE_RUN_V1.json"

CONTROL_ID = "NC32"
EXPECTED_CODE = "FAIL_REQUIRED_SIGN_MISSING"
METHOD = "DIRECT_EXISTING_NATIVE_REPLAY_GATE"

EXPECTED_BOUNDARY_SHA256 = (
    "8aa6647cc93026afee113cc2435fd7af858c93dc17fd1c79a5db2754f246218c"
)
EXPECTED_REPLAY_SHA256 = (
    "ad4844aa4fc005453c0846f132689e5d6c77de4362ee5b27eae390ef9f581613"
)
EXPECTED_HARNESS_SHA256 = (
    "4b090292d8f82c59033201c22012e92b0ce45d35b19c58b0f95b280b02f60ac0"
)
EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
    ).strip()


assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
assert sha256(BOUNDARY) == EXPECTED_BOUNDARY_SHA256
assert sha256(REPLAY) == EXPECTED_REPLAY_SHA256
assert sha256(HARNESS) == EXPECTED_HARNESS_SHA256
assert sha256(CHECKER) == EXPECTED_CHECKER_SHA256
assert not RECEIPT.exists()

head_pre = git("rev-parse", "HEAD")
status_pre = git("status", "--porcelain")
assert status_pre == "", status_pre

sys.path.insert(0, str(V23))
sys.path.insert(1, str(BASE))

import blocal_v23_boundary as route

try:
    route.enclose_route(
        "F_lambda",
        None, None, None, None, None, None,
        Fraction(0), Fraction(0),
        Fraction(0), Fraction(0),
        required_sign=None,
        accept=None,
        evaluation_cap=24000,
    )
except route.ContractFailure as exc:
    assert exc.code == EXPECTED_CODE, (EXPECTED_CODE, exc.code)
else:
    raise AssertionError(f"expected failure {EXPECTED_CODE}")

print("NC32_DIRECT_NATIVE_GATE=PASS")
print("EXPECTED_EXACT_CODE=FAIL_REQUIRED_SIGN_MISSING")
print("NUMERICAL_ARGUMENTS_DEREFERENCED=FALSE")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("END_TO_END_CLAIM=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")

head_post = git("rev-parse", "HEAD")
status_post = git("status", "--porcelain")

assert head_post == head_pre
assert status_post == ""

receipt = {
    "schema": "flambda-nc32-required-sign-missing-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "expected_exact_code": EXPECTED_CODE,
    "native_call": {
        "quantity": "F_lambda",
        "required_sign": None,
        "accept": None,
    },
    "execution_head": head_pre,
    "boundary_sha256": sha256(BOUNDARY),
    "native_replay_sha256": sha256(REPLAY),
    "gate_harness_sha256": sha256(HARNESS),
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__)),
    "harness_exit_code": 0,
    "needs_numerics": False,
    "numerical_arguments_dereferenced": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "end_to_end": False,
    "canonical_control_execution_claim": False,
    "boundary_modified": False,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "binding_use_authorized": False,
    "verdict": "NC32_EXACT_SUBCODE_PASS_NOT_PROMOTED",
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)

print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print("VERDICT=NC32_EXACT_SUBCODE_PASS_NOT_PROMOTED")
