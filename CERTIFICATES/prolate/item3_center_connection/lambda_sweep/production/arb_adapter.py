#!/usr/bin/env python3
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any


class ProductionAdapterError(RuntimeError):
    pass


def _exact_arb_to_fraction(value: Any) -> Fraction:
    mantissa, exponent = value.man_exp()
    m = int(mantissa)
    e = int(exponent)
    return Fraction(m << e, 1) if e >= 0 else Fraction(m, 1 << (-e))


def _fraction_to_arb(value: Fraction, arb_type: Any) -> Any:
    return arb_type(str(value.numerator)) / arb_type(str(value.denominator))


def _interval_to_arb(interval: tuple[Fraction, Fraction], arb_type: Any) -> Any:
    lo, hi = interval
    if lo > hi:
        raise ProductionAdapterError("interval lower endpoint exceeds upper endpoint")
    return _fraction_to_arb(lo, arb_type).union(_fraction_to_arb(hi, arb_type))


class ProductionArbAdapter:
    adapter_id = "ITEM3_SWEEP_ARB_F_OVER_R_V1"

    def __init__(
        self,
        *,
        checkout_root: Path,
        kernel_source_path: str,
        kernel_source_sha256: str,
        tol: str = "1e-8",
        integration_depth: int = 12,
        integration_limit: int = 200000,
    ) -> None:
        from flint import arb, ctx
        from item3_sweep.provenance import PinnedSourceLoader, SourcePin

        self._arb = arb
        self._ctx = ctx
        self._tol = tol
        self._integration_depth = integration_depth
        self._integration_limit = integration_limit
        self._kernel, self.kernel_identity = PinnedSourceLoader(checkout_root).load_module(
            "item3_sweep_pinned_prolate_kernel",
            SourcePin(kernel_source_path, kernel_source_sha256),
        )
        if not callable(getattr(self._kernel, "F_arb", None)):
            raise ProductionAdapterError("pinned kernel lacks F_arb")
        if not callable(getattr(self._kernel, "dFdr_arb", None)):
            raise ProductionAdapterError("pinned kernel lacks dFdr_arb")

    def _canonical_interval(self, value: Any):
        from item3_sweep.adapter import CanonicalInterval

        try:
            lo = _exact_arb_to_fraction(value.lower())
            hi = _exact_arb_to_fraction(value.upper())
        except Exception:
            return CanonicalInterval(Fraction(0), Fraction(0), False)
        return CanonicalInterval(lo, hi, True)

    def _input_balls(
        self,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ) -> tuple[Any, Any]:
        if r[0] <= 0 or r[0] > r[1]:
            raise ProductionAdapterError("production adapter requires 0 < r_lo <= r_hi")
        if lambda_box[0] > lambda_box[1]:
            raise ProductionAdapterError("lambda interval order violation")
        self._ctx.dps = dps
        return _interval_to_arb(r, self._arb), _interval_to_arb(lambda_box, self._arb)

    def _f(self, r_ball: Any, lambda_ball: Any) -> Any:
        return self._kernel.F_arb(
            r_ball,
            lambda_ball,
            tol=self._tol,
            depth=self._integration_depth,
            limit=self._integration_limit,
        )

    def _fr(self, r_ball: Any, lambda_ball: Any) -> Any:
        return self._kernel.dFdr_arb(
            r_ball,
            lambda_ball,
            tol=self._tol,
            depth=self._integration_depth,
            limit=self._integration_limit,
        )

    def evaluate_g(
        self,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ):
        try:
            r_ball, lambda_ball = self._input_balls(r=r, lambda_box=lambda_box, dps=dps)
            return self._canonical_interval(self._f(r_ball, lambda_ball) / r_ball)
        except ProductionAdapterError:
            raise
        except Exception:
            from item3_sweep.adapter import CanonicalInterval
            return CanonicalInterval(Fraction(0), Fraction(0), False)

    def evaluate_gr(
        self,
        *,
        r: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ):
        try:
            r_ball, lambda_ball = self._input_balls(r=r, lambda_box=lambda_box, dps=dps)
            f_ball = self._f(r_ball, lambda_ball)
            fr_ball = self._fr(r_ball, lambda_ball)
            value = fr_ball / r_ball - f_ball / (r_ball * r_ball)
            return self._canonical_interval(value)
        except ProductionAdapterError:
            raise
        except Exception:
            from item3_sweep.adapter import CanonicalInterval
            return CanonicalInterval(Fraction(0), Fraction(0), False)
