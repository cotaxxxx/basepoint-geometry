#!/usr/bin/env python3
"""Independent verifier for exact-rational lambda transport evidence."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

from calibration_context import *
import exact_lambda_contract as producer_contract
from exact_lambda_prepartition_verifier import (
    verify_prepartition_trace_records,
)

VERIFIER_TRANSPORT_PATH = "exact_lambda_transport.py"
VERIFIER_TRANSPORT_SHA256 = "adee7587a7519e8c0274470a63ddda6c82f4b8ebd4117c18fcab1ce77fb0ce80"
VERIFIER_ADDENDUM_PATH = "ROUTED_EVALUATOR_EXACT_LAMBDA_ADDENDUM_V2.md"
VERIFIER_ADDENDUM_SHA256 = "deb672741e972a5d485d6477c8ff87d16d2dfb92d29dbd50511cb2ef8fc7d358"
VERIFIER_ROUNDING_BITS = 192
VERIFIER_RULE_ID = "BLOCAL_V22_FIXED_LATTICE_OUTWARD_192_V1"

VERIFIER_LAMBDA_PLUS = Fraction(206539, 100000)
VERIFIER_LAMBDA_START = Fraction(3307749, 1600000)
VERIFIER_LAMBDA_END = Fraction(118, 25)


def _floor_fixed(q: Fraction) -> Fraction:
    scale = 1 << VERIFIER_ROUNDING_BITS
    return Fraction(q.numerator * scale // q.denominator, scale)


def _ceil_fixed(q: Fraction) -> Fraction:
    scale = 1 << VERIFIER_ROUNDING_BITS
    return Fraction(-((-q.numerator * scale) // q.denominator), scale)


def _rational(obj: Any, where: str) -> Fraction:
    return Rational.from_json(obj, where).as_fraction()


def _rational_interval(obj: Any, where: str) -> tuple[Fraction, Fraction]:
    _require_exact_keys(obj, {"lo", "hi"}, where)
    lo = _rational(obj["lo"], f"{where}.lo")
    hi = _rational(obj["hi"], f"{where}.hi")
    if hi < lo:
        raise CalibrationError(f"{where}: reversed")
    return lo, hi


def _verify_source_pins() -> None:
    if (
        producer_contract.EXACT_LAMBDA_TRANSPORT_SHA256 != VERIFIER_TRANSPORT_SHA256
        or producer_contract.EXACT_LAMBDA_ADDENDUM_SHA256 != VERIFIER_ADDENDUM_SHA256
        or producer_contract.EXACT_LAMBDA_ROUNDING_BITS != VERIFIER_ROUNDING_BITS
        or producer_contract.EXACT_LAMBDA_TRANSPORT_RULE_ID != VERIFIER_RULE_ID
    ):
        raise CalibrationError("exact lambda verifier: producer/checker contract mismatch")
    transport = BTUBE_ROOT / VERIFIER_TRANSPORT_PATH
    addendum = BTUBE_ROOT / VERIFIER_ADDENDUM_PATH
    if sha256_hex(transport.read_bytes()) != VERIFIER_TRANSPORT_SHA256:
        raise CalibrationError("exact lambda verifier: transport source pin mismatch")
    if (
        VERIFIER_ADDENDUM_SHA256 != ROUTED_EXACT_LAMBDA_ADDENDUM_SHA256
        or sha256_hex(addendum.read_bytes()) != VERIFIER_ADDENDUM_SHA256
    ):
        raise CalibrationError("exact lambda verifier: addendum pin mismatch")


def reconstruct_transport(lambda_lo: Fraction, lambda_hi: Fraction) -> dict[str, Any]:
    if lambda_hi < lambda_lo:
        raise CalibrationError("exact lambda verifier: reversed exact lambda")
    if lambda_lo < VERIFIER_LAMBDA_START or VERIFIER_LAMBDA_END < lambda_hi:
        raise CalibrationError("exact lambda verifier: lambda outside result-bearing domain")
    s_lo = lambda_lo - VERIFIER_LAMBDA_PLUS
    s_hi = lambda_hi - VERIFIER_LAMBDA_PLUS
    if s_lo < Fraction(1, 512):
        raise CalibrationError("exact lambda verifier: s lower bound below 2^-9")
    rounded_lo = _floor_fixed(s_lo)
    rounded_hi = _ceil_fixed(s_hi)
    s_iv = DyadicInterval(
        Dyadic.from_fraction(rounded_lo),
        Dyadic.from_fraction(rounded_hi),
    )
    lower_enlargement = s_lo - rounded_lo
    upper_enlargement = rounded_hi - s_hi
    unit = Fraction(1, 1 << VERIFIER_ROUNDING_BITS)
    if not (
        Fraction(0) <= lower_enlargement < unit
        and Fraction(0) <= upper_enlargement < unit
    ):
        raise CalibrationError("exact lambda verifier: rounding bound violated")
    if not (
        VERIFIER_LAMBDA_PLUS + rounded_lo <= lambda_lo
        and lambda_hi <= VERIFIER_LAMBDA_PLUS + rounded_hi
    ):
        raise CalibrationError("exact lambda verifier: lambda containment failed")
    return {
        "exact_lambda_transport_sha256": VERIFIER_TRANSPORT_SHA256,
        "lambda_exact_interval": {
            "lo": Rational.from_fraction(lambda_lo).to_json(),
            "hi": Rational.from_fraction(lambda_hi).to_json(),
        },
        "lambda_plus": Rational.from_fraction(VERIFIER_LAMBDA_PLUS).to_json(),
        "lower_rounding_enlargement": Rational.from_fraction(
            lower_enlargement
        ).to_json(),
        "rounding_bits": VERIFIER_ROUNDING_BITS,
        "rounding_rule_id": VERIFIER_RULE_ID,
        "s_exact_interval": {
            "lo": Rational.from_fraction(s_lo).to_json(),
            "hi": Rational.from_fraction(s_hi).to_json(),
        },
        "s_outward_dyadic_interval": s_iv.to_json(),
        "upper_rounding_enlargement": Rational.from_fraction(
            upper_enlargement
        ).to_json(),
    }


def verify_transport_detail(detail: Any, where: str = "exact lambda transport") -> dict[str, Any]:
    if not isinstance(detail, dict):
        raise CalibrationError(f"{where}: object required")
    required = {
        "exact_lambda_transport_sha256",
        "lambda_exact_interval",
        "lambda_plus",
        "lower_rounding_enlargement",
        "rounding_bits",
        "rounding_rule_id",
        "s_exact_interval",
        "s_outward_dyadic_interval",
        "upper_rounding_enlargement",
    }
    _require_exact_keys(detail, required, where)
    lambda_lo, lambda_hi = _rational_interval(
        detail["lambda_exact_interval"], f"{where}.lambda_exact_interval"
    )
    expected = reconstruct_transport(lambda_lo, lambda_hi)
    if detail != expected:
        raise CalibrationError(f"{where}: independent reconstruction mismatch")
    legacy = detail["s_outward_dyadic_interval"]
    DyadicInterval.from_json(legacy, f"{where}.s_outward_dyadic_interval")
    return detail


def _boundary_detail(record: dict[str, Any]) -> dict[str, Any] | None:
    route_id = record.get("route_id")
    if route_id == ROUTED_BOUNDARY_ROUTE_ID:
        detail = record.get("detail")
        if not isinstance(detail, dict):
            raise CalibrationError("exact lambda verifier: boundary detail missing")
        return detail
    if route_id == ROUTED_STRADDLE_ROUTE_ID:
        children = record.get("children")
        if not isinstance(children, list) or len(children) != 2:
            raise CalibrationError("exact lambda verifier: straddle children missing")
        detail = children[1].get("detail")
        if not isinstance(detail, dict):
            raise CalibrationError("exact lambda verifier: straddle boundary detail missing")
        return detail
    return None


def verify_exact_lambda_trace_bytes(data: bytes) -> dict[str, Any]:
    _verify_source_pins()
    parsed = parse_canonical_jsonl(data)
    boundary_records = 0
    a0b_records = 0
    max_total_enlargement = Fraction(0)
    records = [record for record, _ in parsed]
    for index, (record, _) in enumerate(parsed):
        detail = _boundary_detail(record)
        if detail is None:
            continue
        transport = detail.get("exact_lambda_transport")
        verified = verify_transport_detail(
            transport, f"exact lambda trace[{index}].transport"
        )
        boundary_records += 1
        if record.get("phase") == "A0B":
            a0b_records += 1
        lower = _rational(
            verified["lower_rounding_enlargement"],
            f"exact lambda trace[{index}].lower_rounding_enlargement",
        )
        upper = _rational(
            verified["upper_rounding_enlargement"],
            f"exact lambda trace[{index}].upper_rounding_enlargement",
        )
        total = lower + upper
        if max_total_enlargement < total:
            max_total_enlargement = total
        if not total < Fraction(1, 1 << 191):
            raise CalibrationError(
                "exact lambda verifier: total rounding enlargement >= 2^-191"
            )
        legacy_lambda = DyadicInterval.from_json(
            record["lambda_interval"], f"exact lambda trace[{index}].lambda_interval"
        )
        lam_lo, lam_hi = _rational_interval(
            verified["lambda_exact_interval"],
            f"exact lambda trace[{index}].lambda_exact_interval",
        )
        if not (
            legacy_lambda.lo.as_fraction() <= lam_lo
            and lam_hi <= legacy_lambda.hi.as_fraction()
        ):
            raise CalibrationError(
                "exact lambda verifier: legacy Arb lambda does not contain exact lambda"
            )
    if parsed and boundary_records == 0:
        raise CalibrationError("exact lambda verifier: no exact boundary evidence")
    verify_prepartition_trace_records(records)
    return {
        "a0b_exact_boundary_record_count": a0b_records,
        "boundary_exact_record_count": boundary_records,
        "max_total_rounding_enlargement": Rational.from_fraction(
            max_total_enlargement
        ).to_json(),
        "transport_sha256": VERIFIER_TRANSPORT_SHA256,
    }


def verify_exact_lambda_trace(out_dir: Path) -> dict[str, Any]:
    return verify_exact_lambda_trace_bytes(
        (out_dir / ROUTED_TRACE_NAME).read_bytes()
    )


def assert_no_lambda_native_f_reference(paths: list[Path]) -> None:
    token = "enclose_" + "f"
    for path in paths:
        source = path.read_text(encoding="utf-8")
        if token in source:
            raise CalibrationError(
                f"exact lambda verifier: prohibited lambda-native F reference: {path.name}"
            )


__all__ = [name for name in globals() if not name.startswith("__")]
