#!/usr/bin/env python3
"""Independent full record-layout verifier for B-TUBE calibration."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import calibration
from numeric_schema import (
    D_ONE, D_ZERO, Dyadic, DyadicInterval, Rational, canonical_json_bytes,
    chain_genesis, parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex,
)
from record_layout_contract import _partition, _positive_width


def _layout_candidate_pairs(config: dict) -> list[tuple[Dyadic, Dyadic]]:
    width_items = config.get("candidate_lambda_widths")
    radius_items = config.get("candidate_tube_radii")
    if not isinstance(width_items, list) or not width_items:
        raise calibration.CalibrationError("layout verifier: width candidates missing")
    if not isinstance(radius_items, list) or not radius_items:
        raise calibration.CalibrationError("layout verifier: radius candidates missing")
    widths = [
        Dyadic.from_json(item, f"candidate_lambda_widths[{index}]")
        for index, item in enumerate(width_items)
    ]
    radii = [
        Dyadic.from_json(item, f"candidate_tube_radii[{index}]")
        for index, item in enumerate(radius_items)
    ]
    for name, values in (("width", widths), ("radius", radii)):
        if any(value <= D_ZERO for value in values):
            raise calibration.CalibrationError(
                f"layout verifier: {name} candidates must be positive"
            )
        if len(set(values)) != len(values):
            raise calibration.CalibrationError(
                f"layout verifier: duplicate {name} candidate"
            )
        if any(not values[index + 1] < values[index] for index in range(len(values) - 1)):
            raise calibration.CalibrationError(
                f"layout verifier: {name} candidates not strictly decreasing"
            )
    return [(width, radius) for width in widths for radius in radii]


def _layout_a0_interval(config: dict) -> DyadicInterval:
    cert = parse_canonical_json_bytes(
        (HERE / "A0_BOUNDARY_DISTANCE_CERTIFICATE.json").read_bytes(),
        allow_display=False,
    )
    if cert.get("schema") != "btube-a0-boundary-distance-v1":
        raise calibration.CalibrationError("layout verifier: A0 schema mismatch")
    if cert.get("status") != "A0_CERTIFIED":
        raise calibration.CalibrationError("layout verifier: A0 status mismatch")
    if cert.get("claim") != "1-r_*(lambda_start)>=delta_start_exact>2^-13":
        raise calibration.CalibrationError("layout verifier: A0 claim mismatch")
    dep = config["blocal_dependency"]
    if (
        cert.get("blocal_artifact_sha256") != dep["artifact_zip_sha256"]
        or cert.get("blocal_certificate_sha256") != dep["certificate_sha256"]
        or cert.get("blocal_config_sha256") != dep["config_sha256"]
        or cert.get("blocal_source_head") != dep["source_head"]
        or cert.get("lambda_start") != dep["lambda_start"]
    ):
        raise calibration.CalibrationError("layout verifier: A0/B-LOCAL provenance mismatch")
    floor = Dyadic.from_json(cert["delta_start_dyadic_floor"], "A0.delta_floor")
    exact = Rational.from_json(cert["delta_start_exact"], "A0.delta_exact").as_fraction()
    if floor != Dyadic(1, 13) or not floor.as_fraction() < exact:
        raise calibration.CalibrationError("layout verifier: A0 delta lower bound mismatch")
    interval = DyadicInterval.from_json(
        cert["operational_refined_start_root_interval"], "A0.operational_root"
    )
    expected = DyadicInterval(Dyadic(2047, 11), Dyadic(8191, 13))
    if interval != expected:
        raise calibration.CalibrationError("layout verifier: A0 refined bracket mismatch")
    return interval


def _layout_shift(radius: Dyadic, center: Dyadic) -> DyadicInterval:
    return DyadicInterval(center - radius, center + radius)


def _layout_adaptive(q_hull: DyadicInterval, cap: Dyadic, sigma: Dyadic):
    d_left = q_hull.lo
    d_right = D_ONE - q_hull.hi
    if d_left <= D_ZERO or d_right <= D_ZERO:
        raise calibration.CalibrationError("layout verifier: predictor outside open unit interval")
    rho = cap
    a = sigma * d_left
    b = sigma * d_right
    if a < rho:
        rho = a
    if b < rho:
        rho = b
    if rho <= D_ZERO:
        raise calibration.CalibrationError("layout verifier: nonpositive adaptive radius")
    domain = DyadicInterval(q_hull.lo - rho, q_hull.hi + rho)
    if domain.lo <= D_ZERO or not domain.hi < D_ONE:
        raise calibration.CalibrationError("layout verifier: adaptive tube crosses boundary")
    return rho, d_left, d_right, domain


def _layout_krawczyk(domain: DyadicInterval, record: dict):
    residual = DyadicInterval.from_json(record["residual"], "residual")
    slope = DyadicInterval.from_json(record["slope"], "slope")
    pre = Dyadic.from_json(record["preconditioner"], "preconditioner")
    midpoint = domain.midpoint()
    if pre == D_ZERO:
        return DyadicInterval.point(midpoint), D_ZERO, D_ZERO, "preconditioner_zero", False
    c = DyadicInterval.point(pre)
    m = DyadicInterval.point(midpoint)
    image = m - residual * c + (DyadicInterval.point(D_ONE) - slope * c) * (domain - m)
    left_margin = image.lo - domain.lo
    right_margin = domain.hi - image.hi
    if not domain.strictly_contains(image):
        reason = "krawczyk_not_strict"
        passed = False
    elif not slope.hi < D_ZERO:
        reason = "slope_not_strictly_negative"
        passed = False
    else:
        reason = None
        passed = True
    return image, left_margin, right_margin, reason, passed


def _layout_intersection(left_center: Dyadic, left_rho: Dyadic,
                         right_center: Dyadic, right_rho: Dyadic) -> DyadicInterval | None:
    left = _layout_shift(left_rho, left_center)
    right = _layout_shift(right_rho, right_center)
    return left.intersection(right)


def _verify_binding_candidate(config, candidate_index, width, cap, cells,
                              candidate_start, cell_records, join_records, candidate_end):
    sigma = Dyadic.from_json(config["adaptive_safety_factor"], "adaptive_safety_factor")
    if sigma != Dyadic(1, 1):
        raise calibration.CalibrationError("layout verifier: adaptive sigma mismatch")
    a0 = _layout_a0_interval(config)
    if candidate_start.get("anchor_mode") != "BLOCAL_A0_FORWARD_V1":
        raise calibration.CalibrationError("layout verifier: forward anchor mode mismatch")
    if candidate_start.get("adaptive_safety_factor") != sigma.to_json():
        raise calibration.CalibrationError("layout verifier: candidate sigma mismatch")
    if candidate_start.get("start_root_interval") != a0.to_json():
        raise calibration.CalibrationError("layout verifier: candidate A0 bracket mismatch")

    expected_anchor = a0.midpoint()
    parsed = []
    previous_q_right = None
    for index, record in enumerate(cell_records):
        predictor = record.get("predictor")
        if not isinstance(predictor, dict) or predictor.get("rule") != calibration.Q_RULE:
            raise calibration.CalibrationError("layout verifier: predictor rule mismatch")
        q_left = Dyadic.from_json(predictor["q_left"], "predictor.q_left")
        q_right = Dyadic.from_json(predictor["q_right"], "predictor.q_right")
        if index == 0:
            if q_left != expected_anchor:
                raise calibration.CalibrationError("layout verifier: first predictor not A0 anchored")
        elif q_left != previous_q_right:
            raise calibration.CalibrationError("layout verifier: forward predictor discontinuity")
        previous_q_right = q_right
        q_hull = DyadicInterval.hull([q_left, q_right])
        rho, d_left, d_right, domain = _layout_adaptive(q_hull, cap, sigma)
        if record.get("radius_rule") != "exact_dyadic_min_boundary_margin_v1":
            raise calibration.CalibrationError("layout verifier: adaptive radius rule mismatch")
        if record.get("adaptive_radius") != rho.to_json():
            raise calibration.CalibrationError("layout verifier: adaptive radius mismatch")
        if record.get("boundary_margin_left") != d_left.to_json():
            raise calibration.CalibrationError("layout verifier: left boundary margin mismatch")
        if record.get("boundary_margin_right") != d_right.to_json():
            raise calibration.CalibrationError("layout verifier: right boundary margin mismatch")
        if record.get("tube_interval") != domain.to_json():
            raise calibration.CalibrationError("layout verifier: physical tube mismatch")
        if index == 0 and not a0.contains(_layout_shift(rho, q_left)):
            raise calibration.CalibrationError("layout verifier: first section escapes A0 bracket")
        parsed.append((q_left, q_right, rho, domain))

    join_expected = []
    for index, record in enumerate(join_records):
        ql = parsed[index]
        qr = parsed[index + 1]
        if record.get("left_radius") != ql[2].to_json():
            raise calibration.CalibrationError("layout verifier: JOIN left radius mismatch")
        if record.get("right_radius") != qr[2].to_json():
            raise calibration.CalibrationError("layout verifier: JOIN right radius mismatch")
        intersection = _layout_intersection(ql[1], ql[2], qr[0], qr[2])
        if intersection is None or not intersection.positive_width():
            raise calibration.CalibrationError("layout verifier: adaptive JOIN geometry invalid")
        if record.get("intersection") != intersection.to_json():
            raise calibration.CalibrationError("layout verifier: JOIN intersection mismatch")
        width_value = intersection.hi - intersection.lo
        if record.get("width") != width_value.to_json():
            raise calibration.CalibrationError("layout verifier: JOIN width mismatch")
        join_expected.append(intersection)

    evaluation_count = 0
    continuation = True
    cell_pass_flags = []
    join_pass_flags = []
    for index, record in enumerate(cell_records):
        failure = record.get("failure_reason")
        if not continuation:
            if failure != "branch_anchor_lost" or record.get("passed") is not False:
                raise calibration.CalibrationError("layout verifier: lost branch not fail-closed")
            expected_pass = False
        else:
            image, lm, rm, reason, expected_pass = _layout_krawczyk(parsed[index][3], record)
            evaluation_count += 3
            if record.get("krawczyk_image") != image.to_json():
                raise calibration.CalibrationError("layout verifier: cell Krawczyk image mismatch")
            if record.get("left_margin") != lm.to_json() or record.get("right_margin") != rm.to_json():
                raise calibration.CalibrationError("layout verifier: cell Krawczyk margin mismatch")
            if failure != reason or record.get("passed") is not expected_pass:
                raise calibration.CalibrationError("layout verifier: cell pass/reason mismatch")
        if record.get("evaluation_count") != evaluation_count:
            raise calibration.CalibrationError("layout verifier: cell evaluation count mismatch")
        cell_pass_flags.append(expected_pass)

        if index > 0:
            join_record = join_records[index - 1]
            if not (cell_pass_flags[index - 1] and cell_pass_flags[index]):
                join_reason = "adjacent_cell_failed"
                join_pass = False
            else:
                image, lm, rm, join_reason, join_pass = _layout_krawczyk(
                    join_expected[index - 1], join_record
                )
                evaluation_count += 3
                if join_record.get("krawczyk_image") != image.to_json():
                    raise calibration.CalibrationError("layout verifier: JOIN Krawczyk image mismatch")
                if (join_record.get("left_margin") != lm.to_json()
                        or join_record.get("right_margin") != rm.to_json()):
                    raise calibration.CalibrationError("layout verifier: JOIN Krawczyk margin mismatch")
            if join_record.get("failure_reason") != join_reason:
                raise calibration.CalibrationError("layout verifier: JOIN failure reason mismatch")
            if join_record.get("passed") is not join_pass:
                raise calibration.CalibrationError("layout verifier: JOIN passed mismatch")
            if join_record.get("evaluation_count") != evaluation_count:
                raise calibration.CalibrationError("layout verifier: JOIN evaluation count mismatch")
            join_pass_flags.append(join_pass)
            if not join_pass:
                continuation = False
        if not expected_pass:
            continuation = False

    cg = DyadicInterval(
        Dyadic.from_fraction(calibration.CG_ROOT[0].as_fraction()),
        Dyadic.from_fraction(calibration.CG_ROOT[1].as_fraction()),
    )
    terminal = _layout_shift(parsed[-1][2], parsed[-1][1])
    overlap = terminal.intersection(cg)
    terminal_attempt = (
        overlap is not None
        and overlap.positive_width()
        and cell_pass_flags[-1]
    )
    terminal_pass = False
    expected_overlap = DyadicInterval.point(D_ZERO)
    if terminal_attempt:
        expected_overlap = overlap
        terminal_record = {
            "residual": candidate_end.get("terminal_residual"),
            "slope": candidate_end.get("terminal_slope"),
            "preconditioner": candidate_end.get("terminal_preconditioner"),
        }
        image, lm, rm, terminal_reason, terminal_pass = _layout_krawczyk(
            overlap, terminal_record
        )
        evaluation_count += 3
        if candidate_end.get("terminal_krawczyk_image") != image.to_json():
            raise calibration.CalibrationError("layout verifier: terminal Krawczyk image mismatch")
        if (candidate_end.get("terminal_left_margin") != lm.to_json()
                or candidate_end.get("terminal_right_margin") != rm.to_json()):
            raise calibration.CalibrationError("layout verifier: terminal Krawczyk margin mismatch")
    else:
        terminal_reason = "terminal_cg_overlap_missing"
        zero_interval = DyadicInterval.point(D_ZERO).to_json()
        if (candidate_end.get("terminal_krawczyk_image") != zero_interval
                or candidate_end.get("terminal_residual") != zero_interval
                or candidate_end.get("terminal_slope") != zero_interval
                or candidate_end.get("terminal_preconditioner") != D_ZERO.to_json()
                or candidate_end.get("terminal_left_margin") != D_ZERO.to_json()
                or candidate_end.get("terminal_right_margin") != D_ZERO.to_json()):
            raise calibration.CalibrationError("layout verifier: terminal skipped fields mismatch")
    if candidate_end.get("terminal_cg_intersection") != expected_overlap.to_json():
        raise calibration.CalibrationError("layout verifier: terminal C-G intersection mismatch")
    if candidate_end.get("terminal_failure_reason") != terminal_reason:
        raise calibration.CalibrationError("layout verifier: terminal failure reason mismatch")
    if candidate_end.get("terminal_match_passed") is not terminal_pass:
        raise calibration.CalibrationError("layout verifier: terminal C-G match mismatch")

    joins_pass = all(join_pass_flags)
    expected_pass = (
        all(cell_pass_flags)
        and joins_pass
        and terminal_pass
        and evaluation_count <= config["evaluation_budget"]
    )
    expected_end = {
        "cells_attempted": len(cell_records),
        "cells_passed": sum(cell_pass_flags),
        "evaluation_count": evaluation_count,
        "joins_passed": joins_pass,
        "passed": expected_pass,
    }
    for key, value in expected_end.items():
        if candidate_end.get(key) != value:
            raise calibration.CalibrationError(
                f"layout verifier: adaptive candidate_end {key} mismatch at {candidate_index}"
            )
    return expected_pass


def verify_record_layout(out_dir: Path, *, source_head: str | None = None,
                         update_checker: bool = False,
                         allow_unbound_fixture: bool = False) -> dict:
    config, _ = calibration.load_config(out_dir / "config.calibration.json")
    if allow_unbound_fixture:
        start_rational = calibration.require_diagnostic_mode(config)
    else:
        if config["mode"] == calibration.CALIBRATION_MODE:
            start_rational = calibration.require_diagnostic_mode(config)
        else:
            calibration.require_blocal_dependency(config)
            start_rational = Rational.from_json(
                config["blocal_dependency"]["lambda_start"],
                "blocal_dependency.lambda_start",
            )
    parsed_jsonl = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    records = [record for record, _ in parsed_jsonl]

    previous = chain_genesis(calibration.CHAIN_DOMAIN)
    for record, raw in parsed_jsonl:
        if record.get("previous_record_sha256") != previous:
            raise calibration.CalibrationError("layout verifier: record chain mismatch")
        calibration.assert_result_namespace(record)
        previous = sha256_hex(raw)

    pairs = _layout_candidate_pairs(config)
    start = start_rational.as_fraction()
    end = Rational.from_json(config["lambda_end"]).as_fraction()
    cursor = 0
    pass_flags = []
    binding_deep = config["mode"] == calibration.BINDING_MODE and not allow_unbound_fixture

    for candidate_index, (width, radius) in enumerate(pairs):
        if cursor >= len(records):
            raise calibration.CalibrationError("layout verifier: missing candidate_start")
        candidate_start = records[cursor]
        cursor += 1
        expected_start = {
            "candidate_index": candidate_index,
            "lambda_width": width.to_json(),
            "record_type": "candidate_start",
            "tube_radius": radius.to_json(),
        }
        for key, value in expected_start.items():
            if candidate_start.get(key) != value:
                raise calibration.CalibrationError(
                    f"layout verifier: candidate_start mismatch at {candidate_index}"
                )

        cells = _partition(start, end, width.as_fraction())
        cell_records = []
        for cell_index, (left, right) in enumerate(cells):
            if cursor >= len(records):
                raise calibration.CalibrationError("layout verifier: missing cell record")
            record = records[cursor]
            cursor += 1
            if record.get("record_type") != "cell":
                raise calibration.CalibrationError("layout verifier: expected cell record")
            if record.get("candidate_index") != candidate_index or record.get("cell_index") != cell_index:
                raise calibration.CalibrationError("layout verifier: cell index mismatch")
            expected_interval = {
                "lo": Rational.from_fraction(left).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            }
            if record.get("lambda_interval") != expected_interval:
                raise calibration.CalibrationError("layout verifier: cell coverage mismatch")
            if not isinstance(record.get("passed"), bool):
                raise calibration.CalibrationError("layout verifier: cell passed must be bool")
            cell_records.append(record)

        join_records = []
        for join_index in range(max(len(cells) - 1, 0)):
            if cursor >= len(records):
                raise calibration.CalibrationError("layout verifier: missing JOIN record")
            record = records[cursor]
            cursor += 1
            if record.get("record_type") != "join":
                raise calibration.CalibrationError("layout verifier: expected JOIN record")
            if record.get("candidate_index") != candidate_index or record.get("join_index") != join_index:
                raise calibration.CalibrationError("layout verifier: JOIN index mismatch")
            join_records.append(record)

        if cursor >= len(records):
            raise calibration.CalibrationError("layout verifier: missing candidate_end")
        candidate_end = records[cursor]
        cursor += 1
        if candidate_end.get("record_type") != "candidate_end":
            raise calibration.CalibrationError("layout verifier: expected candidate_end")
        if candidate_end.get("candidate_index") != candidate_index:
            raise calibration.CalibrationError("layout verifier: candidate_end index mismatch")

        if binding_deep:
            expected_pass = _verify_binding_candidate(
                config, candidate_index, width, radius, cells,
                candidate_start, cell_records, join_records, candidate_end,
            )
        else:
            cell_pass_count = sum(record["passed"] for record in cell_records)
            joins_pass = all(
                record.get("failure_reason") is None and _positive_width(record)
                for record in join_records
            )
            final_evaluation_count = (
                cell_records[-1].get("evaluation_count", 0) if cell_records else 0
            )
            expected_pass = (
                cell_pass_count == len(cell_records)
                and joins_pass
                and final_evaluation_count <= config["evaluation_budget"]
            )
            expected_end = {
                "cells_attempted": len(cell_records),
                "cells_passed": cell_pass_count,
                "evaluation_count": final_evaluation_count,
                "joins_passed": joins_pass,
                "passed": expected_pass,
            }
            for key, value in expected_end.items():
                if candidate_end.get(key) != value:
                    raise calibration.CalibrationError(
                        f"layout verifier: candidate_end {key} mismatch at {candidate_index}"
                    )
        pass_flags.append(expected_pass)

    if cursor != len(records):
        raise calibration.CalibrationError("layout verifier: extra record after final candidate")

    summary = parse_canonical_json_bytes(
        (out_dir / "CALIBRATION_SUMMARY.json").read_bytes(), allow_display=False
    )
    calibration.assert_result_namespace(summary)
    if summary.get("record_count") != len(records) or summary.get("chain_tip") != previous:
        raise calibration.CalibrationError("layout verifier: summary chain/count mismatch")
    if summary.get("candidate_count") != len(pairs):
        raise calibration.CalibrationError("layout verifier: summary candidate count mismatch")
    first = next((index for index, passed in enumerate(pass_flags) if passed), None)
    first_passing = None
    if first is not None:
        width, radius = pairs[first]
        first_passing = {
            "candidate_index": first,
            "lambda_width": width.to_json(),
            "tube_radius": radius.to_json(),
        }

    if config["mode"] == calibration.CALIBRATION_MODE:
        recommendation = None
        expected_state = "CALIBRATION_INCOMPLETE"
        expected_coverage = False
    else:
        recommendation = first_passing
        expected_state = "CALIBRATION_COMPLETE" if recommendation is not None else "CALIBRATION_INCOMPLETE"
        expected_coverage = recommendation is not None
    if (summary.get("recommendation") != recommendation
            or summary.get("state") != expected_state
            or summary.get("coverage_claim") is not expected_coverage
            or summary.get("binding_to_final_lambda_start") is not config["binding_to_final_lambda_start"]
            or summary.get("mode") != config["mode"]):
        raise calibration.CalibrationError("layout verifier: recommendation/state policy mismatch")

    if source_head is not None:
        checker_path = out_dir / "CHECKER_REPORT.json"
        checker = parse_canonical_json_bytes(checker_path.read_bytes(), allow_display=False)
        if checker.get("source_head") != source_head or checker.get("verifier") != "PASS":
            raise calibration.CalibrationError("layout verifier: checker/source-head mismatch")
        if update_checker:
            checker["record_layout_verifier"] = "PASS"
            checker_path.write_bytes(canonical_json_bytes(checker))
    return summary


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("verify-output")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    args = parser.parse_args()
    verify_record_layout(args.out, source_head=args.source_head, update_checker=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
