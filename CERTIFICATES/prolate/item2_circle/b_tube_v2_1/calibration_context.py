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

sys.path.insert(0, str(BTUBE_ROOT))

from affine_geometry import (  # noqa: E402
    AffinePredictor,
    Q_RULE,
    exact_join_intersection,
    krawczyk_image,
    physical_tube,
)
from numeric_schema import (  # noqa: E402
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

CONFIG_SCHEMA = "btube-calibration-config-v1"
DESIGN_VERSION = "btube-calibration-design-v1"
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
KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
AUDITED_SOURCE_COMMIT = "dbff78474399c47011906631de9cde75992b6d25"
DESIGN_COMMIT = "4a1b12a2a1e4f89712c33bc554646b44190f6f5b"
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
SOURCE_FILE_LIST = ('CALIBRATION_ONLY_WORKFLOW_DESIGN.md', 'affine_geometry.py', 'calibration.py', 'calibration_context.py', 'calibration_config.py', 'calibration_security.py', 'calibration_numeric.py', 'calibration_candidate.py', 'calibration_runner.py', 'calibration_verify.py', 'calibration_delivery.py', 'calibration_receipt.py', 'config.calibration.json', 'numeric_schema.py', 'record_layout_contract.py', 'record_layout_verifier.py', 'requirements-calibration.txt', 'tests/test_calibration.py', 'tests/test_calibration_config.py', 'tests/test_calibration_guards.py', 'tests/test_calibration_records.py', 'tests/test_selftest.py')
EXPECTED_CONFIG_KEYS = {
    "audited_source_commit", "binding_to_final_lambda_start", "blocal_dependency",
    "candidate_lambda_widths", "candidate_tube_radii", "cg_match_dependency",
    "checker_dps", "design_commit", "design_version", "diagnostic_lambda_start", "dps",
    "evaluation_budget", "lambda_end", "max_cells", "max_subdivisions", "mode",
    "predictor_refresh", "production_kernel_sha256", "q_evaluation_rule",
    "record_chain_genesis_domain", "schema",
}
EXPECTED_BLOCAL_KEYS = {
    "artifact_zip_sha256", "certificate_sha256", "config_sha256", "lambda_start",
    "machine_conclusion", "source_head", "status",
}
EXPECTED_CG_KEYS = {
    "artifact_zip_sha256", "b_kernel_sha256", "cg_kernel_sha256", "config_sha256",
    "lambda", "paper_lemma_id", "root_interval", "source_head",
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
