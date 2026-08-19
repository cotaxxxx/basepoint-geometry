from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
import routed_record_verifier
from numeric_schema import Dyadic, DyadicInterval
from routed_evaluator import routed_bundle_pins
from routed_record_verifier import (
    verifier_bundle_pins,
    verifier_selector_for_r_interval,
    verifier_straddle_children,
)


class RoutedVerifierIndependenceTests(unittest.TestCase):
    def test_verifier_reconstructs_producer_pins(self):
        self.assertEqual(verifier_bundle_pins(), routed_bundle_pins())

    def test_structural_verifier_does_not_import_producer_router(self):
        source = Path(routed_record_verifier.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from routed_evaluator import", source)
        self.assertNotIn("import routed_evaluator", source)

    def test_verifier_selector_reconstructs_tie_and_straddle(self):
        r0 = calibration.ROUTED_SELECTOR
        self.assertEqual(
            verifier_selector_for_r_interval(DyadicInterval.point(r0)),
            calibration.ROUTED_INTERIOR_ROUTE_ID,
        )
        boundary = DyadicInterval.point(Dyadic(7, 3))
        self.assertEqual(
            verifier_selector_for_r_interval(boundary),
            calibration.ROUTED_BOUNDARY_ROUTE_ID,
        )
        straddle = DyadicInterval(Dyadic(1, 1), Dyadic(7, 3))
        self.assertEqual(
            verifier_selector_for_r_interval(straddle),
            calibration.ROUTED_STRADDLE_ROUTE_ID,
        )
        left, right = verifier_straddle_children(straddle)
        self.assertEqual(left, DyadicInterval(Dyadic(1, 1), Dyadic(3, 2)))
        self.assertEqual(right, DyadicInterval(Dyadic(3, 2), Dyadic(7, 3)))


if __name__ == "__main__":
    unittest.main()
