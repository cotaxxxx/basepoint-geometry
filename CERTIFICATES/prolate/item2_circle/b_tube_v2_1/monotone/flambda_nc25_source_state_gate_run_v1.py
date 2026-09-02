#!/usr/bin/env python3
"""Dedicated deterministic NC25 source-state dry-precheck runner.

Executes both frozen canonical NC25 subfamilies through the historical
checker's real _precheck entry point:

NC25a:
  temporary untracked worktree probe
  -> FAIL_DIRTY_SOURCE_TREE

NC25b:
  mismatched expected_head argument
  -> FAIL_HEAD_MISMATCH

No numerical evaluator is reached.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
BASE = HERE.parent
CHECKER = BASE / "flambda_transport_checker_v1.py"

PROBE = REPO_ROOT / ".nc25_dirty_state_probe.tmp"

EXPECTED_A = "FAIL_DIRTY_SOURCE_TREE"
EXPECTED_B = "FAIL_HEAD_MISMATCH"
VERDICT = "NC25_TWO_SUBFAMILY_PASS_NOT_PROMOTED"


def stop(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), *args],
        text=True,
    ).strip()


def load_checker():
    spec = importlib.util.spec_from_file_location("flambda_checker_nc25", CHECKER)
    if spec is None or spec.loader is None:
        stop("cannot construct checker import spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def capture_precheck_failure(checker, expected_head: str) -> tuple[str, object]:
    try:
        checker._precheck(expected_head)
    except checker.CheckerFailure as exc:
        return exc.code, exc.detail
    stop("precheck unexpectedly succeeded")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()
    output = ns.output.expanduser().resolve()

    if not CHECKER.is_file():
        stop(f"checker missing: {CHECKER}")
    if output.exists():
        stop(f"output already exists: {output}")
    if PROBE.exists():
        stop(f"probe path already exists: {PROBE}")

    head_pre = git("rev-parse", "HEAD")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_PRE dirty")

    checker = load_checker()

    # NC25a: canonical uncommitted dirty-state exception.
    try:
        PROBE.write_text("NC25 dirty-state probe\n", encoding="utf-8")

        status_during_probe = git("status", "--porcelain")
        if ".nc25_dirty_state_probe.tmp" not in status_during_probe:
            stop("dirty-state probe not visible to git status")

        code_a, detail_a = capture_precheck_failure(checker, head_pre)
    finally:
        if PROBE.exists():
            PROBE.unlink()

    if code_a != EXPECTED_A:
        stop(f"NC25a wrong code: {code_a!r}")
    if detail_a is not None:
        stop(f"NC25a unexpected detail: {detail_a!r}")
    if git("status", "--porcelain"):
        stop("tree did not return clean after NC25a")

    # NC25b: canonical expected_head argument mutation.
    mismatched_head = "0" * 40
    if mismatched_head == head_pre:
        stop("constructed mismatched head unexpectedly equals current HEAD")

    code_b, detail_b = capture_precheck_failure(checker, mismatched_head)

    if code_b != EXPECTED_B:
        stop(f"NC25b wrong code: {code_b!r}")
    if detail_b is not None:
        stop(f"NC25b unexpected detail: {detail_b!r}")

    head_post = git("rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during NC25 run")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-nc25-source-state-gate-run-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "control_id": "NC25",
        "method": "REAL_CHECKER_DRY_PRECHECK_TWO_SUBFAMILIES",
        "canonical_control_execution_claim": True,
        "subcases": {
            "NC25a": {
                "mutation": "WORKTREE:dirty_state",
                "expected_exact_code": EXPECTED_A,
                "observed_exact_code": code_a,
                "observed_detail": detail_a,
                "temporary_probe": PROBE.name,
                "probe_removed_after_control": True,
            },
            "NC25b": {
                "mutation": "ARGUMENT:expected_head",
                "expected_exact_code": EXPECTED_B,
                "observed_exact_code": code_b,
                "observed_detail": detail_b,
                "mutated_expected_head": mismatched_head,
            },
        },
        "checker_source_sha256": sha256_path(CHECKER),
        "run_source_sha256": sha256_path(Path(__file__).resolve()),
        "needs_numerics": False,
        "numerical_evaluator_called": False,
        "dynamic_failure_path_executed": True,
        "historical_checker_precheck_called": True,
        "end_to_end": False,
        "historical_checker_modified": False,
        "source_tree_pre_clean": True,
        "source_tree_restored_after_nc25a": True,
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

    print("CONTROL_ID=NC25")
    print("METHOD=REAL_CHECKER_DRY_PRECHECK_TWO_SUBFAMILIES")
    print("NC25A_EXPECTED_EXACT_CODE=" + EXPECTED_A)
    print("NC25A_OBSERVED_EXACT_CODE=" + code_a)
    print("NC25B_EXPECTED_EXACT_CODE=" + EXPECTED_B)
    print("NC25B_OBSERVED_EXACT_CODE=" + code_b)
    print("NUMERICAL_EVALUATOR_CALLED=FALSE")
    print("CANONICAL_CONTROL_EXECUTION_CLAIM=TRUE")
    print("HISTORICAL_CHECKER_PRECHECK_CALLED=TRUE")
    print("END_TO_END_CLAIM=FALSE")
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_RESTORED_AFTER_NC25A=TRUE")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=" + VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
