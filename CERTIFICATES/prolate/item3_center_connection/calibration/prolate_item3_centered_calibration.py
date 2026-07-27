#!/usr/bin/env python3
"""Fail-closed centered-form calibration for item 3 C-G-TUBE.

For a fixed ``lambda`` and base point ``m``, each radius ``rad`` records

* a rigorous Arb enclosure of ``G'(m)``;
* a rigorous Arb enclosure of the raw-ball ``G''`` evaluation on
  ``I = m + [-rad, rad]``;
* ``C = upper(abs(G''(I)))``;
* ``slack = C * rad``;
* the strict Arb verdict ``slack < lower(abs(G'(m)))``.

No binary float participates in a certification decision. Existing reports are
accepted only when the complete run metadata and both dependency SHA-256 values
match. Use ``--fresh`` to replace a legacy or intentionally discarded report,
and ``--force-recompute`` to replace selected radii under matching metadata.

Typical resumable run::

    python3 prolate_item3_centered_calibration.py --fresh --rads 1/256
    python3 prolate_item3_centered_calibration.py --rads 1/1024
    python3 prolate_item3_centered_calibration.py --rads 1/4096
    python3 prolate_item3_centered_calibration.py --verify-only
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path
from typing import Any

from flint import arb, ctx

import prolate_circle_F_cleanroom as K
import prolate_circle_Frr_ext as X

SCHEMA_VERSION = 2
LABEL = "item3_centered_form_calibration"
DEFAULT_REPORT = Path("item3_centered_calibration.json")
BASE_KERNEL_SHA256 = (
    "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
)
FRR_KERNEL_SHA256 = (
    "223b7007c9e077b204612fb1ff669b4147a2aa0f9c941cc8e83e81efd975e757"
)


class CalibrationError(RuntimeError):
    """Fail-closed input, provenance, or report-consistency error."""


def qe(x: Fr) -> arb:
    """Convert an exact rational to Arb without a binary-float round trip."""
    return arb(str(x.numerator)) / arb(str(x.denominator))


def normalize_fraction(text: str, *, name: str) -> Fr:
    try:
        return Fr(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise CalibrationError(f"invalid {name}: {text!r}") from exc


def module_source_path(module: Any) -> Path:
    source = inspect.getsourcefile(module)
    candidate = source or getattr(module, "__file__", None)
    if not candidate:
        raise CalibrationError(f"cannot resolve source path for {module.__name__}")
    path = Path(candidate).resolve()
    if not path.is_file():
        raise CalibrationError(f"dependency source is not a file: {path}")
    return path


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_dependencies() -> dict[str, dict[str, str]]:
    specs = (
        ("base", K, BASE_KERNEL_SHA256),
        ("frr", X, FRR_KERNEL_SHA256),
    )
    result: dict[str, dict[str, str]] = {}
    for key, module, expected in specs:
        path = module_source_path(module)
        actual = file_sha256(path)
        if actual != expected:
            raise CalibrationError(
                f"{key} dependency SHA-256 mismatch: expected {expected}, "
                f"got {actual} at {path}"
            )
        result[key] = {
            "module": path.name,
            "sha256": actual,
            "runtime_path": str(path),
        }
    return result


def expected_metadata(args: argparse.Namespace,
                      lam_f: Fr,
                      m_f: Fr,
                      dependencies: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "label": LABEL,
        "lambda": str(lam_f),
        "m": str(m_f),
        "dependencies": {
            key: {"module": value["module"], "sha256": value["sha256"]}
            for key, value in dependencies.items()
        },
        "settings": {
            "dps": args.dps,
            "tol_point": args.tol_point,
            "tol_box": args.tol_box,
            "depth": args.depth,
            "limit": args.limit,
        },
    }


def new_report(metadata: dict[str, Any]) -> dict[str, Any]:
    report = dict(metadata)
    report.update({
        "G_prime_m_ball": None,
        "G_prime_m_endpoints": None,
        "rows": [],
    })
    return report


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise CalibrationError(f"cannot read valid JSON report {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CalibrationError("report root must be a JSON object")
    return value


def validate_metadata(report: dict[str, Any], expected: dict[str, Any]) -> None:
    if report.get("schema_version") != SCHEMA_VERSION:
        raise CalibrationError(
            "report schema mismatch or legacy report; rerun with --fresh"
        )
    for key in ("label", "lambda", "m", "dependencies", "settings"):
        if report.get(key) != expected[key]:
            raise CalibrationError(
                f"resume metadata mismatch for {key}: "
                f"stored={report.get(key)!r}, requested={expected[key]!r}"
            )


def atomic_write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, separators=(",", ":"), ensure_ascii=False).encode()
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    os.replace(tmp, path)


def sign_and_abs_lower(x: arb) -> tuple[str, arb]:
    zero = arb(0)
    if bool(x < zero):
        return "negative", abs(x).lower()
    if bool(x > zero):
        return "positive", abs(x).lower()
    return "unresolved", zero


def compute_g_prime_m(r_m: arb, lam: arb, args: argparse.Namespace) -> arb:
    fm = K.F_arb(
        r_m, lam, tol=args.tol_point,
        depth=args.depth + 1, limit=args.limit * 2,
    )
    frm = K.dFdr_arb(
        r_m, lam, tol=args.tol_point,
        depth=args.depth + 1, limit=args.limit * 2,
    )
    return frm / r_m - fm / (r_m * r_m)


def compute_row(rad_f: Fr,
                r_m: arb,
                lam: arb,
                gpm: arb,
                args: argparse.Namespace) -> dict[str, Any]:
    rad = qe(rad_f)
    r_box = r_m + rad * arb("+/- 1.0")
    fb = K.F_arb(
        r_box, lam, tol=args.tol_box,
        depth=args.depth, limit=args.limit,
    )
    frb = K.dFdr_arb(
        r_box, lam, tol=args.tol_box,
        depth=args.depth, limit=args.limit,
    )
    frrb = X.Frr_arb(
        r_box, lam, tol=args.tol_box,
        depth=args.depth, limit=args.limit,
    )
    gpp = frrb / r_box - 2 * frb / (r_box * r_box) + 2 * fb / (r_box ** 3)
    c_bound = abs(gpp).upper()
    slack_bound = c_bound * rad
    sign, gp_abs_lower = sign_and_abs_lower(gpm)
    certified = sign != "unresolved" and bool(slack_bound < gp_abs_lower)
    return {
        "rad": str(rad_f),
        "cell_width": str(2 * rad_f),
        "r_box": [str((r_m - rad).lower()), str((r_m + rad).upper())],
        "G_pp_ball": str(gpp),
        "G_pp_endpoints": [str(gpp.lower()), str(gpp.upper())],
        "C_bound": str(c_bound),
        "slack_bound": str(slack_bound),
        "G_prime_sign": sign,
        "G_prime_abs_lower_bound": str(gp_abs_lower),
        "comparison": "slack_bound < G_prime_abs_lower_bound (strict Arb)",
        "sign_certified": certified,
    }


def validate_report_rows(report: dict[str, Any], m_f: Fr) -> tuple[int, int]:
    ball_text = report.get("G_prime_m_ball")
    if not isinstance(ball_text, str):
        raise CalibrationError("missing G_prime_m_ball")
    gpm = arb(ball_text)
    sign, gp_abs_lower = sign_and_abs_lower(gpm)
    rows = report.get("rows")
    if not isinstance(rows, list):
        raise CalibrationError("rows must be a list")

    seen: set[str] = set()
    passed = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CalibrationError(f"row {index} is not an object")
        rad_f = normalize_fraction(str(row.get("rad", "")), name=f"row {index} rad")
        rad_key = str(rad_f)
        if row.get("rad") != rad_key:
            raise CalibrationError(f"row {index} radius is not normalized: {row.get('rad')!r}")
        if rad_key in seen:
            raise CalibrationError(f"duplicate radius in report: {rad_key}")
        seen.add(rad_key)
        if rad_f <= 0 or rad_f >= m_f:
            raise CalibrationError(f"row {index} radius must satisfy 0 < rad < m")
        if row.get("cell_width") != str(2 * rad_f):
            raise CalibrationError(f"row {index} cell_width mismatch")

        gpp_text = row.get("G_pp_ball")
        if not isinstance(gpp_text, str):
            raise CalibrationError(f"row {index} missing G_pp_ball")
        gpp = arb(gpp_text)
        c_bound = abs(gpp).upper()
        slack_bound = c_bound * qe(rad_f)
        computed = sign != "unresolved" and bool(slack_bound < gp_abs_lower)
        if row.get("G_prime_sign") != sign:
            raise CalibrationError(f"row {index} G_prime_sign mismatch")
        if row.get("sign_certified") is not computed:
            raise CalibrationError(f"row {index} sign_certified mismatch")
        if computed:
            passed += 1
    return len(rows), passed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rads", nargs="*", default=[])
    parser.add_argument("--lam", default="118/25")
    parser.add_argument("--m", default="11/256")
    parser.add_argument("--dps", type=int, default=25)
    parser.add_argument("--tol-point", default="1e-8")
    parser.add_argument("--tol-box", default="1e-6")
    parser.add_argument("--depth", type=int, default=8)
    parser.add_argument("--limit", type=int, default=60000)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--force-recompute", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.fresh and args.force_recompute:
            raise CalibrationError("--fresh and --force-recompute are mutually exclusive")
        if args.verify_only and (args.fresh or args.force_recompute or args.rads):
            raise CalibrationError("--verify-only cannot be combined with writes or radii")
        if not args.verify_only and not args.rads:
            raise CalibrationError("at least one --rads value is required")
        if args.dps <= 0 or args.depth <= 0 or args.limit <= 0:
            raise CalibrationError("dps, depth, and limit must be positive")

        lam_f = normalize_fraction(args.lam, name="lambda")
        m_f = normalize_fraction(args.m, name="m")
        if lam_f <= 0 or m_f <= 0:
            raise CalibrationError("lambda and m must be positive")

        normalized_rads: list[Fr] = []
        seen_inputs: set[str] = set()
        for raw in args.rads:
            rad_f = normalize_fraction(raw, name="radius")
            if rad_f <= 0 or rad_f >= m_f:
                raise CalibrationError(f"radius must satisfy 0 < rad < m: {raw}")
            key = str(rad_f)
            if key not in seen_inputs:
                seen_inputs.add(key)
                normalized_rads.append(rad_f)

        ctx.dps = args.dps
        dependencies = verify_dependencies()
        metadata = expected_metadata(args, lam_f, m_f, dependencies)
        report_path = args.report.resolve()

        if args.verify_only:
            if not report_path.exists():
                raise CalibrationError(f"report does not exist: {report_path}")
            report = load_json(report_path)
            validate_metadata(report, metadata)
            total, passed = validate_report_rows(report, m_f)
            print(f"VERIFIED rows={total} sign_certified={passed}")
            return 0

        if args.fresh or not report_path.exists():
            report = new_report(metadata)
        else:
            report = load_json(report_path)
            validate_metadata(report, metadata)

        lam, r_m = qe(lam_f), qe(m_f)
        if args.force_recompute or report.get("G_prime_m_ball") is None:
            gpm = compute_g_prime_m(r_m, lam, args)
            report["G_prime_m_ball"] = str(gpm)
            report["G_prime_m_endpoints"] = [str(gpm.lower()), str(gpm.upper())]
        else:
            gpm = arb(report["G_prime_m_ball"])

        existing: dict[str, dict[str, Any]] = {}
        for row in report.get("rows", []):
            key = str(normalize_fraction(str(row.get("rad", "")), name="stored radius"))
            if key in existing:
                raise CalibrationError(f"duplicate stored radius: {key}")
            existing[key] = row

        for rad_f in normalized_rads:
            key = str(rad_f)
            if key in existing and not args.force_recompute:
                continue
            existing[key] = compute_row(rad_f, r_m, lam, gpm, args)

        report["rows"] = sorted(
            existing.values(),
            key=lambda row: normalize_fraction(row["rad"], name="stored radius"),
            reverse=True,
        )
        total, passed = validate_report_rows(report, m_f)
        atomic_write_json(report_path, report)
        for row in report["rows"]:
            print(
                f"rad={row['rad']} C={row['C_bound']} "
                f"slack={row['slack_bound']} certified={row['sign_certified']}"
            )
        print(f"VERIFIED rows={total} sign_certified={passed}")
        return 0
    except CalibrationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
