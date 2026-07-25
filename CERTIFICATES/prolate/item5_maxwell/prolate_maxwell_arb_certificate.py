#!/usr/bin/env python3
"""Serial Arb/Acb reference certificate for prolate item 5.

Stage 5a certifies a unique simple zero of
    D(lambda) = E_lambda(1,0) - E_lambda(0,0)
on the exact rational bracket [1717/500, 1718/500].

Stage 5b applies one interval-Newton step at 687/200 to obtain a smaller
certified enclosure. The production workflow replaces ``integral_2d`` with a
four-band phi-partitioned implementation, but uses the same kernels.
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


def closed_interval(lo_p: int, lo_q: int, hi_p: int, hi_q: int) -> arb:
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
    return {"ball": str(x), "lower": str(x.lower()), "upper": str(x.upper())}


def angle_data(c: acb) -> tuple[acb, acb]:
    """Return f(c)=acos(c)^2 and f'(c), regular at alignment endpoints."""
    one = acb(1)
    z = (one - c) / 2
    H = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    f = 4 * z * H * H
    S = (-f / 4).hypgeom_0f1(acb(3) / 2)
    return f, -2 / S


def integral_1d(
    kernel: Callable[[acb, bool], acb], tol: arb, depth: int, limit: int
) -> acb:
    return acb.integral(
        kernel,
        0,
        1,
        abs_tol=tol,
        rel_tol=tol,
        depth_limit=depth,
        eval_limit=limit,
    )


def integral_2d(
    kernel: Callable[[acb, acb, bool], acb],
    tol: arb,
    depth: int,
    limit: int,
) -> acb:
    upper = acb(arb.pi() / 2)

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
            eval_limit=limit,
        )

    return acb.integral(
        outer,
        0,
        upper,
        abs_tol=tol,
        rel_tol=tol,
        depth_limit=depth,
        eval_limit=limit,
    )


def center_energy(lam_value: arb, tol: arb, depth: int, limit: int) -> acb:
    lam = acb(lam_value)

    def kernel(x: acb, analytic: bool) -> acb:
        x2 = x * x
        ell = 1 + (lam * lam - 1) * x2
        w2 = lam * lam * (1 - x2) + x2
        c = lam / (ell * w2).sqrt(analytic=analytic)
        f, _ = angle_data(c)
        return f

    return integral_1d(kernel, tol, depth, limit)


def center_derivative(lam_value: arb, tol: arb, depth: int, limit: int) -> acb:
    lam = acb(lam_value)

    def kernel(x: acb, analytic: bool) -> acb:
        x2 = x * x
        ell = 1 + (lam * lam - 1) * x2
        w2 = lam * lam * (1 - x2) + x2
        c = lam / (ell * w2).sqrt(analytic=analytic)
        _, f1 = angle_data(c)
        c_lam = c * (
            1 / lam - lam * x2 / ell - lam * (1 - x2) / w2
        )
        return f1 * c_lam

    return integral_1d(kernel, tol, depth, limit)


def boundary_geometry(t: acb, phi: acb, lam: acb, analytic: bool) -> dict:
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
    return {"t2": t2, "s2": s2, "R2": R2, "eta2": eta2, "c": t / (eta * R)}


def boundary_energy(lam_value: arb, tol: arb, depth: int, limit: int) -> acb:
    lam = acb(lam_value)
    pi = acb(arb.pi())

    def kernel(t: acb, phi: acb, analytic: bool) -> acb:
        g = boundary_geometry(t, phi, lam, analytic)
        f, _ = angle_data(g["c"])
        return 8 * t**3 * f / pi

    return integral_2d(kernel, tol, depth, limit)


def boundary_derivative(lam_value: arb, tol: arb, depth: int, limit: int) -> acb:
    lam = acb(lam_value)
    pi = acb(arb.pi())

    def kernel(t: acb, phi: acb, analytic: bool) -> acb:
        g = boundary_geometry(t, phi, lam, analytic)
        _, f1 = angle_data(g["c"])
        R2_lam = 2 * lam * (1 - g["t2"]) * g["s2"]
        eta2_lam = -8 * g["t2"] * (1 - g["t2"]) * g["s2"] / lam**3
        c_lam = -g["c"] * (
            R2_lam / g["R2"] + eta2_lam / g["eta2"]
        ) / 2
        return 8 * t**3 * f1 * c_lam / pi

    return integral_2d(kernel, tol, depth, limit)


def run(dps: int, tolerance: str, depth: int, limit: int) -> dict:
    ctx.dps = dps
    tol = arb(tolerance)

    lo = arb(fmpq(1717, 500))
    hi = arb(fmpq(1718, 500))
    mid = arb(fmpq(687, 200))
    box = closed_interval(1717, 500, 1718, 500)

    E0_lo = center_energy(lo, tol, depth, limit)
    E1_lo = boundary_energy(lo, tol, depth, limit)
    E0_hi = center_energy(hi, tol, depth, limit)
    E1_hi = boundary_energy(hi, tol, depth, limit)
    E0_mid = center_energy(mid, tol, depth, limit)
    E1_mid = boundary_energy(mid, tol, depth, limit)
    E0p_box = center_derivative(box, tol, depth, limit)
    E1p_box = boundary_derivative(box, tol, depth, limit)

    D_lo = E1_lo - E0_lo
    D_hi = E1_hi - E0_hi
    D_mid = E1_mid - E0_mid
    Dp_box = E1p_box - E0p_box

    stage_5a_conditions = {
        "D(3.434) > 0": bool(D_lo.real > 0 and 0 in D_lo.imag),
        "D(3.436) < 0": bool(D_hi.real < 0 and 0 in D_hi.imag),
        "D'([3.434,3.436]) < 0": bool(Dp_box.real < 0 and 0 in Dp_box.imag),
    }
    stage_5a_certified = all(stage_5a_conditions.values())

    derivative_excludes_zero = bool(0 not in Dp_box.real)
    newton = mid - D_mid.real / Dp_box.real if derivative_excludes_zero else box
    newton_inside = bool(
        derivative_excludes_zero
        and newton.lower() > box.lower()
        and newton.upper() < box.upper()
    )
    stage_5b_conditions = {
        "D(3.435) real": bool(0 in D_mid.imag),
        "D'(I5) excludes zero": derivative_excludes_zero,
        "Newton image strictly inside I5": newton_inside,
    }
    stage_5b_certified = stage_5a_certified and all(stage_5b_conditions.values())

    return {
        "status": "CERTIFIED" if stage_5a_certified else "FAILED_OR_INCONCLUSIVE",
        "stage_5a_status": "CERTIFIED" if stage_5a_certified else "FAILED_OR_INCONCLUSIVE",
        "stage_5b_status": "CERTIFIED" if stage_5b_certified else "INCONCLUSIVE",
        "environment": {
            "python": platform.python_version(),
            "python_flint": flint.__version__,
            "flint": flint.__FLINT_VERSION__,
        },
        "arithmetic": "python-flint Arb/Acb ball arithmetic",
        "decimal_precision": dps,
        "integration_tolerance": tolerance,
        "stage_5a_bracket": "[3.434, 3.436]",
        "stage_5a_bracket_exact": "[1717/500, 1718/500]",
        "stage_5b_midpoint": "3.435 = 687/200",
        "stage_5a_conditions": stage_5a_conditions,
        "stage_5b_conditions": stage_5b_conditions,
        "values": {
            "lambda_interval": arb_record(box),
            "D_at_lower": acb_record(D_lo),
            "D_at_upper": acb_record(D_hi),
            "D_at_midpoint": acb_record(D_mid),
            "D_prime_on_interval": acb_record(Dp_box),
            "interval_newton_image": arb_record(newton),
            "E_center_at_midpoint": acb_record(E0_mid),
            "E_boundary_at_midpoint": acb_record(E1_mid),
            "E_center_prime_on_interval": acb_record(E0p_box),
            "E_boundary_prime_on_interval": acb_record(E1p_box),
        },
        "certified_conclusion": (
            "If stage_5a_status is CERTIFIED, D has exactly one simple zero "
            "lambda_cross in [3.434,3.436], D'(lambda_cross)<0, and the boundary "
            "and center values cross transversely. If stage_5b_status is also "
            "CERTIFIED, the interval-Newton image is a smaller enclosure."
        ),
        "noncertified_reference": {
            "lambda_cross": "3.43486844286684...",
            "common_energy": "0.64287764254486...",
            "D_prime_at_root": "-0.07195990796855...",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dps", type=int, default=30)
    parser.add_argument("--tolerance", default="1e-6")
    parser.add_argument("--depth-limit", type=int, default=12)
    parser.add_argument("--eval-limit", type=int, default=200000)
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
    raise SystemExit(0 if result["stage_5a_status"] == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
