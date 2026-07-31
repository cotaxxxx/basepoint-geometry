#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from fractions import Fraction

from mean_value_core_v9 import (
    ExactInterval,
    canonical_midpoint,
    mean_value_enclosure,
    midpoint_children,
    select_split_axis,
)


class MeanValueCoreTests(unittest.TestCase):
    def test_exact_centers(self) -> None:
        self.assertEqual(
            canonical_midpoint((Fraction(1, 64), Fraction(11, 256))),
            Fraction(15, 512),
        )
        self.assertEqual(
            canonical_midpoint((Fraction(123, 25), Fraction(124, 25))),
            Fraction(247, 50),
        )

    def test_mean_value_negative(self) -> None:
        evidence = mean_value_enclosure(
            r_cell=(Fraction(1, 64), Fraction(3, 64)),
            lambda_box=(Fraction(4719, 1000), Fraction(4721, 1000)),
            g_r_center=ExactInterval(Fraction(-21, 1000), Fraction(-20, 1000)),
            g_rr_box=ExactInterval(Fraction(-1, 2), Fraction(1, 2)),
            g_rlambda_box=ExactInterval(Fraction(-1), Fraction(1)),
        )
        self.assertEqual(evidence.r0, Fraction(1, 32))
        self.assertEqual(evidence.lambda0, Fraction(118, 25))
        self.assertTrue(evidence.strict_negative)

    def test_exact_score_tie_selects_r(self) -> None:
        decision = select_split_axis(
            r_cell=(Fraction(0), Fraction(2)),
            lambda_box=(Fraction(0), Fraction(4)),
            g_rr_box=ExactInterval(Fraction(-2), Fraction(2)),
            g_rlambda_box=ExactInterval(Fraction(-1), Fraction(1)),
            r_splittable=True,
            lambda_splittable=True,
        )
        self.assertEqual(decision.r_score.value, decision.lambda_score.value)
        self.assertEqual(decision.selected_axis, "r")
        self.assertEqual(decision.reason, "EXACT_SCORE_TIE_TO_R")

    def test_nonfinite_outranks_finite(self) -> None:
        decision = select_split_axis(
            r_cell=(Fraction(0), Fraction(2)),
            lambda_box=(Fraction(0), Fraction(2)),
            g_rr_box=ExactInterval.nonfinite(),
            g_rlambda_box=ExactInterval(Fraction(-1000), Fraction(1000)),
            r_splittable=True,
            lambda_splittable=True,
        )
        self.assertEqual(decision.selected_axis, "r")
        self.assertEqual(decision.reason, "NONFINITE_R_OUTRANKS_FINITE")

    def test_double_nonfinite_tie_selects_r(self) -> None:
        decision = select_split_axis(
            r_cell=(Fraction(0), Fraction(2)),
            lambda_box=(Fraction(0), Fraction(2)),
            g_rr_box=ExactInterval.nonfinite(),
            g_rlambda_box=ExactInterval.nonfinite(),
            r_splittable=True,
            lambda_splittable=True,
        )
        self.assertEqual(decision.selected_axis, "r")
        self.assertEqual(decision.reason, "DOUBLE_NONFINITE_TIE_TO_R")

    def test_unsplittable_axis_is_not_candidate(self) -> None:
        decision = select_split_axis(
            r_cell=(Fraction(0), Fraction(2)),
            lambda_box=(Fraction(0), Fraction(2)),
            g_rr_box=ExactInterval.nonfinite(),
            g_rlambda_box=ExactInterval(Fraction(-1), Fraction(1)),
            r_splittable=False,
            lambda_splittable=True,
        )
        self.assertEqual(decision.selected_axis, "lambda")
        self.assertEqual(decision.reason, "ONLY_LAMBDA_SPLITTABLE")

    def test_midpoint_children(self) -> None:
        lower, upper = midpoint_children((Fraction(1, 8), Fraction(3, 8)))
        self.assertEqual(lower, (Fraction(1, 8), Fraction(1, 4)))
        self.assertEqual(upper, (Fraction(1, 4), Fraction(3, 8)))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MeanValueCoreTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({
        "schema": "ITEM3_SWEEP_V9_MEAN_VALUE_CORE_TEST_V1",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "verdict": "PASS" if result.wasSuccessful() else "FAIL",
    }, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result.wasSuccessful() else 1)
