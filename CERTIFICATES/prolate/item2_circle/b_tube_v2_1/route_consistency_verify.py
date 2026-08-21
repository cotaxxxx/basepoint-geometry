#!/usr/bin/env python3
"""Fresh independent verifier for the routed-backend consistency certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path

from calibration_context import *
from calibration_config import load_config
from calibration_security import assert_clean_source_tree, load_production_kernel
from exact_lambda_static import assert_exact_lambda_static_gate
from exact_lambda_verifier import reconstruct_transport
from routed_record_verifier import verify_route_consistency_certificate_structure


def _points() -> list[tuple[Fraction, Fraction]]:
    lambdas = (
        Fraction(17, 8), Fraction(5, 2), Fraction(3, 1),
        Fraction(7, 2), Fraction(4, 1), Fraction(9, 2),
    )
    return [
        (Fraction(k, 64), lam)
        for k in range(48, 64)
        for lam in lambdas
    ]


def _point_arb(value: Fraction, arb_type):
    return arb_type(value.numerator) / arb_type(value.denominator)


def verify_route_consistency_fresh(
    certificate_path: Path, *, source_head: str
) -> dict:
    assert_exact_lambda_static_gate()
    from exact_lambda_transport import ExactLambdaRoutedEvaluator
    config, _ = load_config()
    raw = certificate_path.read_bytes()
    certificate = parse_canonical_json_bytes(raw, allow_display=False)
    verify_route_consistency_certificate_structure(
        certificate, expected_source_head=source_head
    )
    kernel, _ = load_production_kernel()
    from flint import arb, ctx
    ctx.dps = config["checker_dps"]
    evaluator = ExactLambdaRoutedEvaluator(kernel, arb, config)
    evaluator.set_phase("ROUTE_CONSISTENCY_VERIFY")
    for row, (r, lam) in zip(certificate["rows"], _points()):
        r_ball = _point_arb(r, arb)
        expected_transport = reconstruct_transport(lam, lam)
        for quantity in ("F", "F_r"):
            _, interior, _ = evaluator.evaluate_forced_exact_arb(
                quantity,
                r_ball,
                lam,
                lam,
                ROUTED_INTERIOR_ROUTE_ID,
                tol=ROUTE_CONSISTENCY_TOL,
                depth=ROUTE_CONSISTENCY_DEPTH,
                limit=ROUTE_CONSISTENCY_LIMIT,
            )
            _, boundary, evidence = evaluator.evaluate_forced_exact_arb(
                quantity,
                r_ball,
                lam,
                lam,
                ROUTED_BOUNDARY_ROUTE_ID,
                tol=ROUTE_CONSISTENCY_TOL,
                depth=ROUTE_CONSISTENCY_DEPTH,
                limit=ROUTE_CONSISTENCY_LIMIT,
            )
            if evidence["detail"].get("exact_lambda_transport") != expected_transport:
                raise CalibrationError(
                    "route consistency fresh verify: transport reconstruction mismatch"
                )
            intersection = interior.intersection(boundary)
            if intersection is None:
                raise CalibrationError(
                    f"route consistency fresh verify: empty {quantity} intersection"
                )
            expected = row[quantity]
            if (
                expected["interior"] != interior.to_json()
                or expected["boundary"] != boundary.to_json()
                or expected["intersection"] != intersection.to_json()
            ):
                raise CalibrationError(
                    f"route consistency fresh verify: replay mismatch {quantity}"
                )
    if (
        evaluator.boundary_evaluation_count
        != certificate["boundary_route_evaluation_count"]
    ):
        raise CalibrationError(
            "route consistency fresh verify: evaluation count mismatch"
        )
    return certificate


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    args = parser.parse_args()
    assert_clean_source_tree()
    assert_exact_lambda_static_gate()
    verify_route_consistency_fresh(
        args.certificate, source_head=args.source_head
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except (CalibrationError, SchemaError, OSError, ValueError, KeyError) as exc:
        print(f"ROUTE CONSISTENCY VERIFY ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
