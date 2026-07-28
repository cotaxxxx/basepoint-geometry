#!/usr/bin/env python3
"""Exact numeric and canonical-byte primitives for B-TUBE v2.1 self-tests.

The proof path is binary/rational only.  Human-readable decimal fields are
non-normative and are never consumed by the mathematical checker.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from typing import Any, Protocol


class SchemaError(ValueError):
    pass


class CanonicalBytesError(SchemaError):
    pass


def _require_int_string(value: Any, where: str) -> int:
    if not isinstance(value, str):
        raise SchemaError(f"{where}: expected integer string")
    if value in {"", "+", "-"}:
        raise SchemaError(f"{where}: invalid integer string")
    if value[0] == "+":
        raise SchemaError(f"{where}: leading plus forbidden")
    body = value[1:] if value.startswith("-") else value
    if not body.isascii() or not body.isdigit():
        raise SchemaError(f"{where}: invalid integer string")
    if len(body) > 1 and body.startswith("0"):
        raise SchemaError(f"{where}: leading zeros forbidden")
    if value == "-0":
        raise SchemaError(f"{where}: negative zero forbidden")
    return int(value)


@dataclass(frozen=True)
class Dyadic:
    """Canonical value m * 2**(-e), with e >= 0."""

    m: int
    e: int

    def __post_init__(self) -> None:
        if not isinstance(self.m, int) or isinstance(self.m, bool):
            raise SchemaError("dyadic mantissa must be int")
        if not isinstance(self.e, int) or isinstance(self.e, bool) or self.e < 0:
            raise SchemaError("dyadic exponent must be a nonnegative int")
        if self.m == 0 and self.e != 0:
            raise SchemaError("zero dyadic must have exponent 0")
        if self.m != 0 and self.e > 0 and self.m % 2 == 0:
            raise SchemaError("nonzero dyadic mantissa must be odd when e > 0")

    @classmethod
    def canonical(cls, m: int, e: int) -> "Dyadic":
        if not isinstance(m, int) or isinstance(m, bool):
            raise SchemaError("dyadic mantissa must be int")
        if not isinstance(e, int) or isinstance(e, bool) or e < 0:
            raise SchemaError("dyadic exponent must be a nonnegative int")
        if m == 0:
            return cls(0, 0)
        while e > 0 and m % 2 == 0:
            m //= 2
            e -= 1
        return cls(m, e)

    @classmethod
    def from_man_exp(cls, mantissa: int, binary_exponent: int) -> "Dyadic":
        """Convert exact mantissa * 2**binary_exponent without rounding."""
        if not isinstance(mantissa, int) or isinstance(mantissa, bool):
            raise SchemaError("man_exp mantissa must be int")
        if not isinstance(binary_exponent, int) or isinstance(binary_exponent, bool):
            raise SchemaError("man_exp exponent must be int")
        if binary_exponent >= 0:
            return cls.canonical(mantissa << binary_exponent, 0)
        return cls.canonical(mantissa, -binary_exponent)

    @classmethod
    def from_fraction(cls, value: Fraction) -> "Dyadic":
        den = value.denominator
        if den <= 0 or den & (den - 1):
            raise SchemaError("fraction is not dyadic")
        return cls.canonical(value.numerator, den.bit_length() - 1)

    @classmethod
    def from_json(cls, obj: Any, where: str = "dyadic") -> "Dyadic":
        if not isinstance(obj, dict) or set(obj) != {"m", "e"}:
            raise SchemaError(f"{where}: expected exactly m,e")
        m = _require_int_string(obj["m"], f"{where}.m")
        e = obj["e"]
        if not isinstance(e, int) or isinstance(e, bool):
            raise SchemaError(f"{where}.e: expected integer")
        return cls(m, e)

    def to_json(self) -> dict[str, Any]:
        return {"m": str(self.m), "e": self.e}

    def as_fraction(self) -> Fraction:
        return Fraction(self.m, 1 << self.e)

    def _binary(self, other: "Dyadic", sign: int) -> "Dyadic":
        if not isinstance(other, Dyadic):
            return NotImplemented
        exponent = max(self.e, other.e)
        left = self.m << (exponent - self.e)
        right = other.m << (exponent - other.e)
        return Dyadic.canonical(left + sign * right, exponent)

    def __add__(self, other: "Dyadic") -> "Dyadic":
        return self._binary(other, 1)

    def __sub__(self, other: "Dyadic") -> "Dyadic":
        return self._binary(other, -1)

    def __neg__(self) -> "Dyadic":
        return Dyadic.canonical(-self.m, self.e)

    def __mul__(self, other: "Dyadic") -> "Dyadic":
        if not isinstance(other, Dyadic):
            return NotImplemented
        return Dyadic.canonical(self.m * other.m, self.e + other.e)

    def reciprocal(self) -> "Dyadic":
        if self.m == 0:
            raise ZeroDivisionError("zero dyadic")
        absolute = abs(self.m)
        if absolute & (absolute - 1):
            raise SchemaError("reciprocal is not dyadic")
        power = absolute.bit_length() - 1
        sign = -1 if self.m < 0 else 1
        return Dyadic.canonical(sign << self.e, power)

    def __truediv__(self, other: "Dyadic") -> "Dyadic":
        return self * other.reciprocal()

    def compare(self, other: "Dyadic") -> int:
        exponent = max(self.e, other.e)
        left = self.m << (exponent - self.e)
        right = other.m << (exponent - other.e)
        return (left > right) - (left < right)

    def __lt__(self, other: "Dyadic") -> bool:
        return self.compare(other) < 0

    def __le__(self, other: "Dyadic") -> bool:
        return self.compare(other) <= 0

    def midpoint(self, other: "Dyadic") -> "Dyadic":
        return (self + other) * Dyadic(1, 1)


D_ZERO = Dyadic(0, 0)
D_ONE = Dyadic(1, 0)
D_NEG_ONE = Dyadic(-1, 0)


@dataclass(frozen=True)
class DyadicInterval:
    lo: Dyadic
    hi: Dyadic

    def __post_init__(self) -> None:
        if self.hi < self.lo:
            raise SchemaError("interval endpoints reversed")

    @classmethod
    def point(cls, value: Dyadic) -> "DyadicInterval":
        return cls(value, value)

    @classmethod
    def from_json(cls, obj: Any, where: str = "interval") -> "DyadicInterval":
        if not isinstance(obj, dict) or set(obj) != {"lo", "hi"}:
            raise SchemaError(f"{where}: expected exactly lo,hi")
        return cls(
            Dyadic.from_json(obj["lo"], f"{where}.lo"),
            Dyadic.from_json(obj["hi"], f"{where}.hi"),
        )

    def to_json(self) -> dict[str, Any]:
        return {"lo": self.lo.to_json(), "hi": self.hi.to_json()}

    def contains(self, other: "DyadicInterval") -> bool:
        return self.lo <= other.lo and other.hi <= self.hi

    def strictly_contains(self, other: "DyadicInterval") -> bool:
        return self.lo < other.lo and other.hi < self.hi

    def positive_width(self) -> bool:
        return self.lo < self.hi

    def midpoint(self) -> Dyadic:
        return self.lo.midpoint(self.hi)

    def intersection(self, other: "DyadicInterval") -> "DyadicInterval | None":
        lo = self.lo if other.lo < self.lo else other.lo
        hi = self.hi if self.hi < other.hi else other.hi
        if hi < lo:
            return None
        return DyadicInterval(lo, hi)

    @classmethod
    def hull(cls, values: list[Dyadic]) -> "DyadicInterval":
        if not values:
            raise SchemaError("empty hull")
        lo = values[0]
        hi = values[0]
        for value in values[1:]:
            if value < lo:
                lo = value
            if hi < value:
                hi = value
        return cls(lo, hi)

    def __add__(self, other: "DyadicInterval") -> "DyadicInterval":
        return DyadicInterval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other: "DyadicInterval") -> "DyadicInterval":
        return DyadicInterval(self.lo - other.hi, self.hi - other.lo)

    def __neg__(self) -> "DyadicInterval":
        return DyadicInterval(-self.hi, -self.lo)

    def __mul__(self, other: "DyadicInterval") -> "DyadicInterval":
        products = [
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        ]
        return DyadicInterval.hull(products)

    def div_dyadic(self, value: Dyadic) -> "DyadicInterval":
        reciprocal = value.reciprocal()
        return self * DyadicInterval.point(reciprocal)


@dataclass(frozen=True)
class Rational:
    p: int
    q: int

    def __post_init__(self) -> None:
        if not isinstance(self.p, int) or isinstance(self.p, bool):
            raise SchemaError("rational numerator must be int")
        if not isinstance(self.q, int) or isinstance(self.q, bool) or self.q <= 0:
            raise SchemaError("rational denominator must be positive int")
        if Fraction(self.p, self.q).numerator != self.p or Fraction(self.p, self.q).denominator != self.q:
            raise SchemaError("rational must be reduced")

    @classmethod
    def from_json(cls, obj: Any, where: str = "rational") -> "Rational":
        if not isinstance(obj, dict) or set(obj) != {"p", "q"}:
            raise SchemaError(f"{where}: expected exactly p,q")
        return cls(
            _require_int_string(obj["p"], f"{where}.p"),
            _require_int_string(obj["q"], f"{where}.q"),
        )

    @classmethod
    def from_fraction(cls, value: Fraction) -> "Rational":
        return cls(value.numerator, value.denominator)

    def to_json(self) -> dict[str, str]:
        return {"p": str(self.p), "q": str(self.q)}

    def as_fraction(self) -> Fraction:
        return Fraction(self.p, self.q)

    def __lt__(self, other: "Rational") -> bool:
        return self.as_fraction() < other.as_fraction()

    def __le__(self, other: "Rational") -> bool:
        return self.as_fraction() <= other.as_fraction()


class ManExpProvider(Protocol):
    def man_exp(self) -> tuple[Any, Any]: ...


class ArbBallProvider(Protocol):
    def mid(self) -> ManExpProvider: ...
    def rad(self) -> ManExpProvider: ...


def exact_man_exp(value: ManExpProvider, where: str) -> Dyadic:
    """Extract exact binary components through man_exp; no text or rounding path."""
    try:
        mantissa_raw, exponent_raw = value.man_exp()
        mantissa = int(mantissa_raw)
        exponent = int(exponent_raw)
    except (TypeError, ValueError, OverflowError) as exc:
        raise SchemaError(f"{where}: nonfinite or invalid binary value") from exc
    return Dyadic.from_man_exp(mantissa, exponent)


def arb_ball_to_exact_interval(ball: ArbBallProvider) -> DyadicInterval:
    """Return exact endpoints of the stored midpoint +/- stored radius ball."""
    midpoint = exact_man_exp(ball.mid(), "arb.mid")
    radius = exact_man_exp(ball.rad(), "arb.rad")
    if radius < D_ZERO:
        raise SchemaError("arb.rad: negative radius")
    return DyadicInterval(midpoint - radius, midpoint + radius)


def _reject_constant(value: str) -> None:
    raise CanonicalBytesError(f"nonfinite JSON constant forbidden: {value}")


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise CanonicalBytesError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _check_ascii_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise CanonicalBytesError(f"{path}: keys must be ASCII strings")
            _check_ascii_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_ascii_keys(child, f"{path}[{index}]")
    elif isinstance(value, float):
        raise CanonicalBytesError(f"{path}: JSON floating numbers forbidden")


def canonical_json_bytes(obj: Any) -> bytes:
    _check_ascii_keys(obj)
    try:
        text = json.dumps(
            obj,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CanonicalBytesError("object cannot be canonically serialized") from exc
    return text.encode("utf-8")


def parse_canonical_json_bytes(data: bytes, *, allow_display: bool = True) -> Any:
    if not isinstance(data, bytes):
        raise CanonicalBytesError("record must be bytes")
    if data.startswith(b"\xef\xbb\xbf"):
        raise CanonicalBytesError("UTF-8 BOM forbidden")
    if b"\r" in data or b"\n" in data:
        raise CanonicalBytesError("record newline forbidden")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CanonicalBytesError("record is not UTF-8") from exc
    try:
        obj = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, CanonicalBytesError) as exc:
        raise CanonicalBytesError("invalid canonical JSON") from exc
    _check_ascii_keys(obj)
    if canonical_json_bytes(obj) != data:
        raise CanonicalBytesError("stored bytes are not canonical")
    if not allow_display and isinstance(obj, dict) and "display" in obj:
        raise CanonicalBytesError("display namespace forbidden here")
    return obj


def canonical_jsonl(records: list[dict[str, Any]]) -> bytes:
    if not records:
        return b""
    return b"\n".join(canonical_json_bytes(record) for record in records)


def parse_canonical_jsonl(data: bytes) -> list[tuple[dict[str, Any], bytes]]:
    if not isinstance(data, bytes):
        raise CanonicalBytesError("JSONL must be bytes")
    if not data:
        return []
    if data.endswith(b"\n"):
        raise CanonicalBytesError("final JSONL linefeed forbidden")
    if b"\r" in data:
        raise CanonicalBytesError("CR forbidden in JSONL")
    out: list[tuple[dict[str, Any], bytes]] = []
    for raw in data.split(b"\n"):
        obj = parse_canonical_json_bytes(raw)
        if not isinstance(obj, dict):
            raise CanonicalBytesError("JSONL record must be object")
        out.append((obj, raw))
    return out


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def chain_genesis(domain: str) -> str:
    if not isinstance(domain, str) or not domain.isascii() or not domain:
        raise SchemaError("genesis domain must be nonempty ASCII")
    return sha256_hex(domain.encode("ascii"))


def canonical_source_forbidden(source: str) -> list[str]:
    """Static guard for forbidden decimal/rounding paths in adapter source."""
    forbidden = ["float(", "Decimal(", ".str(", "arb(str", "arf(str", "mag(str"]
    return [token for token in forbidden if token in source]
