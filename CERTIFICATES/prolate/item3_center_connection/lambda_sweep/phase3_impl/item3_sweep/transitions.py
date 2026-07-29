from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .enums import AttemptStage, RunnerFailureReason, WindowOrigin


class FailureClass(str, Enum):
    RUN_FATAL = "RUN_FATAL"
    BOX_RETRYABLE = "BOX_RETRYABLE"
    GLOBAL_STOP = "GLOBAL_STOP"


class RegenerationPolicy(str, Enum):
    NEVER = "NEVER"
    YES_STAR = "YES_STAR"


@dataclass(frozen=True)
class Transition:
    failure_class: FailureClass
    regeneration: RegenerationPolicy
    next_state: str


_RUN_FATAL = {
    RunnerFailureReason.NONCANONICAL_ENCODING,
    RunnerFailureReason.HASH_ORIGIN_MISMATCH,
    RunnerFailureReason.LOGICAL_DEPENDENCY_GATE_VIOLATION,
    RunnerFailureReason.SCHEMA_VIOLATION,
    RunnerFailureReason.COVERAGE_STRUCTURE_VIOLATION,
    RunnerFailureReason.SHARED_ENDPOINT_BYTES_MISMATCH,
    RunnerFailureReason.KERNEL_IDENTITY_MISMATCH,
    RunnerFailureReason.REQUIRED_STORED_RECORD_MISSING,
    RunnerFailureReason.INTERNAL_INCONSISTENCY,
    RunnerFailureReason.ANCHOR_PREDICATE_VIOLATION,
    RunnerFailureReason.SNAPSHOT_MISMATCH,
    RunnerFailureReason.PILOT_IDENTITY_MISMATCH,
    RunnerFailureReason.DESIGN_IDENTITY_MISMATCH,
}

_RETRY_YES_STAR = {
    RunnerFailureReason.STRICT_SIGN_FAIL,
    RunnerFailureReason.NONFINITE_ENCLOSURE,
    RunnerFailureReason.INHERITED_OVERLAP_INSUFFICIENT,
    RunnerFailureReason.ICG_NOT_CONTAINED,
}

_RETRY_NO = {
    RunnerFailureReason.WINDOW_GENERATION_FAIL,
    RunnerFailureReason.WINDOW_OVERLAP_IMPOSSIBLE,
    RunnerFailureReason.R_CELL_BUDGET_EXCEEDED,
    RunnerFailureReason.PER_BOX_EVAL_LIMIT_REACHED,
}


TRANSITIONS: dict[RunnerFailureReason, Transition] = {}
for reason in _RUN_FATAL:
    TRANSITIONS[reason] = Transition(FailureClass.RUN_FATAL, RegenerationPolicy.NEVER, "RUN_FATAL")
for reason in _RETRY_YES_STAR:
    TRANSITIONS[reason] = Transition(FailureClass.BOX_RETRYABLE, RegenerationPolicy.YES_STAR, "ATTEMPT_STATE_MACHINE")
for reason in _RETRY_NO:
    TRANSITIONS[reason] = Transition(FailureClass.BOX_RETRYABLE, RegenerationPolicy.NEVER, "SLICE_BOX_FAIL")
TRANSITIONS[RunnerFailureReason.GLOBAL_EVAL_LIMIT_REACHED] = Transition(
    FailureClass.GLOBAL_STOP,
    RegenerationPolicy.NEVER,
    "GLOBAL_STOP",
)

if set(TRANSITIONS) != set(RunnerFailureReason):
    raise RuntimeError("failure transition table is not closed")


def may_regenerate(
    *,
    reason: RunnerFailureReason,
    attempt_stage: AttemptStage,
    window_origin: WindowOrigin,
    per_box_remaining: int,
    regenerated_count: int,
) -> bool:
    transition = TRANSITIONS[reason]
    return (
        transition.regeneration is RegenerationPolicy.YES_STAR
        and attempt_stage is AttemptStage.PRIMARY
        and window_origin in {WindowOrigin.CONFIG_SEED, WindowOrigin.PARENT_INHERITED}
        and per_box_remaining > 0
        and regenerated_count == 0
    )


def transition_for(reason: RunnerFailureReason) -> Transition:
    return TRANSITIONS[reason]
