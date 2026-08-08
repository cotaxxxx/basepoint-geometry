#!/usr/bin/env python3
"""Stdlib transaction/cancellation controls for checkpoint_v9_candidate."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import checkpoint_v9_candidate as c


def progress(n: int) -> dict:
    return {
        "schema": "ITEM3_SWEEP_V9_PROGRESS_V1",
        "frontier": {"pending": [n, n + 1]},
        "completed_attempts": n,
        "status": "PARTIAL",
    }


def partial(n: int) -> dict:
    return {
        "schema": "ITEM3_SWEEP_V9_PARTIAL_EVIDENCE_V1",
        "attempts": [{"id": str(i)} for i in range(n)],
        "status": "PARTIAL",
    }


class FakeClock:
    def __init__(self) -> None:
        self.value = 1000.0
    def __call__(self) -> float:
        return self.value


class CheckpointTransactionControls(unittest.TestCase):
    def with_root(self):
        return tempfile.TemporaryDirectory()

    def test_two_commits_recover_exact_chain(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            a = store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            b = store.commit(progress=progress(2), partial_evidence=partial(2), last_complete_attempt_id="A2")
            rec = c.recover_committed(root)
            self.assertEqual([x.checkpoint_sequence for x in rec], [0, 1])
            self.assertEqual(rec[0].checkpoint_sha256, a.checkpoint_sha256)
            self.assertEqual(rec[1].checkpoint_sha256, b.checkpoint_sha256)

    def test_orphan_payload_before_ledger_commit_is_ignored(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            committed = store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            store.publish_orphan_for_test(kind="progress", value=progress(999))
            rec = c.recover_committed(root)
            self.assertEqual(len(rec), 1)
            self.assertEqual(rec[0].checkpoint_sha256, committed.checkpoint_sha256)

    def test_trailing_non_line_suffix_is_ignored(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            committed = store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            with (root / "SWEEP_PROGRESS.jsonl").open("ab") as handle:
                handle.write(b'{"torn":')
                handle.flush()
            rec = c.recover_committed(root)
            self.assertEqual(len(rec), 1)
            self.assertEqual(rec[0].checkpoint_sha256, committed.checkpoint_sha256)

    def test_malformed_complete_line_rejected(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            with (root / "SWEEP_PROGRESS.jsonl").open("ab") as handle:
                handle.write(b'{"broken":true}\n')
            with self.assertRaises(c.CheckpointError):
                c.recover_committed(root)

    def test_missing_committed_payload_rejected(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            record = store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            path = root / "checkpoint_payloads" / "progress" / f"{record.progress_payload_sha256}.json"
            path.unlink()
            with self.assertRaises(c.CheckpointError):
                c.recover_committed(root)

    def test_prior_payload_survives_later_orphan(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            first = store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            old_path = root / "checkpoint_payloads" / "partial" / f"{first.partial_evidence_sha256}.json"
            old_bytes = old_path.read_bytes()
            store.publish_orphan_for_test(kind="partial", value=partial(9))
            self.assertEqual(old_path.read_bytes(), old_bytes)
            self.assertEqual(len(c.recover_committed(root)), 1)

    def test_stale_mirrors_do_not_control_recovery(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            (root / "SWEEP_PROGRESS.json").write_text("stale mirror\n", encoding="utf-8")
            (root / "SWEEP_PARTIAL_EVIDENCE.json").write_text("stale mirror\n", encoding="utf-8")
            self.assertEqual(len(c.recover_committed(root)), 1)

    def test_commit_without_mirror_refresh_still_recovers(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            record = store.commit(
                progress=progress(1),
                partial_evidence=partial(1),
                last_complete_attempt_id="A1",
                refresh_mirrors=False,
            )
            self.assertFalse((root / "SWEEP_PROGRESS.json").exists())
            rec = c.recover_committed(root)
            self.assertEqual(rec[0].checkpoint_sha256, record.checkpoint_sha256)

    def test_payload_size_ceiling_fails_closed(self) -> None:
        with self.with_root() as td:
            store = c.CheckpointStore(Path(td), max_payload_bytes=64)
            with self.assertRaises(c.CheckpointError):
                store.commit(
                    progress=progress(100),
                    partial_evidence=partial(100),
                    last_complete_attempt_id="A100",
                )

    def test_float_in_normative_payload_rejected(self) -> None:
        with self.with_root() as td:
            store = c.CheckpointStore(Path(td))
            bad = progress(1)
            bad["elapsed"] = 1.25
            with self.assertRaises(c.CheckpointError):
                store.commit(progress=bad, partial_evidence=partial(1), last_complete_attempt_id="A1")

    def test_cadence_attempt_threshold(self) -> None:
        clock = FakeClock()
        cadence = c.CheckpointCadence(clock=clock)
        for _ in range(31):
            cadence.completed_attempt()
            self.assertFalse(cadence.should_commit())
        cadence.completed_attempt()
        self.assertTrue(cadence.should_commit())
        cadence.mark_committed()
        self.assertFalse(cadence.should_commit())

    def test_cadence_time_and_structural_shutdown(self) -> None:
        clock = FakeClock()
        cadence = c.CheckpointCadence(clock=clock)
        clock.value += 120.0
        self.assertTrue(cadence.should_commit())
        cadence.mark_committed()
        self.assertTrue(cadence.should_commit(structural=True))
        cadence.mark_committed()
        self.assertTrue(cadence.should_commit(shutdown=True))

    def test_wrong_previous_hash_rejected(self) -> None:
        with self.with_root() as td:
            root = Path(td)
            store = c.CheckpointStore(root)
            store.commit(progress=progress(1), partial_evidence=partial(1), last_complete_attempt_id="A1")
            store.commit(progress=progress(2), partial_evidence=partial(2), last_complete_attempt_id="A2")
            path = root / "SWEEP_PROGRESS.jsonl"
            lines = path.read_bytes().splitlines(keepends=True)
            obj = json.loads(lines[1].decode("utf-8"))
            obj["previous_checkpoint_sha256"] = "f" * 64
            lines[1] = c.canonical_json_file_bytes(obj)
            path.write_bytes(b"".join(lines))
            with self.assertRaises(c.CheckpointError):
                c.recover_committed(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
