from __future__ import annotations

import hashlib
import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from .canonical import ContractReject, git_blob_sha1, sha256_hex
from .enums import CheckerFailureReason


@dataclass(frozen=True)
class SourcePin:
    repo_relative_path: str
    sha256: str


@dataclass(frozen=True)
class SourceIdentity:
    resolved_path: Path
    pre_import_sha256: str
    post_import_sha256: str
    module_origin: Path


class PinnedSourceLoader:
    def __init__(self, checkout_root: Path) -> None:
        self.checkout_root = checkout_root.resolve(strict=True)

    def _resolve_contained(self, relative_path: str) -> Path:
        try:
            candidate = (self.checkout_root / relative_path).resolve(strict=True)
        except FileNotFoundError as exc:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "source path does not resolve inside checkout",
            ) from exc
        try:
            candidate.relative_to(self.checkout_root)
        except ValueError as exc:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "source path escapes checkout root",
            ) from exc
        return candidate

    def verify_bytes(self, pin: SourcePin) -> SourceIdentity:
        path = self._resolve_contained(pin.repo_relative_path)
        before = sha256_hex(path.read_bytes())
        if before != pin.sha256:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "pre-import source hash mismatch",
            )
        return SourceIdentity(path, before, before, path)

    def load_module(self, module_name: str, pin: SourcePin) -> tuple[ModuleType, SourceIdentity]:
        path = self._resolve_contained(pin.repo_relative_path)
        before = sha256_hex(path.read_bytes())
        if before != pin.sha256:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "pre-import source hash mismatch",
            )
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "unable to construct module spec",
            )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        origin = Path(module.__spec__.origin or "").resolve(strict=True)
        if origin != path:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "module origin mismatch",
            )
        after = sha256_hex(path.read_bytes())
        if after != before:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "source changed during import",
            )
        return module, SourceIdentity(path, before, after, origin)


def verify_frozen_design_blob(path: Path, expected_blob_sha1: str) -> None:
    actual = git_blob_sha1(path.read_bytes())
    if actual != expected_blob_sha1:
        raise ContractReject(
            CheckerFailureReason.SOURCE_IDENTITY_FAIL,
            f"frozen design blob mismatch: {actual}",
        )
