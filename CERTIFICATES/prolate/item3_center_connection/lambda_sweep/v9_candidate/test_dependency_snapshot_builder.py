#!/usr/bin/env python3
"""Determinism/structure controls for build_dependency_snapshot_v9."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import build_dependency_snapshot_v9 as b


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


class DependencyBuilderControls(unittest.TestCase):
    def test_two_builds_are_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = root / "a"
            c = root / "b"
            report_a = b.build(ROOT, a)
            report_b = b.build(ROOT, c)
            self.assertEqual(report_a, report_b)
            files_a = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
            files_b = sorted(p.relative_to(c) for p in c.rglob("*") if p.is_file())
            self.assertEqual(files_a, files_b)
            for rel in files_a:
                self.assertEqual((a / rel).read_bytes(), (c / rel).read_bytes(), rel)

    def test_exact_eight_entries_and_source_keys(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            report = b.build(ROOT, out)
            self.assertEqual(report["entry_count"], 8)
            self.assertEqual(set(report["entry_sha256"]), set(b.STATEMENTS))
            self.assertEqual(set(report["source_sha256"]), set(b.SOURCE_PATHS))
            snapshot = json.loads((out / "dependency_snapshot_v9_candidate.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["schema"], b.SNAPSHOT_SCHEMA)
            self.assertEqual(set(snapshot["entries"]), set(b.STATEMENTS))
            self.assertEqual(snapshot["allowlist_id"], b.ALLOWLIST_ID)

    def test_entry_hashes_match_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            report = b.build(ROOT, out)
            for lemma_id, expected in report["entry_sha256"].items():
                observed = hashlib.sha256((out / f"{lemma_id}.json").read_bytes()).hexdigest()
                self.assertEqual(observed, expected)
            snapshot_bytes = (out / "dependency_snapshot_v9_candidate.json").read_bytes()
            self.assertTrue(snapshot_bytes.endswith(b"\n"))
            self.assertEqual(hashlib.sha256(snapshot_bytes).hexdigest(), report["snapshot_sha256"])

    def test_all_generated_json_is_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out"
            b.build(ROOT, out)
            for path in out.glob("*.json"):
                raw = path.read_bytes()
                self.assertTrue(raw.endswith(b"\n"), path.name)
                obj = json.loads(raw.decode("utf-8"))
                self.assertEqual(raw, b.canonical_bytes(obj), path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
