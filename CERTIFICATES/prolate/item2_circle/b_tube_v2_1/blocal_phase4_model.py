#!/usr/bin/env python3
"""Canonical data model for B-LOCAL v2.1. No kernel imports or evaluation."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any

SCHEMA = "blocal-run-config-v1"
DESIGN_VERSION = "2.1"
CANONICALIZER_ID = "BTUBE_NUMERIC_SCHEMA_CANONICAL_JSON_V1"
ADAPTER_ID = "ARB_TO_CANONICAL_DYADIC_INTERVAL_V1"
CHAIN_DOMAIN = "BLOCAL-COVERAGE-CHAIN-v1"
COMPLETE = "BLOCAL_COMPLETE"
INCOMPLETE = "BLOCAL_INCOMPLETE"
CERTIFICATE_SCHEMA = "blocal-certificate-v1"
MACHINE_CONCLUSION_SCHEMA = "btube-blocal-machine-conclusion-v1"
ROUTE_ID = "R1_DIRECT_PINNED_F_ARB_V1"
RANGE = "(lambda_partial,lambda_start]"
LAMBDA_PLUS = Fraction(206539, 100000)
S_NEG = Fraction(1, 1 << 16)
STAGE1_STATEMENT = (
    "B(103/50)>0, B(207/100)<0, B(206538/100000)>0, "
    "B(206539/100000)<0, and B'(lambda)<0 on "
    "[206538/100000,206539/100000]. Hence lambda_partial is the unique "
    "root in (206538/100000,206539/100000)."
)
STAGE1_CONCLUSION = {
    "lambda_partial": "(206538/100000,206539/100000)",
    "strict_upper_bound": "206539/100000",
    "unique_on_interval": True,
}
STAGE1_SCOPE = (
    "Boundary-entry parameter only. Item 2 proper, requiring the single sign "
    "change of F_r, remains open."
)
L4_PREMISES = [
    "STAGE1_UNIQUE_BOUNDARY_ROOT_IN_OPEN_BRACKET",
    "STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET",
    "STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO",
    "L1_EXTENDED_HU_STRICT_POSITIVITY",
    "L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY",
    "L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY",
    "S_NEG_STRICTLY_EXCEEDS_STAGE1_BRACKET_WIDTH",
    "H_CONTINUITY_FROM_FIXED_FORMULA",
]


class BlocalError(RuntimeError):
    pass


def need(condition: Any, message: str) -> None:
    if not condition:
        raise BlocalError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _no_float(value: Any, where: str = "$") -> None:
    if isinstance(value, float):
        raise BlocalError(f"{where}: JSON float forbidden")
    if isinstance(value, dict):
        for key, child in value.items():
            need(isinstance(key, str) and key.isascii(), f"{where}: ASCII key required")
            _no_float(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _no_float(child, f"{where}[{index}]")


def canonical_json_bytes(value: Any) -> bytes:
    _no_float(value)
    try:
        return json.dumps(value, ensure_ascii=True, sort_keys=True,
                          separators=(",", ":"), allow_nan=False).encode()
    except (TypeError, ValueError) as exc:
        raise BlocalError("canonical JSON serialization failed") from exc


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        need(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_canonical_json(raw: bytes) -> dict[str, Any]:
    need(isinstance(raw, bytes), "config bytes required")
    need(not raw.startswith(b"\xef\xbb\xbf"), "BOM forbidden")
    need(b"\r" not in raw and b"\n" not in raw, "config newline forbidden")
    try:
        value = json.loads(
            raw.decode(), object_pairs_hook=_pairs,
            parse_float=lambda _: (_ for _ in ()).throw(BlocalError("JSON float forbidden")),
            parse_constant=lambda x: (_ for _ in ()).throw(BlocalError(f"constant forbidden: {x}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BlocalError("invalid canonical JSON") from exc
    need(isinstance(value, dict), "config object required")
    need(canonical_json_bytes(value) == raw, "config bytes are not canonical")
    return value


def exact_keys(value: Any, keys: set[str], where: str) -> dict[str, Any]:
    need(isinstance(value, dict) and set(value) == keys, f"{where}: exact keys")
    return value


def integer_string(value: Any, where: str) -> int:
    need(isinstance(value, str) and value, f"{where}: integer string")
    need(not value.startswith("+") and value != "-0", f"{where}: canonical integer")
    body = value[1:] if value.startswith("-") else value
    need(body.isascii() and body.isdigit(), f"{where}: decimal digits")
    need(len(body) == 1 or not body.startswith("0"), f"{where}: leading zero")
    return int(value)


def fraction_from_rational(value: Any, where: str = "rational") -> Fraction:
    obj = exact_keys(value, {"p", "q"}, where)
    p, q = integer_string(obj["p"], f"{where}.p"), integer_string(obj["q"], f"{where}.q")
    need(q > 0, f"{where}: positive denominator")
    result = Fraction(p, q)
    need((result.numerator, result.denominator) == (p, q), f"{where}: reduced")
    return result


def rational_json(value: Fraction) -> dict[str, str]:
    return {"p": str(value.numerator), "q": str(value.denominator)}


def fraction_from_dyadic(value: Any, where: str = "dyadic") -> Fraction:
    obj = exact_keys(value, {"m", "e"}, where)
    mantissa, exponent = integer_string(obj["m"], f"{where}.m"), obj["e"]
    need(isinstance(exponent, int) and not isinstance(exponent, bool) and exponent >= 0,
         f"{where}.e")
    need(not (mantissa == 0 and exponent), f"{where}: noncanonical zero")
    need(not (mantissa and exponent and mantissa % 2 == 0), f"{where}: reducible")
    return Fraction(mantissa, 1 << exponent)


def dyadic_json(value: Fraction) -> dict[str, Any]:
    denominator = value.denominator
    need(denominator > 0 and denominator & (denominator - 1) == 0, "non-dyadic fraction")
    exponent, mantissa = denominator.bit_length() - 1, value.numerator
    if not mantissa:
        return {"m": "0", "e": 0}
    while exponent and mantissa % 2 == 0:
        mantissa //= 2
        exponent -= 1
    return {"m": str(mantissa), "e": exponent}


def interval_json(lower: Fraction, upper: Fraction) -> dict[str, Any]:
    need(lower <= upper, "reversed interval")
    return {"lo": dyadic_json(lower), "hi": dyadic_json(upper)}


def interval_fractions(value: Any, where: str = "interval") -> tuple[Fraction, Fraction]:
    obj = exact_keys(value, {"lo", "hi"}, where)
    lower = fraction_from_dyadic(obj["lo"], f"{where}.lo")
    upper = fraction_from_dyadic(obj["hi"], f"{where}.hi")
    need(lower <= upper, f"{where}: reversed")
    return lower, upper


def validate_config(config: dict[str, Any]) -> None:
    exact_keys(config, {
        "schema", "design_version", "authorization", "implementation",
        "stage1_dependency", "kernel", "endpoint_route", "lambda_plus", "s_neg",
        "lambda_candidates", "u_max_candidates", "candidate_order", "precision",
        "budgets", "canonicalizer_id", "adapter", "outputs", "terminal_state_before_run",
    }, "config")
    need(config["schema"] == SCHEMA and config["design_version"] == DESIGN_VERSION,
         "config identity")
    need(config["canonicalizer_id"] == CANONICALIZER_ID, "canonicalizer ID")
    need(config["terminal_state_before_run"] == INCOMPLETE, "pre-run state")
    exact_keys(config["authorization"],
               {"execution", "diagnostic_cli", "calibration_auto_start"}, "authorization")
    need(config["authorization"] == {
        "execution": "TAG_ONLY_EXPLICIT_AUTHORIZATION_REQUIRED",
        "diagnostic_cli": False, "calibration_auto_start": False,
    }, "authorization boundary")
    exact_keys(config["implementation"], {"entrypoint_path", "sources_sha256"}, "implementation")
    need(isinstance(config["implementation"]["sources_sha256"], dict)
         and config["implementation"]["sources_sha256"], "implementation source pins")
    exact_keys(config["adapter"], {"id", "path", "source_sha256"}, "adapter")
    need(config["adapter"]["id"] == ADAPTER_ID, "adapter ID")
    exact_keys(config["kernel"],
               {"path", "sha256", "formula_state", "required_api", "single_supply", "import_policy"},
               "kernel")
    need(config["kernel"]["formula_state"] == "FILLED", "kernel formula state")
    need(config["kernel"]["required_api"] == ["F_arb", "dFdr_arb"], "kernel API")
    need(config["kernel"]["single_supply"] is True, "kernel single supply")
    need(config["kernel"]["import_policy"] ==
         "HASH_BEFORE_IMPORT_ORIGIN_MATCH_REHASH_AFTER_IMPORT", "kernel import policy")
    exact_keys(config["endpoint_route"], {
        "id", "function", "r", "same_pinned_kernel", "finite_enclosure_required",
        "nan_rejected", "one_minus_epsilon_forbidden", "silent_fallback_forbidden",
        "alternate_boundary_kernel",
    }, "endpoint_route")
    route = config["endpoint_route"]
    need(route["id"] == ROUTE_ID and route["function"] == "F_arb", "endpoint route")
    need(fraction_from_rational(route["r"]) == 1, "endpoint exact r=1")
    need(route["same_pinned_kernel"] is True and route["finite_enclosure_required"] is True
         and route["nan_rejected"] is True and route["one_minus_epsilon_forbidden"] is True
         and route["silent_fallback_forbidden"] is True
         and route["alternate_boundary_kernel"] is None, "endpoint route contract")
    need(fraction_from_rational(config["lambda_plus"]) == LAMBDA_PLUS, "lambda_plus")
    need(fraction_from_dyadic(config["s_neg"]) == S_NEG, "s_neg")
    increments = [fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    u_values = [fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    need(increments == [Fraction(1, 1 << k) for k in range(24, 3, -1)], "lambda candidates")
    need(u_values == [Fraction(1, 1 << k) for k in (8, 7, 6, 5, 4)], "u candidates")
    need(config["candidate_order"] == "LAMBDA_MAJOR_U_MAX_MINOR", "candidate order")
    exact_keys(config["precision"],
               {"bits", "absolute_tolerance", "kernel_depth_limit", "kernel_eval_limit"},
               "precision")
    precision = config["precision"]
    need(isinstance(precision["bits"], int) and precision["bits"] >= 128, "precision bits")
    need(fraction_from_dyadic(precision["absolute_tolerance"]) > 0, "positive tolerance")
    need(all(isinstance(precision[k], int) and precision[k] > 0
             for k in ("kernel_depth_limit", "kernel_eval_limit")), "kernel limits")
    exact_keys(config["budgets"], {"L1", "L2", "L3", "J_START"}, "budgets")
    for node in ("L1", "L2", "L3"):
        exact_keys(config["budgets"][node],
                   {"max_depth", "max_evaluations", "max_tiles"}, f"budgets.{node}")
        need(all(isinstance(v, int) and not isinstance(v, bool) and v > 0
                 for v in config["budgets"][node].values()), f"budgets.{node}")
    exact_keys(config["budgets"]["J_START"],
               {"max_bisections", "max_evaluations"}, "budgets.J_START")
    need(all(isinstance(v, int) and not isinstance(v, bool) and v > 0
             for v in config["budgets"]["J_START"].values()), "budgets.J_START")
    exact_keys(config["outputs"], {"records", "certificate", "summary"}, "outputs")


def record_hash(record: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes({k: v for k, v in record.items()
                                              if k != "record_sha256"}))


def chain_genesis(config_hash: str) -> str:
    return sha256_bytes(CHAIN_DOMAIN.encode() + b"\0" + bytes.fromhex(config_hash))


def append_record(records: list[dict[str, Any]], previous: str,
                  body: dict[str, Any]) -> str:
    record = dict(body, previous_record_sha256=previous)
    record["record_sha256"] = record_hash(record)
    records.append(record)
    return record["record_sha256"]


def logical_lemmas() -> list[dict[str, Any]]:
    return [{
        "lemma_id": "BLOCAL_IVT_MONOTONE_ENTRY_V1", "machine_verified": False,
        "premises": list(L4_PREMISES),
        "conclusion": {"unique_non_degenerate_root_for_every_lambda_in": RANGE},
    }]


def machine_conclusion(selected: tuple[int, Fraction, Fraction, dict[str, Any]] | None,
                       counts: dict[str, int], record_count: int,
                       chain_tip: str) -> dict[str, Any]:
    complete = selected is not None
    claims = (
        "stage1_dependency_exact", "l1_extended_exact_coverage",
        "l1_Hu_strictly_positive", "l2_extended_exact_coverage",
        "l2_inner_face_strictly_positive", "l3_nonnegative_exact_coverage",
        "l3_boundary_face_strictly_negative", "start_root_interval_certified",
        "supplies_binding_lambda_start",
    )
    return {
        "schema": MACHINE_CONCLUSION_SCHEMA,
        "status": COMPLETE if complete else INCOMPLETE,
        "selected_candidate_index": selected[0] if selected else None,
        "lambda_start": rational_json(selected[1]) if selected else None,
        "start_root_interval": selected[3]["r_interval"] if selected else None,
        "machine_claims": {**{key: complete for key in claims}, "real_analytic_claimed": False},
        "coverage": {
            "l1_leaf_count": counts["L1"], "l2_leaf_count": counts["L2"],
            "l3_leaf_count": counts["L3"], "record_count": record_count,
            "chain_tip_sha256": chain_tip,
        },
    }
