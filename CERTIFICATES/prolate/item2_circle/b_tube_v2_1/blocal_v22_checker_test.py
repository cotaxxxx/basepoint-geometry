#!/usr/bin/env python3
"""Calculation-free binding negative controls for B-LOCAL v2.2 finite-route checker."""
from __future__ import annotations

import copy
import heapq
from fractions import Fraction

import blocal_v22_checker as checker
import blocal_v22_boundary as boundary
import blocal_v22_model as model
import blocal_v22_policy as policy
import blocal_v22_runner as runner


def rejects(fn, label: str) -> None:
    try:
        fn()
    except Exception:
        return
    raise RuntimeError(f"negative control accepted: {label}")


def check_j_start_f_routing() -> None:
    """Pin strict-sign initial F versus containment-first midpoint routing."""
    calls = []

    class FakeRoute:
        class EnclosureFailure(Exception):
            pass

        def enclose_f(self, *args):
            required_sign, accept = args[-2:]
            calls.append((required_sign, accept))
            interval = model.interval_json(Fraction(1), Fraction(2))
            if accept is not None:
                original = runner._newton_image
                try:
                    runner._newton_image = lambda *unused: (_ for _ in ()).throw(
                        RuntimeError("Newton must not precede strict sign"))
                    model.need(accept(interval), "strict sign short-circuits Newton")
                finally:
                    runner._newton_image = original
            return interval, {
                "evaluation_count": 1
            }

        def enclose_hu(self, *args):
            accept = args[-1] if callable(args[-1]) else None
            interval = model.interval_json(Fraction(2), Fraction(3))
            if accept is not None:
                model.need(accept(interval), "fake derivative target")
            return interval, {"evaluation_count": 1}

    cfg = config()
    cfg["budgets"]["J_START"]["max_bisections"] = 1
    result, reason, _ = runner._build_j_start(
        0, model.LAMBDA_PLUS + Fraction(1, 1 << 9), Fraction(1, 1 << 8),
        cfg, FakeRoute(), object(), object(), object(), object(), object())
    model.need(result is None and reason == "J_START_MAX_BISECTIONS",
               "fake J_START termination")
    model.need(len(calls) == 2, "fake J_START F call count")
    model.need(calls[0] == ("POS", None), "initial left strict POS route")
    model.need(calls[1][0] is None and callable(calls[1][1]),
               "midpoint containment-first accept route")


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
            "method_selection_addendum": "7fafe5f465f9f38e61831b804a4bc95090af41b8fe31347897e7b2f40bf3d316",
            "c1_floor_spec": "8492755d298ace4c09f5118993eb2f2fa968d55ae5d04b81ff20c2c856fc90d3",
        },
    }


def _gamma_detail() -> dict:
    return {
        "gamma_policy": policy.GAMMA_POLICY_ID,
        "gamma_subdivisions": [{"initial_interval":model.interval_json(0,1),
            "cuts":[model.rational_json(0),model.rational_json(1)],"bin_count":1,"max_bin_depth":0,"use_count":1}],
        "gamma_fallback_used": False,
        "gamma_clamp":"[0,1]","gamma_clamp_fail_closed":True,
        "sqrt_policy": policy.SQRT_POLICY_ID,
        "measure_identity": policy.MEASURE_ID,
    }


def proof(cfg: dict, quantity: str, value: Fraction,
          u0: Fraction, u1: Fraction,
          s0: Fraction, s1: Fraction) -> dict:
    children = []
    for reg in ("T1", "T2", "R2", "C1", "TH"):
        detail = _gamma_detail()
        if reg in ("T1", "T2"):
            detail.update({
                "Z_DEN_LO": model.rational_json(Fraction(1)),
                "helper_lemma_id": "BHAT_LOWER_V2",
                "Duffy_Z_components": {"Ahat_lo":model.rational_json(Fraction(1)),
                    "r_lo2_Bhat_lo":model.rational_json(Fraction(0)),
                    "u0_2_over_rho2_hi":model.rational_json(Fraction(0)),
                    "rho2_hi":model.rational_json(Fraction(1))},
                "effective_floor_record_sha256": [],
                "local_geometry": ["S","U","W","B","q"],
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
                "effective_floor_record_sha256": [],
                "taylor_order": 2,
                "remainder_rule": "diag area*w^2/24 + cross supabs*area*wa*wb/16",
            })
            if reg == "C1":detail["c1_q_floor_source"]="C1_A_W2_B"
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
        "effective_evaluation_cap": cfg["route_policies"]["F_ROUTE" if quantity=="F" else "K_ROUTE"]["max_evaluations"],
        "effective_floor_registry": {"call_sites":list(policy.EFFECTIVE_FLOOR_SITES),"unique_count":0,"total_use_count":0,
            "canonical_sha256":model.sha256_bytes(model.canonical_json_bytes({})),"retained_limit":64,"retained":{},
            "truncated":False,"omitted_count":0,"per_site":{x:{"calls":0,"natural":0,"structural":0} for x in policy.EFFECTIVE_FLOOR_SITES}},
        "method_selection_addendum_sha256":"7fafe5f465f9f38e61831b804a4bc95090af41b8fe31347897e7b2f40bf3d316",
        "c1_floor_spec_sha256":"8492755d298ace4c09f5118993eb2f2fa968d55ae5d04b81ff20c2c856fc90d3",
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


def jrecord_v5(cfg:dict)->dict:
    umax=Fraction(1,8);s=Fraction(1,16);lam=model.LAMBDA_PLUS+s
    left,right=1-umax,Fraction(1);mid=(left+right)/2
    pleft=proof(cfg,"F",Fraction(1),1-left,1-left,s,s)
    pmid=proof(cfg,"F",Fraction(0),1-mid,1-mid,s,s)
    phu_full=proof(cfg,"H_U",Fraction(1),Fraction(0),umax,s,s)
    phu=proof(cfg,"H_U",Fraction(1),1-right,1-left,s,s)
    H=phu["normalized_enclosure"];D=model.interval_negate(H)
    qlo,qhi=model.interval_divide_negative_denominator(pmid["normalized_enclosure"],D)
    q=model.outward_dyadic(qlo,qhi);N=model.outward_dyadic(mid-qhi,mid-qlo)
    nlo,nhi=model.interval_fractions(N)
    initial={"evaluation_id":"J-F-001","r":model.rational_json(left),"lambda_start":model.rational_json(lam),
        "route_id":policy.F_ROUTE_ID,"route_proof":pleft,"normalized_F":pleft["normalized_enclosure"],
        "sign":"POSITIVE","role":"INITIAL_LEFT"}
    mp={"evaluation_id":"J-F-002","r":model.rational_json(mid),"lambda_start":model.rational_json(lam),
        "route_id":policy.F_ROUTE_ID,"route_proof":pmid,"normalized_F":pmid["normalized_enclosure"],
        "sign":"UNRESOLVED","role":"BISECTION_MIDPOINT"}
    target=Fraction(1,10)
    step={"step_index":0,"bracket":model.interval_json(left,right),"midpoint":model.rational_json(mid),
        "coordinate_map":{"u_interval":model.interval_json(1-right,1-left),"u_lo_equals":"1-r_right","u_hi_equals":"1-r_left","exact_rational":True},
        "derivative_lower_target_reached":model.rational_json(target),
        "derivative_target_trials":[{"target":model.rational_json(x),"status":"NOT_REACHED","evaluations":3,"failure_reason":"ANGULAR_EVALUATION_BUDGET"} for x in (Fraction(6,5),Fraction(1),Fraction(1,2),Fraction(1,4))]
            +[{"target":model.rational_json(target),"status":"REACHED","evaluations":phu["evaluation_count"],"failure_reason":None}],
        "derivative_sign_only_fallback":False,"H_u":H,"F_r":D,"derivative_route_proof":phu,
        "endpoint_transform":{"rule":"[H_lo,H_hi] -> [-H_hi,-H_lo]","label_only":False},
        "F_midpoint_record":mp,"strict_sign_certified":False,"sign_required_for_continuation":False,
        "F_stop_reason":"NEWTON_CONTAINMENT","quotient":q,
        "quotient_width":model.rational_json(qhi-qlo),
        "negative_denominator_rule":{"reciprocal_endpoint_rule":"[1/F_r_hi,1/F_r_lo]","midpoint_only":False},
        "newton_image":N,"containment_margins":{"left":model.rational_json(nlo-left),"right":model.rational_json(right-nhi)},
        "strict_self_containment":True}
    fullH=phu_full["normalized_enclosure"]
    full={"record_id":"J-DERIVATIVE-FULL","r_interval":model.interval_json(left,right),
        "u_interval":model.interval_json(0,umax),"H_u":fullH,"F_r":model.interval_negate(fullH),"route_proof":phu_full,
        "endpoint_transform":{"rule":"[H_lo,H_hi] -> [-H_hi,-H_lo]","label_only":False},
        "sup_F_r_lt_zero":True,"zero_not_in_F_r":True}
    dcount=phu_full["evaluation_count"]+4*3+phu["evaluation_count"]
    return {"record_type":"J_START","node":"J_START","candidate_index":0,"lambda_start":model.rational_json(lam),
        "initial_bracket":model.interval_json(left,right),"r_interval":model.interval_json(left,right),
        "ordered_bisection_records":[initial],"condition5_derivative_record":full,"newton_steps":[step],"newton_record":step,
        "evaluation_accounting":{"f_point_outer_evaluations":2,"derivative_evaluations":dcount,
            "outer_budget_counts_only":"f_point_outer_evaluations","derivative_counted_in_outer_budget":False},
        "claim":"J_START_UNIQUE_NONDEGENERATE_ROOT","certified":True,
        "direct_pinned_F_arb_called":False,"direct_pinned_dFdr_arb_called":False}


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
    check_j_start_f_routing()
    base = proof(cfg, "H_U", Fraction(1), Fraction(0), Fraction(1, 8),
                 -model.S_NEG, Fraction(1, 16))
    checker.verify_route_proof(base, cfg, "H_U")
    width_heap=[boundary._WidthEntry(Fraction(1),-policy.REGION_ORDER["R2"],"R20"),
                boundary._WidthEntry(Fraction(1),-policy.REGION_ORDER["T1"],"T10"),
                boundary._WidthEntry(Fraction(1),-policy.REGION_ORDER["T1"],"T11")]
    heapq.heapify(width_heap)
    model.need([heapq.heappop(width_heap).path for _ in range(3)]==["T11","T10","R20"],
               "width heap preserves historical max tie-break")

    # Existing fail-closed and structural controls.
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

    # Method-selection addendum binding controls.
    j = jrecord_v5(cfg)
    checker._check_j(j, Fraction(1, 8),
                     model.LAMBDA_PLUS+Fraction(1, 16), cfg)
    for field,label in (("direct_pinned_F_arb_called","direct F"),
                        ("direct_pinned_dFdr_arb_called","direct derivative")):
        b=copy.deepcopy(j);b[field]=True
        rejects(lambda b=b:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),label)
    b=copy.deepcopy(j);b["condition5_derivative_record"]["F_r"]=b["condition5_derivative_record"]["H_u"]
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"label-only derivative negation")
    b=copy.deepcopy(j);b["newton_steps"][0]["coordinate_map"]["u_interval"]=model.interval_json(0,Fraction(1,128))
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"inexact r-u map")
    b=copy.deepcopy(j);b["newton_steps"][0]["negative_denominator_rule"]["midpoint_only"]=True
    # Exact quotient reconstruction rejects any midpoint-only substitution.
    b["newton_steps"][0]["quotient"]=model.interval_json(0,Fraction(1,128))
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"midpoint-only quotient")
    b=copy.deepcopy(j);b["newton_steps"][0]["derivative_lower_target_reached"]=model.rational_json(Fraction(6,5))
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"theta without verification")
    b=copy.deepcopy(j);b["evaluation_accounting"]["derivative_counted_in_outer_budget"]=True
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"derivative charged to outer")
    b=copy.deepcopy(j);b["newton_steps"][0]["containment_margins"]["left"]=model.rational_json(0)
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"false margin")
    b=copy.deepcopy(j);b["newton_steps"][0]["F_stop_reason"]="STRICT_SIGN"
    rejects(lambda:checker._check_j(b,Fraction(1,8),model.LAMBDA_PLUS+Fraction(1,16),cfg),"containment-first reason")
    b=copy.deepcopy(base);b["effective_floor_registry"]["call_sites"].append("SEVENTH_SITE")
    rejects(lambda:checker.verify_route_proof(b,cfg,"H_U"),"unlisted floor site")
    b=copy.deepcopy(base);b["ordered_children"][0]["detail"]["local_geometry"].remove("q")
    rejects(lambda:checker.verify_route_proof(b,cfg,"H_U"),"old Duffy geometry mixed")
    b=copy.deepcopy(base);b["ordered_children"][2]["detail"]["q_lo"]=model.rational_json(0)
    rejects(lambda:checker.verify_route_proof(b,cfg,"H_U"),"sample-derived zero floor")
    b=copy.deepcopy(base);d=b["ordered_children"][2]["detail"];d["gamma_fallback_used"]=True
    d["gamma_subdivisions"]=[{"initial_interval":model.interval_json(0,1),"cuts":[model.rational_json(0),model.rational_json(1)],"bin_count":1,"max_bin_depth":0,"use_count":1}]
    rejects(lambda:checker.verify_route_proof(b,cfg,"H_U"),"gamma adaptive rule removed")

    print("BLOCAL_V22_ALL_BINDING_NEGATIVE_CONTROLS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
