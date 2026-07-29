from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Protocol

from .canonical import CanonicalDyadic, ContractReject, canonical_json_bytes, parse_canonical_json
from .enums import CheckerFailureReason, RunnerFailureReason


@dataclass(frozen=True)
class CanonicalInterval:
    lo: Fraction
    hi: Fraction
    finite: bool = True

    def __post_init__(self) -> None:
        if self.finite and self.lo > self.hi:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    def to_object(self) -> dict[str, Any]:
        if not self.finite:
            return {"finite": False}
        lo = CanonicalDyadic(self.lo).to_object()
        hi = CanonicalDyadic(self.hi).to_object()
        return {"finite": True, "lo": lo, "hi": hi}

    @classmethod
    def from_object(cls, obj: Any) -> "CanonicalInterval":
        if not isinstance(obj, dict) or "finite" not in obj:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                "interval object missing finite field",
            )
        if obj["finite"] is False:
            if set(obj) != {"finite"}:
                raise ContractReject(
                    CheckerFailureReason.NONCANONICAL_ARTIFACT,
                    "nonfinite interval has extra fields",
                )
            return cls(Fraction(0), Fraction(0), False)
        if obj["finite"] is not True or set(obj) != {"finite", "lo", "hi"}:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                "canonical finite interval schema mismatch",
            )
        lo = CanonicalDyadic.from_object(obj["lo"], "interval.lo").value
        hi = CanonicalDyadic.from_object(obj["hi"], "interval.hi").value
        return cls(lo, hi, True)

    def round_trip_bytes(self) -> bytes:
        raw = canonical_json_bytes(self.to_object())
        decoded = self.from_object(parse_canonical_json(raw))
        if decoded != self:
            raise ContractReject(
                CheckerFailureReason.NONCANONICAL_ARTIFACT,
                "interval round-trip mismatch",
            )
        return raw

    def strictly_positive(self) -> bool:
        return self.finite and self.lo > 0

    def strictly_negative(self) -> bool:
        return self.finite and self.hi < 0


class PinnedKernelAdapter(Protocol):
    adapter_id: str

    def evaluate_g(
        self,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ) -> CanonicalInterval:
        ...

    def evaluate_gr(
        self,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ) -> CanonicalInterval:
        ...


class AdapterCallFailure(RuntimeError):
    def __init__(self, reason: RunnerFailureReason):
        super().__init__(reason.value)
        self.reason = reason
