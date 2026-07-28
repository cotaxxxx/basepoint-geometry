#!/usr/bin/env python3
"""Exact affine tube geometry and interval-Krawczyk primitives."""
from __future__ import annotations

from dataclasses import dataclass

from numeric_schema import (
    D_ONE,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    SchemaError,
)

Q_RULE = "exact_endpoint_convex_hull_v1"


@dataclass(frozen=True)
class AffinePredictor:
    lambda_lo: Rational
    lambda_hi: Rational
    q_left: Dyadic
    q_right: Dyadic

    def __post_init__(self) -> None:
        if not self.lambda_lo < self.lambda_hi:
            raise SchemaError("affine predictor lambda interval must have positive width")

    def range_hull(self) -> DyadicInterval:
        """Exact endpoint hull; interval expression evaluation is forbidden."""
        return DyadicInterval.hull([self.q_left, self.q_right])

    def endpoint(self, side: str) -> Dyadic:
        if side == "left":
            return self.q_left
        if side == "right":
            return self.q_right
        raise SchemaError("side must be left or right")


def shifted(interval: DyadicInterval, value: Dyadic) -> DyadicInterval:
    point = DyadicInterval.point(value)
    return interval + point


def physical_tube(q_hull: DyadicInterval, y_box: DyadicInterval) -> DyadicInterval:
    return q_hull + y_box


def krawczyk_image(
    *,
    m: Dyadic,
    residual: DyadicInterval,
    slope: DyadicInterval,
    preconditioner: Dyadic,
    domain: DyadicInterval,
) -> DyadicInterval:
    if preconditioner == D_ZERO:
        raise SchemaError("Krawczyk preconditioner is zero")
    m_point = DyadicInterval.point(m)
    first = m_point - residual.div_dyadic(preconditioner)
    multiplier = DyadicInterval.point(D_ONE) - slope.div_dyadic(preconditioner)
    centered_domain = domain - m_point
    return first + multiplier * centered_domain


def exact_join_intersection(
    left_q_right: Dyadic,
    left_y: DyadicInterval,
    right_q_left: Dyadic,
    right_y: DyadicInterval,
) -> DyadicInterval:
    left_section = shifted(left_y, left_q_right)
    right_section = shifted(right_y, right_q_left)
    intersection = left_section.intersection(right_section)
    if intersection is None or not intersection.positive_width():
        raise SchemaError("JOIN cross-section intersection is empty or zero-width")
    return intersection
