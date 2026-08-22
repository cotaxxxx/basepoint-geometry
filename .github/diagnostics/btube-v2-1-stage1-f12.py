#!/usr/bin/env python3
"""Non-binding Stage-1 F=2^-12 budget diagnostic for B-TUBE v2.1."""
from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from time import perf_counter

from affine_geometry import krawczyk_image
from calibration_config import load_config
from calibration_context import D_ONE, D_ZERO, Dyadic, DyadicInterval
from calibration_numeric import _nearest_dyadic
from calibration_security import load_production_kernel
from exact_lambda_transport import ExactLambdaRoutedEvaluator, _transport_evidence
from routed_evaluator import _model_interval_to_dyadic
from flint import arb, ctx


DIAGNOSTIC_BUDGET = 50_000
DIAGNOSTIC_CHILD_CAP = 50_005
PRODUCTION_BUDGET = 24_000
PRODUCTION_CHILD_CAP = 24_000
F_TARGET = Fraction(1, 1 << 12)


def main() -> int:
    print("BTUBE_STAGE1_F12_DIAGNOSTIC_V1")
    print("EVIDENCE_CLASS=DIAGNOSTIC_NOT_BINDING")
    print("NOT_BINDING=TRUE")
    print(f"DIAGNOSTIC_BUDGET={DIAGNOSTIC_BUDGET}")
    print(f"DIAGNOSTIC_CHILD_CAP={DIAGNOSTIC_CHILD_CAP}")
    print(f"PRODUCTION_BUDGET={PRODUCTION_BUDGET}")
    print(f"PRODUCTION_CHILD_CAP={PRODUCTION_CHILD_CAP}")

    try:
        config, _ = load_config()
        kernel, _ = load_production_kernel()
        ctx.dps = config["dps"]
        ev = ExactLambdaRoutedEvaluator(kernel, arb, config)

        route = ev.modules["blocal_v22_boundary"]
        model = ev.modules["blocal_v22_model"]
        adapter = ev.modules["blocal_arb_adapter"]

        # Controls-only in-memory diagnostic override. No target byte is changed.
        boundary_config = deepcopy(ev.boundary_config)
        for policy_name in ("F_ROUTE", "K_ROUTE"):
            original = boundary_config["route_policies"][policy_name]["max_evaluations"]
            if original != PRODUCTION_BUDGET:
                raise RuntimeError(
                    f"unexpected production budget for {policy_name}: {original}"
                )
            boundary_config["route_policies"][policy_name]["max_evaluations"] = (
                DIAGNOSTIC_BUDGET
            )
            original_children = boundary_config["route_policies"][policy_name][
                "max_children"
            ]
            if original_children != PRODUCTION_CHILD_CAP:
                raise RuntimeError(
                    f"unexpected production child cap for {policy_name}: "
                    f"{original_children}"
                )
            boundary_config["route_policies"][policy_name]["max_children"] = (
                DIAGNOSTIC_CHILD_CAP
            )

        lam = Fraction(3307749, 1600000)
        midpoint = Dyadic(16379, 14)
        rho = Dyadic(5, 15)
        domain = DyadicInterval(Dyadic(32753, 15), Dyadic(32763, 15))
        point = DyadicInterval.point(midpoint)
        s_iv, _ = _transport_evidence(model, lam, lam)
        s0, s1 = s_iv.lo.as_fraction(), s_iv.hi.as_fraction()

        print(f"LAMBDA_START={lam}")
        print(f"MIDPOINT={midpoint.as_fraction()}")
        print(f"RHO={rho.as_fraction()}")
        print(f"DOMAIN_LO={domain.lo.as_fraction()}")
        print(f"DOMAIN_HI={domain.hi.as_fraction()}")
        print(f"F_TARGET={F_TARGET}")

        def measure(label: str, quantity: str, r_iv: DyadicInterval,
                    target: Fraction, require_pos: bool) -> dict:
            r0 = r_iv.lo.as_fraction()
            r1 = r_iv.hi.as_fraction()
            u0, u1 = Fraction(1) - r1, Fraction(1) - r0
            best = {"width": None, "lo": None, "hi": None}

            def accept(enclosure) -> bool:
                lo, hi = model.interval_fractions(
                    enclosure, f"stage1 diagnostic {label}"
                )
                width = hi - lo
                if best["width"] is None or width < best["width"]:
                    best.update(width=width, lo=lo, hi=hi)
                if require_pos and lo <= 0:
                    return False
                return width <= target

            def compute():
                return route.enclose_route(
                    quantity,
                    ev.interior_kernel,
                    adapter,
                    ev.acb_type,
                    ev.arb_type,
                    ev.fmpq_type,
                    boundary_config,
                    u0,
                    u1,
                    s0,
                    s1,
                    required_sign=None,
                    accept=accept,
                    evaluation_cap=DIAGNOSTIC_BUDGET,
                )

            t0 = perf_counter()
            try:
                normalized, proof = ev._with_boundary_precision(compute)
            except route.EnclosureFailure as exc:
                elapsed = perf_counter() - t0
                lo, hi, width = best["lo"], best["hi"], best["width"]
                mid = None if lo is None else (lo + hi) / 2
                print(
                    f"MEASURE label={label} status=CAP target={target} "
                    f"evaluations={exc.evaluations} elapsed={elapsed:.6f} "
                    f"best_lo={lo} best_hi={hi} best_mid={mid} "
                    f"best_width={width} reason={exc.reason}"
                )
                return {
                    "status": "CAP", "evaluations": exc.evaluations,
                    "elapsed": elapsed, "interval": None,
                }

            elapsed = perf_counter() - t0
            interval = _model_interval_to_dyadic(
                model, normalized, f"stage1 diagnostic {label}"
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
                "status": "PASS", "evaluations": used,
                "elapsed": elapsed, "interval": interval,
            }

        # Stage order: F=2^-12 first, then only the best known domain/center precision.
        frow = measure("F_2m12", "F", point, F_TARGET, False)
        if frow["status"] != "PASS":
            print("BEST_PASS=NONE")
            print("DIAGNOSTIC_VERDICT=NONE")
            return 3

        hdrow = measure("HU_DOMAIN_1_2", "H_U", domain, Fraction(1, 2), True)
        hcrow = measure("HU_CENTER_1_2", "H_U", point, Fraction(1, 2), True)
        if hdrow["status"] != "PASS" or hcrow["status"] != "PASS":
            print("BEST_PASS=NONE")
            print("DIAGNOSTIC_VERDICT=NONE")
            return 3

        residual = frow["interval"]
        hu_domain = hdrow["interval"]
        hu_center = hcrow["interval"]
        assert residual is not None and hu_domain is not None and hu_center is not None
        slope = -hu_domain
        center_slope = -hu_center
        slope_mid = center_slope.midpoint()
        if slope_mid == D_ZERO:
            raise RuntimeError("zero center slope preconditioner")

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
        multiplier = (
            DyadicInterval.point(D_ONE)
            - slope * DyadicInterval.point(preconditioner)
        )
        kappa = max(
            abs(multiplier.lo.as_fraction()),
            abs(multiplier.hi.as_fraction()),
        )
        residual_abs = max(
            abs(residual.lo.as_fraction()), abs(residual.hi.as_fraction())
        )
        c_abs = abs(preconditioner.as_fraction())
        allowed_abs_residual = (
            (Fraction(1) - kappa) * rho.as_fraction() / c_abs
        )
        residual_ratio = residual_abs / allowed_abs_residual
        left_margin = image.lo - domain.lo
        right_margin = domain.hi - image.hi
        passed = domain.strictly_contains(image) and slope.hi < D_ZERO
        eval_cost = (
            frow["evaluations"] + hdrow["evaluations"] + hcrow["evaluations"]
        )
        elapsed_cost = frow["elapsed"] + hdrow["elapsed"] + hcrow["elapsed"]

        print(
            "COMBO F=2^-12 HD=1_2 HC=1_2 "
            f"passed={passed} eval_cost={eval_cost} "
            f"elapsed_cost={elapsed_cost:.6f} kappa={kappa} "
            f"residual_abs={residual_abs} "
            f"allowed_abs_residual={allowed_abs_residual} "
            f"residual_ratio={residual_ratio} "
            f"left_margin={left_margin.as_fraction()} "
            f"right_margin={right_margin.as_fraction()} "
            f"preconditioner={preconditioner.as_fraction()}"
        )

        if passed:
            print("BEST_PASS F=2^-12 HD=1_2 HC=1_2")
            print("DIAGNOSTIC_VERDICT=PASS")
            return 0
        print("BEST_PASS=NONE")
        print("DIAGNOSTIC_VERDICT=NONE")
        return 3
    except Exception as exc:
        print(f"DIAGNOSTIC_ERROR={type(exc).__name__}:{exc}")
        print("DIAGNOSTIC_VERDICT=ERROR")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
