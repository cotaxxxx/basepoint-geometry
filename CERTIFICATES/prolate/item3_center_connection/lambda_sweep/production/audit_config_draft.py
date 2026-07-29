#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cb(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def canonical(name):
    path = HERE / name
    raw = path.read_bytes()
    obj = json.loads(raw)
    if cb(obj) != raw:
        raise SystemExit(f"noncanonical: {name}")
    return obj, raw


D, draw = canonical("CONFIG_DECISIONS.candidate.json")
S, sraw = canonical("dependency_snapshot.candidate.json")
R, rraw = canonical("pilot_identity_receipt.candidate.json")
P, praw = canonical("PILOT_SOURCE_REDERIVATION_AUDIT.json")
T, traw = canonical("TARGET_RANGE_POLICY.json")
ast.parse((HERE / "materialize_config.py").read_text(), filename="materialize_config.py")
ast.parse((HERE / "arb_adapter.py").read_text(), filename="arb_adapter.py")
ast.parse((HERE / "run_item3_sweep.py").read_text(), filename="run_item3_sweep.py")
required = {"L-CONT", "L-DERIV", "L-ENCL", "L-SIGN", "L-IVT"}
checks = {
    "decision_status_hold": D["status"] == "REQUIRES_CHAT_SOURCE_AUDIT_PHASE4_REAUDIT_AND_USER_CONFIG_APPROVAL",
    "target_is_anchor_minus_2^-12": D["lambda_target"] == {"p": "483303", "q": "102400"},
    "target_requires_approval": D["lambda_target_approval_required"] is True,
    "target_policy_relation": T["pipeline_validation_target"] == D["lambda_target"] and T["current_contract_can_reach_a_c"] is False,
    "pilot_run_id": S["pilot_run_id"] == R["run_id"] == P["pilot_run_id"] == 30334858060,
    "pilot_source_relation": S["pilot_source_sha256"] == R["pilot_source_sha256"] == D["pilot_source_sha256"] == P["pilot_source_sha256"] == "9da05b2c44119c9937c19a2184ea9722de7876442235896f1f0e0dbc076f2ecc",
    "pilot_source_independently_rederived": P["source_hash_rederived_from_internal_manifest"] is True and P["source_hash_rederived_from_member_bytes"] is True and P["verdict"] == "PASS",
    "pilot_artifact_relation": P["artifact_id"] == D["pilot_artifact_id"] == 8680673043 and P["artifact_sha256"] == D["pilot_artifact_sha256"],
    "pilot_kernel_relation": S["pilot_kernel_source_sha256"] == R["pilot_kernel_source_sha256"] == "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac",
    "snapshot_relation": hashlib.sha256(sraw).hexdigest() == R["dependency_snapshot_sha256"] == D["dependency_snapshot_sha256"],
    "receipt_relation": hashlib.sha256(rraw).hexdigest() == D["pilot_identity_receipt_sha256"],
    "root_endpoint_bytes": S["certified_root_interval"]["lower_endpoint"] == {"p": "1", "q": "64"} and S["certified_root_interval"]["upper_endpoint"] == {"p": "11", "q": "256"},
    "logical_key_set": set(S["logical_dependencies"]) == required == set(D["sweep_logical_dependencies"]),
    "logical_hashes": all(hashlib.sha256(cb(S["logical_dependencies"][key])).hexdigest() == D["sweep_logical_dependencies"][key]["dependency_entry_sha256"] for key in required),
    "run_withheld": D["run_authorized"] is False and D["tag_created"] is False and D["workflow_executed"] is False,
    "source_binding_candidate": D["adapter_binding"] == "PRODUCTION_ARB_ADAPTER_IMPLEMENTED_CANDIDATE" and D["production_entrypoint_status"] == "IMPLEMENTED_CANDIDATE",
    "runtime_reaudit_hold": D["phase4_runtime_dependency_status"] == "PINNED_CANDIDATE_REAUDIT_REQUIRED",
}
fail = [key for key, value in checks.items() if not value]
report = {
    "checks": checks,
    "failure_count": len(fail),
    "failures": fail,
    "kernel_evaluations": 0,
    "mathematical_calculations": 0,
    "schema": "ITEM3_SWEEP_PRODUCTION_CONFIG_DRAFT_AUDIT_V2",
    "verdict": "PASS" if not fail else "FAIL",
}
raw = cb(report)
(HERE / "CONFIG_DRAFT_STATIC_AUDIT.json").write_bytes(raw)
print(raw.decode())
raise SystemExit(0 if not fail else 1)
