#!/usr/bin/env python3
"""Dedicated deterministic NC26 residual-tiling gate runner.

No numerical evaluator is called.  Six canonical NC26 producer-geometry
mutations are passed independently to the real historical checker
_reconstruct_lambda_geometry.  Each must trigger the frozen exact subcode
FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION.
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
RECEIPT = HERE / "F_LAMBDA_NC26_RESIDUAL_TILING_GATE_RUN_V1.json"

EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)
CONTROL_ID = "NC26"
METHOD = "REAL_CHECKER_LAMBDA_GEOMETRY_DRY_PRECHECK_RESIDUAL_SUBCASES"
EXPECTED_EXACT_CODE = "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION"
VERDICT = "NC26_RESIDUAL_TILING_SUBCODES_PASS_NOT_PROMOTED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fj(x: Fraction) -> dict[str, str]:
    return {"p": str(x.numerator), "q": str(x.denominator)}


def tile(lo: Fraction, hi: Fraction) -> dict[str, dict[str, str]]:
    return {"lo": fj(lo), "hi": fj(hi)}


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
    raise SystemExit("STOP: source tree must be clean before NC26 execution")
if RECEIPT.exists():
    raise SystemExit("STOP: NC26 receipt already exists")
if sha256(CHECKER) != EXPECTED_CHECKER_SHA256:
    raise SystemExit("STOP: historical checker SHA mismatch")

spec = importlib.util.spec_from_file_location("nc26_historical_checker", CHECKER)
if spec is None or spec.loader is None:
    raise SystemExit("STOP: cannot load historical checker")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# Exact parent [0,5/32].
# With frozen base tile 1/16, exact reconstruction is:
# [0,1/16], [1/16,1/8], [1/8,5/32].
# The final 1/32 tile is the unique residual.
config = {
    "blocal_dependency": {
        "lambda_start": fj(Fraction(0, 1)),
    },
    "lambda_end": fj(Fraction(5, 32)),
    "max_cells": 1,
}
nominal_width = checker.Dyadic(5, 5)  # 5/32

positive = {
    "cell_index": 0,
    "candidate_parent": {
        "lo": fj(Fraction(0, 1)),
        "hi": fj(Fraction(5, 32)),
    },
    "base_tile": fj(Fraction(1, 16)),
    "tiles": [
        tile(Fraction(0, 1), Fraction(1, 16)),
        tile(Fraction(1, 16), Fraction(1, 8)),
        tile(Fraction(1, 8), Fraction(5, 32)),
    ],
}

geometry = checker._reconstruct_lambda_geometry(
    positive,
    config,
    nominal_width,
)
if geometry["lambda_left"] != Fraction(0, 1):
    raise SystemExit("STOP: unexpected positive lambda_left")
if geometry["lambda_right"] != Fraction(5, 32):
    raise SystemExit("STOP: unexpected positive lambda_right")
if geometry["tiles"] != [
    (Fraction(0, 1), Fraction(1, 16)),
    (Fraction(1, 16), Fraction(1, 8)),
    (Fraction(1, 8), Fraction(5, 32)),
]:
    raise SystemExit("STOP: unexpected positive exact tiling")

mutations = {}

# NC26a: omit the unique residual tile.
m = json.loads(json.dumps(positive))
m["tiles"] = m["tiles"][:-1]
mutations["NC26a"] = ("PRODUCER_GEOMETRY:residual_omitted", m)

# NC26b: duplicate the residual tile.
m = json.loads(json.dumps(positive))
m["tiles"].append(json.loads(json.dumps(m["tiles"][-1])))
mutations["NC26b"] = ("PRODUCER_GEOMETRY:residual_duplicated", m)

# NC26c: place the residual before a full-width tile, so it is non-final.
m = json.loads(json.dumps(positive))
m["tiles"] = [m["tiles"][0], m["tiles"][2], m["tiles"][1]]
mutations["NC26c"] = ("PRODUCER_GEOMETRY:residual_non_final", m)

# NC26d: residual width is nonpositive (zero width).
m = json.loads(json.dumps(positive))
m["tiles"][-1]["hi"] = fj(Fraction(1, 8))
mutations["NC26d"] = ("PRODUCER_GEOMETRY:residual_width_nonpositive", m)

# NC26e: residual width exceeds frozen base width 1/16.
m = json.loads(json.dumps(positive))
m["tiles"][-1]["hi"] = fj(Fraction(7, 32))
mutations["NC26e"] = ("PRODUCER_GEOMETRY:residual_width_too_wide", m)

# NC26f: final residual endpoint does not equal the parent endpoint.
m = json.loads(json.dumps(positive))
m["tiles"][-1]["hi"] = fj(Fraction(3, 16))
mutations["NC26f"] = (
    "PRODUCER_GEOMETRY:residual_final_endpoint_mismatch",
    m,
)

results = {}
for subcase, (mutation_name, mutated) in mutations.items():
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
            f"STOP: {subcase} expected {EXPECTED_EXACT_CODE}, "
            f"observed {observed!r}"
        )

    results[subcase] = {
        "mutation": mutation_name,
        "expected_exact_code": EXPECTED_EXACT_CODE,
        "observed_exact_code": observed,
        "observed_detail": observed_detail,
    }

head_post = subprocess.check_output(
    ["git", "-C", repo, "rev-parse", "HEAD"],
    text=True,
).strip()
status_post = subprocess.check_output(
    ["git", "-C", repo, "status", "--porcelain"],
    text=True,
).strip()

if head_post != head_pre:
    raise SystemExit("STOP: HEAD changed during NC26 run")
if status_post:
    raise SystemExit("STOP: source tree changed during NC26 run")

receipt = {
    "schema": "flambda-nc26-residual-tiling-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "expected_exact_code": EXPECTED_EXACT_CODE,
    "execution_head": head_pre,
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__).resolve()),
    "positive_parent": {
        "lo": "0",
        "hi": "5/32",
    },
    "positive_tiles": [
        ["0", "1/16"],
        ["1/16", "1/8"],
        ["1/8", "5/32"],
    ],
    "residual_width": "1/32",
    "subcases": results,
    "all_six_canonical_subcases_executed": True,
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
for subcase in ("NC26a", "NC26b", "NC26c", "NC26d", "NC26e", "NC26f"):
    r = results[subcase]
    print(
        f"{subcase}={r['mutation']} "
        f"OBSERVED={r['observed_exact_code']}"
    )
print("ALL_SIX_CANONICAL_SUBCASES_EXECUTED=TRUE")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=TRUE")
print("HISTORICAL_CHECKER_LAMBDA_GEOMETRY_CALLED=TRUE")
print("END_TO_END_CLAIM=FALSE")
print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print(f"VERDICT={VERDICT}")
