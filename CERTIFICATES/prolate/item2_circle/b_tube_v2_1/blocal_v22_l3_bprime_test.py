#!/usr/bin/env python3
"""Calculation-free binding negative controls for the L3 Bprime monotonicity checker."""
from __future__ import annotations

import copy
from fractions import Fraction

import blocal_v22_checker as checker
import blocal_v22_checker_test as base_test
import blocal_v22_model as model


def rejects(fn, label: str) -> None:
    try:
        fn()
    except Exception:
        return
    raise RuntimeError(f"L3 negative control accepted: {label}")


def record(cfg: dict, s: Fraction = Fraction(1, 1 << 9)) -> dict:
    lam = model.LAMBDA_PLUS + s
    neg = model.interval_json(Fraction(-1, 4), Fraction(-1, 8))
    return {
        "record_type": "L3_MONOTONICITY",
        "node": "L3",
        "candidate_index": 0,
        "route_id": model.L3_BPRIME_ROUTE_ID,
        "policy_id": model.L3_BPRIME_POLICY_ID,
        "identity_lemma_id": model.L3_BOUNDARY_IDENTITY_ID,
        "inference_id": model.L3_MONOTONICITY_INFERENCE_ID,
        "lambda_plus": model.rational_json(model.LAMBDA_PLUS),
        "s_start": model.rational_json(s),
        "lambda_start": model.rational_json(lam),
        "s_domain": model.interval_json(0, s),
        "stage1_dependency": {
            "source_head": "b0582728d3f8fd3508ba8574a898017212a28caa",
            "artifact_zip_sha256": "ab7112ae7ae570555d1add5c48adb72100562c71aff6b74c94883f58da0f495b",
            "descriptor_sha256": "da7e1554ca29344cd4d781cb3cc48a3581d1e3d36ca3ac7cf837d42fb313e37e",
            "certificate_sha256": "d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188",
            "manifest_sha256": "f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069",
            "bprime_source_sha256": model.STAGE1_BPRIME_SOURCE_SHA256,
            "identity_source_sha256": model.STAGE1_VERIFY_CHANGE_SHA256,
        },
        "stage1_endpoint_evidence": {
            "evaluation_key": "B(206539/100000)",
            "enclosure": model.rational_interval_json(model.STAGE1_BPLUS_LO, model.STAGE1_BPLUS_HI),
            "strict_upper_lt_zero": True,
        },
        "derivative_policy": {k: cfg["l3_bprime_route"][k] for k in (
            "python_flint","dps","bands","rel_tol","eval_limit","depth_limit",
            "max_interval_calls","max_subdivision_depth","subdivision_enabled")},
        "extended_domain_audit": {
            "audit_id": model.L3_BPRIME_DOMAIN_AUDIT_ID,
            "status": "PASS",
            "lambda_domain": model.rational_interval_json(model.LAMBDA_PLUS, lam),
            "lambda_gt_1_exact": True,
            "A_positive_lemma": "A=1+(lambda^2-1)(1-T)q >= 1",
            "W_positive_lemma": "W=lambda^2(1-c2)+c2 >= 1",
            "c2_range_lemma": "c2=4T(1-T)q in [0,1]",
            "x_range_lemma": "W*A-lambda^2*T=(1-T)R; R concave in q; R(0)=D+1; R(1)=(2TD-D-1)^2",
            "angle_data_domain": "0<=x<=1; x=1 handled by pinned hypergeometric branch",
            "identity_id": model.L3_BOUNDARY_IDENTITY_ID,
            "identity_source_sha256": model.STAGE1_VERIFY_CHANGE_SHA256,
            "no_new_singularity_or_branch_crossing": True,
        },
        "inherited_branch_guard_audit": {
            "audit_id": model.L3_BPRIME_BRANCH_GUARD_AUDIT_ID,
            "status": "PASS", "float_call_count": 3,
            "locations": [
                {"function": "_abs_upper", "lineno": 1},
                {"function": "_h_data", "lineno": 2},
                {"function": "_h_data", "lineno": 3},
            ],
            "allowed_functions": ["_abs_upper", "_h_data"],
            "proof_decision_use": False,
        },
        "derivative_proof_domain": model.rational_interval_json(model.LAMBDA_PLUS, lam),
        "derivative_interval_records": [{
            "call_index": 0,
            "lambda_interval": model.rational_interval_json(model.LAMBDA_PLUS, lam),
            "Bprime_enclosure": neg,
            "strict_upper_lt_zero": True,
            "status": "CERTIFIED",
            "failure_reason": None,
        }],
        "final_Bprime_enclosure": neg,
        "Bprime_upper_lt_zero": True,
        "monotonicity_inference_applied": True,
        "boundary_identity_applied": True,
        "direct_F_route_used": False,
        "sampled_or_finite_difference_used": False,
        "float_proof_decision_used": False,
        "final_claim": "H(0,s)<0 on [0,s_start]",
        "certified": True,
        "failure_reason": None,
    }


def main() -> int:
    cfg = base_test.config()
    # Populate the Stage-1 metadata needed by the L3 checker only; model.validate_config
    # intentionally does not duplicate the independent provenance verifier.
    cfg["stage1_dependency"] = {
        "path": "CERTIFICATES/prolate/item2_branch/independent_recheck/certificate_item2_independent.json",
        "source_head": "b0582728d3f8fd3508ba8574a898017212a28caa",
        "certificate_sha256": "d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188",
        "manifest_path": "CERTIFICATES/prolate/item2_branch/independent_recheck/SHA256SUMS.txt",
        "manifest_sha256": "f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069",
        "config_path": "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/config.blocal-stage1.json",
        "config_sha256": "da7e1554ca29344cd4d781cb3cc48a3581d1e3d36ca3ac7cf837d42fb313e37e",
        "artifact_path": "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/dependencies/blocal-stage1-boundary-entry.zip",
        "artifact_zip_sha256": "ab7112ae7ae570555d1add5c48adb72100562c71aff6b74c94883f58da0f495b",
        "certified_statement": "unused by direct L3 unit",
        "machine_conclusion": {}, "scope": "unused", "status": "STAGE1_CONTENT_AUDITED",
    }
    r = record(cfg)
    model.need(checker._check_l3(r, cfg, 0, Fraction(1, 1 << 9)) is True, "baseline L3")

    mutations = []
    b=copy.deepcopy(r);b.pop("stage1_endpoint_evidence");mutations.append((b,"missing endpoint"))
    b=copy.deepcopy(r);b["stage1_endpoint_evidence"]["enclosure"]=model.rational_interval_json(Fraction(-1),Fraction(0));mutations.append((b,"nonnegative endpoint upper"))
    b=copy.deepcopy(r);b["stage1_dependency"]["certificate_sha256"]="0"*64;mutations.append((b,"wrong certificate pin"))
    b=copy.deepcopy(r);b["identity_lemma_id"]="WRONG";mutations.append((b,"wrong identity"))
    b=copy.deepcopy(r);b["extended_domain_audit"]["status"]="FAIL";mutations.append((b,"domain audit fail"))
    b=copy.deepcopy(r);b["derivative_interval_records"][0]["lambda_interval"]=model.rational_interval_json(model.LAMBDA_PLUS+Fraction(1,1000000),model.LAMBDA_PLUS+Fraction(1,1<<9));mutations.append((b,"domain starts late"))
    b=copy.deepcopy(r);b["derivative_interval_records"][0]["lambda_interval"]=model.rational_interval_json(model.LAMBDA_PLUS,model.LAMBDA_PLUS+Fraction(1,1<<10));mutations.append((b,"domain ends early"))
    b=copy.deepcopy(r);b["derivative_interval_records"][0]["Bprime_enclosure"]=model.interval_json(-1,0);b["derivative_interval_records"][0]["strict_upper_lt_zero"]=False;b["derivative_interval_records"][0]["status"]="UNRESOLVED";b["derivative_interval_records"][0]["failure_reason"]="X";mutations.append((b,"Bprime upper nonnegative"))
    b=copy.deepcopy(r);b["derivative_interval_records"]=[];mutations.append((b,"missing derivative leaf"))
    b=copy.deepcopy(r);mid=model.LAMBDA_PLUS+Fraction(1,1<<10);hi=model.LAMBDA_PLUS+Fraction(1,1<<9);leaf=copy.deepcopy(b["derivative_interval_records"][0]);leaf2=copy.deepcopy(leaf);leaf["lambda_interval"]=model.rational_interval_json(model.LAMBDA_PLUS,mid);leaf2["call_index"]=1;leaf2["lambda_interval"]=model.rational_interval_json(mid+Fraction(1,1<<20),hi);b["derivative_interval_records"]=[leaf,leaf2];mutations.append((b,"derivative gap"))
    b=copy.deepcopy(r);b["candidate_index"]=1;mutations.append((b,"candidate mismatch"))
    b=copy.deepcopy(r);b["sampled_or_finite_difference_used"]=True;mutations.append((b,"sampled derivative"))
    b=copy.deepcopy(r);b["stage1_dependency"]["bprime_source_sha256"]="0"*64;mutations.append((b,"wrong Bprime source"))
    b=copy.deepcopy(r);b["inherited_branch_guard_audit"]["float_call_count"]=4;mutations.append((b,"new float path"))
    b=copy.deepcopy(r);b["float_proof_decision_used"]=True;mutations.append((b,"float sign decision"))
    b=copy.deepcopy(r);b["monotonicity_inference_applied"]=False;mutations.append((b,"missing monotonicity"))
    b=copy.deepcopy(r);b["s_domain"]=model.interval_json(Fraction(1,1<<20),Fraction(1,1<<9));mutations.append((b,"s=0 removed"))
    b=copy.deepcopy(r);b["final_claim"]="PASS";mutations.append((b,"direct pass flag"))
    b=copy.deepcopy(r);b["extended_domain_audit"]["identity_source_sha256"]="0"*64;mutations.append((b,"identity provenance"))
    b=copy.deepcopy(r);b["derivative_policy"]["dps"]=19;mutations.append((b,"policy mismatch"))
    b=copy.deepcopy(r);b["boundary_identity_applied"]=False;mutations.append((b,"boundary identity omitted"))

    for bad,label in mutations:
        rejects(lambda bad=bad: checker._check_l3(bad,cfg,0,Fraction(1,1<<9)), label)
    model.need(len(mutations) == 21, "21 binding L3 controls")
    print("L3_BPRIME_BINDING_NEGATIVE_CONTROLS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
