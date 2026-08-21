#!/usr/bin/env python3
"""Implementation-stage controls for exact-lambda routed transport.

This harness is not a calibration run and makes no coverage/certification claim.
It exists to close the Addendum V2 implementation controls before tag/run.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import time

from calibration_context import *
from calibration_config import load_config
from calibration_security import load_production_kernel
from a0b_start_anchor import build_a0b_start_anchor_certificate
from exact_lambda_static import assert_exact_lambda_static_gate
from exact_lambda_transport import (
    ExactLambdaRoutedEvaluator,
    install_exact_lambda_call_sites,
)
from exact_lambda_verifier import reconstruct_transport, verify_transport_detail


ACTIONS_LIMIT_SECONDS = 360 * 60
POSITIVE_R = Fraction(7, 8)
POSITIVE_LAMBDAS = (
    ("lambda_start", Fraction(3307749, 1600000)),
    ("bridge_17_over_8", Fraction(17, 8)),
    ("lambda_end", Fraction(118, 25)),
)


def _point_arb(value: Fraction, arb_type):
    return arb_type(value.numerator) / arb_type(value.denominator)


def _runtime():
    assert_exact_lambda_static_gate()
    config, _ = load_config()
    kernel, _ = load_production_kernel()
    from flint import arb, ctx
    ctx.dps = config["checker_dps"]
    install_exact_lambda_call_sites()
    evaluator = ExactLambdaRoutedEvaluator(kernel, arb, config)
    return config, arb, evaluator


def run_positive_controls() -> dict:
    config, arb, evaluator = _runtime()
    evaluator.set_phase("IMPLEMENTATION_POSITIVE_CONTROL")
    r_ball = _point_arb(POSITIVE_R, arb)
    rows = []
    for label, lam in POSITIVE_LAMBDAS:
        reconstructed = reconstruct_transport(lam, lam)
        verify_transport_detail(reconstructed)
        quantities = {}
        for quantity in ("F", "F_r"):
            _, interval, evidence = evaluator.evaluate_forced_exact_arb(
                quantity,
                r_ball,
                lam,
                lam,
                ROUTED_BOUNDARY_ROUTE_ID,
                tol=ROUTE_CONSISTENCY_TOL,
                depth=ROUTE_CONSISTENCY_DEPTH,
                limit=ROUTE_CONSISTENCY_LIMIT,
            )
            transport = evidence["detail"]["exact_lambda_transport"]
            if transport != reconstructed:
                raise CalibrationError(
                    f"positive control {label}: transport mismatch"
                )
            quantities[quantity] = {
                "boundary_route_id": evidence["detail"]["boundary_route_id"],
                "enclosure": interval.to_json(),
                "evaluation_count": evidence["detail"][
                    "boundary_route_evaluation_count"
                ],
            }
        rows.append(
            {
                "label": label,
                "lambda": Rational.from_fraction(lam).to_json(),
                "quantities": quantities,
                "transport": reconstructed,
            }
        )
    start = rows[0]["transport"]
    if (
        Rational.from_json(start["lower_rounding_enlargement"]).as_fraction()
        != 0
        or Rational.from_json(start["upper_rounding_enlargement"]).as_fraction()
        != 0
    ):
        raise CalibrationError(
            "positive control lambda_start: rounding loss must be zero"
        )
    return {
        "boundary_evaluation_count": evaluator.boundary_evaluation_count,
        "rows": rows,
        "status": "PASS",
    }


def run_a0b_smoke() -> dict:
    config, arb, evaluator = _runtime()
    evaluator.set_phase("A0B")
    certificate = build_a0b_start_anchor_certificate(
        config, evaluator, arb
    )
    trace = [
        record for record in evaluator.trace if record.get("phase") == "A0B"
    ]
    if not trace:
        raise CalibrationError("A0B smoke: routed trace is empty")
    for record in trace:
        if record["route_id"] != ROUTED_BOUNDARY_ROUTE_ID:
            raise CalibrationError("A0B smoke: non-boundary route selected")
        detail = record["detail"]
        verify_transport_detail(detail["exact_lambda_transport"])
    return {
        "a0b_entry_count": len(certificate["entries"]),
        "all_passed": certificate["all_passed"],
        "boundary_evaluation_count": evaluator.boundary_evaluation_count,
        "exact_boundary_trace_count": len(trace),
        "status": "PASS",
    }


def run_wallclock_control() -> dict:
    config, arb, evaluator = _runtime()
    evaluator.set_phase("IMPLEMENTATION_WALLCLOCK")
    r_ball = _point_arb(POSITIVE_R, arb)
    lam = Fraction(17, 8)
    started = time.perf_counter()
    _, _, evidence = evaluator.evaluate_forced_exact_arb(
        "F",
        r_ball,
        lam,
        lam,
        ROUTED_BOUNDARY_ROUTE_ID,
        tol=ROUTE_CONSISTENCY_TOL,
        depth=ROUTE_CONSISTENCY_DEPTH,
        limit=ROUTE_CONSISTENCY_LIMIT,
    )
    elapsed = time.perf_counter() - started
    evaluations = evidence["detail"]["boundary_route_evaluation_count"]
    if not isinstance(evaluations, int) or evaluations <= 0:
        raise CalibrationError("wallclock control: invalid evaluation count")
    seconds_per_evaluation = elapsed / evaluations
    projected = (
        config["boundary_route_evaluation_budget"]
        * seconds_per_evaluation
    )
    margin = ACTIONS_LIMIT_SECONDS - projected
    return {
        "actions_limit_seconds": ACTIONS_LIMIT_SECONDS,
        "boundary_evaluation_budget": config[
            "boundary_route_evaluation_budget"
        ],
        "elapsed_seconds": repr(elapsed),
        "evaluation_count": evaluations,
        "margin_seconds": repr(margin),
        "projected_budget_seconds": repr(projected),
        "seconds_per_evaluation": repr(seconds_per_evaluation),
        "status": "PASS" if margin > 0 else "HOLD",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "control", choices=("positive", "a0b-smoke", "wallclock", "all")
    )
    args = parser.parse_args()
    result = {}
    if args.control in {"positive", "all"}:
        result["positive"] = run_positive_controls()
    if args.control in {"a0b-smoke", "all"}:
        result["a0b_smoke"] = run_a0b_smoke()
    if args.control in {"wallclock", "all"}:
        result["wallclock"] = run_wallclock_control()
    print(canonical_json_bytes(result).decode("ascii"))
    if (
        "wallclock" in result
        and result["wallclock"]["status"] != "PASS"
    ):
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CalibrationError, SchemaError, OSError, ValueError, KeyError) as exc:
        print(f"EXACT LAMBDA CONTROL ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
