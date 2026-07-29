from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from .canonical import ContractReject, canonical_json_bytes
from .enums import CheckerFailureReason


CHAIN_DOMAIN = b"SWEEP_RUN_CONFIG_V1\x00"
RECORD_DOMAIN = b"ITEM3_SWEEP_RECORD_V1\x00"


def chain_genesis(config_sha256: str) -> str:
    try:
        raw = bytes.fromhex(config_sha256)
    except ValueError as exc:
        raise ContractReject(
            CheckerFailureReason.CHAIN_VIOLATION,
            "invalid config SHA-256",
        ) from exc
    if len(raw) != 32:
        raise ContractReject(
            CheckerFailureReason.CHAIN_VIOLATION,
            "invalid config SHA-256 length",
        )
    return hashlib.sha256(CHAIN_DOMAIN + raw).hexdigest()


def chain_record(previous_hash: str, record: dict) -> str:
    try:
        previous = bytes.fromhex(previous_hash)
    except ValueError as exc:
        raise ContractReject(
            CheckerFailureReason.CHAIN_VIOLATION,
            "invalid previous chain hash",
        ) from exc
    if len(previous) != 32:
        raise ContractReject(
            CheckerFailureReason.CHAIN_VIOLATION,
            "invalid previous chain hash length",
        )
    return hashlib.sha256(RECORD_DOMAIN + previous + canonical_json_bytes(record)).hexdigest()


def verify_chain(config_sha256: str, records: Iterable[dict], expected_final_hash: str) -> None:
    current = chain_genesis(config_sha256)
    for record in records:
        current = chain_record(current, record)
    if current != expected_final_hash:
        raise ContractReject(
            CheckerFailureReason.CHAIN_VIOLATION,
            "record chain final hash mismatch",
        )
