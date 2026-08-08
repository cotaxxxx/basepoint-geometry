#!/usr/bin/env python3
"""Short source-binding controls for rehearsal_driver_v9_candidate.

No rigorous integral is executed by this test.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

import rehearsal_driver_v9_candidate as d

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REPORT = HERE / "rehearsal_driver_binding_audit.json"


class DriverBindingControls(unittest.TestCase):
    def test_exact_bound_modules_load(self) -> None:
        adapter, aid = d.load_bound_module(
            checkout_root=ROOT,
            relative_path=d.ADAPTER_PATH,
            expected_sha256=d.ADAPTER_SHA256,
            module_name="binding_test_adapter",
        )
        runner, rid = d.load_bound_module(
            checkout_root=ROOT,
            relative_path=d.RUNNER_PATH,
            expected_sha256=d.RUNNER_SHA256,
            module_name="binding_test_runner",
        )
        checker, cid = d.load_bound_module(
            checkout_root=ROOT,
            relative_path=d.CHECKER_PATH,
            expected_sha256=d.CHECKER_SHA256,
            module_name="binding_test_checker",
        )
        self.assertEqual(adapter.ADAPTER_ID, "ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V2")
        self.assertEqual(runner.RUNNER_ID, "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V1")
        self.assertEqual(checker.CHECKER_ID, "ITEM3_SWEEP_V9_REHEARSAL_CHECKER_CANDIDATE_V1")
        for identity in (aid, rid, cid):
            self.assertEqual(identity.pre_import_sha256, identity.sha256)
            self.assertEqual(identity.post_import_sha256, identity.sha256)
            self.assertEqual(identity.resolved_path, identity.module_origin)

    def test_wrong_hash_rejected(self) -> None:
        with self.assertRaises(d.DriverContractError):
            d.load_bound_module(
                checkout_root=ROOT,
                relative_path=d.RUNNER_PATH,
                expected_sha256="0" * 64,
                module_name="binding_wrong_hash",
            )

    def test_path_escape_rejected(self) -> None:
        with self.assertRaises(Exception):
            d.resolve_contained(HERE, "../../../../../../../../etc/passwd")

    def test_canonical_fraction_encoding(self) -> None:
        self.assertEqual(d.fraction_object(Fraction(-6, 8)), {"p": "-3", "q": "4"})
        payload = d.canonical_json_bytes({"x": Fraction(3, 7)})
        self.assertEqual(payload, b'{"x":{"p":"3","q":"7"}}\n')

    def test_exact_rehearsal_constants(self) -> None:
        self.assertEqual(d.ROOT_R, (Fraction(1, 64), Fraction(11, 256)))
        self.assertEqual(
            d.ROOT_LAMBDA,
            (Fraction(123731943, 26214400), Fraction(118, 25)),
        )
        self.assertEqual(d.ROOT_LAMBDA[1] - d.ROOT_LAMBDA[0], Fraction(1, 1 << 20))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DriverBindingControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "ITEM3_SWEEP_V9_DRIVER_BINDING_AUDIT_V1",
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "failure_details": [text for _case, text in result.failures],
        "error_details": [text for _case, text in result.errors],
        "driver_source_sha256": hashlib.sha256(
            (HERE / "rehearsal_driver_v9_candidate.py").read_bytes()
        ).hexdigest(),
        "adapter_sha256": d.ADAPTER_SHA256,
        "runner_sha256": d.RUNNER_SHA256,
        "checker_sha256": d.CHECKER_SHA256,
        "kernel_sha256": d.KERNEL_SHA256,
    }
    REPORT.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
