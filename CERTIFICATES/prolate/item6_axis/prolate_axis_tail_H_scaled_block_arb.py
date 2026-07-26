#!/usr/bin/env python3
"""Correlation-preserving three-chart driver for compact tail H blocks.

This wrapper reuses the exact block-cover logic from
``prolate_axis_tail_H_block_arb.py``.  The moving layer is split as

    [-1, w-4mu], [w-4mu, w+4mu], [w+4mu, 1].

Unlike the former implementation, each chart substitutes ``c-w`` and the
endpoint factors before Arb evaluation.  In particular, on the inner chart

    c = w + mu*q,  q = 8*t-4,
    c-w = mu*q,
    P = mu^2 * (q^2 + 1-c^2),

are evaluated in these exact factored forms.  This prevents interval loss from
forming ``c`` and then subtracting the same interval ``w`` again.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from flint import acb, arb, ctx, fmpq

import prolate_axis_tail_H_block_arb as base


LAYER_RADIUS = 4


def scaled_tail_H_three_chart(
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

    left_jacobian = 1 + w - radius * mu
    right_jacobian = 1 - w - radius * mu

    def left_kernel(t: acb, analytic: bool) -> acb:
        # c=-1+Jt.  Keep c-w=-(1+w)(1-t)-4mu*t exact.
        c = -1 + left_jacobian * t
        difference = -(1 + w) * (1 - t) - radius * mu * t
        rho2 = left_jacobian * t * (2 - left_jacobian * t)
        n = 1 + w - w * left_jacobian * t
        return left_jacobian * outer_integrand(
            c, difference, rho2, n, analytic
        )

    def inner_kernel(t: acb, analytic: bool) -> acb:
        # c=w+mu*q, q in [-4,4].  Cancel the common mu factor in P and sqrt(P).
        q = 2 * radius * t - radius
        c = w + mu * q
        difference = mu * q
        rho2 = 1 - c * c
        reduced_p = q * q + rho2
        s = rho2 + mu2 * c * c
        reduced_root = (reduced_p * s).sqrt(analytic=analytic)
        n = 1 - w * w - mu * w * q
        cosine = n / reduced_root
        _, h1 = base.regular_angle_data(cosine)
        hbar = base.regular_hbar(cosine)
        bracket = -c + n * q / (mu * reduced_p)
        # dc=2*radius*mu*dt and sqrt(P*S)=mu*sqrt(reduced_p*S).
        return radius * n * (-c * hbar + h1 * bracket) / (
            w * reduced_root
        )

    def right_kernel(t: acb, analytic: bool) -> acb:
        # c=w+4mu+Jt.  Both c-w and 1-c retain exact positive factors.
        c = w + radius * mu + right_jacobian * t
        difference = radius * mu + right_jacobian * t
        rho2 = right_jacobian * (1 - t) * (1 + c)
        n = 1 - w * w - radius * mu * w - w * right_jacobian * t
        return right_jacobian * outer_integrand(
            c, difference, rho2, n, analytic
        )

    left = base.rigorous_integral(
        left_kernel, tolerance, integration_depth, eval_limit
    )
    inner = base.rigorous_integral(
        inner_kernel, tolerance, integration_depth, eval_limit
    )
    right = base.rigorous_integral(
        right_kernel, tolerance, integration_depth, eval_limit
    )
    return left + inner + right


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
    if not (-1 < w_lo - LAYER_RADIUS * mu_hi):
        raise ValueError("left outer chart leaves [-1,1]")
    if not (w_hi + LAYER_RADIUS * mu_hi < 1):
        raise ValueError("right outer chart leaves [-1,1]")

    ctx.dps = args.dps
    base.scaled_tail_H = scaled_tail_H_three_chart
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
        "type": "correlation-preserving mu-scaled three-chart split",
        "layer_radius": LAYER_RADIUS,
        "pieces": ["[-1,w-4mu]", "[w-4mu,w+4mu]", "[w+4mu,1]"],
        "exact_inner_identities": [
            "c=w+mu*(8t-4)",
            "c-w=mu*(8t-4)",
            "P=mu^2*((8t-4)^2+1-c^2)",
        ],
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
