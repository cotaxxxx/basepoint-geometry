#!/usr/bin/env python3
"""Paired, correlation-preserving compact-tail driver for H.

For ``mu=1/lambda`` the moving layer is resolved by three exact pieces:

* an inner blow-up ``c=w+mu*q``, ``q in [-4,4]``;
* a paired outer piece at the common distance ``x=|c-w|``;
* the unmatched far-left piece.

Pairing the two outer sides inside one integration kernel exposes the dominant
left/right cancellation before parameter subdivision.  Every occurrence of
``c-w`` and every vanishing endpoint factor is substituted in factored form.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from flint import acb, arb, ctx, fmpq

import prolate_axis_tail_H_block_arb as base


LAYER_RADIUS = 4


def paired_tail_H(
    mu_value: arb,
    w_value: arb,
    tolerance: arb,
    integration_depth: int,
    eval_limit: int,
) -> acb:
    mu = acb(mu_value)
    w = acb(w_value)
    mu2 = mu * mu
    radius = acb(LAYER_RADIUS)

    def outer_integrand(
        c: acb,
        difference: acb,
        rho2: acb,
        n: acb,
        analytic: bool,
    ) -> acb:
        p = difference * difference + mu2 * rho2
        s = rho2 + mu2 * c * c
        root = (p * s).sqrt(analytic=analytic)
        cosine = mu * n / root
        _, h1 = base.regular_angle_data(cosine)
        hbar = base.regular_hbar(cosine)
        bracket = -c + n * difference / p
        return n * (-c * hbar + h1 * bracket) / (2 * w * root)

    def inner_kernel(t: acb, analytic: bool) -> acb:
        q = 2 * radius * t - radius
        c = w + mu * q
        rho2 = (1 - c) * (1 + c)
        reduced_p = q * q + rho2
        s = rho2 + mu2 * c * c
        reduced_root = (reduced_p * s).sqrt(analytic=analytic)
        n = 1 - w * w - mu * w * q
        cosine = n / reduced_root
        _, h1 = base.regular_angle_data(cosine)
        hbar = base.regular_hbar(cosine)
        bracket = -c + n * q / (mu * reduced_p)
        # dc=8*mu*dt and sqrt(P*S)=mu*sqrt(reduced_p*S).
        return radius * n * (-c * hbar + h1 * bracket) / (
            w * reduced_root
        )

    pair_jacobian = 1 - w - radius * mu

    def paired_outer_kernel(t: acb, analytic: bool) -> acb:
        x = radius * mu + pair_jacobian * t

        c_left = w - x
        rho2_left = (1 - w + x) * (1 + w - x)
        n_left = 1 - w * w + w * x
        left = outer_integrand(
            c_left, -x, rho2_left, n_left, analytic
        )

        c_right = w + x
        # 1-c_right vanishes exactly at t=1.
        rho2_right = pair_jacobian * (1 - t) * (1 + w + x)
        n_right = 1 - w * w - w * x
        right = outer_integrand(
            c_right, x, rho2_right, n_right, analytic
        )

        return pair_jacobian * (left + right)

    def far_left_kernel(t: acb, analytic: bool) -> acb:
        # x runs from 1-w to 1+w; c=w-x runs from 2w-1 to -1.
        x = 1 - w + 2 * w * t
        c = w - x
        rho2 = 4 * w * (1 - t) * (1 - w + w * t)
        n = 1 + w - 2 * w * w + 2 * w * w * t
        return 2 * w * outer_integrand(c, -x, rho2, n, analytic)

    inner = base.rigorous_integral(
        inner_kernel, tolerance, integration_depth, eval_limit
    )
    paired = base.rigorous_integral(
        paired_outer_kernel, tolerance, integration_depth, eval_limit
    )
    far_left = base.rigorous_integral(
        far_left_kernel, tolerance, integration_depth, eval_limit
    )
    return inner + paired + far_left


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dps", type=int, default=50)
    parser.add_argument("--tolerance", default="1e-18")
    parser.add_argument("--integration-depth", type=int, default=22)
    parser.add_argument("--eval-limit", type=int, default=200000)
    parser.add_argument("--max-split-depth", type=int, default=16)
    parser.add_argument("--max-boxes", type=int, default=32768)
    parser.add_argument("--mu-lo-num", type=int, required=True)
    parser.add_argument("--mu-lo-den", type=int, required=True)
    parser.add_argument("--mu-hi-num", type=int, required=True)
    parser.add_argument("--mu-hi-den", type=int, required=True)
    parser.add_argument("--w-lo-num", type=int, required=True)
    parser.add_argument("--w-lo-den", type=int, required=True)
    parser.add_argument("--w-hi-num", type=int, required=True)
    parser.add_argument("--w-hi-den", type=int, required=True)
    parser.add_argument("--json", required=True)
    args = parser.parse_args()

    mu_lo = fmpq(args.mu_lo_num, args.mu_lo_den)
    mu_hi = fmpq(args.mu_hi_num, args.mu_hi_den)
    w_lo = fmpq(args.w_lo_num, args.w_lo_den)
    w_hi = fmpq(args.w_hi_num, args.w_hi_den)
    if not (fmpq(0) < mu_lo < mu_hi):
        raise ValueError("require 0 < mu-lo < mu-hi")
    if not (fmpq(0) < w_lo < w_hi < fmpq(1)):
        raise ValueError("require 0 < w-lo < w-hi < 1")
    if not (w_hi + LAYER_RADIUS * mu_hi < 1):
        raise ValueError("paired outer chart has nonpositive length")

    ctx.dps = args.dps
    base.scaled_tail_H = paired_tail_H
    result = base.certify_block(
        args.dps,
        args.tolerance,
        args.integration_depth,
        args.eval_limit,
        args.max_split_depth,
        args.max_boxes,
        mu_lo,
        mu_hi,
        w_lo,
        w_hi,
    )
    result["integration_chart"] = {
        "type": "paired correlation-preserving moving-layer split",
        "layer_radius": LAYER_RADIUS,
        "pieces": [
            "inner: c=w+mu*(8t-4)",
            "paired: c=w+-x, x=4mu+(1-w-4mu)t",
            "far-left: x=1-w+2wt, c=w-x",
        ],
        "exact_partition": (
            "inner plus paired outer plus unmatched far-left equals [-1,1]"
        ),
    }
    result["script_sha256"] = base.sha256_file(Path(__file__))
    result["base_driver_sha256"] = base.sha256_file(
        Path(__file__).with_name("prolate_axis_tail_H_block_arb.py")
    )
    result["regularization_audit_sha256"] = base.sha256_file(
        Path(__file__).with_name("prolate_axis_tail_regularized_symbolic_audit.py")
    )

    output = Path(args.json)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{result['script_sha256']}  {Path(__file__).name}\n"
        f"{result['base_driver_sha256']}  prolate_axis_tail_H_block_arb.py\n"
        f"{result['regularization_audit_sha256']}  prolate_axis_tail_regularized_symbolic_audit.py\n"
        f"{base.sha256_file(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
