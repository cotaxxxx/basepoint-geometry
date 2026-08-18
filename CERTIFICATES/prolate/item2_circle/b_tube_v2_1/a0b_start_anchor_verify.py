#!/usr/bin/env python3
"""Independent A0B verifier for the first-cross-section point-lambda Krawczyk gate."""
from __future__ import annotations

from calibration_context import *
from calibration_config import require_blocal_dependency


A0B_SCHEMA = "btube-a0b-start-anchors-v1"
A0B_PATH_NAME = "A0B_START_ANCHORS.json"


def _pairs(config: dict[str, Any]) -> list[tuple[Dyadic, Dyadic]]:
    widths = [
        Dyadic.from_json(item, f"candidate_lambda_widths[{index}]")
        for index, item in enumerate(config["candidate_lambda_widths"])
    ]
    radii = [
        Dyadic.from_json(item, f"candidate_tube_radii[{index}]")
        for index, item in enumerate(config["candidate_tube_radii"])
    ]
    return [(width, radius) for width in widths for radius in radii]


def _a0_interval(config: dict[str, Any]) -> DyadicInterval:
    cert = parse_canonical_json_bytes(A0_CERTIFICATE_PATH.read_bytes(), allow_display=False)
    if cert.get("schema") != A0_SCHEMA or cert.get("status") != A0_STATUS:
        raise CalibrationError("A0B verifier: A0 schema/status mismatch")
    dep = config["blocal_dependency"]
    if (
        cert.get("blocal_artifact_sha256") != dep["artifact_zip_sha256"]
        or cert.get("blocal_certificate_sha256") != dep["certificate_sha256"]
        or cert.get("blocal_config_sha256") != dep["config_sha256"]
        or cert.get("blocal_source_head") != dep["source_head"]
        or cert.get("lambda_start") != dep["lambda_start"]
    ):
        raise CalibrationError("A0B verifier: A0/B-LOCAL provenance mismatch")
    delta = Rational.from_json(cert["delta_start_exact"], "A0.delta_exact").as_fraction()
    if not A0_DELTA_FLOOR.as_fraction() < delta <= Fraction(1, 2048):
        raise CalibrationError("A0B verifier: A0 delta consistency invariant failed")
    interval = DyadicInterval.from_json(
        cert["operational_refined_start_root_interval"], "A0.operational_root"
    )
    if interval != A0_OPERATIONAL_ROOT:
        raise CalibrationError("A0B verifier: A0 operational bracket mismatch")
    return interval


def _adaptive(q_hull: DyadicInterval, cap: Dyadic, sigma: Dyadic):
    d_left = q_hull.lo
    d_right = D_ONE - q_hull.hi
    if d_left <= D_ZERO or d_right <= D_ZERO:
        raise CalibrationError("A0B verifier: predictor outside open unit interval")
    rho = cap
    left_bound = sigma * d_left
    right_bound = sigma * d_right
    if left_bound < rho:
        rho = left_bound
    if right_bound < rho:
        rho = right_bound
    if rho <= D_ZERO:
        raise CalibrationError("A0B verifier: nonpositive adaptive radius")
    domain = DyadicInterval(q_hull.lo - rho, q_hull.hi + rho)
    if domain.lo <= D_ZERO or not domain.hi < D_ONE:
        raise CalibrationError("A0B verifier: adaptive tube crosses physical boundary")
    return rho, d_left, d_right, domain


def _krawczyk(domain: DyadicInterval, entry: dict[str, Any]):
    residual = DyadicInterval.from_json(entry["residual"], "A0B.residual")
    slope = DyadicInterval.from_json(entry["slope"], "A0B.slope")
    preconditioner = Dyadic.from_json(entry["preconditioner"], "A0B.preconditioner")
    midpoint = domain.midpoint()
    if preconditioner == D_ZERO:
        return DyadicInterval.point(midpoint), D_ZERO, D_ZERO, "preconditioner_zero", False
    c = DyadicInterval.point(preconditioner)
    m = DyadicInterval.point(midpoint)
    image = m - residual * c + (
        DyadicInterval.point(D_ONE) - slope * c
    ) * (domain - m)
    left_margin = image.lo - domain.lo
    right_margin = domain.hi - image.hi
    if not domain.strictly_contains(image):
        return image, left_margin, right_margin, "krawczyk_not_strict", False
    if not slope.hi < D_ZERO:
        return image, left_margin, right_margin, "slope_not_strictly_negative", False
    return image, left_margin, right_margin, None, True


def verify_a0b_start_anchors(out_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    require_blocal_dependency(config)
    raw = (out_dir / A0B_PATH_NAME).read_bytes()
    cert = parse_canonical_json_bytes(raw, allow_display=False)
    _require_exact_keys(cert, {
        "a0_start_root_interval", "all_passed", "anchor_mode", "candidate_count",
        "entries", "lambda_start", "mode", "schema",
    }, "A0B certificate")
    assert_result_namespace(cert)
    if cert["schema"] != A0B_SCHEMA or cert["mode"] != BINDING_MODE:
        raise CalibrationError("A0B verifier: schema/mode mismatch")
    if cert["anchor_mode"] != ANCHOR_MODE:
        raise CalibrationError("A0B verifier: anchor mode mismatch")
    start = Rational.from_json(
        config["blocal_dependency"]["lambda_start"], "blocal_dependency.lambda_start"
    )
    if cert["lambda_start"] != start.to_json():
        raise CalibrationError("A0B verifier: lambda_start mismatch")
    a0 = _a0_interval(config)
    if cert["a0_start_root_interval"] != a0.to_json():
        raise CalibrationError("A0B verifier: A0 bracket mismatch")
    pairs = _pairs(config)
    entries = cert["entries"]
    if not isinstance(entries, list) or len(entries) != len(pairs):
        raise CalibrationError("A0B verifier: candidate entry completeness mismatch")
    if cert["candidate_count"] != len(pairs):
        raise CalibrationError("A0B verifier: candidate count mismatch")

    parsed = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    first_cells: dict[int, dict[str, Any]] = {}
    for record, _ in parsed:
        if record.get("record_type") == "cell" and record.get("cell_index") == 0:
            index = record.get("candidate_index")
            if not isinstance(index, int) or isinstance(index, bool) or index in first_cells:
                raise CalibrationError("A0B verifier: first-cell index duplicate/invalid")
            first_cells[index] = record
    if set(first_cells) != set(range(len(pairs))):
        raise CalibrationError("A0B verifier: first-cell set incomplete")

    sigma = Dyadic.from_json(config["adaptive_safety_factor"], "adaptive_safety_factor")
    anchor = a0.midpoint()
    start_fraction = start.as_fraction()
    end = Rational.from_json(config["lambda_end"], "lambda_end").as_fraction()
    pass_flags = []
    entry_keys = {
        "adaptive_radius", "adaptive_safety_factor", "boundary_margin_left",
        "boundary_margin_right", "candidate_index", "evaluation_count",
        "failure_reason", "first_lambda_interval", "krawczyk_image",
        "lambda_width", "left_margin", "passed", "point_lambda",
        "preconditioner", "q_left", "q_right", "radius_rule", "residual",
        "right_margin", "slope", "start_section", "tube_interval", "tube_radius",
    }
    for candidate_index, ((width, cap), entry) in enumerate(zip(pairs, entries)):
        _require_exact_keys(entry, entry_keys, f"A0B.entries[{candidate_index}]")
        assert_result_namespace(entry)
        if entry.get("candidate_index") != candidate_index:
            raise CalibrationError("A0B verifier: candidate index mismatch")
        if entry.get("lambda_width") != width.to_json() or entry.get("tube_radius") != cap.to_json():
            raise CalibrationError("A0B verifier: candidate pair mismatch")
        if entry.get("adaptive_safety_factor") != sigma.to_json():
            raise CalibrationError("A0B verifier: sigma mismatch")
        if entry.get("radius_rule") != ADAPTIVE_RADIUS_RULE:
            raise CalibrationError("A0B verifier: radius rule mismatch")
        right = min(start_fraction + width.as_fraction(), end)
        expected_lambda_interval = {
            "lo": Rational.from_fraction(start_fraction).to_json(),
            "hi": Rational.from_fraction(right).to_json(),
        }
        if entry.get("first_lambda_interval") != expected_lambda_interval:
            raise CalibrationError("A0B verifier: first lambda interval mismatch")
        if entry.get("point_lambda") != start.to_json():
            raise CalibrationError("A0B verifier: point lambda mismatch")

        first = first_cells[candidate_index]
        if first.get("lambda_interval") != expected_lambda_interval:
            raise CalibrationError("A0B verifier: first cell lambda coverage mismatch")
        predictor = first.get("predictor")
        if not isinstance(predictor, dict) or predictor.get("rule") != Q_RULE:
            raise CalibrationError("A0B verifier: first predictor rule mismatch")
        q_left = Dyadic.from_json(predictor["q_left"], "first.predictor.q_left")
        q_right = Dyadic.from_json(predictor["q_right"], "first.predictor.q_right")
        if q_left != anchor:
            raise CalibrationError("A0B verifier: first predictor is not A0 midpoint anchored")
        if entry.get("q_left") != q_left.to_json() or entry.get("q_right") != q_right.to_json():
            raise CalibrationError("A0B verifier: producer/first-cell predictor mismatch")

        q_hull = DyadicInterval.hull([q_left, q_right])
        rho, d_left, d_right, tube = _adaptive(q_hull, cap, sigma)
        if entry.get("adaptive_radius") != rho.to_json():
            raise CalibrationError("A0B verifier: adaptive radius mismatch")
        if first.get("adaptive_radius") != rho.to_json():
            raise CalibrationError("A0B verifier: first-cell adaptive radius mismatch")
        if entry.get("boundary_margin_left") != d_left.to_json():
            raise CalibrationError("A0B verifier: left boundary margin mismatch")
        if entry.get("boundary_margin_right") != d_right.to_json():
            raise CalibrationError("A0B verifier: right boundary margin mismatch")
        if entry.get("tube_interval") != tube.to_json() or first.get("tube_interval") != tube.to_json():
            raise CalibrationError("A0B verifier: physical tube mismatch")

        section = DyadicInterval(q_left - rho, q_left + rho)
        if not a0.contains(section):
            raise CalibrationError("A0B verifier: first cross-section escapes A0 bracket")
        if entry.get("start_section") != section.to_json():
            raise CalibrationError("A0B verifier: first cross-section mismatch")
        if not tube.contains(section):
            raise CalibrationError("A0B verifier: first cross-section not contained in first cell")

        image, lm, rm, reason, passed = _krawczyk(section, entry)
        if entry.get("krawczyk_image") != image.to_json():
            raise CalibrationError("A0B verifier: Krawczyk image mismatch")
        if entry.get("left_margin") != lm.to_json() or entry.get("right_margin") != rm.to_json():
            raise CalibrationError("A0B verifier: Krawczyk margin mismatch")
        if entry.get("failure_reason") != reason or entry.get("passed") is not passed:
            raise CalibrationError("A0B verifier: Krawczyk pass/reason mismatch")
        if entry.get("evaluation_count") != 3:
            raise CalibrationError("A0B verifier: point gate evaluation count mismatch")
        if not passed:
            raise CalibrationError("A0B verifier: first-cross-section point Krawczyk failed")
        pass_flags.append(passed)

    if cert["all_passed"] is not all(pass_flags) or cert["all_passed"] is not True:
        raise CalibrationError("A0B verifier: all-passed policy mismatch")
    return cert


__all__ = [name for name in globals() if not name.startswith("__")]
