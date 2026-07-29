from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .canonical import (
    ContractReject,
    canonical_json_bytes,
    sha256_hex,
    validate_id,
    validate_sha256,
)
from .enums import CheckerFailureReason
from .schema import REQUIRED_DEPENDENCIES, ValidatedConfig


@dataclass(frozen=True)
class IdentityEvidence:
    pilot_run_id: int
    pilot_source_sha256: str
    pilot_kernel_source_sha256: str
    dependency_snapshot_sha256: str
    root_interval_endpoints: tuple[Fraction, Fraction]


def verify_pilot_identity(
    *,
    config: ValidatedConfig,
    receipt: dict[str, Any],
    snapshot: dict[str, Any],
    receipt_bytes: bytes,
    snapshot_bytes: bytes,
) -> IdentityEvidence:
    raw = config.raw
    if sha256_hex(receipt_bytes) != raw["cg_pilot_receipt_sha256"]:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "pilot receipt hash mismatch",
        )
    if sha256_hex(snapshot_bytes) != raw["dependency_snapshot_sha256"]:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "dependency snapshot hash mismatch",
        )
    if receipt.get("run_id") != 30334858060 or snapshot.get("pilot_run_id") != 30334858060:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "pilot run id mismatch",
        )
    for key, config_field in [
        ("pilot_source_sha256", "cg_pilot_source_sha256"),
        ("pilot_kernel_source_sha256", "cg_pilot_kernel_source_sha256"),
    ]:
        if receipt.get(key) != raw[config_field] or snapshot.get(key) != raw[config_field]:
            raise ContractReject(
                CheckerFailureReason.PILOT_IDENTITY_FAIL,
                f"pilot identity relation mismatch: {key}",
            )
    if raw["kernel_source_sha256"] != raw["cg_pilot_kernel_source_sha256"]:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "current kernel does not equal pilot kernel",
        )
    certified_lambda = snapshot.get("certified_lambda")
    if certified_lambda != {"p": "118", "q": "25"}:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "snapshot certified lambda mismatch",
        )
    interval = snapshot.get("certified_root_interval")
    if not isinstance(interval, dict):
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "snapshot certified root interval missing",
        )
    lower = interval.get("lower_endpoint")
    upper = interval.get("upper_endpoint")
    if lower != {"p": "1", "q": "64"} or upper != {"p": "11", "q": "256"}:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "root interval endpoint bytes mismatch",
        )
    if "dependency_snapshot_sha256" in receipt and receipt["dependency_snapshot_sha256"] != raw["dependency_snapshot_sha256"]:
        raise ContractReject(
            CheckerFailureReason.PILOT_IDENTITY_FAIL,
            "receipt/snapshot relation mismatch",
        )
    return IdentityEvidence(
        pilot_run_id=30334858060,
        pilot_source_sha256=raw["cg_pilot_source_sha256"],
        pilot_kernel_source_sha256=raw["cg_pilot_kernel_source_sha256"],
        dependency_snapshot_sha256=raw["dependency_snapshot_sha256"],
        root_interval_endpoints=(Fraction(1, 64), Fraction(11, 256)),
    )


def verify_logical_dependencies(
    *,
    config: ValidatedConfig,
    snapshot: dict[str, Any],
) -> None:
    records = snapshot.get("logical_dependencies")
    if not isinstance(records, dict) or set(records) != REQUIRED_DEPENDENCIES:
        raise ContractReject(
            CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
            "snapshot logical dependency key set mismatch",
        )
    configured = config.raw["sweep_logical_dependencies"]
    for lemma_id in REQUIRED_DEPENDENCIES:
        record = records[lemma_id]
        if not isinstance(record, dict) or record.get("lemma_id") != lemma_id:
            raise ContractReject(
                CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                f"snapshot lemma record mismatch: {lemma_id}",
            )
        expected = configured[lemma_id]
        if sha256_hex(canonical_json_bytes(record)) != expected["dependency_entry_sha256"]:
            raise ContractReject(
                CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                f"dependency entry hash mismatch: {lemma_id}",
            )
        if record.get("allowlist_id") != expected["expected_allowlist_id"]:
            raise ContractReject(
                CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                f"dependency allowlist mismatch: {lemma_id}",
            )
        if record.get("supports_machine_conclusion") is not True:
            raise ContractReject(
                CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                f"dependency does not support machine conclusion: {lemma_id}",
            )
