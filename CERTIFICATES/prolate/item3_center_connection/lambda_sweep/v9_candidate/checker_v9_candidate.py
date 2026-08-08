#!/usr/bin/env python3
"""Independent deterministic checker candidate for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / NOT PRODUCTION APPROVED.

This module intentionally does not import runner_v9_candidate.  It independently replays
canonical centers, dps-50 mean-value decisions, split scores, axis choice, path IDs, LIFO
order, and accepted leaves from fresh adapter calls.  It then performs a second fresh
accepted-cell verification at dps 70 using a distinct adapter instance.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Literal


CHECKER_ID = "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V1"
R_FLOOR = Fraction(1, 1 << 16)
LAMBDA_FLOOR = Fraction(1, 1 << 16)
Axis = Literal["r", "lambda"]


class CheckerReject(RuntimeError):
    pass


@dataclass(frozen=True)
class Node:
    r_cell: tuple[Fraction, Fraction]
    lambda_box: tuple[Fraction, Fraction]
    path_id: str
    r_depth: int
    lambda_depth: int


@dataclass(frozen=True)
class CheckerReport:
    checker_id: str
    status: str
    reason: str
    dps50_attempt_count: int
    dps50_leaf_count: int
    dps70_verified_leaf_count: int
    endpoint_dps50_pass: bool
    endpoint_dps70_pass: bool
    adapter_instances_distinct: bool
    control_kernel_call_counts: dict[str, int]
    verify_kernel_call_counts: dict[str, int]


def width(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise CheckerReject("interval lower endpoint exceeds upper endpoint")
    return hi - lo


def midpoint(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise CheckerReject("interval lower endpoint exceeds upper endpoint")
    return (lo + hi) / 2


def can_split(interval: tuple[Fraction, Fraction], floor: Fraction) -> bool:
    return floor > 0 and width(interval) / 2 >= floor


def depth_cap(interval: tuple[Fraction, Fraction], floor: Fraction) -> int:
    w = width(interval)
    if w < floor:
        return 0
    d = 0
    while w / 2 >= floor:
        w /= 2
        d += 1
    return d


def choose_axis(
    *,
    r_score: Fraction | None,
    lambda_score: Fraction | None,
    r_splittable: bool,
    lambda_splittable: bool,
) -> tuple[Axis | None, str]:
    if not r_splittable and not lambda_splittable:
        return None, "NO_SPLITTABLE_AXIS"
    if r_splittable and not lambda_splittable:
        return "r", "ONLY_R_SPLITTABLE"
    if lambda_splittable and not r_splittable:
        return "lambda", "ONLY_LAMBDA_SPLITTABLE"

    r_nf = r_score is None
    l_nf = lambda_score is None
    if r_nf and not l_nf:
        return "r", "NONFINITE_R_OUTRANKS_FINITE"
    if l_nf and not r_nf:
        return "lambda", "NONFINITE_LAMBDA_OUTRANKS_FINITE"
    if r_nf and l_nf:
        return "r", "DOUBLE_NONFINITE_TIE_TO_R"
    assert r_score is not None and lambda_score is not None
    if r_score > lambda_score:
        return "r", "LARGER_EXACT_SCORE"
    if lambda_score > r_score:
        return "lambda", "LARGER_EXACT_SCORE"
    return "r", "EXACT_SCORE_TIE_TO_R"


def children(node: Node, axis: Axis) -> tuple[Node, Node]:
    """Return mathematical processing order: R0,R1 or L1,L0."""
    if axis == "r":
        m = midpoint(node.r_cell)
        return (
            Node((node.r_cell[0], m), node.lambda_box, node.path_id + "/R0", node.r_depth + 1, node.lambda_depth),
            Node((m, node.r_cell[1]), node.lambda_box, node.path_id + "/R1", node.r_depth + 1, node.lambda_depth),
        )
    m = midpoint(node.lambda_box)
    return (
        Node(node.r_cell, (m, node.lambda_box[1]), node.path_id + "/L1", node.r_depth, node.lambda_depth + 1),
        Node(node.r_cell, (node.lambda_box[0], m), node.path_id + "/L0", node.r_depth, node.lambda_depth + 1),
    )


def leaf_key(leaf: Any) -> tuple[Any, ...]:
    return (-leaf.lambda_box[1], -leaf.lambda_box[0], leaf.r_cell[0], leaf.r_cell[1], leaf.path_id)


def _assert_attempt_matches(
    observed: Any,
    *,
    activation: int,
    node: Node,
    verdict: str,
    selected_axis: str | None,
    reason: str,
    r_score: Fraction | None,
    lambda_score: Fraction | None,
) -> None:
    fields = {
        "activation_index": activation,
        "path_id": node.path_id,
        "r_cell": node.r_cell,
        "lambda_box": node.lambda_box,
        "r_depth": node.r_depth,
        "lambda_depth": node.lambda_depth,
        "verdict": verdict,
        "selected_axis": selected_axis,
        "reason": reason,
        "r_score": r_score,
        "lambda_score": lambda_score,
    }
    for name, expected in fields.items():
        if getattr(observed, name, object()) != expected:
            raise CheckerReject(f"runner attempt mismatch: {name}")


def verify_runner_result(
    *,
    runner_result: Any,
    control_adapter: Any,
    verification_adapter: Any,
    dps_control: int = 50,
    dps_verify: int = 70,
    r_floor: Fraction = R_FLOOR,
    lambda_floor: Fraction = LAMBDA_FLOOR,
) -> CheckerReport:
    if control_adapter is verification_adapter:
        raise CheckerReject("checker requires distinct control and verification adapter instances")
    if runner_result.terminal_class != "COMPLETE_CANDIDATE":
        raise CheckerReject("only complete runner candidate may pass checker")

    root_r = runner_result.root_r
    root_lambda = runner_result.root_lambda
    attempts = tuple(runner_result.attempts)
    runner_leaves = tuple(runner_result.accepted_leaves)

    g50_lo = control_adapter.evaluate_g(
        r_cell=(root_r[0], root_r[0]), lambda_box=root_lambda, dps=dps_control
    )
    g50_hi = control_adapter.evaluate_g(
        r_cell=(root_r[1], root_r[1]), lambda_box=root_lambda, dps=dps_control
    )
    endpoint50 = g50_lo.strictly_positive() and g50_hi.strictly_negative()
    if not endpoint50:
        raise CheckerReject("fresh dps50 endpoint signs fail")

    r_cap = depth_cap(root_r, r_floor)
    l_cap = depth_cap(root_lambda, lambda_floor)
    stack: list[Node] = [Node(root_r, root_lambda, "ROOT", 0, 0)]
    fresh_leaf_specs: list[tuple[str, int, tuple[Fraction, Fraction], tuple[Fraction, Fraction], int, int, Fraction]] = []
    activation = 0

    while stack:
        if activation >= len(attempts):
            raise CheckerReject("runner attempt stream ended before replay tree")
        node = stack.pop()
        ev = control_adapter.evaluate_mean_value(
            r_cell=node.r_cell, lambda_box=node.lambda_box, dps=dps_control
        )
        observed = attempts[activation]
        if ev.strict_negative:
            if not ev.mean_value.finite:
                raise CheckerReject("strict NEG with nonfinite mean value")
            _assert_attempt_matches(
                observed,
                activation=activation,
                node=node,
                verdict="NEG",
                selected_axis=None,
                reason="STRICT_NEG",
                r_score=ev.r_score,
                lambda_score=ev.lambda_score,
            )
            fresh_leaf_specs.append((
                node.path_id, activation, node.r_cell, node.lambda_box,
                node.r_depth, node.lambda_depth, ev.mean_value.hi,
            ))
            activation += 1
            continue

        r_split = can_split(node.r_cell, r_floor) and node.r_depth < r_cap
        l_split = can_split(node.lambda_box, lambda_floor) and node.lambda_depth < l_cap
        axis, reason = choose_axis(
            r_score=ev.r_score,
            lambda_score=ev.lambda_score,
            r_splittable=r_split,
            lambda_splittable=l_split,
        )
        if axis is None:
            raise CheckerReject("fresh replay reaches incomplete stop floor")
        _assert_attempt_matches(
            observed,
            activation=activation,
            node=node,
            verdict="SPLIT",
            selected_axis=axis,
            reason=reason,
            r_score=ev.r_score,
            lambda_score=ev.lambda_score,
        )
        first, second = children(node, axis)
        stack.append(second)
        stack.append(first)
        activation += 1

    if activation != len(attempts):
        raise CheckerReject("runner attempt stream has extra records")

    # Compare fresh accepted partition to runner's canonical geometric leaf list.
    fresh_sorted = sorted(
        fresh_leaf_specs,
        key=lambda x: (-x[3][1], -x[3][0], x[2][0], x[2][1], x[0]),
    )
    if len(fresh_sorted) != len(runner_leaves):
        raise CheckerReject("accepted leaf count mismatch")
    for fresh, observed in zip(fresh_sorted, runner_leaves, strict=True):
        path_id, act, r_cell, lambda_box, rd, ld, mv_hi = fresh
        fields = {
            "path_id": path_id,
            "activation_index": act,
            "r_cell": r_cell,
            "lambda_box": lambda_box,
            "r_depth": rd,
            "lambda_depth": ld,
            "mean_value_hi": mv_hi,
        }
        for name, expected in fields.items():
            if getattr(observed, name, object()) != expected:
                raise CheckerReject(f"accepted leaf mismatch: {name}")

    # Fresh verification precision.  It must not alter the partition, only accept/reject.
    g70_lo = verification_adapter.evaluate_g(
        r_cell=(root_r[0], root_r[0]), lambda_box=root_lambda, dps=dps_verify
    )
    g70_hi = verification_adapter.evaluate_g(
        r_cell=(root_r[1], root_r[1]), lambda_box=root_lambda, dps=dps_verify
    )
    endpoint70 = g70_lo.strictly_positive() and g70_hi.strictly_negative()
    if not endpoint70:
        raise CheckerReject("fresh dps70 endpoint signs fail")

    verified = 0
    for path_id, _act, r_cell, lambda_box, _rd, _ld, _mv_hi in fresh_sorted:
        ev70 = verification_adapter.evaluate_mean_value(
            r_cell=r_cell, lambda_box=lambda_box, dps=dps_verify
        )
        if not ev70.strict_negative:
            raise CheckerReject(f"fresh dps70 strict NEG fails: {path_id}")
        verified += 1

    return CheckerReport(
        checker_id=CHECKER_ID,
        status="PASS_CANDIDATE",
        reason="DPS50_REPLAY_AND_DPS70_VERIFY_PASS",
        dps50_attempt_count=activation,
        dps50_leaf_count=len(fresh_sorted),
        dps70_verified_leaf_count=verified,
        endpoint_dps50_pass=endpoint50,
        endpoint_dps70_pass=endpoint70,
        adapter_instances_distinct=True,
        control_kernel_call_counts=dict(control_adapter.kernel_call_counts),
        verify_kernel_call_counts=dict(verification_adapter.kernel_call_counts),
    )
