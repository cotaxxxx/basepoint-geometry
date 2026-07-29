from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, Protocol

from .canonical import ContractReject
from .enums import CheckerFailureReason, CheckerTerminalClass, RecordType
from .frontier import LambdaBox
from .records import Record, RecordGrammarValidator
from .runner import RunnerResult


class FreshEvaluator(Protocol):
    def verify_box(self, box: LambdaBox) -> bool:
        ...


@dataclass(frozen=True)
class CheckerResult:
    terminal_class: CheckerTerminalClass
    failure_reason: CheckerFailureReason | None
    verified_box_ids: tuple[str, ...]


class SweepChecker:
    def __init__(self, fresh_evaluator: FreshEvaluator) -> None:
        self.fresh_evaluator = fresh_evaluator
        self.grammar = RecordGrammarValidator()

    def verify_runner_result(self, result: RunnerResult) -> CheckerResult:
        try:
            self._verify_terminal_consistency(result)
            self._verify_record_segments(result.records)
            self._verify_pass_partition(result.pass_boxes, result.lambda_reached)
            verified = []
            for box in result.pass_boxes:
                if not self.fresh_evaluator.verify_box(box):
                    raise ContractReject(
                        CheckerFailureReason.FRESH_EVALUATION_FAIL,
                        f"fresh evaluation failed: {box.box_id}",
                    )
                verified.append(box.box_id)
            return CheckerResult(
                CheckerTerminalClass.VERIFY_PASS,
                None,
                tuple(verified),
            )
        except ContractReject as exc:
            return CheckerResult(
                CheckerTerminalClass.VERIFY_FAIL,
                exc.reason,
                (),
            )

    def _verify_terminal_consistency(self, result: RunnerResult) -> None:
        types = [record.record_type for record in result.records]
        if result.terminal_class.value == "RUN_FATAL":
            if RecordType.RUN_FATAL not in types:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "RUN_FATAL terminal class without RUN_FATAL record",
                )
            if RecordType.SWEEP_COMPLETE in types or RecordType.SWEEP_INCOMPLETE in types:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "RUN_FATAL mixed with normal sweep verdict",
                )
        elif result.terminal_class.value == "NORMAL_COMPLETE":
            if not types or types[-1] is not RecordType.SWEEP_COMPLETE:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "normal complete does not end with SWEEP_COMPLETE",
                )
        else:
            if not types or types[-1] is not RecordType.SWEEP_INCOMPLETE:
                raise ContractReject(
                    CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                    "normal incomplete does not end with SWEEP_INCOMPLETE",
                )

    def _verify_record_segments(self, records: tuple[Record, ...]) -> None:
        # The full stream is checked by deterministic local patterns.  PASS records
        # may be followed by another box; terminal records close the stream.
        index = 0
        while index < len(records):
            current = records[index]
            if current.record_type is RecordType.SLICE_BOX_PASS:
                if index + 1 < len(records) and records[index + 1].record_type is RecordType.SWEEP_COMPLETE:
                    self.grammar.validate_exact_path("NORMAL_COMPLETE", records[index:index + 2])
                    index += 2
                else:
                    self.grammar.validate_exact_path("PRIMARY_PASS", records[index:index + 1])
                    index += 1
                continue
            if current.record_type is RecordType.FRONTIER_STOP:
                self.grammar.validate_exact_path("FRONTIER_STOP", records[index:index + 2])
                index += 2
                continue
            if current.record_type is RecordType.RUN_FATAL:
                self.grammar.validate_exact_path("RUN_FATAL", records[index:index + 1])
                index += 1
                continue
            if current.record_type is RecordType.BOX_ATTEMPT_FAIL:
                # Determine attempt count and closing path.
                if index + 1 >= len(records):
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "truncated failed-attempt sequence",
                    )
                attempt_count = 1
                if records[index + 1].record_type is RecordType.BOX_ATTEMPT_FAIL:
                    attempt_count = 2
                after = index + attempt_count
                if after >= len(records):
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "truncated failed-attempt sequence",
                    )
                if records[after].record_type is RecordType.SLICE_BOX_PASS:
                    if attempt_count != 1:
                        raise ContractReject(
                            CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                            "regenerated pass must preserve only PRIMARY fail record",
                        )
                    self.grammar.validate_exact_path(
                        "PRIMARY_FAIL_REGENERATED_PASS", records[index:after + 1]
                    )
                    if after + 1 < len(records) and records[after + 1].record_type is RecordType.SWEEP_COMPLETE:
                        index = after + 2
                    else:
                        index = after + 1
                    continue
                if records[after].record_type is not RecordType.SLICE_BOX_FAIL:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "failed attempts not followed by SLICE_BOX_FAIL",
                    )
                if after + 1 >= len(records):
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "SLICE_BOX_FAIL missing next record",
                    )
                next_type = records[after + 1].record_type
                if next_type is RecordType.SPLIT:
                    path = "FAIL_SPLIT_WITH_REGENERATED" if attempt_count == 2 else "FAIL_SPLIT_PRIMARY_ONLY"
                elif next_type is RecordType.SWEEP_INCOMPLETE:
                    last_reason = records[index + attempt_count - 1].payload.get("failure_reason")
                    if last_reason == "GLOBAL_EVAL_LIMIT_REACHED":
                        path = "GLOBAL_STOP_WITH_PRIOR_PRIMARY" if attempt_count == 2 else "GLOBAL_STOP"
                    else:
                        path = "FINAL_FRONTIER_WITH_REGENERATED" if attempt_count == 2 else "FINAL_FRONTIER_PRIMARY_ONLY"
                else:
                    raise ContractReject(
                        CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                        "invalid record after SLICE_BOX_FAIL",
                    )
                self.grammar.validate_exact_path(path, records[index:after + 2])
                index = after + 2
                continue
            raise ContractReject(
                CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
                f"unexpected record at stream position {index}: {current.record_type}",
            )

    def _verify_pass_partition(
        self,
        boxes: tuple[LambdaBox, ...],
        lambda_reached: Fraction,
    ) -> None:
        if not boxes:
            return
        if boxes[0].hi <= boxes[0].lo:
            raise ContractReject(
                CheckerFailureReason.COVERAGE_MANIFEST_VIOLATION,
                "nonpositive first box width",
            )
        for upper, lower in zip(boxes, boxes[1:]):
            if upper.lo != lower.hi:
                raise ContractReject(
                    CheckerFailureReason.COVERAGE_MANIFEST_VIOLATION,
                    "lambda PASS partition gap/overlap",
                )
        if boxes[-1].lo != lambda_reached:
            raise ContractReject(
                CheckerFailureReason.COVERAGE_MANIFEST_VIOLATION,
                "lambda_reached does not equal lower PASS endpoint",
            )
