#!/usr/bin/env python3
"""Pinned-kernel L1/L2/L3 and J_START evaluation engine."""
from __future__ import annotations

from collections import deque
from fractions import Fraction
from types import ModuleType
from typing import Any, Callable

from blocal_phase4_model import (
    ADAPTER_ID, LAMBDA_PLUS, ROUTE_ID, S_NEG,
    dyadic_json, fraction_from_dyadic, interval_fractions, interval_json,
    need, rational_json,
)


def _dyadic_components(value: Fraction) -> tuple[int, int]:
    obj = dyadic_json(value)
    return int(obj["m"]), int(obj["e"])


def arb_exact_dyadic(arb_type: Any, value: Fraction) -> Any:
    mantissa, exponent = _dyadic_components(value)
    return arb_type((mantissa, -exponent))


def arb_exact_rational(arb_type: Any, fmpq_type: Any,
                       value: Fraction) -> Any:
    return arb_type(fmpq_type(value.numerator, value.denominator))


def arb_interval(arb_type: Any, lower: Fraction, upper: Fraction) -> Any:
    need(lower <= upper, "Arb interval order")
    midpoint, radius = (lower + upper) / 2, (upper - lower) / 2
    mm, me = _dyadic_components(midpoint)
    rm, re = _dyadic_components(radius)
    return arb_type((mm, -me), (rm, -re))


def kernel_options(config: dict[str, Any], arb_type: Any) -> dict[str, Any]:
    tolerance = fraction_from_dyadic(config["precision"]["absolute_tolerance"])
    return {
        "tol": arb_exact_dyadic(arb_type, tolerance),
        "depth": config["precision"]["kernel_depth_limit"],
        "limit": config["precision"]["kernel_eval_limit"],
    }


def adapter_interval(adapter: ModuleType, value: Any) -> dict[str, Any]:
    interval = adapter.arb_ball_to_canonical_dyadic_interval(value)
    interval_fractions(interval, "adapter interval")
    return interval


def strict_sign(node: str, enclosure: dict[str, Any]) -> bool:
    lower, upper = interval_fractions(enclosure, f"{node} enclosure")
    return lower > 0 if node in {"L1", "L2"} else upper < 0


def evaluate_l1(kernel: ModuleType, adapter: ModuleType, arb_type: Any,
                fmpq_type: Any, config: dict[str, Any], u_lower: Fraction,
                u_upper: Fraction, s_lower: Fraction,
                s_upper: Fraction) -> dict[str, Any]:
    r_ball = arb_interval(arb_type, 1 - u_upper, 1 - u_lower)
    lambda_ball = arb_exact_rational(arb_type, fmpq_type, LAMBDA_PLUS)
    lambda_ball += arb_interval(arb_type, s_lower, s_upper)
    value = -kernel.dFdr_arb(r_ball, lambda_ball, **kernel_options(config, arb_type))
    need(isinstance(value, arb_type), "L1 kernel return type")
    return adapter_interval(adapter, value)


def evaluate_l2(kernel: ModuleType, adapter: ModuleType, arb_type: Any,
                fmpq_type: Any, config: dict[str, Any], u_face: Fraction,
                s_lower: Fraction, s_upper: Fraction) -> dict[str, Any]:
    r_value = arb_exact_dyadic(arb_type, 1 - u_face)
    lambda_ball = arb_exact_rational(arb_type, fmpq_type, LAMBDA_PLUS)
    lambda_ball += arb_interval(arb_type, s_lower, s_upper)
    value = kernel.F_arb(r_value, lambda_ball, **kernel_options(config, arb_type))
    need(isinstance(value, arb_type), "L2 kernel return type")
    return adapter_interval(adapter, value)


def evaluate_l3_route_a(kernel: ModuleType, adapter: ModuleType,
                        arb_type: Any, fmpq_type: Any,
                        config: dict[str, Any], s_lower: Fraction,
                        s_upper: Fraction) -> dict[str, Any]:
    """Normative route A: exact r=1 through the same pinned F_arb."""
    need(config["endpoint_route"]["id"] == ROUTE_ID, "route A required")
    exact_r_one = arb_type(1)
    lambda_ball = arb_exact_rational(arb_type, fmpq_type, LAMBDA_PLUS)
    lambda_ball += arb_interval(arb_type, s_lower, s_upper)
    value = kernel.F_arb(exact_r_one, lambda_ball, **kernel_options(config, arb_type))
    need(isinstance(value, arb_type), "L3 route A return type")
    return adapter_interval(adapter, value)


def split_1d(lower: Fraction, upper: Fraction) -> tuple[tuple[Fraction, Fraction],
                                                         tuple[Fraction, Fraction]]:
    midpoint = (lower + upper) / 2
    need(lower < midpoint < upper, "1D split")
    return (lower, midpoint), (midpoint, upper)


def split_l1(u_lower: Fraction, u_upper: Fraction, s_lower: Fraction,
             s_upper: Fraction) -> list[tuple[Fraction, Fraction,
                                              Fraction, Fraction]]:
    if u_upper - u_lower >= s_upper - s_lower:
        left, right = split_1d(u_lower, u_upper)
        return [(left[0], left[1], s_lower, s_upper),
                (right[0], right[1], s_lower, s_upper)]
    left, right = split_1d(s_lower, s_upper)
    return [(u_lower, u_upper, left[0], left[1]),
            (u_lower, u_upper, right[0], right[1])]


def certify_node(node: str, candidate_index: int, u_max: Fraction,
                 s_start: Fraction, config: dict[str, Any],
                 evaluator: Callable[..., dict[str, Any]],
                 kernel_sha256: str) -> tuple[list[dict[str, Any]], bool,
                                               str | None, int]:
    budget = config["budgets"][node]
    initial: Any = (Fraction(0), u_max, -S_NEG, s_start) if node == "L1" \
        else ((-S_NEG if node == "L2" else Fraction(0)), s_start)
    pending: deque[tuple[Any, int]] = deque([(initial, 0)])
    leaves: list[dict[str, Any]] = []
    evaluations, first_failure = 0, None
    while pending:
        domain, depth = pending.popleft()
        did_evaluate = evaluations < budget["max_evaluations"]
        if did_evaluate:
            enclosure = evaluator(*domain)
            evaluations += 1
            certified = strict_sign(node, enclosure)
        else:
            enclosure = interval_json(Fraction(-1), Fraction(1))
            certified = False
            first_failure = first_failure or f"{node}_EVALUATION_BUDGET_EXHAUSTED"
        can_split = (not certified and first_failure is None
                     and depth < budget["max_depth"]
                     and len(leaves) + len(pending) + 2 <= budget["max_tiles"]
                     and evaluations < budget["max_evaluations"])
        if can_split:
            children = split_l1(*domain) if node == "L1" else list(split_1d(*domain))
            pending.extend((child, depth + 1) for child in children)
            continue
        if not certified:
            first_failure = first_failure or (
                f"{node}_DEPTH_LIMIT" if depth >= budget["max_depth"] else
                f"{node}_TILE_LIMIT" if len(leaves) + len(pending) + 1 >= budget["max_tiles"] else
                f"{node}_STRICT_SIGN_UNRESOLVED"
            )
        body: dict[str, Any] = {
            "record_type": "TILE", "node": node,
            "candidate_index": candidate_index, "enclosure": enclosure,
            "certified": certified, "depth": depth,
            "evaluations": 1 if did_evaluate else 0,
            "adapter_id": ADAPTER_ID,
            "kernel_source_sha256": kernel_sha256,
            "strict_predicate": "LOWER_GT_ZERO" if node in {"L1", "L2"}
                                else "UPPER_LT_ZERO",
            "failure_reason": None if certified else first_failure,
        }
        if node == "L1":
            u0, u1, s0, s1 = domain
            body.update(u_interval=interval_json(u0, u1),
                        s_interval=interval_json(s0, s1),
                        quantity="H_u_EQUALS_NEGATIVE_F_r")
        else:
            s0, s1 = domain
            body.update(u_face=dyadic_json(u_max if node == "L2" else Fraction(0)),
                        s_interval=interval_json(s0, s1),
                        quantity="H_INNER_FACE" if node == "L2"
                                 else "H_BOUNDARY_FACE_ROUTE_A")
        leaves.append(body)
    return leaves, all(item["certified"] for item in leaves), first_failure, evaluations


def build_j_start(candidate_index: int, lambda_start: Fraction,
                  u_max: Fraction, config: dict[str, Any], kernel: ModuleType,
                  adapter: ModuleType, arb_type: Any,
                  fmpq_type: Any) -> tuple[dict[str, Any] | None, str | None, int]:
    budget, evaluations = config["budgets"]["J_START"], 0
    options = kernel_options(config, arb_type)
    lambda_value = arb_exact_rational(arb_type, fmpq_type, lambda_start)

    def f_at(r: Fraction) -> dict[str, Any]:
        nonlocal evaluations
        need(evaluations < budget["max_evaluations"], "J_START evaluation budget")
        value = kernel.F_arb(arb_exact_dyadic(arb_type, r), lambda_value, **options)
        need(isinstance(value, arb_type), "J_START F return type")
        evaluations += 1
        return adapter_interval(adapter, value)

    left, right = 1 - u_max, Fraction(1)
    f_left = f_at(left)
    if interval_fractions(f_left)[0] <= 0:
        return None, "J_START_LEFT_SIGN_UNRESOLVED", evaluations
    f_right = None
    for _ in range(budget["max_bisections"]):
        midpoint = (left + right) / 2
        f_mid = f_at(midpoint)
        lower, upper = interval_fractions(f_mid)
        if upper < 0:
            right, f_right = midpoint, f_mid
            break
        if lower > 0:
            left, f_left = midpoint, f_mid
            continue
        return None, "J_START_BISECTION_SIGN_UNRESOLVED", evaluations
    if f_right is None or right >= 1:
        return None, "J_START_INTERIOR_NEGATIVE_ENDPOINT_NOT_FOUND", evaluations
    x_ball = arb_interval(arb_type, left, right)
    derivative_value = kernel.dFdr_arb(x_ball, lambda_value, **options)
    need(isinstance(derivative_value, arb_type), "J_START derivative return type")
    evaluations += 1
    derivative = adapter_interval(adapter, derivative_value)
    if interval_fractions(derivative)[1] >= 0:
        return None, "J_START_DERIVATIVE_NEGATIVITY_UNRESOLVED", evaluations
    midpoint = (left + right) / 2
    f_mid_value = kernel.F_arb(arb_exact_dyadic(arb_type, midpoint),
                               lambda_value, **options)
    need(isinstance(f_mid_value, arb_type), "J_START midpoint return type")
    evaluations += 1
    newton = arb_exact_dyadic(arb_type, midpoint) - f_mid_value / derivative_value
    need(isinstance(newton, arb_type), "J_START Newton return type")
    n_lo, n_hi = interval_fractions(adapter_interval(adapter, newton))
    if not (left < n_lo <= n_hi < right):
        return None, "J_START_STRICT_SELF_CONTAINMENT_UNRESOLVED", evaluations
    return {
        "record_type": "J_START", "node": "J_START",
        "selected_candidate_index": candidate_index,
        "lambda_start": rational_json(lambda_start),
        "r_interval": interval_json(left, right),
        "F_at_r_lo": f_left, "F_at_r_hi": f_right,
        "F_r_on_interval": derivative,
        "claim": "J_START_UNIQUE_NONDEGENERATE_ROOT",
        "interval_method": "INTERVAL_NEWTON_OR_KRAWCZYK_V1",
        "strict_self_containment": True, "certified": True,
    }, None, evaluations
