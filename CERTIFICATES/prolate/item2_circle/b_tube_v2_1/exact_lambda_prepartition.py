#!/usr/bin/env python3
"""Deterministic pre-call slope partition for the known exact-lambda fatal box."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from calibration_context import *
from calibration_security import _assert_repo_regular_file
from exact_lambda_prepartition_contract import (
    EXACT_LAMBDA_PREPARTITION_PATH,
    EXACT_LAMBDA_PREPARTITION_RULE_ID,
    EXACT_LAMBDA_PREPARTITION_SHA256,
)
from exact_lambda_transport import (
    ExactLambdaRoutedEvaluator,
    _dyadic_arb,
    _dyadic_interval_arb,
    _kernel_F,
    _kernel_Fr,
    exact_evaluate_krawczyk,
)
from routed_evaluator import selector_for_r_interval


_FATAL_R_LO = Dyadic(74281023883021057323306507, 86)
_FATAL_R_HI = Dyadic(77359446546029624093969931, 86)
_FATAL_LAMBDA_LO = Fraction(3307749, 1600000)
_FATAL_LAMBDA_HI = Fraction(3707749, 1600000)
_LAMBDA_STEP = Fraction(1, 16)


def _verify_source_pin() -> None:
    path = _assert_repo_regular_file(
        BTUBE_ROOT / EXACT_LAMBDA_PREPARTITION_PATH, REPO_ROOT
    )
    if sha256_hex(path.read_bytes()) != EXACT_LAMBDA_PREPARTITION_SHA256:
        raise CalibrationError("exact lambda prepartition: source pin mismatch")


def _target_box(
    domain: DyadicInterval,
    lam_lo: Fraction,
    lam_hi: Fraction,
) -> bool:
    return (
        domain.lo == _FATAL_R_LO
        and domain.hi == _FATAL_R_HI
        and lam_lo == _FATAL_LAMBDA_LO
        and lam_hi == _FATAL_LAMBDA_HI
        and selector_for_r_interval(domain) == ROUTED_BOUNDARY_ROUTE_ID
    )


def _split_midpoint(
    domain: DyadicInterval,
) -> tuple[DyadicInterval, DyadicInterval]:
    midpoint = domain.midpoint()
    return (
        DyadicInterval(domain.lo, midpoint),
        DyadicInterval(midpoint, domain.hi),
    )


def _lambda_cells(
    lam_lo: Fraction,
    lam_hi: Fraction,
) -> dict[str, tuple[Fraction, Fraction]]:
    if lam_hi - lam_lo != Fraction(1, 4):
        raise CalibrationError(
            "exact lambda prepartition: target lambda width changed"
        )
    points = [lam_lo + i * _LAMBDA_STEP for i in range(5)]
    if points[-1] != lam_hi:
        raise CalibrationError(
            "exact lambda prepartition: lambda quartering mismatch"
        )
    return {
        "L00": (points[0], points[1]),
        "L01": (points[1], points[2]),
        "L0": (points[0], points[2]),
        "L10": (points[2], points[3]),
        "L11": (points[3], points[4]),
        "L1": (points[2], points[4]),
        "LALL": (points[0], points[4]),
    }


def _r111_geometric_bins(
    r111: DyadicInterval,
) -> list[tuple[str, DyadicInterval]]:
    t_min = Fraction(1) - r111.hi.as_fraction()
    t_max = Fraction(1) - r111.lo.as_fraction()
    if not Fraction(0) < t_min < t_max:
        raise CalibrationError(
            "exact lambda prepartition: invalid R111 t interval"
        )

    t_edges = [t_min]
    for _ in range(5):
        t_edges.append(2 * t_edges[-1])
    if not t_edges[-1] < t_max <= 2 * t_edges[-1]:
        raise CalibrationError(
            "exact lambda prepartition: frozen six-bin geometry changed"
        )
    t_edges.append(t_max)

    bins: list[tuple[str, DyadicInterval]] = []
    for index, (t_lo, t_hi) in enumerate(zip(t_edges[:-1], t_edges[1:])):
        try:
            r_lo = Dyadic.from_fraction(Fraction(1) - t_hi)
            r_hi = Dyadic.from_fraction(Fraction(1) - t_lo)
        except SchemaError as exc:
            raise CalibrationError(
                "exact lambda prepartition: non-dyadic geometric edge"
            ) from exc
        bins.append((f"B{index}", DyadicInterval(r_lo, r_hi)))

    if bins[0][1].hi != r111.hi or bins[-1][1].lo != r111.lo:
        raise CalibrationError(
            "exact lambda prepartition: R111 endpoint mismatch"
        )
    for left, right in zip(bins[:-1], bins[1:]):
        if right[1].hi != left[1].lo:
            raise CalibrationError(
                "exact lambda prepartition: R111 bins not contiguous"
            )
    return bins


def fatal_slope_prepartition_leaves(
    domain: DyadicInterval,
    lam_lo: Fraction,
    lam_hi: Fraction,
) -> list[dict[str, Any]]:
    """Return the frozen 30-leaf cover; no result-dependent branching."""
    if not _target_box(domain, lam_lo, lam_hi):
        raise CalibrationError(
            "exact lambda prepartition: requested outside frozen target box"
        )

    r0, r1 = _split_midpoint(domain)
    r10, r11 = _split_midpoint(r1)
    r110, r111 = _split_midpoint(r11)
    lambda_cells = _lambda_cells(lam_lo, lam_hi)

    leaf_specs: list[tuple[str, DyadicInterval, str]] = [
        ("R0/LALL", r0, "LALL"),
        ("R10/L0", r10, "L0"),
        ("R10/L1", r10, "L1"),
        ("R110/L00", r110, "L00"),
        ("R110/L01", r110, "L01"),
        ("R110/L1", r110, "L1"),
    ]
    for bin_id, r_bin in _r111_geometric_bins(r111):
        for lambda_id in ("L00", "L01", "L10", "L11"):
            leaf_specs.append(
                (f"R111/{bin_id}/{lambda_id}", r_bin, lambda_id)
            )

    if len(leaf_specs) != 30:
        raise CalibrationError(
            "exact lambda prepartition: frozen leaf count changed"
        )

    leaves = []
    for leaf_id, r_interval, lambda_id in leaf_specs:
        leaf_lambda_lo, leaf_lambda_hi = lambda_cells[lambda_id]
        leaves.append({
            "leaf_id": leaf_id,
            "r_interval": r_interval,
            "lambda_lo": leaf_lambda_lo,
            "lambda_hi": leaf_lambda_hi,
        })
    return leaves


def _prepartitioned_slope(
    kernel: ExactLambdaRoutedEvaluator,
    arb_type: Any,
    domain: DyadicInterval,
    lam_lo: Fraction,
    lam_hi: Fraction,
    *,
    tol: str,
    depth: int,
    limit: int,
) -> DyadicInterval:
    leaves = fatal_slope_prepartition_leaves(
        domain, lam_lo, lam_hi
    )
    base_phase = kernel.phase
    intervals: list[DyadicInterval] = []
    try:
        for leaf in leaves:
            kernel.set_phase(
                base_phase
                + "|"
                + EXACT_LAMBDA_PREPARTITION_RULE_ID
                + "|"
                + leaf["leaf_id"]
            )
            value = _kernel_Fr(
                kernel,
                arb_type,
                _dyadic_interval_arb(
                    leaf["r_interval"], arb_type
                ),
                leaf["lambda_lo"],
                leaf["lambda_hi"],
                tol=tol,
                depth=depth,
                limit=limit,
            )
            intervals.append(
                arb_ball_to_exact_interval(value)
            )
    finally:
        kernel.set_phase(base_phase)

    if len(intervals) != 30:
        raise CalibrationError(
            "exact lambda prepartition: incomplete slope leaf evaluation"
        )
    hull_values = []
    for interval in intervals:
        hull_values.extend((interval.lo, interval.hi))
    slope = DyadicInterval.hull(hull_values)
    if not slope.hi < D_ZERO:
        raise CalibrationError(
            "exact lambda prepartition: frozen slope hull not strictly negative"
        )
    return slope


def exact_evaluate_krawczyk_prepartition(
    *,
    kernel,
    arb_type,
    domain,
    lam_lo,
    lam_hi,
    tol,
    depth,
    limit,
):
    if (
        not isinstance(kernel, ExactLambdaRoutedEvaluator)
        or not _target_box(domain, lam_lo, lam_hi)
    ):
        return exact_evaluate_krawczyk(
            kernel=kernel,
            arb_type=arb_type,
            domain=domain,
            lam_lo=lam_lo,
            lam_hi=lam_hi,
            tol=tol,
            depth=depth,
            limit=limit,
        )

    from calibration_numeric import _dyadic_box, _nearest_dyadic

    midpoint = domain.midpoint()
    midpoint_lam = (lam_lo + lam_hi) / 2
    residual = arb_ball_to_exact_interval(
        _kernel_F(
            kernel,
            arb_type,
            _dyadic_arb(midpoint, arb_type),
            lam_lo,
            lam_hi,
            tol=tol,
            depth=depth,
            limit=limit,
        )
    )
    slope = _prepartitioned_slope(
        kernel,
        arb_type,
        domain,
        lam_lo,
        lam_hi,
        tol=tol,
        depth=depth,
        limit=limit,
    )
    center_slope = arb_ball_to_exact_interval(
        _kernel_Fr(
            kernel,
            arb_type,
            _dyadic_arb(midpoint, arb_type),
            midpoint_lam,
            midpoint_lam,
            tol=tol,
            depth=depth,
            limit=limit,
        )
    )

    slope_mid = center_slope.midpoint()
    preconditioner = D_ZERO
    if slope_mid != D_ZERO:
        preconditioner = _nearest_dyadic(
            Fraction(1, 1) / slope_mid.as_fraction(),
            bits=96,
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
            m=midpoint,
            residual=residual,
            slope=slope,
            preconditioner=preconditioner,
            domain=domain,
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
        "image": image,
        "left_margin": left_margin,
        "passed": passed,
        "preconditioner": preconditioner,
        "reason": reason,
        "residual": residual,
        "right_margin": right_margin,
        "slope": slope,
        "slope_prepartition_leaf_count": 30,
        "slope_prepartition_rule_id":
            EXACT_LAMBDA_PREPARTITION_RULE_ID,
    }


def install_exact_lambda_prepartition_call_site() -> dict[str, str]:
    _verify_source_pin()
    import calibration_candidate as candidate_module

    current = getattr(
        candidate_module, "_evaluate_krawczyk", None
    )
    if current is exact_evaluate_krawczyk_prepartition:
        return {
            "calibration_candidate._evaluate_krawczyk":
                exact_evaluate_krawczyk_prepartition.__name__,
        }
    if current is not exact_evaluate_krawczyk:
        raise CalibrationError(
            "exact lambda prepartition: unexpected patch target "
            "calibration_candidate._evaluate_krawczyk"
        )
    setattr(
        candidate_module,
        "_evaluate_krawczyk",
        exact_evaluate_krawczyk_prepartition,
    )
    return {
        "calibration_candidate._evaluate_krawczyk":
            exact_evaluate_krawczyk_prepartition.__name__,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
