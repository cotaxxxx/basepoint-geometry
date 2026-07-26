#!/usr/bin/env python3
"""Clean-room F_rr extension kernel for the item-3 C-G-TUBE centered form.

Extends prolate_circle_F_cleanroom (sha256 77e7a93c..., B-KERNEL-CR PASS)
with the exact second r-derivative of F. Derivation (audited in
prolate_item3_frr_symbolic_audit.py):

  Fint   = s( -u h + W h1 g1 )
  dFint  = s( -2u h1 g1 + W (h2 g1^2 + h1 g2) )
  d2Fint = s( -3u (h2 g1^2 + h1 g2)
              + W (h3 g1^3 + 3 h2 g1 g2 + h1 g3) )

with g1=gamma_r, g2=gamma_rr, g3=gamma_rrr and

  N   = u(1-ell) + r(u^2-1),   N_r = u^2-1,
  M   = N_r q - 3 N (r-u),     M_r = -N_r (r-u) - 3 N,
  g3  = (lam/w) (M_r q - 5 M (r-u)) q^(-7/2).

h3 = h'''(c) in the endpoint-regular hypergeometric form (derived from the
contiguous relation 0F1(3/2)-0F1(5/2) = -(beta^2/15) 0F1(7/2)):

  h3 = (2/15) (S P3 - 5 P2^2) / S^5,
  S = 0F1(;3/2;-h/4), P2 = 0F1(;5/2;-h/4), P3 = 0F1(;7/2;-h/4),
  h3(c=1) = -8/15.

Center-regular identities (odd F, F(0)=0):
  G(r)   = F(r)/r   = int_0^1 F_r(t r) dt
  G_r(r)            = int_0^1 t F_rr(t r) dt
so the center connection region needs no negative powers of r.
"""
from __future__ import annotations

from flint import acb, arb

import prolate_circle_F_cleanroom as base


def angle_data3(c: acb) -> tuple[acb, acb, acb, acb]:
    """Return h, h', h'', h''' for h(c)=acos(c)^2 (endpoint-regular)."""
    one = acb(1)
    z = (one - c) / 2
    H = z.hypgeom_2f1(one / 2, one / 2, acb(3) / 2)
    h = 4 * z * H * H
    x = -h / 4
    S = x.hypgeom_0f1(acb(3) / 2)
    P2 = x.hypgeom_0f1(acb(5) / 2)
    P3 = x.hypgeom_0f1(acb(7) / 2)
    h1 = -2 / S
    h2 = (acb(2) / 3) * P2 / S**3
    h3 = (acb(2) / 15) * (S * P3 - 5 * P2 * P2) / S**5
    return h, h1, h2, h3


def _geometry3(theta: acb, phi: acb, r: acb, lam: acb,
               analytic: bool) -> dict[str, acb]:
    g = base._geometry(theta, phi, r, lam, analytic)
    u, q, N = g["u"], g["q"], None
    ell = g["ell"]
    N = u * (1 - ell) + r * (u * u - 1)
    N_r = u * u - 1
    M = N_r * q - 3 * N * (r - u)
    M_r = -N_r * (r - u) - 3 * N
    sqrt_q = q.sqrt(analytic=analytic)
    g["gamma_rrr"] = (lam / g["w"]) * (M_r * q - 5 * M * (r - u)) / (q**3 * sqrt_q)
    return g


def _Frr_kernel(theta: acb, phi: acb, r: acb, lam: acb,
                analytic: bool) -> acb:
    g = _geometry3(theta, phi, r, lam, analytic)
    h, h1, h2, h3 = angle_data3(g["gamma"])
    g1, g2, g3 = g["gamma_r"], g["gamma_rr"], g["gamma_rrr"]
    return g["s"] * (
        -3 * g["u"] * (h2 * g1 * g1 + h1 * g2)
        + g["W"] * (h3 * g1**3 + 3 * h2 * g1 * g2 + h1 * g3)
    )


def Frr_expr_acb(r: acb, lam: acb, *, tol: arb, depth: int, limit: int) -> acb:
    return base._rigorous_integral_2d(_Frr_kernel, r, lam, tol, depth, limit)


def Frr_arb(r: arb, lam: arb, tol: str = "1e-8",
            depth: int = 12, limit: int = 200000) -> arb:
    v = Frr_expr_acb(acb(r), acb(lam), tol=arb(tol), depth=depth, limit=limit)
    return base._as_real(v, "Frr_arb")
