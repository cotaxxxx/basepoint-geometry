#!/usr/bin/env python3
"""Pinned-runtime controls for adapter_v9_candidate.

The test produces a machine-readable report but authorizes no production source or
certificate.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

from flint import arb, ctx

import adapter_v9_candidate as a


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]
KERNEL_REL = (
    "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/"
    "prolate_F_derivatives_cleanroom_v9_candidate.py"
)
KERNEL_SHA = "abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76"
REPORT = HERE / "adapter_v9_candidate_runtime_report.json"


def record_check(checks: dict[str, bool], name: str, value: bool) -> None:
    checks[name] = bool(value)


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
    record_check(checks, "adapter_id_exact", adapter.adapter_id == a.ADAPTER_ID)
    record_check(checks, "kernel_pre_hash_exact", adapter.kernel_identity.pre_import_sha256 == KERNEL_SHA)
    record_check(checks, "kernel_post_hash_exact", adapter.kernel_identity.post_import_sha256 == KERNEL_SHA)
    record_check(checks, "kernel_origin_exact", Path(adapter.kernel_identity.module_origin) == (REPO_ROOT / KERNEL_REL).resolve())

    try:
        a.V9MeanValueAdapter(
            checkout_root=REPO_ROOT,
            kernel_source_path=KERNEL_REL,
            kernel_source_sha256="0" * 64,
        )
    except a.AdapterContractError:
        record_check(checks, "wrong_kernel_hash_rejected", True)
    else:
        record_check(checks, "wrong_kernel_hash_rejected", False)

    try:
        a.load_pinned_kernel(
            checkout_root=HERE,
            repo_relative_path="../../../../../../../../etc/passwd",
            expected_sha256="0" * 64,
            module_name="escape_attack",
        )
    except a.AdapterContractError:
        record_check(checks, "path_escape_rejected", True)
    else:
        record_check(checks, "path_escape_rejected", False)

    # Dual-association control classes independent of the expensive kernel.
    inter = a._combine_arb_associations(
        expression_id="TEST",
        direct_value=arb("1 +/- 0.25"),
        factored_value=arb("1.1 +/- 0.25"),
    )
    record_check(checks, "dual_overlap_intersection", inter.association_class == "INTERSECTION" and inter.final.finite)

    direct_only = a._combine_arb_associations(
        expression_id="TEST",
        direct_value=arb(1),
        factored_value=arb.nan(),
    )
    record_check(checks, "dual_direct_only", direct_only.association_class == "DIRECT_ONLY" and direct_only.final.finite)

    factored_only = a._combine_arb_associations(
        expression_id="TEST",
        direct_value=arb.nan(),
        factored_value=arb(1),
    )
    record_check(checks, "dual_factored_only", factored_only.association_class == "FACTORED_ONLY" and factored_only.final.finite)

    neither = a._combine_arb_associations(
        expression_id="TEST",
        direct_value=arb.nan(),
        factored_value=arb.nan(),
    )
    record_check(checks, "dual_both_nonfinite", neither.association_class == "NONFINITE" and not neither.final.finite)

    try:
        a._combine_arb_associations(
            expression_id="TEST",
            direct_value=arb(1),
            factored_value=arb(2),
        )
    except a.QuotientAssociationDisjoint:
        record_check(checks, "dual_disjoint_fatal", True)
    else:
        record_check(checks, "dual_disjoint_fatal", False)

    exact_box = (Fraction(1, 64), Fraction(129, 8192))
    lambda_box = (
        Fraction(123731943, 26214400),
        Fraction(118, 25),
    )

    # Constructor inclusion control.
    rb = a._interval_to_arb(exact_box)
    record_check(checks, "r_input_contains_lo", a._fraction_to_arb(exact_box[0]) in rb)
    record_check(checks, "r_input_contains_hi", a._fraction_to_arb(exact_box[1]) in rb)
    lb = a._interval_to_arb(lambda_box)
    record_check(checks, "lambda_input_contains_lo", a._fraction_to_arb(lambda_box[0]) in lb)
    record_check(checks, "lambda_input_contains_hi", a._fraction_to_arb(lambda_box[1]) in lb)

    old_dps = ctx.dps
    evidence = adapter.evaluate_mean_value(r_cell=exact_box, lambda_box=lambda_box, dps=50)
    record_check(checks, "ctx_dps_restored", ctx.dps == old_dps)
    record_check(checks, "seven_kernel_calls", evidence.kernel_calls == 7)
    record_check(checks, "canonical_r_center", evidence.r0 == (exact_box[0] + exact_box[1]) / 2)
    record_check(checks, "canonical_lambda_center", evidence.lambda0 == (lambda_box[0] + lambda_box[1]) / 2)
    record_check(checks, "g_r_center_finite", evidence.g_r_center.final.finite)
    record_check(checks, "g_rr_box_finite", evidence.g_rr_box.final.finite)
    record_check(checks, "g_rlambda_box_finite", evidence.g_rlambda_box.final.finite)
    record_check(checks, "r_score_finite", evidence.r_score is not None)
    record_check(checks, "lambda_score_finite", evidence.lambda_score is not None)
    record_check(checks, "known_left_cell_strict_NEG", evidence.strict_negative)

    details["source_identity"] = {
        "resolved_path": adapter.kernel_identity.resolved_path,
        "pre_import_sha256": adapter.kernel_identity.pre_import_sha256,
        "post_import_sha256": adapter.kernel_identity.post_import_sha256,
        "module_origin": adapter.kernel_identity.module_origin,
        "kernel_id": adapter.kernel_identity.kernel_id,
    }
    details["r_cell"] = [str(exact_box[0]), str(exact_box[1])]
    details["lambda_box"] = [str(lambda_box[0]), str(lambda_box[1])]
    details["mean_value"] = {
        "lo": str(evidence.mean_value.lo) if evidence.mean_value.finite else None,
        "hi": str(evidence.mean_value.hi) if evidence.mean_value.finite else None,
        "strict_negative": evidence.strict_negative,
        "r_score": str(evidence.r_score) if evidence.r_score is not None else None,
        "lambda_score": str(evidence.lambda_score) if evidence.lambda_score is not None else None,
        "g_r_association": evidence.g_r_center.association_class,
        "g_rr_association": evidence.g_rr_box.association_class,
        "g_rlambda_association": evidence.g_rlambda_box.association_class,
    }
    details["kernel_call_counts"] = adapter.kernel_call_counts
    details["adapter_source_sha256"] = hashlib.sha256((HERE / "adapter_v9_candidate.py").read_bytes()).hexdigest()
    details["python"] = sys.version

    status = "PASSED" if all(checks.values()) else "FAILED"
    report = {
        "schema": "ITEM3_SWEEP_V9_ADAPTER_CANDIDATE_RUNTIME_V1",
        "status": status,
        "checks": checks,
        "details": details,
        "nonclaim": "Adapter runtime PASS is not production approval or a certified lambda range.",
    }
    REPORT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
