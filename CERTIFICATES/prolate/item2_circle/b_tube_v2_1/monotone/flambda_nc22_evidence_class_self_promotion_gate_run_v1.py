#!/usr/bin/env python3
"""Dedicated deterministic NC22 evidence-class self-promotion gate runner.

No numerical evaluator is called.  The canonical NC22 mutation changes the
producer evidence class from BINDING_CANDIDATE to BINDING and submits that
canonical JSON object to the real historical checker _load_producer_receipt.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent
CHECKER = BASE / "flambda_transport_checker_v1.py"
RECEIPT = HERE / "F_LAMBDA_NC22_EVIDENCE_CLASS_SELF_PROMOTION_GATE_RUN_V1.json"

EXPECTED_CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)
CONTROL_ID = "NC22"
METHOD = "REAL_CHECKER_LOAD_PRODUCER_RECEIPT_CANONICAL_SELF_PROMOTION"
EXPECTED_EXACT_CODE = "FAIL_PRODUCER_EVIDENCE_CLASS"
MUTATION = "PRODUCER_RECEIPT:evidence_class:BINDING_CANDIDATE->BINDING"
VERDICT = "NC22_EVIDENCE_CLASS_SELF_PROMOTION_PASS_NOT_PROMOTED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=BASE.parent.parent.parent.parent,
        text=True,
    ).strip()


repo = subprocess.check_output(
    ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
    text=True,
).strip()
repo_path = Path(repo)

head_pre = subprocess.check_output(
    ["git", "-C", repo, "rev-parse", "HEAD"],
    text=True,
).strip()
status_pre = subprocess.check_output(
    ["git", "-C", repo, "status", "--porcelain"],
    text=True,
).strip()

if status_pre:
    raise SystemExit("STOP: source tree must be clean before NC22 execution")
if RECEIPT.exists():
    raise SystemExit("STOP: NC22 receipt already exists")
if sha256(CHECKER) != EXPECTED_CHECKER_SHA256:
    raise SystemExit("STOP: historical checker SHA mismatch")

spec = importlib.util.spec_from_file_location("nc22_historical_checker", CHECKER)
if spec is None or spec.loader is None:
    raise SystemExit("STOP: cannot load historical checker")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

# Positive producer receipt: all fields inspected by _load_producer_receipt
# are the frozen expected values.
positive = {
    "schema": checker.PRODUCER_SCHEMA,
    "evidence_class": "BINDING_CANDIDATE",
    "binding_use_authorized": False,
    "checker_required": True,
    "human_promotion_required": True,
    "producer_verdict": checker.PRODUCER_PASS,
}

# Canonical NC22 self-promotion mutation: only evidence_class changes.
mutated = dict(positive)
mutated["evidence_class"] = "BINDING"

with tempfile.TemporaryDirectory(prefix="flambda_nc22_") as td:
    td_path = Path(td)
    positive_path = td_path / "positive.json"
    mutated_path = td_path / "mutated.json"

    positive_path.write_text(
        json.dumps(positive, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    mutated_path.write_text(
        json.dumps(mutated, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    # Positive control must pass the real historical loader.
    loaded, _ = checker._load_producer_receipt(positive_path)
    if loaded.get("evidence_class") != "BINDING_CANDIDATE":
        raise SystemExit("STOP: positive evidence-class control did not pass")

    observed = None
    observed_detail = None
    try:
        checker._load_producer_receipt(mutated_path)
    except checker.CheckerFailure as exc:
        observed = str(exc)
        observed_detail = getattr(exc, "detail", None)

if observed != EXPECTED_EXACT_CODE:
    raise SystemExit(
        f"STOP: expected {EXPECTED_EXACT_CODE}, observed {observed!r}"
    )

head_post = subprocess.check_output(
    ["git", "-C", repo, "rev-parse", "HEAD"],
    text=True,
).strip()
status_post = subprocess.check_output(
    ["git", "-C", repo, "status", "--porcelain"],
    text=True,
).strip()

if head_post != head_pre:
    raise SystemExit("STOP: HEAD changed during NC22 run")
if status_post:
    raise SystemExit("STOP: source tree changed during NC22 run")

receipt = {
    "schema": "flambda-nc22-evidence-class-self-promotion-gate-run-v1",
    "contract": "F_LAMBDA_CONTRACT_V1.1",
    "control_id": CONTROL_ID,
    "method": METHOD,
    "mutation": MUTATION,
    "positive_evidence_class": "BINDING_CANDIDATE",
    "mutated_evidence_class": "BINDING",
    "expected_exact_code": EXPECTED_EXACT_CODE,
    "observed_exact_code": observed,
    "observed_detail": observed_detail,
    "execution_head": head_pre,
    "historical_checker_sha256": sha256(CHECKER),
    "run_source_sha256": sha256(Path(__file__).resolve()),
    "needs_numerics": False,
    "numerical_evaluator_called": False,
    "dynamic_failure_path_executed": True,
    "historical_checker_load_producer_receipt_called": True,
    "canonical_control_execution_claim": True,
    "historical_checker_modified": False,
    "source_tree_pre_clean": True,
    "source_tree_post_clean": True,
    "head_unchanged_during_run": True,
    "end_to_end": False,
    "binding_use_authorized": False,
    "verdict": VERDICT,
}

RECEIPT.write_text(
    json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print(f"CONTROL_ID={CONTROL_ID}")
print(f"METHOD={METHOD}")
print(f"EXPECTED_EXACT_CODE={EXPECTED_EXACT_CODE}")
print(f"OBSERVED_EXACT_CODE={observed}")
print(f"MUTATION={MUTATION}")
print("POSITIVE_EVIDENCE_CLASS=BINDING_CANDIDATE")
print("MUTATED_EVIDENCE_CLASS=BINDING")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("CANONICAL_CONTROL_EXECUTION_CLAIM=TRUE")
print("HISTORICAL_CHECKER_LOAD_PRODUCER_RECEIPT_CALLED=TRUE")
print("END_TO_END_CLAIM=FALSE")
print("SOURCE_TREE_PRE=CLEAN")
print("SOURCE_TREE_POST=CLEAN")
print("HEAD_UNCHANGED_DURING_RUN=TRUE")
print(f"VERDICT={VERDICT}")
