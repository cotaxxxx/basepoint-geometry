#!/usr/bin/env python3
"""Pinned-runtime audit for the Item 3 sweep v9 guarded candidate v2.

This audit is evidence for source/runtime validation only.  It does not authorize
production use, a tag, a workflow verdict, or a certified lambda range.
"""
from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from pathlib import Path
import sys

import flint
from flint import acb, arb


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "prolate_F_derivatives_cleanroom_v9_candidate.py"
REPORT = HERE / "runtime_audit_candidate_v2.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_tuple(values: tuple[acb, ...]) -> bool:
    return all(value.is_finite() for value in values)


def main() -> int:
    before = sha256_file(SOURCE)
    sys.path.insert(0, str(HERE))
    kernel = importlib.import_module("prolate_F_derivatives_cleanroom_v9_candidate")
    after = sha256_file(SOURCE)

    checks: dict[str, bool] = {}
    details: dict[str, object] = {}

    checks["source_hash_stable_across_import"] = before == after
    module_path = Path(inspect.getsourcefile(kernel) or "").resolve()
    checks["imported_module_is_exact_candidate_path"] = module_path == SOURCE.resolve()
    checks["kernel_id_exact"] = kernel.KERNEL_ID == "ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2"

    endpoint = kernel.angle_data_3(acb(1), analytic=True)
    checks["angle_gamma_one_finite"] = finite_tuple(endpoint)
    checks["h1_at_one_contains_minus_two"] = -2 in endpoint[1].real and 0 in endpoint[1].imag
    checks["h2_at_one_contains_two_thirds"] = arb(2) / 3 in endpoint[2].real and 0 in endpoint[2].imag
    checks["h3_at_one_contains_minus_eight_fifteenths"] = -arb(8) / 15 in endpoint[3].real and 0 in endpoint[3].imag

    cut = kernel.angle_data_3(acb(-1), analytic=True)
    checks["gauss_cut_rejected_fail_closed"] = all(not value.is_finite() for value in cut)
    ordinary = kernel.angle_data_3(acb("0.5"), analytic=True)
    checks["ordinary_angle_point_finite"] = finite_tuple(ordinary)

    valid_r = arb("0.03")
    valid_lam = arb("4.72")
    tol = arb("1e-4")
    try:
        kernel._validate_inputs(valid_r, valid_lam, tol, 8, 50000)
        checks["valid_domain_accepted"] = True
    except Exception as exc:  # pragma: no cover - reported explicitly
        checks["valid_domain_accepted"] = False
        details["valid_domain_error"] = repr(exc)

    invalid_cases = [
        (arb(0), valid_lam, "r_zero"),
        (arb(1), valid_lam, "r_one"),
        (valid_r, arb("0.999"), "lambda_below_one"),
    ]
    for r_value, lam_value, label in invalid_cases:
        try:
            kernel._validate_inputs(r_value, lam_value, tol, 8, 50000)
        except ValueError:
            checks[f"invalid_{label}_rejected"] = True
        else:
            checks[f"invalid_{label}_rejected"] = False

    outputs: dict[str, str] = {}
    public = [
        "F_arb",
        "F_r_arb",
        "F_lambda_arb",
        "F_rr_arb",
        "F_rlambda_arb",
    ]
    for name in public:
        try:
            value = getattr(kernel, name)(
                valid_r,
                valid_lam,
                tol="1e-4",
                depth=8,
                limit=50000,
            )
            outputs[name] = str(value)
            checks[f"{name}_finite"] = bool(value.is_finite())
        except Exception as exc:  # fail closed and record exact obstruction
            outputs[name] = f"ERROR:{type(exc).__name__}:{exc}"
            checks[f"{name}_finite"] = False

    details["outputs_at_r_0.03_lambda_4.72"] = outputs
    details["candidate_sha256_before_import"] = before
    details["candidate_sha256_after_import"] = after
    details["python_flint_version"] = getattr(flint, "__version__", "UNKNOWN")
    details["python_version"] = sys.version

    status = "PASSED" if all(checks.values()) else "FAILED"
    report = {
        "schema": "ITEM3_SWEEP_V9_CANDIDATE_V2_RUNTIME_AUDIT_V1",
        "status": status,
        "checks": checks,
        "details": details,
        "nonclaim": "Runtime PASS does not authorize production use or a certified lambda range.",
    }
    REPORT.write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if status == "PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
