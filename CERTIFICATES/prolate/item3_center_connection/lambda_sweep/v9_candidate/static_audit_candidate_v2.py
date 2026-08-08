#!/usr/bin/env python3
"""Static source-boundary audit for the Item 3 v9 five-output candidate v2.

This script parses source text only. It deliberately does not import python-flint or the
candidate module, so it can verify import/source boundaries before runtime validation.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "prolate_F_derivatives_cleanroom_v9_candidate.py"
REPORT = HERE / "static_audit_candidate_v2.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def call_name(node: ast.Call) -> str | None:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def names_in(node: ast.AST) -> set[str]:
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def main() -> int:
    raw = SOURCE.read_bytes()
    text = raw.decode("utf-8")
    tree = ast.parse(text, filename=str(SOURCE))

    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    allowed_from = {"__future__", "typing", "flint"}
    imports: list[tuple[str, tuple[str, ...]]] = []
    import_ok = True
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            import_ok = False
            imports.append(("IMPORT", tuple(alias.name for alias in node.names)))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append((module, tuple(alias.name for alias in node.names)))
            if module not in allowed_from:
                import_ok = False
    checks["import_allowlist"] = import_ok
    details["imports"] = imports

    function_defs = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    required_public = {
        "F_arb",
        "F_r_arb",
        "F_lambda_arb",
        "F_rr_arb",
        "F_rlambda_arb",
    }
    observed_public = {name for name in function_defs if name.endswith("_arb")}
    checks["exact_public_rigorous_interface_set"] = observed_public == required_public
    details["observed_public_arb"] = sorted(observed_public)

    checks["old_prototype_import_absent"] = "prolate_F_derivatives_cleanroom_v9" not in "\n".join(
        f"{module}:{','.join(names)}" for module, names in imports
    )
    checks["runner_checker_adapter_import_absent"] = not any(
        token in text for token in ("import runner", "import checker", "import adapter", "item3_sweep")
    )
    checks["float_diagnostic_dependencies_absent"] = not any(
        token in text for token in ("import math", "import numpy", "import mpmath", "finite_difference")
    )
    checks["certified_declaration_absent"] = "CERTIFIED" not in text

    ors = []
    forbidden_ands = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BoolOp):
            ns = names_in(node)
            if {"analytic_theta", "analytic_phi"}.issubset(ns):
                if isinstance(node.op, ast.Or):
                    ors.append(node)
                elif isinstance(node.op, ast.And):
                    forbidden_ands.append(node)
    checks["nested_analytic_or_exactly_once"] = len(ors) == 1
    checks["nested_analytic_and_absent"] = len(forbidden_ands) == 0
    details["nested_or_count"] = len(ors)
    details["nested_and_count"] = len(forbidden_ands)

    sqrt_calls = []
    angle_calls = []
    hyp2f1_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            if name == "sqrt":
                sqrt_calls.append(node)
            elif name == "angle_data_3":
                angle_calls.append(node)
            elif name == "hypgeom_2f1":
                hyp2f1_calls.append(node)

    def has_analytic_keyword(call: ast.Call) -> bool:
        return any(
            kw.arg == "analytic"
            and isinstance(kw.value, ast.Name)
            and kw.value.id == "analytic"
            for kw in call.keywords
        )

    checks["two_sqrt_calls_forward_analytic"] = (
        len(sqrt_calls) == 2 and all(has_analytic_keyword(call) for call in sqrt_calls)
    )
    checks["five_angle_calls_forward_analytic"] = (
        len(angle_calls) == 5 and all(has_analytic_keyword(call) for call in angle_calls)
    )
    checks["one_gauss_2f1_call"] = len(hyp2f1_calls) == 1
    details["sqrt_call_count"] = len(sqrt_calls)
    details["angle_call_count"] = len(angle_calls)
    details["hypgeom_2f1_call_count"] = len(hyp2f1_calls)

    guard_fragment = "if analytic and 0 in z.imag and z.real.upper() >= 1:"
    checks["explicit_2f1_cut_guard_present"] = guard_fragment in text
    if len(hyp2f1_calls) == 1 and guard_fragment in text:
        guard_offset = text.index(guard_fragment)
        hyp_offset = text.index("hypgeom_2f1")
        checks["2f1_cut_guard_precedes_call"] = guard_offset < hyp_offset
    else:
        checks["2f1_cut_guard_precedes_call"] = False

    checks["nonfinite_cosine_guard_present"] = "if analytic and not cosine.is_finite():" in text

    validate_node = function_defs.get("_validate_inputs")
    evaluate_node = function_defs.get("_evaluate")
    as_real_node = function_defs.get("_as_real")
    checks["validate_inputs_present"] = validate_node is not None
    checks["evaluate_present"] = evaluate_node is not None
    checks["as_real_present"] = as_real_node is not None

    if evaluate_node is not None:
        evaluate_calls = [
            call_name(node)
            for node in ast.walk(evaluate_node)
            if isinstance(node, ast.Call)
        ]
        checks["evaluate_calls_validate_inputs"] = "_validate_inputs" in evaluate_calls
    else:
        checks["evaluate_calls_validate_inputs"] = False

    public_route_ok = True
    for name in required_public:
        node = function_defs.get(name)
        if node is None:
            public_route_ok = False
            continue
        calls = [
            call_name(item)
            for item in ast.walk(node)
            if isinstance(item, ast.Call)
        ]
        if "_evaluate" not in calls:
            public_route_ok = False
    checks["all_public_interfaces_route_through_evaluate"] = public_route_ok

    if validate_node is not None:
        validate_src = ast.get_source_segment(text, validate_node) or ""
        checks["r_domain_lower_guard"] = "r.lower() <= 0" in validate_src
        checks["r_domain_upper_guard"] = "r.upper() >= 1" in validate_src
        checks["lambda_domain_guard"] = "lam.lower() < 1" in validate_src
        checks["finite_input_guard"] = ".is_finite()" in validate_src
    else:
        checks["r_domain_lower_guard"] = False
        checks["r_domain_upper_guard"] = False
        checks["lambda_domain_guard"] = False
        checks["finite_input_guard"] = False

    if as_real_node is not None:
        as_real_src = ast.get_source_segment(text, as_real_node) or ""
        checks["as_real_rejects_nonfinite"] = "not value.is_finite()" in as_real_src
        checks["as_real_requires_imag_zero_containment"] = "0 in value.imag" in as_real_src
    else:
        checks["as_real_rejects_nonfinite"] = False
        checks["as_real_requires_imag_zero_containment"] = False

    status = "PASSED" if all(checks.values()) else "FAILED"
    report = {
        "schema": "ITEM3_SWEEP_V9_CANDIDATE_V2_STATIC_AUDIT_V1",
        "status": status,
        "candidate_path": SOURCE.name,
        "candidate_sha256": sha256_bytes(raw),
        "checks": checks,
        "details": details,
        "nonclaim": "Static PASS does not validate python-flint runtime semantics or authorize production use.",
    }
    REPORT.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
