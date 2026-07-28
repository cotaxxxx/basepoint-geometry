"""Independent config-to-candidate reconstruction for record layout."""
from __future__ import annotations
from fractions import Fraction

import calibration
from numeric_schema import D_ZERO, Dyadic

def _partition(start: Fraction, end: Fraction, width: Fraction) -> list[tuple[Fraction, Fraction]]:
    cells = []
    left = start
    while left < end:
        right = min(left + width, end)
        cells.append((left, right))
        left = right
    return cells


def _positive_width(record: dict) -> bool:
    try:
        return D_ZERO < Dyadic.from_json(record["width"], "join.width")
    except (KeyError, ValueError):
        return False


def candidate_pairs_from_config(config: dict) -> list[tuple[Dyadic, Dyadic]]:
    width_items = config.get("candidate_lambda_widths")
    radius_items = config.get("candidate_tube_radii")
    if not isinstance(width_items, list) or not width_items:
        raise calibration.CalibrationError("layout verifier: width candidates missing")
    if not isinstance(radius_items, list) or not radius_items:
        raise calibration.CalibrationError("layout verifier: radius candidates missing")
    widths = [Dyadic.from_json(item, f"candidate_lambda_widths[{index}]") for index, item in enumerate(width_items)]
    radii = [Dyadic.from_json(item, f"candidate_tube_radii[{index}]") for index, item in enumerate(radius_items)]
    for name, values in (("width", widths), ("radius", radii)):
        if any(value <= D_ZERO for value in values):
            raise calibration.CalibrationError(f"layout verifier: {name} candidates must be positive")
        if len(set(values)) != len(values):
            raise calibration.CalibrationError(f"layout verifier: duplicate {name} candidate")
        if any(not values[index + 1] < values[index] for index in range(len(values) - 1)):
            raise calibration.CalibrationError(f"layout verifier: {name} candidates not strictly decreasing")
    pairs = []
    for width in widths:
        for radius in radii:
            pairs.append((width, radius))
    return pairs

__all__ = [name for name in globals() if not name.startswith("__")]
