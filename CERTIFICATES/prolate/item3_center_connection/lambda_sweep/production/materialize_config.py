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

from item3_sweep.canonical import canonical_json_bytes, git_blob_sha1, parse_canonical_json
from item3_sweep.preflight import PreflightVerifier
from item3_sweep.schema import ConfigValidator

DESIGN_BLOB = "cafbf7b661911995008dda49bfb3ecabcecb1f12"
DESIGN_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/design_contract_v8_1.md"
RECEIPT_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/pilot_identity_receipt.candidate.json"
SNAPSHOT_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/dependency_snapshot.candidate.json"
DECISIONS_PATH = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/CONFIG_DECISIONS.candidate.json"
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
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    decisions, _ = read_canonical(REPO / DECISIONS_PATH)
    receipt, receipt_raw = read_canonical(REPO / RECEIPT_PATH)
    snapshot, snapshot_raw = read_canonical(REPO / SNAPSHOT_PATH)

    source_paths = {
        "runner_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/runner.py",
        "checker_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/checker.py",
        "r_tile_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/r_tile.py",
        "kernel_source_path": "CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py",
        # Candidate shape binding only. This is the audited protocol boundary, not
        # an executable Arb implementation. The status report forbids run approval.
        "adapter_source_path": "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl/item3_sweep/adapter.py",
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
        "adapter_id": "ITEM3_SWEEP_PHASE3_PROTOCOL_CANDIDATE_V1",
        "adapter_source_path": source_paths["adapter_source_path"],
        "adapter_sha256": sha_file(source_paths["adapter_source_path"]),
        "cg_pilot_run_id": 30334858060,
        "cg_pilot_receipt_path": RECEIPT_PATH,
        "cg_pilot_receipt_sha256": hashlib.sha256(receipt_raw).hexdigest(),
        "cg_pilot_source_sha256": receipt["pilot_source_sha256"],
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

    entrypoint = REPO / "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production/run_item3_sweep.py"
    report = {
        "schema": "ITEM3_SWEEP_PRODUCTION_CONFIG_CANDIDATE_REPORT_V1",
        "status": "HOLD_PRODUCTION_SOURCE_AND_RUNTIME_BINDING",
        "config_path": CONFIG_PATH,
        "config_sha256": config_sha,
        "closed_schema_valid": True,
        "preflight_identity_valid": True,
        "normative_design_blob": preflight.design_blob_sha1,
        "normative_design_sha256": config["sweep_design_sha256"],
        "lambda_target": config["lambda_target"],
        "lambda_target_approval_required": True,
        "budget_and_precision_sufficiency_certified": False,
        "adapter_binding": "PHASE3_PROTOCOL_ONLY_NOT_PRODUCTION_EXECUTABLE",
        "production_entrypoint_exists": entrypoint.is_file(),
        "python_flint_install_step_present_in_phase4_workflow": False,
        "run_authorized": False,
        "tag_created": False,
        "workflow_executed": False,
    }
    report_raw = canonical_json_bytes(report)

    if args.write:
        (REPO / CONFIG_PATH).write_bytes(config_raw)
        (REPO / CONFIG_SHA_PATH).write_text(config_sha, encoding="ascii")
        (REPO / REPORT_PATH).write_bytes(report_raw)
    print(report_raw.decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
