#!/usr/bin/env python3
"""Dedicated deterministic NC19 checker-F_lambda-cap-pin exact gate runner.

F_LAMBDA_CONTRACT_V1.1 preexecution infrastructure.

Scope:
- load the historical checker without modifying it;
- verify the tracked baseline checker_flambda_cell_call_cap pin;
- synthetically mutate only that pin value;
- execute the exact real-checker _need predicate used by _precheck;
- require FAIL_CHECKER_FLAMBDA_CAP_PIN.

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

PIN_KEY = "checker_flambda_cell_call_cap"
EXPECTED_CODE = "FAIL_CHECKER_FLAMBDA_CAP_PIN"
VERDICT = "NC19_EXACT_SUBCODE_PASS_NOT_PROMOTED"


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
    spec = importlib.util.spec_from_file_location("flambda_checker_nc19", CHECKER)
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

    declared_cap = checker.CHECKER_FLAMBDA_CELL_CALL_CAP
    pinned_cap = pins.get(PIN_KEY)

    if not isinstance(declared_cap, int) or declared_cap <= 0:
        stop("historical checker cap is not a positive integer")
    if pinned_cap != declared_cap:
        stop("baseline checker F_lambda cap pin does not match checker constant")

    mutated_cap = declared_cap + 1
    observed_code = None
    observed_detail = None

    try:
        checker._need(
            mutated_cap == declared_cap,
            EXPECTED_CODE,
        )
    except checker.CheckerFailure as exc:
        observed_code = exc.code
        observed_detail = exc.detail
    else:
        stop("NC19 mutation did not fail")

    if observed_code != EXPECTED_CODE:
        stop(f"wrong code: {observed_code!r}")
    if observed_detail is not None:
        stop(f"unexpected detail: {observed_detail!r}")

    head_post = git("rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during NC19 gate")
    if git("status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-nc19-checker-flambda-cap-pin-gate-run-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "control_id": "NC19",
        "method": "SYNTHETIC_PIN_MUTATION_REAL_CHECKER_PREDICATE",
        "canonical_control_execution_claim": False,
        "expected_exact_code": EXPECTED_CODE,
        "observed_exact_code": observed_code,
        "observed_detail": observed_detail,
        "mutation_target": PIN_KEY,
        "baseline_pin_value": pinned_cap,
        "checker_declared_cap": declared_cap,
        "mutated_pin_value": mutated_cap,
        "baseline_pin_matches_checker_constant": True,
        "checker_source_sha256": sha256_path(CHECKER),
        "pin_file_sha256": sha256_path(PIN_FILE),
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

    print("CONTROL_ID=NC19")
    print("METHOD=SYNTHETIC_PIN_MUTATION_REAL_CHECKER_PREDICATE")
    print("MUTATION_TARGET=" + PIN_KEY)
    print("BASELINE_PIN_VALUE=" + str(pinned_cap))
    print("MUTATED_PIN_VALUE=" + str(mutated_cap))
    print("EXPECTED_EXACT_CODE=" + EXPECTED_CODE)
    print("OBSERVED_EXACT_CODE=" + observed_code)
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
