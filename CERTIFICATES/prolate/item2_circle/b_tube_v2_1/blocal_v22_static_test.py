#!/usr/bin/env python3
"""Calculation-free source/static audit for B-LOCAL v2.2 finite-route implementation."""
from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import sys
from pathlib import Path

import blocal_v22_symbolic_audit as symbolic

HERE = Path(__file__).resolve(strict=True).parent
SOURCE_NAMES = [
    "blocal_v22_policy.py",
    "blocal_v22_model.py",
    "blocal_v22_boundary.py",
    "blocal_v22_checker.py",
    "blocal_v22_checker_test.py",
    "blocal_v22_runner.py",
    "blocal_v22_static_test.py",
    "blocal_v22_symbolic_audit.py",
    "blocal_v22_readiness_test.py",
]


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    for name in SOURCE_NAMES:
        p = HERE/name
        need(p.is_file() and not p.is_symlink(), f"source {name}")
        py_compile.compile(str(p), doraise=True)

    result = symbolic.run_audit()
    need(result["exact_algebra"] is True
         and result["F_route_exact"] is True
         and result["J_equals_rho_K"] is True,
         "symbolic audit")

    route = (HERE/"blocal_v22_boundary.py").read_text()
    runner = (HERE/"blocal_v22_runner.py").read_text()
    checker = (HERE/"blocal_v22_checker.py").read_text()
    policy_text = (HERE/"blocal_v22_policy.py").read_text()

    for token in (
        "kernel.F_arb(", "kernel.dFdr_arb(", "1-epsilon",
        "1 - epsilon", "Decimal(", "float(",
    ):
        need(token not in route and token not in runner,
             f"forbidden proof token {token}")

    for token in (
        "enclose_hu", "enclose_f", "validate_helper_lemmas",
        "_safe_nonnegative_sqrt", "_safe_positive_sqrt",
        "_positive_inverse_factors", "R2_W_LO",
        "gamma_fallback_used", "Z_DEN_LO", "q_lo", "q_hi",
    ):
        need(token in route, f"required route token {token}")

    for token in (
        "EXACT_ENDPOINT_RECIPROCAL", "NONNEGATIVE_UPPER_ENDPOINT_SQRT",
        "CHILD_GAMMA_OR_TWO_BIN_FALLBACK_ALL_CELLS",
        "PER_CHILD_Q_LO_WITH_R2_W",
    ):
        need(token in policy_text, f"required policy token {token}")

    for token in (
        "sqrt_policy_id", "gamma_fallback_used", "R2_W_LO",
        "q_hi", "Duffy child exact q endpoint bounds",
        "Newton midpoint proof enclosure",
    ):
        need(token in checker, f"checker binding token {token}")

    out = subprocess.run(
        [sys.executable, str(HERE/"blocal_v22_checker_test.py")],
        check=True, capture_output=True, text=True)
    need("ALL_BINDING_NEGATIVE_CONTROLS_PASS" in out.stdout,
         "negative controls")

    marker = (HERE/"READINESS_DRAFT").read_text()
    need("readiness_draft_revision=2" in marker, "readiness draft revision")
    need("native_repairs=R-1,R-2,R-3,R-4" in marker,
         "readiness repair marker")
    need("config_materialized=false" in marker, "draft config boundary")

    print(json.dumps({
        "schema": "blocal-v22-finite-static-v2",
        "calculation_free": True,
        "kernel_imported": False,
        "symbolic_audit_exact": True,
        "negative_controls": True,
        "R1_R4_checker_bindings": True,
        "source_sha256": {n: digest(HERE/n) for n in SOURCE_NAMES},
        "status": "PASS",
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
