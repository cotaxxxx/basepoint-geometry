#!/usr/bin/env python3
"""Positive B-TUBE v2.1 controls."""
from controls_common import *

def positive_full_mock_chain() -> int:
    return exit_for_bundle(build_bundle(full=True))


def positive_core_deferred() -> int:
    return exit_for_bundle(build_bundle(full=False))


def positive_tight_production_like_cell() -> int:
    return exit_for_bundle(build_bundle(full=True, tight=True))


def positive_checker_dps_equal_generator_dps() -> int:
    return exit_for_bundle(build_bundle(checker_dps=60))


def positive_canonical_dyadic_roundtrip() -> int:
    def run():
        original = Dyadic.canonical(40, 9)
        if Dyadic.from_json(original.to_json()) != original:
            raise AssertionError("dyadic roundtrip")
    return _exit_custom(run)


def positive_join_exact_endpoint() -> int:
    result = check_bundle(build_bundle(full=True))
    return 0 if result.joins == 1 else 1


def positive_canonical_record_bytes_roundtrip() -> int:
    def run():
        bundle = build_bundle()
        for record, raw in parse_canonical_jsonl(bundle.records_jsonl):
            if canonical_json_bytes(record) != raw:
                raise AssertionError("record bytes")
    return _exit_custom(run)


def positive_arf_mag_exact_extraction() -> int:
    def run():
        interval = arb_ball_to_exact_interval(_FakeBall((13, -7), (1, -3)))
        expected = DyadicInterval(Dyadic(-3, 7), Dyadic(29, 7))
        if interval != expected:
            raise AssertionError("exact arf/mag extraction")
    return _exit_custom(run)


def positive_coarse_mag_radius_exact_endpoints() -> int:
    return positive_arf_mag_exact_extraction()


def positive_display_field_variation_ignored() -> int:
    a = exit_for_bundle(build_bundle(display_tag="human-A"))
    b = exit_for_bundle(build_bundle(display_tag="deliberately-wrong-decimal-display"))
    return 0 if a == 0 and b == 0 else 1


def positive_cg_function_identity() -> int:
    bundle = build_bundle()
    config, _, records, _ = _objects(bundle)
    match = next(record for record in records if record["phase"] == "match")
    cg = config["cg_match_dependency"]
    return 0 if match["b_kernel_sha256"] == match["cg_kernel_sha256"] == cg["b_kernel_sha256"] else 1



__all__ = [name for name in globals() if not name.startswith("__")]
