#!/usr/bin/env python3
"""Parallel component runner for the prolate item 5 Arb certificate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from flint import arb, ctx, fmpq

from prolate_maxwell_arb_certificate import (
    acb_record,
    arb_record,
    boundary_derivative,
    boundary_energy,
    center_derivative,
    center_energy,
    closed_interval,
)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["lower", "upper", "midpoint", "derivative"])
    p.add_argument("--dps", type=int, default=40)
    p.add_argument("--tolerance", default="1e-10")
    p.add_argument("--depth-limit", type=int, default=20)
    p.add_argument("--eval-limit", type=int, default=200000)
    args = p.parse_args()

    ctx.dps = args.dps
    tol = arb(args.tolerance)

    if args.mode == "lower":
        lam = arb(fmpq(171743, 50000))
        E0 = center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "lambda": "3.43486",
            "E_center": acb_record(E0),
            "E_boundary": acb_record(E1),
            "D": acb_record(E1 - E0),
        }
    elif args.mode == "upper":
        lam = arb(fmpq(85872, 25000))
        E0 = center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "lambda": "3.43488",
            "E_center": acb_record(E0),
            "E_boundary": acb_record(E1),
            "D": acb_record(E1 - E0),
        }
    elif args.mode == "midpoint":
        lam = arb(fmpq(343487, 100000))
        E0 = center_energy(lam, tol, args.depth_limit, args.eval_limit)
        E1 = boundary_energy(lam, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "lambda": "3.43487",
            "E_center": acb_record(E0),
            "E_boundary": acb_record(E1),
            "D": acb_record(E1 - E0),
        }
    else:
        box = closed_interval(171743, 50000, 85872, 25000)
        E0p = center_derivative(box, tol, args.depth_limit, args.eval_limit)
        E1p = boundary_derivative(box, tol, args.depth_limit, args.eval_limit)
        result = {
            "mode": args.mode,
            "lambda_interval": arb_record(box),
            "E_center_prime": acb_record(E0p),
            "E_boundary_prime": acb_record(E1p),
            "D_prime": acb_record(E1p - E0p),
        }

    result.update({
        "decimal_precision": args.dps,
        "integration_tolerance": args.tolerance,
    })
    out = Path(f"component_{args.mode}.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
