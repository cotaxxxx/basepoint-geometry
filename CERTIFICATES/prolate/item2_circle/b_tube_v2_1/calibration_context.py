#!/usr/bin/env python3
"""Shared constants and exact types for B-TUBE v2.1 calibration."""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import tokenize
from typing import Any, Iterable
import zipfile

HERE = Path(__file__).resolve().parent
BTUBE_ROOT = HERE
REPO_ROOT = HERE.parents[3]
VENDOR_DIR = REPO_ROOT / "CERTIFICATES/prolate/item2_circle/vendor"
WORKFLOW_PATH = REPO_ROOT / ".github/workflows/prolate-item2-btube-v2-1-calibration.yml"
CONFIG_PATH = HERE / "config.calibration.json"
KERNEL_RELATIVE = Path("CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py")
A0_CERTIFICATE_PATH = HERE / "A0_BOUNDARY_DISTANCE_CERTIFICATE.json"
ROUTED_DESIGN_PATH = HERE / "ROUTED_EVALUATOR_DESIGN_V1.md"
ROUTE_CONSISTENCY_PATH = HERE / "ROUTE_CONSISTENCY_CERTIFICATE.json"
ROUTED_TRACE_NAME = "ROUTED_EVALUATION_TRACE.jsonl"
ROUTED_MANIFEST_NAME = "ROUTED_EVALUATOR_MANIFEST.json"
ROUTED_BOUNDARY_DIR = HERE / "dependencies/blocal_v22_source"
ROUTED_BOUNDARY_CONFIG_PATH = ROUTED_BOUNDARY_DIR / "config.blocal-v2.2-run.json"

sys.path.insert(0, str(BTUBE_ROOT))

from affine_geometry import (  # noqa: E402
    AffinePredictor,
    Q_RULE,
    exact_join_intersection,
    krawczyk_image,
    physical_tube,
    shifted,
)
from numeric_schema import (  # noqa: E402
    D_ONE,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    SchemaError,
    arb_ball_to_exact_interval,
    canonical_json_bytes,
    canonical_jsonl,
    chain_genesis,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)

CALIBRATION_MODE = "DIAGNOSTIC_ONLY"
BINDING_MODE = "BINDING"
BLOCAL_UNPINNED_STATUS = "UNPINNED"
BLOCAL_PINNED_STATUS = "PINNED"
BLOCAL_STATUS = BLOCAL_PINNED_STATUS
BLOCAL_STAGE1_UPPER = Rational(206539, 100000)
BLOCAL_ARTIFACT_SHA256 = "7c1748148470426648dd03a483a076b043ed70558258358834671451267e64dc"
BLOCAL_CERTIFICATE_SHA256 = "b8d27c01d63f3ea53bfeb165f7e140d739fab6b3949115e0aac3fd64b2d05cb6"
BLOCAL_CONFIG_SHA256 = "dab371fa62ed10a00029cd31b0002e503952277ef072fb8f5d7fd5222965d469"
BLOCAL_SOURCE_HEAD = "a8997d11850dbd5b63e3064560a1c311e5c9c267"
BLOCAL_LAMBDA_START = Rational(3307749, 1600000)
BLOCAL_MACHINE_CONCLUSION = {
    "all_F_Fr_consumers_finite_routes": True,
    "all_required_consumers_authorized_routes": True,
    "l3_boundary_monotonicity_route": True,
    "lambda_start": {"p": "3307749", "q": "1600000"},
    "schema": "btube-blocal-machine-conclusion-v2-finite-routes",
    "selected_candidate_index": 0,
    "start_root_interval": {
        "hi": {"e": 0, "m": "1"},
        "lo": {"e": 11, "m": "2047"},
    },
    "status": "BLOCAL_COMPLETE",
    "u_max": {"e": 8, "m": "1"},
}
A0_SCHEMA = "btube-a0-boundary-distance-v1"
A0_STATUS = "A0_CERTIFIED"
A0_OPERATIONAL_ROOT = DyadicInterval(Dyadic(2047, 11), Dyadic(8191, 13))
A0_DELTA_FLOOR = Dyadic(1, 13)
A0_DELTA_CEILING = Dyadic(1, 11)
ADAPTIVE_SIGMA = Dyadic(1, 1)
ADAPTIVE_RADIUS_RULE = "exact_dyadic_min_boundary_margin_v1"
ANCHOR_MODE = "BLOCAL_A0_FORWARD_V1"
KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
CG_ARTIFACT_SHA256 = "c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381"
CG_SOURCE_HEAD = "1e0f671c91798b9c044c04c7a4224a21e1e67830"
CG_CONFIG_SHA256 = "bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17"
CG_LEMMA = "F_G_FIXED_SLICE_IDENTITY_V1"
CG_LAMBDA = Rational(118, 25)
CG_ROOT = (Rational(1, 64), Rational(11, 256))
CHAIN_DOMAIN = "B-TUBE-CALIBRATION-RECORD-CHAIN-v1"
TERMINAL_STATES = {"CALIBRATION_COMPLETE", "CALIBRATION_INCOMPLETE", "CALIBRATION_FAILED"}
FORBIDDEN_RESULT_PREFIX = "CERT" + "IFIED_"
FORBIDDEN_RESULT_KEYS = {"verdict", "certified", "production_match"}

ROUTED_CONTRACT_ID = "EXACT_DOMAIN_ROUTED_DUAL_SUPPLY_V1"
ROUTED_INTERIOR_ROUTE_ID = "INTERIOR_CLEANROOM_V1"
ROUTED_BOUNDARY_ROUTE_ID = "BOUNDARY_BLOCAL_FINITE_V1"
ROUTED_STRADDLE_ROUTE_ID = "EXACT_SPLIT_HULL_V1"
ROUTED_SELECTOR = Dyadic(3, 2)
ROUTED_F_ROUTE_ID = "BLOCAL_F_ROUTE_V2"
ROUTED_HU_ROUTE_ID = "BLOCAL_K_ROUTE_V2"
ROUTED_NEGATION_RULE_ID = "BLOCAL_INTERVAL_NEGATION_V1"
ROUTED_BOUNDARY_ROUTE_CALL_CAP = 24000
ROUTED_TRACE_SCHEMA = "btube-routed-evaluation-trace-v1"
ROUTED_MANIFEST_SCHEMA = "btube-routed-evaluator-manifest-v1"
ROUTE_CONSISTENCY_SCHEMA = "btube-route-consistency-certificate-v1"
ROUTE_CONSISTENCY_GRID_ID = "R48_63_OVER_64_X_L6_V1"
ROUTE_CONSISTENCY_TOL = "1e-12"
ROUTE_CONSISTENCY_DEPTH = 12
ROUTE_CONSISTENCY_LIMIT = 200000
ROUTED_DESIGN_COMMIT = "cae2bcb08afc49be63002ae26f9b00e14bbcacf2"
ROUTED_BOUNDARY_CONFIG_SHA256 = BLOCAL_CONFIG_SHA256
ROUTED_BOUNDARY_SOURCE_HEAD = BLOCAL_SOURCE_HEAD
ROUTED_BOUNDARY_FILE_SHA256 = {
    "blocal_arb_adapter.py": "99e640fba88cfe353ea360190a03df7a9de8840637922f9f56fa6b7168d94e66",
    "blocal_phase4_model.py": "92bc9010cbaf7e3c61a79aa6bb05e2f717a99486e1faac416e0f3dd3ee5f327a",
    "blocal_v22_boundary.py": "aea768c02644fdb08c8c32455207efe7424c7dc34efe378ad545c3ab9418abf9",
    "blocal_v22_model.py": "8e9bcb0d9519cd6feb2375486985dddde43735dcb327cded28e96a33c61acb16",
    "blocal_v22_policy.py": "d8bac8535f5146f22906e8cdc604640edd909709998a41d7f377c9802ca7cc65",
    "blocal_v22_symbolic_audit.py": "b75ce97c8ff1342c6472a744cf2b64bf3413a3112190a5ff6fed73f60b40d0a1",
}
ROUTED_BOUNDARY_DEPENDENCY_FILES = frozenset(
    f"dependencies/blocal_v22_source/{name}" for name in ROUTED_BOUNDARY_FILE_SHA256
)

SOURCE_FILE_LIST = (
    "ADAPTIVE_TUBE_DESIGN_V1.md",
    "ROUTED_EVALUATOR_DESIGN_V1.md",
    "A0_BOUNDARY_DISTANCE_CERTIFICATE.json",
    "a0_boundary_distance.py",
    "a0_boundary_distance_verify.py",
    "a0b_start_anchor.py",
    "a0b_start_anchor_verify.py",
    "CALIBRATION_ONLY_WORKFLOW_DESIGN.md",
    "affine_geometry.py",
    "calibration.py",
    "calibration_context.py",
    "calibration_config.py",
    "calibration_security.py",
    "calibration_numeric.py",
    "calibration_candidate.py",
    "calibration_runner.py",
    "calibration_verify.py",
    "calibration_delivery.py",
    "calibration_receipt.py",
    "config.calibration.json",
    "numeric_schema.py",
    "record_layout_contract.py",
    "record_layout_verifier.py",
    "routed_evaluator.py",
    "routed_record_verifier.py",
    "route_consistency.py",
    "route_consistency_verify.py",
    "requirements-calibration.txt",
    "dependencies/blocal_v22_source/blocal_arb_adapter.py",
    "dependencies/blocal_v22_source/blocal_phase4_model.py",
    "dependencies/blocal_v22_source/blocal_v22_boundary.py",
    "dependencies/blocal_v22_source/blocal_v22_model.py",
    "dependencies/blocal_v22_source/blocal_v22_policy.py",
    "dependencies/blocal_v22_source/blocal_v22_symbolic_audit.py",
    "dependencies/blocal_v22_source/config.blocal-v2.2-run.json",
    "tests/test_a0_boundary_distance.py",
    "tests/test_a0b_start_anchor.py",
    "tests/test_adaptive_a1.py",
    "tests/test_calibration.py",
    "tests/test_calibration_config.py",
    "tests/test_calibration_guards.py",
    "tests/test_calibration_records.py",
    "tests/test_routed_evaluator.py",
    "tests/test_routed_verifier_independence.py",
    "tests/test_selftest.py",
)
EXPECTED_CONFIG_KEYS = {
    "adaptive_safety_factor", "audited_source_commit", "binding_to_final_lambda_start",
    "blocal_dependency", "boundary_route_evaluation_budget",
    "candidate_lambda_widths", "candidate_tube_radii",
    "cg_match_dependency", "checker_dps", "design_commit", "design_version",
    "diagnostic_lambda_start", "dps", "evaluation_budget", "lambda_end",
    "max_cells", "max_subdivisions", "mode", "predictor_refresh",
    "production_kernel_sha256", "q_evaluation_rule", "record_chain_genesis_domain",
    "route_consistency_certificate_sha256", "routed_evaluator_contract", "schema",
}
EXPECTED_BLOCAL_KEYS = {
    "artifact_zip_sha256", "certificate_sha256", "config_sha256", "lambda_start",
    "machine_conclusion", "source_head", "status",
}
EXPECTED_CG_KEYS = {
    "artifact_zip_sha256", "b_kernel_sha256", "cg_kernel_sha256", "config_sha256",
    "lambda", "paper_lemma_id", "root_interval", "source_head",
}
EXPECTED_ROUTED_CONTRACT_KEYS = {
    "boundary_adapter_sha256", "boundary_config_sha256", "boundary_model_sha256",
    "boundary_phase4_model_sha256", "boundary_policy_sha256", "boundary_route_id",
    "boundary_source_sha256", "boundary_symbolic_audit_sha256", "contract_id",
    "derivative_route_id", "interior_kernel_sha256", "interior_route_id",
    "negation_rule_id", "selector_r", "straddle_route_id",
}

class CalibrationError(RuntimeError):
    pass


def _require_exact_keys(obj: Any, expected: set[str], where: str) -> dict[str, Any]:
    if not isinstance(obj, dict) or set(obj) != expected:
        raise CalibrationError(f"{where}: exact key set required")
    return obj


def _positive_int(value: Any, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise CalibrationError(f"{where}: positive integer required")
    return value


def _dyadic_list(value: Any, where: str) -> list[Dyadic]:
    if not isinstance(value, list) or not value:
        raise CalibrationError(f"{where}: nonempty list required")
    items = [Dyadic.from_json(item, f"{where}[{index}]") for index, item in enumerate(value)]
    if any(item <= D_ZERO for item in items):
        raise CalibrationError(f"{where}: values must be positive")
    if len(set(items)) != len(items):
        raise CalibrationError(f"{where}: duplicate candidate")
    if any(not items[index + 1] < items[index] for index in range(len(items) - 1)):
        raise CalibrationError(f"{where}: candidates must be strictly decreasing")
    return items


__all__ = [name for name in globals() if not name.startswith("__")]
