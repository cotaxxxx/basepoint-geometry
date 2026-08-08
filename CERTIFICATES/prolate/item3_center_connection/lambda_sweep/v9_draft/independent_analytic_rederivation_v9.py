#!/usr/bin/env python3
"""Independent symbolic rederivation for Item 3 sweep v9.

This file does not import the prototype kernel, adapter, runner, checker, or their
handwritten derivative expressions. It starts from the base scalar formula for gamma and
from an abstract one-variable angle function H(gamma), then independently differentiates
those objects with SymPy.

STATUS: INDEPENDENT FORMAL REDERIVATION / NOT MACHINE AUTHORIZATION.

A PASS supports review of the analytic formulas. It does not by itself prove interval
library semantics, source binding, domain enforcement, or a certified lambda range.
"""
from __future__ import annotations

import json

import sympy as sp


def geometry_checks() -> dict[str, bool]:
    r, lam = sp.symbols("r lam", positive=True, real=True)
    s, c, u = sp.symbols("s c u", real=True)

    ell = s**2 + lam**2 * c**2
    w2 = lam**2 * s**2 + c**2
    q = ell - 2 * r * u + r**2
    W = 1 - r * u
    B = lam / sp.sqrt(w2)
    gamma = B * W / sp.sqrt(q)

    d = r - u
    N = u * (1 - ell) + r * (u**2 - 1)
    N_r = u**2 - 1
    M = N_r * q - 3 * N * d
    M_r = -N_r * d - 3 * N

    B_log_lambda = c**2 / (lam * w2)
    q_lambda = 2 * lam * c**2
    N_lambda = -2 * lam * u * c**2
    M_lambda = N_r * q_lambda - 3 * N_lambda * d

    candidates = {
        "gamma_r": B * N / q ** sp.Rational(3, 2),
        "gamma_rr": B * M / q ** sp.Rational(5, 2),
        "gamma_rrr": B * (M_r * q - 5 * M * d) / q ** sp.Rational(7, 2),
        "gamma_lambda": gamma * (B_log_lambda - lam * c**2 / q),
        "gamma_rlambda": B
        * (N_lambda + N * B_log_lambda - 3 * lam * c**2 * N / q)
        / q ** sp.Rational(3, 2),
        "gamma_rrlambda": B
        * (M_lambda + M * B_log_lambda - 5 * lam * c**2 * M / q)
        / q ** sp.Rational(5, 2),
    }

    exact = {
        "gamma_r": sp.diff(gamma, r),
        "gamma_rr": sp.diff(gamma, r, 2),
        "gamma_rrr": sp.diff(gamma, r, 3),
        "gamma_lambda": sp.diff(gamma, lam),
        "gamma_rlambda": sp.diff(gamma, r, lam),
        "gamma_rrlambda": sp.diff(gamma, r, 2, lam),
    }

    checks = {
        key: sp.simplify(exact[key] - candidates[key]) == 0
        for key in candidates
    }

    # Independent algebraic proof of gamma^2 <= 1.  Impose s^2+c^2=1 only
    # after expanding both sides.
    a = lam**2 - 1
    lhs = sp.expand(w2 * q - lam**2 * W**2)
    rhs = c**2 * (r + a * u) ** 2 + (s**2 - u**2) * (
        c**2 * a**2 + lam**2 * r**2
    )
    reduced = sp.expand(lhs - rhs).subs(c**2, 1 - s**2)
    checks["gamma_range_factorization"] = sp.factor(reduced) == 0

    # Numerator identity used in the first r derivative.
    checks["gamma_r_numerator"] = sp.simplify(
        (-u * q - W * d) - N
    ) == 0

    # Logarithmic derivative of B=lambda/sqrt(w2).
    checks["B_log_lambda"] = sp.simplify(
        sp.diff(B, lam) / B - B_log_lambda
    ) == 0

    return checks


def integrand_checks() -> dict[str, bool]:
    r, lam = sp.symbols("r lam", real=True)
    s, u = sp.symbols("s u", real=True)

    gfun = sp.Function("g")
    H = sp.Function("H")
    g = gfun(r, lam)
    W = 1 - r * u

    g_r = sp.diff(g, r)
    g_rr = sp.diff(g, r, 2)
    g_rrr = sp.diff(g, r, 3)
    g_l = sp.diff(g, lam)
    g_rl = sp.diff(g, r, lam)
    g_rrl = sp.diff(g, r, 2, lam)

    h = H(g)
    h1 = sp.diff(H(g), g)
    h2 = sp.diff(H(g), g, 2)
    h3 = sp.diff(H(g), g, 3)

    phi = s * (-u * h + W * h1 * g_r)

    candidate_r = s * (
        -2 * u * h1 * g_r
        + W * (h2 * g_r**2 + h1 * g_rr)
    )

    A = h2 * g_r**2 + h1 * g_rr
    candidate_rr = s * (
        -3 * u * A
        + W * (h3 * g_r**3 + 3 * h2 * g_r * g_rr + h1 * g_rrr)
    )

    candidate_lambda = s * (
        -u * h1 * g_l
        + W * (h2 * g_l * g_r + h1 * g_rl)
    )

    candidate_rlambda = s * (
        -2 * u * (h2 * g_l * g_r + h1 * g_rl)
        + W * (
            h3 * g_l * g_r**2
            + 2 * h2 * g_r * g_rl
            + h2 * g_l * g_rr
            + h1 * g_rrl
        )
    )

    return {
        "Phi_F_r": sp.simplify(sp.diff(phi, r) - candidate_r) == 0,
        "Phi_F_rr": sp.simplify(sp.diff(phi, r, 2) - candidate_rr) == 0,
        "Phi_F_lambda": sp.simplify(sp.diff(phi, lam) - candidate_lambda) == 0,
        "Phi_F_rlambda": sp.simplify(
            sp.diff(phi, r, lam) - candidate_rlambda
        ) == 0,
    }


def angle_endpoint_checks() -> dict[str, bool]:
    z = sp.symbols("z", positive=True)
    series = sp.series(sp.acos(1 - z) ** 2, z, 0, 5).removeO()

    # d/dx = -d/dz for x=1-z.
    h1 = -sp.diff(series, z).subs(z, 0)
    h2 = sp.diff(series, z, 2).subs(z, 0)
    h3 = -sp.diff(series, z, 3).subs(z, 0)

    return {
        "h1_at_1": sp.simplify(h1 + 2) == 0,
        "h2_at_1": sp.simplify(h2 - sp.Rational(2, 3)) == 0,
        "h3_at_1": sp.simplify(h3 + sp.Rational(8, 15)) == 0,
    }


def quotient_checks() -> dict[str, bool]:
    r, lam = sp.symbols("r lam", positive=True, real=True)
    Ffun = sp.Function("F")
    F = Ffun(r, lam)
    G = F / r

    return {
        "G_r": sp.simplify(
            sp.diff(G, r) - (sp.diff(F, r) / r - F / r**2)
        ) == 0,
        "G_rr": sp.simplify(
            sp.diff(G, r, 2)
            - (sp.diff(F, r, 2) / r - 2 * sp.diff(F, r) / r**2 + 2 * F / r**3)
        ) == 0,
        "G_rlambda": sp.simplify(
            sp.diff(G, r, lam)
            - (sp.diff(F, r, lam) / r - sp.diff(F, lam) / r**2)
        ) == 0,
    }


def main() -> int:
    groups = {
        "geometry": geometry_checks(),
        "integrands": integrand_checks(),
        "angle_endpoint": angle_endpoint_checks(),
        "quotients": quotient_checks(),
    }
    flat = [value for group in groups.values() for value in group.values()]
    report = {
        "schema": "ITEM3_SWEEP_V9_INDEPENDENT_ANALYTIC_REDERIVATION_V1",
        "status": "PASSED" if all(flat) else "FAILED",
        "proof_role": "FORMAL_REDERIVATION_SUPPORT_ONLY",
        "imports_prototype_kernel": False,
        "imports_adapter_runner_checker": False,
        "groups": groups,
        "nonclaims": [
            "does not validate acb.integral semantics",
            "does not validate production source binding",
            "does not authorize a workflow or certificate",
        ],
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if report["status"] == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
