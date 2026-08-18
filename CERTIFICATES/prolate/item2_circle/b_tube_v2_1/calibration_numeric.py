"""Exact candidate, adaptive-radius, and interval helper functions."""
from calibration_context import *
from calibration_security import *


def _nearest_dyadic(value: Fraction, bits: int = 96) -> Dyadic:
    scale = 1 << bits
    numerator = value.numerator * scale
    denominator = value.denominator
    sign = -1 if numerator < 0 else 1
    quotient, remainder = divmod(abs(numerator), denominator)
    if 2 * remainder >= denominator:
        quotient += 1
    return Dyadic.canonical(sign * quotient, bits)


def _candidate_pairs(config: dict[str, Any]) -> list[tuple[Dyadic, Dyadic]]:
    widths = _dyadic_list(config["candidate_lambda_widths"], "candidate_lambda_widths")
    radii = _dyadic_list(config["candidate_tube_radii"], "candidate_tube_radii")
    return [(width, radius) for width in widths for radius in radii]


def _cell_partition(start: Fraction, end: Fraction, width: Fraction, maximum: int):
    cells = []
    left = start
    while left < end:
        right = min(left + width, end)
        if not left < right:
            raise CalibrationError("nonpositive calibration cell")
        cells.append((left, right))
        if len(cells) > maximum:
            raise CalibrationError("maximum cell budget exceeded")
        left = right
    return cells


def _rational_arb(value: Fraction, arb_type):
    return arb_type(value.numerator) / arb_type(value.denominator)


def _dyadic_arb(value: Dyadic, arb_type):
    return arb_type(value.m) / arb_type(1 << value.e)


def _fraction_box(lo: Fraction, hi: Fraction, arb_type):
    midpoint = (lo + hi) / 2
    radius = (hi - lo) / 2
    return _rational_arb(midpoint, arb_type) + _rational_arb(radius, arb_type) * arb_type("+/- 1.0")


def _dyadic_box(interval: DyadicInterval, arb_type):
    midpoint = interval.midpoint()
    radius = (interval.hi - interval.lo) * Dyadic(1, 1)
    return _dyadic_arb(midpoint, arb_type) + _dyadic_arb(radius, arb_type) * arb_type("+/- 1.0")


def _newton_predictor(kernel, arb_type, lam: Fraction, seed: Dyadic, *, iterations: int,
                      tol: str, depth: int, limit: int) -> Dyadic:
    current = seed
    lam_ball = _rational_arb(lam, arb_type)
    for _ in range(iterations):
        point = _dyadic_arb(current, arb_type)
        residual = arb_ball_to_exact_interval(
            kernel.F_arb(point, lam_ball, tol=tol, depth=depth, limit=limit)
        )
        slope = arb_ball_to_exact_interval(
            kernel.dFdr_arb(point, lam_ball, tol=tol, depth=depth, limit=limit)
        )
        slope_mid = slope.midpoint()
        if slope_mid == D_ZERO:
            break
        updated = current.as_fraction() - residual.midpoint().as_fraction() / slope_mid.as_fraction()
        current = _nearest_dyadic(updated)
    return current


def _load_a0_start_interval(path: Path = A0_CERTIFICATE_PATH) -> tuple[DyadicInterval, dict[str, Any]]:
    cert = parse_canonical_json_bytes(path.read_bytes(), allow_display=False)
    if cert.get("schema") != A0_SCHEMA or cert.get("status") != A0_STATUS:
        raise CalibrationError("A0 certificate schema/status mismatch")
    if cert.get("claim") != "1-r_*(lambda_start)>=delta_start_exact>2^-13":
        raise CalibrationError("A0 certificate claim mismatch")
    if cert.get("blocal_artifact_sha256") != BLOCAL_ARTIFACT_SHA256:
        raise CalibrationError("A0 B-LOCAL artifact pin mismatch")
    if cert.get("blocal_certificate_sha256") != BLOCAL_CERTIFICATE_SHA256:
        raise CalibrationError("A0 B-LOCAL certificate pin mismatch")
    if cert.get("blocal_config_sha256") != BLOCAL_CONFIG_SHA256:
        raise CalibrationError("A0 B-LOCAL config pin mismatch")
    if cert.get("blocal_source_head") != BLOCAL_SOURCE_HEAD:
        raise CalibrationError("A0 B-LOCAL source pin mismatch")
    if Rational.from_json(cert["lambda_start"], "A0.lambda_start") != BLOCAL_LAMBDA_START:
        raise CalibrationError("A0 lambda_start mismatch")
    if Dyadic.from_json(cert["delta_start_dyadic_floor"], "A0.delta_floor") != A0_DELTA_FLOOR:
        raise CalibrationError("A0 dyadic floor mismatch")
    delta = Rational.from_json(cert["delta_start_exact"], "A0.delta_exact").as_fraction()
    if not A0_DELTA_FLOOR.as_fraction() < delta:
        raise CalibrationError("A0 exact delta does not exceed 2^-13")
    interval = DyadicInterval.from_json(
        cert["operational_refined_start_root_interval"], "A0.operational_root"
    )
    if interval != A0_OPERATIONAL_ROOT:
        raise CalibrationError("A0 operational root interval mismatch")
    target = DyadicInterval.from_json(cert["target_start_root_interval"], "A0.target_root")
    machine = BLOCAL_MACHINE_CONCLUSION["start_root_interval"]
    if target.to_json() != machine:
        raise CalibrationError("A0 target root interval mismatch")
    if not target.contains(interval):
        raise CalibrationError("A0 refined interval escapes B-LOCAL target")
    return interval, cert


def _adaptive_radius(q_hull: DyadicInterval, cap: Dyadic, sigma: Dyadic
                     ) -> tuple[Dyadic, Dyadic, Dyadic, DyadicInterval]:
    if cap <= D_ZERO:
        raise CalibrationError("adaptive radius cap must be positive")
    if sigma <= D_ZERO or not sigma < D_ONE:
        raise CalibrationError("adaptive safety factor must lie strictly in (0,1)")
    left_margin = q_hull.lo
    right_margin = D_ONE - q_hull.hi
    if left_margin <= D_ZERO or right_margin <= D_ZERO:
        raise CalibrationError("predictor hull outside open unit interval")
    rho = cap
    left_bound = sigma * left_margin
    right_bound = sigma * right_margin
    if left_bound < rho:
        rho = left_bound
    if right_bound < rho:
        rho = right_bound
    if rho <= D_ZERO:
        raise CalibrationError("adaptive radius is nonpositive")
    y_box = DyadicInterval(-rho, rho)
    domain = physical_tube(q_hull, y_box)
    if domain.lo <= D_ZERO or not domain.hi < D_ONE:
        raise CalibrationError("adaptive physical tube outside open unit interval")
    return rho, left_margin, right_margin, domain


def _cg_root_dyadic_interval() -> DyadicInterval:
    return DyadicInterval(
        Dyadic.from_fraction(CG_ROOT[0].as_fraction()),
        Dyadic.from_fraction(CG_ROOT[1].as_fraction()),
    )


def _append_record(records: list[dict[str, Any]], previous: str, body: dict[str, Any]) -> str:
    record = dict(body)
    record["previous_record_sha256"] = previous
    assert_result_namespace(record)
    raw = canonical_json_bytes(record)
    records.append(record)
    return sha256_hex(raw)


__all__ = [name for name in globals() if not name.startswith("__")]
