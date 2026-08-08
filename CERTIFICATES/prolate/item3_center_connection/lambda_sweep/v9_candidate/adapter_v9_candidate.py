#!/usr/bin/env python3
"""Source-bound rigorous adapter candidate for Item 3 sweep v9.

STATUS: VALIDATION CANDIDATE / NOT PRODUCTION APPROVED.

The adapter:
- source-pins and independently loads the guarded five-output kernel;
- converts exact rational/dyadic coordinate intervals to Arb balls;
- computes the frozen dual quotient associations;
- converts Arb results to exact binary-rational endpoint intervals;
- constructs the exact two-variable mean-value enclosure and split scores.

It contains no runner/checker state machine, GitHub API calls, checkpoint logic, or
certification verdict promotion.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any, Literal

from flint import arb, ctx


ADAPTER_ID = "ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V1"
EXPECTED_KERNEL_ID = "ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2"


class AdapterContractError(RuntimeError):
    pass


class QuotientAssociationDisjoint(AdapterContractError):
    pass


@dataclass(frozen=True)
class SourceIdentity:
    resolved_path: str
    pre_import_sha256: str
    post_import_sha256: str
    module_origin: str
    kernel_id: str


@dataclass(frozen=True)
class CanonicalInterval:
    lo: Fraction
    hi: Fraction
    finite: bool = True

    def __post_init__(self) -> None:
        if self.finite and self.lo > self.hi:
            raise AdapterContractError("canonical interval lower endpoint exceeds upper endpoint")

    @classmethod
    def nonfinite(cls) -> "CanonicalInterval":
        return cls(Fraction(0), Fraction(0), False)

    @classmethod
    def point(cls, value: Fraction) -> "CanonicalInterval":
        return cls(value, value, True)

    def __add__(self, other: "CanonicalInterval") -> "CanonicalInterval":
        if not self.finite or not other.finite:
            return CanonicalInterval.nonfinite()
        return CanonicalInterval(self.lo + other.lo, self.hi + other.hi)

    def __mul__(self, other: "CanonicalInterval") -> "CanonicalInterval":
        if not self.finite or not other.finite:
            return CanonicalInterval.nonfinite()
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return CanonicalInterval(min(products), max(products))

    def strictly_negative(self) -> bool:
        return self.finite and self.hi < 0

    def absmax(self) -> Fraction:
        if not self.finite:
            raise AdapterContractError("absmax undefined for nonfinite interval")
        return max(abs(self.lo), abs(self.hi))


AssociationClass = Literal["INTERSECTION", "DIRECT_ONLY", "FACTORED_ONLY", "NONFINITE"]


@dataclass(frozen=True)
class QuotientEvidence:
    expression_id: str
    direct: CanonicalInterval
    factored: CanonicalInterval
    association_class: AssociationClass
    final: CanonicalInterval


@dataclass(frozen=True)
class BoxDerivativeEvidence:
    g_rr: QuotientEvidence
    g_rlambda: QuotientEvidence
    kernel_calls: int


@dataclass(frozen=True)
class MeanValueEvidence:
    r0: Fraction
    lambda0: Fraction
    g_r_center: QuotientEvidence
    g_rr_box: QuotientEvidence
    g_rlambda_box: QuotientEvidence
    r_offset: CanonicalInterval
    lambda_offset: CanonicalInterval
    r_correction: CanonicalInterval
    lambda_correction: CanonicalInterval
    mean_value: CanonicalInterval
    strict_negative: bool
    r_score: Fraction | None
    lambda_score: Fraction | None
    kernel_calls: int


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _resolve_contained(checkout_root: Path, repo_relative_path: str) -> Path:
    root = checkout_root.resolve(strict=True)
    try:
        path = (root / repo_relative_path).resolve(strict=True)
    except FileNotFoundError as exc:
        raise AdapterContractError("kernel source path does not exist") from exc
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise AdapterContractError("kernel source path escapes checkout root") from exc
    if not path.is_file():
        raise AdapterContractError("kernel source path is not a regular file")
    return path


def load_pinned_kernel(
    *,
    checkout_root: Path,
    repo_relative_path: str,
    expected_sha256: str,
    module_name: str,
) -> tuple[ModuleType, SourceIdentity]:
    if len(expected_sha256) != 64 or any(ch not in "0123456789abcdef" for ch in expected_sha256):
        raise AdapterContractError("expected kernel SHA-256 must be 64 lowercase hex")
    path = _resolve_contained(checkout_root, repo_relative_path)
    before = sha256_file(path)
    if before != expected_sha256:
        raise AdapterContractError("pre-import kernel source hash mismatch")

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AdapterContractError("unable to construct kernel import spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    origin_text = module.__spec__.origin if module.__spec__ is not None else None
    if not origin_text:
        raise AdapterContractError("imported kernel has no module origin")
    origin = Path(origin_text).resolve(strict=True)
    if origin != path:
        raise AdapterContractError("imported kernel origin mismatch")

    after = sha256_file(path)
    if after != before:
        raise AdapterContractError("kernel source changed during import")

    kernel_id = getattr(module, "KERNEL_ID", None)
    if kernel_id != EXPECTED_KERNEL_ID:
        raise AdapterContractError("kernel ID mismatch")
    for name in ("F_arb", "F_r_arb", "F_lambda_arb", "F_rr_arb", "F_rlambda_arb"):
        if not callable(getattr(module, name, None)):
            raise AdapterContractError(f"kernel lacks required interface {name}")

    return module, SourceIdentity(
        resolved_path=str(path),
        pre_import_sha256=before,
        post_import_sha256=after,
        module_origin=str(origin),
        kernel_id=kernel_id,
    )


def _exact_arb_to_fraction(value: Any) -> Fraction:
    mantissa, exponent = value.man_exp()
    m = int(mantissa)
    e = int(exponent)
    return Fraction(m << e, 1) if e >= 0 else Fraction(m, 1 << (-e))


def _canonical_interval(value: arb) -> CanonicalInterval:
    if not value.is_finite():
        return CanonicalInterval.nonfinite()
    try:
        lo = _exact_arb_to_fraction(value.lower())
        hi = _exact_arb_to_fraction(value.upper())
    except Exception:
        return CanonicalInterval.nonfinite()
    return CanonicalInterval(lo, hi, True)


def _fraction_to_arb(value: Fraction) -> arb:
    return arb(str(value.numerator)) / arb(str(value.denominator))


def _interval_to_arb(interval: tuple[Fraction, Fraction]) -> arb:
    lo, hi = interval
    if lo > hi:
        raise AdapterContractError("input interval lower endpoint exceeds upper endpoint")
    return _fraction_to_arb(lo).union(_fraction_to_arb(hi))


def canonical_midpoint(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise AdapterContractError("interval lower endpoint exceeds upper endpoint")
    return (lo + hi) / 2


def centered_offset(interval: tuple[Fraction, Fraction], center: Fraction) -> CanonicalInterval:
    lo, hi = interval
    if lo > center or center > hi:
        raise AdapterContractError("center lies outside interval")
    return CanonicalInterval(lo - center, hi - center)


def radius(interval: tuple[Fraction, Fraction]) -> Fraction:
    lo, hi = interval
    if lo > hi:
        raise AdapterContractError("interval lower endpoint exceeds upper endpoint")
    return (hi - lo) / 2


def _combine_arb_associations(
    *,
    expression_id: str,
    direct_value: arb,
    factored_value: arb,
) -> QuotientEvidence:
    direct = _canonical_interval(direct_value)
    factored = _canonical_interval(factored_value)

    if direct.finite and factored.finite:
        if not direct_value.overlaps(factored_value):
            raise QuotientAssociationDisjoint(expression_id)
        try:
            final_value = direct_value.intersection(factored_value)
        except ValueError as exc:
            raise QuotientAssociationDisjoint(expression_id) from exc
        return QuotientEvidence(
            expression_id,
            direct,
            factored,
            "INTERSECTION",
            _canonical_interval(final_value),
        )
    if direct.finite:
        return QuotientEvidence(expression_id, direct, factored, "DIRECT_ONLY", direct)
    if factored.finite:
        return QuotientEvidence(expression_id, direct, factored, "FACTORED_ONLY", factored)
    return QuotientEvidence(
        expression_id,
        direct,
        factored,
        "NONFINITE",
        CanonicalInterval.nonfinite(),
    )


def _quotient_gr(F: arb, F_r: arb, R: arb) -> QuotientEvidence:
    R2 = R * R
    direct = (F_r / R) - (F / R2)
    factored = ((F_r * R) - F) / R2
    return _combine_arb_associations(
        expression_id="ITEM3_V9_GR_DUAL_ASSOC_V1",
        direct_value=direct,
        factored_value=factored,
    )


def _quotient_grr(F: arb, F_r: arb, F_rr: arb, R: arb) -> QuotientEvidence:
    R2 = R * R
    R3 = R2 * R
    direct = ((F_rr / R) - ((2 * F_r) / R2)) + ((2 * F) / R3)
    factored = (((F_rr * R2) - ((2 * F_r) * R)) + (2 * F)) / R3
    return _combine_arb_associations(
        expression_id="ITEM3_V9_GRR_DUAL_ASSOC_V1",
        direct_value=direct,
        factored_value=factored,
    )


def _quotient_grlambda(
    F_lambda: arb,
    F_rlambda: arb,
    R: arb,
) -> QuotientEvidence:
    R2 = R * R
    direct = (F_rlambda / R) - (F_lambda / R2)
    factored = ((F_rlambda * R) - F_lambda) / R2
    return _combine_arb_associations(
        expression_id="ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1",
        direct_value=direct,
        factored_value=factored,
    )


class V9MeanValueAdapter:
    adapter_id = ADAPTER_ID

    def __init__(
        self,
        *,
        checkout_root: Path,
        kernel_source_path: str,
        kernel_source_sha256: str,
        tol: str = "1e-8",
        integration_depth: int = 12,
        integration_limit: int = 200000,
        module_name: str = "item3_v9_pinned_candidate_kernel",
    ) -> None:
        self._kernel, self.kernel_identity = load_pinned_kernel(
            checkout_root=checkout_root,
            repo_relative_path=kernel_source_path,
            expected_sha256=kernel_source_sha256,
            module_name=module_name,
        )
        self._tol = tol
        self._integration_depth = integration_depth
        self._integration_limit = integration_limit
        self.kernel_call_counts = {
            "F": 0,
            "F_r": 0,
            "F_lambda": 0,
            "F_rr": 0,
            "F_rlambda": 0,
        }

    def _call(self, name: str, r_ball: arb, lambda_ball: arb) -> arb:
        attr = {
            "F": "F_arb",
            "F_r": "F_r_arb",
            "F_lambda": "F_lambda_arb",
            "F_rr": "F_rr_arb",
            "F_rlambda": "F_rlambda_arb",
        }[name]
        self.kernel_call_counts[name] += 1
        value = getattr(self._kernel, attr)(
            r_ball,
            lambda_ball,
            tol=self._tol,
            depth=self._integration_depth,
            limit=self._integration_limit,
        )
        if not isinstance(value, arb):
            raise AdapterContractError(f"kernel {attr} returned non-arb value")
        return value

    def _validate_coordinates(
        self,
        r_cell: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
    ) -> None:
        r_lo, r_hi = r_cell
        l_lo, l_hi = lambda_box
        if not (Fraction(0) < r_lo <= r_hi < Fraction(1)):
            raise AdapterContractError("adapter requires 0 < r_lo <= r_hi < 1")
        if not (Fraction(1) <= l_lo <= l_hi):
            raise AdapterContractError("adapter requires 1 <= lambda_lo <= lambda_hi")

    def evaluate_mean_value(
        self,
        *,
        r_cell: tuple[Fraction, Fraction],
        lambda_box: tuple[Fraction, Fraction],
        dps: int,
    ) -> MeanValueEvidence:
        self._validate_coordinates(r_cell, lambda_box)
        if not isinstance(dps, int) or isinstance(dps, bool) or dps <= 0:
            raise AdapterContractError("dps must be a positive integer")

        r0 = canonical_midpoint(r_cell)
        lambda0 = canonical_midpoint(lambda_box)
        old_dps = ctx.dps
        calls_before = sum(self.kernel_call_counts.values())
        try:
            ctx.dps = dps
            r0_ball = _fraction_to_arb(r0)
            l0_ball = _fraction_to_arb(lambda0)
            r_ball = _interval_to_arb(r_cell)
            lambda_ball = _interval_to_arb(lambda_box)

            F0 = self._call("F", r0_ball, l0_ball)
            Fr0 = self._call("F_r", r0_ball, l0_ball)
            g_r_center = _quotient_gr(F0, Fr0, r0_ball)

            F = self._call("F", r_ball, lambda_ball)
            Fr = self._call("F_r", r_ball, lambda_ball)
            Fl = self._call("F_lambda", r_ball, lambda_ball)
            Frr = self._call("F_rr", r_ball, lambda_ball)
            Frl = self._call("F_rlambda", r_ball, lambda_ball)
            g_rr = _quotient_grr(F, Fr, Frr, r_ball)
            g_rlambda = _quotient_grlambda(Fl, Frl, r_ball)
        finally:
            ctx.dps = old_dps

        r_offset = centered_offset(r_cell, r0)
        lambda_offset = centered_offset(lambda_box, lambda0)
        r_correction = g_rr.final * r_offset
        lambda_correction = g_rlambda.final * lambda_offset
        mean_value = g_r_center.final + r_correction + lambda_correction

        r_score = None if not g_rr.final.finite else radius(r_cell) * g_rr.final.absmax()
        lambda_score = (
            None
            if not g_rlambda.final.finite
            else radius(lambda_box) * g_rlambda.final.absmax()
        )
        calls_after = sum(self.kernel_call_counts.values())
        return MeanValueEvidence(
            r0=r0,
            lambda0=lambda0,
            g_r_center=g_r_center,
            g_rr_box=g_rr,
            g_rlambda_box=g_rlambda,
            r_offset=r_offset,
            lambda_offset=lambda_offset,
            r_correction=r_correction,
            lambda_correction=lambda_correction,
            mean_value=mean_value,
            strict_negative=mean_value.strictly_negative(),
            r_score=r_score,
            lambda_score=lambda_score,
            kernel_calls=calls_after - calls_before,
        )
