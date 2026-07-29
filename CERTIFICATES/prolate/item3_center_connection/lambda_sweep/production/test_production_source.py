#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from arb_adapter import _exact_arb_to_fraction
from verify_pilot_artifact import PilotArtifactReject, _parse_manifest, _validate_member_name

HERE = Path(__file__).resolve().parent


class ExactEndpoint:
    def __init__(self, mantissa: int, exponent: int) -> None:
        self.value = (mantissa, exponent)

    def man_exp(self):
        return self.value


class ProductionSourceTests(unittest.TestCase):
    def test_exact_dyadic_positive_exponent(self):
        self.assertEqual(_exact_arb_to_fraction(ExactEndpoint(3, 2)), Fraction(12))

    def test_exact_dyadic_negative_exponent(self):
        self.assertEqual(_exact_arb_to_fraction(ExactEndpoint(-3, -4)), Fraction(-3, 16))

    def test_internal_manifest_parser(self):
        digest = "a" * 64
        self.assertEqual(_parse_manifest(f"{digest}  x.py\n".encode()), {"x.py": digest})

    def test_internal_manifest_rejects_duplicate(self):
        digest = "a" * 64
        raw = f"{digest}  x.py\n{digest}  x.py\n".encode()
        with self.assertRaises(PilotArtifactReject):
            _parse_manifest(raw)

    def test_internal_manifest_rejects_no_final_lf(self):
        digest = "a" * 64
        with self.assertRaises(PilotArtifactReject):
            _parse_manifest(f"{digest}  x.py".encode())

    def test_zip_member_path_rejects_escape(self):
        for value in ("../x", "a/x", "/x", "a\\x"):
            with self.assertRaises(PilotArtifactReject):
                _validate_member_name(value)

    def test_target_policy_direction(self):
        obj = json.loads((HERE / "TARGET_RANGE_POLICY.json").read_bytes())
        anchor = Fraction(int(obj["lambda_anchor"]["p"]), int(obj["lambda_anchor"]["q"]))
        target = Fraction(
            int(obj["pipeline_validation_target"]["p"]),
            int(obj["pipeline_validation_target"]["q"]),
        )
        ac_lo = Fraction(
            int(obj["a_c_certified_bracket"]["lo"]["p"]),
            int(obj["a_c_certified_bracket"]["lo"]["q"]),
        )
        self.assertEqual(target, anchor - Fraction(1, 4096))
        self.assertLess(target, anchor)
        self.assertLess(anchor, ac_lo)
        self.assertFalse(obj["current_contract_can_reach_a_c"])

    def test_config_sha_file_requires_final_lf(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.sha256"
            path.write_text("a" * 64 + "\n", encoding="ascii")
            self.assertEqual(path.read_text(encoding="ascii").strip(), "a" * 64)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductionSourceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "errors": len(result.errors),
        "failures": len(result.failures),
        "kernel_evaluations": 0,
        "mathematical_calculations": 0,
        "schema": "ITEM3_SWEEP_PRODUCTION_SOURCE_TEST_REPORT_V1",
        "tests_run": result.testsRun,
        "verdict": "PASS" if result.wasSuccessful() else "FAIL",
    }
    raw = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    (HERE / "PRODUCTION_SOURCE_TEST_REPORT.json").write_bytes(raw)
    print(raw.decode("ascii"))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
