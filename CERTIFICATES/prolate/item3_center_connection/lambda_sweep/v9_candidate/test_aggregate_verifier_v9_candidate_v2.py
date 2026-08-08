#!/usr/bin/env python3
"""Stdlib structural/mutation controls for aggregate_verifier_v9_candidate_v2."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import aggregate_verifier_v9_candidate_v2 as a


HERE = Path(__file__).resolve().parent
TARGET_LO = {"p": "123731943", "q": "26214400"}
MID = {"p": "247463911", "q": "52428800"}
ANCHOR = {"p": "118", "q": "25"}


def rat(p: str, q: str) -> dict[str, str]:
    return {"p": p, "q": q}


def box(lo: dict, hi: dict) -> dict:
    return {"lo": deepcopy(lo), "hi": deepcopy(hi)}


def source_map() -> dict[str, str]:
    values = {
        "kernel": "a" * 64,
        "adapter": "b" * 64,
        "runner": "c" * 64,
        "checker": "d" * 64,
        "checkpoint": "e" * 64,
        "bridge": "f" * 64,
        "driver": "1" * 64,
        "aggregate_verifier": sha256((HERE / "aggregate_verifier_v9_candidate_v2.py").read_bytes()).hexdigest(),
    }
    return values


def policy() -> dict:
    return {
        "checkpoint": {"attempts": 32, "max_payload_bytes": 33554432, "seconds": 120},
        "dps_control": 50,
        "dps_verify": 70,
        "integration": {"depth": 12, "limit": 200000, "tol": "1e-8"},
        "lambda_floor": rat("1", "65536"),
        "max_activations": 65536,
        "r_floor": rat("1", "65536"),
        "required_freeze_receipt_schema": a.FREEZE_SCHEMA,
    }


def two_shard_plan() -> dict:
    return {
        "dependency_snapshot_sha256": "2" * 64,
        "design_sha256": "3" * 64,
        "ordered_shards": [
            {
                "lambda_box": box(MID, ANCHOR),
                "root_r": box(rat("1", "64"), rat("1", "32")),
                "shard_id": "S00000000",
                "shard_index": 0,
            },
            {
                "lambda_box": box(TARGET_LO, MID),
                "root_r": box(rat("1", "50"), rat("11", "256")),
                "shard_id": "S00000001",
                "shard_index": 1,
            },
        ],
        "policy": policy(),
        "schema": a.PLAN_SCHEMA,
        "shard_count": 2,
        "source_sha256": source_map(),
        "total_lambda_range": box(TARGET_LO, ANCHOR),
    }


def one_shard_plan() -> dict:
    obj = two_shard_plan()
    obj["ordered_shards"] = [
        {
            "lambda_box": box(TARGET_LO, ANCHOR),
            "root_r": box(rat("1", "64"), rat("11", "256")),
            "shard_id": "S00000000",
            "shard_index": 0,
        }
    ]
    obj["shard_count"] = 1
    return obj


def canonical_write(path: Path, obj: dict) -> str:
    data = a.canonical_json_bytes(obj)
    path.write_bytes(data)
    return sha256(data).hexdigest()


def config_for(plan: dict, plan_sha: str, shard_index: int) -> dict:
    shard = plan["ordered_shards"][shard_index]
    p = plan["policy"]
    return {
        "aggregate_plan_sha256": plan_sha,
        "checkpoint": deepcopy(p["checkpoint"]),
        "dependency_snapshot_sha256": plan["dependency_snapshot_sha256"],
        "design_sha256": plan["design_sha256"],
        "dps_control": p["dps_control"],
        "dps_verify": p["dps_verify"],
        "integration": deepcopy(p["integration"]),
        "lambda_box": deepcopy(shard["lambda_box"]),
        "lambda_floor": deepcopy(p["lambda_floor"]),
        "max_activations": p["max_activations"],
        "r_floor": deepcopy(p["r_floor"]),
        "required_freeze_receipt_schema": p["required_freeze_receipt_schema"],
        "root_r": deepcopy(shard["root_r"]),
        "schema": a.CONFIG_SCHEMA,
        "shard_id": shard["shard_id"],
        "shard_index": shard["shard_index"],
        "source_sha256": deepcopy(plan["source_sha256"]),
    }


def freeze_for(plan: dict, plan_sha: str, config_sha: str) -> dict:
    return {
        "aggregate_plan_sha256": plan_sha,
        "config_sha256": config_sha,
        "dependency_snapshot_sha256": plan["dependency_snapshot_sha256"],
        "design_sha256": plan["design_sha256"],
        "freeze_verdict": "V9_FROZEN_APPROVED",
        "nonclaims": ["fixture"],
        "performance_gate_report_sha256": "4" * 64,
        "qualification_manifest_sha256": "5" * 64,
        "schema": a.FREEZE_SCHEMA,
        "source_sha256": deepcopy(plan["source_sha256"]),
        "validation_report_sha256": "6" * 64,
    }


def interval_list(raw_box: dict) -> list[dict]:
    return [deepcopy(raw_box["lo"]), deepcopy(raw_box["hi"])]


def bound_source_record(digest: str, name: str) -> dict:
    return {
        "module_origin": f"/repo/{name}.py",
        "post_import_sha256": digest,
        "pre_import_sha256": digest,
        "repo_relative_path": f"{name}.py",
        "resolved_path": f"/repo/{name}.py",
        "sha256": digest,
    }


def evidence_for(
    plan: dict,
    plan_sha: str,
    shard_index: int,
    config_sha: str,
    receipt_sha: str,
) -> dict:
    shard = plan["ordered_shards"][shard_index]
    root_r = interval_list(shard["root_r"])
    lbox = interval_list(shard["lambda_box"])
    sources = plan["source_sha256"]
    leaf = {
        "activation_index": 0,
        "lambda_box": deepcopy(lbox),
        "lambda_depth": 0,
        "lambda_score": rat("1", "10"),
        "mean_value_hi": rat("-1", "100"),
        "path_id": "ROOT",
        "r_cell": deepcopy(root_r),
        "r_depth": 0,
        "r_score": rat("1", "1"),
    }
    verified = {
        "lambda_box": deepcopy(lbox),
        "mean_value_hi_dps70": rat("-1", "200"),
        "path_id": "ROOT",
        "r_cell": deepcopy(root_r),
    }
    return {
        "aggregate_plan_sha256": plan_sha,
        "authorization": "FROZEN_PRODUCTION",
        "checker_error": None,
        "checker_report": {
            "adapter_instances_distinct": True,
            "checker_id": "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V2",
            "control_kernel_call_counts": {"F": 1},
            "dps50_attempt_count": 1,
            "dps50_leaf_count": 1,
            "dps70_verified_leaf_count": 1,
            "endpoint_g_hi_dps50": {"finite": True, "hi": rat("-1", "10"), "lo": rat("-2", "10")},
            "endpoint_g_hi_dps70": {"finite": True, "hi": rat("-1", "10"), "lo": rat("-2", "10")},
            "endpoint_g_lo_dps50": {"finite": True, "hi": rat("2", "10"), "lo": rat("1", "10")},
            "endpoint_g_lo_dps70": {"finite": True, "hi": rat("2", "10"), "lo": rat("1", "10")},
            "reason": "DPS50_REPLAY_AND_DPS70_VERIFY_PASS",
            "status": "PASS_CANDIDATE",
            "verification_kernel_call_counts": {"F": 1},
            "verify_kernel_call_counts": {"F": 1},
            "verified_leaves_dps70": [verified],
        },
        "checkpoint_commit_count": 1,
        "checkpoint_last_sha256": "7" * 64,
        "config_sha256": config_sha,
        "dependency_snapshot_sha256": plan["dependency_snapshot_sha256"],
        "design_sha256": plan["design_sha256"],
        "driver_id": "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3",
        "freeze_receipt_sha256": receipt_sha,
        "lambda_box": deepcopy(lbox),
        "nonclaim": "fixture",
        "root_r": deepcopy(root_r),
        "runner_error": None,
        "runner_result": {
            "accepted_leaves": [leaf],
            "attempts": [{"activation_index": 0}],
            "endpoint_g_hi": {"finite": True},
            "endpoint_g_lo": {"finite": True},
            "kernel_call_counts": {"F": 1},
            "reason": "ALL_CELLS_STRICT_NEG",
            "root_lambda": deepcopy(lbox),
            "root_r": deepcopy(root_r),
            "runner_id": "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V2",
            "terminal_class": "COMPLETE_CANDIDATE",
        },
        "schema": a.EVIDENCE_SCHEMA,
        "shard_id": shard["shard_id"],
        "shard_index": shard["shard_index"],
        "source_bindings": {
            "adapter": bound_source_record(sources["adapter"], "adapter"),
            "bridge": bound_source_record(sources["bridge"], "bridge"),
            "checker": bound_source_record(sources["checker"], "checker"),
            "checkpoint": bound_source_record(sources["checkpoint"], "checkpoint"),
            "kernel": {
                "checker50_post": sources["kernel"],
                "checker50_pre": sources["kernel"],
                "checker70_post": sources["kernel"],
                "checker70_pre": sources["kernel"],
                "repo_relative_path": "kernel.py",
                "runner_post": sources["kernel"],
                "runner_pre": sources["kernel"],
                "sha256": sources["kernel"],
            },
            "runner": bound_source_record(sources["runner"], "runner"),
        },
        "status": "SHARD_PASS_CANDIDATE",
    }


def materialize_fixture(root: Path, plan_obj: dict) -> tuple[Path, list[Path], list[Path], list[Path]]:
    plan_path = root / "plan.json"
    plan_sha = canonical_write(plan_path, plan_obj)
    configs: list[Path] = []
    receipts: list[Path] = []
    evidence: list[Path] = []
    for i in range(plan_obj["shard_count"]):
        config_path = root / f"config-{i}.json"
        config_sha = canonical_write(config_path, config_for(plan_obj, plan_sha, i))
        receipt_path = root / f"receipt-{i}.json"
        receipt_sha = canonical_write(receipt_path, freeze_for(plan_obj, plan_sha, config_sha))
        evidence_path = root / f"evidence-{i}.json"
        canonical_write(evidence_path, evidence_for(plan_obj, plan_sha, i, config_sha, receipt_sha))
        configs.append(config_path)
        receipts.append(receipt_path)
        evidence.append(evidence_path)
    return plan_path, configs, receipts, evidence


class AggregateV2Controls(unittest.TestCase):
    def test_two_shard_connected_aggregate_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paths = materialize_fixture(Path(td), two_shard_plan())
            result = a.verify_aggregate(
                plan_path=paths[0], config_paths=paths[1],
                freeze_receipt_paths=paths[2], evidence_paths=paths[3],
            )
            self.assertEqual(result["status"], "CERTIFIED_LAMBDA_RANGE")
            self.assertEqual(len(result["adjacency_connections"]), 1)
            self.assertEqual(result["adjacency_connections"][0]["shared_lambda"], MID)
            self.assertEqual(len(result["selected_shard_evidence_sha256"]), 2)
            self.assertRegex(result["selected_chain_tip_sha256"], r"^[0-9a-f]{64}$")

    def test_single_shard_uses_same_schema_without_adjacency(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            paths = materialize_fixture(Path(td), one_shard_plan())
            result = a.verify_aggregate(
                plan_path=paths[0], config_paths=paths[1],
                freeze_receipt_paths=paths[2], evidence_paths=paths[3],
            )
            self.assertEqual(result["status"], "CERTIFIED_LAMBDA_RANGE")
            self.assertEqual(result["adjacency_connections"], [])

    def test_nonoverlapping_adjacent_root_windows_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = two_shard_plan()
            plan["ordered_shards"][1]["root_r"] = box(rat("1", "16"), rat("1", "8"))
            plan_path = Path(td) / "plan.json"
            canonical_write(plan_path, plan)
            with self.assertRaises(a.AggregateReject):
                a.parse_plan(plan_path)

    def test_lambda_gap_or_endpoint_byte_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = two_shard_plan()
            plan["ordered_shards"][1]["lambda_box"]["hi"] = rat("123731956", "26214400")
            plan_path = Path(td) / "plan.json"
            canonical_write(plan_path, plan)
            with self.assertRaises(a.AggregateReject):
                a.parse_plan(plan_path)

    def test_aggregate_verifier_self_hash_mutation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            plan = two_shard_plan()
            plan["source_sha256"]["aggregate_verifier"] = "0" * 64
            plan_path = Path(td) / "plan.json"
            canonical_write(plan_path, plan)
            with self.assertRaises(a.AggregateReject):
                a.parse_plan(plan_path)

    def test_config_plan_hash_mutation_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = two_shard_plan()
            plan_path = root / "plan.json"
            plan_sha = canonical_write(plan_path, plan)
            parsed = a.parse_plan(plan_path)
            config = config_for(plan, plan_sha, 0)
            config["aggregate_plan_sha256"] = "0" * 64
            config_path = root / "config.json"
            canonical_write(config_path, config)
            with self.assertRaises(a.AggregateReject):
                a.parse_config_for_plan(config_path, parsed, parsed.ordered_shards[0])

    def test_freeze_receipt_wrong_config_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plan = one_shard_plan()
            plan_path = root / "plan.json"
            plan_sha = canonical_write(plan_path, plan)
            parsed = a.parse_plan(plan_path)
            config_path = root / "config.json"
            config_sha = canonical_write(config_path, config_for(plan, plan_sha, 0))
            config_obj, observed = a.parse_config_for_plan(config_path, parsed, parsed.ordered_shards[0])
            self.assertEqual(config_sha, observed)
            receipt = freeze_for(plan, plan_sha, config_sha)
            receipt["config_sha256"] = "0" * 64
            receipt_path = root / "freeze.json"
            canonical_write(receipt_path, receipt)
            with self.assertRaises(a.AggregateReject):
                a.parse_freeze_for_config(receipt_path, plan=parsed, config_obj=config_obj, config_sha=config_sha)

    def test_qualification_evidence_cannot_be_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = materialize_fixture(root, one_shard_plan())
            obj = json.loads(paths[3][0].read_text(encoding="utf-8"))
            obj["status"] = "QUALIFICATION_PASS_CANDIDATE"
            obj["authorization"] = "QUALIFICATION_ONLY"
            canonical_write(paths[3][0], obj)
            with self.assertRaises(a.AggregateReject):
                a.verify_aggregate(
                    plan_path=paths[0], config_paths=paths[1],
                    freeze_receipt_paths=paths[2], evidence_paths=paths[3],
                )

    def test_runner_checker_and_source_mutations_rejected(self) -> None:
        mutations = [
            ("runner", lambda o: o["runner_result"].__setitem__("terminal_class", "INCOMPLETE")),
            ("checker", lambda o: o["checker_report"].__setitem__("status", "FAIL")),
            ("dps70", lambda o: o["checker_report"].__setitem__("dps70_verified_leaf_count", 0)),
            ("binding", lambda o: o["source_bindings"]["runner"].__setitem__("post_import_sha256", "0" * 64)),
            ("driver", lambda o: o.__setitem__("driver_id", "WRONG_DRIVER")),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                paths = materialize_fixture(root, one_shard_plan())
                obj = json.loads(paths[3][0].read_text(encoding="utf-8"))
                mutate(obj)
                canonical_write(paths[3][0], obj)
                with self.assertRaises(a.AggregateReject):
                    a.verify_aggregate(
                        plan_path=paths[0], config_paths=paths[1],
                        freeze_receipt_paths=paths[2], evidence_paths=paths[3],
                    )

    def test_selected_chain_binds_full_evidence_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = materialize_fixture(root, one_shard_plan())
            first = a.verify_aggregate(
                plan_path=paths[0], config_paths=paths[1],
                freeze_receipt_paths=paths[2], evidence_paths=paths[3],
            )
            obj = json.loads(paths[3][0].read_text(encoding="utf-8"))
            obj["nonclaim"] = "same proof fields, changed evidence bytes"
            canonical_write(paths[3][0], obj)
            second = a.verify_aggregate(
                plan_path=paths[0], config_paths=paths[1],
                freeze_receipt_paths=paths[2], evidence_paths=paths[3],
            )
            self.assertNotEqual(first["selected_chain_tip_sha256"], second["selected_chain_tip_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
