from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import D_ONE, Dyadic, DyadicInterval, canonical_json_bytes


class AdaptiveA1Tests(unittest.TestCase):
    def test_a0_operational_bracket_is_loaded_exactly(self):
        interval, cert = calibration._load_a0_start_interval()
        self.assertEqual(
            interval,
            DyadicInterval(Dyadic(2047, 11), Dyadic(8191, 13)),
        )
        self.assertEqual(cert["status"], "A0_CERTIFIED")

    def test_first_anchor_radius_is_boundary_aware_and_inside_a0(self):
        interval, _ = calibration._load_a0_start_interval()
        anchor = interval.midpoint()
        hull = DyadicInterval.point(anchor)
        rho, d_left, d_right, domain = calibration._adaptive_radius(
            hull, Dyadic(1, 7), Dyadic(1, 1)
        )
        self.assertEqual(anchor, Dyadic(16379, 14))
        self.assertEqual(d_right, Dyadic(5, 14))
        self.assertEqual(rho, Dyadic(5, 15))
        self.assertGreater(d_left, D_ONE - Dyadic(1, 9))
        self.assertTrue(interval.contains(calibration.shifted(
            DyadicInterval(-rho, rho), anchor
        )))
        self.assertGreater(domain.lo, calibration.D_ZERO)
        self.assertLess(domain.hi, D_ONE)

    def test_heterogeneous_join_has_positive_width(self):
        center = Dyadic(3, 2)
        left_rho = Dyadic(1, 5)
        right_rho = Dyadic(1, 6)
        intersection = calibration.exact_join_intersection(
            center, DyadicInterval(-left_rho, left_rho),
            center, DyadicInterval(-right_rho, right_rho),
        )
        self.assertEqual(intersection, DyadicInterval(
            center - right_rho, center + right_rho
        ))
        self.assertTrue(intersection.positive_width())

    def test_krawczyk_accepts_general_dyadic_preconditioner(self):
        domain = DyadicInterval(Dyadic(1, 3), Dyadic(3, 3))
        image = calibration.krawczyk_image(
            m=Dyadic(1, 2),
            residual=DyadicInterval.point(Dyadic(1, 6)),
            slope=DyadicInterval(Dyadic(-9, 3), Dyadic(-7, 3)),
            preconditioner=Dyadic(-3, 2),
            domain=domain,
        )
        self.assertIsInstance(image, DyadicInterval)

    def test_adaptive_sigma_tamper_rejected(self):
        config = calibration.load_config()[0]
        config["adaptive_safety_factor"] = Dyadic(3, 2).to_json()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_bytes(canonical_json_bytes(config))
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(path)

    def test_forward_anchor_constants_are_normative(self):
        config = calibration.load_config()[0]
        self.assertEqual(
            Dyadic.from_json(config["adaptive_safety_factor"]),
            calibration.ADAPTIVE_SIGMA,
        )
        self.assertEqual(calibration.ANCHOR_MODE, "BLOCAL_A0_FORWARD_V1")
        self.assertEqual(
            calibration.ADAPTIVE_RADIUS_RULE,
            "exact_dyadic_min_boundary_margin_v1",
        )


if __name__ == "__main__":
    unittest.main()
