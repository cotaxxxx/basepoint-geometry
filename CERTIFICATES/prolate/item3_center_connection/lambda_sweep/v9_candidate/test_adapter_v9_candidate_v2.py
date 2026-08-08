#!/usr/bin/env python3
"""Pinned-runtime controls for the Item 3 v9 adapter candidate v2."""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

from flint import arb, ctx

import adapter_v9_candidate_v2 as a

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
KERNEL_REL = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "prolate_F_derivatives_cleanroom_v9_candidate.py"
)
KERNEL_SHA = "abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76"
REPORT = HERE / "adapter_v9_candidate_v2_runtime_report.json"


def encloses(container: arb, contained: arb) -> bool:
    return bool(container.lower() <= contained.lower() and contained.upper() <= container.upper())


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    adapter = a.V9MeanValueAdapter(
        checkout_root=REPO_ROOT,
        kernel_source_path=KERNEL_REL,
        kernel_source_sha256=KERNEL_SHA,
        tol="1e-8",
        integration_depth=12,
        integration_limit=200000,
    )
    checks["adapter_id_exact"] = adapter.adapter_id == "ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V2"
    checks["kernel_pre_hash_exact"] = adapter.kernel_identity.pre_import_sha256 == KERNEL_SHA
    checks["kernel_post_hash_exact"] = adapter.kernel_identity.post_import_sha256 == KERNEL_SHA
    checks["kernel_origin_exact"] = Path(adapter.kernel_identity.module_origin) == (REPO_ROOT / KERNEL_REL).resolve()

    try:
        a.V9MeanValueAdapter(
            checkout_root=REPO_ROOT,
            kernel_source_path=KERNEL_REL,
            kernel_source_sha256="0" * 64,
        )
    except a.AdapterContractError:
        checks["wrong_kernel_hash_rejected"] = True
    else:
        checks["wrong_kernel_hash_rejected"] = False

    try:
        a.load_pinned_kernel(
            checkout_root=HERE,
            repo_relative_path="../../../../../../../../etc/passwd",
            expected_sha256="0" * 64,
            module_name="escape_attack",
        )
    except a.AdapterContractError:
        checks["path_escape_rejected"] = True
    else:
        checks["path_escape_rejected"] = False

    controls = [
        ("dual_overlap_intersection", arb("1 +/- 0.25"), arb("1.1 +/- 0.25"), "INTERSECTION"),
        ("dual_direct_only", arb(1), arb.nan(), "DIRECT_ONLY"),
        ("dual_factored_only", arb.nan(), arb(1), "FACTORED_ONLY"),
        ("dual_both_nonfinite", arb.nan(), arb.nan(), "NONFINITE"),
    ]
    for label, direct, factored, expected in controls:
        result = a._combine_arb_associations(
            expression_id="TEST", direct_value=direct, factored_value=factored
        )
        checks[label] = result.association_class == expected
    try:
        a._combine_arb_associations(
            expression_id="TEST", direct_value=arb(1), factored_value=arb(2)
        )
    except a.QuotientAssociationDisjoint:
        checks["dual_disjoint_fatal"] = True
    else:
        checks["dual_disjoint_fatal"] = False

    r_cell = (Fraction(1, 64), Fraction(129, 8192))
    lambda_box = (Fraction(123731943, 26214400), Fraction(118, 25))
    rb = a._interval_to_arb(r_cell)
    lb = a._interval_to_arb(lambda_box)
    checks["r_input_contains_lo"] = encloses(rb, a._fraction_to_arb(r_cell[0]))
    checks["r_input_contains_hi"] = encloses(rb, a._fraction_to_arb(r_cell[1]))
    checks["lambda_input_contains_lo"] = encloses(lb, a._fraction_to_arb(lambda_box[0]))
    checks["lambda_input_contains_hi"] = encloses(lb, a._fraction_to_arb(lambda_box[1]))

    initial_dps = ctx.dps
    g_lo = adapter.evaluate_g(
        r_cell=(Fraction(1, 64), Fraction(1, 64)), lambda_box=lambda_box, dps=50
    )
    g_hi = adapter.evaluate_g(
        r_cell=(Fraction(11, 256), Fraction(11, 256)), lambda_box=lambda_box, dps=50
    )
    checks["endpoint_g_lo_strict_positive"] = g_lo.strictly_positive()
    checks["endpoint_g_hi_strict_negative"] = g_hi.strictly_negative()
    checks["ctx_restored_after_endpoint_calls"] = ctx.dps == initial_dps

    evidence = adapter.evaluate_mean_value(r_cell=r_cell, lambda_box=lambda_box, dps=50)
    checks["ctx_restored_after_mean_value"] = ctx.dps == initial_dps
    checks["seven_kernel_calls_per_mean_value"] = evidence.kernel_calls == 7
    checks["canonical_r_center"] = evidence.r0 == (r_cell[0] + r_cell[1]) / 2
    checks["canonical_lambda_center"] = evidence.lambda0 == (lambda_box[0] + lambda_box[1]) / 2
    checks["g_r_center_finite"] = evidence.g_r_center.final.finite
    checks["g_rr_box_finite"] = evidence.g_rr_box.final.finite
    checks["g_rlambda_box_finite"] = evidence.g_rlambda_box.final.finite
    checks["r_score_finite"] = evidence.r_score is not None
    checks["lambda_score_finite"] = evidence.lambda_score is not None
    checks["known_left_cell_strict_NEG"] = evidence.strict_negative

    details["adapter_source_sha256"] = hashlib.sha256(
        (HERE / "adapter_v9_candidate_v2.py").read_bytes()
    ).hexdigest()
    details["kernel_source_sha256"] = KERNEL_SHA
    details["endpoint_g_lo"] = [str(g_lo.lo), str(g_lo.hi)] if g_lo.finite else None
    details["endpoint_g_hi"] = [str(g_hi.lo), str(g_hi.hi)] if g_hi.finite else None
    details["mean_value"] = {
        "lo": str(evidence.mean_value.lo) if evidence.mean_value.finite else None,
        "hi": str(evidence.mean_value.hi) if evidence.mean_value.finite else None,
        "strict_negative": evidence.strict_negative,
        "r_score": str(evidence.r_score) if evidence.r_score is not None else None,
        "lambda_score": str(evidence.lambda_score) if evidence.lambda_score is not None else None,
    }
    details["kernel_call_counts_after_all_controls"] = adapter.kernel_call_counts
    details["python"] = sys.version

    status = "PASSED" if all(checks.values()) else "FAILED"
    report = {
        "schema": "ITEM3_SWEEP_V9_ADAPTER_CANDIDATE_V2_RUNTIME_V1",
        "status": status,
        "checks": checks,
        "details": details,
        "nonclaim": "Adapter-v2 runtime PASS is not production approval or a certified lambda range.",
    }
    REPORT.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
