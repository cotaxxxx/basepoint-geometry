#!/usr/bin/env python3
"""Canonical data model for B-LOCAL v2.2 boundary-strip regularization."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

import blocal_phase4_model as v21

SCHEMA = "blocal-run-config-v2"
DESIGN_VERSION = "2.2"
BOUNDARY_LEMMA_ID = "BLOCAL_R1_BOUNDARY_REGULARIZATION_V1"
BOUNDARY_ROUTE_ID = "R1_DUFFY_REGULARIZED_DFDR_V1"
PATCH_TYPE = "EXACT_DYADIC_SQUARE"
REGULARIZATION_METHOD = "TWO_TRIANGLE_DUFFY_AFTER_SYMBOLIC_CANCELLATION_V1"
CHECKER_ID = "BLOCAL_V22_CHECKER_V1"
SYMBOLIC_AUDIT_ID = "BLOCAL_V22_DUFFY_SYMBOLIC_AUDIT_V1"
CHAIN_DOMAIN = "BLOCAL-COVERAGE-CHAIN-v2.2"
COMPLETE = "BLOCAL_COMPLETE"
INCOMPLETE = "BLOCAL_INCOMPLETE"

need = v21.need
sha256_bytes = v21.sha256_bytes
canonical_json_bytes = v21.canonical_json_bytes
parse_canonical_json = v21.parse_canonical_json
exact_keys = v21.exact_keys
fraction_from_rational = v21.fraction_from_rational
fraction_from_dyadic = v21.fraction_from_dyadic
rational_json = v21.rational_json
dyadic_json = v21.dyadic_json
interval_json = v21.interval_json
interval_fractions = v21.interval_fractions
record_hash = v21.record_hash
append_record = v21.append_record
LAMBDA_PLUS = v21.LAMBDA_PLUS
S_NEG = v21.S_NEG
ADAPTER_ID = v21.ADAPTER_ID
CANONICALIZER_ID = v21.CANONICALIZER_ID
ROUTE_ID = v21.ROUTE_ID


def chain_genesis(config_hash: str) -> str:
    return sha256_bytes(CHAIN_DOMAIN.encode() + b"\0" + bytes.fromhex(config_hash))


def _positive_budget(obj: Any, where: str) -> None:
    exact_keys(obj, {"max_depth", "max_evaluations", "max_tiles"}, where)
    need(all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in obj.values()), where)


def validate_config(config: dict[str, Any]) -> None:
    exact_keys(config, {
        "schema", "design_version", "authorization", "implementation",
        "stage1_dependency", "kernel", "endpoint_route", "lambda_plus", "s_neg",
        "lambda_candidates", "u_max_candidates", "candidate_order", "precision",
        "budgets", "canonicalizer_id", "adapter", "outputs", "terminal_state_before_run",
        "boundary_strip", "checker", "symbolic_audit", "base_v21",
    }, "config")
    need(config["schema"] == SCHEMA and config["design_version"] == DESIGN_VERSION,
         "v2.2 config identity")
    need(config["canonicalizer_id"] == CANONICALIZER_ID, "canonicalizer")
    need(config["terminal_state_before_run"] == INCOMPLETE, "pre-run state")
    need(config["authorization"] == {
        "execution": "TAG_ONLY_EXPLICIT_AUTHORIZATION_REQUIRED",
        "diagnostic_cli": False,
        "calibration_auto_start": False,
    }, "authorization boundary")

    exact_keys(config["implementation"], {"entrypoint_path", "sources_sha256"}, "implementation")
    pins = config["implementation"]["sources_sha256"]
    need(isinstance(pins, dict) and len(pins) >= 6, "implementation pins")
    need(all(isinstance(k, str) and isinstance(v, str) and len(v) == 64 for k, v in pins.items()),
         "implementation pin format")

    exact_keys(config["base_v21"], {"engine_path", "engine_sha256", "model_path", "model_sha256",
                                    "provenance_path", "provenance_sha256"}, "base_v21")
    for key in ("engine_sha256", "model_sha256", "provenance_sha256"):
        need(isinstance(config["base_v21"][key], str) and len(config["base_v21"][key]) == 64,
             f"base_v21.{key}")

    exact_keys(config["adapter"], {"id", "path", "source_sha256"}, "adapter")
    need(config["adapter"]["id"] == ADAPTER_ID, "adapter ID")

    exact_keys(config["kernel"],
               {"path", "sha256", "formula_state", "required_api", "single_supply", "import_policy"},
               "kernel")
    need(config["kernel"]["formula_state"] == "FILLED", "kernel state")
    need(config["kernel"]["required_api"] == ["F_arb", "dFdr_arb", "angle_data"],
         "v2.2 kernel API")
    need(config["kernel"]["single_supply"] is True, "kernel single supply")
    need(config["kernel"]["import_policy"] == "HASH_BEFORE_IMPORT_ORIGIN_MATCH_REHASH_AFTER_IMPORT",
         "kernel import policy")

    route = config["endpoint_route"]
    exact_keys(route, {"id", "function", "r", "same_pinned_kernel", "finite_enclosure_required",
                       "nan_rejected", "one_minus_epsilon_forbidden", "silent_fallback_forbidden",
                       "alternate_boundary_kernel"}, "endpoint_route")
    need(route["id"] == ROUTE_ID and route["function"] == "F_arb", "endpoint route")
    need(fraction_from_rational(route["r"]) == 1, "endpoint r")
    need(route["same_pinned_kernel"] is True and route["finite_enclosure_required"] is True
         and route["nan_rejected"] is True and route["one_minus_epsilon_forbidden"] is True
         and route["silent_fallback_forbidden"] is True
         and route["alternate_boundary_kernel"] is None, "endpoint contract")

    need(fraction_from_rational(config["lambda_plus"]) == LAMBDA_PLUS, "lambda_plus")
    need(fraction_from_dyadic(config["s_neg"]) == S_NEG, "s_neg")
    increments = [fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    u_values = [fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    need(increments == [Fraction(1, 1 << k) for k in range(24, 3, -1)], "lambda candidates")
    need(u_values == [Fraction(1, 1 << k) for k in (8, 7, 6, 5, 4)], "u candidates")
    need(config["candidate_order"] == "LAMBDA_MAJOR_U_MAX_MINOR", "candidate order")

    exact_keys(config["precision"],
               {"bits", "absolute_tolerance", "kernel_depth_limit", "kernel_eval_limit",
                "angular_grid_power"}, "precision")
    p = config["precision"]
    need(isinstance(p["bits"], int) and p["bits"] >= 128, "precision bits")
    need(fraction_from_dyadic(p["absolute_tolerance"]) > 0, "tolerance")
    need(all(isinstance(p[k], int) and p[k] > 0
             for k in ("kernel_depth_limit", "kernel_eval_limit", "angular_grid_power")),
         "precision limits")

    exact_keys(config["budgets"], {"L1_INTERIOR", "L1_BOUNDARY", "L2", "L3", "J_START"},
               "budgets")
    for node in ("L1_INTERIOR", "L1_BOUNDARY", "L2", "L3"):
        _positive_budget(config["budgets"][node], f"budgets.{node}")
    exact_keys(config["budgets"]["J_START"], {"max_bisections", "max_evaluations"},
               "budgets.J_START")
    need(all(isinstance(v, int) and not isinstance(v, bool) and v > 0
             for v in config["budgets"]["J_START"].values()), "J_START budget")

    b = config["boundary_strip"]
    exact_keys(b, {"lemma_id", "route_id", "patch_type", "regularization_method",
                   "u_cut", "eps", "same_pinned_kernel", "silent_fallback_forbidden"},
               "boundary_strip")
    need(b["lemma_id"] == BOUNDARY_LEMMA_ID, "boundary lemma")
    need(b["route_id"] == BOUNDARY_ROUTE_ID, "boundary route")
    need(b["patch_type"] == PATCH_TYPE, "patch type")
    need(b["regularization_method"] == REGULARIZATION_METHOD, "regularization method")
    u_cut = fraction_from_dyadic(b["u_cut"], "boundary_strip.u_cut")
    eps = fraction_from_dyadic(b["eps"], "boundary_strip.eps")
    need(u_cut == Fraction(1, 1 << 12), "u_cut frozen value")
    need(eps == Fraction(1, 1 << 8), "eps frozen value")
    need(b["same_pinned_kernel"] is True and b["silent_fallback_forbidden"] is True,
         "boundary route contract")
    need(all(u_cut <= value for value in u_values), "u_cut <= every u_max")

    exact_keys(config["checker"], {"id", "path", "source_sha256"}, "checker")
    need(config["checker"]["id"] == CHECKER_ID, "checker ID")
    exact_keys(config["symbolic_audit"], {"id", "path", "source_sha256"}, "symbolic_audit")
    need(config["symbolic_audit"]["id"] == SYMBOLIC_AUDIT_ID, "symbolic audit ID")
    exact_keys(config["outputs"], {"records", "certificate", "summary"}, "outputs")
