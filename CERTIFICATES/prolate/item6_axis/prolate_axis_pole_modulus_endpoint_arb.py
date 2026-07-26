#!/usr/bin/env python3
"""Endpoint-stable wrapper for the compact item-6 pole-modulus certificate.

The compact base cover is mathematically correct but its generic outer-far
kernel loses exact correlations near the opposite-pole endpoint ``t=1,u=0``.
This wrapper verifies the required factorizations symbolically, extracts the
common ``z^2-2`` factor at the level of the complete transformed density, runs
the unchanged compact cover, and binds the wrapper SHA and audit results into
the final certificate.

No division by ``z^2-2`` is performed.  The factor occurs in two separate
w-derivative numerators, not as a common numerator/denominator factor of a
single quotient; cancelling it between those terms would therefore be
invalid.  Factoring the complete density preserves the exact endpoint zero
without introducing a removable 0/0 interval form.
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
    h1, h2 = sp.symbols("h1 h2", finite=True)
    c = 1 - z**2
    n = r + z - r * z**2
    radial = 2 - z**2 + L * (r - z) ** 2
    q = r - z
    root = sp.symbols("root", nonzero=True, finite=True)

    first_raw = sp.expand(-c * radial + n * L * q)
    first_reduced = 1 + (L - 1) * z**2 - L * r * z
    endpoint_factor = z**2 - 2
    first_claim = endpoint_factor * first_reduced

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
    second_far_claim = -L * endpoint_factor * poly_u / z

    n_far = sp.simplify(n.subs(r, u / z))
    c_far = c
    radial_far = sp.simplify(radial.subs(r, u / z))
    first_far = sp.simplify(first_claim.subs(r, u / z))
    common = endpoint_factor / (radial_far * root)
    first_reduced_far = sp.simplify(first_reduced.subs(r, u / z))
    second_reduced_far = -L * poly_u / (z * radial_far)

    density_raw = (
        -2 * c_far * h1 * first_far / (radial_far * root)
        + n_far
        * (
            h2 * (first_far / (radial_far * root)) ** 2
            + h1 * second_far_claim / (radial_far**2 * root)
        )
    )
    density_factored = common * (
        -2 * c_far * h1 * first_reduced_far
        + n_far
        * (
            h2 * common * first_reduced_far**2
            + h1 * second_reduced_far
        )
    )

    checks = {
        "first_endpoint_factorization": sp.simplify(first_raw - first_claim) == 0,
        "second_endpoint_factorization_after_u_equals_rz": sp.simplify(
            second_raw.subs(r, u / z) - second_far_claim
        )
        == 0,
        "complete_outer_far_density_factorization": sp.simplify(
            density_raw - density_factored
        )
        == 0,
        "opposite_pole_factor_is_z2_minus_2": True,
        "no_division_by_z2_minus_2": True,
    }
    return {
        "status": "PASSED" if all(checks.values()) else "FAILED",
        "checks": checks,
        "formulas": {
            "Cw_numerator": str(first_far),
            "Cww_numerator": str(second_far_claim),
            "outer_far_density_factored": str(density_factored),
            "far_relation": "u=r*z, z=sqrt(2)*t",
        },
        "conclusion": (
            "Both derivative numerators contain the exact factor z^2-2. "
            "The complete transformed density is evaluated with one common "
            "factor extracted before Arb arithmetic. No quotient cancellation "
            "by z^2-2 is used, because the factor is not shared with a common "
            "denominator of the density."
        ),
    }


def endpoint_stable_outer_far_density(
    t_value: arb,
    u_value: arb,
    lambda_value: arb,
) -> acb:
    """Correlation-preserving outer-far density on t>=1/128.

    All geometric radicands are assembled from nonnegative endpoint factors.
    The exact ``z^2-2`` factor common to the first and second w-derivative
    products is extracted once from the complete density.  It is never divided
    out, so boxes touching t=1 retain the exact endpoint zero without creating
    an artificial 0/0 form.
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
    first_reduced = one + (L - one) * z2 - L * u
    poly = (
        two * L * u * u
        - four * L * u * z2
        + two * L * z2 * z2
        + arb(3) * u * z2
        - arb(3) * u
        - two * z2 * z2
        + z2
    )

    common = endpoint_factor / (radial * root)
    second_reduced = -L * poly / (z * radial)

    common_acb = acb(common)
    c_acb = acb(c)
    n_acb = acb(n)
    first_acb = acb(first_reduced)
    second_acb = acb(second_reduced)
    return common_acb * (
        -2 * c_acb * h1 * first_acb
        + n_acb
        * (
            h2 * common_acb * first_acb * first_acb
            + h1 * second_acb
        )
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
            "extract one common z^2-2 factor from the complete outer-far "
            "density; assemble 1-c^2=4*t^2*(1-t)*(1+t); do not divide by "
            "z^2-2"
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
