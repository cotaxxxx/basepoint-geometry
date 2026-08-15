#!/usr/bin/env python3
"""Deterministic adaptive policies for B-LOCAL v2.2 finite F/K routes."""
from __future__ import annotations
from fractions import Fraction
from typing import Any

F_ROUTE_ID = "BLOCAL_F_ROUTE_V2"
K_ROUTE_ID = "BLOCAL_K_ROUTE_V2"
ANGULAR_POLICY_ID = "BLOCAL_TAYLOR2_CHARTED_ANGULAR_ADAPT_V3"
DENOMINATOR_POLICY_ID = "BLOCAL_EXACT_ENDPOINT_RECIPROCAL_DENOMINATOR_V3"
SQRT_POLICY_ID = "BLOCAL_EFFECTIVE_FLOOR_SQRT_V1"
GAMMA_POLICY_ID = "BLOCAL_DETERMINISTIC_GAMMA_MIDPOINT_UNTIL_FINITE_V1"
NORMALIZATION_POLICY_ID = "BLOCAL_ONE_OVER_PI_RATIONAL_ENCLOSURE_V1"
NEWTON_POLICY_ID = "BLOCAL_EXACT_RATIONAL_INTERVAL_NEWTON_V2"
NEGATION_RULE_ID = "BLOCAL_INTERVAL_NEGATION_V1"
MEASURE_ID = "SIN_THETA_DTHETA_EQUALS_MINUS_DC_V1"
DUFFY_ID = "EXACT_DYADIC_SQUARE_TWO_TRIANGLE_DUFFY_LOCAL_GEOMETRY_V3"
Q_LO_POLICY_ID = "BLOCAL_SIX_SITE_EFFECTIVE_FLOOR_V1"
HELPER_VALIDATION_ID = "BLOCAL_HELPER_LEMMAS_RUNTIME_V2"

REGION_ORDER = {"T1": 0, "T2": 1, "R2": 2, "C1": 3, "TH": 4}

EFFECTIVE_FLOOR_SITES = (
    "ORDINARY_Q", "ORDINARY_W2", "ORDINARY_S2",
    "DUFFY_W2", "DUFFY_G2", "DUFFY_S2",
)
DERIVATIVE_TARGET_LADDER = ("6/5", "1/1", "1/2", "1/4", "1/10")


def need(condition: Any, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_route_policy(obj: Any, where: str) -> None:
    need(isinstance(obj, dict), f"{where}: object")
    need(set(obj) == {"id", "max_depth", "max_children", "max_evaluations", "min_depth"},
         f"{where}: exact keys")
    need(obj["id"] == ANGULAR_POLICY_ID, f"{where}: policy id")
    for key in ("max_depth", "max_children", "max_evaluations", "min_depth"):
        need(isinstance(obj[key], int) and not isinstance(obj[key], bool) and obj[key] >= 0,
             f"{where}.{key}")
    need(obj["max_depth"] > 0 and obj["max_children"] >= 4 and obj["max_evaluations"] >= 4,
         f"{where}: positive budgets")
    need(obj["min_depth"] <= obj["max_depth"], f"{where}: min<=max")


def split_axis(a0: Fraction, a1: Fraction, b0: Fraction, b1: Fraction,
               depth: int) -> str:
    """Deterministic longest-width split, axis A on exact ties."""
    wa, wb = a1 - a0, b1 - b0
    need(wa > 0 and wb > 0, "positive child widths")
    if wa > wb:
        return "A"
    if wb > wa:
        return "B"
    return "A" if depth % 2 == 0 else "B"


def split_box(a0: Fraction, a1: Fraction, b0: Fraction, b1: Fraction,
              depth: int) -> list[tuple[Fraction, Fraction, Fraction, Fraction]]:
    axis = split_axis(a0, a1, b0, b1, depth)
    if axis == "A":
        m = (a0 + a1) / 2
        return [(a0, m, b0, b1), (m, a1, b0, b1)]
    m = (b0 + b1) / 2
    return [(a0, a1, b0, m), (a0, a1, m, b1)]


def child_key(child: dict[str, Any]) -> tuple[int, str]:
    return REGION_ORDER[child["region"]], child["path"]
