#!/usr/bin/env python3
"""Fail-closed file, archive, and imported-module provenance gates."""
from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any

from blocal_phase4_model import (
    STAGE1_CONCLUSION, STAGE1_SCOPE, STAGE1_STATEMENT,
    exact_keys, need, parse_canonical_json, sha256_bytes,
)


def repo_file(repository_root: Path, relative_path: str) -> Path:
    need(isinstance(relative_path, str) and relative_path
         and not relative_path.startswith("/")
         and ".." not in Path(relative_path).parts,
         "repository-relative path required")
    root = repository_root.resolve(strict=True)
    candidate = repository_root / relative_path
    need(not candidate.is_symlink(), f"symlink forbidden: {relative_path}")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"path escapes repository: {relative_path}") from exc
    need(resolved.is_file(), f"regular file required: {relative_path}")
    return resolved


def verify_file_pin(repository_root: Path, path_text: str, expected: str,
                    where: str) -> Path:
    path = repo_file(repository_root, path_text)
    need(sha256_bytes(path.read_bytes()) == expected, f"{where}: SHA-256 mismatch")
    return path


def verify_implementation_sources(repository_root: Path,
                                  implementation: dict[str, Any]) -> None:
    exact_keys(implementation, {"entrypoint_path", "sources_sha256"}, "implementation")
    pins = implementation["sources_sha256"]
    need(isinstance(pins, dict) and pins, "implementation source pins")
    need(implementation["entrypoint_path"] in pins, "entrypoint source pin")
    for relative_path, expected in pins.items():
        need(isinstance(expected, str) and len(expected) == 64, "source SHA-256")
        verify_file_pin(repository_root, relative_path, expected,
                        f"implementation source {relative_path}")


def load_pinned_module(repository_root: Path, pin: dict[str, Any],
                       module_name: str, required_callables: tuple[str, ...],
                       required_constants: dict[str, Any] | None = None) -> ModuleType:
    path = verify_file_pin(repository_root, pin["path"], pin["sha256"], module_name)
    before = path.read_bytes()
    need(sha256_bytes(before) == pin["sha256"], f"{module_name}: pre-import hash")
    need(module_name not in sys.modules, f"{module_name}: duplicate module name")
    spec = importlib.util.spec_from_file_location(module_name, path)
    need(spec is not None and spec.loader is not None, f"{module_name}: import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    origin = Path(module.__file__).resolve(strict=True)
    need(origin == path, f"{module_name}: imported origin mismatch")
    need(sha256_bytes(path.read_bytes()) == pin["sha256"],
         f"{module_name}: post-import hash")
    for name in required_callables:
        function = getattr(module, name, None)
        need(callable(function), f"{module_name}: missing callable {name}")
        need(getattr(function, "__module__", None) == module_name,
             f"{module_name}: foreign callable {name}")
    for name, expected in (required_constants or {}).items():
        need(getattr(module, name, None) == expected,
             f"{module_name}: constant {name}")
    return module


def verify_stage1_dependency(repository_root: Path,
                             stage1: dict[str, Any]) -> None:
    exact_keys(stage1, {
        "path", "source_head", "certificate_sha256", "manifest_path",
        "manifest_sha256", "config_path", "config_sha256", "artifact_path",
        "artifact_zip_sha256", "certified_statement", "machine_conclusion",
        "scope", "status",
    }, "stage1_dependency")
    need(stage1["status"] == "STAGE1_CONTENT_AUDITED", "Stage-1 status")
    need(stage1["certified_statement"] == STAGE1_STATEMENT, "Stage-1 statement")
    need(stage1["machine_conclusion"] == STAGE1_CONCLUSION, "Stage-1 conclusion")
    need(stage1["scope"] == STAGE1_SCOPE, "Stage-1 scope")
    descriptor = verify_file_pin(repository_root, stage1["config_path"],
                                 stage1["config_sha256"], "Stage-1 descriptor")
    descriptor_raw = descriptor.read_bytes()
    descriptor_obj = parse_canonical_json(descriptor_raw)
    need(descriptor_obj.get("schema") == "blocal-stage1-dependency-config-v1",
         "Stage-1 descriptor schema")
    need(descriptor_obj.get("descriptor_path") == stage1["config_path"],
         "Stage-1 descriptor path")
    expected = {
        "source_head": stage1["source_head"],
        "certificate_path": stage1["path"],
        "certificate_sha256": stage1["certificate_sha256"],
        "inner_manifest_path": stage1["manifest_path"],
        "inner_manifest_sha256": stage1["manifest_sha256"],
        "content_audit_status": stage1["status"],
        "certificate_conclusion": STAGE1_CONCLUSION,
    }
    for key, value in expected.items():
        need(descriptor_obj.get(key) == value, f"Stage-1 descriptor {key}")
    archive = verify_file_pin(repository_root, stage1["artifact_path"],
                              stage1["artifact_zip_sha256"], "Stage-1 archive")
    with zipfile.ZipFile(archive) as bundle:
        need(bundle.testzip() is None, "Stage-1 archive CRC")
        need(bundle.comment == b"", "Stage-1 archive comment")
        names = bundle.namelist()
        need(names == sorted(names), "Stage-1 archive order")
        need(names == descriptor_obj.get("archive_members"),
             "Stage-1 archive allowlist")
        need(not any("UNVERIFIED_PROVENANCE" in name for name in names),
             "Stage-1 provenance mixing")
        for info in bundle.infolist():
            need(not info.is_dir(), f"Stage-1 directory entry: {info.filename}")
            need(info.date_time == (1980, 1, 1, 0, 0, 0),
                 f"Stage-1 timestamp: {info.filename}")
            need(info.compress_type == zipfile.ZIP_DEFLATED,
                 f"Stage-1 compression: {info.filename}")
            need(info.extra == b"" and info.comment == b"",
                 f"Stage-1 metadata: {info.filename}")
            need((info.external_attr >> 16) & 0o177777 == 0o100644,
                 f"Stage-1 permissions: {info.filename}")
        need(bundle.read("config.blocal-stage1.json") == descriptor_raw,
             "Stage-1 descriptor member")
        payload = descriptor_obj.get("payload_sha256")
        need(isinstance(payload, dict) and len(payload) == 8,
             "Stage-1 payload hashes")
        need(set(payload).issubset(names), "Stage-1 payload allowlist")
        for name, digest in payload.items():
            need(sha256_bytes(bundle.read(name)) == digest,
                 f"Stage-1 member hash: {name}")
