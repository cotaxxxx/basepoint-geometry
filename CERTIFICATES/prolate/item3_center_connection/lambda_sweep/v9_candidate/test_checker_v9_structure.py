#!/usr/bin/env python3
"""Stdlib-only structural/mutation controls for checker_v9_candidate."""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import unittest

import checker_v9_candidate as c
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
    def __init__(self, *, verify_fail_path: tuple[Fraction, Fraction] | None = None) -> None:
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
                strict_negative=False,
                mean_value=MVInterval(Fraction(1)),
                r_score=Fraction(10),
                lambda_score=Fraction(1),
            )
        if self.verify_fail_path is not None and r_cell == self.verify_fail_path and dps == 70:
            return SimpleNamespace(
                strict_negative=False,
                mean_value=MVInterval(Fraction(1)),
                r_score=Fraction(1),
                lambda_score=Fraction(1),
            )
        return SimpleNamespace(
            strict_negative=True,
            mean_value=MVInterval(Fraction(-1)),
            r_score=Fraction(1),
            lambda_score=Fraction(1),
        )


ROOT_R = (Fraction(1, 64), Fraction(11, 256))
ROOT_L = (Fraction(123731943, 26214400), Fraction(118, 25))


def make_runner_result():
    return r.run_rehearsal_partition(
        adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L
    )


class CheckerStructureControls(unittest.TestCase):
    def test_fresh_replay_and_verify_pass(self) -> None:
        result = make_runner_result()
        report = c.verify_runner_result(
            runner_result=result,
            control_adapter=FakeAdapter(),
            verification_adapter=FakeAdapter(),
        )
        self.assertEqual(report.status, "PASS_CANDIDATE")
        self.assertEqual(report.dps50_attempt_count, 3)
        self.assertEqual(report.dps50_leaf_count, 2)
        self.assertEqual(report.dps70_verified_leaf_count, 2)

    def test_same_adapter_instance_rejected(self) -> None:
        result = make_runner_result()
        adapter = FakeAdapter()
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=result,
                control_adapter=adapter,
                verification_adapter=adapter,
            )

    def test_runner_selected_axis_mutation_rejected(self) -> None:
        result = make_runner_result()
        attempts = list(result.attempts)
        attempts[0] = replace(attempts[0], selected_axis="lambda")
        tampered = replace(result, attempts=tuple(attempts))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=tampered,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(),
            )

    def test_runner_score_mutation_rejected(self) -> None:
        result = make_runner_result()
        attempts = list(result.attempts)
        attempts[0] = replace(attempts[0], r_score=Fraction(999))
        tampered = replace(result, attempts=tuple(attempts))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=tampered,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(),
            )

    def test_runner_leaf_mv_mutation_rejected(self) -> None:
        result = make_runner_result()
        leaves = list(result.accepted_leaves)
        leaves[0] = replace(leaves[0], mean_value_hi=Fraction(-2))
        tampered = replace(result, accepted_leaves=tuple(leaves))
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=tampered,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(),
            )

    def test_dps70_failure_rejects_without_repartition(self) -> None:
        result = make_runner_result()
        first_leaf = result.accepted_leaves[0].r_cell
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=result,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(verify_fail_path=first_leaf),
            )

    def test_incomplete_runner_cannot_pass(self) -> None:
        result = replace(make_runner_result(), terminal_class="INCOMPLETE")
        with self.assertRaises(c.CheckerReject):
            c.verify_runner_result(
                runner_result=result,
                control_adapter=FakeAdapter(),
                verification_adapter=FakeAdapter(),
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
