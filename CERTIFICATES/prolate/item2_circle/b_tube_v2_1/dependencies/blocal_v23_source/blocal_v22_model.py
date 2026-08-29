#!/usr/bin/env python3
"""Canonical model for B-LOCAL v2.2 finite-route reimplementation."""
from __future__ import annotations
from fractions import Fraction
from typing import Any
import blocal_phase4_model as v21
import blocal_v22_policy as policy

SCHEMA = "blocal-run-config-v2"
DESIGN_VERSION = "2.2"
CHECKER_ID = "BLOCAL_V22_FINITE_ROUTES_CHECKER_V3"
SYMBOLIC_AUDIT_ID = "BLOCAL_V22_FINITE_ROUTES_SYMBOLIC_AUDIT_V2"
CHAIN_DOMAIN = "BLOCAL-COVERAGE-CHAIN-v2.2-finite-routes"
COMPLETE = "BLOCAL_COMPLETE"
INCOMPLETE = "BLOCAL_INCOMPLETE"
PATCH_TYPE = "EXACT_DYADIC_SQUARE"
REGULARIZATION_METHOD = "TWO_TRIANGLE_DUFFY_AFTER_SYMBOLIC_CANCELLATION_V2"
L3_BPRIME_ROUTE_ID = "BLOCAL_L3_STAGE1_ENDPOINT_PLUS_BPRIME_MONOTONICITY_V1"
L3_BPRIME_POLICY_ID = "BLOCAL_L3_BPRIME_STAGE1_POLICY_V1"
L3_BPRIME_DOMAIN_AUDIT_ID = "BLOCAL_L3_BPRIME_EXTENSION_DOMAIN_AUDIT_V1"
L3_BPRIME_BRANCH_GUARD_AUDIT_ID = "INHERITED_STAGE1_ANALYTIC_BRANCH_GUARDS_V1"
L3_BOUNDARY_IDENTITY_ID = "BLOCAL_L3_BOUNDARY_IDENTITY_B_EQ_F_R1_V1"
L3_MONOTONICITY_INFERENCE_ID = "BLOCAL_L3_MONOTONICITY_FROM_ENDPOINT_V1"
L3_BPRIME_DESIGN_SHA256 = "e726cb3ebd3c10209bac179d50fe9066b5c79d2701fcb3de1ab2e5f3c048cb01"
L3_BPRIME_SOURCE_PATH = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_l3_bprime.py"
STAGE1_BPRIME_SOURCE_SHA256 = "f5f2fe68773423e7ff037e4be9e31094a4ceff5489abd5aff8b14fc1361cd671"
STAGE1_VERIFY_CHANGE_SHA256 = "ee77ba15192a288491eb8b0fe9ecfac5ce0275808ac83f65a36503dc27cc1233"
STAGE1_BPLUS_LO = Fraction(-1989245103410365999127431, 10**30)
STAGE1_BPLUS_HI = Fraction(-346352715755865908388961, 25*10**28)

def rational_interval_json(lower: Fraction, upper: Fraction) -> dict[str, Any]:
    need(lower <= upper, "reversed rational interval")
    return {"lo": rational_json(lower), "hi": rational_json(upper)}

def rational_interval_fractions(value: Any, where: str = "rational interval") -> tuple[Fraction, Fraction]:
    obj = exact_keys(value, {"lo", "hi"}, where)
    lower = fraction_from_rational(obj["lo"], f"{where}.lo")
    upper = fraction_from_rational(obj["hi"], f"{where}.hi")
    need(lower <= upper, f"{where}: reversed")
    return lower, upper

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

ONE_OVER_PI_LO = Fraction(113, 355)
ONE_OVER_PI_HI = Fraction(106, 333)
NORMALIZATION_BITS = 192


def chain_genesis(config_hash: str) -> str:
    return sha256_bytes(CHAIN_DOMAIN.encode() + b"\0" + bytes.fromhex(config_hash))


def floor_dyadic(q: Fraction, bits: int = NORMALIZATION_BITS) -> Fraction:
    need(bits > 0, "rounding bits")
    scale = 1 << bits
    n = q.numerator * scale // q.denominator
    return Fraction(n, scale)


def ceil_dyadic(q: Fraction, bits: int = NORMALIZATION_BITS) -> Fraction:
    need(bits > 0, "rounding bits")
    scale = 1 << bits
    n = -((-q.numerator * scale) // q.denominator)
    return Fraction(n, scale)


def outward_dyadic(lower: Fraction, upper: Fraction,
                    bits: int = NORMALIZATION_BITS) -> dict[str, Any]:
    need(lower <= upper, "outward interval order")
    return interval_json(floor_dyadic(lower, bits), ceil_dyadic(upper, bits))


def interval_negate(value: Any) -> dict[str, Any]:
    lo, hi = interval_fractions(value, "negate")
    return interval_json(-hi, -lo)


def interval_add_exact(values: list[Any]) -> tuple[Fraction, Fraction]:
    lo = hi = Fraction(0)
    for value in values:
        a, b = interval_fractions(value, "sum child")
        lo += a; hi += b
    return lo, hi


def interval_divide_negative_denominator(num: Any, den: Any) -> tuple[Fraction, Fraction]:
    a, b = interval_fractions(num, "Newton numerator")
    c, d = interval_fractions(den, "Newton denominator")
    need(c <= d < 0, "strict negative Newton denominator")
    candidates = [a/c, a/d, b/c, b/d]
    return min(candidates), max(candidates)


def normalize_interval(unnormalized: Any) -> dict[str, Any]:
    a, b = interval_fractions(unnormalized, "unnormalized")
    factors = (ONE_OVER_PI_LO, ONE_OVER_PI_HI)
    values = [a*factors[0], a*factors[1], b*factors[0], b*factors[1]]
    return outward_dyadic(min(values), max(values))


def _positive_budget(obj: Any, where: str) -> None:
    exact_keys(obj, {"max_depth", "max_evaluations", "max_tiles"}, where)
    need(all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in obj.values()), where)


def validate_config(config: dict[str, Any]) -> None:
    exact_keys(config, {
        "schema", "design_version", "authorization", "implementation", "stage1_dependency",
        "kernel", "lambda_plus", "s_neg", "lambda_candidates", "u_max_candidates",
        "candidate_order", "precision", "budgets", "route_policies", "canonicalizer_id",
        "adapter", "outputs", "terminal_state_before_run", "geometry", "checker",
        "symbolic_audit", "base_v21", "design_contracts",
        "lambda_candidate_reduction", "l3_bprime_route",
    }, "config")
    need(config["schema"] == SCHEMA and config["design_version"] == DESIGN_VERSION,
         "config identity")
    need(config["canonicalizer_id"] == CANONICALIZER_ID, "canonicalizer")
    need(config["terminal_state_before_run"] == INCOMPLETE, "pre-run state")
    need(config["authorization"] == {
        "execution":"TAG_ONLY_EXPLICIT_AUTHORIZATION_REQUIRED",
        "diagnostic_cli":False, "calibration_auto_start":False,
    }, "authorization")
    exact_keys(config["implementation"], {"entrypoint_path", "sources_sha256"}, "implementation")
    pins = config["implementation"]["sources_sha256"]
    need(isinstance(pins, dict) and pins, "source pins")
    need(all(isinstance(k,str) and isinstance(v,str) and len(v)==64 for k,v in pins.items()),
         "source pin format")
    exact_keys(config["base_v21"], {"engine_path","engine_sha256","model_path","model_sha256",
                                    "provenance_path","provenance_sha256"}, "base_v21")
    exact_keys(config["adapter"], {"id","path","source_sha256"}, "adapter")
    need(config["adapter"]["id"] == ADAPTER_ID, "adapter id")
    exact_keys(config["kernel"], {"path","sha256","formula_state","required_api","single_supply",
                                  "import_policy"}, "kernel")
    need(config["kernel"]["formula_state"] == "FILLED", "kernel state")
    need(config["kernel"]["required_api"] == ["F_arb","dFdr_arb","angle_data"], "kernel API")
    need(config["kernel"]["single_supply"] is True, "single supply")
    need(config["kernel"]["import_policy"] == "HASH_BEFORE_IMPORT_ORIGIN_MATCH_REHASH_AFTER_IMPORT",
         "kernel import")
    l3=config["l3_bprime_route"]
    exact_keys(l3, {
        "id","policy_id","path","source_sha256","stage1_bprime_member_sha256",
        "stage1_verify_change_of_variables_sha256","identity_id","inference_id",
        "domain_audit_id","branch_guard_audit_id","python_flint","dps","bands",
        "rel_tol","eval_limit","depth_limit","max_interval_calls",
        "max_subdivision_depth","subdivision_enabled","endpoint_evidence",
    }, "l3_bprime_route")
    need(l3["id"]==L3_BPRIME_ROUTE_ID and l3["policy_id"]==L3_BPRIME_POLICY_ID, "L3 Bprime route ids")
    need(l3["path"]==L3_BPRIME_SOURCE_PATH and l3["source_sha256"]==pins.get(L3_BPRIME_SOURCE_PATH), "L3 Bprime source pin")
    need(l3["stage1_bprime_member_sha256"]==STAGE1_BPRIME_SOURCE_SHA256, "Stage-1 Bprime member pin")
    need(l3["stage1_verify_change_of_variables_sha256"]==STAGE1_VERIFY_CHANGE_SHA256, "Stage-1 identity source pin")
    need(l3["identity_id"]==L3_BOUNDARY_IDENTITY_ID and l3["inference_id"]==L3_MONOTONICITY_INFERENCE_ID, "L3 identity/inference ids")
    need(l3["domain_audit_id"]==L3_BPRIME_DOMAIN_AUDIT_ID and l3["branch_guard_audit_id"]==L3_BPRIME_BRANCH_GUARD_AUDIT_ID, "L3 audit ids")
    need(l3["python_flint"]=="0.9.0" and l3["dps"]==18 and l3["bands"]==4, "L3 Bprime runtime policy")
    need(fraction_from_dyadic(l3["rel_tol"])==Fraction(1,1<<18), "L3 Bprime rel_tol")
    need(l3["eval_limit"]==8000 and l3["depth_limit"]==22, "L3 Bprime integral budgets")
    need(l3["max_interval_calls"]==1 and l3["max_subdivision_depth"]==0 and l3["subdivision_enabled"] is False, "L3 Bprime outer policy")
    ep=l3["endpoint_evidence"]
    exact_keys(ep,{"evaluation_key","enclosure"},"L3 endpoint evidence")
    need(ep["evaluation_key"]=="B(206539/100000)","L3 endpoint key")
    elo,ehi=rational_interval_fractions(ep["enclosure"],"L3 endpoint enclosure")
    need((elo,ehi)==(STAGE1_BPLUS_LO,STAGE1_BPLUS_HI) and ehi<0,"L3 endpoint enclosure pin")
    need(fraction_from_rational(config["lambda_plus"]) == LAMBDA_PLUS, "lambda_plus")
    need(fraction_from_dyadic(config["s_neg"]) == S_NEG, "s_neg")
    increments=[fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    uvals=[fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    need(increments == [Fraction(1,1<<k) for k in range(9,3,-1)], "lambda candidates")
    need(uvals == [Fraction(1,1<<k) for k in (8,7,6,5,4)], "u candidates")
    need(config["candidate_order"] == "LAMBDA_MAJOR_U_MAX_MINOR", "candidate order")
    need(config["lambda_candidate_reduction"] == {
        "basis":"LADDER_RUN_5_AGGREGATE_RECORD",
        "workflow_run_id":31798611738,
        "aggregate_record_sha256":"d6c7e5f5a42acbbfb9e7b37fa2e7c5026a558ebc4d270ee5951f7b162081cca7",
        "validated_candidate_count":21,
        "excluded_original_indices":list(range(15)),
        "retained_original_indices":list(range(15,21)),
        "observation":"Original indices 0-14 were all budget-faithful MAX_EVALUATIONS INDETERMINATE.",
        "nonclaim":"This candidate-set reduction removes already observed indeterminate recomputation; it does not relax certification conditions, decision criteria, or budgets.",
    }, "lambda candidate reduction provenance")
    exact_keys(config["precision"], {"bits","absolute_tolerance"}, "precision")
    need(isinstance(config["precision"]["bits"],int) and config["precision"]["bits"]>=128,
         "precision bits")
    need(fraction_from_dyadic(config["precision"]["absolute_tolerance"])>0, "tolerance")
    exact_keys(config["budgets"], {"L1","L2","L3","J_START"}, "budgets")
    for node in ("L1","L2","L3"):
        _positive_budget(config["budgets"][node], f"budgets.{node}")
    exact_keys(config["budgets"]["J_START"], {"max_bisections","max_evaluations"}, "J_START")
    need(all(isinstance(v,int) and not isinstance(v,bool) and v>0
             for v in config["budgets"]["J_START"].values()), "J_START budget")
    exact_keys(config["route_policies"], {"F_ROUTE","K_ROUTE"}, "route_policies")
    policy.validate_route_policy(config["route_policies"]["F_ROUTE"], "F_ROUTE policy")
    policy.validate_route_policy(config["route_policies"]["K_ROUTE"], "K_ROUTE policy")
    g=config["geometry"]
    exact_keys(g, {"eps","u_cut","patch_type","regularization_method"}, "geometry")
    need(fraction_from_dyadic(g["eps"]) == Fraction(1,1<<8), "eps fixed")
    ucut=fraction_from_dyadic(g["u_cut"])
    need(ucut == Fraction(1,1<<12) and all(ucut<=u for u in uvals), "u_cut landmark")
    need(g["patch_type"]==PATCH_TYPE and g["regularization_method"]==REGULARIZATION_METHOD,
         "geometry method")
    exact_keys(config["checker"], {"id","path","source_sha256"}, "checker")
    need(config["checker"]["id"] == CHECKER_ID, "checker id")
    exact_keys(config["symbolic_audit"], {"id","path","source_sha256"}, "audit")
    need(config["symbolic_audit"]["id"] == SYMBOLIC_AUDIT_ID, "audit id")
    exact_keys(config["outputs"], {"records","certificate","summary"}, "outputs")
    need(config["design_contracts"] == {
        "revision":"f305adaca6aeaf533472fa919d8a333537ba4954e4e4c842a57e0deca0c1265f",
        "f4":"c9cf94295fb53fa5e4446a19d3711de5b78924d22f16a3d93756d73fd475b115",
        "f5":"cf64fcfee14e73e3784c6b4af1027b53e7d24cf605631ec396fcf28a3dbe9e41",
        "method_selection_addendum":"7fafe5f465f9f38e61831b804a4bc95090af41b8fe31347897e7b2f40bf3d316",
        "c1_floor_spec":"8492755d298ace4c09f5118993eb2f2fa968d55ae5d04b81ff20c2c856fc90d3",
        "l3_bprime":L3_BPRIME_DESIGN_SHA256,
    }, "design contract hashes")
