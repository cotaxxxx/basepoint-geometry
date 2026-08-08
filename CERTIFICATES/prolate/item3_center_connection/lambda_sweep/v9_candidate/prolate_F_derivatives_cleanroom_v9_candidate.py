#!/usr/bin/env python3
"""Guarded five-output clean-room candidate for Item 3 sweep v9.

STATUS
------
AUDIT CANDIDATE / NOT APPROVED FOR PRODUCTION.

This source is derived from ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md.  It publishes only the
five rigorous F-level interfaces required by v9 and deliberately omits diagnostic float
interfaces.

The source incorporates the python-flint acb.integral callback obligations recorded in
ACB_INTEGRAL_ANALYTIC_FLAG_AUDIT.md:

* nested analytic requests propagate by logical OR;
* branch-sensitive square roots receive the analytic requirement;
* the Gauss 2F1 principal cut is rejected explicitly during analytic callback requests;
* the public rigorous interfaces reject parameter boxes outside 0 < r < 1, lambda >= 1.

Nothing in this file authorizes a workflow, config, tag, source approval, or certificate.
"""
from __future__ import annotations

from typing import Callable

from flint import acb, arb


CANDIDATE_STATE = "AUDIT_CANDIDATE_NOT_APPROVED"
KERNEL_ID = "ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2"


def _nonfinite_angle_tuple() -> tuple[acb, acb, acb, acb]:
    nan = acb(arb.nan(), arb.nan())
    return nan, nan, nan, nan


def angle_data_3(cosine: acb, *, analytic: bool) -> tuple[acb, acb, acb, acb]:
    """Return h=acos(c)^2 and its first three derivatives.

    The physical real domain has 0 < c <= 1.  For validated complex integration the
    callback may be asked to certify analyticity on a complex ball.  With

        z = (1-c)/2,

    the principal Gauss 2F1 representation has its real branch cut from z=1 to +infinity.
    python-flint hypgeom_2f1 has no analytic= flag, so we reject any analytic-request ball
    that can intersect that cut before calling it.
    """
    if analytic and not cosine.is_finite():
        return _nonfinite_angle_tuple()

    one = acb(1)
    z = (one - cosine) / 2

    if analytic and 0 in z.imag and z.real.upper() >= 1:
        return _nonfinite_angle_tuple()

    hyper = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    h = 4 * z * hyper * hyper
    x = -h / 4

    # 0F1 is entire in x for these fixed non-pole parameters.  Division by a ball
    # containing a zero of S fails closed through a non-finite enclosure.
    S = x.hypgeom_0f1(acb(3) / 2)
    T = x.hypgeom_0f1(acb(5) / 2)
    U = x.hypgeom_0f1(acb(7) / 2)

    h1 = -2 / S
    h2 = (acb(2) / 3) * T / S**3
    h3 = (acb(2) / 15) * U / S**4 - (acb(2) / 3) * T**2 / S**5
    return h, h1, h2, h3


def _geometry(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    *,
    analytic: bool,
) -> dict[str, acb]:
    """Fixed-domain geometry and exact gamma derivatives."""
    s = theta.sin()
    c = theta.cos()
    c2 = c * c
    u = s * phi.cos()

    ell = s * s + lam * lam * c2
    w2 = lam * lam * s * s + c2
    w = w2.sqrt(analytic=analytic)

    q = ell - 2 * r * u + r * r
    sqrt_q = q.sqrt(analytic=analytic)
    W = 1 - r * u
    B = lam / w
    gamma = B * W / sqrt_q

    d = r - u
    N = u * (1 - ell) + r * (u * u - 1)
    N_r = u * u - 1
    M = N_r * q - 3 * N * d
    M_r = -N_r * d - 3 * N

    gamma_r = B * N / (q * sqrt_q)
    gamma_rr = B * M / (q * q * sqrt_q)
    gamma_rrr = B * (M_r * q - 5 * M * d) / (q * q * q * sqrt_q)

    B_log_lambda = c2 / (lam * w2)
    q_lambda = 2 * lam * c2
    N_lambda = -2 * lam * u * c2
    M_lambda = N_r * q_lambda - 3 * N_lambda * d

    gamma_lambda = gamma * (B_log_lambda - lam * c2 / q)
    gamma_rlambda = B * (
        N_lambda
        + N * B_log_lambda
        - 3 * lam * c2 * N / q
    ) / (q * sqrt_q)
    gamma_rrlambda = B * (
        M_lambda
        + M * B_log_lambda
        - 5 * lam * c2 * M / q
    ) / (q * q * sqrt_q)

    return {
        "s": s,
        "u": u,
        "W": W,
        "gamma": gamma,
        "gamma_r": gamma_r,
        "gamma_rr": gamma_rr,
        "gamma_rrr": gamma_rrr,
        "gamma_lambda": gamma_lambda,
        "gamma_rlambda": gamma_rlambda,
        "gamma_rrlambda": gamma_rrlambda,
    }


def _F_kernel(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
    g = _geometry(theta, phi, r, lam, analytic=analytic)
    h, h1, _, _ = angle_data_3(g["gamma"], analytic=analytic)
    return g["s"] * (-g["u"] * h + g["W"] * h1 * g["gamma_r"])


def _F_r_kernel(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
    g = _geometry(theta, phi, r, lam, analytic=analytic)
    _, h1, h2, _ = angle_data_3(g["gamma"], analytic=analytic)
    return g["s"] * (
        -2 * g["u"] * h1 * g["gamma_r"]
        + g["W"] * (
            h2 * g["gamma_r"] ** 2
            + h1 * g["gamma_rr"]
        )
    )


def _F_lambda_kernel(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    analytic: bool,
) -> acb:
    g = _geometry(theta, phi, r, lam, analytic=analytic)
    _, h1, h2, _ = angle_data_3(g["gamma"], analytic=analytic)
    return g["s"] * (
        -g["u"] * h1 * g["gamma_lambda"]
        + g["W"] * (
            h2 * g["gamma_lambda"] * g["gamma_r"]
            + h1 * g["gamma_rlambda"]
        )
    )


def _F_rr_kernel(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
    g = _geometry(theta, phi, r, lam, analytic=analytic)
    _, h1, h2, h3 = angle_data_3(g["gamma"], analytic=analytic)
    A = h2 * g["gamma_r"] ** 2 + h1 * g["gamma_rr"]
    return g["s"] * (
        -3 * g["u"] * A
        + g["W"] * (
            h3 * g["gamma_r"] ** 3
            + 3 * h2 * g["gamma_r"] * g["gamma_rr"]
            + h1 * g["gamma_rrr"]
        )
    )


def _F_rlambda_kernel(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    analytic: bool,
) -> acb:
    g = _geometry(theta, phi, r, lam, analytic=analytic)
    _, h1, h2, h3 = angle_data_3(g["gamma"], analytic=analytic)
    return g["s"] * (
        -2 * g["u"] * (
            h2 * g["gamma_lambda"] * g["gamma_r"]
            + h1 * g["gamma_rlambda"]
        )
        + g["W"] * (
            h3 * g["gamma_lambda"] * g["gamma_r"] ** 2
            + 2 * h2 * g["gamma_r"] * g["gamma_rlambda"]
            + h2 * g["gamma_lambda"] * g["gamma_rr"]
            + h1 * g["gamma_rrlambda"]
        )
    )


Kernel = Callable[[acb, acb, acb, acb, bool], acb]


def _rigorous_integral_2d(
    kernel: Kernel,
    r: acb,
    lam: acb,
    tol: arb,
    depth: int,
    limit: int,
) -> acb:
    """Validated fixed-domain integral with nested analytic propagation."""
    upper_theta = arb.pi() / 2
    upper_phi = arb.pi()

    def outer(theta: acb, analytic_theta: bool) -> acb:
        def inner(phi: acb, analytic_phi: bool) -> acb:
            analytic_required = analytic_theta or analytic_phi
            return kernel(
                theta,
                phi,
                r,
                lam,
                analytic_required,
            )

        return acb.integral(
            inner,
            0,
            upper_phi,
            abs_tol=tol,
            rel_tol=tol,
            depth_limit=depth,
            eval_limit=limit,
        )

    total = acb.integral(
        outer,
        0,
        upper_theta,
        abs_tol=tol,
        rel_tol=tol,
        depth_limit=depth,
        eval_limit=limit,
    )
    return total / acb(arb.pi())


_DEF_TOL = "1e-8"
_DEF_DEPTH = 12
_DEF_LIMIT = 200000


def _validate_inputs(r: arb, lam: arb, tol: arb, depth: int, limit: int) -> None:
    if not r.is_finite() or not lam.is_finite() or not tol.is_finite():
        raise ValueError("kernel inputs must be finite")
    if r.lower() <= 0 or r.upper() >= 1:
        raise ValueError(f"require 0 < r < 1 on the complete input ball: {r}")
    if lam.lower() < 1:
        raise ValueError(f"require lambda >= 1 on the complete input ball: {lam}")
    if tol.lower() <= 0:
        raise ValueError(f"integration tolerance must be strictly positive: {tol}")
    if not isinstance(depth, int) or depth <= 0:
        raise ValueError("depth must be a positive int")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit must be a positive int")


def _as_real(value: acb, where: str) -> arb:
    if not value.is_finite():
        raise ValueError(f"{where}: non-finite validated integral: {value}")
    if not bool(0 in value.imag):
        raise ValueError(f"{where}: imaginary part excludes zero: {value.imag}")
    return value.real


def _evaluate(
    kernel: Kernel,
    r: arb,
    lam: arb,
    *,
    tol: str,
    depth: int,
    limit: int,
    where: str,
) -> arb:
    tol_ball = arb(tol)
    _validate_inputs(r, lam, tol_ball, depth, limit)
    value = _rigorous_integral_2d(
        kernel,
        acb(r),
        acb(lam),
        tol_ball,
        depth,
        limit,
    )
    return _as_real(value, where)


def F_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    return _evaluate(_F_kernel, r, lam, tol=tol, depth=depth, limit=limit, where="F_arb")


def F_r_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    return _evaluate(_F_r_kernel, r, lam, tol=tol, depth=depth, limit=limit, where="F_r_arb")


def F_lambda_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    return _evaluate(
        _F_lambda_kernel,
        r,
        lam,
        tol=tol,
        depth=depth,
        limit=limit,
        where="F_lambda_arb",
    )


def F_rr_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    return _evaluate(_F_rr_kernel, r, lam, tol=tol, depth=depth, limit=limit, where="F_rr_arb")


def F_rlambda_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    return _evaluate(
        _F_rlambda_kernel,
        r,
        lam,
        tol=tol,
        depth=depth,
        limit=limit,
        where="F_rlambda_arb",
    )
