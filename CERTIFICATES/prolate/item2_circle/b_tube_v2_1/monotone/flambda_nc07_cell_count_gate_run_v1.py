#!/usr/bin/env python3
"""Dedicated deterministic NC07 cell-count gate runner.

Scope:
- execute the existing frozen NC07 cell-count gate asset;
- require both NC07a and NC07b to emit FAIL_LAMBDA_TILING;
- require the positive control and PASS_NOT_PROMOTED markers;
- perform no numerical kernel evaluation;
- make no end-to-end or promotion claim.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
GATE = HERE / "flambda_nc07_cell_count_gate_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC07_CELL_COUNT_GATE_RUN_V1.json"

EXPECTED_GATE_SHA256 = (
    "55fe03e1c661db550958b8badbc2ccc4b1f5b093cde1c0ade28bc51263b5d4e1"
)
EXPECTED_CODE = "FAIL_LAMBDA_TILING"
VERDICT = "NC07_EXACT_SUBCODE_PASS_NOT_PROMOTED"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO,
        text=True,
    ).strip()


if sha256_file(GATE) != EXPECTED_GATE_SHA256:
    raise SystemExit("STOP: NC07_GATE_SHA_MISMATCH")

if git("status", "--porcelain"):
    raise SystemExit("STOP: WORKTREE_NOT_CLEAN_BEFORE_RUN")

execution_head = git("rev-parse", "HEAD")

env = os.environ.copy()
env["PYTHONDONTWRITEBYTECODE"] = "1"

proc = subprocess.run(
    ["python3", str(GATE)],
    cwd=REPO,
    env=env,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

print(proc.stdout, end="")

if proc.returncode != 0:
    raise SystemExit(f"STOP: NC07_GATE_EXIT_{proc.returncode}")

required = [
    "NC07_POSITIVE_CONTROL=PASS",
    "NC07a=FAIL_LAMBDA_TILING",
    "NC07b=FAIL_LAMBDA_TILING",
    "NC07_CELL_COUNT_GATE=PASS_NOT_PROMOTED",
]
missing = [x for x in required if x not in proc.stdout]
if missing:
    raise SystemExit("STOP: NC07_REQUIRED_OUTPUT_MISSING:" + ";".join(missing))

if git("rev-parse", "HEAD") != execution_head:
    raise SystemExit("STOP: HEAD_CHANGED_DURING_RUN")

if git("status", "--porcelain"):
    raise SystemExit("STOP: WORKTREE_CHANGED_DURING_RUN")

runner_sha = sha256_file(Path(__file__).resolve())

receipt = {
    "schema": "flambda-nc07-cell-count-gate-run-v1",
    "control_id": "NC07",
    "expected_code": EXPECTED_CODE,
    "execution_head": execution_head,
    "gate_asset": str(GATE.relative_to(REPO)),
    "gate_asset_sha256": EXPECTED_GATE_SHA256,
    "runner": str(Path(__file__).resolve().relative_to(REPO)),
    "runner_sha256": runner_sha,
    "stdout_sha256": sha256_bytes(proc.stdout.encode("utf-8")),
    "method": "DIRECT_EXISTING_GATE_UNIT",
    "numerical_evaluator_called": False,
    "end_to_end_claim": False,
    "canonical_control_execution_claim": False,
    "verdict": VERDICT,
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("CONTROL_ID=NC07")
print("METHOD=DIRECT_EXISTING_GATE_UNIT")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("END_TO_END_CLAIM=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=FALSE")
print(f"VERDICT={VERDICT}")
print(f"RECEIPT={RECEIPT.relative_to(REPO)}")
