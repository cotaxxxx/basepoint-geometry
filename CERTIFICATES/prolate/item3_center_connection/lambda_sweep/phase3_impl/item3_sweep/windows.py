from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import ceil, floor
from typing import Iterable, Optional

from .canonical import ContractReject, canonical_json_bytes, sha256_hex
from .enums import CheckerFailureReason, RunnerFailureReason, WindowOrigin


@dataclass(frozen=True)
class PredictorPoint:
    lambda_value: Fraction
    root_midpoint: Fraction
    source_box_id: str
    source_overlap: Optional[tuple[Fraction, Fraction]] = None

    def to_object(self) -> dict[str, object]:
        def rat(x: Fraction) -> dict[str, str]:
            return {"p": str(x.numerator), "q": str(x.denominator)}

        obj: dict[str, object] = {
            "lambda": rat(self.lambda_value),
            "root_midpoint": rat(self.root_midpoint),
            "source_box_id": self.source_box_id,
        }
        if self.source_overlap is not None:
            obj["source_overlap"] = [rat(self.source_overlap[0]), rat(self.source_overlap[1])]
        return obj


@dataclass(frozen=True)
class PredictorContext:
    latest: PredictorPoint
    previous: Optional[PredictorPoint]

    @classmethod
    def capture(cls, points: Iterable[PredictorPoint]) -> "PredictorContext":
        seq = tuple(points)
        if not seq:
            raise ContractReject(
                CheckerFailureReason.PREDICTOR_CONTEXT_MISMATCH,
                "predictor context requires at least one point",
            )
        return cls(latest=seq[-1], previous=seq[-2] if len(seq) >= 2 else None)

    @property
    def origin(self) -> WindowOrigin:
        return (
            WindowOrigin.PREDICTOR_LINEAR
            if self.previous is not None
            else WindowOrigin.PREDICTOR_HORIZONTAL
        )

    def evaluate(self, lambda_hi: Fraction) -> Fraction:
        if self.previous is None:
            return self.latest.root_midpoint
        p0, p1 = self.previous, self.latest
        if p1.lambda_value == p0.lambda_value:
            raise ContractReject(
                CheckerFailureReason.PREDICTOR_CONTEXT_MISMATCH,
                "predictor lambda coordinates coincide",
            )
        slope = (p1.root_midpoint - p0.root_midpoint) / (p1.lambda_value - p0.lambda_value)
        return p1.root_midpoint + slope * (lambda_hi - p1.lambda_value)

    def canonical_sha256(self) -> str:
        obj = {
            "latest_point": self.latest.to_object(),
            "previous_point_if_present": self.previous.to_object() if self.previous else None,
            "source_pass_box_ids": [
                point.source_box_id
                for point in ((self.previous, self.latest) if self.previous else (self.latest,))
                if point is not None
            ],
        }
        return sha256_hex(canonical_json_bytes(obj))


@dataclass(frozen=True)
class WindowStep:
    side: str
    before: tuple[Fraction, Fraction]
    after: tuple[Fraction, Fraction]
    lower_saturated: bool
    upper_saturated: bool


@dataclass(frozen=True)
class GeneratedWindow:
    lo: Fraction
    hi: Fraction
    origin: WindowOrigin
    q: Fraction
    step_history: tuple[WindowStep, ...]

    @property
    def width(self) -> Fraction:
        return self.hi - self.lo


class WindowGenerationError(RuntimeError):
    def __init__(self, reason: RunnerFailureReason, message: str):
        super().__init__(message)
        self.reason = reason


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def _ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _width_of_intersection(
    first: tuple[Fraction, Fraction],
    second: tuple[Fraction, Fraction],
) -> Fraction:
    lo = max(first[0], second[0])
    hi = min(first[1], second[1])
    return max(Fraction(0), hi - lo)


def generate_window(
    *,
    q: Fraction,
    origin: WindowOrigin,
    grid: Fraction,
    minimum_width: Fraction,
    previous_window: tuple[Fraction, Fraction],
    delta_overlap_min: Fraction,
) -> GeneratedWindow:
    if grid <= 0 or minimum_width <= 0 or delta_overlap_min <= 0:
        raise ValueError("positive grid/width/overlap required")

    c_lo = _floor_fraction(q / grid) * grid
    c_hi = _ceil_fraction(q / grid) * grid
    initial_width = c_hi - c_lo
    needed_steps = max(0, _ceil_fraction((minimum_width - initial_width) / grid))
    lower_steps = _ceil_fraction(Fraction(needed_steps, 2))
    upper_steps = needed_steps // 2
    w_lo = c_lo - lower_steps * grid
    w_hi = c_hi + upper_steps * grid

    domain = (grid, 1 - grid)
    maximum_possible_overlap = _width_of_intersection(previous_window, domain)
    if maximum_possible_overlap < delta_overlap_min:
        raise WindowGenerationError(
            RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
            "previous window cannot overlap clamped domain sufficiently",
        )

    steps: list[WindowStep] = []
    max_iterations = int((1 / grid)) + 4
    for _ in range(max_iterations):
        if _width_of_intersection(previous_window, (w_lo, w_hi)) >= delta_overlap_min:
            break
        lower_saturated = w_lo <= grid
        upper_saturated = w_hi >= 1 - grid
        if lower_saturated and upper_saturated:
            raise WindowGenerationError(
                RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
                "both window sides saturated before overlap minimum",
            )
        previous_mid = (previous_window[0] + previous_window[1]) / 2
        current_mid = (w_lo + w_hi) / 2
        if previous_mid > current_mid:
            preferred = "UPPER"
        elif previous_mid < current_mid:
            preferred = "LOWER"
        else:
            preferred = "LOWER"
        if preferred == "LOWER" and lower_saturated:
            preferred = "UPPER"
        elif preferred == "UPPER" and upper_saturated:
            preferred = "LOWER"
        before = (w_lo, w_hi)
        if preferred == "LOWER":
            if lower_saturated:
                raise WindowGenerationError(
                    RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
                    "lower side selected while saturated",
                )
            w_lo -= grid
        else:
            if upper_saturated:
                raise WindowGenerationError(
                    RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
                    "upper side selected while saturated",
                )
            w_hi += grid
        if w_lo < grid or w_hi > 1 - grid:
            raise WindowGenerationError(
                RunnerFailureReason.WINDOW_GENERATION_FAIL,
                "window step moved outside clamped domain",
            )
        steps.append(
            WindowStep(
                side=preferred,
                before=before,
                after=(w_lo, w_hi),
                lower_saturated=lower_saturated,
                upper_saturated=upper_saturated,
            )
        )
    else:
        raise WindowGenerationError(
            RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
            "overlap loop exceeded deterministic iteration bound",
        )

    w_lo = max(w_lo, grid)
    w_hi = min(w_hi, 1 - grid)
    if not w_lo < w_hi:
        raise WindowGenerationError(
            RunnerFailureReason.WINDOW_GENERATION_FAIL,
            "clamp produced empty window",
        )
    if w_hi - w_lo < minimum_width:
        raise WindowGenerationError(
            RunnerFailureReason.WINDOW_GENERATION_FAIL,
            "clamp lost minimum width",
        )
    if _width_of_intersection(previous_window, (w_lo, w_hi)) < delta_overlap_min:
        raise WindowGenerationError(
            RunnerFailureReason.WINDOW_GENERATION_FAIL,
            "clamp lost overlap",
        )
    return GeneratedWindow(
        lo=w_lo,
        hi=w_hi,
        origin=origin,
        q=q,
        step_history=tuple(steps),
    )
