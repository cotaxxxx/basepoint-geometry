#!/usr/bin/env python3
"""Deterministic Item 3 sweep v9 rehearsal runner candidate.

STATUS: IMPLEMENTATION CANDIDATE / NOT PRODUCTION APPROVED.

The runner proves at most, for one preapproved lambda shard and one r window:
- G(r_lo, Lambda) > 0;
- G(r_hi, Lambda) < 0;
- G_r < 0 on an exact binary partition of [r_lo,r_hi] x Lambda.

It does not promote a certificate.  Non-NEG or budget/floor exhaustion is INCOMPLETE,
not a mathematical counterexample.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Literal


RUNNER_ID = "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V1"
R_FLOOR = Fraction(1, 1 << 16)
LAMBDA_FLOOR = Fraction(1, 1 << 16)
Axis = Literal["r", "lambda"]


class RunnerContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class Node:
    r_cell: tuple[Fraction, Fraction]
    lambda_box: tuple[Fraction, Fraction]
    path_id: str
    r_depth: int
    lambda_depth: int


@dataclass(frozen=True)
class AcceptedLeaf:
    path_id: str
    activation_index: int
    r_cell: tuple[Fraction, Fraction]
    lambda_box: tuple[Fraction, Fraction]
    r_depth: int
    lambda_depth: int
    mean_value_hi: Fraction
    r_score: Fraction | None
    lambda_score: Fraction | None


@dataclass(frozen=True)
class AttemptRecord:
    activation_index: int
    path_id: str
    r_cell: tuple[Fraction, Fraction]
    lambda_box: tuple[Fraction, Fraction]
    r_depth: int
    lambda_depth: int
    verdict: str
    selected_axis: str | None
    reason: str
    r_score: Fraction | None
    lambda_score: Fraction | None


@dataclass(frozen=True)
class RunnerResult:
    runner_id: str
    terminal_class: str
    reason: str
    endpoint_g_lo: Any
    endpoint_g_hi: Any
    attempts: tuple[AttemptRecord, ...]
    accepted_leaves: tuple[AcceptedLeaf, ...]
    root_r: tuple[Fraction, Fraction]
    root_lambda: tuple[Fraction, Fraction]
    kernel_call_counts: dict[str, int]


def width(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise RunnerContractError("interval lower endpoint exceeds upper endpoint")
    return hi - lo


def midpoint(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise RunnerContractError("interval lower endpoint exceeds upper endpoint")
    return (lo + hi) / 2


def can_split(interval: tuple[Fraction, Fraction], floor: Fraction) -> bool:
    if floor <= 0:
        raise RunnerContractError("split floor must be positive")
    return width(interval) / 2 >= floor


def derived_depth_cap(interval: tuple[Fraction, Fraction], floor: Fraction) -> int:
    """Exact max d with width/2^d >= floor; zero when root width < floor."""
    w = width(interval)
    if w < floor:
        return 0
    d = 0
    while w / 2 >= floor:
        w /= 2
        d += 1
    return d


def select_axis(
    *,
    r_score: Fraction | None,
    lambda_score: Fraction | None,
    r_splittable: bool,
    lambda_splittable: bool,
) -> tuple[Axis | None, str]:
    candidates: list[Axis] = []
    if r_splittable:
        candidates.append("r")
    if lambda_splittable:
        candidates.append("lambda")
    if not candidates:
        return None, "NO_SPLITTABLE_AXIS"
    if candidates == ["r"]:
        return "r", "ONLY_R_SPLITTABLE"
    if candidates == ["lambda"]:
        return "lambda", "ONLY_LAMBDA_SPLITTABLE"

    r_nonfinite = r_score is None
    l_nonfinite = lambda_score is None
    if r_nonfinite and not l_nonfinite:
        return "r", "NONFINITE_R_OUTRANKS_FINITE"
    if l_nonfinite and not r_nonfinite:
        return "lambda", "NONFINITE_LAMBDA_OUTRANKS_FINITE"
    if r_nonfinite and l_nonfinite:
        return "r", "DOUBLE_NONFINITE_TIE_TO_R"
    assert r_score is not None and lambda_score is not None
    if r_score > lambda_score:
        return "r", "LARGER_EXACT_SCORE"
    if lambda_score > r_score:
        return "lambda", "LARGER_EXACT_SCORE"
    return "r", "EXACT_SCORE_TIE_TO_R"


def split_node(node: Node, axis: Axis) -> tuple[Node, Node]:
    """Return children in mathematical processing order, not push order."""
    if axis == "r":
        m = midpoint(node.r_cell)
        lower = Node(
            (node.r_cell[0], m), node.lambda_box, node.path_id + "/R0",
            node.r_depth + 1, node.lambda_depth,
        )
        upper = Node(
            (m, node.r_cell[1]), node.lambda_box, node.path_id + "/R1",
            node.r_depth + 1, node.lambda_depth,
        )
        return lower, upper
    m = midpoint(node.lambda_box)
    upper = Node(
        node.r_cell, (m, node.lambda_box[1]), node.path_id + "/L1",
        node.r_depth, node.lambda_depth + 1,
    )
    lower = Node(
        node.r_cell, (node.lambda_box[0], m), node.path_id + "/L0",
        node.r_depth, node.lambda_depth + 1,
    )
    return upper, lower


def canonical_leaf_order(leaf: AcceptedLeaf) -> tuple[Any, ...]:
    # Negate Fractions for descending lambda order.
    return (
        -leaf.lambda_box[1],
        -leaf.lambda_box[0],
        leaf.r_cell[0],
        leaf.r_cell[1],
        leaf.path_id,
    )


def run_rehearsal_partition(
    *,
    adapter: Any,
    root_r: tuple[Fraction, Fraction],
    root_lambda: tuple[Fraction, Fraction],
    dps: int = 50,
    max_activations: int = 65536,
    r_floor: Fraction = R_FLOOR,
    lambda_floor: Fraction = LAMBDA_FLOOR,
) -> RunnerResult:
    if not (Fraction(0) < root_r[0] < root_r[1] < Fraction(1)):
        raise RunnerContractError("root r window must satisfy 0<lo<hi<1")
    if not (Fraction(1) <= root_lambda[0] < root_lambda[1]):
        raise RunnerContractError("root lambda box must satisfy 1<=lo<hi")
    if not isinstance(max_activations, int) or max_activations <= 0:
        raise RunnerContractError("max_activations must be positive integer")

    # S1/S2 are required on the whole preapproved lambda root.  A failure is not
    # repaired by silently shrinking lambda; it is an incomplete rehearsal.
    g_lo = adapter.evaluate_g(
        r_cell=(root_r[0], root_r[0]), lambda_box=root_lambda, dps=dps
    )
    g_hi = adapter.evaluate_g(
        r_cell=(root_r[1], root_r[1]), lambda_box=root_lambda, dps=dps
    )
    if not g_lo.strictly_positive():
        return RunnerResult(
            RUNNER_ID, "INCOMPLETE", "S1_ENDPOINT_SIGN_FAIL", g_lo, g_hi,
            (), (), root_r, root_lambda, dict(adapter.kernel_call_counts),
        )
    if not g_hi.strictly_negative():
        return RunnerResult(
            RUNNER_ID, "INCOMPLETE", "S2_ENDPOINT_SIGN_FAIL", g_lo, g_hi,
            (), (), root_r, root_lambda, dict(adapter.kernel_call_counts),
        )

    r_cap = derived_depth_cap(root_r, r_floor)
    lambda_cap = derived_depth_cap(root_lambda, lambda_floor)
    stack: list[Node] = [Node(root_r, root_lambda, "ROOT", 0, 0)]
    attempts: list[AttemptRecord] = []
    accepted: list[AcceptedLeaf] = []
    activation = 0

    while stack:
        if activation >= max_activations:
            return RunnerResult(
                RUNNER_ID, "INCOMPLETE", "ACTIVATION_BUDGET_EXHAUSTED", g_lo, g_hi,
                tuple(attempts), tuple(sorted(accepted, key=canonical_leaf_order)),
                root_r, root_lambda, dict(adapter.kernel_call_counts),
            )
        node = stack.pop()
        current_activation = activation
        activation += 1

        evidence = adapter.evaluate_mean_value(
            r_cell=node.r_cell, lambda_box=node.lambda_box, dps=dps
        )
        if evidence.strict_negative:
            assert evidence.mean_value.finite
            accepted.append(AcceptedLeaf(
                path_id=node.path_id,
                activation_index=current_activation,
                r_cell=node.r_cell,
                lambda_box=node.lambda_box,
                r_depth=node.r_depth,
                lambda_depth=node.lambda_depth,
                mean_value_hi=evidence.mean_value.hi,
                r_score=evidence.r_score,
                lambda_score=evidence.lambda_score,
            ))
            attempts.append(AttemptRecord(
                current_activation, node.path_id, node.r_cell, node.lambda_box,
                node.r_depth, node.lambda_depth, "NEG", None, "STRICT_NEG",
                evidence.r_score, evidence.lambda_score,
            ))
            continue

        r_splittable = can_split(node.r_cell, r_floor) and node.r_depth < r_cap
        lambda_splittable = (
            can_split(node.lambda_box, lambda_floor)
            and node.lambda_depth < lambda_cap
        )
        axis, reason = select_axis(
            r_score=evidence.r_score,
            lambda_score=evidence.lambda_score,
            r_splittable=r_splittable,
            lambda_splittable=lambda_splittable,
        )
        if axis is None:
            attempts.append(AttemptRecord(
                current_activation, node.path_id, node.r_cell, node.lambda_box,
                node.r_depth, node.lambda_depth, "INCOMPLETE", None, reason,
                evidence.r_score, evidence.lambda_score,
            ))
            return RunnerResult(
                RUNNER_ID, "INCOMPLETE", "STOP_FLOOR_NO_STRICT_NEG", g_lo, g_hi,
                tuple(attempts), tuple(sorted(accepted, key=canonical_leaf_order)),
                root_r, root_lambda, dict(adapter.kernel_call_counts),
            )

        first, second = split_node(node, axis)
        attempts.append(AttemptRecord(
            current_activation, node.path_id, node.r_cell, node.lambda_box,
            node.r_depth, node.lambda_depth, "SPLIT", axis, reason,
            evidence.r_score, evidence.lambda_score,
        ))
        # LIFO push reverse of mathematical processing order.
        stack.append(second)
        stack.append(first)

    ordered = tuple(sorted(accepted, key=canonical_leaf_order))
    return RunnerResult(
        RUNNER_ID, "COMPLETE_CANDIDATE", "ALL_CELLS_STRICT_NEG", g_lo, g_hi,
        tuple(attempts), ordered, root_r, root_lambda, dict(adapter.kernel_call_counts),
    )
