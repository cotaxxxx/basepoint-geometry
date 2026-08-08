#!/usr/bin/env python3
"""Stdlib controls for checkpoint-hook runner candidate v2."""
from __future__ import annotations

from fractions import Fraction
from types import SimpleNamespace
import unittest

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
    def __init__(self) -> None:
        self.kernel_call_counts = {"FAKE": 0}
    def evaluate_g(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        return SignInterval("POS" if r_cell[0] == Fraction(1, 64) else "NEG")
    def evaluate_mean_value(self, *, r_cell, lambda_box, dps):
        self.kernel_call_counts["FAKE"] += 1
        root = (Fraction(1, 64), Fraction(11, 256))
        if r_cell == root:
            return SimpleNamespace(
                strict_negative=False,
                mean_value=MVInterval(Fraction(1)),
                r_score=Fraction(10),
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


class RunnerV2Controls(unittest.TestCase):
    def test_same_mathematical_order_with_hook(self) -> None:
        snapshots = []
        result = r.run_rehearsal_partition(
            adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
            progress_hook=snapshots.append,
        )
        self.assertEqual(result.terminal_class, "COMPLETE_CANDIDATE")
        self.assertEqual(result.runner_id, "ITEM3_SWEEP_V9_REHEARSAL_RUNNER_CANDIDATE_V2")
        self.assertEqual([x.path_id for x in result.attempts], ["ROOT", "ROOT/R0", "ROOT/R1"])
        self.assertEqual([x.path_id for x in result.accepted_leaves], ["ROOT/R0", "ROOT/R1"])
        self.assertEqual([x.event for x in snapshots], [
            "ATTEMPT_COMPLETE", "ATTEMPT_COMPLETE", "ATTEMPT_COMPLETE", "SHARD_COMPLETE"
        ])
        self.assertEqual([x.path_id for x in snapshots[0].pending_nodes], ["ROOT/R1", "ROOT/R0"])
        self.assertEqual([x.path_id for x in snapshots[1].pending_nodes], ["ROOT/R1"])
        self.assertEqual(snapshots[2].pending_nodes, ())
        self.assertEqual(snapshots[3].pending_nodes, ())
        self.assertEqual(snapshots[0].last_complete_attempt_id, "A0:ROOT")
        self.assertEqual(snapshots[3].last_complete_attempt_id, "A2:ROOT/R1")

    def test_no_hook_does_not_change_result(self) -> None:
        a = r.run_rehearsal_partition(adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L)
        b = r.run_rehearsal_partition(adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L, progress_hook=lambda _x: None)
        self.assertEqual(a, b)

    def test_hook_failure_is_infrastructure_error(self) -> None:
        def fail(_snapshot):
            raise OSError("injected checkpoint failure")
        with self.assertRaises(r.RunnerInfrastructureError):
            r.run_rehearsal_partition(
                adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
                progress_hook=fail,
            )

    def test_rehearsal_caps_unchanged(self) -> None:
        self.assertEqual(r.derived_depth_cap(ROOT_R, r.R_FLOOR), 10)
        self.assertEqual(r.derived_depth_cap(ROOT_L, r.LAMBDA_FLOOR), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
