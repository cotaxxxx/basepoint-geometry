#!/usr/bin/env python3
"""Dedicated deterministic NC01 checker-source-pin exact gate runner.

F_LAMBDA_CONTRACT_V1.1 preexecution infrastructure.

Scope:
- load the historical checker without modifying it;
- compute the actual checker source SHA with the real checker _sha;
- synthetically mutate only the checker_source_sha256 pin value;
- execute the exact real-checker _need predicate used by _precheck;
- require FAIL_PIN_MISMATCH with detail checker_source_sha256.

Nonclaims:
- not canonical tracked PIN_FILE mutation;
- not end-to-end transport;
- no numerical F or F_lambda evaluation;
- no binding promotion;
- does not modify the historical checker or tracked pin file.
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
PIN_FILE = (
    BASE
    / "dependencies"
    / "blocal_v23_source"
    / "F_LAMBDA_TRANSPORT_CHECKER_V1_PINS.json"
)

EXPECTED_CODE = "FAIL_PIN_MISMATCH"
EXPECTED_DETAIL = "checker_source_sha256"
VERDICT = "NC01_EXACT_SUBCODE_PASS_NOT_PROMOTED"


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
    spec = importlib.util.spec_from_file_location("flambda_checker_nc01", CHECKER)
    if spec is None or spec.loader is None:
        stop("cannot construct checker import spec")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()
    output = ns.output.expanduser().resolve()

    if not CHECKER.is_file():
        stop(f"CHECKER missing: {CHECKER}")
    if not PIN_FILE.is_file():
        stop(f"PIN_FILE missing: {PIN_FILE}")
    if output.exists():
        stop(f"output already exists: {output}")

    head_pre = git("rev-parse", "HEAD")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_PRE dirty")

    checker = load_checker()

    pins = json.loads(PIN_FILE.read_text(encoding="utf-8"))
    pinned_actual = pins.get(EXPECTED_DETAIL)
    actual = checker._sha(checker.CHECKER_SOURCE)

    if not isinstance(pinned_actual, str):
        stop("checker_source_sha256 pin missing")
    if pinned_actual != actual:
        stop("baseline checker source pin does not match actual source")

    mutated_pin = "0" * 64
    if mutated_pin == actual:
        stop("synthetic mutation unexpectedly equals actual source SHA")

    observed_code = None
    observed_detail = None

    try:
        checker._need(
            mutated_pin == actual,
            EXPECTED_CODE,
            EXPECTED_DETAIL,
        )
    except checker.CheckerFailure as exc:
        observed_code = exc.code
        observed_detail = exc.detail
    else:
        stop("NC01 mutation did not fail")

    if observed_code != EXPECTED_CODE:
        stop(f"wrong code: {observed_code!r}")
    if observed_detail != EXPECTED_DETAIL:
        stop(f"wrong detail: {observed_detail!r}")

    head_post = git("rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during NC01 gate")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-nc01-source-pin-gate-run-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "control_id": "NC01",
        "method": "SYNTHETIC_PIN_MUTATION_REAL_CHECKER_PREDICATE",
        "canonical_control_execution_claim": False,
        "expected_exact_code": EXPECTED_CODE,
        "expected_detail": EXPECTED_DETAIL,
        "observed_exact_code": observed_code,
        "observed_detail": observed_detail,
        "checker_source_sha256": sha256_path(CHECKER),
        "pin_file_sha256": sha256_path(PIN_FILE),
        "baseline_pin_matches_actual": True,
        "mutation_target": EXPECTED_DETAIL,
        "mutation_value": mutated_pin,
        "run_source_sha256": sha256_path(Path(__file__).resolve()),
        "needs_numerics": False,
        "numerical_evaluator_called": False,
        "dynamic_failure_path_executed": True,
        "end_to_end": False,
        "historical_checker_modified": False,
        "tracked_pin_file_modified": False,
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

    print("CONTROL_ID=NC01")
    print("METHOD=SYNTHETIC_PIN_MUTATION_REAL_CHECKER_PREDICATE")
    print("EXPECTED_EXACT_CODE=" + EXPECTED_CODE)
    print("OBSERVED_EXACT_CODE=" + observed_code)
    print("OBSERVED_DETAIL=" + str(observed_detail))
    print("NUMERICAL_EVALUATOR_CALLED=FALSE")
    print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")
    print("END_TO_END_CLAIM=FALSE")
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=" + VERDICT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
