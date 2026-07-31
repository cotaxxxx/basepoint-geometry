#!/usr/bin/env python3
'''Diagnostic tests for the v9 five-output derivative-kernel prototype.

Finite-difference checks are DIAGNOSTIC_ONLY and cannot approve the kernel.
'''
from __future__ import annotations

import json
import math
import unittest

import prolate_F_derivatives_cleanroom_v9 as kernel


class FloatDerivativeDiagnostics(unittest.TestCase):
    POINTS = (
        (0.0300, 4.7200),
        (0.0160, 4.7198),
        (0.0420, 4.7202),
    )

    def assert_close(self, actual: float, expected: float, label: str) -> None:
        error = abs(actual - expected)
        scale = max(1.0, abs(actual), abs(expected))
        self.assertLess(error, 5e-8 * scale, label)

    def test_first_and_second_derivatives(self) -> None:
        h_r = 1e-5
        h_lambda = 1e-5
        for r, lam in self.POINTS:
            with self.subTest(r=r, lam=lam):
                F = kernel.F_float(r, lam)
                F_r = kernel.F_r_float(r, lam)
                F_lambda = kernel.F_lambda_float(r, lam)
                F_rr = kernel.F_rr_float(r, lam)
                F_rlambda = kernel.F_rlambda_float(r, lam)

                fd_F_r = (
                    kernel.F_float(r + h_r, lam)
                    - kernel.F_float(r - h_r, lam)
                ) / (2 * h_r)
                fd_F_lambda = (
                    kernel.F_float(r, lam + h_lambda)
                    - kernel.F_float(r, lam - h_lambda)
                ) / (2 * h_lambda)
                fd_F_rr = (
                    kernel.F_r_float(r + h_r, lam)
                    - kernel.F_r_float(r - h_r, lam)
                ) / (2 * h_r)
                fd_F_rlambda = (
                    kernel.F_r_float(r, lam + h_lambda)
                    - kernel.F_r_float(r, lam - h_lambda)
                ) / (2 * h_lambda)

                self.assertTrue(math.isfinite(F))
                self.assert_close(F_r, fd_F_r, "F_r diagnostic mismatch")
                self.assert_close(F_lambda, fd_F_lambda, "F_lambda diagnostic mismatch")
                self.assert_close(F_rr, fd_F_rr, "F_rr diagnostic mismatch")
                self.assert_close(F_rlambda, fd_F_rlambda, "F_rlambda diagnostic mismatch")

    def test_angle_third_derivative_limit(self) -> None:
        _, h1, h2, h3 = kernel._float_angle_data_3(1.0)
        self.assertEqual(h1, -2.0)
        self.assertEqual(h2, 2.0 / 3.0)
        self.assertEqual(h3, -8.0 / 15.0)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FloatDerivativeDiagnostics)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "ITEM3_SWEEP_V9_FLOAT_DIAGNOSTIC_V1",
        "proof_status": "DIAGNOSTIC_ONLY",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "verdict": "PASS" if result.wasSuccessful() else "FAIL",
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result.wasSuccessful() else 1)
