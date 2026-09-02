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
CHECKER = HERE.parent / "flambda_transport_checker_v1.py"
HARNESS = HERE / "flambda_gate_unit_harness_v1_11.py"
RECEIPT = HERE / "F_LAMBDA_NC15A_ANCHOR_SIGN_NEG_GATE_RUN_V1.json"

CONTROL_ID = "NC15a"
EXPECTED_CODE = "FAIL_ANCHOR_SIGN_NEG"
METHOD = "SYNTHETIC_EVALUATOR_REAL_CHECKER_FUNCTION"

EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)
EXPECTED_HARNESS_SHA256 = (
    "4b090292d8f82c59033201c22012e92b0ce45d35b19c58b0f95b280b02f60ac0"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
    ).strip()


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "flambda_checker_nc15a", CHECKER
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def expect_checker_failure(fn, expected_code: str) -> None:
    try:
        fn()
    except Exception as exc:
        code = getattr(exc, "code", None)
        assert code == expected_code, (expected_code, code, repr(exc))
    else:
        raise AssertionError(f"expected failure {expected_code}")


assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
assert sha256(CHECKER) == EXPECTED_CHECKER_SHA256
assert sha256(HARNESS) == EXPECTED_HARNESS_SHA256
assert not RECEIPT.exists()

head_pre = git("rev-parse", "HEAD")
status_pre = git("status", "--porcelain")
assert status_pre == "", status_pre

checker = load_checker()


class NC15aInterval:
    lo = checker.Dyadic.from_fraction(Fraction(1))
    hi = checker.Dyadic.from_fraction(Fraction(2))

    @classmethod
    def to_json(cls):
        return {
            "lo": cls.lo.to_json(),
            "hi": cls.hi.to_json(),
            "synthetic": "nc15a",
        }


class NC15aEvaluator:
    @staticmethod
    def _evaluate_exact(*args, **kwargs):
        evidence = {
            "quantity": "F",
            "post_failure_fallback": False,
            "boundary_route_evaluation_count_delta": 0,
            "detail": "synthetic_no_numerics",
        }
        return None, NC15aInterval(), evidence


expect_checker_failure(
    lambda: checker._anchor_check(
        evaluator=NC15aEvaluator(),
        endpoint=checker.Dyadic(0, 0),
        lam=Fraction(1, 2),
        required_sign="NEG",
        config={
            "max_subdivisions": 1,
            "evaluation_budget": 1,
        },
    ),
    EXPECTED_CODE,
)

print("NC15a_DIRECT_GATE=PASS")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("END_TO_END_CLAIM=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")

head_post = git("rev-parse", "HEAD")
status_post = git("status", "--porcelain")
assert head_post == head_pre
assert status_post == ""

receipt = {
    "schema": "flambda-nc15a-anchor-sign-neg-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "expected_exact_code": EXPECTED_CODE,
    "synthetic_enclosure": "violates_NEG",
    "execution_head": head_pre,
    "historical_checker_sha256": sha256(CHECKER),
    "gate_harness_sha256": sha256(HARNESS),
    "run_source_sha256": sha256(Path(__file__)),
    "harness_exit_code": 0,
    "needs_numerics": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "end_to_end": False,
    "canonical_control_execution_claim": False,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "binding_use_authorized": False,
    "verdict": "NC15a_EXACT_SUBCODE_PASS_NOT_PROMOTED",
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)

print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print("VERDICT=NC15a_EXACT_SUBCODE_PASS_NOT_PROMOTED")
