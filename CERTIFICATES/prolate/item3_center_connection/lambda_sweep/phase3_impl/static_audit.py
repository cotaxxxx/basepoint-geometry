#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from item3_sweep.control_registry import CONTROL_BINDINGS, validate_control_bindings
from item3_sweep.enums import CheckerFailureReason, RunnerFailureReason
from item3_sweep.transitions import TRANSITIONS

FORBIDDEN_IMPORT_ROOTS = {"flint", "arb", "mpmath", "numpy", "scipy", "sympy"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main() -> int:
    validate_control_bindings()
    runner_enum = {item.value for item in RunnerFailureReason}
    checker_enum = {item.value for item in CheckerFailureReason}
    if not runner_enum.isdisjoint(checker_enum):
        raise RuntimeError("runner/checker failure enums overlap")
    if set(TRANSITIONS) != set(RunnerFailureReason):
        raise RuntimeError("runner transition table not closed")

    files = sorted(
        path for path in HERE.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    imports: dict[str, list[str]] = {}
    forbidden: dict[str, list[str]] = {}
    hashes: dict[str, str] = {}
    for path in files:
        relative = path.relative_to(HERE).as_posix()
        roots = sorted(scan_imports(path))
        imports[relative] = roots
        bad = sorted(set(roots) & FORBIDDEN_IMPORT_ROOTS)
        if bad:
            forbidden[relative] = bad
        hashes[relative] = sha256(path)
    if forbidden:
        raise RuntimeError(f"forbidden calculation imports: {forbidden}")

    report = {
        "schema": "ITEM3_SWEEP_PHASE3_STATIC_AUDIT_V1",
        "control_binding_count": len(CONTROL_BINDINGS),
        "runner_failure_reason_count": len(runner_enum),
        "checker_failure_reason_count": len(checker_enum),
        "runner_checker_enums_disjoint": True,
        "transition_table_closed": True,
        "forbidden_calculation_imports": forbidden,
        "source_sha256": hashes,
        "imports": imports,
        "verdict": "PASS",
    }
    raw = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    (HERE / "PHASE3_STATIC_AUDIT.json").write_text(raw, encoding="ascii")
    print(raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
