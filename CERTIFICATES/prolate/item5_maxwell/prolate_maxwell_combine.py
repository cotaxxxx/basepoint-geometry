#!/usr/bin/env python3
"""Combine parallel item 5 component enclosures into one certificate."""
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

    lo = fmpq(171743, 50000)
    hi = fmpq(85872, 25000)
    box = arb((lo + hi) / 2, (hi - lo) / 2)
    mid = arb(fmpq(343487, 100000))
    newton = mid - D_mid / Dp

    conditions = {
        "D(lambda_lo) > 0": bool(D_lo > 0 and lower["D"]["imag_contains_zero"]),
        "D(lambda_hi) < 0": bool(D_hi < 0 and upper["D"]["imag_contains_zero"]),
        "D'(I) < 0": bool(Dp < 0 and derivative["D_prime"]["imag_contains_zero"]),
        "D(lambda_mid) real": bool(midpoint["D"]["imag_contains_zero"]),
        "interval Newton image strictly inside I": bool(
            newton.lower() > box.lower() and newton.upper() < box.upper()
        ),
    }

    result = {
        "status": "CERTIFIED" if all(conditions.values()) else "FAILED_OR_INCONCLUSIVE",
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
        },
        "arithmetic": "python-flint Arb/Acb ball arithmetic; parallel component run",
        "lambda_bracket": "[3.43486, 3.43488]",
        "conditions": conditions,
        "values": {
            "D_at_lower": lower["D"],
            "D_at_upper": upper["D"],
            "D_at_midpoint": midpoint["D"],
            "D_prime_on_interval": derivative["D_prime"],
            "interval_newton_image": arb_record(newton),
            "E_center_at_midpoint": midpoint["E_center"],
            "E_boundary_at_midpoint": midpoint["E_boundary"],
            "E_center_prime_on_interval": derivative["E_center_prime"],
            "E_boundary_prime_on_interval": derivative["E_boundary_prime"],
        },
        "certified_conclusion": (
            "If status is CERTIFIED, D(lambda)=E_lambda(1,0)-E_lambda(0,0) "
            "has exactly one zero lambda_cross in [3.43486,3.43488], "
            "D'(lambda_cross)<0, and the boundary and center values cross transversely."
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
    raise SystemExit(0 if result["status"] == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
