#!/usr/bin/env python3
"""Exact mock kernel for schema/checker self-tests only.

F(r, lambda) = ROOT - r and F_r = -1.  It has no mathematical role in the
prolate theorem and is rejected outside SELFTEST_ONLY mode.
"""
from __future__ import annotations

from numeric_schema import D_NEG_ONE, Dyadic, DyadicInterval, Rational

ROOT = Dyadic(1, 5)  # 1/32, inside the canonical C-G root bracket.
MOCK_KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"


def F_interval(r_box: DyadicInterval, lambda_box: tuple[Rational, Rational]) -> DyadicInterval:
    del lambda_box
    return DyadicInterval.point(ROOT) - r_box


def dFdr_interval(r_box: DyadicInterval, lambda_box: tuple[Rational, Rational]) -> DyadicInterval:
    del r_box, lambda_box
    return DyadicInterval.point(D_NEG_ONE)
