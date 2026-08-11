#!/usr/bin/env python3
"""Calculation-free binding negative controls for B-LOCAL v2.2 finite-route checker."""
from __future__ import annotations

import copy
from fractions import Fraction

import blocal_arb_adapter as adapter
import blocal_v22_checker as checker
import blocal_v22_model as model
import blocal_v22_policy as policy


def rejects(fn, label: str) -> None:
    try:
        fn()
    except Exception:
        return
    raise RuntimeError(f"negative control accepted: {label}")


def config() -> dict:
    z = "0"*64
    return {
        "schema": model.SCHEMA,
        "design_version": model.DESIGN_VERSION,
        "authorization": {
            "execution": "TAG_ONLY_EXPLICIT_AUTHORIZATION_REQUIRED",
            "diagnostic_cli": False,
            "calibration_auto_start": False,
        },
        "implementation": {"entrypoint_path": "x", "sources_sha256": {"x": z}},
        "stage1_dependency": {},
        "kernel": {
            "path": "k", "sha256": z, "formula_state": "FILLED",
            "required_api": ["F_arb", "dFdr_arb", "angle_data"],
            "single_supply": True,
            "import_policy": "HASH_BEFORE_IMPORT_ORIGIN_MATCH_REHASH_AFTER_IMPORT",
        },
        "lambda_plus": model.rational_json(model.LAMBDA_PLUS),
        "s_neg": model.dyadic_json(model.S_NEG),
        "lambda_candidates": [
            model.dyadic_json(Fraction(1, 1 << k)) for k in range(24, 3, -1)
        ],
        "u_max_candidates": [
            model.dyadic_json(Fraction(1, 1 << k)) for k in (8, 7, 6, 5, 4)
        ],
        "candidate_order": "LAMBDA_MAJOR_U_MAX_MINOR",
        "precision": {
            "bits": 256,
            "absolute_tolerance": model.dyadic_json(Fraction(1, 1 << 160)),
        },
        "budgets": {
            "L1": {"max_depth": 18, "max_evaluations": 20000, "max_tiles": 12000},
            "L2": {"max_depth": 22, "max_evaluations": 12000, "max_tiles": 8000},
            "L3": {"max_depth": 22, "max_evaluations": 12000, "max_tiles": 8000},
            "J_START": {"max_bisections": 40, "max_evaluations": 96},
        },
        "route_policies": {
            "F_ROUTE": {
                "id": policy.ANGULAR_POLICY_ID, "max_depth": 12,
                "max_children": 12000, "max_evaluations": 12000, "min_depth": 1,
            },
            "K_ROUTE": {
                "id": policy.ANGULAR_POLICY_ID, "max_depth": 12,
                "max_children": 12000, "max_evaluations": 12000, "min_depth": 1,
            },
        },
        "canonicalizer_id": model.CANONICALIZER_ID,
        "adapter": {"id": model.ADAPTER_ID, "path": "a", "source_sha256": z},
        "outputs": {"records": "r", "certificate": "c", "summary": "s"},
        "terminal_state_before_run": model.INCOMPLETE,
        "geometry": {
            "eps": model.dyadic_json(Fraction(1, 1 << 8)),
            "u_cut": model.dyadic_json(Fraction(1, 1 << 12)),
            "patch_type": model.PATCH_TYPE,
            "regularization_method": model.REGULARIZATION_METHOD,
        },
        "checker": {"id": model.CHECKER_ID, "path": "q", "source_sha256": z},
        "symbolic_audit": {
            "id": model.SYMBOLIC_AUDIT_ID, "path": "y", "source_sha256": z
        },
        "base_v21": {
            "engine_path": "e", "engine_sha256": z,
            "model_path": "m", "model_sha256": z,
            "provenance_path": "p", "provenance_sha256": z,
        },
        "design_contracts": {
            "revision": "f305adaca6aeaf533472fa919d8a333537ba4954e4e4c842a57e0deca0c1265f",
            "f4": "c9cf94295fb53fa5e4446a19d3711de5b78924d22f16a3d93756d73fd475b115",
            "f5": "cf64fcfee14e73e3784c6b4af1027b53e7d24cf605631ec396fcf28a3dbe9e41",
        },
    }


def _gamma_detail() -> dict:
    return {
        "gamma_policy": policy.GAMMA_POLICY_ID,
        "gamma_subdivisions": [],
        "gamma_fallback_used": False,
        "sqrt_policy": policy.SQRT_POLICY_ID,
        "measure_identity": policy.MEASURE_ID,
    }


def proof(cfg: dict, quantity: str, value: Fraction,
          u0: Fraction, u1: Fraction,
          s0: Fraction, s1: Fraction) -> dict:
    children = []
    for reg in ("T1", "T2", "R1", "R2"):
        detail = _gamma_detail()
        if reg in ("T1", "T2"):
            detail.update({
                "Z_DEN_LO": model.rational_json(Fraction(1)),
                "helper_lemma_id": "BHAT_LOWER_V2",
                "duffy_id": policy.DUFFY_ID,
                "triangle_substitution": reg,
                "bounded_extensions": {
                    "y_h": "[0,1]", "v": "[-1,1]",
                    "z": "[0,1/sqrt(Z_DEN_LO)]",
                },
            })
        else:
            detail.update({
                "q_lo": model.rational_json(Fraction(1)),
                "q_hi": model.rational_json(Fraction(1)),
                "q_lo_policy": policy.Q_LO_POLICY_ID,
                "denominator_policy": policy.DENOMINATOR_POLICY_ID,
            })
            if reg == "R2":
                detail["R2_W_LO"] = model.rational_json(Fraction(1))
                detail["R2_COS_PHI_LO_HI"] = model.rational_json(Fraction(0))
        children.append({
            "child_id": reg,
            "parent_id": None,
            "region": reg,
            "depth": 0,
            "box": {
                "a": model.interval_json(Fraction(0), Fraction(1)),
                "b": model.interval_json(Fraction(0), Fraction(1)),
            },
            "source_coordinates":
                "(x,y_D)" if reg in ("T1", "T2") else "NORMALIZED_SOURCE_BOX",
            "detail": detail,
            "contribution_enclosure": model.interval_json(value, value),
            "status": "ACCEPTED",
        })
    lo, hi = model.interval_add_exact(
        [x["contribution_enclosure"] for x in children])
    unnorm = model.outward_dyadic(lo, hi)
    p = {
        "route_id": policy.F_ROUTE_ID if quantity == "F" else policy.K_ROUTE_ID,
        "quantity": quantity,
        "angular_policy_id": policy.ANGULAR_POLICY_ID,
        "policy": cfg["route_policies"]["F_ROUTE" if quantity == "F" else "K_ROUTE"],
        "denominator_policy_id": policy.DENOMINATOR_POLICY_ID,
        "sqrt_policy_id": policy.SQRT_POLICY_ID,
        "gamma_policy_id": policy.GAMMA_POLICY_ID,
        "q_lo_policy_id": policy.Q_LO_POLICY_ID,
        "normalization_policy_id": policy.NORMALIZATION_POLICY_ID,
        "one_over_pi_enclosure": {
            "lo": model.rational_json(model.ONE_OVER_PI_LO),
            "hi": model.rational_json(model.ONE_OVER_PI_HI),
        },
        "normalization_bits": model.NORMALIZATION_BITS,
        "u_interval": model.interval_json(u0, u1),
        "s_interval": model.interval_json(s0, s1),
        "eps": cfg["geometry"]["eps"],
        "patch_type": model.PATCH_TYPE,
        "ordered_children": children,
        "split_reasons": {},
        "evaluation_count": 4,
        "unnormalized_sum": unnorm,
        "normalized_enclosure": model.normalize_interval(unnorm),
        "complete_closed_cover": True,
        "direct_pinned_integrator_called": False,
    }
    p["proof_id"] = model.sha256_bytes(model.canonical_json_bytes(p))
    return p


def jrecord(cfg: dict) -> dict:
    umax = Fraction(1, 8)
    s = Fraction(1, 16)
    lam = model.LAMBDA_PLUS+s
    left = 1-umax
    right = Fraction(15, 16)
    mid = (left+right)/2
    pleft = proof(cfg, "F", Fraction(1), 1-left, 1-left, s, s)
    pright = proof(cfg, "F", Fraction(-1), 1-right, 1-right, s, s)
    pmid = proof(cfg, "F", Fraction(0), 1-mid, 1-mid, s, s)
    phu = proof(cfg, "H_U", Fraction(1), 1-right, 1-left, s, s)
    hu = phu["normalized_enclosure"]
    D = model.interval_negate(hu)
    qlo, qhi = model.interval_divide_negative_denominator(
        pmid["normalized_enclosure"], D)
    q = model.outward_dyadic(qlo, qhi)
    N = model.outward_dyadic(mid-qhi, mid-qlo)
    pts = [
        {
            "evaluation_id": "J-F-001",
            "r": model.rational_json(left),
            "lambda_start": model.rational_json(lam),
            "route_id": policy.F_ROUTE_ID,
            "route_proof": pleft,
            "normalized_F": pleft["normalized_enclosure"],
            "sign": "POSITIVE",
            "role": "INITIAL_LEFT",
        },
        {
            "evaluation_id": "J-F-002",
            "r": model.rational_json(right),
            "lambda_start": model.rational_json(lam),
            "route_id": policy.F_ROUTE_ID,
            "route_proof": pright,
            "normalized_F": pright["normalized_enclosure"],
            "sign": "NEGATIVE",
            "role": "RETAINED_RIGHT",
        },
        {
            "evaluation_id": "J-F-003",
            "r": model.rational_json(mid),
            "lambda_start": model.rational_json(lam),
            "route_id": policy.F_ROUTE_ID,
            "route_proof": pmid,
            "normalized_F": pmid["normalized_enclosure"],
            "sign": "UNRESOLVED",
            "role": "NEWTON_MIDPOINT",
        },
    ]
    der = {
        "record_id": "J-DERIVATIVE",
        "r_interval": model.interval_json(left, right),
        "u_interval": model.interval_json(1-right, 1-left),
        "lambda_start": model.rational_json(lam),
        "s": model.rational_json(s),
        "route_id": policy.K_ROUTE_ID,
        "route_proof": phu,
        "H_u": hu,
        "negation_rule_id": policy.NEGATION_RULE_ID,
        "F_r": D,
        "sup_F_r_lt_zero": True,
    }
    new = {
        "record_id": "J-NEWTON",
        "bracket": model.interval_json(left, right),
        "midpoint": model.rational_json(mid),
        "midpoint_F_record_id": "J-F-003",
        "F_m": pmid["normalized_enclosure"],
        "derivative_record_id": "J-DERIVATIVE",
        "D": D,
        "interval_arithmetic_policy_id": policy.NEWTON_POLICY_ID,
        "quotient": q,
        "newton_image": N,
        "strict_self_containment": True,
        "method_id": "INTERVAL_NEWTON_V2",
    }
    return {
        "record_type": "J_START",
        "node": "J_START",
        "candidate_index": 0,
        "lambda_start": model.rational_json(lam),
        "initial_bracket": model.interval_json(1-umax, Fraction(1)),
        "r_interval": model.interval_json(left, right),
        "ordered_bisection_records": pts,
        "derivative_record": der,
        "newton_record": new,
        "claim": "J_START_UNIQUE_NONDEGENERATE_ROOT",
        "certified": True,
        "direct_pinned_F_arb_called": False,
        "direct_pinned_dFdr_arb_called": False,
    }


class BadME:
    def man_exp(self):
        raise ValueError("nonfinite")


class BadBall:
    def mid(self):
        return BadME()

    def rad(self):
        return BadME()


def main() -> int:
    cfg = config()
    model.validate_config(cfg)
    base = proof(cfg, "H_U", Fraction(1), Fraction(0), Fraction(1, 8),
                 -model.S_NEG, Fraction(1, 16))
    checker.verify_route_proof(base, cfg, "H_U")

    # Existing fail-closed and structural controls.
    rejects(lambda: adapter.arb_ball_to_canonical_dyadic_interval(BadBall()),
            "nonfinite Arb")
    bad = copy.deepcopy(base)
    bad["ordered_children"][0]["box"]["a"] = model.interval_json(
        Fraction(0), Fraction(3, 4))
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"), "gap")
    bad = copy.deepcopy(base)
    bad["ordered_children"].append(copy.deepcopy(bad["ordered_children"][0]))
    bad["ordered_children"][-1]["child_id"] = "T1X"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"), "overlap")
    badc = copy.deepcopy(cfg)
    badc["geometry"]["patch_type"] = "CIRCULAR_PATCH"
    rejects(lambda: model.validate_config(badc), "circular patch")
    badc = copy.deepcopy(cfg)
    badc["geometry"]["u_cut"] = {"m": "0", "e": 0}
    rejects(lambda: model.validate_config(badc), "invalid u_cut")
    bad = copy.deepcopy(base)
    bad["ordered_children"][0]["detail"]["triangle_substitution"] = "T2"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"), "wrong T1/T2")
    bad = copy.deepcopy(base)
    bad["ordered_children"][0]["detail"]["measure_identity"] = "MISSING"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "missing measure identity")
    bad = copy.deepcopy(base)
    bad["ordered_children"][0]["detail"]["Z_DEN_LO"] = model.rational_json(
        Fraction(0))
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "Z_DEN_LO <=0")
    bad = copy.deepcopy(base)
    bad["ordered_children"][0]["detail"]["bounded_extensions"]["z"] = \
        "DIRECT_0_OVER_0"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "direct corner 0/0")
    rejects(lambda: checker.verify_symbolic_audit_result({"exact_algebra": False}),
            "symbolic audit failure")
    bad = copy.deepcopy(base)
    bad["route_id"] = "R1_DIRECT_PINNED_F_ARB_V1"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "direct pinned route claim")

    # R-1 through R-4 checker bindings.
    bad = copy.deepcopy(base)
    bad["sqrt_policy_id"] = "UNSAFE_DIRECT_SQRT"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R1 root sqrt policy")
    bad = copy.deepcopy(base)
    bad["ordered_children"][2]["detail"]["sqrt_policy"] = "UNSAFE_DIRECT_SQRT"
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R1 child sqrt policy")
    bad = copy.deepcopy(base)
    bad["ordered_children"][2]["detail"]["q_hi"] = model.rational_json(
        Fraction(1, 2))
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R2 q_hi below q_lo")
    bad = copy.deepcopy(base)
    bad["ordered_children"][3]["detail"]["R2_W_LO"] = model.rational_json(
        Fraction(2))
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R3 q floor omits W lower")
    bad = copy.deepcopy(base)
    d = bad["ordered_children"][2]["detail"]
    d["gamma_fallback_used"] = True
    d["gamma_subdivisions"] = [{
        "lo": model.dyadic_json(Fraction(0)),
        "hi": model.dyadic_json(Fraction(1)),
    }]
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R4 malformed global gamma fallback")
    bad = copy.deepcopy(base)
    d = bad["ordered_children"][2]["detail"]
    d["gamma_fallback_used"] = True
    d["gamma_subdivisions"] = []
    rejects(lambda: checker.verify_route_proof(bad, cfg, "H_U"),
            "R4 fallback marker mismatch")

    # J_START 12 binding controls.
    j = jrecord(cfg)
    checker._check_j(j, Fraction(1, 8),
                     model.LAMBDA_PLUS+Fraction(1, 16), cfg)
    for field, label in [
        ("direct_pinned_F_arb_called", "J direct F_arb"),
        ("direct_pinned_dFdr_arb_called", "J direct dFdr_arb"),
    ]:
        b = copy.deepcopy(j)
        b[field] = True
        rejects(lambda b=b: checker._check_j(
            b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg), label)
    b = copy.deepcopy(j)
    b["derivative_record"]["F_r"] = b["derivative_record"]["H_u"]
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "reverse negation")
    rejects(lambda: model.interval_divide_negative_denominator(
        model.interval_json(Fraction(0), Fraction(0)),
        model.interval_json(Fraction(-1), Fraction(1))), "D contains zero")
    b = copy.deepcopy(j)
    b["derivative_record"]["u_interval"] = model.interval_json(
        Fraction(0), Fraction(1, 128))
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "bad r-u map")
    b = copy.deepcopy(j)
    b["ordered_bisection_records"][0]["route_proof"]["normalized_enclosure"] = \
        model.interval_json(Fraction(2), Fraction(2))
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "normalization mismatch")
    b = copy.deepcopy(j)
    b["ordered_bisection_records"][0]["route_proof"] = None
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "sampled enclosure")
    b = copy.deepcopy(j)
    b["ordered_bisection_records"][1]["role"] = "RETAINED_LEFT"
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "contrary bisection update")
    b = copy.deepcopy(j)
    b["r_interval"] = model.interval_json(Fraction(7, 8), Fraction(1))
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "right=1")
    b = copy.deepcopy(j)
    b["newton_record"]["D"] = model.interval_json(Fraction(-1), Fraction(1))
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "Newton zero denominator")
    b = copy.deepcopy(j)
    b["newton_record"]["newton_image"] = b["r_interval"]
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "false self containment")
    b = copy.deepcopy(j)
    b["ordered_bisection_records"][0]["route_proof"]["ordered_children"].pop()
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "missing angular child")
    b = copy.deepcopy(j)
    b["ordered_bisection_records"][2]["route_proof"] = None
    rejects(lambda: checker._check_j(
        b, Fraction(1, 8), model.LAMBDA_PLUS+Fraction(1, 16), cfg),
        "missing Newton midpoint route proof")

    print("BLOCAL_V22_ALL_BINDING_NEGATIVE_CONTROLS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
