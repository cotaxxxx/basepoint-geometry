#!/usr/bin/env python3
"""Focused read-only Krawczyk gap diagnostic for B-TUBE v2.1."""
from __future__ import annotations

from fractions import Fraction
from time import perf_counter

from affine_geometry import krawczyk_image
from calibration_config import load_config
from calibration_context import D_ONE, D_ZERO, Dyadic, DyadicInterval
from calibration_numeric import _nearest_dyadic
from calibration_security import load_production_kernel
from exact_lambda_transport import (
    EXACT_LAMBDA_REFINEMENT_EVAL_CAP,
    ExactLambdaRoutedEvaluator,
    _transport_evidence,
)
from routed_evaluator import _model_interval_to_dyadic
from flint import arb, ctx


def main() -> int:
    config, _ = load_config()
    kernel, _ = load_production_kernel()
    ctx.dps = config["dps"]
    ev = ExactLambdaRoutedEvaluator(kernel, arb, config)

    route = ev.modules["blocal_v22_boundary"]
    model = ev.modules["blocal_v22_model"]
    adapter = ev.modules["blocal_arb_adapter"]

    lam = Fraction(3307749, 1600000)
    midpoint = Dyadic(16379, 14)
    rho = Dyadic(5, 15)
    domain = DyadicInterval(Dyadic(32753, 15), Dyadic(32763, 15))
    point = DyadicInterval.point(midpoint)
    s_iv, _ = _transport_evidence(model, lam, lam)
    s0, s1 = s_iv.lo.as_fraction(), s_iv.hi.as_fraction()

    print("BTUBE_KRAWCZYK_GAP_DIAGNOSTIC_V1")
    print(f"LAMBDA_START={lam}")
    print(f"MIDPOINT={midpoint.as_fraction()}")
    print(f"RHO={rho.as_fraction()}")
    print(f"DOMAIN_LO={domain.lo.as_fraction()}")
    print(f"DOMAIN_HI={domain.hi.as_fraction()}")
    print(f"CALL_CAP={EXACT_LAMBDA_REFINEMENT_EVAL_CAP}")

    def measure(label: str, quantity: str, r_iv: DyadicInterval,
                target: Fraction, require_pos: bool) -> dict:
        r0 = r_iv.lo.as_fraction()
        r1 = r_iv.hi.as_fraction()
        u0, u1 = Fraction(1) - r1, Fraction(1) - r0

        def accept(enclosure) -> bool:
            lo, hi = model.interval_fractions(enclosure, f"gap diagnostic {label}")
            if require_pos and lo <= 0:
                return False
            return hi - lo <= target

        def compute():
            return route.enclose_route(
                quantity,
                ev.interior_kernel,
                adapter,
                ev.acb_type,
                ev.arb_type,
                ev.fmpq_type,
                ev.boundary_config,
                u0,
                u1,
                s0,
                s1,
                required_sign=None,
                accept=accept,
                evaluation_cap=EXACT_LAMBDA_REFINEMENT_EVAL_CAP,
            )

        t0 = perf_counter()
        try:
            normalized, proof = ev._with_boundary_precision(compute)
        except route.EnclosureFailure as exc:
            elapsed = perf_counter() - t0
            print(
                f"MEASURE label={label} status=CAP target={target} "
                f"evaluations={exc.evaluations} elapsed={elapsed:.6f} "
                f"reason={exc.reason}"
            )
            return {
                "status": "CAP",
                "evaluations": exc.evaluations,
                "elapsed": elapsed,
                "interval": None,
            }

        elapsed = perf_counter() - t0
        interval = _model_interval_to_dyadic(
            model, normalized, f"gap diagnostic {label}"
        )
        lo = interval.lo.as_fraction()
        hi = interval.hi.as_fraction()
        used = proof["evaluation_count"]
        print(
            f"MEASURE label={label} status=PASS target={target} "
            f"evaluations={used} elapsed={elapsed:.6f} "
            f"lo={lo} hi={hi} mid={(lo + hi) / 2} width={hi - lo}"
        )
        return {
            "status": "PASS",
            "evaluations": used,
            "elapsed": elapsed,
            "interval": interval,
        }

    f_results = {}
    for exp in (11, 12, 13):
        f_results[exp] = measure(
            f"F_2m{exp}", "F", point, Fraction(1, 1 << exp), False
        )

    hd_results = {}
    for label, target in (
        ("1", Fraction(1)),
        ("7_8", Fraction(7, 8)),
        ("3_4", Fraction(3, 4)),
        ("5_8", Fraction(5, 8)),
        ("1_2", Fraction(1, 2)),
    ):
        hd_results[label] = measure(
            f"HU_DOMAIN_{label}", "H_U", domain, target, True
        )

    hc_results = {}
    for label, target in (
        ("1", Fraction(1)),
        ("1_2", Fraction(1, 2)),
    ):
        hc_results[label] = measure(
            f"HU_CENTER_{label}", "H_U", point, target, True
        )

    passing = []
    for f_exp, frow in f_results.items():
        if frow["status"] != "PASS":
            continue
        residual = frow["interval"]
        assert residual is not None
        for hd_label, hdrow in hd_results.items():
            if hdrow["status"] != "PASS":
                continue
            hu_domain = hdrow["interval"]
            assert hu_domain is not None
            slope = -hu_domain
            for hc_label, hcrow in hc_results.items():
                if hcrow["status"] != "PASS":
                    continue
                hu_center = hcrow["interval"]
                assert hu_center is not None
                center_slope = -hu_center
                slope_mid = center_slope.midpoint()
                if slope_mid == D_ZERO:
                    print(
                        f"COMBO F=2^-{f_exp} HD={hd_label} HC={hc_label} "
                        "status=PRECONDITIONER_ZERO"
                    )
                    continue

                preconditioner = _nearest_dyadic(
                    Fraction(1, 1) / slope_mid.as_fraction(), bits=96
                )
                image = krawczyk_image(
                    m=midpoint,
                    residual=residual,
                    slope=slope,
                    preconditioner=preconditioner,
                    domain=domain,
                )
                left_margin = image.lo - domain.lo
                right_margin = domain.hi - image.hi
                passed = domain.strictly_contains(image) and slope.hi < D_ZERO

                multiplier = (
                    DyadicInterval.point(D_ONE)
                    - slope * DyadicInterval.point(preconditioner)
                )
                kappa = max(
                    abs(multiplier.lo.as_fraction()),
                    abs(multiplier.hi.as_fraction()),
                )
                residual_abs = max(
                    abs(residual.lo.as_fraction()),
                    abs(residual.hi.as_fraction()),
                )
                c_abs = abs(preconditioner.as_fraction())
                zero_residual_margin = (Fraction(1) - kappa) * rho.as_fraction()
                allowed_abs_residual = (
                    zero_residual_margin / c_abs if c_abs != 0 else Fraction(0)
                )
                eval_cost = (
                    frow["evaluations"]
                    + hdrow["evaluations"]
                    + hcrow["evaluations"]
                )
                elapsed_cost = (
                    frow["elapsed"] + hdrow["elapsed"] + hcrow["elapsed"]
                )
                print(
                    f"COMBO F=2^-{f_exp} HD={hd_label} HC={hc_label} "
                    f"passed={passed} eval_cost={eval_cost} "
                    f"elapsed_cost={elapsed_cost:.6f} kappa={kappa} "
                    f"residual_abs={residual_abs} "
                    f"allowed_abs_residual={allowed_abs_residual} "
                    f"left_margin={left_margin.as_fraction()} "
                    f"right_margin={right_margin.as_fraction()} "
                    f"preconditioner={preconditioner.as_fraction()}"
                )
                if passed:
                    passing.append(
                        (
                            eval_cost,
                            elapsed_cost,
                            f_exp,
                            hd_label,
                            hc_label,
                            kappa,
                            residual_abs,
                            allowed_abs_residual,
                            left_margin.as_fraction(),
                            right_margin.as_fraction(),
                        )
                    )

    if passing:
        best = min(
            passing,
            key=lambda row: (row[0], row[1], row[2], row[3], row[4]),
        )
        print(
            "BEST_PASS "
            f"eval_cost={best[0]} elapsed_cost={best[1]:.6f} "
            f"F=2^-{best[2]} HD={best[3]} HC={best[4]} "
            f"kappa={best[5]} residual_abs={best[6]} "
            f"allowed_abs_residual={best[7]} "
            f"left_margin={best[8]} right_margin={best[9]}"
        )
    else:
        print("BEST_PASS=NONE")

    print("DIAGNOSTIC_STATUS=COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
