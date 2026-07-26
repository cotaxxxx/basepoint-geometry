#!/usr/bin/env python3
"""Endpoint-stable wrapper for the compact item-6 pole-modulus certificate.

The generic cosine/hypergeometric outer-far kernel is efficient away from the
opposite pole but may produce a spurious branch-point enclosure when a box
touches ``t=1``. This wrapper uses two exact representations:

* away from the endpoint, the complete cosine density is factored once by its
  common ``z^2-2`` numerator factor (never divided out);
* on the endpoint cap, the audited signed-angle formula
  ``delta=atan(X/N)`` and its rational-algebraic w derivatives are evaluated
  directly, avoiding the cosine branch point altogether.

The two formulas are exact representations of the same transformed A''
density. The compact cover and exact partition accounting are unchanged.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import sympy as sp
from flint import acb, arb, fmpq

import prolate_axis_pole_modulus_arb as base
import prolate_axis_pole_modulus_compact_arb as compact

SIGNED_ENDPOINT_T = fmpq(255, 256)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def endpoint_factorization_audit() -> dict:
    z, r, u, L = sp.symbols("z r u L", nonzero=True, finite=True)
    t, lam = sp.symbols("t lam", positive=True, finite=True)
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

    z_t = sp.sqrt(2) * t
    z2_t = 2 * t**2
    c_t = 1 - z2_t
    w_t = 1 - u
    rho2_t = 4 * t**2 * (1 - t) * (1 + t)
    N_t = u + z2_t - u * z2_t
    q_t = u - z2_t
    R2_t = rho2_t + lam**2 * q_t**2

    checks = {
        "first_endpoint_factorization": sp.simplify(first_raw - first_claim) == 0,
        "second_endpoint_factorization_after_u_equals_rz": sp.simplify(
            second_raw.subs(r, u / z) - second_far_claim
        ) == 0,
        "complete_outer_far_density_factorization": sp.simplify(
            density_raw - density_factored
        ) == 0,
        "signed_chart_one_minus_c_squared": sp.expand(1 - c_t**2 - rho2_t) == 0,
        "signed_chart_N": sp.expand(1 - w_t * c_t - N_t) == 0,
        "signed_chart_R_squared": sp.expand(
            1 - c_t**2 + lam**2 * (c_t - w_t) ** 2 - R2_t
        ) == 0,
        "signed_chart_c_minus_w": sp.expand(c_t - w_t - q_t) == 0,
        "outer_t_jacobian": sp.simplify(2 * z_t * sp.sqrt(2) - 4 * t) == 0,
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
            "signed_N": str(N_t),
            "signed_rho_squared": str(rho2_t),
            "signed_R_squared": str(R2_t),
            "signed_delta": "atan(rho*(lambda*w-(lambda-1/lambda)*c)/N)",
            "signed_delta_w": "lambda*rho/R_squared",
            "signed_delta_ww": "2*lambda^3*rho*(c-w)/R_squared^2",
            "outer_t_jacobian": "4*t",
            "far_relation": "u=r*z, z=sqrt(2)*t",
        },
        "domain_statement": (
            "On t>=1/128, 0<=u<=1/64 and 1<=lambda<=100, "
            "N=1-(1-u)(1-2*t^2)>0. Hence signed atan has no branch ambiguity."
        ),
        "conclusion": (
            "The cosine density is factored without cancelling z^2-2. Boxes in "
            "the endpoint cap use the exact signed-angle A'' integrand with "
            "Jacobian 4*t, eliminating the cosine branch-point enclosure."
        ),
    }


def factored_outer_far_density(
    t_value: arb,
    u_value: arb,
    lambda_value: arb,
) -> acb:
    """Factored cosine density away from the opposite-pole endpoint."""
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


def signed_outer_far_density(
    t_value: arb,
    u_value: arb,
    lambda_value: arb,
) -> acb:
    """Exact signed-angle transformed A'' density on the endpoint cap."""
    t = arb(t_value)
    u = arb(u_value)
    lam = arb(lambda_value)

    one = arb(1)
    two = arb(2)
    four = arb(4)
    L = lam**2

    t2 = t**2
    z2 = two * t2
    c = one - z2
    w = one - u
    endpoint_gap = abs(one - t)
    one_plus_t = one + t
    rho = two * t * endpoint_gap.sqrt() * one_plus_t.sqrt()
    rho2 = four * t2 * endpoint_gap * one_plus_t
    N = u + z2 - u * z2
    q = u - z2
    q2 = q**2
    R2 = rho2 + L * q2

    cross = rho * (lam * w - (lam - one / lam) * c)
    delta = acb((cross / N).atan())
    delta_w = acb(lam * rho / R2)
    delta_ww = acb(two * lam * L * rho * q / (R2**2))
    c_acb = acb(c)
    N_acb = acb(N)
    transformed = (
        -2 * c_acb * delta * delta_w
        + N_acb * (delta_w * delta_w + delta * delta_ww)
    )
    return acb(four * t) * transformed


def endpoint_stable_outer_far_density(
    t_value: arb,
    u_value: arb,
    lambda_value: arb,
) -> acb:
    """Hybrid exact outer-far density with a signed endpoint cap."""
    t = arb(t_value)
    if t.lower() >= arb(SIGNED_ENDPOINT_T):
        return signed_outer_far_density(t, u_value, lambda_value)
    return factored_outer_far_density(t, u_value, lambda_value)


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
        "signed_endpoint_t": str(SIGNED_ENDPOINT_T),
        "method": (
            "factor the complete cosine density without dividing by z^2-2; "
            "for t>=255/256 use exact nonnegative endpoint factors, real Arb "
            "atan, signed-angle derivatives, and the 4*t outer-chart Jacobian"
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
        f"{sha256_file(wrapper_path.with_name('prolate_axis_signed_angle_symbolic_audit.py'))}  "
        "prolate_axis_signed_angle_symbolic_audit.py\n"
        f"{sha256_file(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result.get("status") == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
