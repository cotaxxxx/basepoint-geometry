#!/usr/bin/env python3
"""Canonicalize and verify schema-v2 centered calibration from endpoint balls.

The lower/upper endpoint strings are the authoritative stored enclosures.
Compact ``str(arb)`` display balls are regenerated from them, preventing any
precision loss across resumable invocations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path
from typing import Any

from flint import arb

SCHEMA_VERSION = 2
BASE_SHA = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
FRR_SHA = "223b7007c9e077b204612fb1ff669b4147a2aa0f9c941cc8e83e81efd975e757"


class VerifyError(RuntimeError):
    pass


def qe(x: Fr) -> arb:
    return arb(str(x.numerator)) / arb(str(x.denominator))


def endpoints_ball(value: Any, where: str) -> arb:
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(v, str) for v in value):
        raise VerifyError(f"{where}: expected two endpoint strings")
    lo, hi = arb(value[0]), arb(value[1])
    if bool(lo > hi):
        raise VerifyError(f"{where}: reversed endpoints")
    return (lo + hi) / 2 + ((hi - lo) / 2) * arb("+/- 1.0")


def sign_lower(x: arb) -> tuple[str, arb]:
    zero = arb(0)
    if bool(x < zero):
        return "negative", abs(x).lower()
    if bool(x > zero):
        return "positive", abs(x).lower()
    return "unresolved", zero


def canonicalize(report: dict[str, Any], rewrite: bool) -> tuple[int, int]:
    if report.get("schema_version") != SCHEMA_VERSION:
        raise VerifyError("schema_version must be 2")
    deps = report.get("dependencies")
    expected_deps = {
        "base": {"module": "prolate_circle_F_cleanroom.py", "sha256": BASE_SHA},
        "frr": {"module": "prolate_circle_Frr_ext.py", "sha256": FRR_SHA},
    }
    if deps != expected_deps:
        raise VerifyError("dependency metadata mismatch")
    try:
        m_f = Fr(report["m"])
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise VerifyError("invalid m") from exc

    gpm = endpoints_ball(report.get("G_prime_m_endpoints"), "G_prime_m_endpoints")
    sign, gp_lb = sign_lower(gpm)
    gpm_text = str(gpm)
    if rewrite:
        report["G_prime_m_ball"] = gpm_text
    elif report.get("G_prime_m_ball") != gpm_text:
        raise VerifyError("noncanonical G_prime_m_ball")

    rows = report.get("rows")
    if not isinstance(rows, list):
        raise VerifyError("rows must be a list")
    seen: set[str] = set()
    passed = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise VerifyError(f"row {index}: not an object")
        try:
            rad_f = Fr(row["rad"])
        except (KeyError, ValueError, ZeroDivisionError) as exc:
            raise VerifyError(f"row {index}: invalid rad") from exc
        rad_key = str(rad_f)
        if row.get("rad") != rad_key or rad_key in seen:
            raise VerifyError(f"row {index}: noncanonical or duplicate rad")
        seen.add(rad_key)
        if rad_f <= 0 or rad_f >= m_f:
            raise VerifyError(f"row {index}: require 0 < rad < m")

        gpp = endpoints_ball(row.get("G_pp_endpoints"), f"row {index} G_pp_endpoints")
        c_bound = abs(gpp).upper()
        slack = c_bound * qe(rad_f)
        verdict = sign != "unresolved" and bool(slack < gp_lb)
        fields = {
            "cell_width": str(2 * rad_f),
            "G_pp_ball": str(gpp),
            "C_bound": str(c_bound),
            "slack_bound": str(slack),
            "G_prime_sign": sign,
            "G_prime_abs_lower_bound": str(gp_lb),
            "comparison": "slack_bound < G_prime_abs_lower_bound (strict Arb)",
            "sign_certified": verdict,
        }
        if rewrite:
            row.update(fields)
        else:
            for key, value in fields.items():
                if row.get(key) != value:
                    raise VerifyError(f"row {index}: noncanonical {key}")
        passed += int(verdict)
    return len(rows), passed


def write_atomic(path: Path, report: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(json.dumps(report, separators=(",", ":")).encode())
    os.replace(tmp, path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("item3_centered_calibration.json"))
    parser.add_argument("--rewrite", action="store_true")
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_bytes())
        if not isinstance(report, dict):
            raise VerifyError("report root must be an object")
        total, passed = canonicalize(report, args.rewrite)
        if args.rewrite:
            write_atomic(args.report, report)
        print(f"CANONICAL rows={total} sign_certified={passed}")
        return 0
    except (OSError, json.JSONDecodeError, VerifyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
