#!/usr/bin/env python3
"""Dedicated deterministic NC04b predictor-input-pin gate.

This is F_LAMBDA_CONTRACT_V1.1 preexecution infrastructure.

Scope:
- verify the frozen A0B cell-0 predictor-input pin receipt;
- compare candidate q_left/q_right exactly against that pin;
- emit FAIL_PREDICTOR_INPUT_PIN on either exact mismatch;
- exercise q_left and q_right mutations independently.

Nonclaims:
- not the historical F_LAMBDA checker;
- no numerical F or F_lambda evaluation;
- no transport theorem assembly;
- no binding promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]

PIN_PATH = HERE / "A0B_CELL0_PREDICTOR_INPUT_PIN_V1.json"

PIN_SHA256 = (
    "e76380c45f30dbe84a002ced1778415965340ed084796996180f52bbeca2cc2e"
)
COMPONENT1_SHA256 = (
    "f60c22cbc1d4a45e5593a64e64194f7e3dbc97df69e1547aca092d2d93b7911f"
)
A0B_START_ANCHORS_SHA256 = (
    "8e70bc71a5dfe564802fc72b0dc187eb67388bab94af068870ada6168a58a334"
)
A0_CERTIFICATE_SHA256 = (
    "03b20c172c6562ed32ea66f35dcd177bb887e17e60b7c49f632e91e0e1183b81"
)

EXPECTED_CODE = "FAIL_PREDICTOR_INPUT_PIN"
EPS = Fraction(1, 1 << 100)


class GateFailure(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}:{detail}" if detail else code)
        self.code = code
        self.detail = detail


def fail(code: str, detail: str = "") -> None:
    raise GateFailure(code, detail)


def need(cond: bool, code: str, detail: str = "") -> None:
    if not cond:
        fail(code, detail)


def stop(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), *args],
        text=True,
    ).strip()


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        stop(f"expected JSON object: {path}")
    return obj


def qtext(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def validate_pin() -> tuple[dict[str, Any], Fraction, Fraction]:
    need(PIN_PATH.is_file(), "FAIL_PIN_RECORD_MISSING")
    need(sha256_path(PIN_PATH) == PIN_SHA256, "FAIL_PIN_RECORD_SHA")

    pin = load_json(PIN_PATH)

    need(
        pin.get("schema") == "a0b-cell0-predictor-input-pin-v1",
        "FAIL_PIN_RECORD_SCHEMA",
    )
    need(pin.get("control_id") == "NC04b", "FAIL_PIN_RECORD_CONTROL_ID")
    need(
        pin.get("contract") == "F_LAMBDA_CONTRACT_V1.1",
        "FAIL_PIN_RECORD_CONTRACT",
    )
    need(
        pin.get("evidence_class") == "PIN_RECORD",
        "FAIL_PIN_RECORD_EVIDENCE_CLASS",
    )
    need(
        pin.get("binding_use_authorized") is False,
        "FAIL_PIN_RECORD_BINDING_STATE",
    )

    component1 = pin.get("component1")
    need(isinstance(component1, dict), "FAIL_COMPONENT1_PIN")
    need(
        component1.get("sha256") == COMPONENT1_SHA256,
        "FAIL_COMPONENT1_PIN",
    )
    need(
        component1.get("component1_match") is True,
        "FAIL_COMPONENT1_EXACT_MATCH",
    )
    need(
        component1.get("q_left_exact_match") is True,
        "FAIL_COMPONENT1_Q_LEFT_MATCH",
    )
    need(
        component1.get("q_right_exact_match") is True,
        "FAIL_COMPONENT1_Q_RIGHT_MATCH",
    )

    anchors = pin.get("a0b_start_anchors")
    need(isinstance(anchors, dict), "FAIL_A0B_ANCHORS_PIN")
    need(
        anchors.get("sha256") == A0B_START_ANCHORS_SHA256,
        "FAIL_A0B_ANCHORS_PIN",
    )

    a0 = pin.get("a0_certificate")
    need(isinstance(a0, dict), "FAIL_A0_CERTIFICATE_PIN")
    need(
        a0.get("sha256") == A0_CERTIFICATE_SHA256,
        "FAIL_A0_CERTIFICATE_PIN",
    )

    nc04b = pin.get("nc04b")
    need(isinstance(nc04b, dict), "FAIL_NC04b_PIN_STATE")
    need(
        nc04b.get("expected_contract_code") == EXPECTED_CODE,
        "FAIL_NC04b_EXPECTED_CODE_PIN",
    )
    need(
        nc04b.get("mutation_target") == "q_left_or_q_right",
        "FAIL_NC04b_MUTATION_TARGET_PIN",
    )
    need(
        nc04b.get("ready_for_execution") is True,
        "FAIL_NC04b_EXECUTION_STATE",
    )

    try:
        q_left = Fraction(anchors["q_left"])
        q_right = Fraction(anchors["q_right"])
        c1_q_left = Fraction(component1["q_left"])
        c1_q_right = Fraction(component1["q_right"])
        a0_q_left = Fraction(a0["q_left"])
    except Exception as exc:
        raise GateFailure("FAIL_PIN_RATIONAL_PARSE", str(exc)) from exc

    need(q_left == c1_q_left, "FAIL_COMPONENT1_Q_LEFT_MATCH")
    need(q_right == c1_q_right, "FAIL_COMPONENT1_Q_RIGHT_MATCH")
    need(q_left == a0_q_left, "FAIL_A0_Q_LEFT_MATCH")

    return pin, q_left, q_right


def predictor_pin_gate(
    candidate: dict[str, Any],
    *,
    pinned_q_left: Fraction,
    pinned_q_right: Fraction,
) -> None:
    predictor = candidate.get("predictor")
    need(isinstance(predictor, dict), "FAIL_PREDICTOR_INPUT_PIN")

    try:
        q_left = Fraction(predictor["q_left"])
        q_right = Fraction(predictor["q_right"])
    except Exception as exc:
        raise GateFailure(EXPECTED_CODE, f"parse:{exc}") from exc

    if q_left != pinned_q_left:
        fail(EXPECTED_CODE, "q_left")
    if q_right != pinned_q_right:
        fail(EXPECTED_CODE, "q_right")


def expect_failure(
    candidate: dict[str, Any],
    *,
    pinned_q_left: Fraction,
    pinned_q_right: Fraction,
    mutation_case: str,
) -> dict[str, Any]:
    try:
        predictor_pin_gate(
            candidate,
            pinned_q_left=pinned_q_left,
            pinned_q_right=pinned_q_right,
        )
    except GateFailure as exc:
        if exc.code != EXPECTED_CODE:
            stop(
                f"{mutation_case}: expected {EXPECTED_CODE}, "
                f"got {exc.code}:{exc.detail}"
            )
        return {
            "mutation_case": mutation_case,
            "status": "PASS",
            "expected_failure_code": EXPECTED_CODE,
            "observed_failure_code": exc.code,
            "observed_detail": exc.detail,
        }
    stop(f"{mutation_case}: expected {EXPECTED_CODE}, gate passed")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()

    output = ns.output.expanduser().resolve()

    head_pre = git("rev-parse", "HEAD")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_PRE dirty")

    _, q_left, q_right = validate_pin()

    baseline = {
        "predictor": {
            "q_left": qtext(q_left),
            "q_right": qtext(q_right),
        }
    }

    # Positive control: the exact frozen predictor inputs must pass.
    predictor_pin_gate(
        baseline,
        pinned_q_left=q_left,
        pinned_q_right=q_right,
    )

    q_left_case = json.loads(json.dumps(baseline))
    q_left_case["predictor"]["q_left"] = qtext(q_left + EPS)

    q_right_case = json.loads(json.dumps(baseline))
    q_right_case["predictor"]["q_right"] = qtext(q_right + EPS)

    results = [
        expect_failure(
            q_left_case,
            pinned_q_left=q_left,
            pinned_q_right=q_right,
            mutation_case="q_left_mutated",
        ),
        expect_failure(
            q_right_case,
            pinned_q_left=q_left,
            pinned_q_right=q_right,
            mutation_case="q_right_mutated",
        ),
    ]

    if any(row["status"] != "PASS" for row in results):
        stop("NC04b completion invariant failed")

    head_post = git("rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during NC04b gate")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-nc04b-predictor-pin-gate-run-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "gate_source_sha256": sha256_path(Path(__file__).resolve()),
        "control_id": "NC04b",
        "method": "RECEIPT_MUTATION",
        "needs_numerics": False,
        "end_to_end": False,
        "historical_checker_modified": False,
        "a0b_predictor_pin_sha256": PIN_SHA256,
        "component1_geometry_receipt_sha256": COMPONENT1_SHA256,
        "a0b_start_anchors_sha256": A0B_START_ANCHORS_SHA256,
        "pinned_q_left": qtext(q_left),
        "pinned_q_right": qtext(q_right),
        "expected_exact_code": EXPECTED_CODE,
        "positive_control_exact_pin_match": True,
        "mutation_results": results,
        "all_mutations_pass": True,
        "source_tree_pre_clean": True,
        "source_tree_post_clean": True,
        "head_unchanged_during_run": True,
        "execution_head": head_pre,
        "binding_use_authorized": False,
        "verdict": "NC04b_EXACT_SUBCODE_PASS_NOT_PROMOTED",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("CONTROL_ID=NC04b")
    print("METHOD=RECEIPT_MUTATION")
    print("POSITIVE_CONTROL=PASS")
    for row in results:
        print(
            f"{row['mutation_case']}=PASS:"
            f"{row['observed_failure_code']}:{row['observed_detail']}"
        )
    print("EXPECTED_EXACT_CODE=" + EXPECTED_CODE)
    print("A0B_PREDICTOR_PIN_SHA256=" + PIN_SHA256)
    print("COMPONENT1_GEOMETRY_RECEIPT_SHA256=" + COMPONENT1_SHA256)
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=NC04b_EXACT_SUBCODE_PASS_NOT_PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
