#!/usr/bin/env python3
'''Prototype five-output clean-room derivative kernel for Item 3 sweep v9.

STATUS
------
PROTOTYPE / NOT AUDITED / NOT APPROVED FOR PRODUCTION.

This source is a new implementation derived from the fixed-domain formula documented
in Issue #23 and ANALYTIC_DERIVATION.md. It does not modify or replace the existing
pinned production kernel.

Published rigorous interfaces:
    F_arb
    F_r_arb
    F_lambda_arb
    F_rr_arb
    F_rlambda_arb

Published diagnostic interfaces:
    F_float
    F_r_float
    F_lambda_float
    F_rr_float
    F_rlambda_float

Finite differences are not used by any rigorous interface.
'''
from __future__ import annotations

import math
from typing import Callable

from flint import acb, arb


PROTOTYPE_STATE = "NOT_AUDITED"
KERNEL_ID = "ITEM3_SWEEP_V9_FIVE_OUTPUT_PROTOTYPE_V1"


def angle_data_3(c: acb) -> tuple[acb, acb, acb, acb]:
    '''Return h and its first three derivatives for h(c)=acos(c)^2.

    Hypergeometric representations remove the apparent singularity at c=1.

    Put z=(1-c)/2, h=4*z*2F1(1/2,1/2;3/2;z)^2 and x=-h/4. With

        S = 0F1(;3/2;x),
        T = 0F1(;5/2;x),
        U = 0F1(;7/2;x),

    one has

        h1 = -2/S,
        h2 = (2/3) T/S^3,
        h3 = (2/15) U/S^4 - (2/3) T^2/S^5.

    In particular the third derivative at c=1 is -8/15.
    '''
    one = acb(1)
    z = (one - c) / 2
    H = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    h = 4 * z * H * H
    x = -h / 4
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
    analytic: bool,
) -> dict[str, acb]:
    '''Fixed-domain geometry and exact derivatives of gamma.

    The returned derivatives are gamma_r, gamma_rr, gamma_rrr,
    gamma_lambda, gamma_rlambda, and gamma_rrlambda.
    '''
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

    # B_lambda / B = c^2 / (lambda*w^2).
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
    g = _geometry(theta, phi, r, lam, analytic)
    h, h1, _, _ = angle_data_3(g["gamma"])
    return g["s"] * (-g["u"] * h + g["W"] * h1 * g["gamma_r"])


def _F_r_kernel(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
    g = _geometry(theta, phi, r, lam, analytic)
    _, h1, h2, _ = angle_data_3(g["gamma"])
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
    g = _geometry(theta, phi, r, lam, analytic)
    _, h1, h2, _ = angle_data_3(g["gamma"])
    return g["s"] * (
        -g["u"] * h1 * g["gamma_lambda"]
        + g["W"] * (
            h2 * g["gamma_lambda"] * g["gamma_r"]
            + h1 * g["gamma_rlambda"]
        )
    )


def _F_rr_kernel(theta: acb, phi: acb, r: acb, lam: acb, analytic: bool) -> acb:
    g = _geometry(theta, phi, r, lam, analytic)
    _, h1, h2, h3 = angle_data_3(g["gamma"])
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
    g = _geometry(theta, phi, r, lam, analytic)
    _, h1, h2, h3 = angle_data_3(g["gamma"])
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
    '''Validated fixed-domain integral with the manuscript normalization.'''
    upper_theta = arb.pi() / 2
    upper_phi = arb.pi()

    def outer(theta: acb, analytic_theta: bool) -> acb:
        def inner(phi: acb, analytic_phi: bool) -> acb:
            return kernel(
                theta,
                phi,
                r,
                lam,
                analytic_theta and analytic_phi,
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


def _as_real(value: acb, where: str) -> arb:
    if not bool(0 in value.imag):
        raise ValueError(f"{where}: imaginary part excludes 0: {value.imag}")
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
    value = _rigorous_integral_2d(
        kernel,
        acb(r),
        acb(lam),
        arb(tol),
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


# Compatibility alias for diagnostic comparison with the existing source.
dFdr_arb = F_r_arb


_FLOAT_N_THETA = 64
_FLOAT_N_PHI = 128
_FLOAT_GEOMETRY: tuple[tuple[float, float, float], ...] = tuple(
    (
        math.sin((i + 0.5) * math.pi / (2 * _FLOAT_N_THETA)),
        math.cos((i + 0.5) * math.pi / (2 * _FLOAT_N_THETA)),
        math.cos((j + 0.5) * math.pi / _FLOAT_N_PHI),
    )
    for i in range(_FLOAT_N_THETA)
    for j in range(_FLOAT_N_PHI)
)
_FLOAT_WEIGHT = math.pi / (2 * _FLOAT_N_THETA * _FLOAT_N_PHI)


def _float_angle_data_3(c: float) -> tuple[float, float, float, float]:
    c = min(1.0, max(-1.0, c))
    beta = math.acos(c)
    h = beta * beta
    one_minus = max(0.0, 1.0 - c * c)
    if one_minus < 1e-18:
        return h, -2.0, 2.0 / 3.0, -8.0 / 15.0
    root = math.sqrt(one_minus)
    h1 = -2.0 * beta / root
    h2 = 2.0 / one_minus - 2.0 * c * beta / (one_minus * root)
    h3 = (
        6.0 * c / (one_minus * one_minus)
        - 2.0 * beta * (1.0 + 2.0 * c * c)
        / (one_minus * one_minus * root)
    )
    return h, h1, h2, h3


def _float_geometry(
    s: float,
    c: float,
    cos_phi: float,
    r: float,
    lam: float,
) -> dict[str, float]:
    c2 = c * c
    u = s * cos_phi
    ell = s * s + lam * lam * c2
    w2 = lam * lam * s * s + c2
    w = math.sqrt(w2)
    q = ell - 2.0 * r * u + r * r
    sqrt_q = math.sqrt(q)
    W = 1.0 - r * u
    B = lam / w
    gamma = B * W / sqrt_q

    d = r - u
    N = u * (1.0 - ell) + r * (u * u - 1.0)
    N_r = u * u - 1.0
    M = N_r * q - 3.0 * N * d
    M_r = -N_r * d - 3.0 * N

    gamma_r = B * N / (q * sqrt_q)
    gamma_rr = B * M / (q * q * sqrt_q)
    gamma_rrr = B * (M_r * q - 5.0 * M * d) / (q * q * q * sqrt_q)

    B_log_lambda = c2 / (lam * w2)
    q_lambda = 2.0 * lam * c2
    N_lambda = -2.0 * lam * u * c2
    M_lambda = N_r * q_lambda - 3.0 * N_lambda * d

    gamma_lambda = gamma * (B_log_lambda - lam * c2 / q)
    gamma_rlambda = B * (
        N_lambda + N * B_log_lambda - 3.0 * lam * c2 * N / q
    ) / (q * sqrt_q)
    gamma_rrlambda = B * (
        M_lambda + M * B_log_lambda - 5.0 * lam * c2 * M / q
    ) / (q * q * sqrt_q)

    return {
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


def _float_all(r: float, lam: float) -> tuple[float, float, float, float, float]:
    totals = [0.0] * 5
    for s, c, cos_phi in _FLOAT_GEOMETRY:
        g = _float_geometry(s, c, cos_phi, r, lam)
        h, h1, h2, h3 = _float_angle_data_3(g["gamma"])
        u = g["u"]
        W = g["W"]
        gr = g["gamma_r"]
        grr = g["gamma_rr"]
        grrr = g["gamma_rrr"]
        gl = g["gamma_lambda"]
        grl = g["gamma_rlambda"]
        grrl = g["gamma_rrlambda"]

        totals[0] += s * (-u * h + W * h1 * gr)
        totals[1] += s * (
            -2.0 * u * h1 * gr
            + W * (h2 * gr * gr + h1 * grr)
        )
        totals[2] += s * (
            -u * h1 * gl
            + W * (h2 * gl * gr + h1 * grl)
        )
        totals[3] += s * (
            -3.0 * u * (h2 * gr * gr + h1 * grr)
            + W * (h3 * gr**3 + 3.0 * h2 * gr * grr + h1 * grrr)
        )
        totals[4] += s * (
            -2.0 * u * (h2 * gl * gr + h1 * grl)
            + W * (
                h3 * gl * gr * gr
                + 2.0 * h2 * gr * grl
                + h2 * gl * grr
                + h1 * grrl
            )
        )
    return tuple(_FLOAT_WEIGHT * value for value in totals)


def F_float(r: float, lam: float) -> float:
    return _float_all(r, lam)[0]


def F_r_float(r: float, lam: float) -> float:
    return _float_all(r, lam)[1]


def F_lambda_float(r: float, lam: float) -> float:
    return _float_all(r, lam)[2]


def F_rr_float(r: float, lam: float) -> float:
    return _float_all(r, lam)[3]


def F_rlambda_float(r: float, lam: float) -> float:
    return _float_all(r, lam)[4]


dFdr_float = F_r_float
