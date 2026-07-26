#!/usr/bin/env python3
"""Rigorous Arb/Acb certificate for the prolate boundary Maxwell transition.

Target
------
Let
    D(lambda) = E_lambda(1,0) - E_lambda(0,0),
where r=1 is the equatorial boundary point and r=0 is the center.
The script is designed to certify on the exact rational bracket
    I = [3.43486, 3.43488]
that
    D(3.43486) > 0,
    D(3.43488) < 0,
    D'(I) < 0,
and that an interval-Newton image based at 3.43487 lies strictly inside I.
These statements prove a unique simple Maxwell parameter lambda_cross in I.

The center energy is a one-dimensional integral. The boundary energy is a
regularized two-dimensional quarter-sphere integral in the same half-angle
coordinates used by the boundary-entry certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Callable

import flint
from flint import acb, arb, ctx, fmpq


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def closed_rational_interval(
    lo_p: int, lo_q: int, hi_p: int, hi_q: int
) -> arb:
    lo = fmpq(lo_p, lo_q)
    hi = fmpq(hi_p, hi_q)
    return arb((lo + hi) / 2, (hi - lo) / 2)


def acb_record(x: acb) -> dict:
    return {
        "real_ball": str(x.real),
        "real_lower": str(x.real.lower()),
        "real_upper": str(x.real.upper()),
        "imag_ball": str(x.imag),
        "imag_contains_zero": bool(0 in x.imag),
    }


def arb_record(x: arb) -> dict:
    return {
        "ball": str(x),
        "lower": str(x.lower()),
        "upper": str(x.upper()),
    }


def regular_angle_data(c: acb) -> tuple[acb, acb]:
    """Return f(c)=acos(c)^2 and f'(c), with removable endpoints regularized."""
    one = acb(1)
    z = (one - c) / 2
    H = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    f = 4 * z * H * H
    S = (-f / 4).hypgeom_0f1(acb(3) / 2)
    f1 = -2 / S
    return f, f1


def rigorous_integral_1d(
    kernel: Callable[[acb, bool], acb],
    tol: arb,
    depth: int,
    eval_limit: int,
) -> acb:
    return acb.integral(
        kernel,
        0,
        1,
        abs_tol=tol,
        rel_tol=tol,
        depth_limit=depth,
        eval_limit=eval_limit,
    )


def rigorous_integral_2d(
    kernel: Callable[[acb, acb, bool], acb],
    tol: arb,
    depth: int,
    eval_limit: int,
) -> acb:
    upper_phi = acb(arb.pi() / 2)

    def outer(phi: acb, analytic_phi: bool) -> acb:
        def inner(t: acb, analytic_t: bool) -> acb:
            return kernel(t, phi, analytic_phi and analytic_t)

        return acb.integral(
            inner,
            0,
            1,
            abs_tol=tol,
            rel_tol=tol,
            depth_limit=depth,
            eval_limit=eval_limit,
        )

    return acb.integral(
        outer,
        0,
        upper_phi,
        abs_tol=tol,
        rel_tol=tol,
        depth_limit=depth,
        eval_limit=eval_limit,
    )


def center_values(
    lam_value: arb,
    tol: arb,
    depth: int,
    eval_limit: int,
) -> tuple[acb, acb]:
    lam = acb(lam_value)

    def energy_kernel(x: acb, analytic: bool) -> acb:
        x2 = x * x
        ell = 1 + (lam * lam - 1) * x2
        w2 = lam * lam * (1 - x2) + x2
        c = lam / (ell * w2).sqrt(analytic=analytic)
        f, _ = regular_angle_data(c)
        return f

    def derivative_kernel(x: acb, analytic: bool) -> acb:
        x2 = x * x
        ell = 1 + (lam * lam - 1) * x2
        w2 = lam * lam * (1 - x2) + x2
        c = lam / (ell * w2).sqrt(analytic=analytic)
        _, f1 = regular_angle_data(c)
        c_lam = c * (
            1 / lam
            - lam * x2 / ell
            - lam * (1 - x2) / w2
        )
        return f1 * c_lam

    return (
        rigorous_integral_1d(energy_kernel, tol, depth, eval_limit),
        rigorous_integral_1d(derivative_kernel, tol, depth, eval_limit),
    )


def boundary_values(
    lam_value: arb,
    tol: arb,
    depth: int,
    eval_limit: int,
) -> tuple[acb, acb]:
    lam = acb(lam_value)

    def geometry(t: acb, phi: acb, analytic: bool) -> dict[str, acb]:
        t2 = t * t
        a = 1 - 2 * t2
        s2 = phi.sin() ** 2
        c2 = 1 - s2
        L2 = c2 + lam * lam * s2
        J2 = c2 + s2 / (lam * lam)
        R2 = t2 + (1 - t2) * L2
        eta2 = a * a + 4 * t2 * (1 - t2) * J2
        R = R2.sqrt(analytic=analytic)
        eta = eta2.sqrt(analytic=analytic)
        c = t / (eta * R)
        return {
            "t2": t2,
            "s2": s2,
            "R2": R2,
            "eta2": eta2,
            "c": c,
        }

    def energy_kernel(t: acb, phi: acb, analytic: bool) -> acb:
        g = geometry(t, phi, analytic)
        f, _ = regular_angle_data(g["c"])
        # Desired boundary energy is (8/pi) int int t^3 f dt dphi.
        return 8 * t**3 * f / acb(arb.pi())

    def derivative_kernel(t: acb, phi: acb, analytic: bool) -> acb:
        g = geometry(t, phi, analytic)
        _, f1 = regular_angle_data(g["c"])
        R2_lam = 2 * lam * (1 - g["t2"]) * g["s2"]
        eta2_lam = (
            -8 * g["t2"] * (1 - g["t2"]) * g["s2"] / lam**3
        )
        c_lam = -g["c"] * (
            R2_lam / g["R2"] + eta2_lam / g["eta2"]
        ) / 2
        return 8 * t**3 * f1 * c_lam / acb(arb.pi())

    return (
        rigorous_integral_2d(energy_kernel, tol, depth, eval_limit),
        rigorous_integral_2d(derivative_kernel, tol, depth, eval_limit),
    )


def D_values(
    lam_value: arb,
    tol: arb,
    depth: int,
    eval_limit: int,
) -> tuple[acb, acb, acb, acb]:
    E0, E0p = center_values(lam_value, tol, depth, eval_limit)
    E1, E1p = boundary_values(lam_value, tol, depth, eval_limit)
    return E1 - E0, E1p - E0p, E0, E1


def run(dps: int, tolerance: str, depth: int, eval_limit: int) -> dict:
    ctx.dps = dps
    tol = arb(tolerance)

    lam_lo = arb(fmpq(171743, 50000))   # 3.43486
    lam_hi = arb(fmpq(85872, 25000))    # 3.43488
    lam_mid = arb(fmpq(343487, 100000)) # 3.43487
    lam_I = closed_rational_interval(171743, 50000, 85872, 25000)

    D_lo, _, E0_lo, E1_lo = D_values(lam_lo, tol, depth, eval_limit)
    D_hi, _, E0_hi, E1_hi = D_values(lam_hi, tol, depth, eval_limit)
    D_mid, _, E0_mid, E1_mid = D_values(lam_mid, tol, depth, eval_limit)
    _, Dp_I, E0_I, E1_I = D_values(lam_I, tol, depth, eval_limit)

    newton = lam_mid - D_mid.real / Dp_I.real
    newton_inside = bool(
        newton.lower() > lam_I.lower()
        and newton.upper() < lam_I.upper()
    )

    conditions = {
        "D(lambda_lo) > 0": bool(D_lo.real > 0 and 0 in D_lo.imag),
        "D(lambda_hi) < 0": bool(D_hi.real < 0 and 0 in D_hi.imag),
        "D'(I) < 0": bool(Dp_I.real < 0 and 0 in Dp_I.imag),
        "D(lambda_mid) real": bool(0 in D_mid.imag),
        "interval Newton image strictly inside I": newton_inside,
    }

    status = "CERTIFIED" if all(conditions.values()) else "FAILED_OR_INCONCLUSIVE"
    return {
        "status": status,
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
        },
        "arithmetic": "python-flint Arb/Acb ball arithmetic",
        "decimal_precision": dps,
        "integration_tolerance": tolerance,
        "lambda_bracket": "[3.43486, 3.43488]",
        "conditions": conditions,
        "values": {
            "lambda_interval": arb_record(lam_I),
            "D_at_lower": acb_record(D_lo),
            "D_at_upper": acb_record(D_hi),
            "D_at_midpoint": acb_record(D_mid),
            "D_prime_on_interval": acb_record(Dp_I),
            "interval_newton_image": arb_record(newton),
            "E_center_at_midpoint": acb_record(E0_mid),
            "E_boundary_at_midpoint": acb_record(E1_mid),
            "E_center_on_interval": acb_record(E0_I),
            "E_boundary_on_interval": acb_record(E1_I),
            "endpoint_energy_records": {
                "center_lower": acb_record(E0_lo),
                "boundary_lower": acb_record(E1_lo),
                "center_upper": acb_record(E0_hi),
                "boundary_upper": acb_record(E1_hi),
            },
        },
        "certified_conclusion": (
            "If status is CERTIFIED, D has exactly one zero lambda_cross "
            "in [3.43486,3.43488], D'(lambda_cross)<0, and the boundary "
            "and center critical values cross transversely there."
        ),
        "formulas": {
            "D": "E_lambda(1,0)-E_lambda(0,0)",
            "center": "int_0^1 acos(lambda/sqrt(ell*w2))^2 dx",
            "ell": "1+(lambda^2-1)x^2",
            "w2": "lambda^2(1-x^2)+x^2",
            "boundary": "(8/pi) int_0^(pi/2) int_0^1 t^3 acos(c)^2 dt dphi",
            "boundary_c": "t/(eta*R) in the boundary-entry half-angle chart",
        },
        "noncertified_reference": {
            "lambda_cross": "3.4348684428668...",
            "common_energy": "0.64287764254486...",
            "D_prime_at_root": "-0.07195990796855...",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dps", type=int, default=70)
    parser.add_argument("--tolerance", default="1e-22")
    parser.add_argument("--depth-limit", type=int, default=28)
    parser.add_argument("--eval-limit", type=int, default=500000)
    parser.add_argument("--json", default="prolate_maxwell_arb_certificate.json")
    args = parser.parse_args()

    result = run(args.dps, args.tolerance, args.depth_limit, args.eval_limit)
    result["script_sha256"] = sha256_file(Path(__file__))
    output = Path(args.json)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{sha256_file(Path(__file__))}  {Path(__file__).name}\n"
        f"{sha256_file(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
