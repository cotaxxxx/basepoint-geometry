#!/usr/bin/env python3
"""Pinned exact Arb-ball to canonical dyadic interval adapter.

This module performs only exact binary mantissa/exponent extraction. It does
not import the mathematical kernel and has no decimal, string-display, float,
or approximate midpoint/radius path.
"""
from __future__ import annotations

from typing import Any, Protocol

ADAPTER_ID = "ARB_TO_CANONICAL_DYADIC_INTERVAL_V1"


class AdapterError(ValueError):
    pass


class ManExpProvider(Protocol):
    def man_exp(self) -> tuple[Any, Any]: ...


class ArbBallProvider(Protocol):
    def mid(self) -> ManExpProvider: ...
    def rad(self) -> ManExpProvider: ...


def _integer(value: Any, where: str) -> int:
    if isinstance(value, bool):
        raise AdapterError(f"{where}: bool forbidden")
    try:
        result = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise AdapterError(f"{where}: finite integer required") from exc
    return result


def canonical_dyadic(mantissa: int, denominator_exponent: int) -> dict[str, Any]:
    if not isinstance(mantissa, int) or isinstance(mantissa, bool):
        raise AdapterError("dyadic mantissa must be int")
    if (
        not isinstance(denominator_exponent, int)
        or isinstance(denominator_exponent, bool)
        or denominator_exponent < 0
    ):
        raise AdapterError("dyadic exponent must be a nonnegative int")
    if mantissa == 0:
        return {"m": "0", "e": 0}
    while denominator_exponent and mantissa % 2 == 0:
        mantissa //= 2
        denominator_exponent -= 1
    return {"m": str(mantissa), "e": denominator_exponent}


def exact_man_exp(value: ManExpProvider, where: str) -> tuple[int, int]:
    try:
        mantissa_raw, binary_exponent_raw = value.man_exp()
    except Exception as exc:
        raise AdapterError(f"{where}: man_exp unavailable or nonfinite") from exc
    mantissa = _integer(mantissa_raw, f"{where}.mantissa")
    binary_exponent = _integer(binary_exponent_raw, f"{where}.binary_exponent")
    if binary_exponent >= 0:
        return mantissa << binary_exponent, 0
    return mantissa, -binary_exponent


def _aligned_sum(
    left: tuple[int, int], right: tuple[int, int], sign: int
) -> tuple[int, int]:
    exponent = max(left[1], right[1])
    left_mantissa = left[0] << (exponent - left[1])
    right_mantissa = right[0] << (exponent - right[1])
    return left_mantissa + sign * right_mantissa, exponent


def arb_ball_to_canonical_dyadic_interval(ball: ArbBallProvider) -> dict[str, Any]:
    midpoint = exact_man_exp(ball.mid(), "arb.mid")
    radius = exact_man_exp(ball.rad(), "arb.rad")
    if radius[0] < 0:
        raise AdapterError("arb.rad: negative radius")
    lower = _aligned_sum(midpoint, radius, -1)
    upper = _aligned_sum(midpoint, radius, +1)
    return {
        "lo": canonical_dyadic(*lower),
        "hi": canonical_dyadic(*upper),
    }


__all__ = [
    "ADAPTER_ID",
    "AdapterError",
    "arb_ball_to_canonical_dyadic_interval",
    "canonical_dyadic",
    "exact_man_exp",
]
