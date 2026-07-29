#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PHASE3 = REPO / "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl"
if str(PHASE3) not in sys.path:
    sys.path.insert(0, str(PHASE3))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from item3_sweep.canonical import canonical_json_bytes, parse_canonical_json
from item3_sweep.preflight import PreflightVerifier
from item3_sweep.schema import ConfigValidator
from verify_pilot_artifact import verify_artifact

DESIGN_BLOB = "cafbf7b661911995008dda49bfb3ecabcecb1f12"
DESIGN_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/design_contract_v8_1.md"
RECEIPT_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/pilot_identity_receipt.candidate.json"
SNAPSHOT_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/dependency_snapshot.candidate.json"
DECISIONS_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/CONFIG_DECISIONS.candidate.json"
TARGET_POLICY_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/TARGET_RANGE_POLICY.json"
CONFIG_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/config.item3-sweep-run.candidate.json"
CONFIG_SHA_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/config.item3-sweep-run.candidate.sha256"
REPORT_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/PRODUCTION_CONFIG_CANDIDATE_REPORT.json"


def read_canonical(path: Path):
    raw = path.read_bytes()
    return parse_canonical_json(raw), raw


def sha_file(relative: str) -> str:
    return hashlib.sha256((REPO / relative).read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-artifact-zip", type=Path, required=True)
    parser.add_argument("--pilot-artifact-dir", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    decisions, _ = read_canonical(REPO / DECISIONS_PATH)
    receipt, receipt_raw = read_canonical(REPO / RECEIPT_PATH)
    snapshot, snapshot_raw = read_canonical(REPO / SNAPSHOT_PATH)
    target_policy, _ = read_canonical(REPO / TARGET_POLICY_PATH)
    pilot_evidence = verify_artifact(
        zip_path=args.pilot_artifact_zip,
        extracted_dir=args.pilot_artifact_dir,
    )
    if pilot_evidence.pilot_source_sha256 != receipt["pilot_source_sha256"]:
        raise RuntimeError("artifact-rederived pilot source SHA-256 differs from receipt")
    if pilot_evidence.pilot_source_sha256 != snapshot["pilot_source_sha256"]:
        raise RuntimeError("artifact-rederived pilot source SHA-256 differs from snapshot")
    if pilot_evidence.pilot_source_sha256 != decisions["pilot_source_sha256"]:
        raise RuntimeError("artifact-rederived pilot source SHA-256 differs from decisions")
    if target_policy["pipeline_validation_target"] != decisions["lambda_target"]:
        raise RuntimeError("target range policy differs from candidate lambda_target")
    if target_policy["current_contract_can_reach_a_c"] is not False:
        raise RuntimeError("target policy must fail closed on upward a_c coverage")

    source_paths = {
        "runner_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/runner.py",
        "checker_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/checker.py",
        "r_tile_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/r_tile.py",
        "kernel_source_path": "CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py",
        "adapter_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/arb_adapter.py",
    }

    config = {
        "sweep_design_path": DESIGN_PATH,
        "sweep_design_sha256": sha_file(DESIGN_PATH),
        "lambda_anchor": decisions["lambda_anchor"],
        "lambda_target": decisions["lambda_target"],
        "min_lambda_width_exp": decisions["min_lambda_width_exp"],
        "delta_overlap_min": decisions["delta_overlap_min"],
        "window_grid_exp": decisions["window_grid_exp"],
        "window_min_width_exp": decisions["window_min_width_exp"],
        "w0_lo": decisions["w0_lo"],
        "w0_hi": decisions["w0_hi"],
        "global_eval_limit": decisions["global_eval_limit"],
        "per_box_eval_limit": decisions["per_box_eval_limit"],
        "max_lambda_depth": decisions["max_lambda_depth"],
        "max_r_cells_per_box": decisions["max_r_cells_per_box"],
        "dps": decisions["dps"],
        "checker_dps": decisions["checker_dps"],
        "runner_source_path": source_paths["runner_source_path"],
        "runner_source_sha256": sha_file(source_paths["runner_source_path"]),
        "checker_source_path": source_paths["checker_source_path"],
        "checker_source_sha256": sha_file(source_paths["checker_source_path"]),
        "r_tile_algorithm_id": "ADAPTIVE_R_BISECTION_V1",
        "r_tile_source_path": source_paths["r_tile_source_path"],
        "r_tile_source_sha256": sha_file(source_paths["r_tile_source_path"]),
        "kernel_source_path": source_paths["kernel_source_path"],
        "kernel_source_sha256": sha_file(source_paths["kernel_source_path"]),
        "adapter_id": "ITEM3_SWEEP_ARB_F_OVER_R_V1",
        "adapter_source_path": source_paths["adapter_source_path"],
        "adapter_sha256": sha_file(source_paths["adapter_source_path"]),
        "cg_pilot_run_id": 30334858060,
        "cg_pilot_receipt_path": RECEIPT_PATH,
        "cg_pilot_receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
        "cg_pilot_source_sha256": pilot_evidence.pilot_source_sha256,
        "cg_pilot_kernel_source_sha256": receipt["pilot_kernel_source_sha256"],
        "dependency_snapshot_path": SNAPSHOT_PATH,
        "dependency_snapshot_sha256": hashlib.sha256(snapshot_raw).hexdigest(),
        "sweep_logical_dependencies": decisions["sweep_logical_dependencies"],
        "lambda_coordinate_encoding_id": "CANONICAL_REDUCED_RATIONAL_V1",
        "r_coordinate_encoding_id": "CANONICAL_DYADIC_V1",
        "enclosure_encoding_id": "CANONICAL_DYADIC_INTERVAL_V1",
    }

    validated = ConfigValidator().validate(config)
    config_raw = canonical_json_bytes(validated.raw)
    config_sha = hashlib.sha256(config_raw).hexdigest()

    preflight = PreflightVerifier(
        checkout_root=REPO,
        expected_design_blob_sha1=DESIGN_BLOB,
    ).verify(
        config_bytes=config_raw,
        stored_config_sha256=config_sha,
        receipt_bytes=receipt_raw,
        snapshot_bytes=snapshot_raw,
    )

    report = {
        "adapter_binding": "PRODUCTION_ARB_ADAPTER_CANDIDATE",
        "budget_and_precision_sufficiency_certified": False,
        "closed_schema_valid": True,
        "config_path": CONFIG_PATH,
        "config_sha256": config_sha,
        "lambda_target": config["lambda_target"],
        "lambda_target_approval_required": True,
        "normative_design_blob": preflight.design_blob_sha1,
        "normative_design_sha256": config["sweep_design_sha256"],
        "phase4_reaudit_required": True,
        "pilot_artifact_id": pilot_evidence.artifact_id,
        "pilot_artifact_sha256": pilot_evidence.artifact_sha256,
        "pilot_source_hash_rederived_from_artifact": True,
        "pilot_source_sha256": pilot_evidence.pilot_source_sha256,
        "preflight_identity_valid": True,
        "production_entrypoint_exists": (HERE / "run_item3_sweep.py").is_file(),
        "python_flint_require_hashes_candidate_present": (HERE / "requirements-python-flint.txt").is_file(),
        "run_authorized": False,
        "schema": "ITEM3_SWEEP_PRODUCTION_CONFIG_CANDIDATE_REPORT_V2",
        "status": "HOLD_USER_CONFIG_APPROVAL_AND_PHASE4_REAUDIT",
        "tag_created": False,
        "target_range_policy_status": target_policy["status"],
        "workflow_executed": False,
    }
    report_raw = canonical_json_bytes(report)

    if args.write:
        (REPO / CONFIG_PATH).write_bytes(config_raw)
        (REPO / CONFIG_SHA_PATH).write_text(config_sha + "\n", encoding="ascii")
        (REPO / REPORT_PATH).write_bytes(report_raw)
    print(report_raw.decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
