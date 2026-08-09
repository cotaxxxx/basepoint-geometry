#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, sys
from pathlib import Path

BASE = Path("CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate")
PLAN = BASE / "connected_pilot_identity_v1/plan_config/connected_pilot_plan_v2.json"
CONFIGS = [
    BASE / f"connected_pilot_identity_v1/plan_config/shard_{i}_config_v1.json"
    for i in range(4)
]
DEPS = BASE / "connected_pilot_identity_v1/dependencies/dependency_snapshot_v9_candidate.json"
AGG = BASE / "aggregate_verifier_v9_candidate_v2.py"
LEGACY_REPORT = Path(sys.argv[1])
OUT = Path(sys.argv[2])

EXPECTED = {
    "plan_sha256":"aba9b2d1571cdc7c9aa7c4520233cafe7d7690f45bbcd7bbf7068339c78d67a9",
    "config_sha256":[
        "f3838d1c49f917e19fabfdb8c991dd5040128f81aadd58a930218dceecef2b03",
        "2c1a612c1d32c5675af92dd0fad2c07b4af18b0bab370e62d44a68a8d44d0f41",
        "32214842510f63cdf781dac4f145d5d4a46942b1194d9386717cdba1a4c95002",
        "36bd40c39c722805f3742b3a9e8f562e2c39deca07c4f27666f54a88bf6e7ebe",
    ],
    "dependency_snapshot_sha256":"ee033ab46b844168887a6e2e1f5a2b97cc460d1b43bbafd77be49897127950aa",
    "aggregate_verifier_sha256":"c8990f24f28fba74178b99129d1fd1c4d0bd05a46a65e7e0a11e1fea9b251eef",
}
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load_canonical(p: Path):
    raw = p.read_bytes()
    obj = json.loads(raw.decode("utf-8"))
    can = (json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) + "\n").encode()
    if raw != can:
        raise SystemExit(f"noncanonical JSON: {p}")
    return obj
if sha(PLAN) != EXPECTED["plan_sha256"]:
    raise SystemExit("plan SHA mismatch")
if sha(DEPS) != EXPECTED["dependency_snapshot_sha256"]:
    raise SystemExit("dependency snapshot SHA mismatch")
if sha(AGG) != EXPECTED["aggregate_verifier_sha256"]:
    raise SystemExit("aggregate verifier SHA mismatch")
observed_cfg = [sha(p) for p in CONFIGS]
if observed_cfg != EXPECTED["config_sha256"]:
    raise SystemExit(f"config SHA mismatch: {observed_cfg}")

spec = importlib.util.spec_from_file_location("connected_v1_aggregate", AGG)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
plan = mod.parse_plan(PLAN)
for i, p in enumerate(CONFIGS):
    mod.parse_config_for_plan(p, plan, plan.ordered_shards[i])

legacy = load_canonical(LEGACY_REPORT)
if legacy.get("schema") != "ITEM3_SWEEP_V9_256_LEAF_VALIDATION_REPORT_V2":
    raise SystemExit("legacy validation schema mismatch")
if legacy.get("status") != "PASSED" or legacy.get("leaf_count") != 256 or legacy.get("failure_count") != 0:
    raise SystemExit("legacy counted 256-leaf validation not PASS")
if legacy.get("missing_control_ids") or legacy.get("extra_control_ids") or legacy.get("failed_control_ids"):
    raise SystemExit("legacy validation ID-set mismatch")

report = {
    "schema":"ITEM3_SWEEP_V9_CONNECTED_IDENTITY_VALIDATION_REPORT_V1",
    "status":"PASSED",
    "authorization":"VALIDATION_ONLY",
    "leaf_count":256,
    "failure_count":0,
    "category_counts":legacy["category_counts"],
    "category_floors":legacy["category_floors"],
    "semantic_tuple_unique":legacy["semantic_tuple_unique"],
    "control_ids_unique":legacy["control_ids_unique"],
    "missing_control_ids":[],
    "extra_control_ids":[],
    "failed_control_ids":[],
    "prepublished_expect_sha256":legacy["expect_sha256"],
    "control_matrix_sha256":legacy["matrix_sha256"],
    "corpus_validation_source_sha256":legacy["validation_source_sha256"],
    "independent_reference_sha256":legacy["independent_reference_sha256"],
    "underlying_counted_validation_report_sha256":sha(LEGACY_REPORT),
    "target_bundle":{
        "plan_sha256":EXPECTED["plan_sha256"],
        "config_sha256":EXPECTED["config_sha256"],
        "dependency_snapshot_sha256":EXPECTED["dependency_snapshot_sha256"],
        "source_sha256":plan.source_sha256,
        "design_sha256":plan.design_sha256,
    },
    "freeze_authorized":False,
    "production_rehearsal_authorized":False,
    "tag_created":False,
    "certified_lambda_range":False,
}
OUT.parent.mkdir(parents=True, exist_ok=False)
OUT.write_text(json.dumps(report, sort_keys=True, separators=(",",":")) + "\n", encoding="utf-8")
print(json.dumps(report, sort_keys=True))
