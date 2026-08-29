#!/usr/bin/env python3
"""Focused negative controls for the independent F_lambda transport checker.

This file implements only the controls whose exact current contracts are fixed:
NC04 (diagnostic-width endpoint substitution must fail geometry reconstruction)
and NC20 (producer-glue dependency must fail at source/runtime independence).
It deliberately makes no claim to be the historical full NC01..NCxx catalog.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import flambda_transport_checker_v1 as checker
from calibration_context import Dyadic, canonical_json_bytes
from numeric_schema import parse_canonical_json_bytes

NC_SCHEMA = "btube-flambda-transport-checker-v1-negative-controls"
DELTA = Fraction(6900531025808907, 1 << 86)


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_canonical(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = parse_canonical_json_bytes(raw)
    if not isinstance(obj, dict):
        raise SystemExit(f"STOP: expected JSON object: {path}")
    return obj, raw


def expect_failure(
    *,
    expected_code: str,
    expected_head: str,
    producer_receipt_path: Path,
) -> dict[str, Any]:
    try:
        checker.check_receipt(
            expected_head=expected_head,
            producer_receipt_path=producer_receipt_path,
        )
    except checker.CheckerFailure as exc:
        if exc.code != expected_code:
            raise SystemExit(
                f"STOP: expected {expected_code}, got {exc.code}:{exc.detail}"
            ) from exc
        return {
            "status": "PASS",
            "expected_failure_code": expected_code,
            "observed_failure_code": exc.code,
            "observed_detail": exc.detail,
        }
    except Exception as exc:
        raise SystemExit(
            f"STOP: expected CheckerFailure {expected_code}, got "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    raise SystemExit(f"STOP: expected failure {expected_code}, checker passed")


def run_nc04(
    *,
    producer: dict[str, Any],
    expected_head: str,
) -> dict[str, Any]:
    mutated = json.loads(json.dumps(producer))
    r_lo = Dyadic.from_json(mutated["r_lo"], "r_lo").as_fraction()
    r_hi = Dyadic.from_json(mutated["r_hi"], "r_hi").as_fraction()
    widened_lo = r_lo - DELTA
    widened_hi = r_hi + DELTA

    mutated["r_lo"] = Dyadic.from_fraction(widened_lo).to_json()
    mutated["r_hi"] = Dyadic.from_fraction(widened_hi).to_json()
    mutated["tube_interval"]["lo"] = Dyadic.from_fraction(widened_lo).to_json()
    mutated["tube_interval"]["hi"] = Dyadic.from_fraction(widened_hi).to_json()

    with tempfile.TemporaryDirectory(prefix="btube-nc04-") as td:
        path = Path(td) / "producer_nc04.json"
        path.write_bytes(canonical_json_bytes(mutated))
        result = expect_failure(
            expected_code="FAIL_TUBE_GEOMETRY_RECONSTRUCTION",
            expected_head=expected_head,
            producer_receipt_path=path,
        )

    result.update(
        {
            "nc_id": "NC04",
            "mutation": "WIDEN_BOTH_PHYSICAL_TUBE_ENDPOINTS_BY_DIAGNOSTIC_DELTA",
            "delta": {
                "p": str(DELTA.numerator),
                "q": str(DELTA.denominator),
            },
            "mutated_r_lo": {
                "p": str(widened_lo.numerator),
                "q": str(widened_lo.denominator),
            },
            "mutated_r_hi": {
                "p": str(widened_hi.numerator),
                "q": str(widened_hi.denominator),
            },
        }
    )
    return result


def run_nc20(
    *,
    producer_receipt_path: Path,
    expected_head: str,
) -> dict[str, Any]:
    positive = checker._assert_checker_independence()

    sentinel = types.ModuleType(checker.FORBIDDEN_PRODUCER_MODULE)
    sentinel.__file__ = str(checker.FORBIDDEN_PRODUCER_PATH)
    old = sys.modules.get(checker.FORBIDDEN_PRODUCER_MODULE)
    sys.modules[checker.FORBIDDEN_PRODUCER_MODULE] = sentinel
    try:
        negative = expect_failure(
            expected_code="FAIL_PRODUCER_GLUE_DEPENDENCY",
            expected_head=expected_head,
            producer_receipt_path=producer_receipt_path,
        )
    finally:
        if old is None:
            sys.modules.pop(checker.FORBIDDEN_PRODUCER_MODULE, None)
        else:
            sys.modules[checker.FORBIDDEN_PRODUCER_MODULE] = old

    return {
        "nc_id": "NC20",
        "status": "PASS",
        "positive_source_runtime_independence": positive,
        "runtime_injection_control": negative,
        "expected_failure_code": "FAIL_PRODUCER_GLUE_DEPENDENCY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-receipt", required=True)
    parser.add_argument("--checker-receipt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expected-head", required=True)
    args = parser.parse_args()

    producer_path = Path(args.producer_receipt).expanduser().resolve()
    checker_path = Path(args.checker_receipt).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    producer, producer_raw = load_canonical(producer_path)
    checked, checker_raw = load_canonical(checker_path)

    if checked.get("schema") != checker.CHECKER_SCHEMA:
        raise SystemExit("STOP: checker receipt schema mismatch")
    if checked.get("checker_verdict") != "PASS_BINDING_CANDIDATE_CHECK":
        raise SystemExit("STOP: checker receipt is not a passing checker receipt")
    if checked.get("execution_head") != args.expected_head:
        raise SystemExit("STOP: checker receipt execution HEAD mismatch")
    if (
        checked.get("producer_receipt", {}).get("sha256")
        != sha_bytes(producer_raw)
    ):
        raise SystemExit("STOP: checker receipt is not linked to producer receipt")

    nc04 = run_nc04(producer=producer, expected_head=args.expected_head)
    nc20 = run_nc20(
        producer_receipt_path=producer_path,
        expected_head=args.expected_head,
    )

    result = {
        "schema": NC_SCHEMA,
        "status": "PASS_SPECIFIED_CONTROLS",
        "execution_head": args.expected_head,
        "binding_use_authorized": False,
        "full_historical_nc_catalog_claim": False,
        "catalog_scope": ["NC04", "NC20"],
        "producer_receipt_sha256": sha_bytes(producer_raw),
        "checker_receipt_sha256": sha_bytes(checker_raw),
        "controls": [nc04, nc20],
    }
    output_path.write_bytes(canonical_json_bytes(result))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
