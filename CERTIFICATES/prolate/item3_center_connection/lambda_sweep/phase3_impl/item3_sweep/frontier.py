from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional

from .canonical import ContractReject
from .enums import CheckerFailureReason, PrimaryWindowMode


@dataclass(frozen=True)
class LambdaBox:
    lo: Fraction
    hi: Fraction
    depth: int
    box_id: str
    parent_box_id: Optional[str] = None
    primary_window_mode: PrimaryWindowMode = PrimaryWindowMode.PREDICTOR_AT_ACTIVATION
    inherited_window: Optional[tuple[Fraction, Fraction]] = None

    @property
    def width(self) -> Fraction:
        return self.hi - self.lo


@dataclass(frozen=True)
class SplitResult:
    parent: LambdaBox
    midpoint: Fraction
    upper_child: LambdaBox
    lower_child: LambdaBox


class FrontierMachine:
    def __init__(
        self,
        *,
        lambda_anchor: Fraction,
        lambda_target: Fraction,
        minimum_width: Fraction,
        max_depth: int,
    ) -> None:
        if not lambda_target < lambda_anchor:
            raise ValueError("target must be below anchor")
        self.lambda_anchor = lambda_anchor
        self.lambda_target = lambda_target
        self.minimum_width = minimum_width
        self.max_depth = max_depth
        self.current_upper = lambda_anchor
        self.lambda_reached = lambda_anchor
        self.stack: list[LambdaBox] = []
        self._serial = 0
        self.current = self._new_initial_box()

    def _next_id(self, prefix: str) -> str:
        self._serial += 1
        return f"{prefix}-{self._serial:08d}"

    def _new_initial_box(self) -> LambdaBox:
        lo = max(self.lambda_target, self.current_upper - Fraction(1, 16))
        return LambdaBox(
            lo=lo,
            hi=self.current_upper,
            depth=0,
            box_id=self._next_id("initial"),
        )

    def candidate_is_attemptable(self, candidate: Optional[LambdaBox] = None) -> bool:
        box = candidate or self.current
        return box.width >= self.minimum_width

    def validate_frontier_stop(self, candidate: Optional[LambdaBox] = None) -> None:
        box = candidate or self.current
        valid = (
            box.width < self.minimum_width
            and box.depth == 0
            and not self.stack
            and box.lo == self.lambda_target
            and box.hi == self.current_upper
        )
        if not valid:
            raise ContractReject(
                CheckerFailureReason.FRONTIER_REDERIVATION_MISMATCH,
                "invalid FRONTIER_STOP candidate",
            )

    def can_split(self, box: Optional[LambdaBox] = None) -> bool:
        candidate = box or self.current
        return candidate.depth < self.max_depth and candidate.width / 2 >= self.minimum_width

    def split(
        self,
        *,
        inherited_window: Optional[tuple[Fraction, Fraction]],
    ) -> SplitResult:
        parent = self.current
        if not self.can_split(parent):
            raise ContractReject(
                CheckerFailureReason.FRONTIER_REDERIVATION_MISMATCH,
                "split attempted when forbidden",
            )
        midpoint = (parent.lo + parent.hi) / 2
        mode = (
            PrimaryWindowMode.PARENT_INHERITED
            if inherited_window is not None
            else PrimaryWindowMode.PREDICTOR_AT_ACTIVATION
        )
        upper = LambdaBox(
            lo=midpoint,
            hi=parent.hi,
            depth=parent.depth + 1,
            box_id=self._next_id("upper"),
            parent_box_id=parent.box_id,
            primary_window_mode=mode,
            inherited_window=inherited_window,
        )
        lower = LambdaBox(
            lo=parent.lo,
            hi=midpoint,
            depth=parent.depth + 1,
            box_id=self._next_id("lower"),
            parent_box_id=parent.box_id,
            primary_window_mode=mode,
            inherited_window=inherited_window,
        )
        self.stack.append(lower)
        self.current = upper
        return SplitResult(parent=parent, midpoint=midpoint, upper_child=upper, lower_child=lower)

    def pass_current(self) -> Optional[LambdaBox]:
        passed = self.current
        self.current_upper = passed.lo
        self.lambda_reached = passed.lo
        if self.current_upper == self.lambda_target:
            if self.stack:
                raise ContractReject(
                    CheckerFailureReason.FRONTIER_REDERIVATION_MISMATCH,
                    "target reached with nonempty pending-child stack",
                )
            self.current = passed
            return None
        if self.stack:
            pending = self.stack[-1]
            if pending.hi != self.current_upper:
                raise ContractReject(
                    CheckerFailureReason.FRONTIER_REDERIVATION_MISMATCH,
                    "stack.top.lambda_hi != current_upper",
                )
            self.current = self.stack.pop()
            return self.current
        self.current = self._new_initial_box()
        return self.current

    def fail_current_and_split(
        self,
        *,
        inherited_window: Optional[tuple[Fraction, Fraction]],
    ) -> SplitResult:
        return self.split(inherited_window=inherited_window)
