#!/usr/bin/env python3
'''Deterministic two-variable mean-value core for Item 3 sweep v9.

STATUS: PROTOTYPE / NOT AUDITED / NOT APPROVED FOR PRODUCTION.

This module contains no floating-point arithmetic and no kernel calls. It freezes the
exact center, mean-value arithmetic, split scores, and split-axis decision inherited
from the v9 design.
'''
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal


Axis = Literal["r", "lambda"]


@dataclass(frozen=True)
class ExactInterval:
    lo: Fraction
    hi: Fraction
    finite: bool = True

    def __post_init__(self) -> None:
        if self.finite and self.lo > self.hi:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @classmethod
    def nonfinite(cls) -> "ExactInterval":
        return cls(Fraction(0), Fraction(0), False)

    @classmethod
    def point(cls, value: Fraction) -> "ExactInterval":
        return cls(value, value, True)

    def __add__(self, other: "ExactInterval") -> "ExactInterval":
        if not self.finite or not other.finite:
            return self.nonfinite()
        return ExactInterval(self.lo + other.lo, self.hi + other.hi)

    def __mul__(self, other: "ExactInterval") -> "ExactInterval":
        if not self.finite or not other.finite:
            return self.nonfinite()
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return ExactInterval(min(products), max(products))

    def strictly_negative(self) -> bool:
        return self.finite and self.hi < 0

    def absmax(self) -> Fraction:
        if not self.finite:
            raise ValueError("absmax undefined for nonfinite interval")
        return max(abs(self.lo), abs(self.hi))


@dataclass(frozen=True)
class MeanValueEvidence:
    r0: Fraction
    lambda0: Fraction
    r_offset: ExactInterval
    lambda_offset: ExactInterval
    r_correction: ExactInterval
    lambda_correction: ExactInterval
    mean_value: ExactInterval
    strict_negative: bool


@dataclass(frozen=True)
class SplitScore:
    finite: bool
    value: Fraction = Fraction(0)

    @classmethod
    def nonfinite(cls) -> "SplitScore":
        return cls(False, Fraction(0))


@dataclass(frozen=True)
class SplitDecision:
    selected_axis: Axis | None
    reason: str
    r_score: SplitScore
    lambda_score: SplitScore


def canonical_midpoint(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise ValueError("interval lower endpoint exceeds upper endpoint")
    return (lo + hi) / 2


def radius(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise ValueError("interval lower endpoint exceeds upper endpoint")
    return (hi - lo) / 2


def centered_offset(interval: tuple[Fraction, Fraction], center: Fraction) -> ExactInterval:
    lo, hi = interval
    if lo > center or center > hi:
        raise ValueError("center lies outside interval")
    return ExactInterval(lo - center, hi - center)


def mean_value_enclosure(
    *,
    r_cell: tuple[Fraction, Fraction],
    lambda_box: tuple[Fraction, Fraction],
    g_r_center: ExactInterval,
    g_rr_box: ExactInterval,
    g_rlambda_box: ExactInterval,
) -> MeanValueEvidence:
    r0 = canonical_midpoint(r_cell)
    lambda0 = canonical_midpoint(lambda_box)
    r_offset = centered_offset(r_cell, r0)
    lambda_offset = centered_offset(lambda_box, lambda0)
    r_correction = g_rr_box * r_offset
    lambda_correction = g_rlambda_box * lambda_offset
    mean_value = g_r_center + r_correction + lambda_correction
    return MeanValueEvidence(
        r0=r0,
        lambda0=lambda0,
        r_offset=r_offset,
        lambda_offset=lambda_offset,
        r_correction=r_correction,
        lambda_correction=lambda_correction,
        mean_value=mean_value,
        strict_negative=mean_value.strictly_negative(),
    )


def split_score(
    derivative_box: ExactInterval,
    coordinate_interval: tuple[Fraction, Fraction],
) -> SplitScore:
    if not derivative_box.finite:
        return SplitScore.nonfinite()
    return SplitScore(True, radius(coordinate_interval) * derivative_box.absmax())


def select_split_axis(
    *,
    r_cell: tuple[Fraction, Fraction],
    lambda_box: tuple[Fraction, Fraction],
    g_rr_box: ExactInterval,
    g_rlambda_box: ExactInterval,
    r_splittable: bool,
    lambda_splittable: bool,
) -> SplitDecision:
    r_score = split_score(g_rr_box, r_cell)
    lambda_score = split_score(g_rlambda_box, lambda_box)

    candidates: list[Axis] = []
    if r_splittable:
        candidates.append("r")
    if lambda_splittable:
        candidates.append("lambda")
    if not candidates:
        return SplitDecision(None, "NO_SPLITTABLE_AXIS", r_score, lambda_score)

    if candidates == ["r"]:
        return SplitDecision("r", "ONLY_R_SPLITTABLE", r_score, lambda_score)
    if candidates == ["lambda"]:
        return SplitDecision("lambda", "ONLY_LAMBDA_SPLITTABLE", r_score, lambda_score)

    if not r_score.finite and lambda_score.finite:
        return SplitDecision("r", "NONFINITE_R_OUTRANKS_FINITE", r_score, lambda_score)
    if r_score.finite and not lambda_score.finite:
        return SplitDecision(
            "lambda",
            "NONFINITE_LAMBDA_OUTRANKS_FINITE",
            r_score,
            lambda_score,
        )
    if not r_score.finite and not lambda_score.finite:
        return SplitDecision("r", "DOUBLE_NONFINITE_TIE_TO_R", r_score, lambda_score)

    if r_score.value > lambda_score.value:
        return SplitDecision("r", "LARGER_EXACT_SCORE", r_score, lambda_score)
    if lambda_score.value > r_score.value:
        return SplitDecision("lambda", "LARGER_EXACT_SCORE", r_score, lambda_score)
    return SplitDecision("r", "EXACT_SCORE_TIE_TO_R", r_score, lambda_score)


def midpoint_children(
    interval: tuple[Fraction, Fraction],
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    lo, hi = interval
    if lo >= hi:
        raise ValueError("cannot split a degenerate interval")
    mid = canonical_midpoint(interval)
    return (lo, mid), (mid, hi)
