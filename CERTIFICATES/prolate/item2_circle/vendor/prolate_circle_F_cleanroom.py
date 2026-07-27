#!/usr/bin/env python3
"""Clean-room implementation of the item-0 F(r, lambda) kernel.

PROVENANCE
----------
This module is a NEW implementation. It is NOT the historical
``prolate_general_r_arb_kernels.py`` (sha256 ef065381...), whose source was
not recovered. Do not present this file, or any hash of it, as the original.

The defining formula is taken from Section 3 of Furuta,
"A Certified Stationary-Orbit Bifurcation for a Cone-Volume-Weighted
Radial-Normal Angle on Prolate Spheroids" (July 20, 2026):

  E_lambda(r) = (1/(2*pi)) integral_[0,pi/2] integral_[0,2*pi]
      (1-r*u) h(gamma) sin(theta) dphi dtheta,

  u = sin(theta) cos(phi),
  ell = sin(theta)^2 + lambda^2 cos(theta)^2,
  w^2 = lambda^2 sin(theta)^2 + cos(theta)^2,
  gamma = lambda (1-r*u) / (w sqrt(ell - 2*r*u + r^2)),
  h(c) = acos(c)^2.

The implementation differentiates this fixed-domain formula exactly under the
integral sign. The algebraic derivatives are independently checked by
``symbolic_audit_dFdr.py``. Equivalence with the historical kernel is claimed
only after the item0d regression and symbolic audit both pass.

Public interface:
  F_arb(r: arb, lam: arb) -> arb
  dFdr_arb(r: arb, lam: arb) -> arb
  F_float(r: float, lam: float) -> float
  dFdr_float(r: float, lam: float) -> float
"""
from __future__ import annotations

from typing import Callable
import math

from flint import acb, arb, ctx


class FormulaPending(NotImplementedError):
    """Retained for compatibility with the pre-formula clean-room harness."""


FORMULA_STATE = "FILLED"


def angle_data(c: acb) -> tuple[acb, acb, acb]:
    """Return h(c), h'(c), h''(c) for h(c)=acos(c)^2.

    The hypergeometric formulas remove the apparent singularity at c=1:

      z=(1-c)/2,
      h=4 z 2F1(1/2,1/2;3/2;z)^2,
      h'=-2/0F1(;3/2;-h/4),
      h''=(2/3)0F1(;5/2;-h/4)/0F1(;3/2;-h/4)^3.
    """
    one = acb(1)
    z = (one - c) / 2
    H = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    h = 4 * z * H * H
    x = -h / 4
    S = x.hypgeom_0f1(acb(3) / 2)
    T = x.hypgeom_0f1(acb(5) / 2)
    h1 = -2 / S
    h2 = (acb(2) / 3) * T / S**3
    return h, h1, h2


def _geometry(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    analytic: bool,
) -> dict[str, acb]:
    """Fixed-domain prolate geometry and exact r-derivatives of gamma."""
    s = theta.sin()
    c = theta.cos()
    u = s * phi.cos()

    ell = s * s + lam * lam * c * c
    w2 = lam * lam * s * s + c * c
    w = w2.sqrt(analytic=analytic)

    q = ell - 2 * r * u + r * r
    sqrt_q = q.sqrt(analytic=analytic)
    W = 1 - r * u
    gamma = lam * W / (w * sqrt_q)

    # Exact derivatives with respect to r.
    # N is the numerator in gamma_r = (lam/w) N q^(-3/2).
    N = u * (1 - ell) + r * (u * u - 1)
    gamma_r = (lam / w) * N / (q * sqrt_q)

    N_r = u * u - 1
    gamma_rr = (lam / w) * (
        N_r * q - 3 * N * (r - u)
    ) / (q * q * sqrt_q)

    return {
        "s": s,
        "u": u,
        "ell": ell,
        "w": w,
        "q": q,
        "W": W,
        "gamma": gamma,
        "gamma_r": gamma_r,
        "gamma_rr": gamma_rr,
    }


def _F_kernel(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    analytic: bool,
) -> acb:
    g = _geometry(theta, phi, r, lam, analytic)
    h, h1, _ = angle_data(g["gamma"])
    return g["s"] * (
        -g["u"] * h + g["W"] * h1 * g["gamma_r"]
    )


def _dFdr_kernel(
    theta: acb,
    phi: acb,
    r: acb,
    lam: acb,
    analytic: bool,
) -> acb:
    g = _geometry(theta, phi, r, lam, analytic)
    _, h1, h2 = angle_data(g["gamma"])
    return g["s"] * (
        -2 * g["u"] * h1 * g["gamma_r"]
        + g["W"] * (
            h2 * g["gamma_r"] ** 2
            + h1 * g["gamma_rr"]
        )
    )


def _rigorous_integral_2d(
    kernel: Callable[[acb, acb, acb, acb, bool], acb],
    r: acb,
    lam: acb,
    tol: arb,
    depth: int,
    limit: int,
) -> acb:
    """Validated fixed-domain integral for F or dF/dr.

    The integrand depends on phi only through cos(phi), so
    integral_[0,2*pi] = 2 integral_[0,pi]. Combining this with the
    manuscript normalization 1/(2*pi) leaves a prefactor 1/pi.
    """
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


# --------------------------------------------------------------------------
# FORMULA SECTION -- filled from the manuscript's exact integral formula.
# --------------------------------------------------------------------------
def F_expr_acb(r: acb, lam: acb, *, tol: arb, depth: int, limit: int) -> acb:
    """Validated enclosure of F(r,lambda)=partial_r E_lambda(r)."""
    return _rigorous_integral_2d(_F_kernel, r, lam, tol, depth, limit)


def dFdr_expr_acb(
    r: acb,
    lam: acb,
    *,
    tol: arb,
    depth: int,
    limit: int,
) -> acb:
    """Validated enclosure of partial_r F=partial_r^2 E_lambda(r)."""
    return _rigorous_integral_2d(_dFdr_kernel, r, lam, tol, depth, limit)
# --------------------------------------------------------------------------


_DEF_TOL = "1e-8"
_DEF_DEPTH = 12
_DEF_LIMIT = 200000


def _as_real(x: acb, where: str) -> arb:
    if not bool(0 in x.imag):
        raise ValueError(f"{where}: imaginary part excludes 0: {x.imag}")
    return x.real


def F_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    v = F_expr_acb(acb(r), acb(lam), tol=arb(tol), depth=depth, limit=limit)
    return _as_real(v, "F_arb")


def dFdr_arb(
    r: arb,
    lam: arb,
    tol: str = _DEF_TOL,
    depth: int = _DEF_DEPTH,
    limit: int = _DEF_LIMIT,
) -> arb:
    v = dFdr_expr_acb(
        acb(r), acb(lam), tol=arb(tol), depth=depth, limit=limit
    )
    return _as_real(v, "dFdr_arb")


# Non-rigorous fixed midpoint grid for B-SEED only. The rigorous functions
# above never use this path.
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


def _float_pair(r: float, lam: float) -> tuple[float, float]:
    total_F = 0.0
    total_dF = 0.0
    lam2 = lam * lam
    for s, c, cos_phi in _FLOAT_GEOMETRY:
        u = s * cos_phi
        ell = s * s + lam2 * c * c
        w = math.sqrt(lam2 * s * s + c * c)
        q = ell - 2 * r * u + r * r
        sqrt_q = math.sqrt(q)
        W = 1 - r * u
        gamma = lam * W / (w * sqrt_q)
        gamma = min(1.0, max(-1.0, gamma))
        beta = math.acos(gamma)
        h = beta * beta
        one_minus = max(0.0, 1 - gamma * gamma)
        if one_minus < 1e-20:
            h1 = -2.0
            h2 = 2.0 / 3.0
        else:
            root = math.sqrt(one_minus)
            h1 = -2 * beta / root
            h2 = 2 / one_minus - 2 * gamma * beta / (one_minus * root)

        N = u * (1 - ell) + r * (u * u - 1)
        gamma_r = (lam / w) * N / (q * sqrt_q)
        gamma_rr = (lam / w) * (
            (u * u - 1) * q - 3 * N * (r - u)
        ) / (q * q * sqrt_q)

        total_F += s * (-u * h + W * h1 * gamma_r)
        total_dF += s * (
            -2 * u * h1 * gamma_r
            + W * (h2 * gamma_r * gamma_r + h1 * gamma_rr)
        )
    return _FLOAT_WEIGHT * total_F, _FLOAT_WEIGHT * total_dF


def F_float(r: float, lam: float) -> float:
    return _float_pair(r, lam)[0]


def dFdr_float(r: float, lam: float) -> float:
    return _float_pair(r, lam)[1]
