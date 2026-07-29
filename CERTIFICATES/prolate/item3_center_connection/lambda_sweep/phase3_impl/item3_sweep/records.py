from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .canonical import CanonicalRational, ContractReject, validate_sha256
from .enums import (
    AttemptStage,
    CheckerFailureReason,
    RecordType,
    PrimaryWindowMode,
    RunnerFailureReason,
    RunnerTerminalClass,
    WindowOrigin,
)


@dataclass(frozen=True)
class Record:
    record_type: RecordType
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationCounters:
    attempt_evaluations_used: int
    box_evaluations_used_cumulative: int
    global_evaluations_used_cumulative: int

    def validate(self) -> None:
        values = (
            self.attempt_evaluations_used,
            self.box_evaluations_used_cumulative,
            self.global_evaluations_used_cumulative,
        )
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                "evaluation counters must be nonnegative integers",
            )
        if self.attempt_evaluations_used > self.box_evaluations_used_cumulative:
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                "attempt counter exceeds box counter",
            )
        if self.box_evaluations_used_cumulative > self.global_evaluations_used_cumulative:
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                "box counter exceeds global counter",
            )


NORMAL_PATHS: dict[str, tuple[RecordType, ...]] = {
    "PRIMARY_PASS": (RecordType.SLICE_BOX_PASS,),
    "PRIMARY_FAIL_REGENERATED_PASS": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_PASS,
    ),
    "FAIL_SPLIT_PRIMARY_ONLY": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SPLIT,
    ),
    "FAIL_SPLIT_WITH_REGENERATED": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SPLIT,
    ),
    "FINAL_FRONTIER_PRIMARY_ONLY": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SWEEP_INCOMPLETE,
    ),
    "FINAL_FRONTIER_WITH_REGENERATED": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SWEEP_INCOMPLETE,
    ),
    "GLOBAL_STOP": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SWEEP_INCOMPLETE,
    ),
    "GLOBAL_STOP_WITH_PRIOR_PRIMARY": (
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.BOX_ATTEMPT_FAIL,
        RecordType.SLICE_BOX_FAIL,
        RecordType.SWEEP_INCOMPLETE,
    ),
    "FRONTIER_STOP": (
        RecordType.FRONTIER_STOP,
        RecordType.SWEEP_INCOMPLETE,
    ),
    "RUN_FATAL": (RecordType.RUN_FATAL,),
    "NORMAL_COMPLETE": (
        RecordType.SLICE_BOX_PASS,
        RecordType.SWEEP_COMPLETE,
    ),
}


class RecordGrammarValidator:
    def validate_exact_path(self, path_name: str, records: Iterable[Record]) -> None:
        records_tuple = tuple(records)
        expected = NORMAL_PATHS.get(path_name)
        if expected is None:
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                f"unknown grammar path: {path_name}",
            )
        actual = tuple(record.record_type for record in records_tuple)
        if actual != expected:
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                f"record sequence mismatch: expected={expected}, actual={actual}",
            )
        self._validate_payloads(path_name, records_tuple)

    def _validate_payloads(self, path_name: str, records: tuple[Record, ...]) -> None:
        attempt_records = [r for r in records if r.record_type is RecordType.BOX_ATTEMPT_FAIL]
        seen_stages: list[AttemptStage] = []
        for record in attempt_records:
            payload = record.payload
            required = {
                "box",
                "box_id",
                "attempt_stage",
                "window_origin",
                "depth",
                "failure_reason",
                "failure_location",
                "counters",
                "fixed_budget",
                "predictor_context_sha256",
                "primary_window_constructed",
            }
            if not required <= set(payload):
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "BOX_ATTEMPT_FAIL missing required fields",
                )
            try:
                stage = AttemptStage(payload["attempt_stage"])
                WindowOrigin(payload["window_origin"])
                RunnerFailureReason(payload["failure_reason"])
            except ValueError as exc:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "invalid closed-enum value",
                ) from exc
            counters = payload["counters"]
            EvaluationCounters(**counters).validate()
            fixed_budget = payload["fixed_budget"]
            if set(fixed_budget) != {"global_eval_limit", "per_box_eval_limit"}:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "fixed budget field mismatch",
                )
            if (
                not isinstance(fixed_budget["global_eval_limit"], int)
                or not isinstance(fixed_budget["per_box_eval_limit"], int)
                or fixed_budget["per_box_eval_limit"] > fixed_budget["global_eval_limit"]
            ):
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "invalid fixed budget values",
                )
            validate_sha256(payload["predictor_context_sha256"], "predictor_context_sha256")
            if payload["box_id"] != payload["box"].get("box_id") or payload["depth"] != payload["box"].get("depth"):
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "box duplicate fields mismatch",
                )
            seen_stages.append(stage)

        if seen_stages:
            if seen_stages[0] is not AttemptStage.PRIMARY:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "first failed attempt must be PRIMARY",
                )
            if len(seen_stages) > 1 and seen_stages != [AttemptStage.PRIMARY, AttemptStage.REGENERATED]:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "failed attempt stage order mismatch",
                )

            if len(attempt_records) > 1:
                primary_payload = attempt_records[0].payload
                if primary_payload["window_origin"] in {
                    WindowOrigin.PREDICTOR_HORIZONTAL.value,
                    WindowOrigin.PREDICTOR_LINEAR.value,
                }:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "predictor-derived PRIMARY must not regenerate",
                    )
                if primary_payload["failure_reason"] not in {
                    RunnerFailureReason.STRICT_SIGN_FAIL.value,
                    RunnerFailureReason.NONFINITE_ENCLOSURE.value,
                    RunnerFailureReason.INHERITED_OVERLAP_INSUFFICIENT.value,
                    RunnerFailureReason.ICG_NOT_CONTAINED.value,
                }:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "PRIMARY failure reason does not permit regeneration",
                    )

        for record in attempt_records:
            if record.payload["failure_reason"] in {
                RunnerFailureReason.WINDOW_GENERATION_FAIL.value,
                RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE.value,
            } and record.payload["counters"]["attempt_evaluations_used"] != 0:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "PREP failure must use exactly zero evaluations",
                )

        for record in records:
            if record.record_type is RecordType.SPLIT:
                payload = record.payload
                required = {
                    "parent", "parent_depth", "midpoint", "upper_child",
                    "lower_child", "children_per_box_counter_start",
                }
                if set(payload) != required or payload["children_per_box_counter_start"] != 0:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SPLIT payload schema/counter mismatch",
                    )
                parent = payload["parent"]
                upper = payload["upper_child"]
                lower = payload["lower_child"]
                midpoint = CanonicalRational.from_object(payload["midpoint"], "split.midpoint").value
                p_lo = CanonicalRational.from_object(parent["lambda_lo"], "parent.lo").value
                p_hi = CanonicalRational.from_object(parent["lambda_hi"], "parent.hi").value
                u_lo = CanonicalRational.from_object(upper["lambda_lo"], "upper.lo").value
                u_hi = CanonicalRational.from_object(upper["lambda_hi"], "upper.hi").value
                l_lo = CanonicalRational.from_object(lower["lambda_lo"], "lower.lo").value
                l_hi = CanonicalRational.from_object(lower["lambda_hi"], "lower.hi").value
                if midpoint != (p_lo + p_hi) / 2 or (u_lo, u_hi) != (midpoint, p_hi) or (l_lo, l_hi) != (p_lo, midpoint):
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SPLIT child endpoint mismatch",
                    )
                if payload["parent_depth"] != parent["depth"] or upper["depth"] != parent["depth"] + 1 or lower["depth"] != parent["depth"] + 1:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SPLIT child depth mismatch",
                    )
                try:
                    PrimaryWindowMode(upper["primary_window_mode"])
                    PrimaryWindowMode(lower["primary_window_mode"])
                except ValueError as exc:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SPLIT child window mode invalid",
                    ) from exc
            elif record.record_type is RecordType.SWEEP_COMPLETE:
                if record.payload.get("runner_terminal_class") != RunnerTerminalClass.NORMAL_COMPLETE.value or record.payload.get("stack_size") != 0:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SWEEP_COMPLETE terminal payload mismatch",
                    )
            elif record.record_type is RecordType.SWEEP_INCOMPLETE:
                if record.payload.get("runner_terminal_class") != RunnerTerminalClass.NORMAL_INCOMPLETE.value:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SWEEP_INCOMPLETE terminal payload mismatch",
                    )

        if path_name in {"GLOBAL_STOP", "GLOBAL_STOP_WITH_PRIOR_PRIMARY"}:
            if not attempt_records or attempt_records[-1].payload["failure_reason"] != RunnerFailureReason.GLOBAL_EVAL_LIMIT_REACHED.value:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "GLOBAL_STOP reason mismatch",
                )
        if path_name == "FRONTIER_STOP":
            payload = records[0].payload
            forbidden = {"attempt_stage", "window_origin", "counters"}
            if forbidden & set(payload) or payload.get("depth") != 0:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "FRONTIER_STOP contains attempt fields or nonzero depth",
                )
        if path_name == "RUN_FATAL":
            payload = records[0].payload
            if payload.get("manifest_emitted", False) or payload.get("sweep_verdict") is not None:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "RUN_FATAL must not emit manifest or sweep verdict",
                )
        if path_name == "NORMAL_COMPLETE":
            if records[-1].payload.get("runner_terminal_class") not in {None, RunnerTerminalClass.NORMAL_COMPLETE.value}:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "SWEEP_COMPLETE terminal class mismatch",
                )
