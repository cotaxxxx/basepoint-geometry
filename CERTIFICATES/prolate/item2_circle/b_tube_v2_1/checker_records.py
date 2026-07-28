#!/usr/bin/env python3
"""Record-level reconstruction for B-TUBE v2.1 self-tests."""
from checker_common import *

def _check_cell(record: dict[str, Any], expected_index: int) -> dict[str, Any]:
    if record.get("phase") != "cell" or record.get("cell_index") != expected_index:
        _fail("cell phase/index mismatch")
    if record.get("q_rule") != Q_RULE:
        _fail("cell q rule mismatch")
    if record.get("unresolved") is not False:
        _fail("unresolved cell")
    lam_lo = Rational.from_json(record["lambda"]["lo"], "cell.lambda.lo")
    lam_hi = Rational.from_json(record["lambda"]["hi"], "cell.lambda.hi")
    q_left = Dyadic.from_json(record["q_endpoint"]["left"], "cell.q.left")
    q_right = Dyadic.from_json(record["q_endpoint"]["right"], "cell.q.right")
    y_box = DyadicInterval.from_json(record["y_interval"], "cell.y")
    m_y = Dyadic.from_json(record["m_y"], "cell.m_y")
    preconditioner = Dyadic.from_json(record["preconditioner"], "cell.c")
    if preconditioner == D_ZERO:
        _fail("cell preconditioner is zero")
    predictor = AffinePredictor(lam_lo, lam_hi, q_left, q_right)
    q_hull = predictor.range_hull()
    x_box = physical_tube(q_hull, y_box)
    residual = F_interval(q_hull + DyadicInterval.point(m_y), (lam_lo, lam_hi))
    slope = dFdr_interval(x_box, (lam_lo, lam_hi))
    k_image = krawczyk_image(
        m=m_y,
        residual=residual,
        slope=slope,
        preconditioner=preconditioner,
        domain=y_box,
    )
    saved = record.get("saved")
    if not isinstance(saved, dict):
        _fail("cell saved enclosures missing")
    _saved_contains(saved["q_hull"], q_hull, "cell.saved.q_hull")
    _saved_contains(saved["physical_x"], x_box, "cell.saved.physical_x")
    _saved_contains(saved["residual_h"], residual, "cell.saved.residual_h")
    _saved_contains(saved["slope"], slope, "cell.saved.slope")
    _saved_contains(saved["krawczyk"], k_image, "cell.saved.krawczyk")
    if not y_box.strictly_contains(k_image):
        _fail("cell Krawczyk image is not strictly inside Y")
    if not slope.hi < D_ZERO:
        _fail("cell slope is not strictly negative")
    return {
        "record": record,
        "lambda_lo": lam_lo,
        "lambda_hi": lam_hi,
        "q_left": q_left,
        "q_right": q_right,
        "y_box": y_box,
        "x_box": x_box,
    }


def _check_join(record: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> None:
    if record.get("phase") != "join" or record.get("between") != [left["record"]["cell_index"], right["record"]["cell_index"]]:
        _fail("JOIN references wrong cells")
    if record.get("unresolved") is not False:
        _fail("unresolved JOIN")
    lam = Rational.from_json(record["lambda"], "join.lambda")
    if lam != left["lambda_hi"] or lam != right["lambda_lo"]:
        _fail("JOIN lambda is not the exact shared endpoint")
    left_section = shifted(left["y_box"], left["q_right"])
    right_section = shifted(right["y_box"], right["q_left"])
    stored_left = DyadicInterval.from_json(record["left_section"], "join.left_section")
    stored_right = DyadicInterval.from_json(record["right_section"], "join.right_section")
    _exact_interval_equal(stored_left, left_section, "join.left_section")
    _exact_interval_equal(stored_right, right_section, "join.right_section")
    intersection = exact_join_intersection(left["q_right"], left["y_box"], right["q_left"], right["y_box"])
    stored_intersection = DyadicInterval.from_json(record["intersection"], "join.intersection")
    _exact_interval_equal(stored_intersection, intersection, "join.intersection")
    midpoint = Dyadic.from_json(record["midpoint"], "join.midpoint")
    if midpoint != intersection.midpoint():
        _fail("JOIN midpoint mismatch")
    preconditioner = Dyadic.from_json(record["preconditioner"], "join.c")
    if preconditioner == D_ZERO:
        _fail("JOIN preconditioner is zero")
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(intersection, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=preconditioner,
        domain=intersection,
    )
    saved = record["saved"]
    _saved_contains(saved["residual"], residual, "join.saved.residual")
    _saved_contains(saved["slope"], slope, "join.saved.slope")
    _saved_contains(saved["krawczyk"], k_image, "join.saved.krawczyk")
    if not intersection.strictly_contains(k_image):
        _fail("JOIN K(J;lambda*) is not strictly inside J")


def _check_boundary(
    record: dict[str, Any],
    first: dict[str, Any],
    config: dict[str, Any],
    summary: dict[str, Any],
) -> str:
    if record.get("phase") != "boundary" or record.get("unresolved") is not False:
        _fail("invalid boundary record")
    lambda_start = Rational.from_json(config["lambda_start"], "config.lambda_start")
    _rational_equal(record["lambda_start"], lambda_start, "boundary.lambda_start")
    if first["lambda_lo"] != lambda_start:
        _fail("first cell left endpoint differs from boundary lambda_start")
    status = record.get("status")
    if status == "DEFERRED":
        if summary.get("expected_verdict") != "CERTIFIED_CORE_INTERVAL" or summary.get("boundary_connection") != "DEFERRED":
            _fail("DEFERRED boundary mixed with FULL verdict")
        forbidden = {"dependency_artifact_sha256", "terminal_root_interval", "intersection", "saved"}
        if forbidden.intersection(record):
            _fail("DEFERRED boundary contains pseudo-certificate fields")
        return "CERTIFIED_CORE_INTERVAL"
    if status != "PASS":
        _fail("unsupported boundary status")
    if summary.get("expected_verdict") != "CERTIFIED_B_TUBE_FULL" or summary.get("boundary_connection") != "PASS":
        _fail("PASS boundary mixed with CORE verdict")
    if record.get("dependency_artifact_sha256") != config.get("boundary_dependency_sha256") or record.get("dependency_artifact_sha256") != BLOCAL_MOCK_SHA256:
        _dependency_fail("boundary dependency SHA mismatch")
    terminal = DyadicInterval.from_json(record["terminal_root_interval"], "boundary.terminal")
    first_section = shifted(first["y_box"], first["q_left"])
    stored_first = DyadicInterval.from_json(record["first_section"], "boundary.first_section")
    _exact_interval_equal(stored_first, first_section, "boundary.first_section")
    intersection = terminal.intersection(first_section)
    if intersection is None or not intersection.positive_width():
        _fail("boundary intersection empty")
    stored_intersection = DyadicInterval.from_json(record["intersection"], "boundary.intersection")
    _exact_interval_equal(stored_intersection, intersection, "boundary.intersection")
    midpoint = Dyadic.from_json(record["midpoint"], "boundary.midpoint")
    if midpoint != intersection.midpoint():
        _fail("boundary midpoint mismatch")
    preconditioner = Dyadic.from_json(record["preconditioner"], "boundary.c")
    if preconditioner == D_ZERO:
        _fail("boundary preconditioner zero")
    lam = lambda_start
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(intersection, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=preconditioner,
        domain=intersection,
    )
    saved = record["saved"]
    _saved_contains(saved["residual"], residual, "boundary.saved.residual")
    _saved_contains(saved["slope"], slope, "boundary.saved.slope")
    _saved_contains(saved["krawczyk"], k_image, "boundary.saved.krawczyk")
    if not intersection.strictly_contains(k_image):
        _fail("boundary Krawczyk image not strictly inside interface intersection")
    return "CERTIFIED_B_TUBE_FULL"


def _check_match(record: dict[str, Any], last: dict[str, Any], config: dict[str, Any]) -> None:
    if record.get("phase") != "match" or record.get("unresolved") is not False:
        _fail("invalid match record")
    lambda_match = Rational.from_json(config["lambda_match"], "config.lambda_match")
    lam = _rational_equal(record["lambda"], lambda_match, "match.lambda")
    if last["lambda_hi"] != lambda_match:
        _fail("last cell right endpoint is not 118/25")
    section = shifted(last["y_box"], last["q_right"])
    stored_section = DyadicInterval.from_json(record["last_section"], "match.last_section")
    _exact_interval_equal(stored_section, section, "match.last_section")
    midpoint = Dyadic.from_json(record["midpoint"], "match.midpoint")
    if midpoint != section.midpoint():
        _fail("match midpoint mismatch")
    preconditioner = Dyadic.from_json(record["preconditioner"], "match.c")
    if preconditioner == D_ZERO:
        _fail("match preconditioner zero")
    residual = F_interval(DyadicInterval.point(midpoint), (lam, lam))
    slope = dFdr_interval(section, (lam, lam))
    k_image = krawczyk_image(
        m=midpoint,
        residual=residual,
        slope=slope,
        preconditioner=preconditioner,
        domain=section,
    )
    saved = record["saved"]
    _saved_contains(saved["residual"], residual, "match.saved.residual")
    _saved_contains(saved["slope"], slope, "match.saved.slope")
    _saved_contains(saved["krawczyk"], k_image, "match.saved.krawczyk")
    cg = config["cg_match_dependency"]
    if record.get("cg_artifact_sha256") != cg["artifact_zip_sha256"]:
        _dependency_fail("match C-G artifact SHA mismatch")
    if record.get("b_kernel_sha256") != cg["b_kernel_sha256"]:
        _dependency_fail("match B kernel SHA mismatch")
    if record.get("cg_kernel_sha256") != cg["cg_kernel_sha256"]:
        _dependency_fail("match C-G kernel SHA mismatch")
    if record.get("b_kernel_sha256") != record.get("cg_kernel_sha256"):
        _dependency_fail("match functions are not pinned to identical kernel SHA")
    if record.get("fg_identity_lemma_id") != FG_LEMMA:
        _dependency_fail("match F/G identity lemma mismatch")
    cg_root = DyadicInterval.from_json(record["cg_root_interval"], "match.cg_root")
    pinned_root = DyadicInterval(
        Dyadic.from_fraction(Rational.from_json(cg["root_interval"]["lo"]).as_fraction()),
        Dyadic.from_fraction(Rational.from_json(cg["root_interval"]["hi"]).as_fraction()),
    )
    _exact_interval_equal(cg_root, pinned_root, "match.cg_root")
    if not cg_root.strictly_contains(k_image):
        _fail("MATCH Krawczyk image not strictly inside canonical C-G root bracket")



__all__ = [name for name in globals() if not name.startswith("__")]
