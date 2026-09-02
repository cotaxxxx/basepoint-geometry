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
RECEIPT = HERE / "F_LAMBDA_NC11_UNRESOLVED_GATE_RUN_V1.json"

CONTROL_ID = "NC11"
CONTRACT_EXPECTED_CODE = "FAIL_UNRESOLVED"
EXPECTED_REASON = "ANGULAR_EVALUATION_BUDGET"
METHOD = "TINY_CAP_NATIVE_ROUTE_GATE"
EVALUATION_CAP = 1

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
        ["git", *args], cwd=ROOT, text=True
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

import blocal_v22_model as model
import blocal_arb_adapter as adapter
import blocal_v23_boundary as route
import calibration_runner
from flint import arb, acb, fmpq, ctx

cal, _ = calibration_runner.load_config()
ctx.dps = cal["dps"]
raw_kernel, _ = calibration_runner.load_production_kernel()

bcfg = json.loads((V23 / "config.blocal-v2.2-run.json").read_text())
frag = json.loads((V23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
bcfg["route_policies"].update(frag["route_policies"])

# Exact existing replay cell: R_HI x C0.
r_hi = Fraction(77359446546029624093969931, 1 << 86)
u = Fraction(1) - r_hi
lam0 = Fraction(3307749, 1600000)
llo = lam0
lhi = lam0 + Fraction(1, 16)
s0 = llo - model.LAMBDA_PLUS
s1 = lhi - model.LAMBDA_PLUS

observed_reason = None
observed_evaluations = None

try:
    route.enclose_route(
        "F_lambda",
        raw_kernel,
        adapter,
        acb,
        arb,
        fmpq,
        bcfg,
        u,
        u,
        s0,
        s1,
        required_sign="NEG",
        accept=None,
        evaluation_cap=EVALUATION_CAP,
    )
except route.base.EnclosureFailure as exc:
    observed_reason = exc.reason
    observed_evaluations = getattr(exc, "evaluations", None)
    assert observed_reason == EXPECTED_REASON, (
        EXPECTED_REASON,
        observed_reason,
    )
else:
    raise AssertionError(
        f"expected EnclosureFailure {EXPECTED_REASON}"
    )

print("NC11_TINY_CAP_NATIVE_GATE=PASS")
print("CONTRACT_EXPECTED_CODE=FAIL_UNRESOLVED")
print("OBSERVED_ROUTE_REASON=" + str(observed_reason))
print("DECLARED_EVALUATION_CAP=1")
print("NUMERICAL_EVALUATOR_CALLED=TRUE")
print("END_TO_END_CLAIM=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")

head_post = git("rev-parse", "HEAD")
status_post = git("status", "--porcelain")

assert head_post == head_pre
assert status_post == ""

receipt = {
    "schema": "flambda-nc11-unresolved-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "contract_expected_code": CONTRACT_EXPECTED_CODE,
    "implementation_subcode": EXPECTED_REASON,
    "subcode_mapping_predeclared": True,
    "native_call": {
        "quantity": "F_lambda",
        "required_sign": "NEG",
        "accept": None,
        "evaluation_cap": EVALUATION_CAP,
        "cell": "R_HI/C0",
        "r": str(r_hi),
        "lambda_lo": str(llo),
        "lambda_hi": str(lhi),
    },
    "observed_route_reason": observed_reason,
    "observed_evaluations_at_failure": observed_evaluations,
    "execution_head": head_pre,
    "boundary_sha256": sha256(BOUNDARY),
    "native_replay_sha256": sha256(REPLAY),
    "gate_harness_sha256": sha256(HARNESS),
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__)),
    "harness_exit_code": 0,
    "needs_numerics": True,
    "numerical_arguments_dereferenced": True,
    "numerical_evaluator_called": True,
    "dynamic_failure_path_executed": True,
    "end_to_end": False,
    "canonical_control_execution_claim": False,
    "boundary_modified": False,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "binding_use_authorized": False,
    "verdict": "NC11_EXACT_SUBCODE_PASS_NOT_PROMOTED",
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n"
)

print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print("VERDICT=NC11_EXACT_SUBCODE_PASS_NOT_PROMOTED")
