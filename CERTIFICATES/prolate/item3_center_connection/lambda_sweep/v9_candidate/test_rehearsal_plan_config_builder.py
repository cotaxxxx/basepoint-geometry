#!/usr/bin/env python3
"""Deterministic pipeline controls: dependency snapshot -> plan -> config."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import aggregate_verifier_v9_candidate_v2 as aggregate
import build_dependency_snapshot_v9 as deps
import build_rehearsal_plan_config_v9 as pc
import rehearsal_driver_v9_candidate_v3 as driver


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


class RehearsalPlanConfigControls(unittest.TestCase):
    def build_once(self):
        dep_tmp = tempfile.TemporaryDirectory(dir=HERE)
        out_tmp = tempfile.TemporaryDirectory(dir=HERE)
        dep_dir = Path(dep_tmp.name) / "dependency"
        out_dir = Path(out_tmp.name) / "planconfig"
        dep_report = deps.build(ROOT, dep_dir)
        snapshot = dep_dir / "dependency_snapshot_v9_candidate.json"
        pc_report = pc.build(
            repo_root=ROOT,
            dependency_snapshot_path=snapshot,
            output_dir=out_dir,
        )
        return dep_tmp, out_tmp, dep_report, pc_report, dep_dir, out_dir

    def test_generated_plan_and_config_are_accepted_by_both_parsers(self) -> None:
        dep_tmp, out_tmp, _dr, report, _dep_dir, out_dir = self.build_once()
        try:
            plan_path = out_dir / "rehearsal_plan_v2.json"
            config_path = out_dir / "rehearsal_shard_config_v1.json"
            parsed_plan = aggregate.parse_plan(plan_path)
            config = driver.parse_config(config_path)
            config_obj, observed_config_sha = aggregate.parse_config_for_plan(
                config_path, parsed_plan, parsed_plan.ordered_shards[0]
            )
            self.assertEqual(observed_config_sha, config.config_sha256)
            self.assertEqual(observed_config_sha, report["config_sha256"])
            self.assertEqual(parsed_plan.plan_sha256, report["plan_sha256"])
            self.assertEqual(config.aggregate_plan_sha256, parsed_plan.plan_sha256)
            self.assertEqual(config_obj["source_sha256"], parsed_plan.source_sha256)
        finally:
            dep_tmp.cleanup(); out_tmp.cleanup()

    def test_plan_has_no_config_hash_cycle(self) -> None:
        dep_tmp, out_tmp, _dr, report, _dep_dir, out_dir = self.build_once()
        try:
            plan = json.loads((out_dir / "rehearsal_plan_v2.json").read_text(encoding="utf-8"))
            self.assertNotIn("config_sha256", plan)
            self.assertNotIn("config_sha256", plan["ordered_shards"][0])
            config = json.loads((out_dir / "rehearsal_shard_config_v1.json").read_text(encoding="utf-8"))
            self.assertEqual(config["aggregate_plan_sha256"], report["plan_sha256"])
        finally:
            dep_tmp.cleanup(); out_tmp.cleanup()

    def test_exact_rehearsal_geometry_and_policy(self) -> None:
        dep_tmp, out_tmp, _dr, _report, _dep_dir, out_dir = self.build_once()
        try:
            config = driver.parse_config(out_dir / "rehearsal_shard_config_v1.json")
            self.assertEqual(config.lambda_box[1] - config.lambda_box[0], driver.Fraction(1, 1 << 20))
            self.assertEqual(config.root_r, (driver.Fraction(1, 64), driver.Fraction(11, 256)))
            self.assertEqual(config.r_floor, driver.Fraction(1, 1 << 16))
            self.assertEqual(config.lambda_floor, driver.Fraction(1, 1 << 16))
            self.assertEqual(config.dps_control, 50)
            self.assertEqual(config.dps_verify, 70)
        finally:
            dep_tmp.cleanup(); out_tmp.cleanup()

    def test_source_map_binds_driver_and_aggregate_verifier_current_bytes(self) -> None:
        dep_tmp, out_tmp, _dr, _report, _dep_dir, out_dir = self.build_once()
        try:
            plan = json.loads((out_dir / "rehearsal_plan_v2.json").read_text(encoding="utf-8"))
            self.assertEqual(set(plan["source_sha256"]), set(aggregate.SOURCE_KEYS))
            self.assertEqual(
                plan["source_sha256"]["driver"],
                hashlib.sha256((HERE / "rehearsal_driver_v9_candidate_v3.py").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                plan["source_sha256"]["aggregate_verifier"],
                hashlib.sha256((HERE / "aggregate_verifier_v9_candidate_v2.py").read_bytes()).hexdigest(),
            )
        finally:
            dep_tmp.cleanup(); out_tmp.cleanup()

    def test_two_full_builds_are_byte_identical(self) -> None:
        one = self.build_once(); two = self.build_once()
        try:
            one_out, two_out = one[5], two[5]
            names = [
                "rehearsal_plan_v2.json",
                "rehearsal_plan_v2.json.sha256",
                "rehearsal_shard_config_v1.json",
                "rehearsal_shard_config_v1.json.sha256",
                "rehearsal_plan_config_build_report.json",
            ]
            for name in names:
                self.assertEqual((one_out / name).read_bytes(), (two_out / name).read_bytes(), name)
            self.assertEqual(one[3], two[3])
        finally:
            one[0].cleanup(); one[1].cleanup(); two[0].cleanup(); two[1].cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
