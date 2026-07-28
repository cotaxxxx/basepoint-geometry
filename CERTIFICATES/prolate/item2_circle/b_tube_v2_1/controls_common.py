#!/usr/bin/env python3
"""Single-dictionary positive/negative controls for B-TUBE v2.1 self-tests."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from typing import Any, Callable

from b_tube_checker import CheckError, check_bundle, exit_for_bundle
from b_tube_selftest_runner import (
    BLOCAL_MOCK_SHA256,
    CG_ARTIFACT_SHA256,
    FG_LEMMA,
    Bundle,
    _chain_records,
    build_bundle,
)
from numeric_schema import (
    CanonicalBytesError,
    Dyadic,
    DyadicInterval,
    Rational,
    SchemaError,
    arb_ball_to_exact_interval,
    canonical_json_bytes,
    canonical_source_forbidden,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)


CONTROL_EXPECT: dict[str, int] = {
    "positive_full_mock_chain": 0,
    "positive_core_deferred": 0,
    "positive_tight_production_like_cell": 0,
    "positive_checker_dps_equal_generator_dps": 0,
    "positive_canonical_dyadic_roundtrip": 0,
    "positive_join_exact_endpoint": 0,
    "positive_canonical_record_bytes_roundtrip": 0,
    "positive_arf_mag_exact_extraction": 0,
    "positive_coarse_mag_radius_exact_endpoints": 0,
    "positive_display_field_variation_ignored": 0,
    "positive_cg_function_identity": 0,
    "neg_noncanonical_dyadic": 1,
    "neg_saved_enclosure_shrink": 1,
    "neg_preconditioner_zero": 1,
    "neg_preconditioner_tamper": 1,
    "neg_slope_sign_flip": 1,
    "neg_missing_cell": 1,
    "neg_lambda_gap": 1,
    "neg_lambda_overlap": 1,
    "neg_left_endpoint_mismatch": 1,
    "neg_right_endpoint_mismatch": 1,
    "neg_q_endpoint_tamper": 1,
    "neg_q_rule_tamper": 1,
    "neg_join_empty_intersection": 1,
    "neg_join_krawczyk_shrink": 1,
    "neg_join_preconditioner_zero": 1,
    "neg_join_record_missing": 1,
    "neg_boundary_dependency_sha": 2,
    "neg_match_interval_tamper": 1,
    "neg_cg_artifact_sha_tamper": 2,
    "neg_cg_kernel_sha_mismatch": 2,
    "neg_fg_identity_lemma_missing": 2,
    "neg_previous_record_sha": 1,
    "neg_chain_record_reorder": 1,
    "neg_record_key_order_noncanonical": 1,
    "neg_record_whitespace_noncanonical": 1,
    "neg_record_trailing_newline": 1,
    "neg_record_crlf": 1,
    "neg_record_duplicate_key": 1,
    "neg_record_chain_hash_over_linefeed": 1,
    "neg_checker_dps_below_generator_dps": 1,
    "neg_unresolved_leaf": 1,
    "neg_adapter_string_path_detected": 1,
}


class _FakeExact:
    def __init__(self, mantissa: int, exponent: int, *, fail: bool = False):
        self._mantissa = mantissa
        self._exponent = exponent
        self._fail = fail

    def man_exp(self):
        if self._fail:
            raise ValueError("nonfinite")
        return self._mantissa, self._exponent


class _FakeBall:
    def __init__(self, mid: tuple[int, int], rad: tuple[int, int]):
        self._mid = _FakeExact(*mid)
        self._rad = _FakeExact(*rad)

    def mid(self):
        return self._mid

    def rad(self):
        return self._rad


def _objects(bundle: Bundle):
    config = parse_canonical_json_bytes(bundle.config_bytes)
    deps = parse_canonical_json_bytes(bundle.dependencies_bytes)
    summary = parse_canonical_json_bytes(bundle.summary_bytes)
    records = [record for record, _ in parse_canonical_jsonl(bundle.records_jsonl)]
    return config, deps, records, summary


def _rebuild(
    bundle: Bundle,
    *,
    config: dict[str, Any] | None = None,
    deps: dict[str, Any] | None = None,
    records: list[dict[str, Any]] | None = None,
    summary: dict[str, Any] | None = None,
    rechain: bool = True,
) -> Bundle:
    old_config, old_deps, old_records, old_summary = _objects(bundle)
    config = old_config if config is None else config
    deps = old_deps if deps is None else deps
    records = old_records if records is None else records
    summary = old_summary if summary is None else summary
    if rechain:
        clean: list[dict[str, Any]] = []
        for record in records:
            item = dict(record)
            item.pop("record_index", None)
            item.pop("previous_record_sha256", None)
            clean.append(item)
        records_bytes, tip = _chain_records(clean, config)
        summary = dict(summary)
        summary["record_count"] = len(clean)
        summary["chain_tip_sha256"] = tip
    else:
        records_bytes = bundle.records_jsonl
    return Bundle(
        config_bytes=canonical_json_bytes(config),
        dependencies_bytes=canonical_json_bytes(deps),
        records_jsonl=records_bytes,
        summary_bytes=canonical_json_bytes(summary),
    )


def _mutate_record(bundle: Bundle, phase: str, mutate: Callable[[dict[str, Any]], None], *, occurrence: int = 0) -> Bundle:
    config, deps, records, summary = _objects(bundle)
    found = 0
    for record in records:
        if record.get("phase") == phase:
            if found == occurrence:
                mutate(record)
                return _rebuild(bundle, config=config, deps=deps, records=records, summary=summary)
            found += 1
    raise AssertionError(f"phase not found: {phase}")


def _exit_custom(fn: Callable[[], None]) -> int:
    try:
        fn()
    except (CheckError, SchemaError, CanonicalBytesError, AssertionError, ValueError):
        return 1
    return 0



__all__ = [name for name in globals() if not name.startswith("__")]
