#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PROD = REPO / ".github/workflows/prolate-item3-lambda-sweep.yml"
OBS = REPO / ".github/workflows/prolate-item3-lambda-sweep-observer.yml"
REQ = REPO / "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/requirements-python-flint.txt"


def cbytes(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def read(path):
    raw = path.read_bytes()
    if b"\r" in raw:
        raise RuntimeError(f"CR found: {path}")
    return raw.decode()


prod = read(PROD)
obs = read(OBS)
policy_raw = (HERE / "WORKFLOW_POLICY.json").read_bytes()
policy = json.loads(policy_raw)
op_raw = (HERE / "OBSERVER_POLICY.json").read_bytes()
op = json.loads(op_raw)
req_raw = REQ.read_bytes()
if cbytes(policy) != policy_raw:
    raise RuntimeError("workflow policy noncanonical")
if cbytes(op) != op_raw:
    raise RuntimeError("observer policy noncanonical")
if hashlib.sha256(op_raw).hexdigest() != policy["observer_policy_sha256"]:
    raise RuntimeError("observer policy hash mismatch")
if hashlib.sha256(req_raw).hexdigest() != policy["python_flint_requirements_sha256"]:
    raise RuntimeError("python-flint requirements hash mismatch")

marker_start = "          python3 - <<'PY'\n"
marker_end = "\n          PY\n"
if marker_start not in obs or marker_end not in obs:
    raise RuntimeError("observer inline Python markers missing")
inline = obs.split(marker_start, 1)[1].split(marker_end, 1)[0]
inline = "\n".join(line[10:] if line.startswith("          ") else line for line in inline.splitlines())
compile(inline, "observer-inline.py", "exec")

checks = {
    "production_tag_only": 'tags:\n      - "item3-sweep-run-*"' in prod and "workflow_dispatch" not in prod and "branches:" not in prod,
    "production_permissions": "contents: read" in prod and "actions: read" in prod and "contents: write" not in prod,
    "precheckout_binding": 'TAG_SUFFIX="${GITHUB_REF#refs/tags/item3-sweep-run-}"' in prod and 'test "$TAG_SUFFIX" = "$GITHUB_SHA"' in prod,
    "precheck_before_checkout": prod.index("Verify tag suffix equals commit SHA") < prod.index("Checkout immutable source"),
    "checkout_pinned": "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683" in prod and "persist-credentials: false" in prod,
    "postcheckout_binding": 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"' in prod,
    "setup_python_pinned": "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in prod and 'python-version: "3.12"' in prod,
    "python_flint_require_hashes": all(token in prod for token in ("--require-hashes", "--no-deps", "--only-binary=:all:")),
    "python_flint_wheel_hash": policy["python_flint_wheel_sha256"].encode() in req_raw,
    "design_blob_gate": "cafbf7b661911995008dda49bfb3ecabcecb1f12" in prod,
    "phase3_three_gates": all(x in prod for x in ("run_phase3_tests.py", "static_audit.py", "run_phase3_fixture_bridge.py")),
    "production_source_gates": all(x in prod for x in ("audit_config_draft.py", "audit_production_source.py", "test_production_source.py")),
    "pilot_artifact_pin": str(policy["pilot_artifact_id"]) in prod and policy["pilot_artifact_sha256"] in prod,
    "pilot_source_rederivation_gate": "verify_pilot_artifact.py" in prod and "pilot-artifact-verification.json" in prod,
    "production_inputs_fail_closed": all(x in prod for x in ("config.item3-sweep-run.json", "config.item3-sweep-run.sha256", "run_item3_sweep.py", 'test -f "$CONFIG"', 'test -f "$ENTRY"')),
    "artifact_action_pinned": "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in prod,
    "observer_separate_trigger": 'workflow_run:' in obs and '"Prolate Item 3 Lambda Sweep"' in obs and "item3-sweep-run-*" not in obs,
    "observer_permissions": "actions: read" in obs and "contents: write" in obs,
    "observer_checkout_no_credentials": "persist-credentials: false" in obs,
    "observer_policy_loaded": "OBSERVER_POLICY.json" in obs,
    "observer_monotone": 'run_id <= previous_run_id' in obs,
    "observer_excluded_head": 'head_sha == excluded' in obs,
    "observer_atomic_git_data": all(x in obs for x in ("/git/blobs", "/git/trees", "/git/commits", "/git/refs/heads/")),
    "observer_inline_python_compiles": True,
    "observer_no_branch_creation": "/git/refs" not in obs.replace("/git/refs/heads/", ""),
    "policy_reaudit_required": policy["prior_phase4_pass_applies_to_current_workflow_bytes"] is False and policy["status"].startswith("PHASE4_REAUDIT_REQUIRED"),
    "policy_run_withheld": policy["tag_created"] is False and policy["workflow_executed"] is False and policy["run_authorized"] is False,
    "observer_repo": op["source_repository"] == "cotaxxxx/geometric-dual-topology",
    "excluded_head_shape": re.fullmatch(r"[0-9a-f]{40}", op["excluded_head_sha"]) is not None,
}
fail = [key for key, value in checks.items() if not value]
report = {
    "checks": checks,
    "failure_count": len(fail),
    "failures": fail,
    "observer_policy_sha256": hashlib.sha256(op_raw).hexdigest(),
    "observer_workflow_sha256": hashlib.sha256(OBS.read_bytes()).hexdigest(),
    "production_calculation_performed": False,
    "production_workflow_sha256": hashlib.sha256(PROD.read_bytes()).hexdigest(),
    "python_flint_requirements_sha256": hashlib.sha256(req_raw).hexdigest(),
    "schema": "ITEM3_SWEEP_PHASE4_STATIC_AUDIT_V2",
    "tag_created": False,
    "verdict": "PASS" if not fail else "FAIL",
    "workflow_executed": False,
    "workflow_policy_sha256": hashlib.sha256(policy_raw).hexdigest(),
}
if __name__ == "__main__":
    raw = cbytes(report)
    (HERE / "PHASE4_STATIC_AUDIT_V2.json").write_bytes(raw)
    print(raw.decode())
    raise SystemExit(0 if not fail else 1)
