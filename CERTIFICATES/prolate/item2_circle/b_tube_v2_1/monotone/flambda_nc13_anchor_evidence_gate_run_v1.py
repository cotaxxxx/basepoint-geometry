#!/usr/bin/env python3
"""Dedicated deterministic NC13 anchor-evidence gate runner.

This is F_LAMBDA_CONTRACT_V1.1 preexecution infrastructure.

Scope:
- execute the V1.6 gate-unit harness;
- require the real-checker NC13 direct gate to pass;
- require explicit non-numerical / non-end-to-end harness markers;
- emit a deterministic run receipt.

Nonclaims:
- not end-to-end numerical transport;
- no numerical F or F_lambda evaluation;
- no binding promotion;
- does not modify the historical checker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]

HARNESS = HERE / "flambda_gate_unit_harness_v1_6.py"

EXPECTED_CODE = "FAIL_ANCHOR_EVIDENCE"
VERDICT = "NC13_EXACT_SUBCODE_PASS_NOT_PROMOTED"

REQUIRED_STDOUT_LINES = (
    "NC13_DIRECT_GATE=PASS",
    "NUMERICAL_EVALUATOR_CALLED=FALSE",
    "END_TO_END_CLAIM=FALSE",
    "GATE_HARNESS=PASS_NOT_PROMOTED",
)


def stop(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), *args],
        text=True,
    ).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()

    output = ns.output.expanduser().resolve()

    if not HARNESS.is_file():
        stop(f"HARNESS missing: {HARNESS}")

    head_pre = git("rev-parse", "HEAD")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_PRE dirty")

    child_env = dict(__import__("os").environ)
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"

    proc = subprocess.run(
        [sys.executable, str(HARNESS)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=child_env,
    )

    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="", file=sys.stderr)
        stop(f"HARNESS exit code {proc.returncode}")

    stdout_lines = set(proc.stdout.splitlines())
    missing = [
        line for line in REQUIRED_STDOUT_LINES
        if line not in stdout_lines
    ]
    if missing:
        stop("HARNESS required marker missing: " + ", ".join(missing))

    head_post = git("rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during NC13 gate")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-nc13-anchor-evidence-gate-run-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "control_id": "NC13",
        "method": "SYNTHETIC_ROUTE_REAL_CHECKER_FUNCTION",
        "expected_exact_code": EXPECTED_CODE,
        "gate_harness_sha256": sha256_path(HARNESS),
        "run_source_sha256": sha256_path(Path(__file__).resolve()),
        "harness_exit_code": proc.returncode,
        "harness_stdout_sha256": sha256_text(proc.stdout),
        "required_stdout_lines": list(REQUIRED_STDOUT_LINES),
        "all_required_stdout_lines_present": True,
        "needs_numerics": False,
        "numerical_evaluator_called": False,
        "end_to_end": False,
        "historical_checker_modified": False,
        "source_tree_pre_clean": True,
        "source_tree_post_clean": True,
        "head_unchanged_during_run": True,
        "execution_head": head_pre,
        "binding_use_authorized": False,
        "verdict": VERDICT,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("CONTROL_ID=NC13")
    print("METHOD=SYNTHETIC_ROUTE_REAL_CHECKER_FUNCTION")
    print("EXPECTED_EXACT_CODE=" + EXPECTED_CODE)
    print("NC13_DIRECT_GATE=PASS")
    print("NUMERICAL_EVALUATOR_CALLED=FALSE")
    print("END_TO_END_CLAIM=FALSE")
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=" + VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
