#!/usr/bin/env python3
"""Integration controls for runner-v2 -> checkpoint bridge -> durable store."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

import checkpoint_bridge_v9_candidate as b
import checkpoint_v9_candidate as cp
import runner_v9_candidate_v2 as r


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


class CheckpointBridgeControls(unittest.TestCase):
    def test_default_cadence_commits_structural_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = cp.CheckpointStore(root)
            cadence = cp.CheckpointCadence(seconds=10_000, attempts=32)
            hook = b.ProgressCheckpointHook(store=store, cadence=cadence)
            result = r.run_rehearsal_partition(
                adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
                progress_hook=hook,
            )
            self.assertEqual(result.terminal_class, "COMPLETE_CANDIDATE")
            records = cp.recover_committed(root)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].last_complete_attempt_id, "A2:ROOT/R1")
            self.assertEqual(len(hook.commit_records), 1)

    def test_attempt_threshold_one_commits_every_attempt_plus_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = cp.CheckpointStore(root)
            cadence = cp.CheckpointCadence(seconds=10_000, attempts=1)
            hook = b.ProgressCheckpointHook(store=store, cadence=cadence)
            r.run_rehearsal_partition(
                adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
                progress_hook=hook,
            )
            records = cp.recover_committed(root)
            self.assertEqual(len(records), 4)
            self.assertEqual([x.checkpoint_sequence for x in records], [0, 1, 2, 3])
            self.assertEqual(records[-1].last_complete_attempt_id, "A2:ROOT/R1")

    def test_payloads_are_json_native_no_fraction_objects(self) -> None:
        snapshots = []
        r.run_rehearsal_partition(
            adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
            progress_hook=snapshots.append,
        )
        p = b.progress_payload(snapshots[0])
        q = b.partial_payload(snapshots[0])
        cp.canonical_json_file_bytes(p)
        cp.canonical_json_file_bytes(q)
        self.assertEqual(p["root_r"][0], {"p": "1", "q": "64"})
        self.assertEqual(q["attempts"][0]["path_id"], "ROOT")

    def test_force_shutdown_commits_latest_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            store = cp.CheckpointStore(Path(td))
            cadence = cp.CheckpointCadence(seconds=10_000, attempts=100)
            hook = b.ProgressCheckpointHook(store=store, cadence=cadence)
            snapshots = []
            def combined(snapshot):
                snapshots.append(snapshot)
                hook(snapshot)
            # Stop the runner by injected hook failure after one recorded snapshot is not
            # needed here; feed one real completed snapshot then force a shutdown commit.
            r.run_rehearsal_partition(
                adapter=FakeAdapter(), root_r=ROOT_R, root_lambda=ROOT_L,
                progress_hook=snapshots.append,
            )
            hook(snapshots[0])
            self.assertEqual(cp.recover_committed(Path(td), allow_missing_ledger=True), [])
            record = hook.force_shutdown_checkpoint()
            self.assertIsNotNone(record)
            self.assertEqual(len(cp.recover_committed(Path(td))), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
