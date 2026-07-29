#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping

ARTIFACT_ID = 8680673043
PILOT_RUN_ID = 30334858060
ARTIFACT_SHA256 = "c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381"
PILOT_SOURCE_MEMBER = "c_g_tube_pilot.py"
PILOT_SOURCE_SHA256 = "9da05b2c44119c9937c19a2184ea9722de7876442235896f1f0e0dbc076f2ecc"
MANIFEST_MEMBER = "SHA256SUMS.txt"
REQUIRED_MEMBERS = frozenset({
    "CONTROLS.json",
    "C_G_ENDPOINT_SIGNS.json",
    "C_G_IDENTITY_CROSSCHECK.json",
    "C_G_TUBE_PILOT.json",
    "DEPENDENCIES.json",
    "README.md",
    MANIFEST_MEMBER,
    "c_g_tube_checker.py",
    PILOT_SOURCE_MEMBER,
    "cells_chain.jsonl",
    "config.json",
    "endpoints_chain.jsonl",
    "gen_manifest.py",
    "run_controls.py",
    "spots_chain.jsonl",
})
_SHA_LINE = re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)")


class PilotArtifactReject(RuntimeError):
    pass


@dataclass(frozen=True)
class PilotArtifactEvidence:
    artifact_id: int
    artifact_sha256: str
    pilot_run_id: int
    pilot_source_sha256: str
    member_count: int
    manifest_entry_count: int

    def to_object(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_sha256": self.artifact_sha256,
            "internal_manifest_member": MANIFEST_MEMBER,
            "manifest_entry_count": self.manifest_entry_count,
            "member_count": self.member_count,
            "pilot_run_id": self.pilot_run_id,
            "pilot_source_member": PILOT_SOURCE_MEMBER,
            "pilot_source_sha256": self.pilot_source_sha256,
            "schema": "ITEM3_CG_PILOT_ARTIFACT_REDERIVATION_V1",
            "source_hash_rederived_from_member_bytes": True,
            "source_hash_rederived_from_internal_manifest": True,
            "verdict": "PASS",
        }


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _validate_member_name(name: str) -> str:
    if not name or "\\" in name or name.startswith("/"):
        raise PilotArtifactReject(f"unsafe ZIP member name: {name!r}")
    path = PurePosixPath(name)
    if len(path.parts) != 1 or any(part in {"", ".", ".."} for part in path.parts):
        raise PilotArtifactReject(f"non-flat or unsafe ZIP member name: {name!r}")
    return name


def _parse_manifest(raw: bytes) -> dict[str, str]:
    if b"\r" in raw or not raw.endswith(b"\n"):
        raise PilotArtifactReject("internal SHA256SUMS.txt must use LF and final LF")
    result: dict[str, str] = {}
    for line in raw.decode("ascii").splitlines():
        match = _SHA_LINE.fullmatch(line)
        if match is None:
            raise PilotArtifactReject(f"invalid internal manifest line: {line!r}")
        digest, name = match.groups()
        _validate_member_name(name)
        if name in result:
            raise PilotArtifactReject(f"duplicate internal manifest member: {name}")
        result[name] = digest
    return result


def _read_zip(zip_path: Path) -> tuple[dict[str, bytes], bytes]:
    zip_raw = zip_path.read_bytes()
    if sha256_bytes(zip_raw) != ARTIFACT_SHA256:
        raise PilotArtifactReject("pilot artifact ZIP SHA-256 mismatch")
    with zipfile.ZipFile(zip_path) as archive:
        infos = archive.infolist()
        names = [_validate_member_name(info.filename) for info in infos]
        if len(names) != len(set(names)):
            raise PilotArtifactReject("duplicate ZIP member name")
        if any(info.is_dir() for info in infos):
            raise PilotArtifactReject("directories are forbidden in canonical pilot artifact")
        if set(names) != REQUIRED_MEMBERS:
            missing = sorted(REQUIRED_MEMBERS - set(names))
            unknown = sorted(set(names) - REQUIRED_MEMBERS)
            raise PilotArtifactReject(f"pilot member set mismatch: missing={missing}, unknown={unknown}")
        members = {name: archive.read(name) for name in names}
    return members, zip_raw


def _verify_extracted_directory(directory: Path, members: Mapping[str, bytes]) -> None:
    actual = {path.name for path in directory.iterdir() if path.is_file()}
    if actual != REQUIRED_MEMBERS:
        raise PilotArtifactReject("extracted pilot member set mismatch")
    if any(path.is_dir() or path.is_symlink() for path in directory.iterdir()):
        raise PilotArtifactReject("extracted pilot directory must contain regular files only")
    for name, raw in members.items():
        path = directory / name
        if not path.is_file() or path.is_symlink() or path.read_bytes() != raw:
            raise PilotArtifactReject(f"ZIP/extracted byte mismatch: {name}")


def verify_artifact(*, zip_path: Path, extracted_dir: Path | None = None) -> PilotArtifactEvidence:
    members, _ = _read_zip(zip_path)
    manifest = _parse_manifest(members[MANIFEST_MEMBER])
    expected_manifest_names = REQUIRED_MEMBERS - {MANIFEST_MEMBER}
    if set(manifest) != expected_manifest_names:
        raise PilotArtifactReject("internal manifest member set mismatch")
    for name in sorted(expected_manifest_names):
        actual = sha256_bytes(members[name])
        if manifest[name] != actual:
            raise PilotArtifactReject(f"internal manifest hash mismatch: {name}")
    source_actual = sha256_bytes(members[PILOT_SOURCE_MEMBER])
    if source_actual != PILOT_SOURCE_SHA256:
        raise PilotArtifactReject("pilot source member SHA-256 mismatch")
    if manifest[PILOT_SOURCE_MEMBER] != PILOT_SOURCE_SHA256:
        raise PilotArtifactReject("pilot source internal-manifest SHA-256 mismatch")
    if extracted_dir is not None:
        _verify_extracted_directory(extracted_dir, members)
    return PilotArtifactEvidence(
        artifact_id=ARTIFACT_ID,
        artifact_sha256=ARTIFACT_SHA256,
        pilot_run_id=PILOT_RUN_ID,
        pilot_source_sha256=PILOT_SOURCE_SHA256,
        member_count=len(members),
        manifest_entry_count=len(manifest),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    evidence = verify_artifact(zip_path=args.artifact_zip, extracted_dir=args.artifact_dir)
    raw = canonical_json_bytes(evidence.to_object())
    if args.write_report is not None:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_bytes(raw)
    print(raw.decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
