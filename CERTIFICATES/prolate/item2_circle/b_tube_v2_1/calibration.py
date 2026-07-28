#!/usr/bin/env python3
"""Calibration-only implementation for B-TUBE v2.1.

The process-separated entry points run candidate evaluation, independent checking,
deterministic delivery assembly, and static configuration verification. No entry
point emits a production B-TUBE verdict.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import tokenize
from typing import Any, Iterable
import zipfile

HERE = Path(__file__).resolve().parent
BTUBE_ROOT = HERE
REPO_ROOT = HERE.parents[3]
VENDOR_DIR = REPO_ROOT / "CERTIFICATES/prolate/item2_circle/vendor"
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/prolate-item2-btube-v2-1-calibration.yml"
CONFIG_PATH = HERE / "config.calibration.json"
KERNEL_RELATIVE = Path("CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py")

sys.path.insert(0, str(BTUBE_ROOT))

from affine_geometry import (  # noqa: E402
    AffinePredictor,
    Q_RULE,
    exact_join_intersection,
    krawczyk_image,
    physical_tube,
)
from numeric_schema import (  # noqa: E402
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    SchemaError,
    arb_ball_to_exact_interval,
    canonical_json_bytes,
    canonical_jsonl,
    chain_genesis,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)

CONFIG_SCHEMA = "btube-calibration-config-v1"
DESIGN_VERSION = "btube-calibration-design-v1"
KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
AUDITED_SOURCE_COMMIT = "dbff78474399c47011906631de9cde75992b6d25"
DESIGN_COMMIT = "4a1b12a2a1e4f89712c33bc554646b44190f6f5b"
CG_ARTIFACT_SHA256 = "c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381"
CG_SOURCE_HEAD = "1e0f671c91798b9c044c04c7a4224a21e1e67830"
CG_CONFIG_SHA256 = "bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17"
CG_LEMMA = "F_G_FIXED_SLICE_IDENTITY_V1"
CG_LAMBDA = Rational(118, 25)
CG_ROOT = (Rational(1, 64), Rational(11, 256))
CHAIN_DOMAIN = "B-TUBE-CALIBRATION-RECORD-CHAIN-v1"
TERMINAL_STATES = {"CALIBRATION_COMPLETE", "CALIBRATION_INCOMPLETE", "CALIBRATION_FAILED"}
FORBIDDEN_RESULT_PREFIX = "CERT" + "IFIED_"
FORBIDDEN_RESULT_KEYS = {"verdict", "certified", "production_match"}
SOURCE_FILE_LIST = (
    "CALIBRATION_ONLY_WORKFLOW_DESIGN.md",
    "affine_geometry.py",
    "calibration.py",
    "config.calibration.json",
    "numeric_schema.py",
    "requirements-calibration.txt",
    "tests/test_calibration.py",
    "tests/test_selftest.py",
)
EXPECTED_CONFIG_KEYS = {
    "audited_source_commit", "candidate_lambda_widths", "candidate_tube_radii",
    "cg_match_dependency", "checker_dps", "design_commit", "design_version", "dps",
    "evaluation_budget", "lambda_end", "lambda_start", "max_cells",
    "max_subdivisions", "predictor_refresh", "production_kernel_sha256",
    "q_evaluation_rule", "record_chain_genesis_domain", "schema",
}
EXPECTED_CG_KEYS = {
    "artifact_zip_sha256", "b_kernel_sha256", "cg_kernel_sha256", "config_sha256",
    "lambda", "paper_lemma_id", "root_interval", "source_head",
}


class CalibrationError(RuntimeError):
    pass


def _require_exact_keys(obj: Any, expected: set[str], where: str) -> dict[str, Any]:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise CalibrationError(f"{where}: exact key set required")
    return obj


def _positive_int(value: Any, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise CalibrationError(f"{where}: positive integer required")
    return value


def _dyadic_list(value: Any, where: str) -> list[Dyadic]:
    if not isinstance(value, list) or not value:
        raise CalibrationError(f"{where}: nonempty list required")
    items = [Dyadic.from_json(item, f"{where}[{index}]") for index, item in enumerate(value)]
    if any(item <= D_ZERO for item in items):
        raise CalibrationError(f"{where}: values must be positive")
    if len(set(items)) != len(items):
        raise CalibrationError(f"{where}: duplicate candidate")
    if any(not items[index + 1] < items[index] for index in range(len(items) - 1)):
        raise CalibrationError(f"{where}: candidates must be strictly decreasing")
    return items


def load_config(path: Path = CONFIG_PATH) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = parse_canonical_json_bytes(raw, allow_display=False)
    _require_exact_keys(obj, EXPECTED_CONFIG_KEYS, "config")
    if obj["schema"] != CONFIG_SCHEMA or obj["design_version"] != DESIGN_VERSION:
        raise CalibrationError("config: schema/design mismatch")
    if obj["audited_source_commit"] != AUDITED_SOURCE_COMMIT:
        raise CalibrationError("config: audited source mismatch")
    if obj["design_commit"] != DESIGN_COMMIT:
        raise CalibrationError("config: design commit mismatch")
    if obj["production_kernel_sha256"] != KERNEL_SHA256:
        raise CalibrationError("config: production kernel pin mismatch")
    if obj["record_chain_genesis_domain"] != CHAIN_DOMAIN:
        raise CalibrationError("config: chain domain mismatch")
    if obj["q_evaluation_rule"] != Q_RULE:
        raise CalibrationError("config: affine evaluation rule mismatch")
    start = Rational.from_json(obj["lambda_start"], "lambda_start")
    end = Rational.from_json(obj["lambda_end"], "lambda_end")
    if start != Rational(2, 1):
        raise CalibrationError("config: lambda_start is not frozen B-LOCAL input")
    if end != CG_LAMBDA or not start < end:
        raise CalibrationError("config: terminal endpoint mismatch")
    dps = _positive_int(obj["dps"], "dps")
    checker_dps = _positive_int(obj["checker_dps"], "checker_dps")
    if checker_dps < dps:
        raise CalibrationError("config: checker_dps < dps")
    for key in ("predictor_refresh", "max_cells", "max_subdivisions", "evaluation_budget"):
        _positive_int(obj[key], key)
    _dyadic_list(obj["candidate_lambda_widths"], "candidate_lambda_widths")
    _dyadic_list(obj["candidate_tube_radii"], "candidate_tube_radii")

    cg = _require_exact_keys(obj["cg_match_dependency"], EXPECTED_CG_KEYS, "cg_match_dependency")
    if cg["artifact_zip_sha256"] != CG_ARTIFACT_SHA256:
        raise CalibrationError("config: C-G artifact mismatch")
    if cg["source_head"] != CG_SOURCE_HEAD:
        raise CalibrationError("config: C-G source mismatch")
    if cg["config_sha256"] != CG_CONFIG_SHA256:
        raise CalibrationError("config: C-G config mismatch")
    if cg["b_kernel_sha256"] != KERNEL_SHA256 or cg["cg_kernel_sha256"] != KERNEL_SHA256:
        raise CalibrationError("config: C-G/reference kernel mismatch")
    if cg["paper_lemma_id"] != CG_LEMMA:
        raise CalibrationError("config: C-G lemma mismatch")
    if Rational.from_json(cg["lambda"], "cg.lambda") != CG_LAMBDA:
        raise CalibrationError("config: C-G lambda mismatch")
    root = _require_exact_keys(cg["root_interval"], {"lo", "hi"}, "cg.root_interval")
    if (Rational.from_json(root["lo"]) != CG_ROOT[0]
            or Rational.from_json(root["hi"]) != CG_ROOT[1]):
        raise CalibrationError("config: C-G root interval mismatch")
    return obj, raw


def _source_forbidden_code(source: str) -> list[str]:
    patterns = (
        "flo" + "at(", "Dec" + "imal(", "." + "str(",
        "arb(" + "str", "arf(" + "str", "mag(" + "str",
    )
    code = "".join(
        token.string
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type not in {tokenize.STRING, tokenize.COMMENT}
    )
    return [pattern for pattern in patterns if pattern in code]


def assert_clean_source_tree(root: Path = BTUBE_ROOT) -> None:
    offenders: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.py")):
        hits = _source_forbidden_code(path.read_text(encoding="utf-8"))
        if hits:
            offenders[path.relative_to(root).as_posix()] = hits
    if offenders:
        raise CalibrationError(f"source scan failed: {offenders}")


def assert_workflow_security(path: Path = WORKFLOW_PATH) -> None:
    text = path.read_text(encoding="utf-8")
    required = (
        "permissions:\n  contents: read", "persist-credentials: false",
        "btube-v2-1-calibration-approved-*", "github.sha", "--require-hashes",
        "--only-binary=:all:",
    )
    if any(token not in text for token in required):
        raise CalibrationError("workflow security/authorization guard missing")
    forbidden = (
        "workflow_dispatch", "pull-requests: write", "issues: write",
        "contents: write", "persist-credentials: true",
    )
    if any(token in text for token in forbidden):
        raise CalibrationError("workflow contains forbidden write/dispatch capability")


def assert_no_stale_inputs(out_dir: Path) -> None:
    if out_dir.exists():
        raise CalibrationError("fresh-only output path already exists")
    for name in {
        "resume.json", "checkpoint.json", "calibration_records.jsonl",
        "CALIBRATION_SUMMARY.json", "DELIVERY_RECEIPT.json",
    }:
        if (HERE / name).exists():
            raise CalibrationError(f"stale calibration input present: {name}")


def assert_result_namespace(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_RESULT_KEYS:
                raise CalibrationError(f"{path}: forbidden result key {key}")
            assert_result_namespace(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_result_namespace(child, f"{path}[{index}]")
    elif isinstance(value, str) and FORBIDDEN_RESULT_PREFIX in value:
        raise CalibrationError(f"{path}: production certification string forbidden")


def _assert_repo_regular_file(path: Path, repo_root: Path = REPO_ROOT) -> Path:
    if path.is_symlink():
        raise CalibrationError("dependency path is a symlink")
    resolved_root = repo_root.resolve(strict=True)
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise CalibrationError("dependency path escapes repository") from exc
    if not resolved.is_file():
        raise CalibrationError("dependency is not a regular file")
    return resolved


def load_production_kernel(repo_root: Path = REPO_ROOT):
    kernel_path = _assert_repo_regular_file(repo_root / KERNEL_RELATIVE, repo_root)
    before = sha256_hex(kernel_path.read_bytes())
    if before != KERNEL_SHA256:
        raise CalibrationError("production F/F_r kernel file-byte SHA mismatch")
    spec = importlib.util.spec_from_file_location("btube_v21_calibration_kernel", kernel_path)
    if spec is None or spec.loader is None:
        raise CalibrationError("production kernel import spec unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    after = sha256_hex(Path(module.__file__).resolve(strict=True).read_bytes())
    if after != before:
        raise CalibrationError("production kernel changed during import")
    for name in ("F_arb", "dFdr_arb"):
        function = getattr(module, name, None)
        if function is None or getattr(function, "__module__", None) != module.__name__:
            raise CalibrationError("F and F_r must be supplied by the single pinned file")
    return module, kernel_path


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


def _append_record(records: list[dict[str, Any]], previous: str, body: dict[str, Any]) -> str:
    record = dict(body)
    record["previous_record_sha256"] = previous
    assert_result_namespace(record)
    raw = canonical_json_bytes(record)
    records.append(record)
    return sha256_hex(raw)


def _candidate_run(*, config, kernel, arb_type, width, radius, candidate_index,
                   records, previous):
    start = Rational.from_json(config["lambda_start"]).as_fraction()
    end = Rational.from_json(config["lambda_end"]).as_fraction()
    cells = _cell_partition(start, end, width.as_fraction(), config["max_cells"])
    tol = "1e-20"
    depth = config["max_subdivisions"]
    limit = config["evaluation_budget"]
    y_box = DyadicInterval(-radius, radius)
    anchor = _nearest_dyadic((CG_ROOT[0].as_fraction() + CG_ROOT[1].as_fraction()) / 2)
    predictors_reversed = []
    seed = anchor
    refresh = config["predictor_refresh"]
    for reverse_index, (left, right) in enumerate(reversed(cells)):
        right_iterations = 4 if reverse_index % refresh == 0 else 1
        q_right = _newton_predictor(
            kernel, arb_type, right, seed, iterations=right_iterations,
            tol=tol, depth=depth, limit=limit,
        )
        q_left = _newton_predictor(
            kernel, arb_type, left, q_right, iterations=1,
            tol=tol, depth=depth, limit=limit,
        )
        predictor = AffinePredictor(
            Rational.from_fraction(left), Rational.from_fraction(right), q_left, q_right,
        )
        predictors_reversed.append((left, right, predictor))
        seed = q_left
    predictors = list(reversed(predictors_reversed))

    previous = _append_record(records, previous, {
        "candidate_index": candidate_index, "lambda_width": width.to_json(),
        "record_type": "candidate_start", "tube_radius": radius.to_json(),
    })
    cell_passes = []
    joins_pass = True
    evaluation_count = 0
    sections = []
    for cell_index, (left, right, predictor) in enumerate(predictors):
        domain = physical_tube(predictor.range_hull(), y_box)
        reason = None
        image = DyadicInterval.point(domain.midpoint())
        residual = DyadicInterval.point(D_ZERO)
        slope = DyadicInterval.point(D_ZERO)
        preconditioner = D_ZERO
        left_margin = D_ZERO
        right_margin = D_ZERO
        passed = False
        if domain.lo <= D_ZERO or not domain.hi < Dyadic(1, 0):
            reason = "physical_tube_outside_open_unit_interval"
        else:
            lam_box = _fraction_box(left, right, arb_type)
            domain_box = _dyadic_box(domain, arb_type)
            midpoint = domain.midpoint()
            midpoint_lam = (left + right) / 2
            residual = arb_ball_to_exact_interval(kernel.F_arb(
                _dyadic_arb(midpoint, arb_type), lam_box,
                tol=tol, depth=depth, limit=limit,
            ))
            slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
                domain_box, lam_box, tol=tol, depth=depth, limit=limit,
            ))
            center_slope = arb_ball_to_exact_interval(kernel.dFdr_arb(
                _dyadic_arb(midpoint, arb_type), _rational_arb(midpoint_lam, arb_type),
                tol=tol, depth=depth, limit=limit,
            ))
            evaluation_count += 3
            preconditioner = center_slope.midpoint()
            if preconditioner == D_ZERO:
                reason = "preconditioner_zero"
            else:
                image = krawczyk_image(
                    m=midpoint, residual=residual, slope=slope,
                    preconditioner=preconditioner, domain=domain,
                )
                left_margin = image.lo - domain.lo
                right_margin = domain.hi - image.hi
                if not domain.strictly_contains(image):
                    reason = "krawczyk_not_strict"
                elif not slope.hi < D_ZERO:
                    reason = "slope_not_strictly_negative"
                else:
                    passed = True
        cell_passes.append(passed)
        sections.append((predictor, y_box))
        previous = _append_record(records, previous, {
            "candidate_index": candidate_index,
            "cell_index": cell_index,
            "evaluation_count": evaluation_count,
            "failure_reason": reason,
            "krawczyk_image": image.to_json(),
            "lambda_interval": {
                "lo": Rational.from_fraction(left).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            },
            "left_margin": left_margin.to_json(),
            "passed": passed,
            "predictor": {
                "q_left": predictor.q_left.to_json(),
                "q_right": predictor.q_right.to_json(),
                "rule": Q_RULE,
            },
            "preconditioner": preconditioner.to_json(),
            "record_type": "cell",
            "residual": residual.to_json(),
            "right_margin": right_margin.to_json(),
            "slope": slope.to_json(),
            "subdivision_count": 0,
            "tube_interval": domain.to_json(),
        })

    for join_index in range(len(sections) - 1):
        left_predictor, left_y = sections[join_index]
        right_predictor, right_y = sections[join_index + 1]
        failure = None
        width_value = D_ZERO
        try:
            intersection = exact_join_intersection(
                left_predictor.q_right, left_y, right_predictor.q_left, right_y,
            )
            width_value = intersection.hi - intersection.lo
        except SchemaError:
            intersection = DyadicInterval.point(D_ZERO)
            failure = "join_empty_or_zero_width"
            joins_pass = False
        previous = _append_record(records, previous, {
            "candidate_index": candidate_index,
            "failure_reason": failure,
            "intersection": intersection.to_json(),
            "join_index": join_index,
            "record_type": "join",
            "width": width_value.to_json(),
        })

    passed = all(cell_passes) and joins_pass and evaluation_count <= limit
    previous = _append_record(records, previous, {
        "candidate_index": candidate_index,
        "cells_attempted": len(cells),
        "cells_passed": sum(cell_passes),
        "evaluation_count": evaluation_count,
        "joins_passed": joins_pass,
        "passed": passed,
        "record_type": "candidate_end",
    })
    return passed, previous, {
        "candidate_index": candidate_index,
        "lambda_width": width.to_json(),
        "tube_radius": radius.to_json(),
    }


def run_calibration(out_dir: Path) -> int:
    assert_no_stale_inputs(out_dir)
    assert_clean_source_tree()
    assert_workflow_security()
    config, config_raw = load_config()
    kernel, kernel_path = load_production_kernel()
    from flint import arb, ctx
    ctx.dps = config["dps"]
    out_dir.mkdir(parents=True)
    (out_dir / "config.calibration.json").write_bytes(config_raw)
    records = []
    previous = chain_genesis(CHAIN_DOMAIN)
    recommendation = None
    for candidate_index, (width, radius) in enumerate(_candidate_pairs(config)):
        passed, previous, candidate = _candidate_run(
            config=config, kernel=kernel, arb_type=arb, width=width, radius=radius,
            candidate_index=candidate_index, records=records, previous=previous,
        )
        if passed and recommendation is None:
            recommendation = candidate
    state = "CALIBRATION_COMPLETE" if recommendation is not None else "CALIBRATION_INCOMPLETE"
    summary = {
        "candidate_count": len(_candidate_pairs(config)),
        "chain_tip": previous,
        "machine_conclusion": {"real_analytic": False},
        "recommendation": recommendation,
        "record_count": len(records),
        "schema": "btube-calibration-summary-v1",
        "state": state,
    }
    assert_result_namespace(summary)
    (out_dir / "calibration_records.jsonl").write_bytes(canonical_jsonl(records))
    (out_dir / "CALIBRATION_SUMMARY.json").write_bytes(canonical_json_bytes(summary))
    source_manifest = {
        "audited_source_commit": AUDITED_SOURCE_COMMIT,
        "design_commit": DESIGN_COMMIT,
        "kernel_path": kernel_path.relative_to(REPO_ROOT).as_posix(),
        "kernel_sha256": sha256_hex(kernel_path.read_bytes()),
        "schema": "btube-calibration-source-manifest-v1",
    }
    (out_dir / "SOURCE_MANIFEST.json").write_bytes(canonical_json_bytes(source_manifest))
    return 0


def _verify_records(out_dir: Path):
    config, config_raw = load_config(out_dir / "config.calibration.json")
    parsed = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    previous = chain_genesis(CHAIN_DOMAIN)
    for record, raw in parsed:
        if record.get("previous_record_sha256") != previous:
            raise CalibrationError("record chain mismatch")
        assert_result_namespace(record)
        previous = sha256_hex(raw)
    summary = parse_canonical_json_bytes(
        (out_dir / "CALIBRATION_SUMMARY.json").read_bytes(), allow_display=False,
    )
    _require_exact_keys(summary, {
        "candidate_count", "chain_tip", "machine_conclusion", "recommendation",
        "record_count", "schema", "state",
    }, "summary")
    assert_result_namespace(summary)
    if summary["schema"] != "btube-calibration-summary-v1":
        raise CalibrationError("summary schema mismatch")
    if summary["machine_conclusion"] != {"real_analytic": False}:
        raise CalibrationError("machine_conclusion must be exactly present-and-false")
    if summary["state"] not in TERMINAL_STATES:
        raise CalibrationError("invalid terminal state")
    if summary["chain_tip"] != previous or summary["record_count"] != len(parsed):
        raise CalibrationError("summary chain/count mismatch")
    ends = [record for record, _ in parsed if record.get("record_type") == "candidate_end"]
    pairs = _candidate_pairs(config)
    if len(ends) != summary["candidate_count"] or len(ends) != len(pairs):
        raise CalibrationError("candidate completeness mismatch")
    passing = [record["candidate_index"] for record in ends if record.get("passed") is True]
    expected = None
    if passing:
        first = min(passing)
        width, radius = pairs[first]
        expected = {
            "candidate_index": first,
            "lambda_width": width.to_json(),
            "tube_radius": radius.to_json(),
        }
    expected_state = "CALIBRATION_COMPLETE" if expected is not None else "CALIBRATION_INCOMPLETE"
    if summary["recommendation"] != expected or summary["state"] != expected_state:
        raise CalibrationError("deterministic recommendation mismatch")
    return config, summary, config_raw


def verify_pre(out_dir: Path, source_head: str) -> int:
    assert_clean_source_tree()
    assert_workflow_security()
    load_production_kernel()
    _, summary, config_raw = _verify_records(out_dir)
    report = {
        "config_sha256": sha256_hex(config_raw),
        "kernel_sha256": KERNEL_SHA256,
        "record_chain_tip": summary["chain_tip"],
        "schema": "btube-calibration-checker-report-v1",
        "source_head": source_head,
        "state": summary["state"],
        "verifier": "PASS",
    }
    assert_result_namespace(report)
    (out_dir / "CHECKER_REPORT.json").write_bytes(canonical_json_bytes(report))
    return 0


def _payload_files(run_dir: Path) -> dict[str, Path]:
    files = {
        "CALIBRATION_SUMMARY.json": run_dir / "CALIBRATION_SUMMARY.json",
        "CHECKER_REPORT.json": run_dir / "CHECKER_REPORT.json",
        "SOURCE_MANIFEST.json": run_dir / "SOURCE_MANIFEST.json",
        "calibration_records.jsonl": run_dir / "calibration_records.jsonl",
        "config.calibration.json": run_dir / "config.calibration.json",
        "source/.github/workflows/prolate-item2-btube-v2-1-calibration.yml": WORKFLOW_PATH,
        f"source/{KERNEL_RELATIVE.as_posix()}": REPO_ROOT / KERNEL_RELATIVE,
    }
    for relative in SOURCE_FILE_LIST:
        files[f"source/CERTIFICATES/prolate/item2_circle/b_tube_v2_1/{relative}"] = BTUBE_ROOT / relative
    return files


def _build_deterministic_zip(payload_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(item for item in payload_dir.rglob("*") if item.is_file()):
            relative = path.relative_to(payload_dir).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def deliver(run_dir: Path, delivery_dir: Path, source_head: str) -> int:
    if delivery_dir.exists():
        raise CalibrationError("delivery directory must not exist")
    _, summary, config_raw = _verify_records(run_dir)
    checker = parse_canonical_json_bytes((run_dir / "CHECKER_REPORT.json").read_bytes())
    if checker.get("verifier") != "PASS" or checker.get("source_head") != source_head:
        raise CalibrationError("pre-verifier report mismatch")
    delivery_dir.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="btube-calibration-payload-") as temporary:
        payload_dir = Path(temporary) / "payload"
        payload_dir.mkdir()
        for relative, source in sorted(_payload_files(run_dir).items()):
            target = payload_dir / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        manifest = {
            "files": {
                path.relative_to(payload_dir).as_posix(): sha256_hex(path.read_bytes())
                for path in sorted(item for item in payload_dir.rglob("*") if item.is_file())
            },
            "schema": "btube-calibration-payload-manifest-v1",
        }
        manifest_raw = canonical_json_bytes(manifest)
        manifest_path = payload_dir / "PAYLOAD_SHA256SUMS.json"
        manifest_path.write_bytes(manifest_raw)
        for relative, digest in manifest["files"].items():
            if sha256_hex((payload_dir / relative).read_bytes()) != digest:
                raise CalibrationError("payload changed after manifest creation")
        if manifest_path.read_bytes() != manifest_raw:
            raise CalibrationError("payload manifest byte mismatch")
        archive_path = delivery_dir / "btube-v2-1-calibration.zip"
        _build_deterministic_zip(payload_dir, archive_path)
        receipt = {
            "archive_name": archive_path.name,
            "archive_sha256": sha256_hex(archive_path.read_bytes()),
            "configuration_sha256": sha256_hex(config_raw),
            "kernel_file_sha256": KERNEL_SHA256,
            "payload_manifest_sha256": sha256_hex(manifest_raw),
            "schema": "btube-calibration-delivery-receipt-v1",
            "source_head": source_head,
            "state": summary["state"],
            "workflow_source_sha256": sha256_hex(WORKFLOW_PATH.read_bytes()),
        }
        assert_result_namespace(receipt)
        receipt_raw = canonical_json_bytes(receipt)
        receipt_path = delivery_dir / "DELIVERY_RECEIPT.json"
        receipt_path.write_bytes(receipt_raw)
        if receipt_path.read_bytes() != canonical_json_bytes(receipt):
            raise CalibrationError("receipt canonical-byte mismatch")
        if sha256_hex(archive_path.read_bytes()) != receipt["archive_sha256"]:
            raise CalibrationError("archive changed after receipt creation")
    return 0


def verify_final(archive_path: Path, receipt_path: Path, source_head: str) -> int:
    receipt = parse_canonical_json_bytes(receipt_path.read_bytes(), allow_display=False)
    _require_exact_keys(receipt, {
        "archive_name", "archive_sha256", "configuration_sha256",
        "kernel_file_sha256", "payload_manifest_sha256", "schema", "source_head",
        "state", "workflow_source_sha256",
    }, "receipt")
    assert_result_namespace(receipt)
    if receipt["schema"] != "btube-calibration-delivery-receipt-v1":
        raise CalibrationError("receipt schema mismatch")
    if receipt["source_head"] != source_head:
        raise CalibrationError("receipt source-head mismatch")
    if receipt["kernel_file_sha256"] != KERNEL_SHA256:
        raise CalibrationError("receipt kernel mismatch")
    if receipt["state"] not in {"CALIBRATION_COMPLETE", "CALIBRATION_INCOMPLETE"}:
        raise CalibrationError("receipt terminal state invalid")
    if receipt["archive_name"] != archive_path.name or sha256_hex(archive_path.read_bytes()) != receipt["archive_sha256"]:
        raise CalibrationError("archive byte mismatch")
    if sha256_hex(WORKFLOW_PATH.read_bytes()) != receipt["workflow_source_sha256"]:
        raise CalibrationError("workflow source mismatch")
    load_production_kernel()
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if names != sorted(names) or len(names) != len(set(names)):
            raise CalibrationError("archive paths not unique/sorted")
        manifest_raw = archive.read("PAYLOAD_SHA256SUMS.json")
        if sha256_hex(manifest_raw) != receipt["payload_manifest_sha256"]:
            raise CalibrationError("payload manifest digest mismatch")
        manifest = parse_canonical_json_bytes(manifest_raw, allow_display=False)
        _require_exact_keys(manifest, {"files", "schema"}, "payload manifest")
        if manifest["schema"] != "btube-calibration-payload-manifest-v1":
            raise CalibrationError("payload manifest schema mismatch")
        expected_names = sorted(set(manifest["files"]) | {"PAYLOAD_SHA256SUMS.json"})
        if names != expected_names:
            raise CalibrationError("archive payload file set mismatch")
        for relative, digest in manifest["files"].items():
            if sha256_hex(archive.read(relative)) != digest:
                raise CalibrationError(f"archive payload digest mismatch: {relative}")
        config_raw = archive.read("config.calibration.json")
        if sha256_hex(config_raw) != receipt["configuration_sha256"]:
            raise CalibrationError("configuration digest mismatch")
        parse_canonical_json_bytes(config_raw, allow_display=False)
        summary = parse_canonical_json_bytes(archive.read("CALIBRATION_SUMMARY.json"), allow_display=False)
        if summary.get("state") != receipt["state"]:
            raise CalibrationError("receipt/summary state mismatch")
        assert_result_namespace(summary)
    return 0


def assert_no_workflow_in_result_merge(changed_paths: Iterable[str]) -> None:
    workflow = ".github/workflows/prolate-item2-btube-v2-1-calibration.yml"
    if workflow in set(changed_paths):
        raise CalibrationError("temporary calibration workflow survives result merge")


def verify_config_only() -> int:
    load_config()
    assert_clean_source_tree()
    assert_workflow_security()
    load_production_kernel()
    return 0


def _main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--out", type=Path, required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--phase", choices=("pre", "final"), required=True)
    verify_parser.add_argument("--source-head", required=True)
    verify_parser.add_argument("--out", type=Path)
    verify_parser.add_argument("--archive", type=Path)
    verify_parser.add_argument("--receipt", type=Path)
    deliver_parser = subparsers.add_parser("deliver")
    deliver_parser.add_argument("--out", type=Path, required=True)
    deliver_parser.add_argument("--delivery", type=Path, required=True)
    deliver_parser.add_argument("--source-head", required=True)
    subparsers.add_parser("verify-config")
    args = parser.parse_args()
    if args.command == "run":
        return run_calibration(args.out)
    if args.command == "deliver":
        return deliver(args.out, args.delivery, args.source_head)
    if args.command == "verify-config":
        return verify_config_only()
    if args.phase == "pre":
        if args.out is None:
            raise CalibrationError("--out is required for pre verification")
        return verify_pre(args.out, args.source_head)
    if args.archive is None or args.receipt is None:
        raise CalibrationError("--archive and --receipt are required for final verification")
    return verify_final(args.archive, args.receipt, args.source_head)


if __name__ == "__main__":
    try:
        raise SystemExit(_main())
    except (CalibrationError, SchemaError, OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f"CALIBRATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
