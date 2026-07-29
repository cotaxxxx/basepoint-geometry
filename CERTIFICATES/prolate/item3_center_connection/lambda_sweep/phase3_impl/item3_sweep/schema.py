from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable

from .canonical import (
    CanonicalDyadic,
    CanonicalRational,
    ContractReject,
    validate_id,
    validate_repo_relative_path,
    validate_sha256,
)
from .enums import CheckerFailureReason


REQUIRED_DEPENDENCIES = frozenset({"L-CONT", "L-DERIV", "L-ENCL", "L-SIGN", "L-IVT"})
DEPENDENCY_ENTRY_FIELDS = frozenset(
    {"lemma_id", "dependency_entry_sha256", "expected_allowlist_id"}
)

REQUIRED_CONFIG_FIELDS = frozenset(
    {
        "sweep_design_path",
        "sweep_design_sha256",
        "lambda_anchor",
        "lambda_target",
        "min_lambda_width_exp",
        "delta_overlap_min",
        "window_grid_exp",
        "window_min_width_exp",
        "w0_lo",
        "w0_hi",
        "global_eval_limit",
        "per_box_eval_limit",
        "max_lambda_depth",
        "max_r_cells_per_box",
        "dps",
        "checker_dps",
        "runner_source_path",
        "runner_source_sha256",
        "checker_source_path",
        "checker_source_sha256",
        "r_tile_algorithm_id",
        "r_tile_source_path",
        "r_tile_source_sha256",
        "kernel_source_path",
        "kernel_source_sha256",
        "adapter_id",
        "adapter_source_path",
        "adapter_sha256",
        "cg_pilot_run_id",
        "cg_pilot_receipt_path",
        "cg_pilot_receipt_sha256",
        "cg_pilot_source_sha256",
        "cg_pilot_kernel_source_sha256",
        "dependency_snapshot_path",
        "dependency_snapshot_sha256",
        "sweep_logical_dependencies",
        "lambda_coordinate_encoding_id",
        "r_coordinate_encoding_id",
        "enclosure_encoding_id",
    }
)

PATH_FIELDS = frozenset(field for field in REQUIRED_CONFIG_FIELDS if field.endswith("_path"))
SHA_FIELDS = frozenset(field for field in REQUIRED_CONFIG_FIELDS if field.endswith("_sha256"))
NONNEGATIVE_INT_FIELDS = frozenset(
    {"min_lambda_width_exp", "window_grid_exp", "window_min_width_exp", "max_lambda_depth"}
)
POSITIVE_INT_FIELDS = frozenset(
    {
        "global_eval_limit",
        "per_box_eval_limit",
        "max_r_cells_per_box",
        "dps",
        "checker_dps",
    }
)

CONSTANT_FIELDS = {
    "lambda_coordinate_encoding_id": "CANONICAL_REDUCED_RATIONAL_V1",
    "r_coordinate_encoding_id": "CANONICAL_DYADIC_V1",
    "enclosure_encoding_id": "CANONICAL_DYADIC_INTERVAL_V1",
    "r_tile_algorithm_id": "ADAPTIVE_R_BISECTION_V1",
}


@dataclass(frozen=True)
class ValidatedConfig:
    raw: dict[str, Any]
    lambda_anchor: Fraction
    lambda_target: Fraction
    delta_overlap_min: Fraction
    grid: Fraction
    minimum_window_width: Fraction
    w0_lo: Fraction
    w0_hi: Fraction

    @property
    def minimum_lambda_width(self) -> Fraction:
        return Fraction(1, 1 << self.raw["min_lambda_width_exp"])


class ConfigValidator:
    def __init__(self, *, symlink_escape_prefixes: Iterable[str] = ()) -> None:
        self._escape_prefixes = tuple(symlink_escape_prefixes)

    def validate(self, config: Any) -> ValidatedConfig:
        if not isinstance(config, dict):
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "config must be an object",
            )
        if set(config) != REQUIRED_CONFIG_FIELDS:
            missing = sorted(REQUIRED_CONFIG_FIELDS - set(config))
            unknown = sorted(set(config) - REQUIRED_CONFIG_FIELDS)
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                f"closed config schema violation; missing={missing}, unknown={unknown}",
            )

        anchor = CanonicalRational.from_object(config["lambda_anchor"], "lambda_anchor").value
        target = CanonicalRational.from_object(config["lambda_target"], "lambda_target").value
        if anchor != Fraction(118, 25):
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "lambda_anchor must equal 118/25",
            )
        if not Fraction(1) <= target < anchor:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "lambda_target outside [1,lambda_anchor)",
            )

        for field in NONNEGATIVE_INT_FIELDS:
            value = config[field]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ContractReject(
                    CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                    f"{field} must be a nonnegative integer",
                )
        for field in POSITIVE_INT_FIELDS:
            value = config[field]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ContractReject(
                    CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                    f"{field} must be a positive integer",
                )

        if config["per_box_eval_limit"] > config["global_eval_limit"]:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "per_box_eval_limit exceeds global_eval_limit",
            )
        if config["checker_dps"] < config["dps"]:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "checker_dps must be >= dps",
            )
        if config["cg_pilot_run_id"] != 30334858060:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "cg_pilot_run_id mismatch",
            )

        delta = CanonicalRational.from_object(
            config["delta_overlap_min"], "delta_overlap_min"
        ).value
        grid = Fraction(1, 1 << config["window_grid_exp"])
        minimum_window_width = Fraction(1, 1 << config["window_min_width_exp"])
        w0_lo = CanonicalDyadic.from_object(config["w0_lo"], "w0_lo").value
        w0_hi = CanonicalDyadic.from_object(config["w0_hi"], "w0_hi").value

        if delta <= 0:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "delta_overlap_min must be positive",
            )
        if delta > minimum_window_width:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "delta_overlap_min exceeds minimum window width",
            )
        if minimum_window_width > 1 - 2 * grid:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "minimum window width exceeds clamped domain",
            )
        if not grid <= w0_lo < w0_hi <= 1 - grid:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "W_anchor_seed violates domain gate",
            )
        if not w0_lo <= Fraction(1, 64) <= Fraction(11, 256) <= w0_hi:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "W_anchor_seed does not contain I_CG hull",
            )
        if w0_hi - w0_lo < delta:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "W_anchor_seed narrower than overlap minimum",
            )
        if w0_hi - w0_lo < minimum_window_width:
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "W_anchor_seed narrower than minimum window width",
            )

        for field in PATH_FIELDS:
            validate_repo_relative_path(
                config[field],
                field,
                symlink_escape_prefixes=self._escape_prefixes,
            )
        for field in SHA_FIELDS:
            validate_sha256(config[field], field)
        validate_id(config["adapter_id"], "adapter_id")

        for field, expected in CONSTANT_FIELDS.items():
            if config[field] != expected:
                raise ContractReject(
                    CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                    f"{field} must equal {expected}",
                )

        dependencies = config["sweep_logical_dependencies"]
        if not isinstance(dependencies, dict) or set(dependencies) != REQUIRED_DEPENDENCIES:
            raise ContractReject(
                CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                "logical dependency key set mismatch",
            )
        for key, entry in dependencies.items():
            if not isinstance(entry, dict) or set(entry) != DEPENDENCY_ENTRY_FIELDS:
                raise ContractReject(
                    CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                    f"logical dependency entry schema mismatch: {key}",
                )
            if entry["lemma_id"] != key:
                raise ContractReject(
                    CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                    f"logical dependency lemma_id mismatch: {key}",
                )
            try:
                validate_sha256(entry["dependency_entry_sha256"], f"{key}.dependency_entry_sha256")
                validate_id(entry["expected_allowlist_id"], f"{key}.expected_allowlist_id")
            except ContractReject as exc:
                raise ContractReject(
                    CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
                    f"logical dependency field violation: {key}",
                ) from exc

        return ValidatedConfig(
            raw=config,
            lambda_anchor=anchor,
            lambda_target=target,
            delta_overlap_min=delta,
            grid=grid,
            minimum_window_width=minimum_window_width,
            w0_lo=w0_lo,
            w0_hi=w0_hi,
        )


def normalize_external_aliases(config: dict[str, Any]) -> dict[str, Any]:
    """Normalize the sole permitted external alias before canonical config hashing."""
    normalized = dict(config)
    if "lambda_match" in normalized:
        match = CanonicalRational.from_object(normalized["lambda_match"], "lambda_match").value
        anchor = CanonicalRational.from_object(normalized.get("lambda_anchor"), "lambda_anchor").value
        if match != anchor or match != Fraction(118, 25):
            raise ContractReject(
                CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                "lambda_match alias mismatch",
            )
        del normalized["lambda_match"]
    return normalized
