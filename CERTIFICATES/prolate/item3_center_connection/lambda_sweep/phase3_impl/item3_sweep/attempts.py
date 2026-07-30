from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Optional

from .adapter import CanonicalInterval, PinnedKernelAdapter
from .budget import BudgetStop, EvaluationBudget
from .canonical import ContractReject
from .enums import AttemptStage, RunnerFailureReason
from .frontier import LambdaBox
from .r_tile import RCell, RTileFailure, RTileResult, adaptive_r_bisection
from .runner import AttemptOutcome


@dataclass(frozen=True)
class AttemptEvidence:
    box_id: str
    stage: AttemptStage
    window: tuple[Fraction, Fraction]
    s1: CanonicalInterval
    s2: CanonicalInterval
    r_tile: RTileResult
    derivative_intervals: tuple[CanonicalInterval, ...]
    overlap_width: Fraction
    anchor_icg_contained: bool


@dataclass(frozen=True)
class AttemptStructuralContext:
    previous_window: tuple[Fraction, Fraction]
    delta_overlap_min: Fraction
    is_anchor_leaf: bool
    require_icg_hull: bool
    icg_hull: tuple[Fraction, Fraction] = (Fraction(1, 64), Fraction(11, 256))


class CertifiedAttemptEvaluator:
    """A0-A7 orchestration with a pinned adapter boundary.

    The adapter may use Arb in production.  This orchestrator only enforces the
    frozen contract's order, budget, canonical-enclosure, sign and r-tile rules.
    """

    def __init__(
        self,
        *,
        adapter: PinnedKernelAdapter,
        dps: int,
        max_r_cells_per_box: int,
        context_provider: Callable[[LambdaBox], AttemptStructuralContext],
    ) -> None:
        self.adapter = adapter
        self.dps = dps
        self.max_r_cells_per_box = max_r_cells_per_box
        self.context_provider = context_provider
        self.evidence: dict[tuple[str, AttemptStage], AttemptEvidence] = {}

    def _call_g(
        self,
        budget: EvaluationBudget,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
    ) -> CanonicalInterval:
        budget.before_call()
        try:
            interval = self.adapter.evaluate_g(r=r, lambda_box=lambda_box, dps=self.dps)
        finally:
            # Any entered adapter call counts, including exceptions.
            budget.count_executed_call()
        interval.round_trip_bytes()
        if not interval.finite:
            raise _AttemptFailure(RunnerFailureReason.NONFINITE_ENCLOSURE)
        return interval

    def _call_gr(
        self,
        budget: EvaluationBudget,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
    ) -> CanonicalInterval:
        budget.before_call()
        try:
            interval = self.adapter.evaluate_gr(r=r, lambda_box=lambda_box, dps=self.dps)
        finally:
            budget.count_executed_call()
        interval.round_trip_bytes()
        return interval

    def evaluate(
        self,
        *,
        box: LambdaBox,
        window: tuple[Fraction, Fraction],
        stage: AttemptStage,
        budget: EvaluationBudget,
    ) -> AttemptOutcome:
        context = self.context_provider(box)
        lambda_box = (box.lo, box.hi)
        derivative_by_cell: dict[tuple[Fraction, Fraction], CanonicalInterval] = {}
        try:
            s1 = self._call_g(budget, r=(window[0], window[0]), lambda_box=lambda_box)
            if not s1.strictly_positive():
                raise _AttemptFailure(RunnerFailureReason.STRICT_SIGN_FAIL)
            s2 = self._call_g(budget, r=(window[1], window[1]), lambda_box=lambda_box)
            if not s2.strictly_negative():
                raise _AttemptFailure(RunnerFailureReason.STRICT_SIGN_FAIL)

            class Oracle:
                def strict_negative(_, cell: RCell) -> bool:
                    interval = self._call_gr(
                        budget,
                        r=(cell.lo, cell.hi),
                        lambda_box=lambda_box,
                    )
                    derivative_by_cell[(cell.lo, cell.hi)] = interval
                    return interval.strictly_negative()

            r_tile = adaptive_r_bisection(
                RCell(window[0], window[1]),
                Oracle(),
                max_r_cells_per_box=self.max_r_cells_per_box,
            )
            overlap_lo = max(window[0], context.previous_window[0])
            overlap_hi = min(window[1], context.previous_window[1])
            overlap_width = max(Fraction(0), overlap_hi - overlap_lo)
            if overlap_width < context.delta_overlap_min:
                reason = (
                    RunnerFailureReason.INHERITED_OVERLAP_INSUFFICIENT
                    if box.inherited_window is not None
                    else RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE
                )
                raise _AttemptFailure(reason)
            icg_contained = window[0] <= context.icg_hull[0] <= context.icg_hull[1] <= window[1]
            if context.is_anchor_leaf and context.require_icg_hull and not icg_contained:
                raise _AttemptFailure(RunnerFailureReason.ICG_NOT_CONTAINED)
            self.evidence[(box.box_id, stage)] = AttemptEvidence(
                box_id=box.box_id,
                stage=stage,
                window=window,
                s1=s1,
                s2=s2,
                r_tile=r_tile,
                derivative_intervals=tuple(
                    derivative_by_cell[(cell.lo, cell.hi)] for cell in r_tile.accepted_leaves
                ),
                overlap_width=overlap_width,
                anchor_icg_contained=icg_contained,
            )
            return AttemptOutcome.pass_()
        except (ContractReject, ValueError):
            return AttemptOutcome.fail(RunnerFailureReason.NONCANONICAL_ENCODING)
        except BudgetStop as exc:
            return AttemptOutcome.fail(exc.reason)
        except RTileFailure as exc:
            return AttemptOutcome.fail(exc.reason)
        except _AttemptFailure as exc:
            return AttemptOutcome.fail(exc.reason)


class _AttemptFailure(RuntimeError):
    def __init__(self, reason: RunnerFailureReason):
        super().__init__(reason.value)
        self.reason = reason
