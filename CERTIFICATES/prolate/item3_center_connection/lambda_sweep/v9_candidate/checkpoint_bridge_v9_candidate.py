#!/usr/bin/env python3
"""Canonical bridge from runner ProgressSnapshot to checkpoint transaction payloads.

STATUS: IMPLEMENTATION CANDIDATE / PROVENANCE ONLY / NO RESUME.

The bridge is dependency-injected: it does not import runner or checkpoint source.  The
source-bound driver supplies a validated CheckpointStore and CheckpointCadence instance.
"""
from __future__ import annotations

from fractions import Fraction
import time
from typing import Any


BRIDGE_ID = "ITEM3_SWEEP_V9_CHECKPOINT_BRIDGE_CANDIDATE_V1"


class BridgeContractError(RuntimeError):
    pass


def frac(value: Fraction) -> dict[str, str]:
    if not isinstance(value, Fraction):
        raise BridgeContractError("expected Fraction")
    return {"p": str(value.numerator), "q": str(value.denominator)}


def interval(value: tuple[Fraction, Fraction]) -> list[dict[str, str]]:
    if not isinstance(value, tuple) or len(value) != 2:
        raise BridgeContractError("expected interval tuple")
    return [frac(value[0]), frac(value[1])]


def maybe_frac(value: Fraction | None) -> dict[str, str] | None:
    return None if value is None else frac(value)


def node_obj(node: Any) -> dict[str, Any]:
    return {
        "lambda_box": interval(node.lambda_box),
        "lambda_depth": int(node.lambda_depth),
        "path_id": str(node.path_id),
        "r_cell": interval(node.r_cell),
        "r_depth": int(node.r_depth),
    }


def attempt_obj(attempt: Any) -> dict[str, Any]:
    return {
        "activation_index": int(attempt.activation_index),
        "lambda_box": interval(attempt.lambda_box),
        "lambda_depth": int(attempt.lambda_depth),
        "lambda_score": maybe_frac(attempt.lambda_score),
        "path_id": str(attempt.path_id),
        "r_cell": interval(attempt.r_cell),
        "r_depth": int(attempt.r_depth),
        "r_score": maybe_frac(attempt.r_score),
        "reason": str(attempt.reason),
        "selected_axis": attempt.selected_axis,
        "verdict": str(attempt.verdict),
    }


def leaf_obj(leaf: Any) -> dict[str, Any]:
    return {
        "activation_index": int(leaf.activation_index),
        "lambda_box": interval(leaf.lambda_box),
        "lambda_depth": int(leaf.lambda_depth),
        "lambda_score": maybe_frac(leaf.lambda_score),
        "mean_value_hi": frac(leaf.mean_value_hi),
        "path_id": str(leaf.path_id),
        "r_cell": interval(leaf.r_cell),
        "r_depth": int(leaf.r_depth),
        "r_score": maybe_frac(leaf.r_score),
    }


def progress_payload(snapshot: Any) -> dict[str, Any]:
    return {
        "accepted_leaf_count": len(snapshot.accepted_leaves),
        "activation_next": int(snapshot.activation_next),
        "completed_attempt_count": len(snapshot.attempts),
        "event": str(snapshot.event),
        "frontier": [node_obj(node) for node in snapshot.pending_nodes],
        "last_complete_attempt_id": str(snapshot.last_complete_attempt_id),
        "root_lambda": interval(snapshot.root_lambda),
        "root_r": interval(snapshot.root_r),
        "schema": "ITEM3_SWEEP_V9_PROGRESS_V1",
        "status": "PARTIAL",
    }


def partial_payload(snapshot: Any) -> dict[str, Any]:
    return {
        "accepted_leaves": [leaf_obj(leaf) for leaf in snapshot.accepted_leaves],
        "attempts": [attempt_obj(attempt) for attempt in snapshot.attempts],
        "last_complete_attempt_id": str(snapshot.last_complete_attempt_id),
        "root_lambda": interval(snapshot.root_lambda),
        "root_r": interval(snapshot.root_r),
        "schema": "ITEM3_SWEEP_V9_PARTIAL_EVIDENCE_V1",
        "status": "PARTIAL",
    }


class ProgressCheckpointHook:
    def __init__(self, *, store: Any, cadence: Any) -> None:
        self.store = store
        self.cadence = cadence
        self.commit_records: list[Any] = []
        self.last_snapshot: Any | None = None
        self.checkpoint_wall_seconds = 0.0

    def _commit(self, snapshot: Any) -> Any:
        start = time.monotonic()
        record = self.store.commit(
            progress=progress_payload(snapshot),
            partial_evidence=partial_payload(snapshot),
            last_complete_attempt_id=snapshot.last_complete_attempt_id,
        )
        self.checkpoint_wall_seconds += time.monotonic() - start
        self.cadence.mark_committed()
        self.commit_records.append(record)
        return record

    def __call__(self, snapshot: Any) -> None:
        self.last_snapshot = snapshot
        if snapshot.event == "ATTEMPT_COMPLETE":
            self.cadence.completed_attempt()
        structural = snapshot.event == "SHARD_COMPLETE"
        if self.cadence.should_commit(structural=structural):
            self._commit(snapshot)

    def force_shutdown_checkpoint(self) -> Any | None:
        """Controlled-shutdown helper; mathematical state is not resumed from it."""
        if self.last_snapshot is None:
            return None
        if self.cadence.should_commit(shutdown=True):
            return self._commit(self.last_snapshot)
        return None
