#!/usr/bin/env python3
"""Stdlib-only structural controls for runner_v9_candidate."""
from __future__ import annotations

from fractions import Fraction
from types import SimpleNamespace
import unittest

import runner_v9_candidate as r


class SignInterval:
    def __init__(self, sign: str) -> None:
        self.sign = sign

    def strictly_positive(self) -> bool:
        return self.sign == "POS"

    def strictly_negative(self) -> bool:
        return self.sign == "NEG"


class MVInterval:
    finite = True

    def __init__(self, hi: Fraction) -> None:
        self.hi = hi


class FakeAdapter:
    def __init__(self, policy) -> None:
        self.policy = policy
        self.kernel_call_counts = {"FAKE": 0}

    def evaluate_g(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        return SignInterval("POS" if r_cell[0] == Fraction(1, 64) else "NEG")

    def evaluate_mean_value(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        strict, rs, ls = self.policy(r_cell, lambda_box)
        return SimpleNamespace(
            strict_negative=strict,
            mean_value=MVInterval(Fraction(-1) if strict else Fraction(1)),
            r_score=rs,
            lambda_score=ls,
        )


ROOT_R = (Fraction(1, 64), Fraction(11, 256))
REHEARSAL_LAMBDA = (Fraction(123731943, 26214400), Fraction(118, 25))


class RunnerStructureControls(unittest.TestCase):
    def test_rehearsal_lambda_depth_cap_zero(self) -> None:
        self.assertEqual(r.derived_depth_cap(REHEARSAL_LAMBDA, Fraction(1, 1 << 16)), 0)

    def test_r_root_depth_cap_exact(self) -> None:
        self.assertEqual(r.derived_depth_cap(ROOT_R, Fraction(1, 1 << 16)), 10)

    def test_r_processing_order_lower_then_upper(self) -> None:
        root_mid = (ROOT_R[0] + ROOT_R[1]) / 2
        def policy(rcell, lbox):
            if rcell == ROOT_R:
                return False, Fraction(10), Fraction(1)
            return True, Fraction(1), Fraction(1)

        result = r.run_rehearsal_partition(
            adapter=FakeAdapter(policy), root_r=ROOT_R, root_lambda=REHEARSAL_LAMBDA
        )
        self.assertEqual(result.terminal_class, "COMPLETE_CANDIDATE")
        self.assertEqual([x.path_id for x in result.attempts], ["ROOT", "ROOT/R0", "ROOT/R1"])
        self.assertEqual([x.path_id for x in result.accepted_leaves], ["ROOT/R0", "ROOT/R1"])
        self.assertEqual(result.accepted_leaves[0].r_cell, (ROOT_R[0], root_mid))
        self.assertEqual(result.accepted_leaves[1].r_cell, (root_mid, ROOT_R[1]))

    def test_lambda_processing_order_upper_then_lower(self) -> None:
        # Make r unsplittable and lambda splittable only for this structural test.
        lbox = (Fraction(4), Fraction(5))
        def policy(rcell, lb):
            if lb == lbox:
                return False, Fraction(1), Fraction(10)
            return True, Fraction(1), Fraction(1)

        result = r.run_rehearsal_partition(
            adapter=FakeAdapter(policy),
            root_r=ROOT_R,
            root_lambda=lbox,
            r_floor=Fraction(1),
            lambda_floor=Fraction(1, 8),
        )
        self.assertEqual(result.terminal_class, "COMPLETE_CANDIDATE")
        self.assertEqual([x.path_id for x in result.attempts], ["ROOT", "ROOT/L1", "ROOT/L0"])
        self.assertEqual([x.path_id for x in result.accepted_leaves], ["ROOT/L1", "ROOT/L0"])

    def test_exact_finite_tie_selects_r(self) -> None:
        axis, reason = r.select_axis(
            r_score=Fraction(7, 9),
            lambda_score=Fraction(7, 9),
            r_splittable=True,
            lambda_splittable=True,
        )
        self.assertEqual((axis, reason), ("r", "EXACT_SCORE_TIE_TO_R"))

    def test_double_nonfinite_tie_selects_r(self) -> None:
        axis, reason = r.select_axis(
            r_score=None,
            lambda_score=None,
            r_splittable=True,
            lambda_splittable=True,
        )
        self.assertEqual((axis, reason), ("r", "DOUBLE_NONFINITE_TIE_TO_R"))

    def test_unsplittable_nonneg_is_incomplete(self) -> None:
        small_r = (Fraction(1, 64), Fraction(1, 64) + Fraction(1, 1 << 16))
        def policy(rcell, lbox):
            return False, Fraction(1), Fraction(1)

        result = r.run_rehearsal_partition(
            adapter=FakeAdapter(policy),
            root_r=small_r,
            root_lambda=REHEARSAL_LAMBDA,
            r_floor=Fraction(1, 1 << 16),
            lambda_floor=Fraction(1, 1 << 16),
        )
        self.assertEqual(result.terminal_class, "INCOMPLETE")
        self.assertEqual(result.reason, "STOP_FLOOR_NO_STRICT_NEG")

    def test_endpoint_failure_does_not_refine(self) -> None:
        class BadEndpointAdapter(FakeAdapter):
            def evaluate_g(self, *, r_cell, lambda_box, dps):
                return SignInterval("NEG")
        result = r.run_rehearsal_partition(
            adapter=BadEndpointAdapter(lambda *_: (True, Fraction(1), Fraction(1))),
            root_r=ROOT_R,
            root_lambda=REHEARSAL_LAMBDA,
        )
        self.assertEqual(result.terminal_class, "INCOMPLETE")
        self.assertEqual(result.reason, "S1_ENDPOINT_SIGN_FAIL")
        self.assertEqual(result.attempts, ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
