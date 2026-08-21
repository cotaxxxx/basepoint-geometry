from __future__ import annotations

import copy
from fractions import Fraction
import unittest
from unittest import mock

import calibration_security
from calibration_context import CalibrationError, Dyadic, DyadicInterval, Rational, SchemaError
from exact_lambda_contract import (
    EXACT_LAMBDA_ROUNDING_BITS,
    EXACT_LAMBDA_TRANSPORT_SHA256,
)
from exact_lambda_static import assert_exact_lambda_static_gate
from exact_lambda_transport import (
    ExactLambdaRoutedEvaluator,
    _install_runtime_lambda_native_f_guard,
)
from exact_lambda_verifier import (
    reconstruct_transport,
    verify_transport_detail,
)
from numeric_schema import parse_canonical_json_bytes


LAMBDA_START = Fraction(3307749, 1600000)
BRIDGE = Fraction(17, 8)
LAMBDA_END = Fraction(118, 25)


class ExactLambdaPositiveControls(unittest.TestCase):
    def test_positive_lambda_start_zero_rounding_loss(self):
        detail = reconstruct_transport(LAMBDA_START, LAMBDA_START)
        self.assertEqual(
            Rational.from_json(detail["s_exact_interval"]["lo"]).as_fraction(),
            Fraction(1, 512),
        )
        self.assertEqual(
            Rational.from_json(
                detail["lower_rounding_enlargement"]
            ).as_fraction(),
            Fraction(0),
        )
        self.assertEqual(
            Rational.from_json(
                detail["upper_rounding_enlargement"]
            ).as_fraction(),
            Fraction(0),
        )
        verify_transport_detail(detail)

    def test_positive_bridge_requires_outward_rounding(self):
        detail = reconstruct_transport(BRIDGE, BRIDGE)
        lower = Rational.from_json(
            detail["lower_rounding_enlargement"]
        ).as_fraction()
        upper = Rational.from_json(
            detail["upper_rounding_enlargement"]
        ).as_fraction()
        self.assertGreater(lower + upper, 0)
        self.assertLess(lower + upper, Fraction(1, 1 << 191))
        verify_transport_detail(detail)

    def test_positive_lambda_end_requires_outward_rounding(self):
        detail = reconstruct_transport(LAMBDA_END, LAMBDA_END)
        lower = Rational.from_json(
            detail["lower_rounding_enlargement"]
        ).as_fraction()
        upper = Rational.from_json(
            detail["upper_rounding_enlargement"]
        ).as_fraction()
        self.assertGreater(lower + upper, 0)
        self.assertLess(lower + upper, Fraction(1, 1 << 191))
        verify_transport_detail(detail)

    def test_static_gate(self):
        result = assert_exact_lambda_static_gate()
        self.assertEqual(
            result["transport_sha256"], EXACT_LAMBDA_TRANSPORT_SHA256
        )


class ExactLambdaNegativeControls(unittest.TestCase):
    def setUp(self):
        self.base = reconstruct_transport(BRIDGE, BRIDGE)

    def assert_transport_rejected(self, mutate):
        with self.assertRaises((CalibrationError, SchemaError)):
            detail = copy.deepcopy(self.base)
            mutate(detail)
            verify_transport_detail(detail)

    def test_negative_01_noncanonical_rational_encoding_rejected(self):
        with self.assertRaises(SchemaError):
            Rational.from_json({"p": "02", "q": "1"})
        with self.assertRaises(Exception):
            parse_canonical_json_bytes(b'{"q":"1","p":"2"}')

    def test_negative_02_modified_exact_lambda_rejected(self):
        def mutate(detail):
            detail["lambda_exact_interval"]["lo"] = Rational.from_fraction(
                Fraction(5, 2)
            ).to_json()
        self.assert_transport_rejected(mutate)

    def test_negative_03_modified_lambda_plus_rejected(self):
        self.assert_transport_rejected(
            lambda d: d.__setitem__(
                "lambda_plus", Rational.from_fraction(Fraction(2, 1)).to_json()
            )
        )

    def test_negative_04_modified_exact_s_rejected(self):
        def mutate(detail):
            detail["s_exact_interval"]["hi"] = Rational.from_fraction(
                Fraction(1, 10)
            ).to_json()
        self.assert_transport_rejected(mutate)

    def test_negative_05_inward_rounded_s_rejected(self):
        def mutate(detail):
            iv = DyadicInterval.from_json(detail["s_outward_dyadic_interval"])
            one_ulp = Dyadic(1, EXACT_LAMBDA_ROUNDING_BITS)
            detail["s_outward_dyadic_interval"] = DyadicInterval(
                iv.lo + one_ulp, iv.hi
            ).to_json()
        self.assert_transport_rejected(mutate)

    def test_negative_06_one_ulp_endpoint_tamper_rejected(self):
        def mutate(detail):
            iv = DyadicInterval.from_json(detail["s_outward_dyadic_interval"])
            one_ulp = Dyadic(1, EXACT_LAMBDA_ROUNDING_BITS)
            detail["s_outward_dyadic_interval"] = DyadicInterval(
                iv.lo, iv.hi + one_ulp
            ).to_json()
        self.assert_transport_rejected(mutate)

    def test_negative_07_rounding_bits_tamper_rejected(self):
        self.assert_transport_rejected(
            lambda d: d.__setitem__("rounding_bits", 191)
        )

    def test_negative_08_lambda_not_contained_rejected(self):
        def mutate(detail):
            iv = DyadicInterval.from_json(detail["s_outward_dyadic_interval"])
            one_ulp = Dyadic(1, EXACT_LAMBDA_ROUNDING_BITS)
            detail["s_outward_dyadic_interval"] = DyadicInterval(
                iv.lo + one_ulp, iv.hi - one_ulp
            ).to_json()
        self.assert_transport_rejected(mutate)

    def test_negative_09_arb_only_lambda_api_rejected(self):
        evaluator = object.__new__(ExactLambdaRoutedEvaluator)
        with self.assertRaises(CalibrationError):
            evaluator.F_arb(None, None)

    def test_negative_10_lambda_native_f_runtime_route_rejected(self):
        class FakeRoute:
            def enclose_f(self):
                return "unexpected"
        route = FakeRoute()
        _install_runtime_lambda_native_f_guard(route)
        with self.assertRaises(CalibrationError):
            route.enclose_f()

    def test_negative_11_frozen_source_sha_mismatch_rejected(self):
        tampered = dict(calibration_security.ROUTED_BOUNDARY_FILE_SHA256)
        name = sorted(tampered)[0]
        tampered[name] = "0" * 64
        with mock.patch.object(
            calibration_security, "ROUTED_BOUNDARY_FILE_SHA256", tampered
        ):
            with self.assertRaises(CalibrationError):
                calibration_security.assert_routed_boundary_dependency_bytes()

    def test_negative_12_frozen_config_sha_mismatch_rejected(self):
        with mock.patch.object(
            calibration_security, "ROUTED_BOUNDARY_CONFIG_SHA256", "0" * 64
        ):
            with self.assertRaises(CalibrationError):
                calibration_security.assert_routed_boundary_dependency_bytes()

    def test_negative_13_producer_s_mismatch_rejected(self):
        def mutate(detail):
            detail["s_outward_dyadic_interval"] = DyadicInterval.point(
                Dyadic(1, 9)
            ).to_json()
        self.assert_transport_rejected(mutate)


if __name__ == "__main__":
    unittest.main()
