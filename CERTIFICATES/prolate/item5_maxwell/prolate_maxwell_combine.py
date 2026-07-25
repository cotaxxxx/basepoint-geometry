#!/usr/bin/env python3
"""Combine item 5 component enclosures into Stage 5a/5b certificates."""
from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path

import flint
from flint import arb, ctx, fmpq


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load(name: str) -> dict:
    return json.loads(Path("components", f"component_{name}.json").read_text())


def parse_real(record: dict) -> arb:
    return arb(record["real_ball"])


def arb_record(x: arb) -> dict:
    return {"ball": str(x), "lower": str(x.lower()), "upper": str(x.upper())}


def main() -> None:
    ctx.dps = 50
    lower = load("lower")
    upper = load("upper")
    midpoint = load("midpoint")
    derivative = load("derivative")

    D_lo = parse_real(lower["D"])
    D_hi = parse_real(upper["D"])
    D_mid = parse_real(midpoint["D"])
    Dp = parse_real(derivative["D_prime"])

    lo = fmpq(1717, 500)
    hi = fmpq(1718, 500)
    box = arb((lo + hi) / 2, (hi - lo) / 2)
    mid = arb(fmpq(687, 200))

    stage_5a_conditions = {
        "D(3.434) > 0": bool(D_lo > 0 and lower["D"]["imag_contains_zero"]),
        "D(3.436) < 0": bool(D_hi < 0 and upper["D"]["imag_contains_zero"]),
        "D'([3.434,3.436]) < 0": bool(
            Dp < 0 and derivative["D_prime"]["imag_contains_zero"]
        ),
    }
    stage_5a_certified = all(stage_5a_conditions.values())

    derivative_excludes_zero = bool(0 not in Dp)
    newton = mid - D_mid / Dp if derivative_excludes_zero else box
    newton_inside = bool(
        derivative_excludes_zero
        and newton.lower() > box.lower()
        and newton.upper() < box.upper()
    )
    stage_5b_conditions = {
        "D(3.435) real": bool(midpoint["D"]["imag_contains_zero"]),
        "D'(I5) excludes zero": derivative_excludes_zero,
        "Newton image strictly inside I5": newton_inside,
    }
    stage_5b_certified = stage_5a_certified and all(stage_5b_conditions.values())

    result = {
        "status": "CERTIFIED" if stage_5a_certified else "FAILED_OR_INCONCLUSIVE",
        "stage_5a_status": "CERTIFIED" if stage_5a_certified else "FAILED_OR_INCONCLUSIVE",
        "stage_5b_status": "CERTIFIED" if stage_5b_certified else "INCONCLUSIVE",
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
        },
        "arithmetic": "python-flint Arb/Acb ball arithmetic; four-band boundary integration",
        "stage_5a_bracket": "[3.434, 3.436]",
        "stage_5a_bracket_exact": "[1717/500, 1718/500]",
        "stage_5b_midpoint": "3.435 = 687/200",
        "stage_5a_conditions": stage_5a_conditions,
        "stage_5b_conditions": stage_5b_conditions,
        "values": {
            "D_at_lower": lower["D"],
            "D_at_upper": upper["D"],
            "D_at_midpoint": midpoint["D"],
            "D_prime_on_stage_5a_interval": derivative["D_prime"],
            "interval_newton_image": arb_record(newton),
            "E_center_at_midpoint": midpoint["E_center"],
            "E_boundary_at_midpoint": midpoint["E_boundary"],
            "E_center_prime_on_interval": derivative["E_center_prime"],
            "E_boundary_prime_on_interval": derivative["E_boundary_prime"],
        },
        "certified_conclusion": (
            "If stage_5a_status is CERTIFIED, D(lambda)=E_lambda(1,0)-E_lambda(0,0) "
            "has exactly one simple zero lambda_cross in [3.434,3.436], with "
            "D'(lambda_cross)<0 and transverse boundary/center value crossing. "
            "If stage_5b_status is also CERTIFIED, the interval-Newton image is a "
            "strictly smaller certified enclosure of lambda_cross."
        ),
        "components": {
            "lower": lower,
            "upper": upper,
            "midpoint": midpoint,
            "derivative": derivative,
        },
        "noncertified_reference": {
            "lambda_cross": "3.43486844286684...",
            "common_energy": "0.64287764254486...",
            "D_prime_at_root": "-0.07195990796855...",
        },
    }

    out = Path("prolate_maxwell_arb_certificate.json")
    result["script_sha256"] = sha256_file(Path(__file__))
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    out.with_suffix(out.suffix + ".sha256").write_text(
        f"{sha256_file(Path(__file__))}  {Path(__file__).name}\n"
        f"{sha256_file(out)}  {out.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if stage_5a_certified else 1)


if __name__ == "__main__":
    main()
