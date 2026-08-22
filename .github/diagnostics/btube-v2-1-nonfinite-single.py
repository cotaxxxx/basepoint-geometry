#!/usr/bin/env python3
"""Non-binding single-site layer diagnosis for the first census NONFINITE."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

from flint import arb, ctx

from affine_geometry import krawczyk_image
from calibration_config import load_config
from calibration_context import D_ZERO, Dyadic, DyadicInterval
from calibration_numeric import _nearest_dyadic
from calibration_security import load_production_kernel
from exact_lambda_transport import (
    ExactLambdaRoutedEvaluator,
    _dyadic_arb,
    install_exact_lambda_call_sites,
)
from numeric_schema import arb_ball_to_exact_interval
from routed_evaluator import _dyadic_interval_arb


LAMBDA_LO = Fraction(4907749, 1600000)
LAMBDA_HI = Fraction(5307749, 1600000)
DOMAIN = DyadicInterval(
    Dyadic.from_fraction(Fraction(57385725776159258912693602241, 1 << 96)),
    Dyadic.from_fraction(Fraction(67096226730500986174060564743, 1 << 96)),
)
OUT = Path("diagnostic-output/nonfinite-single-NOT_BINDING.json")


def error(exc: Exception) -> dict:
    return {"status": "ERROR", "error_type": type(exc).__name__, "error": str(exc)}


def arb_probe(value) -> dict:
    row = {"status": "PASS", "repr": str(value)}
    for name, getter in (("mid", value.mid), ("rad", value.rad)):
        try:
            component = getter()
            row[name] = {"repr": str(component), "man_exp": [str(x) for x in component.man_exp()]}
        except Exception as exc:
            row[name] = error(exc)
    try:
        row["roundtrip_exact_interval"] = arb_ball_to_exact_interval(value).to_json()
    except Exception as exc:
        row["roundtrip_exact_interval"] = error(exc)
    return row


def main() -> int:
    print("BTUBE_NONFINITE_SINGLE_V1")
    print("EVIDENCE_CLASS=DIAGNOSTIC_NOT_BINDING")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "btube-nonfinite-single-v1",
        "evidence_class": "DIAGNOSTIC_NOT_BINDING",
        "lambda_lo": str(LAMBDA_LO),
        "lambda_hi": str(LAMBDA_HI),
        "domain": DOMAIN.to_json(),
        "stages": {},
    }
    t0 = perf_counter()
    try:
        config, _ = load_config()
        raw_kernel, _ = load_production_kernel()
        ctx.dps = config["dps"]
        install_exact_lambda_call_sites()
        evaluator = ExactLambdaRoutedEvaluator(raw_kernel, arb, config)
        evaluator.set_phase("DIAGNOSTIC_NONFINITE_SINGLE")
        tol = "1e-20"
        depth = config["max_subdivisions"]
        limit = config["evaluation_budget"]
        midpoint = DOMAIN.midpoint()
        point_arb = _dyadic_arb(midpoint, arb)
        domain_arb = _dyadic_interval_arb(DOMAIN, arb)
        point_input = evaluator._r_input(point_arb)
        domain_input = evaluator._r_input(domain_arb)
        report["stages"]["R_INPUT"] = {
            "status": "PASS",
            "midpoint": midpoint.to_json(),
            "point_arb": arb_probe(point_arb),
            "point_roundtrip": point_input.to_json(),
            "domain_arb": arb_probe(domain_arb),
            "domain_roundtrip": domain_input.to_json(),
        }

        exact: dict[str, DyadicInterval] = {}
        calls = (
            ("F", "F", point_input, LAMBDA_LO, LAMBDA_HI),
            ("HU_DOMAIN", "F_r", domain_input, LAMBDA_LO, LAMBDA_HI),
            ("HU_CENTER", "F_r", point_input,
             (LAMBDA_LO + LAMBDA_HI) / 2, (LAMBDA_LO + LAMBDA_HI) / 2),
        )
        for stage, quantity, r_iv, lam_lo, lam_hi in calls:
            before = evaluator.boundary_evaluation_count
            try:
                value, interval, evidence = evaluator._evaluate_exact(
                    quantity, r_iv, lam_lo, lam_hi, tol, depth, limit, record=False
                )
                exact[stage] = interval
                report["stages"][stage] = {
                    "status": "PASS",
                    "exact_interval": interval.to_json(),
                    "arb_value": arb_probe(value),
                    "route_id": evidence["route_id"],
                    "charged_evaluations": evaluator.boundary_evaluation_count - before,
                }
            except Exception as exc:
                report["stages"][stage] = {
                    **error(exc),
                    "charged_evaluations": evaluator.boundary_evaluation_count - before,
                }

        if all(name in exact for name in ("F", "HU_DOMAIN", "HU_CENTER")):
            center_mid = exact["HU_CENTER"].midpoint()
            preconditioner = D_ZERO
            if center_mid != D_ZERO:
                preconditioner = _nearest_dyadic(
                    Fraction(1, 1) / center_mid.as_fraction(), bits=96
                )
            report["stages"]["PRECONDITIONER"] = {
                "status": "PASS", "value": preconditioner.to_json()
            }
            if preconditioner == D_ZERO:
                report["stages"]["KRAWCZYK_IMAGE"] = {
                    "status": "SKIPPED", "reason": "PRECONDITIONER_ZERO"
                }
            else:
                image = krawczyk_image(
                    m=midpoint, residual=exact["F"], slope=exact["HU_DOMAIN"],
                    preconditioner=preconditioner, domain=DOMAIN,
                )
                report["stages"]["KRAWCZYK_IMAGE"] = {
                    "status": "PASS", "image": image.to_json(),
                    "strictly_contained": DOMAIN.strictly_contains(image),
                }
        else:
            report["stages"]["PRECONDITIONER"] = {"status": "SKIPPED_UPSTREAM"}
            report["stages"]["KRAWCZYK_IMAGE"] = {"status": "SKIPPED_UPSTREAM"}

        f_stage = report["stages"].get("F", {})
        arb_mid = f_stage.get("arb_value", {}).get("mid", {})
        report["classification"] = (
            "EXACT_FINITE_ARB_MID_INVALID"
            if f_stage.get("status") == "PASS" and arb_mid.get("status") == "ERROR"
            else "OTHER"
        )
        report["charged_boundary_evaluations"] = evaluator.boundary_evaluation_count
        report["diagnostic_verdict"] = "PASS"
        rc = 0
    except Exception as exc:
        report["diagnostic_verdict"] = "ERROR"
        report["fatal"] = error(exc)
        rc = 4
    report["elapsed_seconds"] = f"{perf_counter() - t0:.6f}"
    OUT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"DIAGNOSTIC_VERDICT={report['diagnostic_verdict']}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
