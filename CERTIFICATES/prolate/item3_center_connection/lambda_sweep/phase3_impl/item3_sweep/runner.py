from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Protocol

from .budget import BudgetStop, EvaluationBudget
from .enums import (
    AttemptStage,
    RecordType,
    RunnerFailureReason,
    RunnerTerminalClass,
    WindowOrigin,
)
from .frontier import FrontierMachine, LambdaBox
from .records import Record
from .transitions import FailureClass, may_regenerate, transition_for
from .windows import GeneratedWindow, PredictorContext, WindowGenerationError, generate_window


@dataclass(frozen=True)
class AttemptOutcome:
    passed: bool
    failure_reason: Optional[RunnerFailureReason] = None
    primary_window_constructed: bool = True

    @classmethod
    def pass_(cls) -> "AttemptOutcome":
        return cls(True, None, True)

    @classmethod
    def fail(
        cls,
        reason: RunnerFailureReason,
        *,
        primary_window_constructed: bool = True,
    ) -> "AttemptOutcome":
        return cls(False, reason, primary_window_constructed)


class AttemptEvaluator(Protocol):
    """Phase-3 injected evaluator.

    Production implementations may call Arb only through a pinned adapter.  The
    Phase-3 source tests use deterministic fakes and perform no mathematics.
    """

    def evaluate(
        self,
        *,
        box: LambdaBox,
        window: tuple[Fraction, Fraction],
        stage: AttemptStage,
        budget: EvaluationBudget,
    ) -> AttemptOutcome:
        ...


@dataclass(frozen=True)
class RunnerResult:
    terminal_class: RunnerTerminalClass
    records: tuple[Record, ...]
    lambda_reached: Fraction
    pass_boxes: tuple[LambdaBox, ...]


class SweepRunner:
    def __init__(
        self,
        *,
        frontier: FrontierMachine,
        budget: EvaluationBudget,
        evaluator: AttemptEvaluator,
        grid: Fraction,
        minimum_window_width: Fraction,
        delta_overlap_min: Fraction,
        anchor_seed_window: tuple[Fraction, Fraction],
        predictor_points: list,
    ) -> None:
        self.frontier = frontier
        self.budget = budget
        self.evaluator = evaluator
        self.grid = grid
        self.minimum_window_width = minimum_window_width
        self.delta_overlap_min = delta_overlap_min
        self.anchor_seed_window = anchor_seed_window
        self.predictor_points = predictor_points
        self.records: list[Record] = []
        self.pass_boxes: list[LambdaBox] = []
        self.pass_windows: list[tuple[Fraction, Fraction]] = []
        self._first_box = True

    def _capture_predictor_context(self) -> PredictorContext:
        return PredictorContext.capture(self.predictor_points)

    def _build_primary_window(
        self,
        box: LambdaBox,
        context: PredictorContext,
    ) -> tuple[tuple[Fraction, Fraction], WindowOrigin, bool]:
        if self._first_box:
            return self.anchor_seed_window, WindowOrigin.CONFIG_SEED, True
        if box.inherited_window is not None:
            return box.inherited_window, WindowOrigin.PARENT_INHERITED, True
        previous = self.pass_windows[-1] if self.pass_windows else self.anchor_seed_window
        q = context.evaluate(box.hi)
        generated = generate_window(
            q=q,
            origin=context.origin,
            grid=self.grid,
            minimum_width=self.minimum_window_width,
            previous_window=previous,
            delta_overlap_min=self.delta_overlap_min,
        )
        return (generated.lo, generated.hi), generated.origin, True

    @staticmethod
    def _fraction_object(value: Fraction) -> dict[str, str]:
        return {"p": str(value.numerator), "q": str(value.denominator)}

    @classmethod
    def _box_object(cls, box: LambdaBox) -> dict[str, object]:
        return {
            "box_id": box.box_id,
            "lambda_lo": cls._fraction_object(box.lo),
            "lambda_hi": cls._fraction_object(box.hi),
            "depth": box.depth,
            "parent_box_id": box.parent_box_id,
            "primary_window_mode": box.primary_window_mode.value,
            "inherited_window": (
                [cls._fraction_object(box.inherited_window[0]), cls._fraction_object(box.inherited_window[1])]
                if box.inherited_window is not None else None
            ),
        }

    @classmethod
    def _split_payload(cls, split) -> dict[str, object]:
        return {
            "parent": cls._box_object(split.parent),
            "parent_depth": split.parent.depth,
            "midpoint": cls._fraction_object(split.midpoint),
            "upper_child": cls._box_object(split.upper_child),
            "lower_child": cls._box_object(split.lower_child),
            "children_per_box_counter_start": 0,
        }

    def _incomplete_record(self) -> Record:
        return Record(
            RecordType.SWEEP_INCOMPLETE,
            {
                "runner_terminal_class": RunnerTerminalClass.NORMAL_INCOMPLETE.value,
                "lambda_reached": self._fraction_object(self.frontier.lambda_reached),
                "stack_size": len(self.frontier.stack),
            },
        )

    def _complete_record(self) -> Record:
        return Record(
            RecordType.SWEEP_COMPLETE,
            {
                "runner_terminal_class": RunnerTerminalClass.NORMAL_COMPLETE.value,
                "lambda_reached": self._fraction_object(self.frontier.lambda_reached),
                "stack_size": len(self.frontier.stack),
            },
        )

    def _fatal_record(self, *, reason: RunnerFailureReason, location: str) -> Record:
        return Record(
            RecordType.RUN_FATAL,
            {
                "reason": reason.value,
                "detection_location": location,
                "diagnostic_state": {
                    "lambda_reached": self._fraction_object(self.frontier.lambda_reached),
                    "stack_size": len(self.frontier.stack),
                },
                "manifest_emitted": False,
                "sweep_verdict": None,
            },
        )

    def _attempt_fail_record(
        self,
        *,
        box: LambdaBox,
        stage: AttemptStage,
        origin: WindowOrigin,
        reason: RunnerFailureReason,
        context: PredictorContext,
        primary_window_constructed: bool,
    ) -> Record:
        return Record(
            RecordType.BOX_ATTEMPT_FAIL,
            {
                "box": self._box_object(box),
                "box_id": box.box_id,
                "attempt_stage": stage.value,
                "window_origin": origin.value,
                "depth": box.depth,
                "failure_reason": reason.value,
                "failure_location": "PREP" if not primary_window_constructed else "A0_A7",
                "counters": self.budget.counters(),
                "fixed_budget": {
                    "global_eval_limit": self.budget.global_limit,
                    "per_box_eval_limit": self.budget.per_box_limit,
                },
                "predictor_context_sha256": context.canonical_sha256(),
                "primary_window_constructed": primary_window_constructed,
            },
        )

    def _evaluate_attempt(
        self,
        *,
        box: LambdaBox,
        window: tuple[Fraction, Fraction],
        stage: AttemptStage,
    ) -> AttemptOutcome:
        self.budget.start_attempt()
        try:
            return self.evaluator.evaluate(
                box=box,
                window=window,
                stage=stage,
                budget=self.budget,
            )
        except BudgetStop as stop:
            return AttemptOutcome.fail(stop.reason)

    def run(self, *, max_boxes: int = 10000) -> RunnerResult:
        processed = 0
        while processed < max_boxes:
            processed += 1
            box = self.frontier.current
            if not self.frontier.candidate_is_attemptable(box):
                self.frontier.validate_frontier_stop(box)
                self.records.extend(
                    [
                        Record(
                            RecordType.FRONTIER_STOP,
                            {
                                "reason": "LAMBDA_WIDTH_BELOW_MINIMUM",
                                "box": self._box_object(box),
                                "box_id": box.box_id,
                                "depth": 0,
                            },
                        ),
                        self._incomplete_record(),
                    ]
                )
                return RunnerResult(
                    RunnerTerminalClass.NORMAL_INCOMPLETE,
                    tuple(self.records),
                    self.frontier.lambda_reached,
                    tuple(self.pass_boxes),
                )

            context = self._capture_predictor_context()
            try:
                primary_window, primary_origin, primary_constructed = self._build_primary_window(box, context)
            except WindowGenerationError as exc:
                # PREP failures consume exactly zero evaluations.
                self.budget.start_attempt()
                self.records.append(
                    self._attempt_fail_record(
                        box=box,
                        stage=AttemptStage.PRIMARY,
                        origin=context.origin,
                        reason=exc.reason,
                        context=context,
                        primary_window_constructed=False,
                    )
                )
                self.records.append(Record(RecordType.SLICE_BOX_FAIL, {"box_id": box.box_id}))
                if self.frontier.can_split(box):
                    split = self.frontier.fail_current_and_split(inherited_window=None)
                    self.budget.start_child_box()
                    self.records.append(
                        Record(
                            RecordType.SPLIT,
                            self._split_payload(split),
                        )
                    )
                    self._first_box = False
                    continue
                self.records.append(
                    self._incomplete_record()
                )
                return RunnerResult(
                    RunnerTerminalClass.NORMAL_INCOMPLETE,
                    tuple(self.records),
                    self.frontier.lambda_reached,
                    tuple(self.pass_boxes),
                )

            primary = self._evaluate_attempt(
                box=box,
                window=primary_window,
                stage=AttemptStage.PRIMARY,
            )
            if primary.passed:
                self._accept_pass(box, primary_window)
                result = self._advance_after_pass()
                if result is not None:
                    return result
                self._first_box = False
                continue

            assert primary.failure_reason is not None
            transition = transition_for(primary.failure_reason)

            if transition.failure_class is FailureClass.RUN_FATAL:
                self.records.append(
                    self._fatal_record(
                        reason=primary.failure_reason, location="PRIMARY_ATTEMPT"
                    )
                )
                return RunnerResult(
                    RunnerTerminalClass.RUN_FATAL,
                    tuple(self.records),
                    self.frontier.lambda_reached,
                    tuple(self.pass_boxes),
                )

            self.records.append(
                self._attempt_fail_record(
                    box=box,
                    stage=AttemptStage.PRIMARY,
                    origin=primary_origin,
                    reason=primary.failure_reason,
                    context=context,
                    primary_window_constructed=primary.primary_window_constructed,
                )
            )

            if transition.failure_class is FailureClass.GLOBAL_STOP:
                self.records.extend(
                    [
                        Record(RecordType.SLICE_BOX_FAIL, {"box_id": box.box_id}),
                        self._incomplete_record(),
                    ]
                )
                return RunnerResult(
                    RunnerTerminalClass.NORMAL_INCOMPLETE,
                    tuple(self.records),
                    self.frontier.lambda_reached,
                    tuple(self.pass_boxes),
                )

            regenerated_count = 0
            regenerated_outcome: Optional[AttemptOutcome] = None
            if may_regenerate(
                reason=primary.failure_reason,
                attempt_stage=AttemptStage.PRIMARY,
                window_origin=primary_origin,
                per_box_remaining=self.budget.per_box_remaining,
                regenerated_count=regenerated_count,
            ):
                regenerated_count += 1
                q = context.evaluate(box.hi)
                previous = self.pass_windows[-1] if self.pass_windows else self.anchor_seed_window
                try:
                    generated = generate_window(
                        q=q,
                        origin=context.origin,
                        grid=self.grid,
                        minimum_width=self.minimum_window_width,
                        previous_window=previous,
                        delta_overlap_min=self.delta_overlap_min,
                    )
                    regenerated_window = (generated.lo, generated.hi)
                    regenerated_outcome = self._evaluate_attempt(
                        box=box,
                        window=regenerated_window,
                        stage=AttemptStage.REGENERATED,
                    )
                except WindowGenerationError as exc:
                    self.budget.start_attempt()
                    regenerated_outcome = AttemptOutcome.fail(
                        exc.reason, primary_window_constructed=True
                    )

                if regenerated_outcome.passed:
                    self._accept_pass(box, regenerated_window)
                    result = self._advance_after_pass()
                    if result is not None:
                        return result
                    self._first_box = False
                    continue

                assert regenerated_outcome.failure_reason is not None
                regenerated_transition = transition_for(regenerated_outcome.failure_reason)
                if regenerated_transition.failure_class is FailureClass.RUN_FATAL:
                    self.records.append(
                        self._fatal_record(
                            reason=regenerated_outcome.failure_reason,
                            location="REGENERATED_ATTEMPT",
                        )
                    )
                    return RunnerResult(
                        RunnerTerminalClass.RUN_FATAL,
                        tuple(self.records),
                        self.frontier.lambda_reached,
                        tuple(self.pass_boxes),
                    )

                self.records.append(
                    self._attempt_fail_record(
                        box=box,
                        stage=AttemptStage.REGENERATED,
                        origin=context.origin,
                        reason=regenerated_outcome.failure_reason,
                        context=context,
                        primary_window_constructed=True,
                    )
                )
                if regenerated_transition.failure_class is FailureClass.GLOBAL_STOP:
                    self.records.extend(
                        [
                            Record(RecordType.SLICE_BOX_FAIL, {"box_id": box.box_id}),
                            self._incomplete_record(),
                        ]
                    )
                    return RunnerResult(
                        RunnerTerminalClass.NORMAL_INCOMPLETE,
                        tuple(self.records),
                        self.frontier.lambda_reached,
                        tuple(self.pass_boxes),
                    )

            self.records.append(Record(RecordType.SLICE_BOX_FAIL, {"box_id": box.box_id}))
            if self.frontier.can_split(box):
                inherited = primary_window if primary.primary_window_constructed else None
                split = self.frontier.fail_current_and_split(inherited_window=inherited)
                self.budget.start_child_box()
                self.records.append(
                    Record(
                        RecordType.SPLIT,
                        self._split_payload(split),
                    )
                )
                self._first_box = False
                continue
            self.records.append(
                self._incomplete_record()
            )
            return RunnerResult(
                RunnerTerminalClass.NORMAL_INCOMPLETE,
                tuple(self.records),
                self.frontier.lambda_reached,
                tuple(self.pass_boxes),
            )
        raise RuntimeError("max_boxes safety bound exceeded")

    def _accept_pass(self, box: LambdaBox, window: tuple[Fraction, Fraction]) -> None:
        if self.pass_windows:
            previous = self.pass_windows[-1]
            overlap_lo = max(previous[0], window[0])
            overlap_hi = min(previous[1], window[1])
            if overlap_lo >= overlap_hi:
                raise RuntimeError("accepted adjacent windows must have positive overlap")
            from .windows import PredictorPoint
            self.predictor_points.append(
                PredictorPoint(
                    lambda_value=box.hi,
                    root_midpoint=(overlap_lo + overlap_hi) / 2,
                    source_box_id=box.box_id,
                    source_overlap=(overlap_lo, overlap_hi),
                )
            )
        self.pass_boxes.append(box)
        self.pass_windows.append(window)
        self.records.append(
            Record(
                RecordType.SLICE_BOX_PASS,
                {
                    "box": self._box_object(box),
                    "box_id": box.box_id,
                    "window": [self._fraction_object(window[0]), self._fraction_object(window[1])],
                },
            )
        )

    def _advance_after_pass(self) -> Optional[RunnerResult]:
        next_box = self.frontier.pass_current()
        if next_box is None:
            self.records.append(
                self._complete_record()
            )
            return RunnerResult(
                RunnerTerminalClass.NORMAL_COMPLETE,
                tuple(self.records),
                self.frontier.lambda_reached,
                tuple(self.pass_boxes),
            )
        if next_box.parent_box_id is not None:
            self.budget.start_child_box()
        return None
