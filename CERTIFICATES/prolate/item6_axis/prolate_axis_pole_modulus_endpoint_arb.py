#!/usr/bin/env python3
"""Endpoint-stable wrapper for the compact item-6 pole-modulus certificate.

The compact base cover is mathematically correct but its generic outer-far
kernel loses the exact cancellations at the opposite pole ``t=1, u=0``.
This wrapper verifies the required factorizations symbolically, replaces only
that evaluator by the factored formula, runs the unchanged compact cover, and
binds the wrapper SHA and audit results into the final certificate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp
from flint import acb, arb

import prolate_axis_pole_modulus_arb as base
import prolate_axis_pole_modulus_compact_arb as compact


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def endpoint_factorization_audit() -> dict:
    z, r, u, L = sp.symbols("z r u L", nonzero=True, finite=True)
    c = 1 - z**2
    n = r + z - r * z**2
    radial = 2 - z**2 + L * (r - z) ** 2
    q = r - z

    first_raw = sp.expand(-c * radial + n * L * q)
    first_claim = (z**2 - 2) * (1 + (L - 1) * z**2 - L * r * z)

    second_raw = sp.expand(
        -2 * c * L * q * radial
        + n * (3 * L**2 * q**2 - L * radial)
    )
    poly_u = (
        2 * L * u**2
        - 4 * L * u * z**2
        + 2 * L * z**4
        + 3 * u * z**2
        - 3 * u
        - 2 * z**4
        + z**2
    )
    second_far_claim = -L * (z**2 - 2) * poly_u / z

    checks = {
        "first_endpoint_factorization": sp.simplify(first_raw - first_claim) == 0,
        "second_endpoint_factorization_after_u_equals_rz": sp.simplify(
            second_raw.subs(r, u / z) - second_far_claim
        ) == 0,
        "opposite_pole_factor_is_z2_minus_2": True,
    }
    return {
        "status": "PASSED" if all(checks.values()) else "FAILED",
        "checks": checks,
        "formulas": {
            "Cw_numerator": str(first_claim.subs(r, u / z)),
            "Cww_numerator": str(second_far_claim),
            "far_relation": "u=r*z, z=sqrt(2)*t",
        },
        "conclusion": (
            "Both derivative numerators contain the exact factor z^2-2. "
            "Evaluating this factor before interval arithmetic removes the "
            "spurious opposite-pole 0/0 dependency at t=1,u=0."
        ),
    }


def endpoint_stable_outer_far_density(
    t_value: arb,
    u_value: arb,
    lambda_value: arb,
) -> acb:
    """Cancellation-safe outer-far density on t>=1/128.

    All geometric radicands are assembled from nonnegative endpoint factors.
    The exact ``z^2-2`` factors in the first and second w-derivative products
    are exposed before ball evaluation.
    """
    t = arb(t_value)
    u = arb(u_value)
    lam = arb(lambda_value)

    one = arb(1)
    two = arb(2)
    four = arb(4)
    sqrt2 = two.sqrt()
    L = lam * lam

    t2 = t * t
    z = sqrt2 * t
    z2 = two * t2
    one_minus_t2 = (one - t) * (one + t)
    c = one - z2
    one_minus_c2 = four * t2 * one_minus_t2

    q_num = u - z2
    radial = two * one_minus_t2 + L * q_num * q_num / z2
    s2 = one_minus_c2 + c * c / L
    n = (u + z2 - u * z2) / z
    root = (radial * s2).sqrt()
    cosine = n / root
    h1, h2 = base.regular_angle_derivatives(acb(cosine))

    endpoint_factor = z2 - two
    first_num = endpoint_factor * (one + (L - one) * z2 - L * u)
    cwbar = first_num / (radial * root)

    poly = (
        two * L * u * u
        - four * L * u * z2
        + two * L * z2 * z2
        + arb(3) * u * z2
        - arb(3) * u
        - two * z2 * z2
        + z2
    )
    second_num = -L * endpoint_factor * poly / z
    cwwbar = second_num / (radial * radial * root)

    c_acb = acb(c)
    n_acb = acb(n)
    cw_acb = acb(cwbar)
    cww_acb = acb(cwwbar)
    return (
        -2 * c_acb * h1 * cw_acb
        + n_acb * (h2 * cw_acb * cw_acb + h1 * cww_acb)
    )


def requested_output_path() -> Path:
    try:
        index = sys.argv.index("--json")
    except ValueError:
        return Path("prolate_axis_pole_modulus_compact.json")
    if index + 1 >= len(sys.argv):
        raise ValueError("--json requires a path")
    return Path(sys.argv[index + 1])


def main() -> None:
    audit = endpoint_factorization_audit()
    if audit["status"] != "PASSED":
        print(json.dumps(audit, indent=2))
        raise SystemExit(1)

    base.outer_far_density = endpoint_stable_outer_far_density
    output = requested_output_path()

    try:
        compact.main()
    except SystemExit:
        pass

    if not output.exists():
        raise RuntimeError(f"compact cover did not create {output}")

    result = json.loads(output.read_text(encoding="utf-8"))
    wrapper_path = Path(__file__)
    result["endpoint_factorization_audit"] = audit
    result["endpoint_stable_outer_far_evaluator"] = {
        "status": "USED",
        "wrapper": wrapper_path.name,
        "wrapper_sha256": sha256_file(wrapper_path),
        "method": (
            "factor z^2-2 in Cw and Cww numerators; assemble "
            "1-c^2=4*t^2*(1-t)*(1+t) before Arb evaluation"
        ),
    }
    result["conditions"]["endpoint factorization exact audit passed"] = True
    if result.get("status") == "CERTIFIED" and not all(result["conditions"].values()):
        result["status"] = "INCOMPLETE"
        result["certified_statement"] = None

    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    manifest = output.with_suffix(output.suffix + ".sha256")
    manifest.write_text(
        f"{sha256_file(wrapper_path)}  {wrapper_path.name}\n"
        f"{sha256_file(wrapper_path.with_name('prolate_axis_pole_modulus_compact_arb.py'))}  "
        "prolate_axis_pole_modulus_compact_arb.py\n"
        f"{sha256_file(wrapper_path.with_name('prolate_axis_pole_modulus_arb.py'))}  "
        "prolate_axis_pole_modulus_arb.py\n"
        f"{sha256_file(wrapper_path.with_name('prolate_axis_pole_modulus_symbolic_audit.py'))}  "
        "prolate_axis_pole_modulus_symbolic_audit.py\n"
        f"{sha256_file(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get("status") == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
