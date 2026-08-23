#!/usr/bin/env python3
"""
Stage-1 computational analytic package for the prolate-spheroid CAP.

This script is NOT yet the final computer-assisted proof:
it uses arbitrary-precision floating-point quadrature (mpmath), not
outward-rounded interval arithmetic. Its purpose is to freeze and independently
check the exact one-dimensional formulas that the interval proof must certify.

Geometry
--------
K_a = {(x,y,z): x^2+y^2+z^2/a^2 <= 1},  a >= 1,
p_r = (r,0,0).

The boundary is
    X(theta,phi) = (sin(theta)cos(phi), sin(theta)sin(phi), a cos(theta)).

The normalized cone-volume-weighted mean squared radial-normal angle is
    E_a(r) = (1/(4*pi)) int_0^pi int_0^(2*pi)
             (1-r sin(theta)cos(phi)) alpha(r,theta,phi)^2
             sin(theta) dphi dtheta.

We compute
    Q(a)  = d^2 E_a / dr^2 at r=0,
    H4(a) = d^4 E_a / dr^4 at r=0.

The O(2)-symmetric transverse Taylor expansion is
    E_a(r) = E_a(0) + Q(a) r^2/2 + H4(a) r^4/24 + O(r^6).

Candidate numerical result
--------------------------
    a_c = 4.72438340452113340672471215759...
    Q'(a_c) = -0.0946382010182073142289...
    H4(a_c) = -1.43848466593955621656...

The final CAP must replace mpmath evaluations by outward-rounded interval
quadrature and certify:
    Q(4.72438) > 0,
    Q(4.72439) < 0,
    Q'(a) < 0 on [4.72438, 4.72439],
    H4(a) < 0 on [4.72438, 4.72439].
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mpmath as mp


def h_derivatives(beta: mp.mpf) -> tuple[mp.mpf, mp.mpf, mp.mpf, mp.mpf]:
    """Return h^(j)(cos beta), j=1,...,4, for h(c)=acos(c)^2.

    Stable Taylor expansions are used near beta=0 to remove cancellation.
    """
    b = mp.mpf(beta)
    if abs(b) < mp.mpf("1e-6"):
        z = b * b
        h1 = (
            -2
            - z / 3
            - 7 * z**2 / 180
            - 31 * z**3 / 7560
            - 127 * z**4 / 302400
            - 73 * z**5 / 1710720
        )
        h2 = (
            mp.mpf(2) / 3
            + 4 * z / 15
            + 4 * z**2 / 63
            + 8 * z**3 / 675
            + 4 * z**4 / 2079
            + mp.mpf(5528) * z**5 / 19348875
        )
        h3 = (
            -mp.mpf(8) / 15
            - 12 * z / 35
            - 13 * z**2 / 105
            - mp.mpf(1153) * z**3 / 34650
            - mp.mpf(187619) * z**4 / 25225200
            - mp.mpf(3325549) * z**5 / 2270268000
        )
        h4 = (
            mp.mpf(24) / 35
            + 64 * z / 105
            + mp.mpf(1024) * z**2 / 3465
            + mp.mpf(70144) * z**3 / 675675
            + mp.mpf(140032) * z**4 / 4729725
            + mp.mpf(2395648) * z**5 / 328930875
        )
        return h1, h2, h3, h4

    s = mp.sin(b)
    c = mp.cos(b)
    h1 = -2 * b / s
    h2 = 2 / s**2 - 2 * b * c / s**3
    h3 = 6 * c / s**4 - 2 * b * (1 + 2 * c**2) / s**5
    h4 = (8 + 22 * c**2) / s**6 - 6 * b * c * (3 + 2 * c**2) / s**7
    return h1, h2, h3, h4


def local_parameters(a: mp.mpf, theta: mp.mpf):
    s = mp.sin(theta)
    c = mp.cos(theta)
    ell = s * s + a * a * c * c
    w = mp.sqrt(a * a * s * s + c * c)
    C = a / (w * mp.sqrt(ell))
    beta = mp.atan((a - 1 / a) * s * c)
    return s, c, ell, C, beta


def quadratic_integrand(theta: mp.mpf, a: mp.mpf) -> mp.mpf:
    """Integrand whose integral over [0,pi/2] is Q(a)."""
    s, _, ell, C, beta = local_parameters(a, theta)
    h1, h2, _, _ = h_derivatives(beta)

    b2 = C / ell**2 * (
        C * h2 * (ell - 1) ** 2 * s**2
        + h1 * ((2 * ell**2 - 4 * ell + 3) * s**2 - 2 * ell)
    )
    return mp.mpf("0.5") * s * b2


def Q(a: mp.mpf) -> mp.mpf:
    a = mp.mpf(a)
    return mp.quad(
        lambda theta: quadratic_integrand(theta, a),
        [0, mp.pi / 4, mp.pi / 2],
    )


def fourth_phi_coefficients(theta: mp.mpf, a: mp.mpf):
    """Coefficients A4,A2,A0 in the fourth r-derivative at r=0."""
    s, _, ell, C, beta = local_parameters(a, theta)
    h1, h2, h3, h4 = h_derivatives(beta)

    ell2 = ell**2
    ell3 = ell**3
    ell4 = ell**4

    A4 = C / ell4 * (
        C**3 * h4 * (ell - 1) ** 4
        + C**2
        * h3
        * (4 * ell4 - 24 * ell3 + 54 * ell2 - 52 * ell + 18)
        + C * h2 * (-24 * ell3 + 108 * ell2 - 168 * ell + 87)
        + h1 * (36 * ell2 - 120 * ell + 105)
    )

    A2 = -6 * C / ell3 * (
        C**2 * h3 * (ell - 1) ** 2
        + C * h2 * (4 * ell2 - 12 * ell + 9)
        + h1 * (2 * ell2 - 12 * ell + 15)
    )

    A0 = 3 * C / ell2 * (C * h2 + 3 * h1)
    return s, A4, A2, A0


def fourth_integrand(theta: mp.mpf, a: mp.mpf) -> mp.mpf:
    """Integrand whose integral over [0,pi/2] is H4(a)."""
    s, A4, A2, A0 = fourth_phi_coefficients(theta, a)
    phi_average = mp.mpf(3) / 4 * A4 * s**4 + A2 * s**2 + 2 * A0
    return mp.mpf("0.5") * s * phi_average


def H4(a: mp.mpf) -> mp.mpf:
    a = mp.mpf(a)
    return mp.quad(
        lambda theta: fourth_integrand(theta, a),
        [0, mp.pi / 4, mp.pi / 2],
    )


def build_report(dps: int = 60) -> dict:
    mp.mp.dps = dps

    root = mp.findroot(Q, (mp.mpf("4.7"), mp.mpf("4.75")))
    qprime = mp.diff(Q, root)
    h4_at_root = H4(root)

    checkpoints = {}
    for text in (
        "4.70",
        "4.72",
        "4.72438",
        "4.7243834",
        "4.72439",
        "4.73",
        "4.75",
    ):
        a = mp.mpf(text)
        checkpoints[text] = {
            "Q": mp.nstr(Q(a), 40),
            "Q_prime": mp.nstr(mp.diff(Q, a), 40),
            "H4": mp.nstr(H4(a), 40),
        }

    return {
        "status": "exploratory_high_precision_not_interval_certified",
        "precision_decimal_digits": dps,
        "geometry": "x^2+y^2+z^2/a^2 <= 1; transverse base point p=(r,0,0)",
        "candidate": {
            "a_c": mp.nstr(root, 50),
            "Q_at_a_c": mp.nstr(Q(root), 20),
            "Q_prime_at_a_c": mp.nstr(qprime, 50),
            "H4_at_a_c": mp.nstr(h4_at_root, 50),
            "quartic_Taylor_coefficient_H4_over_24": mp.nstr(
                h4_at_root / 24, 50
            ),
        },
        "proposed_CAP_bracket": {
            "a_left": "4.72438",
            "a_right": "4.72439",
            "required_signs": [
                "Q(a_left) > 0",
                "Q(a_right) < 0",
                "Q'(a) < 0 throughout [a_left,a_right]",
                "H4(a) < 0 throughout [a_left,a_right]",
            ],
        },
        "checkpoints": checkpoints,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dps", type=int, default=60)
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("prolate_cap_stage1_report.json"),
    )
    args = parser.parse_args()

    report = build_report(args.dps)
    args.json.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
