#!/usr/bin/env python3
"""Dedicated deterministic NC05 lambda-gap dry-precheck runner.

Executes the frozen historical checker's exact lambda-geometry
reconstruction predicate with a synthetic exact-rational gap between
adjacent producer-supplied lambda tiles.

No numerical evaluator is constructed or called.
"""

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
BASE = HERE.parent
CHECKER = BASE / "flambda_transport_checker_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC05_LAMBDA_GAP_GATE_RUN_V1.json"

EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)
CONTROL_ID = "NC05"
EXPECTED_CODE = "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION"
METHOD = "REAL_CHECKER_LAMBDA_GEOMETRY_DRY_PRECHECK_EXACT_GAP"
VERDICT = "NC05_EXACT_GAP_SUBCODE_PASS_NOT_PROMOTED"


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
        "flambda_checker_nc05",
        CHECKER,
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def fj(x: Fraction) -> dict[str, str]:
    return {"p": str(x.numerator), "q": str(x.denominator)}


assert os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"
assert sha256(CHECKER) == EXPECTED_CHECKER_SHA256
assert not RECEIPT.exists()

head_pre = git("rev-parse", "HEAD")
status_pre = git("status", "--porcelain")
assert status_pre == "", status_pre

checker = load_checker()

# Minimal exact geometry chosen so reconstruction requires two adjacent
# FLAMBDA_BASE_TILE tiles:
#
# parent = [0, 1/8]
# base tile = 1/16
# expected tiles = [0,1/16], [1/16,1/8]
#
# NC05 removes the exact rational interval (1/32, 1/16) from coverage by
# moving only the first tile's right endpoint from 1/16 to 1/32.
config = {
    "max_cells": 1,
    "blocal_dependency": {
        "lambda_start": {"p": "0", "q": "1"},
    },
    "lambda_end": {"p": "1", "q": "8"},
}

nominal_width = checker.Dyadic(1, -3)

positive = {
    "cell_index": 0,
    "candidate_parent": {
        "lo": fj(Fraction(0, 1)),
        "hi": fj(Fraction(1, 8)),
    },
    "base_tile": fj(Fraction(1, 16)),
    "tiles": [
        {
            "lo": fj(Fraction(0, 1)),
            "hi": fj(Fraction(1, 16)),
        },
        {
            "lo": fj(Fraction(1, 16)),
            "hi": fj(Fraction(1, 8)),
        },
    ],
}

observed = checker._reconstruct_lambda_geometry(
    positive,
    config,
    nominal_width,
)
assert observed["lambda_left"] == Fraction(0, 1)
assert observed["lambda_right"] == Fraction(1, 8)
assert observed["tiles"] == [
    (Fraction(0, 1), Fraction(1, 16)),
    (Fraction(1, 16), Fraction(1, 8)),
]

mutated = {
    **positive,
    "tiles": [
        {
            "lo": fj(Fraction(0, 1)),
            "hi": fj(Fraction(1, 32)),
        },
        {
            "lo": fj(Fraction(1, 16)),
            "hi": fj(Fraction(1, 8)),
        },
    ],
}

try:
    checker._reconstruct_lambda_geometry(
        mutated,
        config,
        nominal_width,
    )
except checker.CheckerFailure as exc:
    observed_code = exc.code
    observed_detail = exc.detail
else:
    raise AssertionError(f"expected failure {EXPECTED_CODE}")

assert observed_code == EXPECTED_CODE, (EXPECTED_CODE, observed_code)

head_post = git("rev-parse", "HEAD")
status_post = git("status", "--porcelain")
assert head_post == head_pre
assert status_post == ""

receipt = {
    "schema": "flambda-nc05-lambda-gap-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "mutation": "PRODUCER_GEOMETRY:lambda_gap",
    "expected_exact_code": EXPECTED_CODE,
    "observed_exact_code": observed_code,
    "observed_detail": observed_detail,
    "gap": {
        "lo": "1/32",
        "hi": "1/16",
        "width": "1/32",
        "property": "exact_rational_portion_removed_between_adjacent_lambda_tiles",
    },
    "positive_parent": {
        "lo": "0",
        "hi": "1/8",
        "base_tile": "1/16",
        "tile_count": 2,
    },
    "execution_head": head_pre,
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__)),
    "needs_numerics": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "historical_checker_lambda_geometry_called": True,
    "end_to_end": False,
    "canonical_control_execution_claim": True,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "binding_use_authorized": False,
    "verdict": VERDICT,
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(f"CONTROL_ID={CONTROL_ID}")
print(f"METHOD={METHOD}")
print(f"EXPECTED_EXACT_CODE={EXPECTED_CODE}")
print(f"OBSERVED_EXACT_CODE={observed_code}")
print("MUTATION=PRODUCER_GEOMETRY:lambda_gap")
print("GAP=(1/32,1/16)")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=TRUE")
print("HISTORICAL_CHECKER_LAMBDA_GEOMETRY_CALLED=TRUE")
print("END_TO_END_CLAIM=FALSE")
print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print(f"VERDICT={VERDICT}")
