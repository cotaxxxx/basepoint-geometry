#!/usr/bin/env python3
'''
Independent exact symbolic audit of the quartic kernel H4.

The raw weighted angular integrand is

    F(r) = (1-r*u) h(gamma(r)),
    h(c) = acos(c)^2,

with

    gamma(r)
      = C (1-r*u) (1 - 2*r*u/ell + r^2/ell)^(-1/2).

The script differentiates gamma exactly through order four, applies the
chain rule to h(gamma(r)), includes the derivative of the cone-volume
weight (1-r*u), and verifies:

  1. F^(4)(0) = A4*u^4 + A2*u^2 + A0 pointwise;
  2. the coefficients of u^4, u^2 and u^0 agree separately;
  3. the odd powers vanish identically;
  4. exact phi averaging gives the H4 kernel used by Arb.
'''

from __future__ import annotations

import sympy as sp


def main() -> None:
    r, u, ell, C, s = sp.symbols(
        "r u ell C s", real=True
    )
    h1, h2, h3, h4 = sp.symbols(
        "h1 h2 h3 h4"
    )

    gamma = (
        C
        * (1 - r * u)
        * (1 - 2 * r * u / ell + r**2 / ell) ** sp.Rational(-1, 2)
    )

    g1, g2, g3, g4 = [
        sp.factor(sp.simplify(sp.diff(gamma, r, order).subs(r, 0)))
        for order in range(1, 5)
    ]

    composite_third = (
        h3 * g1**3
        + 3 * h2 * g1 * g2
        + h1 * g3
    )

    composite_fourth = (
        h4 * g1**4
        + 6 * h3 * g1**2 * g2
        + 3 * h2 * g2**2
        + 4 * h2 * g1 * g3
        + h1 * g4
    )

    # For w(r)=1-r*u:
    # F^(4)(0)=(h o gamma)^(4)(0)-4u(h o gamma)^(3)(0).
    raw_fourth = sp.cancel(
        composite_fourth - 4 * u * composite_third
    )

    A4 = C / ell**4 * (
        C**3 * h4 * (ell - 1) ** 4
        + C**2
        * h3
        * (
            4 * ell**4
            - 24 * ell**3
            + 54 * ell**2
            - 52 * ell
            + 18
        )
        + C
        * h2
        * (
            -24 * ell**3
            + 108 * ell**2
            - 168 * ell
            + 87
        )
        + h1 * (
            36 * ell**2
            - 120 * ell
            + 105
        )
    )

    A2 = -6 * C / ell**3 * (
        C**2 * h3 * (ell - 1) ** 2
        + C * h2 * (
            4 * ell**2
            - 12 * ell
            + 9
        )
        + h1 * (
            2 * ell**2
            - 12 * ell
            + 15
        )
    )

    A0 = 3 * C / ell**2 * (
        C * h2 + 3 * h1
    )

    expected_pointwise = sp.cancel(
        A4 * u**4 + A2 * u**2 + A0
    )

    pointwise_difference = sp.factor(
        sp.together(raw_fourth - expected_pointwise)
    )

    polynomial = sp.Poly(sp.cancel(raw_fourth), u)
    coefficient_checks = {
        "u^4": sp.factor(
            sp.together(polynomial.coeff_monomial(u**4) - A4)
        ),
        "u^2": sp.factor(
            sp.together(polynomial.coeff_monomial(u**2) - A2)
        ),
        "u^0": sp.factor(
            sp.together(polynomial.coeff_monomial(1) - A0)
        ),
        "u^3": polynomial.coeff_monomial(u**3),
        "u^1": polynomial.coeff_monomial(u),
    }

    phi_integrated_from_raw = sp.pi * (
        sp.Rational(3, 4)
        * polynomial.coeff_monomial(u**4)
        * s**4
        + polynomial.coeff_monomial(u**2) * s**2
        + 2 * polynomial.coeff_monomial(1)
    )

    expected_phi_integrated = sp.pi * (
        sp.Rational(3, 4) * A4 * s**4
        + A2 * s**2
        + 2 * A0
    )

    phi_difference = sp.factor(
        sp.together(
            phi_integrated_from_raw - expected_phi_integrated
        )
    )

    print("gamma derivatives at r=0:")
    print("g1 =", g1)
    print("g2 =", g2)
    print("g3 =", g3)
    print("g4 =", g4)
    print()

    print("Pointwise identity difference:")
    print(pointwise_difference)
    print()

    print("Coefficient-by-coefficient differences:")
    for label, value in coefficient_checks.items():
        print(f"{label}: {value}")
    print()

    print("Phi-integrated identity difference:")
    print(phi_difference)
    print()

    assert pointwise_difference == 0
    assert all(value == 0 for value in coefficient_checks.values())
    assert phi_difference == 0

    print("PASS: exact differentiation gives precisely A4, A2 and A0.")
    print("PASS: odd powers vanish identically.")
    print("PASS: exact phi averaging gives precisely the H4 integrand.")


if __name__ == "__main__":
    main()
