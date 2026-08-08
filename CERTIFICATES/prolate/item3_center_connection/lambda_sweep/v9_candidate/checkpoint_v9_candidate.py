#!/usr/bin/env python3
"""Cancellation-safe checkpoint transaction candidate for Item 3 sweep v9.

STATUS: IMPLEMENTATION CANDIDATE / PROVENANCE ONLY / NO RESUME.

The only checkpoint commit point is fsync of an append-only canonical JSONL line after
both hash-addressed immutable payloads are durable.  Latest JSON files are mirrors only.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Callable


CHECKPOINT_LINE_SCHEMA = "ITEM3_SWEEP_V9_PROGRESS_LINE_V1"
MAX_PAYLOAD_BYTES = 33_554_432
ZERO_SHA256 = "0" * 64


class CheckpointError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommitRecord:
    checkpoint_sequence: int
    checkpoint_sha256: str
    progress_payload_sha256: str
    partial_evidence_sha256: str
    frontier_digest_sha256: str
    last_complete_attempt_id: str
    mirror_refresh_ok: bool


@dataclass
class CadenceState:
    last_commit_monotonic: float
    attempts_since_commit: int = 0


class CheckpointCadence:
    def __init__(
        self,
        *,
        seconds: float = 120.0,
        attempts: int = 32,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if seconds <= 0 or attempts <= 0:
            raise CheckpointError("checkpoint cadence thresholds must be positive")
        self.seconds = float(seconds)
        self.attempts = int(attempts)
        self.clock = clock
        self.state = CadenceState(last_commit_monotonic=float(clock()))

    def completed_attempt(self) -> None:
        self.state.attempts_since_commit += 1

    def should_commit(self, *, structural: bool = False, shutdown: bool = False) -> bool:
        now = float(self.clock())
        return bool(
            structural
            or shutdown
            or self.state.attempts_since_commit >= self.attempts
            or now - self.state.last_commit_monotonic >= self.seconds
        )

    def mark_committed(self) -> None:
        self.state.last_commit_monotonic = float(self.clock())
        self.state.attempts_since_commit = 0


def _reject_floats(value: Any, where: str = "root") -> None:
    if isinstance(value, float):
        raise CheckpointError(f"binary float prohibited in canonical checkpoint object: {where}")
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise CheckpointError(f"non-string JSON key: {where}")
        for key, item in value.items():
            _reject_floats(item, f"{where}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_floats(item, f"{where}[{index}]")
    elif value is None or isinstance(value, (str, int, bool)):
        return
    else:
        raise CheckpointError(f"unsupported canonical checkpoint type at {where}: {type(value)!r}")


def canonical_json_file_bytes(value: Any) -> bytes:
    _reject_floats(value)
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_temp_fsync(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.monotonic_ns()}")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temp, flags, 0o600)
    try:
        offset = 0
        while offset < len(data):
            written = os.write(fd, data[offset:])
            if written <= 0:
                raise CheckpointError("short checkpoint write")
            offset += written
        os.fsync(fd)
    finally:
        os.close(fd)
    return temp


def atomic_replace_file(path: Path, data: bytes) -> None:
    temp = _write_temp_fsync(path, data)
    try:
        os.replace(temp, path)
        _fsync_directory(path.parent)
    finally:
        if temp.exists():
            temp.unlink()


class CheckpointStore:
    def __init__(
        self,
        root: Path,
        *,
        max_payload_bytes: int = MAX_PAYLOAD_BYTES,
    ) -> None:
        self.root = root
        self.max_payload_bytes = int(max_payload_bytes)
        if self.max_payload_bytes <= 0:
            raise CheckpointError("max payload bytes must be positive")
        self.progress_dir = self.root / "checkpoint_payloads" / "progress"
        self.partial_dir = self.root / "checkpoint_payloads" / "partial"
        self.jsonl_path = self.root / "SWEEP_PROGRESS.jsonl"
        self.progress_mirror = self.root / "SWEEP_PROGRESS.json"
        self.partial_mirror = self.root / "SWEEP_PARTIAL_EVIDENCE.json"
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        self.partial_dir.mkdir(parents=True, exist_ok=True)
        _fsync_directory(self.progress_dir.parent)
        self._records = recover_committed(self.root, allow_missing_ledger=True)

    def _publish_payload(self, kind: str, value: Any) -> tuple[str, bytes, Path]:
        data = canonical_json_file_bytes(value)
        if len(data) > self.max_payload_bytes:
            raise CheckpointError(f"{kind} payload exceeds maximum serialized size")
        digest = sha256_bytes(data)
        directory = self.progress_dir if kind == "progress" else self.partial_dir
        final = directory / f"{digest}.json"
        if final.exists():
            if final.read_bytes() != data:
                raise CheckpointError("existing hash-derived payload path has different bytes")
            return digest, data, final
        temp = _write_temp_fsync(final, data)
        try:
            # A same-hash file could have appeared since the existence check.  Never
            # overwrite an immutable payload without byte verification.
            if final.exists():
                if final.read_bytes() != data:
                    raise CheckpointError("concurrent hash path collision with different bytes")
                temp.unlink()
            else:
                os.replace(temp, final)
                _fsync_directory(directory)
        finally:
            if temp.exists():
                temp.unlink()
        return digest, data, final

    def publish_orphan_for_test(self, *, kind: str, value: Any) -> str:
        """Publish an immutable payload without a ledger commit; validation helper only."""
        if kind not in {"progress", "partial"}:
            raise CheckpointError("unknown payload kind")
        digest, _data, _path = self._publish_payload(kind, value)
        return digest

    def commit(
        self,
        *,
        progress: dict[str, Any],
        partial_evidence: dict[str, Any],
        last_complete_attempt_id: str,
        refresh_mirrors: bool = True,
    ) -> CommitRecord:
        if not isinstance(last_complete_attempt_id, str) or not last_complete_attempt_id:
            raise CheckpointError("last_complete_attempt_id must be nonempty string")
        if "frontier" not in progress:
            raise CheckpointError("progress payload must contain frontier")

        progress_sha, progress_bytes, _ = self._publish_payload("progress", progress)
        partial_sha, partial_bytes, _ = self._publish_payload("partial", partial_evidence)
        frontier_bytes = canonical_json_file_bytes(progress["frontier"])
        frontier_sha = sha256_bytes(frontier_bytes)

        sequence = len(self._records)
        previous = self._records[-1].checkpoint_sha256 if self._records else ZERO_SHA256
        obj = {
            "checkpoint_sequence": sequence,
            "frontier_digest_sha256": frontier_sha,
            "last_complete_attempt_id": last_complete_attempt_id,
            "partial_evidence_sha256": partial_sha,
            "previous_checkpoint_sha256": previous,
            "progress_payload_sha256": progress_sha,
            "schema": CHECKPOINT_LINE_SCHEMA,
            "status": "PARTIAL",
        }
        line = canonical_json_file_bytes(obj)
        checkpoint_sha = sha256_bytes(line)

        self.root.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.jsonl_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            offset = 0
            while offset < len(line):
                written = os.write(fd, line[offset:])
                if written <= 0:
                    raise CheckpointError("short JSONL checkpoint write")
                offset += written
            os.fsync(fd)
        finally:
            os.close(fd)
        _fsync_directory(self.root)

        mirror_ok = True
        if refresh_mirrors:
            try:
                atomic_replace_file(self.progress_mirror, progress_bytes)
                atomic_replace_file(self.partial_mirror, partial_bytes)
            except Exception:
                mirror_ok = False

        record = CommitRecord(
            sequence,
            checkpoint_sha,
            progress_sha,
            partial_sha,
            frontier_sha,
            last_complete_attempt_id,
            mirror_ok,
        )
        self._records.append(record)
        return record


def _validate_canonical_line(line: bytes) -> dict[str, Any]:
    if not line.endswith(b"\n"):
        raise CheckpointError("checkpoint line lacks LF")
    try:
        obj = json.loads(line[:-1].decode("utf-8"))
    except Exception as exc:
        raise CheckpointError("checkpoint JSON parse failure") from exc
    if canonical_json_file_bytes(obj) != line:
        raise CheckpointError("checkpoint JSON line is not canonical")
    if not isinstance(obj, dict):
        raise CheckpointError("checkpoint line must be object")
    expected = {
        "checkpoint_sequence",
        "frontier_digest_sha256",
        "last_complete_attempt_id",
        "partial_evidence_sha256",
        "previous_checkpoint_sha256",
        "progress_payload_sha256",
        "schema",
        "status",
    }
    if set(obj) != expected:
        raise CheckpointError("checkpoint line field set mismatch")
    if obj["schema"] != CHECKPOINT_LINE_SCHEMA or obj["status"] != "PARTIAL":
        raise CheckpointError("checkpoint line schema/status mismatch")
    return obj


def _read_payload(root: Path, kind: str, digest: str) -> tuple[dict[str, Any], bytes]:
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise CheckpointError("invalid payload digest text")
    path = root / "checkpoint_payloads" / kind / f"{digest}.json"
    if not path.is_file():
        raise CheckpointError("committed payload missing")
    data = path.read_bytes()
    if sha256_bytes(data) != digest:
        raise CheckpointError("committed payload digest mismatch")
    try:
        obj = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise CheckpointError("payload JSON parse failure") from exc
    if canonical_json_file_bytes(obj) != data:
        raise CheckpointError("payload bytes are not canonical")
    if not isinstance(obj, dict):
        raise CheckpointError("payload must be JSON object")
    return obj, data


def recover_committed(root: Path, *, allow_missing_ledger: bool = False) -> list[CommitRecord]:
    ledger = root / "SWEEP_PROGRESS.jsonl"
    if not ledger.exists():
        if allow_missing_ledger:
            return []
        raise CheckpointError("checkpoint ledger missing")
    raw = ledger.read_bytes()
    last_lf = raw.rfind(b"\n")
    if last_lf < 0:
        return []
    committed_prefix = raw[: last_lf + 1]
    lines = committed_prefix.splitlines(keepends=True)
    records: list[CommitRecord] = []
    previous = ZERO_SHA256
    for index, line in enumerate(lines):
        obj = _validate_canonical_line(line)
        if obj["checkpoint_sequence"] != index:
            raise CheckpointError("checkpoint sequence mismatch")
        if obj["previous_checkpoint_sha256"] != previous:
            raise CheckpointError("previous checkpoint hash mismatch")
        progress, _ = _read_payload(root, "progress", obj["progress_payload_sha256"])
        _partial, _ = _read_payload(root, "partial", obj["partial_evidence_sha256"])
        if "frontier" not in progress:
            raise CheckpointError("committed progress payload lacks frontier")
        frontier_sha = sha256_bytes(canonical_json_file_bytes(progress["frontier"]))
        if frontier_sha != obj["frontier_digest_sha256"]:
            raise CheckpointError("frontier digest mismatch")
        checkpoint_sha = sha256_bytes(line)
        record = CommitRecord(
            index,
            checkpoint_sha,
            obj["progress_payload_sha256"],
            obj["partial_evidence_sha256"],
            obj["frontier_digest_sha256"],
            obj["last_complete_attempt_id"],
            True,
        )
        records.append(record)
        previous = checkpoint_sha
    return records
