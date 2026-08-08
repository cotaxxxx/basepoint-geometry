#!/usr/bin/env python3
"""Short source-binding controls for rehearsal_driver_v9_candidate_v2.

No rigorous integral is executed.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import rehearsal_driver_v9_candidate_v2 as d

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REPORT = HERE / "rehearsal_driver_v2_binding_audit.json"


class DriverV2BindingControls(unittest.TestCase):
    def test_all_bound_modules_load_exactly(self) -> None:
        modules, bindings = d._bind_all(ROOT)
        self.assertEqual(modules["adapter"].ADAPTER_ID, "ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V2")
        self.assertEqual(modules["runner"].RUNNER_ID, "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V2")
        self.assertEqual(modules["checker"].CHECKER_ID, "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V2")
        self.assertEqual(modules["bridge"].BRIDGE_ID, "ITEM3_SWEEP_V9_CHECKPOINT_BRIDGE_CANDIDATE_V1")
        self.assertEqual(modules["checkpoint"].CHECKPOINT_LINE_SCHEMA, "ITEM3_SWEEP_V9_PROGRESS_LINE_V1")
        for binding in bindings.values():
            self.assertEqual(binding.pre_import_sha256, binding.sha256)
            self.assertEqual(binding.post_import_sha256, binding.sha256)
            self.assertEqual(binding.resolved_path, binding.module_origin)

    def test_canonical_fraction_helper(self) -> None:
        self.assertEqual(
            d.canonical_json_bytes({"x": Fraction(3, 7)}),
            b'{"x":{"p":"3","q":"7"}}\n',
        )

    def test_exact_rehearsal_range(self) -> None:
        self.assertEqual(d.ROOT_R, (Fraction(1, 64), Fraction(11, 256)))
        self.assertEqual(d.ROOT_LAMBDA[1] - d.ROOT_LAMBDA[0], Fraction(1, 1 << 20))

    def test_wrong_bound_hash_rejected(self) -> None:
        with self.assertRaises(d.DriverContractError):
            d.load_bound_module(
                checkout_root=ROOT,
                relative_path=d.CHECKPOINT_PATH,
                expected_sha256="0" * 64,
                module_name="driver_v2_wrong_hash",
            )

    def test_output_dir_must_be_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fresh = root / "fresh"
            d._require_fresh_output_dir(fresh)
            self.assertTrue(fresh.is_dir())
            (fresh / "stale.txt").write_text("stale", encoding="utf-8")
            with self.assertRaises(d.DriverContractError):
                d._require_fresh_output_dir(fresh)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DriverV2BindingControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "ITEM3_SWEEP_V9_DRIVER_V2_BINDING_AUDIT_V1",
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failure_details": [text for _case, text in result.failures],
        "error_details": [text for _case, text in result.errors],
        "driver_source_sha256": hashlib.sha256(
            (HERE / "rehearsal_driver_v9_candidate_v2.py").read_bytes()
        ).hexdigest(),
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
