from __future__ import annotations

from fractions import Fraction
import copy
import unittest

from calibration_context import (
    CalibrationError,
    Dyadic,
    DyadicInterval,
    Rational,
    ROUTED_BOUNDARY_ROUTE_ID,
)
import exact_lambda_prepartition as producer
import exact_lambda_prepartition_verifier as verifier


class ExactLambdaPrepartitionTests(unittest.TestCase):
    def setUp(self):
        self.domain = DyadicInterval(
            Dyadic(74281023883021057323306507, 86),
            Dyadic(77359446546029624093969931, 86),
        )
        self.lam_lo = Fraction(3307749, 1600000)
        self.lam_hi = Fraction(3707749, 1600000)

    def test_frozen_30_leaf_partition_matches_independent_reconstruction(self):
        produced = producer.fatal_slope_prepartition_leaves(
            self.domain, self.lam_lo, self.lam_hi
        )
        checked = verifier.expected_prepartition_leaves()
        self.assertEqual(len(produced), 30)
        self.assertEqual(len(checked), 30)
        for left, right in zip(produced, checked):
            self.assertEqual(left["leaf_id"], right["leaf_id"])
            self.assertEqual(left["r_interval"], right["r_interval"])
            self.assertEqual(left["lambda_lo"], right["lambda_lo"])
            self.assertEqual(left["lambda_hi"], right["lambda_hi"])

    def test_frozen_partition_identity_and_endpoints(self):
        leaves = producer.fatal_slope_prepartition_leaves(
            self.domain, self.lam_lo, self.lam_hi
        )
        self.assertEqual(
            [row["leaf_id"] for row in leaves[:6]],
            [
                "R0/LALL",
                "R10/L0",
                "R10/L1",
                "R110/L00",
                "R110/L01",
                "R110/L1",
            ],
        )
        self.assertEqual(leaves[0]["r_interval"].lo, self.domain.lo)
        self.assertEqual(leaves[6]["r_interval"].hi, self.domain.hi)
        self.assertEqual(leaves[0]["lambda_lo"], self.lam_lo)
        self.assertEqual(leaves[0]["lambda_hi"], self.lam_hi)

        r111 = leaves[6:]
        self.assertEqual(len(r111), 24)
        for offset in range(0, 24, 4):
            group = r111[offset:offset + 4]
            self.assertTrue(
                all(x["r_interval"] == group[0]["r_interval"] for x in group)
            )
            self.assertEqual(
                [(x["lambda_lo"], x["lambda_hi"]) for x in group],
                [
                    (self.lam_lo, self.lam_lo + Fraction(1, 16)),
                    (
                        self.lam_lo + Fraction(1, 16),
                        self.lam_lo + Fraction(2, 16),
                    ),
                    (
                        self.lam_lo + Fraction(2, 16),
                        self.lam_lo + Fraction(3, 16),
                    ),
                    (
                        self.lam_lo + Fraction(3, 16),
                        self.lam_hi,
                    ),
                ],
            )

        r_bins = [r111[i]["r_interval"] for i in range(0, 24, 4)]
        for near, far in zip(r_bins[:-1], r_bins[1:]):
            self.assertEqual(far.hi, near.lo)
        self.assertEqual(r_bins[0].hi, self.domain.hi)

    def test_outside_frozen_target_rejected(self):
        shifted = DyadicInterval(
            self.domain.lo,
            self.domain.hi - Dyadic(1, 86),
        )
        with self.assertRaises(CalibrationError):
            producer.fatal_slope_prepartition_leaves(
                shifted, self.lam_lo, self.lam_hi
            )

    def _synthetic_trace(self):
        marker = "|" + verifier.VERIFIER_PREPARTITION_RULE_ID + "|"
        rows = []
        cumulative = 0
        for leaf in verifier.expected_prepartition_leaves():
            cumulative += 1
            rows.append({
                "phase": "CANDIDATE:0" + marker + leaf["leaf_id"],
                "quantity": "F_r",
                "route_id": ROUTED_BOUNDARY_ROUTE_ID,
                "post_failure_fallback": False,
                "r_interval": leaf["r_interval"].to_json(),
                "detail": {
                    "exact_lambda_transport": {
                        "lambda_exact_interval": {
                            "lo": Rational.from_fraction(
                                leaf["lambda_lo"]
                            ).to_json(),
                            "hi": Rational.from_fraction(
                                leaf["lambda_hi"]
                            ).to_json(),
                        },
                    },
                    "refinement_predicate_id": "R7_HU_POS_V1",
                },
                "enclosure": DyadicInterval(
                    Dyadic(-2, 0), Dyadic(-1, 0)
                ).to_json(),
                "boundary_route_evaluation_count_delta": 1,
                "boundary_route_evaluation_count_total": cumulative,
            })
        return rows

    def test_independent_trace_verifier_accepts_exact_30_leaf_profile(self):
        result = verifier.verify_prepartition_trace_records(
            self._synthetic_trace()
        )
        self.assertEqual(result["prepartition_leaf_count"], 30)
        self.assertEqual(result["prepartition_group_count"], 1)
        self.assertEqual(
            result["prepartition_total_boundary_evaluations"], 30
        )

    def test_independent_trace_verifier_rejects_lambda_tamper(self):
        rows = self._synthetic_trace()
        rows = copy.deepcopy(rows)
        rows[10]["detail"]["exact_lambda_transport"][
            "lambda_exact_interval"
        ]["lo"] = Rational.from_fraction(Fraction(5, 2)).to_json()
        with self.assertRaises(CalibrationError):
            verifier.verify_prepartition_trace_records(rows)

    def test_candidate_zero_without_prepartition_is_rejected(self):
        with self.assertRaises(CalibrationError):
            verifier.verify_prepartition_trace_records([
                {"phase": "CANDIDATE:0"}
            ])


if __name__ == "__main__":
    unittest.main()
