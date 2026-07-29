#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
PROD=REPO/".github/workflows/prolate-item3-lambda-sweep.yml"
OBS=REPO/".github/workflows/prolate-item3-lambda-sweep-observer.yml"

def cbytes(obj):
    return json.dumps(obj,ensure_ascii=True,sort_keys=True,separators=(",",":")).encode()

def read(path):
    raw=path.read_bytes()
    if b"\r" in raw:
        raise RuntimeError(f"CR found: {path}")
    return raw.decode()

prod=read(PROD)
obs=read(OBS)
policy=json.loads((HERE/"WORKFLOW_POLICY.json").read_bytes())
op_raw=(HERE/"OBSERVER_POLICY.json").read_bytes()
op=json.loads(op_raw)
if cbytes(op)!=op_raw:
    raise RuntimeError("observer policy noncanonical")
if hashlib.sha256(op_raw).hexdigest()!=policy["observer_policy_sha256"]:
    raise RuntimeError("observer policy hash mismatch")

marker_start = "          python3 - <<'PY'\n"
marker_end = "\n          PY\n"
if marker_start not in obs or marker_end not in obs:
    raise RuntimeError("observer inline Python markers missing")
inline = obs.split(marker_start,1)[1].split(marker_end,1)[0]
inline = "\n".join(line[10:] if line.startswith("          ") else line for line in inline.splitlines())
compile(inline, "observer-inline.py", "exec")

checks={
 "production_tag_only": 'tags:\n      - "item3-sweep-run-*"' in prod and "workflow_dispatch" not in prod and "branches:" not in prod,
 "production_read_only": "permissions:\n  contents: read" in prod and "contents: write" not in prod,
 "precheckout_binding": 'TAG_SUFFIX="${GITHUB_REF#refs/tags/item3-sweep-run-}"' in prod and "test \"$TAG_SUFFIX\" = \"$GITHUB_SHA\"" in prod,
 "precheck_before_checkout": prod.index("Verify tag suffix equals commit SHA") < prod.index("Checkout immutable source"),
 "checkout_pinned": "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683" in prod and "persist-credentials: false" in prod,
 "postcheckout_binding": 'test "$(git rev-parse HEAD)" = "$GITHUB_SHA"' in prod,
 "design_blob_gate": "cafbf7b661911995008dda49bfb3ecabcecb1f12" in prod,
 "phase3_three_gates": all(x in prod for x in ("run_phase3_tests.py","static_audit.py","run_phase3_fixture_bridge.py")),
 "production_inputs_fail_closed": all(x in prod for x in ("config.item3-sweep-run.json","run_item3_sweep.py","test -f \"$CONFIG\"","test -f \"$ENTRY\"")),
 "artifact_action_pinned": "actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a" in prod,
 "observer_separate_trigger": 'workflow_run:' in obs and '"Prolate Item 3 Lambda Sweep"' in obs and "item3-sweep-run-*" not in obs,
 "observer_permissions": "actions: read" in obs and "contents: write" in obs,
 "observer_checkout_no_credentials": "persist-credentials: false" in obs,
 "observer_policy_loaded": "OBSERVER_POLICY.json" in obs,
 "observer_monotone": 'run_id <= previous_run_id' in obs,
 "observer_excluded_head": 'head_sha == excluded' in obs,
 "observer_atomic_git_data": all(x in obs for x in ("/git/blobs","/git/trees","/git/commits","/git/refs/heads/")),
 "observer_inline_python_compiles": True,
 "observer_no_branch_creation": "/git/refs" not in obs.replace("/git/refs/heads/",""),
 "policy_reference_commit": policy["reference_pattern_commit"]=="e86c130d18f69e9d9944a2f35a5af2f37f399881",
 "policy_run_withheld": policy["tag_created"] is False and policy["workflow_executed"] is False and policy["run_authorized"] is False,
 "observer_repo": op["source_repository"]=="cotaxxxx/geometric-dual-topology",
 "excluded_head_shape": re.fullmatch(r"[0-9a-f]{40}",op["excluded_head_sha"]) is not None,
}
fail=[k for k,v in checks.items() if not v]
report={
 "schema":"ITEM3_SWEEP_PHASE4_STATIC_AUDIT_V1",
 "checks":checks,
 "failure_count":len(fail),
 "failures":fail,
 "production_workflow_sha256":hashlib.sha256(PROD.read_bytes()).hexdigest(),
 "observer_workflow_sha256":hashlib.sha256(OBS.read_bytes()).hexdigest(),
 "workflow_policy_sha256":hashlib.sha256((HERE/"WORKFLOW_POLICY.json").read_bytes()).hexdigest(),
 "observer_policy_sha256":hashlib.sha256(op_raw).hexdigest(),
 "tag_created":False,
 "workflow_executed":False,
 "production_calculation_performed":False,
 "verdict":"PASS" if not fail else "FAIL",
}
if __name__=="__main__":
    raw=cbytes(report)
    (HERE/"PHASE4_STATIC_AUDIT.json").write_bytes(raw)
    print(raw.decode())
    raise SystemExit(0 if not fail else 1)
