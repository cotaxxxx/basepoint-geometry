#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PRODUCER = HERE.parent / "flambda_transport_producer_v1.py"
HARNESS = HERE / "flambda_gate_unit_harness_v1_11.py"
CHECKER = HERE.parent / "flambda_transport_checker_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC21_PARENT_WIDTH_GATE_RUN_V1.json"

CONTROL_ID = "NC21"
EXPECTED_CODE = "FAIL_PARENT_WIDTH"
METHOD = "PRODUCER_SIDE_EXACT_GATE"

EXPECTED_PRODUCER_SHA256 = (
    "f1b77313f29694765494d12e3edd043651162989758c9cecf8a00ef152f1776f"
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


def load_producer():
    spec = importlib.util.spec_from_file_location(
        "flambda_producer_nc21", PRODUCER
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
assert sha256(PRODUCER) == EXPECTED_PRODUCER_SHA256
assert sha256(HARNESS) == EXPECTED_HARNESS_SHA256
assert sha256(CHECKER) == EXPECTED_CHECKER_SHA256
assert not RECEIPT.exists()

head_pre = git("rev-parse", "HEAD")
status_pre = git("status", "--porcelain")
assert status_pre == "", status_pre

producer = load_producer()

try:
    producer._residual_tiling(Fraction(1, 2), Fraction(1, 2))
except producer.ProducerFailure as exc:
    assert exc.code == EXPECTED_CODE, (EXPECTED_CODE, exc.code)
else:
    raise AssertionError(f"expected failure {EXPECTED_CODE}")

print("NC21_PRODUCER_SIDE_EXACT_GATE=PASS")
print("EXPECTED_EXACT_CODE=FAIL_PARENT_WIDTH")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("END_TO_END_CLAIM=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")

head_post = git("rev-parse", "HEAD")
status_post = git("status", "--porcelain")

assert head_post == head_pre
assert status_post == ""

receipt = {
    "schema": "flambda-nc21-parent-width-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "expected_exact_code": EXPECTED_CODE,
    "synthetic_parent": {
        "lo": "1/2",
        "hi": "1/2",
        "property": "nonpositive_parent_width",
    },
    "execution_head": head_pre,
    "producer_source_sha256": sha256(PRODUCER),
    "gate_harness_sha256": sha256(HARNESS),
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__)),
    "harness_exit_code": 0,
    "needs_numerics": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "end_to_end": False,
    "canonical_control_execution_claim": False,
    "producer_modified": False,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "binding_use_authorized": False,
    "verdict": "NC21_EXACT_SUBCODE_PASS_NOT_PROMOTED",
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)

print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print("VERDICT=NC21_EXACT_SUBCODE_PASS_NOT_PROMOTED")
