#!/usr/bin/env python3
"""
Rigorous Arb certificate for the transverse degeneracy of the
cone-volume-weighted mean squared radial-normal angle on prolate spheroids.

This script uses python-flint / Arb ball arithmetic and Arb's rigorous
complex numerical integration. It certifies:

  1. Q(4.7) > 0,
  2. Q(4.75) < 0,
  3. Q'(a) < 0 for every a in [4.7, 4.75],
  4. H4(a) < 0 for every a in [4.7, 4.75].

It also certifies the narrower localization

  Q(4.72438) > 0,  Q(4.72439) < 0.

Definitions
-----------
K_a = {(x,y,z): x^2 + y^2 + z^2/a^2 <= 1},  a >= 1,
p_r = (r,0,0),

E_a(r) = E_a(0) + Q(a) r^2/2 + H4(a) r^4/24 + O(r^6).

Endpoint regularization
-----------------------
Let h(c) = acos(c)^2, c = cos(beta), z = beta^2, and

  S = 0F1(;3/2;-z/4) = sin(beta)/beta,
  T = 0F1(;5/2;-z/4),
  U = 0F1(;7/2;-z/4),
  V = 0F1(;9/2;-z/4).

Then the derivatives of h with respect to c admit the cancellation-free
entire representations

  h1 = -2/S,
  h2 = (2/3) T/S^3,
  h3 = (2/15) U/S^4 - (2/3) T^2/S^5,
  h4 = (2/105) V/S^5 - (4/9) U T/S^6 + (10/9) T^3/S^7.

These formulas remain regular at beta=0, so no endpoint cutoff delta or
separate Taylor chart is required.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from flint import acb, arb, ctx, fmpq


I = acb(0, 1)


def rational_ball(p: int, q: int = 1) -> arb:
    """An Arb ball containing the exact rational p/q."""
    return arb(fmpq(p, q))


def closed_rational_interval(
    lo_p: int, lo_q: int, hi_p: int, hi_q: int
) -> arb:
    """An Arb ball enclosing the exact closed rational interval [lo, hi]."""
    lo = fmpq(lo_p, lo_q)
    hi = fmpq(hi_p, hi_q)
    return arb((lo + hi) / 2, (hi - lo) / 2)


def atan_analytic(z: acb, analytic: bool) -> acb:
    """Principal atan using logarithms with branch checking for integration."""
    return (
        (1 + I * z).log(analytic=analytic)
        - (1 - I * z).log(analytic=analytic)
    ) / (2 * I)


def h_derivatives_from_t(
    t: acb, analytic: bool
) -> tuple[acb, acb, acb, acb]:
    """Return h^(1),...,h^(4) for h(c)=acos(c)^2, c=cos(atan(t)).

    Hypergeometric formulas remove the beta=0 endpoint singularities.
    """
    beta = atan_analytic(t, analytic)
    x = -(beta * beta) / 4

    S = x.hypgeom_0f1(acb(3) / 2)
    T = x.hypgeom_0f1(acb(5) / 2)
    U = x.hypgeom_0f1(acb(7) / 2)
    V = x.hypgeom_0f1(acb(9) / 2)

    h1 = -2 / S
    h2 = acb(2) / 3 * T / S**3
    h3 = acb(2) / 15 * U / S**4 - acb(2) / 3 * T**2 / S**5
    h4 = (
        acb(2) / 105 * V / S**5
        - acb(4) / 9 * U * T / S**6
        + acb(10) / 9 * T**3 / S**7
    )
    return h1, h2, h3, h4


@dataclass
class Dual:
    """First-order automatic differentiation over Acb balls."""

    value: acb
    derivative: acb

    def __init__(self, value, derivative=0):
        self.value = acb(value)
        self.derivative = acb(derivative)

    def __add__(self, other):
        other = as_dual(other)
        return Dual(
            self.value + other.value,
            self.derivative + other.derivative,
        )

    __radd__ = __add__

    def __neg__(self):
        return Dual(-self.value, -self.derivative)

    def __sub__(self, other):
        return self + (-as_dual(other))

    def __rsub__(self, other):
        return as_dual(other) - self

    def __mul__(self, other):
        other = as_dual(other)
        return Dual(
            self.value * other.value,
            self.derivative * other.value
            + self.value * other.derivative,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = as_dual(other)
        return Dual(
            self.value / other.value,
            (
                self.derivative * other.value
                - self.value * other.derivative
            )
            / other.value**2,
        )

    def __rtruediv__(self, other):
        return as_dual(other) / self

    def __pow__(self, exponent: int):
        if not isinstance(exponent, int):
            raise TypeError("Dual supports only integer powers")
        if exponent == 0:
            return Dual(1, 0)
        return Dual(
            self.value**exponent,
            exponent
            * self.value ** (exponent - 1)
            * self.derivative,
        )

    def sqrt(self, analytic: bool):
        root = self.value.sqrt(analytic=analytic)
        return Dual(root, self.derivative / (2 * root))


def as_dual(value) -> Dual:
    return value if isinstance(value, Dual) else Dual(value, 0)


def local_scalar(theta: acb, a: acb, analytic: bool):
    s = theta.sin()
    c = theta.cos()
    ell = s * s + a * a * c * c
    w = (a * a * s * s + c * c).sqrt(analytic=analytic)
    C = a / (w * ell.sqrt(analytic=analytic))
    t = (a - 1 / a) * s * c
    return s, ell, C, t


def q_integrand(theta: acb, a: acb, analytic: bool) -> acb:
    """Integrand on [0,pi/2] whose integral is Q(a)."""
    s, ell, C, t = local_scalar(theta, a, analytic)
    h1, h2, _, _ = h_derivatives_from_t(t, analytic)

    b2 = C / ell**2 * (
        C * h2 * (ell - 1) ** 2 * s**2
        + h1
        * (
            (2 * ell**2 - 4 * ell + 3) * s**2
            - 2 * ell
        )
    )
    return s * b2 / 2


def qprime_integrand(
    theta: acb, a_interval: arb, analytic: bool
) -> acb:
    """Rigorous enclosure of d/da of the Q integrand over an a interval."""
    s = theta.sin()
    c = theta.cos()
    a = Dual(acb(a_interval), 1)

    ell = s * s + a * a * c * c
    w = (a * a * s * s + c * c).sqrt(analytic)
    C = a / (w * ell.sqrt(analytic))
    t = (a - 1 / a) * s * c

    h1, h2, h3, _ = h_derivatives_from_t(t.value, analytic)

    # d h_j(C(a))/da = h_{j+1}(C(a)) C'(a)
    H1 = Dual(h1, h2 * C.derivative)
    H2 = Dual(h2, h3 * C.derivative)

    b2 = C / ell**2 * (
        C * H2 * (ell - 1) ** 2 * s**2
        + H1
        * (
            (2 * ell**2 - 4 * ell + 3) * s**2
            - 2 * ell
        )
    )
    return (s * b2 / 2).derivative


def h4_integrand(
    theta: acb, a_interval: arb, analytic: bool
) -> acb:
    """Rigorous enclosure of the fourth transverse derivative integrand."""
    a = acb(a_interval)
    s, ell, C, t = local_scalar(theta, a, analytic)
    h1, h2, h3, h4 = h_derivatives_from_t(t, analytic)

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
        + h1 * (36 * ell**2 - 120 * ell + 105)
    )

    A2 = -6 * C / ell**3 * (
        C**2 * h3 * (ell - 1) ** 2
        + C * h2 * (4 * ell**2 - 12 * ell + 9)
        + h1 * (2 * ell**2 - 12 * ell + 15)
    )

    A0 = 3 * C / ell**2 * (C * h2 + 3 * h1)

    phi_average = (
        acb(3) / 4 * A4 * s**4
        + A2 * s**2
        + 2 * A0
    )
    return s * phi_average / 2


def rigorous_integral(
    func: Callable[[acb, bool], acb],
    tolerance: arb,
    depth_limit: int,
    eval_limit: int,
) -> acb:
    return acb.integral(
        func,
        0,
        arb.pi() / 2,
        abs_tol=tolerance,
        rel_tol=tolerance,
        depth_limit=depth_limit,
        eval_limit=eval_limit,
    )


def interval_record(value: acb) -> dict:
    return {
        "real": {
            "ball": str(value.real),
            "lower": str(value.real.lower()),
            "upper": str(value.real.upper()),
        },
        "imaginary": {
            "ball": str(value.imag),
            "contains_zero": bool(0 in value.imag),
        },
    }


def certify_positive(value: acb) -> bool:
    return bool(value.real > 0 and 0 in value.imag)


def certify_negative(value: acb) -> bool:
    return bool(value.real < 0 and 0 in value.imag)


def rational_partition(
    lo: fmpq, hi: fmpq, parts: int
) -> list[tuple[fmpq, fmpq, arb]]:
    width = (hi - lo) / parts
    result = []
    for index in range(parts):
        left = lo + index * width
        right = left + width
        result.append(
            (
                left,
                right,
                arb((left + right) / 2, (right - left) / 2),
            )
        )
    return result


def run_certificate(
    dps: int,
    tolerance_text: str,
    subdivisions: int,
    depth_limit: int,
    eval_limit: int,
) -> dict:
    ctx.dps = dps
    tolerance = arb(tolerance_text)

    wide_left = rational_ball(47, 10)
    wide_right = rational_ball(19, 4)
    narrow_left = rational_ball(236219, 50000)     # 4.72438
    narrow_right = rational_ball(472439, 100000)   # 4.72439

    fixed_q = {}
    for label, point in (
        ("4.7", wide_left),
        ("4.75", wide_right),
        ("4.72438", narrow_left),
        ("4.72439", narrow_right),
    ):
        value = rigorous_integral(
            lambda theta, analytic, point=point: q_integrand(
                theta, acb(point), analytic
            ),
            tolerance,
            depth_limit,
            eval_limit,
        )
        fixed_q[label] = {
            **interval_record(value),
            "positive": certify_positive(value),
            "negative": certify_negative(value),
        }

    lo = fmpq(47, 10)
    hi = fmpq(19, 4)
    partition = rational_partition(lo, hi, subdivisions)

    qprime_records = []
    h4_records = []

    for left, right, a_interval in partition:
        qprime_value = rigorous_integral(
            lambda theta, analytic, a_interval=a_interval:
                qprime_integrand(theta, a_interval, analytic),
            tolerance,
            depth_limit,
            eval_limit,
        )
        h4_value = rigorous_integral(
            lambda theta, analytic, a_interval=a_interval:
                h4_integrand(theta, a_interval, analytic),
            tolerance,
            depth_limit,
            eval_limit,
        )

        interval_label = f"[{left}, {right}]"
        qprime_records.append(
            {
                "a_interval": interval_label,
                **interval_record(qprime_value),
                "certified_negative": certify_negative(qprime_value),
            }
        )
        h4_records.append(
            {
                "a_interval": interval_label,
                **interval_record(h4_value),
                "certified_negative": certify_negative(h4_value),
            }
        )

    conditions = {
        "Q(4.7) > 0": fixed_q["4.7"]["positive"],
        "Q(4.75) < 0": fixed_q["4.75"]["negative"],
        "Q'(a) < 0 on [4.7,4.75]": all(
            item["certified_negative"] for item in qprime_records
        ),
        "H4(a) < 0 on [4.7,4.75]": all(
            item["certified_negative"] for item in h4_records
        ),
        "Q(4.72438) > 0": fixed_q["4.72438"]["positive"],
        "Q(4.72439) < 0": fixed_q["4.72439"]["negative"],
    }

    return {
        "status": (
            "CERTIFIED"
            if all(conditions.values())
            else "FAILED_OR_INCONCLUSIVE"
        ),
        "arithmetic": "python-flint Arb/Acb ball arithmetic",
        "decimal_precision": dps,
        "integration_tolerance": tolerance_text,
        "wide_proof_interval": "[4.7, 4.75]",
        "narrow_certified_root_bracket": "[4.72438, 4.72439]",
        "parameter_subdivisions": subdivisions,
        "conditions": conditions,
        "fixed_Q_evaluations": fixed_q,
        "Qprime_partition": qprime_records,
        "H4_partition": h4_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dps", type=int, default=50)
    parser.add_argument("--tolerance", default="1e-20")
    parser.add_argument("--subdivisions", type=int, default=5)
    parser.add_argument("--depth-limit", type=int, default=30)
    parser.add_argument("--eval-limit", type=int, default=200000)
    parser.add_argument(
        "--json",
        type=Path,
        default=Path("prolate_cap_arb_certificate.json"),
    )
    args = parser.parse_args()

    report = run_certificate(
        dps=args.dps,
        tolerance_text=args.tolerance,
        subdivisions=args.subdivisions,
        depth_limit=args.depth_limit,
        eval_limit=args.eval_limit,
    )

    args.json.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if report["status"] != "CERTIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
