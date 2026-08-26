from __future__ import annotations
from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
import calibration_security
import a0b_start_anchor_verify as a0bv
from numeric_schema import D_ZERO, Dyadic, DyadicInterval, Rational


class A0BStartAnchorTests(unittest.TestCase):
    def test_independent_verifier_imports_result_namespace_guard(self):
        self.assertIs(
            a0bv.assert_result_namespace,
            calibration_security.assert_result_namespace,
        )

    def test_a0_delta_consistency_invariant(self):
        _, cert = calibration._load_a0_start_interval()
        delta = Rational.from_json(cert["delta_start_exact"]).as_fraction()
        self.assertGreater(delta, Fraction(1, 8192))
        self.assertLessEqual(delta, Fraction(1, 2048))

    def test_independent_krawczyk_allows_noninverse_exact_preconditioner(self):
        domain = DyadicInterval(Dyadic(1, 2), Dyadic(3, 2))
        entry = {
            "preconditioner": Dyadic(-3, 3).to_json(),
            "residual": DyadicInterval.point(D_ZERO).to_json(),
            "slope": DyadicInterval.point(Dyadic(-2, 0)).to_json(),
        }
        image, left, right, reason, passed = a0bv._krawczyk(domain, entry)
        self.assertTrue(passed)
        self.assertIsNone(reason)
        self.assertTrue(domain.strictly_contains(image))
        self.assertGreater(left, D_ZERO)
        self.assertGreater(right, D_ZERO)

    def test_candidate_start_gate_is_candidate_local(self):
        self.assertTrue(calibration._effective_candidate_pass(True, True))
        self.assertFalse(calibration._effective_candidate_pass(True, False))
        self.assertFalse(calibration._effective_candidate_pass(False, True))

    def test_a0b_schema_and_gate_are_normative(self):
        self.assertEqual(a0bv.A0B_SCHEMA, "btube-a0b-start-anchors-v1")
        self.assertEqual(a0bv.A0B_PATH_NAME, "A0B_START_ANCHORS.json")
        self.assertEqual(calibration.ANCHOR_MODE, "BLOCAL_A0_FORWARD_V1")


if __name__ == "__main__":
    unittest.main()
