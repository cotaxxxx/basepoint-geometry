#!/usr/bin/env python3
"""Short canonical-config/source-binding controls for rehearsal driver candidate v3.

No rigorous integral is executed by this test.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

import rehearsal_driver_v9_candidate_v3 as d


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REPORT = HERE / "rehearsal_driver_v3_binding_audit.json"

DESIGN_SHA = "1" * 64
DEPENDENCY_SHA = "2" * 64
PLAN_SHA = "3" * 64
QUALIFICATION_SHA = "4" * 64
VALIDATION_SHA = "5" * 64
PERFORMANCE_SHA = "6" * 64


def rat(p: str, q: str) -> dict[str, str]:
    return {"p": p, "q": q}


def interval(lo_p: str, lo_q: str, hi_p: str, hi_q: str) -> dict:
    return {"lo": rat(lo_p, lo_q), "hi": rat(hi_p, hi_q)}


def driver_sha() -> str:
    return hashlib.sha256((HERE / "rehearsal_driver_v9_candidate_v3.py").read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    return {
        "kernel": d.KERNEL_SHA256,
        "adapter": d.ADAPTER_SHA256,
        "runner": d.RUNNER_SHA256,
        "checker": d.CHECKER_SHA256,
        "checkpoint": d.CHECKPOINT_SHA256,
        "bridge": d.BRIDGE_SHA256,
        "aggregate_verifier": d.AGGREGATE_VERIFIER_SHA256,
        "driver": driver_sha(),
    }


def valid_config_obj() -> dict:
    return {
        "aggregate_plan_sha256": PLAN_SHA,
        "checkpoint": {
            "attempts": 32,
            "max_payload_bytes": 33554432,
            "seconds": 120,
        },
        "dependency_snapshot_sha256": DEPENDENCY_SHA,
        "design_sha256": DESIGN_SHA,
        "dps_control": 50,
        "dps_verify": 70,
        "integration": {"depth": 12, "limit": 200000, "tol": "1e-8"},
        "lambda_box": interval("123731943", "26214400", "118", "25"),
        "lambda_floor": rat("1", "65536"),
        "max_activations": 65536,
        "r_floor": rat("1", "65536"),
        "required_freeze_receipt_schema": d.FREEZE_SCHEMA,
        "root_r": interval("1", "64", "11", "256"),
        "schema": d.CONFIG_SCHEMA,
        "shard_id": "S00000000",
        "shard_index": 0,
        "source_sha256": source_hashes(),
    }


def write_canonical(path: Path, obj: dict) -> str:
    data = d.canonical_json_bytes(obj)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def valid_freeze_obj(config: d.ShardConfig) -> dict:
    return {
        "aggregate_plan_sha256": config.aggregate_plan_sha256,
        "config_sha256": config.config_sha256,
        "dependency_snapshot_sha256": config.dependency_snapshot_sha256,
        "design_sha256": config.design_sha256,
        "freeze_verdict": "V9_FROZEN_APPROVED",
        "nonclaims": ["receipt fixture only; no mathematical run is executed"],
        "performance_gate_report_sha256": PERFORMANCE_SHA,
        "qualification_manifest_sha256": QUALIFICATION_SHA,
        "schema": d.FREEZE_SCHEMA,
        "source_sha256": config.source_sha256,
        "validation_report_sha256": VALIDATION_SHA,
    }


class DriverV3Controls(unittest.TestCase):
    def test_valid_config_parses_and_hashes_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "config.json"
            expected_sha = write_canonical(path, valid_config_obj())
            config = d.parse_config(path)
            self.assertEqual(config.config_sha256, expected_sha)
            self.assertEqual(config.lambda_box[1] - config.lambda_box[0], d.Fraction(1, 1 << 20))
            self.assertEqual(config.root_r, (d.Fraction(1, 64), d.Fraction(11, 256)))
            self.assertEqual(config.source_sha256["driver"], driver_sha())

    def test_all_bound_modules_load_exactly(self) -> None:
        modules, bindings = d._bind_all(ROOT)
        self.assertEqual(modules["adapter"].ADAPTER_ID, "ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V2")
        self.assertEqual(modules["runner"].RUNNER_ID, "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V2")
        self.assertEqual(modules["checker"].CHECKER_ID, "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V2")
        self.assertEqual(modules["checkpoint"].CHECKPOINT_LINE_SCHEMA, "ITEM3_SWEEP_V9_PROGRESS_LINE_V1")
        self.assertEqual(modules["bridge"].BRIDGE_ID, "ITEM3_SWEEP_V9_CHECKPOINT_BRIDGE_CANDIDATE_V2")
        for binding in bindings.values():
            self.assertEqual(binding.pre_import_sha256, binding.sha256)
            self.assertEqual(binding.post_import_sha256, binding.sha256)
            self.assertEqual(binding.resolved_path, binding.module_origin)

    def test_nonreduced_rational_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            obj = valid_config_obj()
            obj["root_r"]["lo"] = rat("2", "128")
            path = Path(td) / "config.json"
            write_canonical(path, obj)
            with self.assertRaises(d.DriverContractError):
                d.parse_config(path)

    def test_floor_dps_and_source_hash_mutations_rejected(self) -> None:
        mutations = []
        obj = valid_config_obj(); obj["r_floor"] = rat("1", "32768"); mutations.append(obj)
        obj = valid_config_obj(); obj["dps_verify"] = 69; mutations.append(obj)
        obj = valid_config_obj(); obj["source_sha256"]["runner"] = "0" * 64; mutations.append(obj)
        for index, obj in enumerate(mutations):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as td:
                path = Path(td) / "config.json"
                write_canonical(path, obj)
                with self.assertRaises(d.DriverContractError):
                    d.parse_config(path)

    def test_binary_float_in_config_rejected_before_write_helper(self) -> None:
        obj = valid_config_obj()
        obj["checkpoint"]["seconds"] = 120.0
        with self.assertRaises(d.DriverContractError):
            d.canonical_json_bytes(obj)

    def test_qualification_with_freeze_receipt_argument_rejected_before_math(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config_path = root / "config.json"
            write_canonical(config_path, valid_config_obj())
            receipt_path = root / "receipt.json"
            receipt_path.write_text("{}\n", encoding="utf-8")
            with self.assertRaises(d.DriverContractError):
                d.execute_shard(
                    checkout_root=ROOT,
                    config_path=config_path,
                    output_dir=root / "out",
                    qualification_mode=True,
                    freeze_receipt_path=receipt_path,
                )

    def test_production_without_freeze_receipt_rejected_before_math(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config_path = root / "config.json"
            write_canonical(config_path, valid_config_obj())
            with self.assertRaises(d.DriverContractError):
                d.execute_shard(
                    checkout_root=ROOT,
                    config_path=config_path,
                    output_dir=root / "out",
                    qualification_mode=False,
                    freeze_receipt_path=None,
                )

    def test_matching_freeze_receipt_parses(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config_path = root / "config.json"
            write_canonical(config_path, valid_config_obj())
            config = d.parse_config(config_path)
            receipt_path = root / "freeze.json"
            receipt_sha = write_canonical(receipt_path, valid_freeze_obj(config))
            receipt, observed_sha = d.parse_freeze_receipt(receipt_path, config)
            self.assertEqual(observed_sha, receipt_sha)
            self.assertEqual(receipt["freeze_verdict"], "V9_FROZEN_APPROVED")

    def test_freeze_receipt_identity_mutations_rejected(self) -> None:
        fields = ["config_sha256", "design_sha256", "aggregate_plan_sha256"]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config_path = root / "config.json"
            write_canonical(config_path, valid_config_obj())
            config = d.parse_config(config_path)
            for field in fields:
                with self.subTest(field=field):
                    obj = valid_freeze_obj(config)
                    obj[field] = "f" * 64
                    receipt_path = root / f"freeze-{field}.json"
                    write_canonical(receipt_path, obj)
                    with self.assertRaises(d.DriverContractError):
                        d.parse_freeze_receipt(receipt_path, config)
            obj = valid_freeze_obj(config)
            obj["source_sha256"] = deepcopy(config.source_sha256)
            obj["source_sha256"]["checker"] = "e" * 64
            receipt_path = root / "freeze-source.json"
            write_canonical(receipt_path, obj)
            with self.assertRaises(d.DriverContractError):
                d.parse_freeze_receipt(receipt_path, config)
            obj = valid_freeze_obj(config)
            obj["freeze_verdict"] = "NOT_APPROVED"
            receipt_path = root / "freeze-verdict.json"
            write_canonical(receipt_path, obj)
            with self.assertRaises(d.DriverContractError):
                d.parse_freeze_receipt(receipt_path, config)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DriverV3Controls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "ITEM3_SWEEP_V9_DRIVER_V3_BINDING_AUDIT_V1",
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failure_details": [text for _case, text in result.failures],
        "error_details": [text for _case, text in result.errors],
        "driver_source_sha256": driver_sha(),
        "kernel_sha256": d.KERNEL_SHA256,
        "adapter_sha256": d.ADAPTER_SHA256,
        "runner_sha256": d.RUNNER_SHA256,
        "checker_sha256": d.CHECKER_SHA256,
        "checkpoint_sha256": d.CHECKPOINT_SHA256,
        "bridge_sha256": d.BRIDGE_SHA256,
    }
    REPORT.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
