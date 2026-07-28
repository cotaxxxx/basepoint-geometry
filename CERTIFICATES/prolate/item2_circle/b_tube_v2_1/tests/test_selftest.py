from __future__ import annotations

from dataclasses import replace
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mock_kernel
from b_tube_checker import CheckError, check_bundle
from b_tube_selftest_runner import build_bundle
from checker_common import SELFTEST_MOCK_KERNEL_FILE_SHA256
from numeric_schema import (
    Dyadic,
    DyadicInterval,
    Rational,
    arb_ball_to_exact_interval,
    canonical_json_bytes,
    canonical_source_forbidden,
    parse_canonical_json_bytes,
    sha256_hex,
)
from run_controls import run_all_controls


class FakeExact:
    def __init__(self, m, e):
        self.data = (m, e)

    def man_exp(self):
        return self.data


class FakeBall:
    def mid(self):
        return FakeExact(13, -7)

    def rad(self):
        return FakeExact(1, -3)


class NumericSchemaTests(unittest.TestCase):
    def test_dyadic_canonicalization(self):
        self.assertEqual(Dyadic.canonical(40, 9), Dyadic(5, 6))
        self.assertEqual(Dyadic.from_json({"m": "5", "e": 6}), Dyadic(5, 6))
        with self.assertRaises(ValueError):
            Dyadic.from_json({"m": "10", "e": 7})

    def test_exact_integer_comparison(self):
        self.assertLess(Dyadic(1, 5), Dyadic(3, 6))
        outer = DyadicInterval(Dyadic(-1, 4), Dyadic(1, 4))
        inner = DyadicInterval(Dyadic(-1, 5), Dyadic(1, 5))
        self.assertTrue(outer.strictly_contains(inner))

    def test_canonical_bytes(self):
        obj = {"b": 2, "a": {"m": "1", "e": 2}}
        raw = canonical_json_bytes(obj)
        self.assertEqual(raw, b'{"a":{"e":2,"m":"1"},"b":2}')
        self.assertEqual(parse_canonical_json_bytes(raw), obj)
        with self.assertRaises(ValueError):
            parse_canonical_json_bytes(b'{"b":2, "a":1}')

    def test_arf_mag_exact_adapter(self):
        self.assertEqual(
            arb_ball_to_exact_interval(FakeBall()),
            DyadicInterval(Dyadic(-3, 7), Dyadic(29, 7)),
        )

    def test_rational_reduced(self):
        self.assertEqual(Rational.from_json({"p": "118", "q": "25"}), Rational(118, 25))
        with self.assertRaises(ValueError):
            Rational.from_json({"p": "236", "q": "50"})

    def test_module_source_self_scan_and_kernel_pin(self):
        offenders = {}
        for path in sorted(ROOT.glob("*.py")):
            hits = canonical_source_forbidden(path.read_text(encoding="utf-8"))
            if hits:
                offenders[path.name] = hits
        self.assertEqual(offenders, {})
        kernel_path = pathlib.Path(mock_kernel.__file__)
        self.assertEqual(sha256_hex(kernel_path.read_bytes()), SELFTEST_MOCK_KERNEL_FILE_SHA256)


class CheckerTests(unittest.TestCase):
    def test_full_and_core_verdicts(self):
        self.assertEqual(check_bundle(build_bundle(full=True)).verdict, "CERTIFIED_B_TUBE_FULL")
        self.assertEqual(check_bundle(build_bundle(full=False)).verdict, "CERTIFIED_CORE_INTERVAL")

    def test_real_analytic_present_and_false(self):
        bundle = build_bundle()
        summary = parse_canonical_json_bytes(bundle.summary_bytes)
        summary["machine_conclusion"].pop("real_analytic")
        with self.assertRaises(CheckError):
            check_bundle(replace(bundle, summary_bytes=canonical_json_bytes(summary)))

        summary = parse_canonical_json_bytes(bundle.summary_bytes)
        summary["machine_conclusion"]["real_analytic"] = True
        with self.assertRaises(CheckError):
            check_bundle(replace(bundle, summary_bytes=canonical_json_bytes(summary)))

    def test_tight_cell(self):
        self.assertEqual(check_bundle(build_bundle(tight=True)).cells, 2)

    def test_all_controls(self):
        failures = {name: result for name, result in run_all_controls().items() if not result["ok"]}
        self.assertEqual(failures, {})


if __name__ == "__main__":
    unittest.main()
