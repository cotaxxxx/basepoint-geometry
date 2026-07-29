from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .canonical import (
    ContractReject,
    canonical_json_bytes,
    git_blob_sha1,
    parse_canonical_json,
    sha256_hex,
)
from .enums import CheckerFailureReason
from .identity import IdentityEvidence, verify_logical_dependencies, verify_pilot_identity
from .provenance import PinnedSourceLoader, SourceIdentity, SourcePin
from .schema import ConfigValidator, ValidatedConfig


@dataclass(frozen=True)
class PreflightResult:
    config: ValidatedConfig
    config_sha256: str
    design_blob_sha1: str
    source_identities: tuple[SourceIdentity, ...]
    pilot_identity: IdentityEvidence


class PreflightVerifier:
    def __init__(
        self,
        *,
        checkout_root: Path,
        expected_design_blob_sha1: str,
        symlink_escape_prefixes: Iterable[str] = (),
    ) -> None:
        self.checkout_root = checkout_root
        self.expected_design_blob_sha1 = expected_design_blob_sha1
        self.config_validator = ConfigValidator(
            symlink_escape_prefixes=symlink_escape_prefixes
        )
        self.source_loader = PinnedSourceLoader(checkout_root)

    def verify(
        self,
        *,
        config_bytes: bytes,
        stored_config_sha256: str,
        receipt_bytes: bytes,
        snapshot_bytes: bytes,
    ) -> PreflightResult:
        config_obj = parse_canonical_json(config_bytes)
        config = self.config_validator.validate(config_obj)
        config_sha = sha256_hex(canonical_json_bytes(config.raw))
        if config_sha != stored_config_sha256:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "complete run config SHA-256 mismatch",
            )

        design_path = self.checkout_root / config.raw["sweep_design_path"]
        design_bytes = design_path.read_bytes()
        if sha256_hex(design_bytes) != config.raw["sweep_design_sha256"]:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "design SHA-256 mismatch",
            )
        design_blob = git_blob_sha1(design_bytes)
        if design_blob != self.expected_design_blob_sha1:
            raise ContractReject(
                CheckerFailureReason.SOURCE_IDENTITY_FAIL,
                "frozen design blob mismatch",
            )

        pins = [
            SourcePin(config.raw["runner_source_path"], config.raw["runner_source_sha256"]),
            SourcePin(config.raw["checker_source_path"], config.raw["checker_source_sha256"]),
            SourcePin(config.raw["r_tile_source_path"], config.raw["r_tile_source_sha256"]),
            SourcePin(config.raw["kernel_source_path"], config.raw["kernel_source_sha256"]),
            SourcePin(config.raw["adapter_source_path"], config.raw["adapter_sha256"]),
        ]
        identities = tuple(self.source_loader.verify_bytes(pin) for pin in pins)
        receipt = parse_canonical_json(receipt_bytes)
        snapshot = parse_canonical_json(snapshot_bytes)
        identity = verify_pilot_identity(
            config=config,
            receipt=receipt,
            snapshot=snapshot,
            receipt_bytes=receipt_bytes,
            snapshot_bytes=snapshot_bytes,
        )
        verify_logical_dependencies(config=config, snapshot=snapshot)
        return PreflightResult(
            config=config,
            config_sha256=config_sha,
            design_blob_sha1=design_blob,
            source_identities=identities,
            pilot_identity=identity,
        )
