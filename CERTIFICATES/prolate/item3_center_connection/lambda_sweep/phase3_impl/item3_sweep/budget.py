from __future__ import annotations

from dataclasses import dataclass

from .enums import RunnerFailureReason


class BudgetStop(RuntimeError):
    def __init__(self, reason: RunnerFailureReason):
        super().__init__(reason.value)
        self.reason = reason


@dataclass
class EvaluationBudget:
    global_limit: int
    per_box_limit: int
    global_used: int = 0
    box_used: int = 0
    attempt_used: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.global_limit, int) or isinstance(self.global_limit, bool) or self.global_limit <= 0:
            raise ValueError("global_limit must be a positive integer")
        if not isinstance(self.per_box_limit, int) or isinstance(self.per_box_limit, bool) or self.per_box_limit <= 0:
            raise ValueError("per_box_limit must be a positive integer")
        if self.per_box_limit > self.global_limit:
            raise ValueError("per_box_limit must not exceed global_limit")
        for name, value in {
            "global_used": self.global_used,
            "box_used": self.box_used,
            "attempt_used": self.attempt_used,
        }.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.global_used > self.global_limit or self.box_used > self.per_box_limit:
            raise ValueError("initial evaluation counters exceed fixed limits")
        if self.attempt_used > self.box_used or self.box_used > self.global_used:
            raise ValueError("initial evaluation counters are not cumulative")

    def start_attempt(self) -> None:
        self.attempt_used = 0

    def start_child_box(self) -> None:
        self.box_used = 0
        self.attempt_used = 0

    def before_call(self) -> None:
        # Contractual priority: global, then per-box.
        if self.global_used + 1 > self.global_limit:
            raise BudgetStop(RunnerFailureReason.GLOBAL_EVAL_LIMIT_REACHED)
        if self.box_used + 1 > self.per_box_limit:
            raise BudgetStop(RunnerFailureReason.PER_BOX_EVAL_LIMIT_REACHED)

    def count_executed_call(self) -> None:
        self.global_used += 1
        self.box_used += 1
        self.attempt_used += 1

    @property
    def per_box_remaining(self) -> int:
        return max(0, self.per_box_limit - self.box_used)

    def counters(self) -> dict[str, int]:
        return {
            "attempt_evaluations_used": self.attempt_used,
            "box_evaluations_used_cumulative": self.box_used,
            "global_evaluations_used_cumulative": self.global_used,
        }
