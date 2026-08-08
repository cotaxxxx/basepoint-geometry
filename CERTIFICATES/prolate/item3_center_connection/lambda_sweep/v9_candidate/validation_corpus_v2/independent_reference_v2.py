#!/usr/bin/env python3
"""Independent real-arithmetic reference path for Item 3 sweep v9 validation.

This module intentionally imports no candidate/prototype kernel, adapter, runner, checker,
or checkpoint source.  It evaluates the real F integral by a fixed midpoint cubature using
Python's math module and obtains r derivatives by symmetric finite differences of that
independently integrated F.  It is validation support only, not a rigorous enclosure.
"""
from __future__ import annotations

import math


def _h_h1(gamma: float) -> tuple[float, float]:
    # Physical-domain removable limit h'(1)=-2.
    if gamma >= 1.0 - 1.0e-13:
        return 0.0, -2.0
    if gamma <= -1.0:
        gamma = -1.0 + 1.0e-15
    a = math.acos(gamma)
    s = math.sqrt(max(0.0, 1.0 - gamma * gamma))
    return a * a, -2.0 * a / s


def _phi_f(theta: float, phi: float, r: float, lam: float) -> float:
    s = math.sin(theta)
    c = math.cos(theta)
    c2 = c * c
    u = s * math.cos(phi)
    ell = s * s + lam * lam * c2
    w2 = lam * lam * s * s + c2
    w = math.sqrt(w2)
    q = ell - 2.0 * r * u + r * r
    sqrt_q = math.sqrt(q)
    W = 1.0 - r * u
    B = lam / w
    gamma = B * W / sqrt_q
    # Numerical roundoff may move a physical gamma infinitesimally above one.
    gamma = min(1.0, max(-1.0, gamma))
    d = r - u
    N = u * (1.0 - ell) + r * (u * u - 1.0)
    gamma_r = B * N / (q * sqrt_q)
    h, h1 = _h_h1(gamma)
    return s * (-u * h + W * h1 * gamma_r)


def F_reference(r: float, lam: float, *, n_theta: int = 80, n_phi: int = 120) -> float:
    if not (0.0 < r < 1.0 and lam >= 1.0):
        raise ValueError("reference domain requires 0<r<1, lambda>=1")
    if n_theta <= 0 or n_phi <= 0:
        raise ValueError("positive cubature sizes required")
    dtheta = (math.pi / 2.0) / n_theta
    dphi = math.pi / n_phi
    total = 0.0
    for i in range(n_theta):
        theta = (i + 0.5) * dtheta
        row = 0.0
        for j in range(n_phi):
            phi = (j + 0.5) * dphi
            row += _phi_f(theta, phi, r, lam)
        total += row
    return total * dtheta * dphi / math.pi


def F_r_reference(r: float, lam: float, *, h: float = 2.0e-4) -> float:
    if not (h > 0.0 and r - h > 0.0 and r + h < 1.0):
        raise ValueError("finite-difference step leaves domain")
    return (F_reference(r + h, lam) - F_reference(r - h, lam)) / (2.0 * h)


def F_rr_reference(r: float, lam: float, *, h: float = 4.0e-4) -> float:
    if not (h > 0.0 and r - h > 0.0 and r + h < 1.0):
        raise ValueError("finite-difference step leaves domain")
    return (
        F_reference(r + h, lam)
        - 2.0 * F_reference(r, lam)
        + F_reference(r - h, lam)
    ) / (h * h)


REFERENCE_POINTS = (
    (0.0165, 4.71999910),
    (0.0200, 4.71999925),
    (0.0240, 4.71999940),
    (0.0300, 4.71999955),
    (0.0360, 4.71999975),
    (0.0420, 4.71999995),
)
