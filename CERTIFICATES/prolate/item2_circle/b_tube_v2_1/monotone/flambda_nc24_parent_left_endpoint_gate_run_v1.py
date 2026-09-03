#!/usr/bin/env python3
"""Dedicated deterministic NC24 parent-left-endpoint gate runner.

No numerical evaluator is called.  The canonical NC24 mutation changes only
producer candidate_parent.lo away from the exact lambda_left reconstructed
from config lambda_start, cell_index, and nominal_width.  The mutated geometry
is passed to the real historical checker _reconstruct_lambda_geometry.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
CHECKER = BASE / "flambda_transport_checker_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC24_PARENT_LEFT_ENDPOINT_GATE_RUN_V1.json"

EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)
CONTROL_ID = "NC24"
METHOD = "REAL_CHECKER_LAMBDA_GEOMETRY_DRY_PRECHECK_PARENT_LEFT_ENDPOINT"
EXPECTED_EXACT_CODE = "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION"
MUTATION = "PRODUCER_GEOMETRY:parent_left_endpoint"
VERDICT = "NC24_PARENT_LEFT_ENDPOINT_SUBCODE_PASS_NOT_PROMOTED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fj(x: Fraction) -> dict[str, str]:
    return {"p": str(x.numerator), "q": str(x.denominator)}


repo = subprocess.check_output(
    ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
    text=True,
).strip()

head_pre = subprocess.check_output(
    ["git", "-C", repo, "rev-parse", "HEAD"],
    text=True,
).strip()
status_pre = subprocess.check_output(
    ["git", "-C", repo, "status", "--porcelain"],
    text=True,
).strip()

if status_pre:
    raise SystemExit("STOP: source tree must be clean before NC24 execution")
if RECEIPT.exists():
    raise SystemExit("STOP: NC24 receipt already exists")
if sha256(CHECKER) != EXPECTED_CHECKER_SHA256:
    raise SystemExit("STOP: historical checker SHA mismatch")

spec = importlib.util.spec_from_file_location("nc24_historical_checker", CHECKER)
if spec is None or spec.loader is None:
    raise SystemExit("STOP: cannot load historical checker")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# Exact synthetic geometry chosen only to exercise the frozen reconstruction
# predicate.  lambda_start=0, nominal_width=1/8, cell_index=0 gives the exact
# reconstructed parent [0, 1/8], tiled by two frozen 1/16 base tiles.
config = {
    "blocal_dependency": {
        "lambda_start": fj(Fraction(0, 1)),
    },
    "lambda_end": fj(Fraction(1, 4)),
    "max_cells": 2,
}
nominal_width = checker.Dyadic(1, 3)

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

# Positive geometry must pass the real historical reconstruction.
geometry = checker._reconstruct_lambda_geometry(
    positive,
    config,
    nominal_width,
)
if geometry["lambda_left"] != Fraction(0, 1):
    raise SystemExit("STOP: unexpected positive lambda_left")
if geometry["lambda_right"] != Fraction(1, 8):
    raise SystemExit("STOP: unexpected positive lambda_right")

# Canonical NC24 mutation: candidate_parent.lo only.
# All tiles, parent-hi, base tile, config, cell index, and width stay unchanged.
mutated = json.loads(json.dumps(positive))
mutated["candidate_parent"]["lo"] = fj(Fraction(1, 32))

observed = None
observed_detail = None
try:
    checker._reconstruct_lambda_geometry(
        mutated,
        config,
        nominal_width,
    )
except checker.CheckerFailure as exc:
    observed = str(exc)
    observed_detail = getattr(exc, "detail", None)

if observed != EXPECTED_EXACT_CODE:
    raise SystemExit(
        f"STOP: expected {EXPECTED_EXACT_CODE}, observed {observed!r}"
    )

head_post = subprocess.check_output(
    ["git", "-C", repo, "rev-parse", "HEAD"],
    text=True,
).strip()
status_post = subprocess.check_output(
    ["git", "-C", repo, "status", "--porcelain"],
    text=True,
).strip()

if head_post != head_pre:
    raise SystemExit("STOP: HEAD changed during NC24 run")
if status_post:
    raise SystemExit("STOP: source tree changed during NC24 run")

receipt = {
    "schema": "flambda-nc24-parent-left-endpoint-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "mutation": MUTATION,
    "expected_exact_code": EXPECTED_EXACT_CODE,
    "observed_exact_code": observed,
    "observed_detail": observed_detail,
    "execution_head": head_pre,
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__).resolve()),
    "positive_parent": {
        "lo": "0",
        "hi": "1/8",
    },
    "mutated_parent": {
        "lo": "1/32",
        "hi": "1/8",
    },
    "reconstructed_lambda_left": "0",
    "left_endpoint_displacement": "1/32",
    "parent_hi_unchanged": True,
    "tiles_unchanged": True,
    "base_tile_unchanged": True,
    "cell_index_unchanged": True,
    "needs_numerics": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "historical_checker_lambda_geometry_called": True,
    "canonical_control_execution_claim": True,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "end_to_end": False,
    "binding_use_authorized": False,
    "verdict": VERDICT,
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(f"CONTROL_ID={CONTROL_ID}")
print(f"METHOD={METHOD}")
print(f"EXPECTED_EXACT_CODE={EXPECTED_EXACT_CODE}")
print(f"OBSERVED_EXACT_CODE={observed}")
print(f"MUTATION={MUTATION}")
print("RECONSTRUCTED_LAMBDA_LEFT=0")
print("POSITIVE_PARENT_LO=0")
print("MUTATED_PARENT_LO=1/32")
print("PARENT_HI_UNCHANGED=TRUE")
print("TILES_UNCHANGED=TRUE")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=TRUE")
print("HISTORICAL_CHECKER_LAMBDA_GEOMETRY_CALLED=TRUE")
print("END_TO_END_CLAIM=FALSE")
print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print(f"VERDICT={VERDICT}")
