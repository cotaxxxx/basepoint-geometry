#!/usr/bin/env python3
"""Parallel component runner for the prolate item 5 Arb certificate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from flint import acb, arb, ctx, fmpq

import prolate_maxwell_arb_certificate as cert


def phi_partitioned_integral_2d(
    kernel: Callable[[acb, acb, bool], acb],
    tol: arb,
    depth: int,
    limit: int,
) -> acb:
    """Validated 2D integral with four exact phi bands.

    Each band is enclosed independently and the resulting Acb balls are added.
    This keeps the complex trigonometric images narrower than one integration
    over the full phi interval.
    """
    nphi = 4
    local_tol = tol / 8
    total = acb(0)
    pi = arb.pi()

    for j in range(nphi):
        phi_lo = acb(pi * j / (2 * nphi))
        phi_hi = acb(pi * (j + 1) / (2 * nphi))

        def outer(phi: acb, analytic_phi: bool) -> acb:
            def inner(t: acb, analytic_t: bool) -> acb:
                return kernel(t, phi, analytic_phi and analytic_t)

            return acb.integral(
                inner,
                0,
                1,
                abs_tol=local_tol,
                rel_tol=local_tol,
                depth_limit=depth,
                eval_limit=limit,
            )

        total += acb.integral(
            outer,
            phi_lo,
            phi_hi,
            abs_tol=local_tol,
            rel_tol=local_tol,
            depth_limit=depth,
            eval_limit=limit,
        )

    return total


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["lower", "upper", "midpoint", "derivative"])
    p.add_argument("--dps", type=int, default=30)
    p.add_argument("--tolerance", default="1e-6")
    p.add_argument("--depth-limit", type=int, default=12)
    p.add_argument("--eval-limit", type=int, default=200000)
    args = p.parse_args()

    ctx.dps = args.dps
    tol = arb(args.tolerance)
    cert.integral_2d = phi_partitioned_integral_2d

    if args.mode == "lower":
        lam = arb(fmpq(1717, 500))
        E0 = cert.center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = cert.boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "stage": "5a",
            "lambda": "3.434",
            "lambda_exact": "1717/500",
            "E_center": cert.acb_record(E0),
            "E_boundary": cert.acb_record(E1),
            "D": cert.acb_record(E1 - E0),
        }
    elif args.mode == "upper":
        lam = arb(fmpq(1718, 500))
        E0 = cert.center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = cert.boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "stage": "5a",
            "lambda": "3.436",
            "lambda_exact": "1718/500",
            "E_center": cert.acb_record(E0),
            "E_boundary": cert.acb_record(E1),
            "D": cert.acb_record(E1 - E0),
        }
    elif args.mode == "midpoint":
        lam = arb(fmpq(687, 200))
        E0 = cert.center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = cert.boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "stage": "5b",
            "lambda": "3.435",
            "lambda_exact": "687/200",
            "E_center": cert.acb_record(E0),
            "E_boundary": cert.acb_record(E1),
            "D": cert.acb_record(E1 - E0),
        }
    else:
        box = cert.closed_interval(1717, 500, 1718, 500)
        E0p = cert.center_derivative(box, tol, args.depth_limit, args.eval_limit)
        E1p = cert.boundary_derivative(box, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "stage": "5a_and_5b",
            "lambda_interval": cert.arb_record(box),
            "lambda_interval_exact": "[1717/500,1718/500]",
            "E_center_prime": cert.acb_record(E0p),
            "E_boundary_prime": cert.acb_record(E1p),
            "D_prime": cert.acb_record(E1p - E0p),
        }

    result.update({
        "decimal_precision": args.dps,
        "integration_tolerance": args.tolerance,
        "phi_subdivisions": 4,
    })
    out = Path(f"component_{args.mode}.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
