#!/usr/bin/env python3
"""Independent structural verifier for routed evaluation records and bridge evidence."""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

from calibration_context import *
from calibration_config import _expected_routed_contract
from routed_evaluator import (
    exact_straddle_children,
    routed_bundle_pins,
    selector_for_r_interval,
    trace_genesis,
)


def _trace_hash(record: dict[str, Any]) -> str:
    body = {key: value for key, value in record.items() if key != "trace_record_sha256"}
    return sha256_hex(canonical_json_bytes(body))


def _verify_trace_record(record: dict[str, Any], previous: str, sequence: int,
                         cumulative: int) -> tuple[str, int]:
    required = {
        "boundary_route_evaluation_count_delta", "boundary_route_evaluation_count_total",
        "children", "contract_id", "detail", "enclosure", "lambda_interval", "phase",
        "pins", "post_failure_fallback", "previous_trace_sha256", "quantity", "r_interval",
        "route_id", "schema", "selector_r", "sequence", "trace_record_sha256",
    }
    _require_exact_keys(record, required, f"routed trace[{sequence}]")
    if record["schema"] != ROUTED_TRACE_SCHEMA:
        raise CalibrationError("routed trace: schema mismatch")
    if record["sequence"] != sequence:
        raise CalibrationError("routed trace: sequence mismatch")
    if record["previous_trace_sha256"] != previous:
        raise CalibrationError("routed trace: chain mismatch")
    if record["trace_record_sha256"] != _trace_hash(record):
        raise CalibrationError("routed trace: record digest mismatch")
    if record["contract_id"] != ROUTED_CONTRACT_ID:
        raise CalibrationError("routed trace: contract mismatch")
    if record["selector_r"] != ROUTED_SELECTOR.to_json():
        raise CalibrationError("routed trace: selector mismatch")
    if record["pins"] != routed_bundle_pins():
        raise CalibrationError("routed trace: source/pin mismatch")
    if record["post_failure_fallback"] is not False:
        raise CalibrationError("routed trace: post-failure fallback forbidden")
    if record["quantity"] not in {"F", "F_r"}:
        raise CalibrationError("routed trace: quantity mismatch")
    r_iv = DyadicInterval.from_json(record["r_interval"], "routed trace r")
    lam_iv = DyadicInterval.from_json(record["lambda_interval"], "routed trace lambda")
    del lam_iv
    enclosure = DyadicInterval.from_json(record["enclosure"], "routed trace enclosure")
    expected_route = selector_for_r_interval(r_iv)
    if record["route_id"] != expected_route:
        raise CalibrationError("routed trace: route/domain mismatch")
    delta = record["boundary_route_evaluation_count_delta"]
    total = record["boundary_route_evaluation_count_total"]
    if not isinstance(delta, int) or isinstance(delta, bool) or delta < 0:
        raise CalibrationError("routed trace: invalid boundary delta")
    if not isinstance(total, int) or isinstance(total, bool):
        raise CalibrationError("routed trace: invalid boundary total")
    if expected_route == ROUTED_INTERIOR_ROUTE_ID and delta != 0:
        raise CalibrationError("routed trace: interior route charged boundary budget")
    if expected_route in {ROUTED_BOUNDARY_ROUTE_ID, ROUTED_STRADDLE_ROUTE_ID} and delta <= 0:
        raise CalibrationError("routed trace: boundary route must consume positive budget")
    cumulative += delta
    if total != cumulative:
        raise CalibrationError("routed trace: cumulative boundary accounting mismatch")
    children = record["children"]
    if not isinstance(children, list):
        raise CalibrationError("routed trace: children must be a list")
    if expected_route == ROUTED_STRADDLE_ROUTE_ID:
        if len(children) != 2:
            raise CalibrationError("routed trace: straddle child count mismatch")
        left, right = exact_straddle_children(r_iv)
        expected_children = (
            (ROUTED_INTERIOR_ROUTE_ID, left),
            (ROUTED_BOUNDARY_ROUTE_ID, right),
        )
        hull_values: list[Dyadic] = []
        for child, (route_id, domain) in zip(children, expected_children):
            if child.get("route_id") != route_id or child.get("r_interval") != domain.to_json():
                raise CalibrationError("routed trace: straddle split/route mismatch")
            child_iv = DyadicInterval.from_json(child.get("enclosure"), "straddle child enclosure")
            hull_values.extend((child_iv.lo, child_iv.hi))
        if DyadicInterval.hull(hull_values) != enclosure:
            raise CalibrationError("routed trace: straddle hull mismatch")
    elif children:
        raise CalibrationError("routed trace: non-straddle children forbidden")
    if expected_route == ROUTED_BOUNDARY_ROUTE_ID:
        boundary_detail = record["detail"]
    elif expected_route == ROUTED_STRADDLE_ROUTE_ID:
        boundary_detail = children[1].get("detail")
    else:
        boundary_detail = None
    if boundary_detail is not None:
        if not isinstance(boundary_detail, dict):
            raise CalibrationError("routed trace: boundary detail missing")
        expected_boundary_id = (
            ROUTED_F_ROUTE_ID if record["quantity"] == "F" else ROUTED_HU_ROUTE_ID
        )
        expected_source_quantity = "F" if record["quantity"] == "F" else "H_U"
        expected_transform = (
            None if record["quantity"] == "F" else ROUTED_NEGATION_RULE_ID
        )
        if (
            boundary_detail.get("boundary_route_id") != expected_boundary_id
            or boundary_detail.get("source_quantity") != expected_source_quantity
            or boundary_detail.get("transform") != expected_transform
        ):
            raise CalibrationError("routed trace: boundary quantity/negation contract mismatch")
    phase = record["phase"]
    if not isinstance(phase, str) or not phase:
        raise CalibrationError("routed trace: phase missing")
    if phase == "A0B" and expected_route != ROUTED_BOUNDARY_ROUTE_ID:
        raise CalibrationError("routed trace: A0B must use boundary backend")
    return record["trace_record_sha256"], cumulative


def verify_routed_trace(out_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    path = out_dir / ROUTED_TRACE_NAME
    parsed = parse_canonical_jsonl(path.read_bytes())
    previous = trace_genesis()
    cumulative = 0
    a0b_count = 0
    for index, (record, _) in enumerate(parsed):
        previous, cumulative = _verify_trace_record(record, previous, index, cumulative)
        if record["phase"] == "A0B":
            a0b_count += 1
    if config["mode"] == BINDING_MODE and a0b_count == 0:
        raise CalibrationError("routed trace: missing A0B boundary evaluations")
    if cumulative > config["boundary_route_evaluation_budget"]:
        raise CalibrationError("routed trace: boundary budget exceeded")
    return {
        "boundary_route_evaluation_count": cumulative,
        "record_count": len(parsed),
        "trace_chain_tip": previous,
    }


def _expected_bridge_points() -> list[tuple[Fraction, Fraction]]:
    lambdas = (
        Fraction(17, 8), Fraction(5, 2), Fraction(3, 1),
        Fraction(7, 2), Fraction(4, 1), Fraction(9, 2),
    )
    return [(Fraction(k, 64), lam) for k in range(48, 64) for lam in lambdas]


def _bridge_grid_json() -> list[dict[str, Any]]:
    return [
        {
            "lambda": Rational.from_fraction(lam).to_json(),
            "r": Rational.from_fraction(r).to_json(),
        }
        for r, lam in _expected_bridge_points()
    ]


def bridge_grid_sha256() -> str:
    return sha256_hex(canonical_json_bytes(_bridge_grid_json()))


def verify_route_consistency_certificate_structure(
    certificate: dict[str, Any], *, expected_source_head: str | None = None
) -> dict[str, Any]:
    required = {
        "boundary_route_evaluation_count", "contract_id", "grid_id", "grid_sha256",
        "implementation_source_head", "pins", "producer_settings", "row_count", "rows",
        "schema", "status",
    }
    _require_exact_keys(certificate, required, "route consistency certificate")
    if (
        certificate["schema"] != ROUTE_CONSISTENCY_SCHEMA
        or certificate["status"] != "PASS"
        or certificate["contract_id"] != ROUTED_CONTRACT_ID
        or certificate["grid_id"] != ROUTE_CONSISTENCY_GRID_ID
    ):
        raise CalibrationError("route consistency certificate: identity/status mismatch")
    if certificate["pins"] != routed_bundle_pins():
        raise CalibrationError("route consistency certificate: source/pin mismatch")
    source_head = certificate["implementation_source_head"]
    if (
        not isinstance(source_head, str)
        or len(source_head) != 40
        or any(ch not in "0123456789abcdef" for ch in source_head)
    ):
        raise CalibrationError("route consistency certificate: source head format")
    if expected_source_head is not None and source_head != expected_source_head:
        raise CalibrationError("route consistency certificate: source head mismatch")
    settings = certificate["producer_settings"]
    _require_exact_keys(settings, {"depth", "dps", "limit", "tol"}, "bridge settings")
    if (
        settings["tol"] != ROUTE_CONSISTENCY_TOL
        or settings["depth"] != ROUTE_CONSISTENCY_DEPTH
        or settings["limit"] != ROUTE_CONSISTENCY_LIMIT
        or not isinstance(settings["dps"], int)
        or isinstance(settings["dps"], bool)
        or settings["dps"] <= 0
    ):
        raise CalibrationError("route consistency certificate: settings mismatch")
    points = _expected_bridge_points()
    if certificate["row_count"] != len(points) or certificate["grid_sha256"] != bridge_grid_sha256():
        raise CalibrationError("route consistency certificate: grid summary mismatch")
    rows = certificate["rows"]
    if not isinstance(rows, list) or len(rows) != len(points):
        raise CalibrationError("route consistency certificate: row completeness mismatch")
    for index, (row, (r, lam)) in enumerate(zip(rows, points)):
        _require_exact_keys(row, {"F", "F_r", "index", "lambda", "r"}, f"bridge row {index}")
        if (
            row["index"] != index
            or row["r"] != Rational.from_fraction(r).to_json()
            or row["lambda"] != Rational.from_fraction(lam).to_json()
        ):
            raise CalibrationError("route consistency certificate: grid row mismatch")
        for quantity in ("F", "F_r"):
            item = row[quantity]
            _require_exact_keys(
                item, {"boundary", "interior", "intersection"}, f"bridge row {index}.{quantity}"
            )
            interior = DyadicInterval.from_json(item["interior"], "bridge interior")
            boundary = DyadicInterval.from_json(item["boundary"], "bridge boundary")
            intersection = interior.intersection(boundary)
            if intersection is None or item["intersection"] != intersection.to_json():
                raise CalibrationError("route consistency certificate: empty/tampered intersection")
    count = certificate["boundary_route_evaluation_count"]
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise CalibrationError("route consistency certificate: boundary evaluation count")
    return certificate


def require_route_consistency_certificate(config: dict[str, Any]) -> dict[str, Any]:
    pin = config.get("route_consistency_certificate_sha256")
    if pin is None:
        raise CalibrationError(
            "route consistency certificate is not pinned; routed binding run is not authorized"
        )
    raw = ROUTE_CONSISTENCY_PATH.read_bytes()
    if sha256_hex(raw) != pin:
        raise CalibrationError("route consistency certificate byte SHA mismatch")
    cert = parse_canonical_json_bytes(raw, allow_display=False)
    verified = verify_route_consistency_certificate_structure(
        cert, expected_source_head=config["audited_source_commit"]
    )
    if verified["producer_settings"]["dps"] != config["checker_dps"]:
        raise CalibrationError("route consistency certificate: checker precision mismatch")
    return verified


def verify_routed_manifest(out_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    manifest = parse_canonical_json_bytes(
        (out_dir / ROUTED_MANIFEST_NAME).read_bytes(), allow_display=False
    )
    required = {
        "audited_source_commit", "boundary_route_evaluation_budget",
        "boundary_route_evaluation_count", "contract_id", "design_commit", "pins",
        "route_consistency_certificate_sha256", "schema", "trace_chain_tip",
        "trace_record_count",
    }
    _require_exact_keys(manifest, required, "routed manifest")
    if manifest["schema"] != ROUTED_MANIFEST_SCHEMA:
        raise CalibrationError("routed manifest: schema mismatch")
    if manifest["contract_id"] != ROUTED_CONTRACT_ID:
        raise CalibrationError("routed manifest: contract mismatch")
    if manifest["pins"] != routed_bundle_pins():
        raise CalibrationError("routed manifest: pin mismatch")
    if manifest["audited_source_commit"] != config["audited_source_commit"]:
        raise CalibrationError("routed manifest: audited source mismatch")
    if manifest["design_commit"] != config["design_commit"]:
        raise CalibrationError("routed manifest: design commit mismatch")
    if (
        manifest["boundary_route_evaluation_budget"]
        != config["boundary_route_evaluation_budget"]
    ):
        raise CalibrationError("routed manifest: boundary budget mismatch")
    if (
        manifest["route_consistency_certificate_sha256"]
        != config["route_consistency_certificate_sha256"]
    ):
        raise CalibrationError("routed manifest: bridge pin mismatch")
    trace = verify_routed_trace(out_dir, config)
    if (
        manifest["boundary_route_evaluation_count"]
        != trace["boundary_route_evaluation_count"]
        or manifest["trace_record_count"] != trace["record_count"]
        or manifest["trace_chain_tip"] != trace["trace_chain_tip"]
    ):
        raise CalibrationError("routed manifest: trace summary mismatch")
    return manifest


def verify_routed_outputs(out_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    require_route_consistency_certificate(config)
    return verify_routed_manifest(out_dir, config)


__all__ = [name for name in globals() if not name.startswith("__")]
