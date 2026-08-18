#!/usr/bin/env python3
"""A0B producer: point-lambda Krawczyk gates on exact first cross-sections."""
from __future__ import annotations

from calibration_context import *
from calibration_config import require_blocal_dependency
from calibration_numeric import *
from calibration_security import assert_result_namespace


A0B_SCHEMA = "btube-a0b-start-anchors-v1"


def _evaluate_point(*, kernel, arb_type, domain, lam, tol, depth, limit):
    lam_box = _fraction_box(lam, lam, arb_type)
    domain_box = _dyadic_box(domain, arb_type)
    midpoint = domain.midpoint()
    residual = arb_ball_to_exact_interval(kernel.F_arb(
        _dyadic_arb(midpoint, arb_type), lam_box,
        tol=tol, depth=depth, limit=limit,
    ))
    slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
        domain_box, lam_box, tol=tol, depth=depth, limit=limit,
    ))
    center_slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
        _dyadic_arb(midpoint, arb_type), _rational_arb(lam, arb_type),
        tol=tol, depth=depth, limit=limit,
    ))
    slope_mid = center_slope.midpoint()
    preconditioner = D_ZERO
    if slope_mid != D_ZERO:
        preconditioner = _nearest_dyadic(
            Fraction(1, 1) / slope_mid.as_fraction(), bits=96
        )
    image = DyadicInterval.point(midpoint)
    left_margin = D_ZERO
    right_margin = D_ZERO
    reason = None
    passed = False
    if preconditioner == D_ZERO:
        reason = "preconditioner_zero"
    else:
        image = krawczyk_image(
            m=midpoint, residual=residual, slope=slope,
            preconditioner=preconditioner, domain=domain,
        )
        left_margin = image.lo - domain.lo
        right_margin = domain.hi - image.hi
        if not domain.strictly_contains(image):
            reason = "krawczyk_not_strict"
        elif not slope.hi < D_ZERO:
            reason = "slope_not_strictly_negative"
        else:
            passed = True
    return {
        "failure_reason": reason,
        "krawczyk_image": image.to_json(),
        "left_margin": left_margin.to_json(),
        "passed": passed,
        "preconditioner": preconditioner.to_json(),
        "residual": residual.to_json(),
        "right_margin": right_margin.to_json(),
        "slope": slope.to_json(),
    }


def build_a0b_start_anchor_certificate(config, kernel, arb_type) -> dict[str, Any]:
    require_blocal_dependency(config)
    start = Rational.from_json(
        config["blocal_dependency"]["lambda_start"], "blocal_dependency.lambda_start"
    ).as_fraction()
    end = Rational.from_json(config["lambda_end"], "lambda_end").as_fraction()
    sigma = Dyadic.from_json(config["adaptive_safety_factor"], "adaptive_safety_factor")
    a0_interval, _ = _load_a0_start_interval()
    anchor = a0_interval.midpoint()
    tol = "1e-20"
    depth = config["max_subdivisions"]
    limit = config["evaluation_budget"]
    entries = []
    for candidate_index, (width, cap) in enumerate(_candidate_pairs(config)):
        right = min(start + width.as_fraction(), end)
        q_right = _newton_predictor(
            kernel, arb_type, right, anchor, iterations=4,
            tol=tol, depth=depth, limit=limit,
        )
        q_hull = DyadicInterval.hull([anchor, q_right])
        rho = D_ZERO
        d_left = D_ZERO
        d_right = D_ZERO
        domain = DyadicInterval.point(anchor)
        section = DyadicInterval.point(anchor)
        try:
            rho, d_left, d_right, domain = _adaptive_radius(q_hull, cap, sigma)
            section = shifted(DyadicInterval(-rho, rho), anchor)
        except CalibrationError:
            result = {
                "failure_reason": "adaptive_radius_or_physical_domain_invalid",
                "krawczyk_image": DyadicInterval.point(anchor).to_json(),
                "left_margin": D_ZERO.to_json(),
                "passed": False,
                "preconditioner": D_ZERO.to_json(),
                "residual": DyadicInterval.point(D_ZERO).to_json(),
                "right_margin": D_ZERO.to_json(),
                "slope": DyadicInterval.point(D_ZERO).to_json(),
            }
            evaluations = 0
        else:
            if not a0_interval.contains(section):
                result = {
                    "failure_reason": "start_anchor_section_outside_a0_bracket",
                    "krawczyk_image": DyadicInterval.point(section.midpoint()).to_json(),
                    "left_margin": D_ZERO.to_json(),
                    "passed": False,
                    "preconditioner": D_ZERO.to_json(),
                    "residual": DyadicInterval.point(D_ZERO).to_json(),
                    "right_margin": D_ZERO.to_json(),
                    "slope": DyadicInterval.point(D_ZERO).to_json(),
                }
                evaluations = 0
            else:
                result = _evaluate_point(
                    kernel=kernel, arb_type=arb_type, domain=section, lam=start,
                    tol=tol, depth=depth, limit=limit,
                )
                evaluations = 3
        entry = {
            "adaptive_radius": rho.to_json(),
            "adaptive_safety_factor": sigma.to_json(),
            "boundary_margin_left": d_left.to_json(),
            "boundary_margin_right": d_right.to_json(),
            "candidate_index": candidate_index,
            "evaluation_count": evaluations,
            "first_lambda_interval": {
                "lo": Rational.from_fraction(start).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            },
            "lambda_width": width.to_json(),
            "point_lambda": Rational.from_fraction(start).to_json(),
            "q_left": anchor.to_json(),
            "q_right": q_right.to_json(),
            "radius_rule": ADAPTIVE_RADIUS_RULE,
            "start_section": section.to_json(),
            "tube_interval": domain.to_json(),
            "tube_radius": cap.to_json(),
            **result,
        }
        assert_result_namespace(entry)
        entries.append(entry)
    certificate = {
        "a0_start_root_interval": a0_interval.to_json(),
        "all_passed": all(entry["passed"] for entry in entries),
        "anchor_mode": ANCHOR_MODE,
        "candidate_count": len(entries),
        "entries": entries,
        "lambda_start": Rational.from_fraction(start).to_json(),
        "mode": config["mode"],
        "schema": A0B_SCHEMA,
    }
    assert_result_namespace(certificate)
    return certificate


__all__ = [name for name in globals() if not name.startswith("__")]
