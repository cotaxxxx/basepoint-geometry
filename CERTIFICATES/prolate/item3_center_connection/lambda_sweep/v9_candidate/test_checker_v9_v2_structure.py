#!/usr/bin/env python3
"""Stdlib structural/mutation controls for checker candidate v2."""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import unittest

import checker_v9_candidate_v2 as c
import runner_v9_candidate_v2 as r


class SignInterval:
    def __init__(self, sign: str) -> None:
        self.sign = sign
    def __eq__(self, other) -> bool:
        return isinstance(other, SignInterval) and self.sign == other.sign
    def strictly_positive(self) -> bool:
        return self.sign == "POS"
    def strictly_negative(self) -> bool:
        return self.sign == "NEG"


class MVInterval:
    finite = True
    def __init__(self, hi: Fraction) -> None:
        self.hi = hi


class FakeAdapter:
    def __init__(self, *, verify_fail_path=None) -> None:
        self.kernel_call_counts = {"FAKE": 0}
        self.verify_fail_path = verify_fail_path
    def evaluate_g(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        return SignInterval("POS" if r_cell[0] == Fraction(1, 64) else "NEG")
    def evaluate_mean_value(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        root = (Fraction(1, 64), Fraction(11, 256))
        if r_cell == root and dps == 50:
            return SimpleNamespace(
                strict_negative=False, mean_value=MVInterval(Fraction(1)),
                r_score=Fraction(10), lambda_score=Fraction(1),
            )
        if self.verify_fail_path is not None and r_cell == self.verify_fail_path and dps == 70:
            return SimpleNamespace(
                strict_negative=False, mean_value=MVInterval(Fraction(1)),
                r_score=Fraction(1), lambda_score=Fraction(1),
            )
        return SimpleNamespace(
            strict_negative=True, mean_value=MVInterval(Fraction(-1)),
            r_score=Fraction(1), lambda_score=Fraction(1),
        )


ROOT_R = (Fraction(1, 64), Fraction(11, 256))
ROOT_L = (Fraction(123731943, 26214400), Fraction(118, 25))


def make_result():
    return r.run_rehearsal_partition(
        adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L
    )


class CheckerV2Controls(unittest.TestCase):
    def test_fresh_replay_records_dps70_leaf_bounds(self) -> None:
        report = c.verify_runner_result(
            runner_result=make_result(),
            control_adapter=FakeAdapter(),
            verification_adapter=FakeAdapter(),
        )
        self.assertEqual(report.status, "PASS_CANDIDATE")
        self.assertEqual(report.dps50_attempt_count, 3)
        self.assertEqual(report.dps70_verified_leaf_count, 2)
        self.assertEqual([v.path_id for v in report.verified_leaves_dps70], ["ROOT/R0", "ROOT/R1"])
        self.assertTrue(all(v.mean_value_hi_dps70 < 0 for v in report.verified_leaves_dps70))

    def test_runner_id_mutation_rejected(self) -> None:
        tampered = replace(make_result(), runner_id="WRONG")
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=tampered,
                control_adapter=FakeAdapter(), verification_adapter=FakeAdapter(),
            )

    def test_runner_endpoint_evidence_mutation_rejected(self) -> None:
        tampered = replace(make_result(), endpoint_g_lo=SignInterval("NEG"))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=tampered,
                control_adapter=FakeAdapter(), verification_adapter=FakeAdapter(),
            )

    def test_axis_mutation_rejected(self) -> None:
        result = make_result()
        attempts = list(result.attempts)
        attempts[0] = replace(attempts[0], selected_axis="lambda")
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=replace(result, attempts=tuple(attempts)),
                control_adapter=FakeAdapter(), verification_adapter=FakeAdapter(),
            )

    def test_score_mutation_rejected(self) -> None:
        result = make_result()
        attempts = list(result.attempts)
        attempts[0] = replace(attempts[0], r_score=Fraction(999))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=replace(result, attempts=tuple(attempts)),
                control_adapter=FakeAdapter(), verification_adapter=FakeAdapter(),
            )

    def test_leaf_bound_mutation_rejected(self) -> None:
        result = make_result()
        leaves = list(result.accepted_leaves)
        leaves[0] = replace(leaves[0], mean_value_hi=Fraction(-2))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=replace(result, accepted_leaves=tuple(leaves)),
                control_adapter=FakeAdapter(), verification_adapter=FakeAdapter(),
            )

    def test_same_adapter_rejected(self) -> None:
        adapter = FakeAdapter()
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=make_result(), control_adapter=adapter,
                verification_adapter=adapter,
            )

    def test_dps70_failure_rejected(self) -> None:
        result = make_result()
        first = result.accepted_leaves[0].r_cell
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=result,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(verify_fail_path=first),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
