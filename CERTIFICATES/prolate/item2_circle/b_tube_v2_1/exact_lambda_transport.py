#!/usr/bin/env python3
"""Exact-rational lambda transport for the routed B-TUBE v2.1 evaluator."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from calibration_context import *
from calibration_security import _assert_repo_regular_file
from exact_lambda_contract import (
    EXACT_LAMBDA_ADDENDUM_PATH,
    EXACT_LAMBDA_ADDENDUM_SHA256,
    EXACT_LAMBDA_ROUNDING_BITS,
    EXACT_LAMBDA_TRANSPORT_PATH,
    EXACT_LAMBDA_TRANSPORT_RULE_ID,
    EXACT_LAMBDA_TRANSPORT_SHA256,
)
from routed_evaluator import (
    RoutedEvaluator,
    _dyadic_arb,
    _dyadic_interval_arb,
    _model_interval_to_dyadic,
    exact_straddle_children,
    routed_bundle_pins,
    selector_for_r_interval,
)

EXACT_LAMBDA_TRANSPORT_DETAIL_KEY = "exact_lambda_transport"
EXACT_LAMBDA_REFINEMENT_EVAL_CAP = 24000
EXACT_LAMBDA_F_NONZERO_PREDICATE_ID = "R7_F_NONZERO_V1"
EXACT_LAMBDA_HU_POS_PREDICATE_ID = "R7_HU_POS_V1"


def _rational_interval_json(lo: Fraction, hi: Fraction) -> dict[str, Any]:
    if not isinstance(lo, Fraction) or not isinstance(hi, Fraction) or hi < lo:
        raise CalibrationError("exact lambda transport: invalid rational interval")
    return {
        "lo": Rational.from_fraction(lo).to_json(),
        "hi": Rational.from_fraction(hi).to_json(),
    }


def _fraction_arb(value: Fraction, arb_type):
    return arb_type(value.numerator) / arb_type(value.denominator)


def _fraction_interval_arb(lo: Fraction, hi: Fraction, arb_type):
    if not isinstance(lo, Fraction) or not isinstance(hi, Fraction) or hi < lo:
        raise CalibrationError("exact lambda transport: reversed/nonexact lambda interval")
    return _fraction_arb(lo, arb_type).union(_fraction_arb(hi, arb_type))


def _exact_lambda_domain(lo: Fraction, hi: Fraction) -> None:
    if not isinstance(lo, Fraction) or not isinstance(hi, Fraction) or hi < lo:
        raise CalibrationError("exact lambda transport: canonical Fraction interval required")
    if lo < BLOCAL_LAMBDA_START.as_fraction() or CG_LAMBDA.as_fraction() < hi:
        raise CalibrationError("exact lambda transport: lambda outside result-bearing domain")


def _transport_evidence(
    model: Any, lo: Fraction, hi: Fraction
) -> tuple[DyadicInterval, dict[str, Any]]:
    _exact_lambda_domain(lo, hi)
    if model.NORMALIZATION_BITS != EXACT_LAMBDA_ROUNDING_BITS:
        raise CalibrationError("exact lambda transport: frozen rounding-bit mismatch")
    lambda_plus = model.LAMBDA_PLUS
    s_lo = lo - lambda_plus
    s_hi = hi - lambda_plus
    rounded_lo = model.floor_dyadic(s_lo, EXACT_LAMBDA_ROUNDING_BITS)
    rounded_hi = model.ceil_dyadic(s_hi, EXACT_LAMBDA_ROUNDING_BITS)
    try:
        s_iv = DyadicInterval(
            Dyadic.from_fraction(rounded_lo),
            Dyadic.from_fraction(rounded_hi),
        )
    except SchemaError as exc:
        raise CalibrationError(
            "exact lambda transport: frozen rounding was not dyadic"
        ) from exc
    lower_enlargement = s_lo - rounded_lo
    upper_enlargement = rounded_hi - s_hi
    unit = Fraction(1, 1 << EXACT_LAMBDA_ROUNDING_BITS)
    if not (
        Fraction(0) <= lower_enlargement < unit
        and Fraction(0) <= upper_enlargement < unit
    ):
        raise CalibrationError("exact lambda transport: outward-rounding bound violated")
    if not (
        lambda_plus + s_iv.lo.as_fraction() <= lo
        and hi <= lambda_plus + s_iv.hi.as_fraction()
    ):
        raise CalibrationError("exact lambda transport: lambda containment failed")
    return s_iv, {
        "exact_lambda_transport_sha256": EXACT_LAMBDA_TRANSPORT_SHA256,
        "lambda_exact_interval": _rational_interval_json(lo, hi),
        "lambda_plus": Rational.from_fraction(lambda_plus).to_json(),
        "lower_rounding_enlargement": Rational.from_fraction(
            lower_enlargement
        ).to_json(),
        "rounding_bits": EXACT_LAMBDA_ROUNDING_BITS,
        "rounding_rule_id": EXACT_LAMBDA_TRANSPORT_RULE_ID,
        "s_exact_interval": _rational_interval_json(s_lo, s_hi),
        "s_outward_dyadic_interval": s_iv.to_json(),
        "upper_rounding_enlargement": Rational.from_fraction(
            upper_enlargement
        ).to_json(),
    }


def _install_runtime_lambda_native_f_guard(route: Any) -> None:
    def _forbidden_lambda_native_route(*args, **kwargs):
        raise CalibrationError(
            "exact lambda transport: lambda-native B-LOCAL F route forbidden"
        )
    setattr(route, "enclose_" + "f", _forbidden_lambda_native_route)


class ExactLambdaRoutedEvaluator(RoutedEvaluator):
    """Routed evaluator requiring exact rational lambda provenance."""

    def __init__(self, interior_kernel: Any, arb_type: Any, config: dict[str, Any]):
        source_path = _assert_repo_regular_file(
            BTUBE_ROOT / EXACT_LAMBDA_TRANSPORT_PATH, REPO_ROOT
        )
        if sha256_hex(source_path.read_bytes()) != EXACT_LAMBDA_TRANSPORT_SHA256:
            raise CalibrationError("exact lambda transport: source pin mismatch")
        addendum_path = _assert_repo_regular_file(
            BTUBE_ROOT / EXACT_LAMBDA_ADDENDUM_PATH, REPO_ROOT
        )
        if (
            EXACT_LAMBDA_ADDENDUM_SHA256 != ROUTED_EXACT_LAMBDA_ADDENDUM_SHA256
            or sha256_hex(addendum_path.read_bytes()) != EXACT_LAMBDA_ADDENDUM_SHA256
        ):
            raise CalibrationError("exact lambda transport: addendum pin mismatch")
        super().__init__(interior_kernel, arb_type, config)
        if EXACT_LAMBDA_REFINEMENT_EVAL_CAP != ROUTED_BOUNDARY_ROUTE_CALL_CAP:
            raise CalibrationError(
                "exact lambda transport: refinement evaluation cap mismatch"
            )
        _install_runtime_lambda_native_f_guard(
            self.modules["blocal_v22_boundary"]
        )

    def _boundary_exact(
        self,
        quantity: str,
        r_iv: DyadicInterval,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        *,
        f_nonzero: bool = False,
    ):
        route = self.modules["blocal_v22_boundary"]
        model = self.modules["blocal_v22_model"]
        adapter = self.modules["blocal_arb_adapter"]
        r0, r1 = r_iv.lo.as_fraction(), r_iv.hi.as_fraction()
        u0, u1 = Fraction(1) - r1, Fraction(1) - r0
        s_iv, transport = _transport_evidence(model, lambda_lo, lambda_hi)
        s0, s1 = s_iv.lo.as_fraction(), s_iv.hi.as_fraction()
        cap = min(EXACT_LAMBDA_REFINEMENT_EVAL_CAP, self._boundary_call_cap())

        def f_nonzero_accept(enclosure):
            lo, hi = model.interval_fractions(
                enclosure, "exact lambda transport F NONZERO refinement"
            )
            return hi < 0 or 0 < lo

        def compute():
            if quantity == "F":
                return route.enclose_route(
                    "F",
                    self.interior_kernel,
                    adapter,
                    self.acb_type,
                    self.arb_type,
                    self.fmpq_type,
                    self.boundary_config,
                    u0,
                    u1,
                    s0,
                    s1,
                    required_sign=None,
                    accept=f_nonzero_accept if f_nonzero else None,
                    evaluation_cap=cap,
                )
            return route.enclose_hu(
                self.interior_kernel,
                adapter,
                self.acb_type,
                self.arb_type,
                self.fmpq_type,
                self.boundary_config,
                u0,
                u1,
                s0,
                s1,
                required_sign="POS",
                evaluation_cap=cap,
            )

        try:
            normalized, proof = self._with_boundary_precision(compute)
        except route.EnclosureFailure as exc:
            self._charge_boundary(exc.evaluations)
            raise CalibrationError(
                f"exact lambda transport: boundary route incomplete: {exc.reason}"
            ) from exc
        used = proof.get("evaluation_count")
        self._charge_boundary(used)
        expected_s_json = model.interval_json(s0, s1)
        if proof.get("s_interval") != expected_s_json:
            raise CalibrationError(
                "exact lambda transport: frozen proof s interval mismatch"
            )
        interval = _model_interval_to_dyadic(
            model, normalized, f"boundary.{quantity}"
        )
        if quantity == "F_r":
            interval = -interval
        value = _dyadic_interval_arb(interval, self.arb_type)
        return value, interval, {
            "boundary_proof_id": proof.get("proof_id"),
            "boundary_route_evaluation_count": used,
            "boundary_route_id": proof.get("route_id"),
            EXACT_LAMBDA_TRANSPORT_DETAIL_KEY: transport,
            "refinement_evaluation_cap": EXACT_LAMBDA_REFINEMENT_EVAL_CAP,
            "refinement_predicate_id": (
                EXACT_LAMBDA_F_NONZERO_PREDICATE_ID
                if quantity == "F" and f_nonzero
                else EXACT_LAMBDA_HU_POS_PREDICATE_ID
                if quantity == "F_r"
                else None
            ),
            "source_quantity": "F" if quantity == "F" else "H_U",
            "transform": None if quantity == "F" else ROUTED_NEGATION_RULE_ID,
        }, used

    def _interior_exact(
        self,
        quantity: str,
        r_iv: DyadicInterval,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        tol: str,
        depth: int,
        limit: int,
    ):
        _exact_lambda_domain(lambda_lo, lambda_hi)
        r_ball = _dyadic_interval_arb(r_iv, self.arb_type)
        lam_ball = _fraction_interval_arb(lambda_lo, lambda_hi, self.arb_type)
        function = (
            self.interior_kernel.F_arb
            if quantity == "F"
            else self.interior_kernel.dFdr_arb
        )
        value = function(r_ball, lam_ball, tol=tol, depth=depth, limit=limit)
        interval = arb_ball_to_exact_interval(value)
        return value, interval, {
            "interior_kernel_sha256": KERNEL_SHA256,
            "source_quantity": quantity,
        }, 0

    def _evaluate_exact(
        self,
        quantity: str,
        r_iv: DyadicInterval,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        tol: str,
        depth: int,
        limit: int,
        *,
        force_route: str | None = None,
        record: bool = True,
        f_nonzero: bool = False,
    ):
        if quantity not in {"F", "F_r"}:
            raise CalibrationError("exact lambda transport: unsupported quantity")
        if f_nonzero and quantity != "F":
            raise CalibrationError(
                "exact lambda transport: NONZERO refinement is F-only"
            )
        _exact_lambda_domain(lambda_lo, lambda_hi)
        lam_ball = _fraction_interval_arb(lambda_lo, lambda_hi, self.arb_type)
        lam_iv = arb_ball_to_exact_interval(lam_ball)
        natural_route = selector_for_r_interval(r_iv)
        selected = natural_route if force_route is None else force_route
        if force_route is not None and force_route not in {
            ROUTED_INTERIOR_ROUTE_ID,
            ROUTED_BOUNDARY_ROUTE_ID,
        }:
            raise CalibrationError(
                "exact lambda transport: invalid forced backend route"
            )
        children: list[dict[str, Any]] = []
        if selected == ROUTED_INTERIOR_ROUTE_ID:
            value, interval, detail, used = self._interior_exact(
                quantity, r_iv, lambda_lo, lambda_hi, tol, depth, limit
            )
        elif selected == ROUTED_BOUNDARY_ROUTE_ID:
            value, interval, detail, used = self._boundary_exact(
                quantity, r_iv, lambda_lo, lambda_hi, f_nonzero=f_nonzero
            )
        elif selected == ROUTED_STRADDLE_ROUTE_ID and force_route is None:
            left, right = exact_straddle_children(r_iv)
            _, li, ld, lu = self._interior_exact(
                quantity, left, lambda_lo, lambda_hi, tol, depth, limit
            )
            _, ri, rd, ru = self._boundary_exact(
                quantity, right, lambda_lo, lambda_hi, f_nonzero=f_nonzero
            )
            interval = DyadicInterval.hull([li.lo, li.hi, ri.lo, ri.hi])
            value = _dyadic_interval_arb(interval, self.arb_type)
            used = lu + ru
            detail = {"split_rule": ROUTED_STRADDLE_ROUTE_ID}
            children = [
                {
                    "detail": ld,
                    "enclosure": li.to_json(),
                    "r_interval": left.to_json(),
                    "route_id": ROUTED_INTERIOR_ROUTE_ID,
                },
                {
                    "detail": rd,
                    "enclosure": ri.to_json(),
                    "r_interval": right.to_json(),
                    "route_id": ROUTED_BOUNDARY_ROUTE_ID,
                },
            ]
        else:
            raise CalibrationError("exact lambda transport: invalid forced route")
        if f_nonzero and not (interval.hi < D_ZERO or D_ZERO < interval.lo):
            raise CalibrationError(
                "exact lambda transport: F NONZERO refinement unresolved"
            )
        evidence = {
            "boundary_route_evaluation_count_delta": used,
            "boundary_route_evaluation_count_total": self.boundary_evaluation_count,
            "children": children,
            "contract_id": ROUTED_CONTRACT_ID,
            "detail": detail,
            "enclosure": interval.to_json(),
            "lambda_interval": lam_iv.to_json(),
            "phase": self.phase,
            "pins": routed_bundle_pins(),
            "post_failure_fallback": False,
            "quantity": quantity,
            "r_interval": r_iv.to_json(),
            "route_id": selected,
            "selector_r": ROUTED_SELECTOR.to_json(),
        }
        if record:
            self._append_trace(evidence)
        return value, interval, evidence

    def _r_input(self, r: Any) -> DyadicInterval:
        try:
            return arb_ball_to_exact_interval(r)
        except (SchemaError, ValueError, TypeError, OverflowError) as exc:
            raise CalibrationError("exact lambda transport: invalid r ball") from exc

    def F_exact_arb(
        self,
        r: Any,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        tol: str = "1e-8",
        depth: int = 12,
        limit: int = 200000,
        *,
        require_nonzero: bool = False,
    ):
        value, _, _ = self._evaluate_exact(
            "F",
            self._r_input(r),
            lambda_lo,
            lambda_hi,
            tol,
            depth,
            limit,
            f_nonzero=require_nonzero,
        )
        return value

    def dFdr_exact_arb(
        self,
        r: Any,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        tol: str = "1e-8",
        depth: int = 12,
        limit: int = 200000,
    ):
        value, _, _ = self._evaluate_exact(
            "F_r", self._r_input(r), lambda_lo, lambda_hi, tol, depth, limit
        )
        return value

    def evaluate_forced_exact_arb(
        self,
        quantity: str,
        r: Any,
        lambda_lo: Fraction,
        lambda_hi: Fraction,
        route_id: str,
        *,
        tol: str,
        depth: int,
        limit: int,
    ):
        return self._evaluate_exact(
            quantity,
            self._r_input(r),
            lambda_lo,
            lambda_hi,
            tol,
            depth,
            limit,
            force_route=route_id,
            record=False,
        )

    def F_arb(self, *args, **kwargs):
        raise CalibrationError(
            "exact lambda transport: result-bearing F requires exact rational lambda API"
        )

    def dFdr_arb(self, *args, **kwargs):
        raise CalibrationError(
            "exact lambda transport: result-bearing F_r requires exact rational lambda API"
        )

    def evaluate_forced_arb(self, *args, **kwargs):
        raise CalibrationError(
            "exact lambda transport: forced result-bearing evaluation requires exact lambda API"
        )


def _raw_lambda_ball(lambda_lo: Fraction, lambda_hi: Fraction, arb_type):
    return _fraction_interval_arb(lambda_lo, lambda_hi, arb_type)


def _kernel_F(
    kernel, arb_type, r_arg, lambda_lo: Fraction, lambda_hi: Fraction,
    *, tol, depth, limit, nonzero: bool = False
):
    if isinstance(kernel, ExactLambdaRoutedEvaluator):
        return kernel.F_exact_arb(
            r_arg,
            lambda_lo,
            lambda_hi,
            tol=tol,
            depth=depth,
            limit=limit,
            require_nonzero=nonzero,
        )
    value = kernel.F_arb(
        r_arg,
        _raw_lambda_ball(lambda_lo, lambda_hi, arb_type),
        tol=tol,
        depth=depth,
        limit=limit,
    )
    if nonzero:
        interval = arb_ball_to_exact_interval(value)
        if not (interval.hi < D_ZERO or D_ZERO < interval.lo):
            raise CalibrationError(
                "exact lambda transport: F NONZERO refinement unresolved"
            )
    return value


def _kernel_Fr(
    kernel, arb_type, r_arg, lambda_lo: Fraction, lambda_hi: Fraction,
    *, tol, depth, limit
):
    if isinstance(kernel, ExactLambdaRoutedEvaluator):
        return kernel.dFdr_exact_arb(
            r_arg, lambda_lo, lambda_hi, tol=tol, depth=depth, limit=limit
        )
    return kernel.dFdr_arb(
        r_arg,
        _raw_lambda_ball(lambda_lo, lambda_hi, arb_type),
        tol=tol,
        depth=depth,
        limit=limit,
    )


def exact_newton_predictor(
    kernel,
    arb_type,
    lam: Fraction,
    seed: Dyadic,
    *,
    iterations: int,
    tol: str,
    depth: int,
    limit: int,
) -> Dyadic:
    from calibration_numeric import _nearest_dyadic
    current = seed
    for _ in range(iterations):
        point = _dyadic_arb(current, arb_type)
        residual = arb_ball_to_exact_interval(
            _kernel_F(
                kernel, arb_type, point, lam, lam,
                tol=tol, depth=depth, limit=limit, nonzero=True
            )
        )
        slope = arb_ball_to_exact_interval(
            _kernel_Fr(
                kernel, arb_type, point, lam, lam,
                tol=tol, depth=depth, limit=limit
            )
        )
        slope_mid = slope.midpoint()
        if slope_mid == D_ZERO:
            break
        updated = (
            current.as_fraction()
            - residual.midpoint().as_fraction() / slope_mid.as_fraction()
        )
        current = _nearest_dyadic(updated)
    return current


def exact_evaluate_krawczyk(
    *, kernel, arb_type, domain, lam_lo, lam_hi, tol, depth, limit
):
    from calibration_numeric import _dyadic_box, _nearest_dyadic
    domain_box = _dyadic_box(domain, arb_type)
    midpoint = domain.midpoint()
    midpoint_lam = (lam_lo + lam_hi) / 2
    residual = arb_ball_to_exact_interval(
        _kernel_F(
            kernel, arb_type, _dyadic_arb(midpoint, arb_type),
            lam_lo, lam_hi, tol=tol, depth=depth, limit=limit
        )
    )
    slope = arb_ball_to_exact_interval(
        _kernel_Fr(
            kernel, arb_type, domain_box,
            lam_lo, lam_hi, tol=tol, depth=depth, limit=limit
        )
    )
    center_slope = arb_ball_to_exact_interval(
        _kernel_Fr(
            kernel, arb_type, _dyadic_arb(midpoint, arb_type),
            midpoint_lam, midpoint_lam,
            tol=tol, depth=depth, limit=limit
        )
    )
    slope_mid = center_slope.midpoint()
    preconditioner = D_ZERO
    if slope_mid != D_ZERO:
        preconditioner = _nearest_dyadic(
            Fraction(1, 1) / slope_mid.as_fraction(), bits=96
        )
    image = DyadicInterval.point(midpoint)
    left_margin = D_ZERO
    right_margin = D_ZERO
    reason = None
    passed = False
    if preconditioner == D_ZERO:
        reason = "preconditioner_zero"
    else:
        image = krawczyk_image(
            m=midpoint,
            residual=residual,
            slope=slope,
            preconditioner=preconditioner,
            domain=domain,
        )
        left_margin = image.lo - domain.lo
        right_margin = domain.hi - image.hi
        if not domain.strictly_contains(image):
            reason = "krawczyk_not_strict"
        elif not slope.hi < D_ZERO:
            reason = "slope_not_strictly_negative"
        else:
            passed = True
    return {
        "image": image,
        "left_margin": left_margin,
        "passed": passed,
        "preconditioner": preconditioner,
        "reason": reason,
        "residual": residual,
        "right_margin": right_margin,
        "slope": slope,
    }


def exact_evaluate_point(*, kernel, arb_type, domain, lam, tol, depth, limit):
    result = exact_evaluate_krawczyk(
        kernel=kernel,
        arb_type=arb_type,
        domain=domain,
        lam_lo=lam,
        lam_hi=lam,
        tol=tol,
        depth=depth,
        limit=limit,
    )
    return {
        "failure_reason": result["reason"],
        "krawczyk_image": result["image"].to_json(),
        "left_margin": result["left_margin"].to_json(),
        "passed": result["passed"],
        "preconditioner": result["preconditioner"].to_json(),
        "residual": result["residual"].to_json(),
        "right_margin": result["right_margin"].to_json(),
        "slope": result["slope"].to_json(),
    }


def install_exact_lambda_call_sites() -> dict[str, str]:
    import a0b_start_anchor as anchor_module
    import calibration_candidate as candidate_module
    import calibration_numeric as numeric_module

    targets = (
        (
            numeric_module,
            "_newton_predictor",
            "calibration_numeric",
            exact_newton_predictor,
        ),
        (
            candidate_module,
            "_newton_predictor",
            "calibration_numeric",
            exact_newton_predictor,
        ),
        (
            candidate_module,
            "_evaluate_krawczyk",
            "calibration_candidate",
            exact_evaluate_krawczyk,
        ),
        (
            anchor_module,
            "_newton_predictor",
            "calibration_numeric",
            exact_newton_predictor,
        ),
        (
            anchor_module,
            "_evaluate_point",
            "a0b_start_anchor",
            exact_evaluate_point,
        ),
    )
    for module, name, original_module, replacement in targets:
        current = getattr(module, name, None)
        if current is replacement:
            continue
        if current is None or getattr(current, "__module__", None) != original_module:
            raise CalibrationError(
                f"exact lambda transport: unexpected patch target "
                f"{module.__name__}.{name}"
            )
        setattr(module, name, replacement)
    return {
        "a0b_start_anchor._evaluate_point": exact_evaluate_point.__name__,
        "a0b_start_anchor._newton_predictor": exact_newton_predictor.__name__,
        "calibration_candidate._evaluate_krawczyk": exact_evaluate_krawczyk.__name__,
        "calibration_candidate._newton_predictor": exact_newton_predictor.__name__,
        "calibration_numeric._newton_predictor": exact_newton_predictor.__name__,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
