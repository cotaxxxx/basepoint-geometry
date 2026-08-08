#!/usr/bin/env python3
"""Deterministic one-shard rehearsal plan/config generator for Item 3 sweep v9.

Dependency direction is deliberately one-way:

    design/source/dependency bytes -> plan bytes -> config bytes.

The plan contains no config hash, so no plan<->config hash cycle exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BASE = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/"
PLAN_SCHEMA = "ITEM3_SWEEP_V9_SHARD_PLAN_V2"
CONFIG_SCHEMA = "ITEM3_SWEEP_V9_SHARD_RUN_CONFIG_V1"
FREEZE_SCHEMA = "ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1"

DESIGN_PATH = BASE + "v9_draft/design_contract_v9_integrated_candidate_v2.md"
SOURCE_PATHS = {
    "kernel": BASE + "v9_candidate/prolate_F_derivatives_cleanroom_v9_candidate.py",
    "adapter": BASE + "v9_candidate/adapter_v9_candidate_v2.py",
    "runner": BASE + "v9_candidate/runner_v9_candidate_v2.py",
    "checker": BASE + "v9_candidate/checker_v9_candidate_v2.py",
    "checkpoint": BASE + "v9_candidate/checkpoint_v9_candidate.py",
    "bridge": BASE + "v9_candidate/checkpoint_bridge_v9_candidate_v2.py",
    "driver": BASE + "v9_candidate/rehearsal_driver_v9_candidate_v3.py",
    "aggregate_verifier": BASE + "v9_candidate/aggregate_verifier_v9_candidate_v2.py",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def rat(p: int, q: int = 1) -> dict[str, str]:
    from fractions import Fraction
    f = Fraction(p, q)
    return {"p": str(f.numerator), "q": str(f.denominator)}


def interval(lo: dict[str, str], hi: dict[str, str]) -> dict[str, Any]:
    return {"lo": lo, "hi": hi}


def require_file(root: Path, relative: str) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"path escapes repository: {relative}") from exc
    if not path.is_file():
        raise RuntimeError(f"required file missing: {relative}")
    return path


def build(
    *,
    repo_root: Path,
    dependency_snapshot_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    repo_root = repo_root.resolve(strict=True)
    design_path = require_file(repo_root, DESIGN_PATH)
    if not dependency_snapshot_path.is_absolute():
        dependency_snapshot_path = (repo_root / dependency_snapshot_path).resolve(strict=True)
    else:
        dependency_snapshot_path = dependency_snapshot_path.resolve(strict=True)
    try:
        dependency_snapshot_path.relative_to(repo_root)
    except ValueError as exc:
        raise RuntimeError("dependency snapshot must lie inside repository root") from exc

    design_sha = sha256_file(design_path)
    dependency_sha = sha256_file(dependency_snapshot_path)
    source_sha = {
        key: sha256_file(require_file(repo_root, relative))
        for key, relative in SOURCE_PATHS.items()
    }

    policy = {
        "checkpoint": {"attempts": 32, "max_payload_bytes": 33554432, "seconds": 120},
        "dps_control": 50,
        "dps_verify": 70,
        "integration": {"depth": 12, "limit": 200000, "tol": "1e-8"},
        "lambda_floor": rat(1, 1 << 16),
        "max_activations": 65536,
        "r_floor": rat(1, 1 << 16),
        "required_freeze_receipt_schema": FREEZE_SCHEMA,
    }
    rehearsal_lambda = interval(
        rat(123731943, 26214400),
        rat(118, 25),
    )
    rehearsal_r = interval(rat(1, 64), rat(11, 256))

    plan = {
        "dependency_snapshot_sha256": dependency_sha,
        "design_sha256": design_sha,
        "ordered_shards": [
            {
                "lambda_box": rehearsal_lambda,
                "root_r": rehearsal_r,
                "shard_id": "S00000000",
                "shard_index": 0,
            }
        ],
        "policy": policy,
        "schema": PLAN_SCHEMA,
        "shard_count": 1,
        "source_sha256": source_sha,
        "total_lambda_range": rehearsal_lambda,
    }
    plan_bytes = canonical_bytes(plan)
    plan_sha = hashlib.sha256(plan_bytes).hexdigest()

    config = {
        "aggregate_plan_sha256": plan_sha,
        "checkpoint": policy["checkpoint"],
        "dependency_snapshot_sha256": dependency_sha,
        "design_sha256": design_sha,
        "dps_control": policy["dps_control"],
        "dps_verify": policy["dps_verify"],
        "integration": policy["integration"],
        "lambda_box": rehearsal_lambda,
        "lambda_floor": policy["lambda_floor"],
        "max_activations": policy["max_activations"],
        "r_floor": policy["r_floor"],
        "required_freeze_receipt_schema": policy["required_freeze_receipt_schema"],
        "root_r": rehearsal_r,
        "schema": CONFIG_SCHEMA,
        "shard_id": "S00000000",
        "shard_index": 0,
        "source_sha256": source_sha,
    }
    config_bytes = canonical_bytes(config)
    config_sha = hashlib.sha256(config_bytes).hexdigest()

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "rehearsal_plan_v2.json").write_bytes(plan_bytes)
    (output_dir / "rehearsal_plan_v2.json.sha256").write_text(plan_sha + "\n", encoding="ascii")
    (output_dir / "rehearsal_shard_config_v1.json").write_bytes(config_bytes)
    (output_dir / "rehearsal_shard_config_v1.json.sha256").write_text(config_sha + "\n", encoding="ascii")

    report = {
        "config_sha256": config_sha,
        "dependency_snapshot_sha256": dependency_sha,
        "design_sha256": design_sha,
        "plan_sha256": plan_sha,
        "schema": "ITEM3_SWEEP_V9_REHEARSAL_PLAN_CONFIG_BUILD_V1",
        "source_sha256": source_sha,
        "status": "BUILT_CANDIDATE",
    }
    (output_dir / "rehearsal_plan_config_build_report.json").write_bytes(canonical_bytes(report))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--dependency-snapshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = build(
        repo_root=args.repo_root,
        dependency_snapshot_path=args.dependency_snapshot,
        output_dir=args.output_dir,
    )
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
