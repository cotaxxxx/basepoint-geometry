#!/usr/bin/env python3
"""Independent verifier for the frozen fatal-box slope prepartition."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from calibration_context import *
import exact_lambda_prepartition_contract as producer_contract


VERIFIER_PREPARTITION_PATH = "exact_lambda_prepartition.py"
VERIFIER_PREPARTITION_SHA256 = (
    "23df9d9bd15683e6693008b0312f0b50ed537b031ae3e4db8a89178512bf7b9d"
)
VERIFIER_PREPARTITION_RULE_ID = "R111_FATAL_SLOPE_PREPARTITION_30_LEAF_V1"

VERIFIER_FATAL_R_LO = Dyadic(74281023883021057323306507, 86)
VERIFIER_FATAL_R_HI = Dyadic(77359446546029624093969931, 86)
VERIFIER_FATAL_LAMBDA_LO = Fraction(3307749, 1600000)
VERIFIER_FATAL_LAMBDA_HI = Fraction(3707749, 1600000)
VERIFIER_LAMBDA_STEP = Fraction(1, 16)


def _verify_source_pin() -> None:
    if (
        producer_contract.EXACT_LAMBDA_PREPARTITION_PATH
        != VERIFIER_PREPARTITION_PATH
        or producer_contract.EXACT_LAMBDA_PREPARTITION_SHA256
        != VERIFIER_PREPARTITION_SHA256
        or producer_contract.EXACT_LAMBDA_PREPARTITION_RULE_ID
        != VERIFIER_PREPARTITION_RULE_ID
    ):
        raise CalibrationError(
            "exact lambda prepartition verifier: producer/checker contract mismatch"
        )
    path = BTUBE_ROOT / VERIFIER_PREPARTITION_PATH
    if sha256_hex(path.read_bytes()) != VERIFIER_PREPARTITION_SHA256:
        raise CalibrationError(
            "exact lambda prepartition verifier: source pin mismatch"
        )


def _split_midpoint(
    domain: DyadicInterval,
) -> tuple[DyadicInterval, DyadicInterval]:
    midpoint = domain.midpoint()
    return (
        DyadicInterval(domain.lo, midpoint),
        DyadicInterval(midpoint, domain.hi),
    )


def _lambda_cells() -> dict[str, tuple[Fraction, Fraction]]:
    lo = VERIFIER_FATAL_LAMBDA_LO
    points = [lo + i * VERIFIER_LAMBDA_STEP for i in range(5)]
    if points[-1] != VERIFIER_FATAL_LAMBDA_HI:
        raise CalibrationError(
            "exact lambda prepartition verifier: lambda constants inconsistent"
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


def _r111_bins(
    r111: DyadicInterval,
) -> list[tuple[str, DyadicInterval]]:
    t_min = Fraction(1) - r111.hi.as_fraction()
    t_max = Fraction(1) - r111.lo.as_fraction()
    edges = [t_min]
    for _ in range(5):
        edges.append(2 * edges[-1])
    if not edges[-1] < t_max <= 2 * edges[-1]:
        raise CalibrationError(
            "exact lambda prepartition verifier: six-bin geometry mismatch"
        )
    edges.append(t_max)

    result = []
    for index, (t_lo, t_hi) in enumerate(zip(edges[:-1], edges[1:])):
        result.append(
            (
                f"B{index}",
                DyadicInterval(
                    Dyadic.from_fraction(Fraction(1) - t_hi),
                    Dyadic.from_fraction(Fraction(1) - t_lo),
                ),
            )
        )
    return result


def expected_prepartition_leaves() -> list[dict[str, Any]]:
    parent = DyadicInterval(
        VERIFIER_FATAL_R_LO,
        VERIFIER_FATAL_R_HI,
    )
    r0, r1 = _split_midpoint(parent)
    r10, r11 = _split_midpoint(r1)
    r110, r111 = _split_midpoint(r11)
    lambdas = _lambda_cells()

    specs: list[tuple[str, DyadicInterval, str]] = [
        ("R0/LALL", r0, "LALL"),
        ("R10/L0", r10, "L0"),
        ("R10/L1", r10, "L1"),
        ("R110/L00", r110, "L00"),
        ("R110/L01", r110, "L01"),
        ("R110/L1", r110, "L1"),
    ]
    for bin_id, r_bin in _r111_bins(r111):
        for lambda_id in ("L00", "L01", "L10", "L11"):
            specs.append(
                (f"R111/{bin_id}/{lambda_id}", r_bin, lambda_id)
            )

    if len(specs) != 30:
        raise CalibrationError(
            "exact lambda prepartition verifier: expected leaf count changed"
        )

    return [
        {
            "leaf_id": leaf_id,
            "r_interval": r_interval,
            "lambda_lo": lambdas[lambda_id][0],
            "lambda_hi": lambdas[lambda_id][1],
        }
        for leaf_id, r_interval, lambda_id in specs
    ]


def _rational(obj: Any, where: str) -> Fraction:
    return Rational.from_json(obj, where).as_fraction()


def verify_prepartition_trace_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    _verify_source_pin()

    marker = "|" + VERIFIER_PREPARTITION_RULE_ID + "|"
    tagged = [
        record
        for record in records
        if marker in str(record.get("phase", ""))
    ]
    candidate0_present = any(
        str(record.get("phase", "")).startswith("CANDIDATE:0")
        for record in records
    )

    if not tagged:
        if candidate0_present:
            raise CalibrationError(
                "exact lambda prepartition verifier: "
                "candidate 0 present without frozen prepartition evidence"
            )
        return {
            "prepartition_group_count": 0,
            "prepartition_leaf_count": 0,
            "prepartition_rule_id": VERIFIER_PREPARTITION_RULE_ID,
        }

    if len(tagged) != 30:
        raise CalibrationError(
            "exact lambda prepartition verifier: leaf trace count mismatch"
        )

    expected = expected_prepartition_leaves()
    observed_ids = []
    total_evaluations = 0

    for index, (record, leaf) in enumerate(zip(tagged, expected)):
        phase = record.get("phase")
        if not isinstance(phase, str):
            raise CalibrationError(
                "exact lambda prepartition verifier: phase missing"
            )
        prefix, separator, leaf_id = phase.partition(marker)
        if (
            not separator
            or prefix != "CANDIDATE:0"
            or leaf_id != leaf["leaf_id"]
        ):
            raise CalibrationError(
                "exact lambda prepartition verifier: "
                f"leaf order/identity mismatch at {index}"
            )
        observed_ids.append(leaf_id)

        if (
            record.get("quantity") != "F_r"
            or record.get("route_id") != ROUTED_BOUNDARY_ROUTE_ID
            or record.get("post_failure_fallback") is not False
        ):
            raise CalibrationError(
                "exact lambda prepartition verifier: leaf route contract mismatch"
            )

        r_interval = DyadicInterval.from_json(
            record.get("r_interval"),
            f"prepartition trace[{index}].r_interval",
        )
        if r_interval != leaf["r_interval"]:
            raise CalibrationError(
                "exact lambda prepartition verifier: leaf r interval mismatch"
            )

        detail = record.get("detail")
        if not isinstance(detail, dict):
            raise CalibrationError(
                "exact lambda prepartition verifier: boundary detail missing"
            )
        transport = detail.get("exact_lambda_transport")
        if not isinstance(transport, dict):
            raise CalibrationError(
                "exact lambda prepartition verifier: transport detail missing"
            )
        exact_lambda = transport.get("lambda_exact_interval")
        if not isinstance(exact_lambda, dict):
            raise CalibrationError(
                "exact lambda prepartition verifier: exact lambda missing"
            )
        lo = _rational(
            exact_lambda.get("lo"),
            f"prepartition trace[{index}].lambda.lo",
        )
        hi = _rational(
            exact_lambda.get("hi"),
            f"prepartition trace[{index}].lambda.hi",
        )
        if lo != leaf["lambda_lo"] or hi != leaf["lambda_hi"]:
            raise CalibrationError(
                "exact lambda prepartition verifier: leaf lambda mismatch"
            )

        if detail.get("refinement_predicate_id") != "R7_HU_POS_V1":
            raise CalibrationError(
                "exact lambda prepartition verifier: H_U predicate mismatch"
            )

        enclosure = DyadicInterval.from_json(
            record.get("enclosure"),
            f"prepartition trace[{index}].enclosure",
        )
        if not enclosure.hi < D_ZERO:
            raise CalibrationError(
                "exact lambda prepartition verifier: "
                "leaf F_r is not strictly negative"
            )

        delta = record.get("boundary_route_evaluation_count_delta")
        if not isinstance(delta, int) or isinstance(delta, bool) or delta <= 0:
            raise CalibrationError(
                "exact lambda prepartition verifier: invalid evaluation delta"
            )
        total_evaluations += delta

    if len(set(observed_ids)) != 30:
        raise CalibrationError(
            "exact lambda prepartition verifier: duplicate leaf identity"
        )

    return {
        "prepartition_group_count": 1,
        "prepartition_leaf_count": 30,
        "prepartition_rule_id": VERIFIER_PREPARTITION_RULE_ID,
        "prepartition_total_boundary_evaluations": total_evaluations,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
