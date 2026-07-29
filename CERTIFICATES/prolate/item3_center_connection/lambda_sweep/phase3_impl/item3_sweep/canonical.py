from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import PurePosixPath
from typing import Any, Iterable

from .enums import CheckerFailureReason


class ContractReject(ValueError):
    def __init__(self, reason: CheckerFailureReason, message: str):
        super().__init__(message)
        self.reason = reason


def _pairs_no_duplicates(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"duplicate JSON key: {key}",
            )
        result[key] = value
    return result


def canonical_json_bytes(value: Any) -> bytes:
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str) or not key.isascii():
                    raise ContractReject(
                        CheckerFailureReason.NONCANONICAL_ARTIFACT,
                        "JSON keys must be ASCII strings",
                    )
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, float):
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                "floats are forbidden in exact artifacts",
            )

    walk(value)
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def parse_canonical_json(raw: bytes) -> Any:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw or b"\n" in raw:
        raise ContractReject(
            CheckerFailureReason.NONCANONICAL_ARTIFACT,
            "BOM/CR/LF forbidden in canonical JSON object bytes",
        )
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ContractReject(
                    CheckerFailureReason.NONCANONICAL_ARTIFACT,
                    f"non-finite token: {token}",
                )
            ),
        )
    except ContractReject:
        raise
    except Exception as exc:
        raise ContractReject(
            CheckerFailureReason.NONCANONICAL_ARTIFACT,
            "invalid canonical JSON",
        ) from exc
    if canonical_json_bytes(value) != raw:
        raise ContractReject(
            CheckerFailureReason.NONCANONICAL_ARTIFACT,
            "JSON bytes are not canonical",
        )
    return value


def parse_canonical_jsonl(raw: bytes) -> list[Any]:
    if b"\r" in raw or raw.endswith(b"\n"):
        raise ContractReject(
            CheckerFailureReason.NONCANONICAL_ARTIFACT,
            "canonical JSONL forbids CR and final LF",
        )
    if not raw:
        return []
    return [parse_canonical_json(line) for line in raw.split(b"\n")]


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


_INTEGER_RE = re.compile(r"0|-?[1-9][0-9]*")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_ID_RE = re.compile(r"[A-Za-z0-9._:-]+")


def require_integer_string(value: Any, field: str) -> int:
    if not isinstance(value, str) or not _INTEGER_RE.fullmatch(value):
        raise ContractReject(
            CheckerFailureReason.NONCANONICAL_ARTIFACT,
            f"{field}: noncanonical integer string",
        )
    return int(value)


@dataclass(frozen=True, order=True)
class CanonicalRational:
    value: Fraction

    @classmethod
    def from_object(cls, obj: Any, field: str = "rational") -> "CanonicalRational":
        if not isinstance(obj, dict) or set(obj) != {"p", "q"}:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                f"{field}: expected {{p,q}}",
            )
        p = require_integer_string(obj["p"], f"{field}.p")
        q = require_integer_string(obj["q"], f"{field}.q")
        if q <= 0:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"{field}: denominator must be positive",
            )
        value = Fraction(p, q)
        if value.numerator != p or value.denominator != q:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"{field}: fraction not reduced",
            )
        return cls(value)

    @classmethod
    def of(cls, p: int, q: int = 1) -> "CanonicalRational":
        return cls(Fraction(p, q))

    def to_object(self) -> dict[str, str]:
        return {"p": str(self.value.numerator), "q": str(self.value.denominator)}

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_object())


@dataclass(frozen=True, order=True)
class CanonicalDyadic:
    value: Fraction

    @classmethod
    def from_object(cls, obj: Any, field: str = "dyadic") -> "CanonicalDyadic":
        if not isinstance(obj, dict) or set(obj) != {"m", "e"}:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                f"{field}: expected {{m,e}}",
            )
        m = require_integer_string(obj["m"], f"{field}.m")
        e = obj["e"]
        if not isinstance(e, int) or isinstance(e, bool) or e < 0:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"{field}: exponent must be nonnegative integer",
            )
        if m == 0 and e != 0:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"{field}: zero must use exponent 0",
            )
        if m != 0 and e > 0 and m % 2 == 0:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                f"{field}: dyadic is not reduced",
            )
        return cls(Fraction(m, 1 << e))

    @classmethod
    def of(cls, m: int, e: int = 0) -> "CanonicalDyadic":
        if e < 0:
            raise ValueError("negative exponent")
        value = Fraction(m, 1 << e)
        return cls(value)

    def to_object(self) -> dict[str, Any]:
        numerator = self.value.numerator
        denominator = self.value.denominator
        if denominator & (denominator - 1):
            raise ValueError("value is not dyadic")
        exponent = denominator.bit_length() - 1
        if numerator == 0:
            exponent = 0
        return {"m": str(numerator), "e": exponent}

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_object())


def validate_sha256(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ContractReject(
            CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
            f"{field}: expected 64 lowercase hex",
        )
    return value


def validate_id(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ContractReject(
            CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
            f"{field}: invalid ID",
        )
    return value


def validate_repo_relative_path(
    value: Any,
    field: str,
    *,
    symlink_escape_prefixes: Iterable[str] = (),
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or value.startswith("/")
        or value.endswith("/")
        or "//" in value
        or "\x00" in value
    ):
        raise ContractReject(
            CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
            f"{field}: invalid repository-relative path",
        )
    components = value.split("/")
    if any(part in {"", ".", ".."} for part in components):
        raise ContractReject(
            CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
            f"{field}: non-normal path component",
        )
    if str(PurePosixPath(value)) != value:
        raise ContractReject(
            CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
            f"{field}: path not normalized",
        )
    for prefix in symlink_escape_prefixes:
        if value == prefix or value.startswith(prefix + "/"):
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                f"{field}: symlink escape",
            )
    return value
