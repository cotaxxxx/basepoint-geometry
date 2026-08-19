#!/usr/bin/env python3
"""Produce the exact-grid routed-backend consistency certificate."""
from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path

from calibration_context import *
from calibration_config import load_config
from calibration_security import assert_clean_source_tree, load_production_kernel
from routed_evaluator import RoutedEvaluator, routed_bundle_pins
from routed_record_verifier import bridge_grid_sha256


def _points() -> list[tuple[Fraction, Fraction]]:
    lambdas = (
        Fraction(17, 8), Fraction(5, 2), Fraction(3, 1),
        Fraction(7, 2), Fraction(4, 1), Fraction(9, 2),
    )
    return [(Fraction(k, 64), lam) for k in range(48, 64) for lam in lambdas]


def _point_arb(value: Fraction, arb_type):
    return arb_type(value.numerator) / arb_type(value.denominator)


def _interval_json(value: DyadicInterval) -> dict:
    return value.to_json()


def build_route_consistency_certificate(
    config: dict, interior_kernel, arb_type, *, source_head: str
) -> dict:
    evaluator = RoutedEvaluator(interior_kernel, arb_type, config)
    evaluator.set_phase("ROUTE_CONSISTENCY")
    rows = []
    for index, (r, lam) in enumerate(_points()):
        r_ball = _point_arb(r, arb_type)
        lam_ball = _point_arb(lam, arb_type)
        row = {
            "index": index,
            "lambda": Rational.from_fraction(lam).to_json(),
            "r": Rational.from_fraction(r).to_json(),
        }
        for quantity in ("F", "F_r"):
            _, interior, _ = evaluator.evaluate_forced_arb(
                quantity, r_ball, lam_ball, ROUTED_INTERIOR_ROUTE_ID,
                tol=ROUTE_CONSISTENCY_TOL,
                depth=ROUTE_CONSISTENCY_DEPTH,
                limit=ROUTE_CONSISTENCY_LIMIT,
            )
            _, boundary, _ = evaluator.evaluate_forced_arb(
                quantity, r_ball, lam_ball, ROUTED_BOUNDARY_ROUTE_ID,
                tol=ROUTE_CONSISTENCY_TOL,
                depth=ROUTE_CONSISTENCY_DEPTH,
                limit=ROUTE_CONSISTENCY_LIMIT,
            )
            intersection = interior.intersection(boundary)
            if intersection is None:
                raise CalibrationError(
                    f"ROUTE_CONSISTENCY_FAILED: {quantity} row {index}"
                )
            row[quantity] = {
                "boundary": _interval_json(boundary),
                "interior": _interval_json(interior),
                "intersection": _interval_json(intersection),
            }
        rows.append(row)
    certificate = {
        "boundary_route_evaluation_count": evaluator.boundary_evaluation_count,
        "contract_id": ROUTED_CONTRACT_ID,
        "grid_id": ROUTE_CONSISTENCY_GRID_ID,
        "grid_sha256": bridge_grid_sha256(),
        "implementation_source_head": source_head,
        "pins": routed_bundle_pins(),
        "producer_settings": {
            "depth": ROUTE_CONSISTENCY_DEPTH,
            "dps": config["checker_dps"],
            "limit": ROUTE_CONSISTENCY_LIMIT,
            "tol": ROUTE_CONSISTENCY_TOL,
        },
        "row_count": len(rows),
        "rows": rows,
        "schema": ROUTE_CONSISTENCY_SCHEMA,
        "status": "PASS",
    }
    return certificate


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise CalibrationError("route consistency output already exists")
    assert_clean_source_tree()
    config, _ = load_config()
    kernel, _ = load_production_kernel()
    from flint import arb, ctx  # type: ignore[import-not-found]
    ctx.dps = config["checker_dps"]
    certificate = build_route_consistency_certificate(
        config, kernel, arb, source_head=args.source_head
    )
    args.out.write_bytes(canonical_json_bytes(certificate))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except (CalibrationError, SchemaError, OSError, ValueError, KeyError) as exc:
        print(f"ROUTE CONSISTENCY ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
