#!/usr/bin/env python3
"""Structural B-TUBE v2.1 negative controls."""
from controls_common import *

def neg_noncanonical_dyadic() -> int:
    bundle = _mutate_record(build_bundle(), "cell", lambda r: r["q_endpoint"].__setitem__("left", {"m": "2", "e": 6}))
    return exit_for_bundle(bundle)


def neg_saved_enclosure_shrink() -> int:
    def mutate(r):
        r["saved"]["krawczyk"] = DyadicInterval(Dyadic(0, 0), Dyadic(0, 0)).to_json()
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", mutate))


def neg_preconditioner_zero() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r.__setitem__("preconditioner", Dyadic(0, 0).to_json())))


def neg_preconditioner_tamper() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r.__setitem__("preconditioner", Dyadic(1, 0).to_json())))


def neg_slope_sign_flip() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r["saved"].__setitem__("slope", DyadicInterval.point(Dyadic(1, 0)).to_json())))


def neg_missing_cell() -> int:
    bundle = build_bundle()
    config, deps, records, summary = _objects(bundle)
    removed = False
    kept = []
    for record in records:
        if record.get("phase") == "cell" and record.get("cell_index") == 1 and not removed:
            removed = True
            continue
        kept.append(record)
    return exit_for_bundle(_rebuild(bundle, config=config, deps=deps, records=kept, summary=summary))


def _change_second_cell_lambda(key: str, value: Rational) -> int:
    def mutate(r):
        r["lambda"][key] = value.to_json()
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", mutate, occurrence=1))


def neg_lambda_gap() -> int:
    return _change_second_cell_lambda("lo", Rational(25, 8))


def neg_lambda_overlap() -> int:
    return _change_second_cell_lambda("lo", Rational(23, 8))


def neg_left_endpoint_mismatch() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r["lambda"].__setitem__("lo", Rational(17, 8).to_json()), occurrence=0))


def neg_right_endpoint_mismatch() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r["lambda"].__setitem__("hi", Rational(19, 4).to_json()), occurrence=1))


def neg_q_endpoint_tamper() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "cell", lambda r: r["q_endpoint"].__setitem__("left", Dyadic(1, 4).to_json())))


def neg_q_rule_tamper() -> int:
    bundle = build_bundle()
    config, deps, records, summary = _objects(bundle)
    config["q_evaluation_rule"] = "interval_expression_forbidden"
    return exit_for_bundle(_rebuild(bundle, config=config, deps=deps, records=records, summary=summary))


def neg_join_empty_intersection() -> int:
    def mutate(r):
        r["left_section"] = DyadicInterval(Dyadic(-1, 0), Dyadic(-1, 1)).to_json()
        r["right_section"] = DyadicInterval(Dyadic(1, 1), Dyadic(1, 0)).to_json()
        r["intersection"] = DyadicInterval.point(Dyadic(0, 0)).to_json()
    return exit_for_bundle(_mutate_record(build_bundle(), "join", mutate))


def neg_join_krawczyk_shrink() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "join", lambda r: r["saved"].__setitem__("krawczyk", DyadicInterval.point(Dyadic(0, 0)).to_json())))


def neg_join_preconditioner_zero() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "join", lambda r: r.__setitem__("preconditioner", Dyadic(0, 0).to_json())))


def neg_join_record_missing() -> int:
    bundle = build_bundle()
    config, deps, records, summary = _objects(bundle)
    records = [record for record in records if record.get("phase") != "join"]
    return exit_for_bundle(_rebuild(bundle, config=config, deps=deps, records=records, summary=summary))


def neg_boundary_dependency_sha() -> int:
    return exit_for_bundle(_mutate_record(build_bundle(), "boundary", lambda r: r.__setitem__("dependency_artifact_sha256", "2" * 64)))



__all__ = [name for name in globals() if not name.startswith("__")]
