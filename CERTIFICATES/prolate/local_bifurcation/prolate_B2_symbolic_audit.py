#!/usr/bin/env python3
"""
Independent symbolic audit of the transverse quadratic kernel B2.

The script starts from the raw weighted angular integrand

    F(r) = (1-r*u) h(cos_alpha(r)),
    h(c) = acos(c)^2,

where

    cos_alpha(r)
      = C (1-r*u) (1 - 2*r*u/ell + r^2/ell)^(-1/2).

Here u = sin(theta) cos(phi), ell = sin(theta)^2 + a^2 cos(theta)^2,
and C = a/(sqrt(a^2 sin(theta)^2 + cos(theta)^2)*sqrt(ell)).

It differentiates F twice with respect to r at r=0, performs the exact
phi moments

    integral_0^(2*pi) 1 dphi = 2*pi,
    integral_0^(2*pi) u^2 dphi = pi sin(theta)^2,

and verifies that the result is exactly the B2 kernel used by the Arb CAP.
"""

from __future__ import annotations

import sympy as sp


def main() -> None:
    r, u, ell, C, s = sp.symbols(
        "r u ell C s", real=True, positive=True
    )
    h = sp.Function("h")

    cos_alpha = (
        C
        * (1 - r * u)
        * (1 - 2 * r * u / ell + r**2 / ell) ** sp.Rational(-1, 2)
    )
    weighted_integrand = (1 - r * u) * h(cos_alpha)

    raw_second = sp.simplify(
        sp.diff(weighted_integrand, r, 2).subs(r, 0)
    )

    h1 = sp.Symbol("h1")
    h2 = sp.Symbol("h2")
    abstract_second = raw_second.xreplace(
        {
            sp.Subs(sp.Derivative(h(sp.Symbol("_xi_1")), sp.Symbol("_xi_1")),
                    sp.Symbol("_xi_1"), C): h1,
            sp.Subs(sp.Derivative(h(sp.Symbol("_xi_1")),
                                  (sp.Symbol("_xi_1"), 2)),
                    sp.Symbol("_xi_1"), C): h2,
            sp.Derivative(h(C), C): h1,
            sp.Derivative(h(C), (C, 2)): h2,
        }
    )
    abstract_second = sp.simplify(abstract_second)

    expected_pointwise = C / ell**2 * (
        C * h2 * (ell - 1) ** 2 * u**2
        + h1 * ((2 * ell**2 - 4 * ell + 3) * u**2 - ell)
    )

    pointwise_difference = sp.simplify(
        abstract_second - expected_pointwise
    )

    # Exact phi integration by replacing u^2 moments.
    phi_integrated = sp.expand(expected_pointwise)
    phi_integrated = phi_integrated.subs(u**2, s**2 / 2)
    # The preceding replacement gives the phi average. Multiply by 2*pi.
    phi_integrated = sp.simplify(2 * sp.pi * phi_integrated)

    expected_phi_integrated = sp.pi * C / ell**2 * (
        C * h2 * (ell - 1) ** 2 * s**2
        + h1
        * (
            (2 * ell**2 - 4 * ell + 3) * s**2
            - 2 * ell
        )
    )

    phi_difference = sp.simplify(
        phi_integrated - expected_phi_integrated
    )

    print("Raw second derivative:")
    print(sp.factor(abstract_second))
    print()
    print("Pointwise identity difference:")
    print(pointwise_difference)
    print()
    print("Phi-integrated identity difference:")
    print(phi_difference)

    assert pointwise_difference == 0
    assert phi_difference == 0

    print()
    print("PASS: the independently differentiated raw integrand")
    print("      gives exactly the B2 kernel used in the CAP.")


if __name__ == "__main__":
    main()
