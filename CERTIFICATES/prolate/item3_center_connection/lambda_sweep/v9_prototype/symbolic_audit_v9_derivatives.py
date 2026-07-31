#!/usr/bin/env python3
'''Diagnostic symbolic audit for the v9 geometry derivatives.

STATUS: DIAGNOSTIC_ONLY. This script is not proof machinery and is not imported by
runner, checker, adapter, or kernel source.
'''
from __future__ import annotations

import json

import sympy as sp


def main() -> int:
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

    z = sp.symbols("z", positive=True)
    h_series = sp.series(sp.acos(1 - z) ** 2, z, 0, 4).removeO()
    h3_limit = -sp.diff(h_series, z, 3).subs(z, 0)
    checks["h3_at_one"] = sp.simplify(h3_limit + sp.Rational(8, 15)) == 0

    report = {
        "schema": "ITEM3_SWEEP_V9_SYMBOLIC_DIAGNOSTIC_V1",
        "proof_status": "DIAGNOSTIC_ONLY",
        "checks": checks,
        "verdict": "PASS" if all(checks.values()) else "FAIL",
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
