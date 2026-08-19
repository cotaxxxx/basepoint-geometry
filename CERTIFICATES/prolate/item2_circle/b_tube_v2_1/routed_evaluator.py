#!/usr/bin/env python3
"""Exact-domain routed F/F_r evaluator for B-TUBE v2.1."""
from __future__ import annotations

from fractions import Fraction
import importlib
from pathlib import Path
import sys
from typing import Any

from calibration_context import *
from calibration_config import _expected_routed_contract
from calibration_security import _assert_repo_regular_file


def selector_for_r_interval(domain: DyadicInterval) -> str:
    if domain.lo < D_ZERO or D_ONE < domain.hi:
        raise CalibrationError("routed evaluator: r domain outside [0,1]")
    if domain.hi <= ROUTED_SELECTOR:
        return ROUTED_INTERIOR_ROUTE_ID
    if ROUTED_SELECTOR < domain.lo:
        return ROUTED_BOUNDARY_ROUTE_ID
    return ROUTED_STRADDLE_ROUTE_ID


def exact_straddle_children(domain: DyadicInterval) -> tuple[DyadicInterval, DyadicInterval]:
    if selector_for_r_interval(domain) != ROUTED_STRADDLE_ROUTE_ID:
        raise CalibrationError("routed evaluator: non-straddle domain")
    return (
        DyadicInterval(domain.lo, ROUTED_SELECTOR),
        DyadicInterval(ROUTED_SELECTOR, domain.hi),
    )


def routed_bundle_pins() -> dict[str, Any]:
    return {
        "boundary_files_sha256": dict(sorted(ROUTED_BOUNDARY_FILE_SHA256.items())),
        "boundary_config_sha256": ROUTED_BOUNDARY_CONFIG_SHA256,
        "boundary_source_head": ROUTED_BOUNDARY_SOURCE_HEAD,
        "contract": _expected_routed_contract(),
        "design_commit": ROUTED_DESIGN_COMMIT,
        "interior_kernel_sha256": KERNEL_SHA256,
    }


def _dyadic_arb(value: Dyadic, arb_type):
    return arb_type(value.m) / arb_type(1 << value.e)


def _dyadic_interval_arb(value: DyadicInterval, arb_type):
    return _dyadic_arb(value.lo, arb_type).union(_dyadic_arb(value.hi, arb_type))


def _model_interval_to_dyadic(model: Any, value: Any, where: str) -> DyadicInterval:
    lo, hi = model.interval_fractions(value, where)
    try:
        return DyadicInterval(Dyadic.from_fraction(lo), Dyadic.from_fraction(hi))
    except SchemaError as exc:
        raise CalibrationError(f"routed evaluator: non-dyadic B-LOCAL enclosure at {where}") from exc


def _trace_genesis() -> str:
    return sha256_hex((ROUTED_CONTRACT_ID + "\0TRACE_V1").encode("ascii"))


def _module_origin(module: Any) -> Path:
    value = getattr(module, "__file__", None)
    if value is None:
        raise CalibrationError("routed evaluator: dependency module has no origin")
    return Path(value).resolve(strict=True)


def verify_boundary_dependency_bytes(root: Path = ROUTED_BOUNDARY_DIR) -> dict[str, str]:
    if root.is_symlink():
        raise CalibrationError("routed evaluator: boundary dependency directory is symlink")
    resolved = root.resolve(strict=True)
    expected_names = set(ROUTED_BOUNDARY_FILE_SHA256) | {"config.blocal-v2.2-run.json"}
    actual_names = {path.name for path in resolved.iterdir() if path.is_file()}
    if actual_names != expected_names:
        raise CalibrationError("routed evaluator: boundary dependency file set mismatch")
    observed: dict[str, str] = {}
    for name, expected in sorted(ROUTED_BOUNDARY_FILE_SHA256.items()):
        path = _assert_repo_regular_file(resolved / name, REPO_ROOT)
        digest = sha256_hex(path.read_bytes())
        if digest != expected:
            raise CalibrationError(f"routed evaluator: boundary dependency SHA mismatch: {name}")
        observed[name] = digest
    config_path = _assert_repo_regular_file(resolved / "config.blocal-v2.2-run.json", REPO_ROOT)
    config_digest = sha256_hex(config_path.read_bytes())
    if config_digest != ROUTED_BOUNDARY_CONFIG_SHA256:
        raise CalibrationError("routed evaluator: B-LOCAL config SHA mismatch")
    observed["config.blocal-v2.2-run.json"] = config_digest
    return observed


def _load_boundary_modules():
    verify_boundary_dependency_bytes()
    dep_text = ROUTED_BOUNDARY_DIR.resolve(strict=True).as_posix()
    if dep_text not in sys.path:
        sys.path.insert(0, dep_text)
    names = (
        "blocal_phase4_model",
        "blocal_v22_policy",
        "blocal_v22_model",
        "blocal_arb_adapter",
        "blocal_v22_symbolic_audit",
        "blocal_v22_boundary",
    )
    modules: dict[str, Any] = {}
    for name in names:
        module = importlib.import_module(name)
        expected_path = (ROUTED_BOUNDARY_DIR / f"{name}.py").resolve(strict=True)
        if _module_origin(module) != expected_path:
            raise CalibrationError(f"routed evaluator: imported dependency origin mismatch: {name}")
        expected_sha = ROUTED_BOUNDARY_FILE_SHA256[f"{name}.py"]
        if sha256_hex(expected_path.read_bytes()) != expected_sha:
            raise CalibrationError(f"routed evaluator: post-import dependency SHA mismatch: {name}")
        modules[name] = module
    return modules


def _validate_boundary_config(modules: dict[str, Any]) -> dict[str, Any]:
    model = modules["blocal_v22_model"]
    raw = ROUTED_BOUNDARY_CONFIG_PATH.read_bytes()
    if sha256_hex(raw) != ROUTED_BOUNDARY_CONFIG_SHA256:
        raise CalibrationError("routed evaluator: frozen B-LOCAL config changed")
    config = model.parse_canonical_json(raw)
    model.validate_config(config)
    source_pins = config["implementation"]["sources_sha256"]
    checks = {
        "blocal_v22_boundary.py": source_pins["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"],
        "blocal_v22_model.py": source_pins["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_model.py"],
        "blocal_v22_policy.py": source_pins["CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_policy.py"],
        "blocal_v22_symbolic_audit.py": config["symbolic_audit"]["source_sha256"],
        "blocal_arb_adapter.py": config["adapter"]["source_sha256"],
        "blocal_phase4_model.py": config["base_v21"]["model_sha256"],
    }
    if checks != ROUTED_BOUNDARY_FILE_SHA256:
        raise CalibrationError("routed evaluator: B-LOCAL config/source pin mismatch")
    if config["kernel"]["sha256"] != KERNEL_SHA256:
        raise CalibrationError("routed evaluator: B-LOCAL kernel provenance mismatch")
    if config["route_policies"]["F_ROUTE"]["max_evaluations"] != ROUTED_BOUNDARY_ROUTE_CALL_CAP:
        raise CalibrationError("routed evaluator: F route call cap mismatch")
    if config["route_policies"]["K_ROUTE"]["max_evaluations"] != ROUTED_BOUNDARY_ROUTE_CALL_CAP:
        raise CalibrationError("routed evaluator: derivative route call cap mismatch")
    policy = modules["blocal_v22_policy"]
    if (
        policy.F_ROUTE_ID != ROUTED_F_ROUTE_ID
        or policy.K_ROUTE_ID != ROUTED_HU_ROUTE_ID
        or policy.NEGATION_RULE_ID != ROUTED_NEGATION_RULE_ID
    ):
        raise CalibrationError("routed evaluator: boundary route ID mismatch")
    audit = modules["blocal_v22_symbolic_audit"].run_audit()
    if (
        audit.get("exact_algebra") is not True
        or audit.get("F_route_exact") is not True
        or audit.get("J_equals_rho_K") is not True
        or audit.get("numeric_substitution_used_as_proof") is not False
    ):
        raise CalibrationError("routed evaluator: boundary symbolic audit failed")
    return config


class RoutedEvaluator:
    """Facade preserving the F_arb/dFdr_arb API with exact pre-call routing."""

    FORMULA_STATE = "FILLED"

    def __init__(self, interior_kernel: Any, arb_type: Any, config: dict[str, Any]):
        if config.get("routed_evaluator_contract") != _expected_routed_contract():
            raise CalibrationError("routed evaluator: active contract mismatch")
        self.interior_kernel = interior_kernel
        self.arb_type = arb_type
        self.config = config
        self.boundary_budget = config["boundary_route_evaluation_budget"]
        self.boundary_evaluation_count = 0
        self.phase = "UNSET"
        self.trace: list[dict[str, Any]] = []
        self.trace_tip = _trace_genesis()
        self.modules = _load_boundary_modules()
        self.boundary_config = _validate_boundary_config(self.modules)
        from flint import acb, ctx, fmpq  # type: ignore[import-not-found]
        self.acb_type = acb
        self.fmpq_type = fmpq
        self.ctx = ctx
        helper = self._with_boundary_precision(
            lambda: self.modules["blocal_v22_boundary"].validate_helper_lemmas(
                self.arb_type, self.fmpq_type, self.boundary_config
            )
        )
        if not helper or any(row.get("status") != "PASS" for row in helper):
            raise CalibrationError("routed evaluator: boundary helper validation failed")

    def set_phase(self, phase: str) -> None:
        if not isinstance(phase, str) or not phase:
            raise CalibrationError("routed evaluator: nonempty phase required")
        self.phase = phase

    def _remaining_boundary_budget(self) -> int:
        remaining = self.boundary_budget - self.boundary_evaluation_count
        if remaining <= 0:
            raise CalibrationError("routed evaluator: boundary evaluation budget exhausted")
        return remaining

    def _charge_boundary(self, count: int) -> None:
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise CalibrationError("routed evaluator: invalid boundary evaluation count")
        self.boundary_evaluation_count += count
        if self.boundary_evaluation_count > self.boundary_budget:
            raise CalibrationError("routed evaluator: boundary evaluation budget exceeded")

    def _boundary_call_cap(self) -> int:
        return min(ROUTED_BOUNDARY_ROUTE_CALL_CAP, self._remaining_boundary_budget())

    def _with_boundary_precision(self, function):
        old_prec = self.ctx.prec
        self.ctx.prec = self.boundary_config["precision"]["bits"]
        try:
            return function()
        finally:
            self.ctx.prec = old_prec

    def _boundary(self, quantity: str, r_iv: DyadicInterval, lam_iv: DyadicInterval):
        route = self.modules["blocal_v22_boundary"]
        model = self.modules["blocal_v22_model"]
        adapter = self.modules["blocal_arb_adapter"]
        r0, r1 = r_iv.lo.as_fraction(), r_iv.hi.as_fraction()
        l0, l1 = lam_iv.lo.as_fraction(), lam_iv.hi.as_fraction()
        cap = self._boundary_call_cap()

        def compute():
            if quantity == "F":
                return route.enclose_f(
                    self.interior_kernel,
                    adapter,
                    self.acb_type,
                    self.arb_type,
                    self.fmpq_type,
                    self.boundary_config,
                    r0,
                    r1,
                    l0,
                    l1,
                    required_sign=None,
                    evaluation_cap=cap,
                )
            u0, u1 = Fraction(1) - r1, Fraction(1) - r0
            s0, s1 = l0 - model.LAMBDA_PLUS, l1 - model.LAMBDA_PLUS
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
                required_sign=None,
                evaluation_cap=cap,
            )

        try:
            normalized, proof = self._with_boundary_precision(compute)
        except route.EnclosureFailure as exc:
            self._charge_boundary(exc.evaluations)
            raise CalibrationError(
                f"routed evaluator: boundary route incomplete: {exc.reason}"
            ) from exc
        used = proof.get("evaluation_count")
        self._charge_boundary(used)
        interval = _model_interval_to_dyadic(model, normalized, f"boundary.{quantity}")
        if quantity == "F_r":
            interval = -interval
        value = _dyadic_interval_arb(interval, self.arb_type)
        return value, interval, {
            "boundary_proof_id": proof.get("proof_id"),
            "boundary_route_evaluation_count": used,
            "boundary_route_id": proof.get("route_id"),
            "source_quantity": "F" if quantity == "F" else "H_U",
            "transform": None if quantity == "F" else ROUTED_NEGATION_RULE_ID,
        }, used

    def _interior(self, quantity: str, r_iv: DyadicInterval, lam_iv: DyadicInterval,
                  tol: str, depth: int, limit: int):
        r_ball = _dyadic_interval_arb(r_iv, self.arb_type)
        lam_ball = _dyadic_interval_arb(lam_iv, self.arb_type)
        function = self.interior_kernel.F_arb if quantity == "F" else self.interior_kernel.dFdr_arb
        value = function(r_ball, lam_ball, tol=tol, depth=depth, limit=limit)
        interval = arb_ball_to_exact_interval(value)
        return value, interval, {
            "interior_kernel_sha256": KERNEL_SHA256,
            "source_quantity": quantity,
        }, 0

    def _evaluate(self, quantity: str, r_iv: DyadicInterval, lam_iv: DyadicInterval,
                  tol: str, depth: int, limit: int, *, force_route: str | None = None,
                  record: bool = True):
        if quantity not in {"F", "F_r"}:
            raise CalibrationError("routed evaluator: unsupported quantity")
        natural_route = selector_for_r_interval(r_iv)
        selected = natural_route if force_route is None else force_route
        if force_route is not None and force_route not in {
            ROUTED_INTERIOR_ROUTE_ID, ROUTED_BOUNDARY_ROUTE_ID
        }:
            raise CalibrationError("routed evaluator: invalid forced backend route")
        children: list[dict[str, Any]] = []
        if selected == ROUTED_INTERIOR_ROUTE_ID:
            value, interval, detail, used = self._interior(
                quantity, r_iv, lam_iv, tol, depth, limit
            )
        elif selected == ROUTED_BOUNDARY_ROUTE_ID:
            value, interval, detail, used = self._boundary(quantity, r_iv, lam_iv)
        elif selected == ROUTED_STRADDLE_ROUTE_ID and force_route is None:
            left, right = exact_straddle_children(r_iv)
            lv, li, ld, lu = self._interior(quantity, left, lam_iv, tol, depth, limit)
            del lv
            rv, ri, rd, ru = self._boundary(quantity, right, lam_iv)
            del rv
            interval = DyadicInterval.hull([li.lo, li.hi, ri.lo, ri.hi])
            value = _dyadic_interval_arb(interval, self.arb_type)
            used = lu + ru
            detail = {"split_rule": ROUTED_STRADDLE_ROUTE_ID}
            children = [
                {
                    "enclosure": li.to_json(),
                    "r_interval": left.to_json(),
                    "route_id": ROUTED_INTERIOR_ROUTE_ID,
                    "detail": ld,
                },
                {
                    "enclosure": ri.to_json(),
                    "r_interval": right.to_json(),
                    "route_id": ROUTED_BOUNDARY_ROUTE_ID,
                    "detail": rd,
                },
            ]
        else:
            raise CalibrationError("routed evaluator: invalid forced route")
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

    def _append_trace(self, evidence: dict[str, Any]) -> None:
        body = dict(evidence)
        body["previous_trace_sha256"] = self.trace_tip
        body["schema"] = ROUTED_TRACE_SCHEMA
        body["sequence"] = len(self.trace)
        digest = sha256_hex(canonical_json_bytes(body))
        body["trace_record_sha256"] = digest
        self.trace.append(body)
        self.trace_tip = digest

    def _arb_inputs(self, r: Any, lam: Any) -> tuple[DyadicInterval, DyadicInterval]:
        try:
            r_iv = arb_ball_to_exact_interval(r)
            lam_iv = arb_ball_to_exact_interval(lam)
        except (SchemaError, ValueError, TypeError, OverflowError) as exc:
            raise CalibrationError("routed evaluator: nonfinite/noncanonical input ball") from exc
        return r_iv, lam_iv

    def F_arb(self, r: Any, lam: Any, tol: str = "1e-8", depth: int = 12,
              limit: int = 200000):
        r_iv, lam_iv = self._arb_inputs(r, lam)
        value, _, _ = self._evaluate("F", r_iv, lam_iv, tol, depth, limit)
        return value

    def dFdr_arb(self, r: Any, lam: Any, tol: str = "1e-8", depth: int = 12,
                  limit: int = 200000):
        r_iv, lam_iv = self._arb_inputs(r, lam)
        value, _, _ = self._evaluate("F_r", r_iv, lam_iv, tol, depth, limit)
        return value

    def evaluate_forced_arb(self, quantity: str, r: Any, lam: Any, route_id: str,
                            *, tol: str, depth: int, limit: int):
        r_iv, lam_iv = self._arb_inputs(r, lam)
        return self._evaluate(
            quantity, r_iv, lam_iv, tol, depth, limit,
            force_route=route_id, record=False,
        )


def trace_genesis() -> str:
    return _trace_genesis()


__all__ = [name for name in globals() if not name.startswith("__")]
