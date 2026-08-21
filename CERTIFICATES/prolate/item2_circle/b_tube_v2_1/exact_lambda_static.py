#!/usr/bin/env python3
"""Static non-contact and prohibited-route gate for exact-lambda transport."""
from __future__ import annotations

from calibration_context import *
from calibration_security import (
    _assert_repo_regular_file,
    assert_routed_boundary_dependency_bytes,
)
from exact_lambda_contract import (
    EXACT_LAMBDA_ADDENDUM_PATH,
    EXACT_LAMBDA_ADDENDUM_SHA256,
    EXACT_LAMBDA_TRANSPORT_PATH,
    EXACT_LAMBDA_TRANSPORT_SHA256,
)

RESULT_BEARING_EXACT_LAMBDA_SOURCES = (
    EXACT_LAMBDA_TRANSPORT_PATH,
    "calibration_runner.py",
    "route_consistency.py",
    "route_consistency_verify.py",
)


def assert_exact_lambda_static_gate() -> dict[str, Any]:
    frozen = assert_routed_boundary_dependency_bytes()
    transport = _assert_repo_regular_file(
        BTUBE_ROOT / EXACT_LAMBDA_TRANSPORT_PATH, REPO_ROOT
    )
    if sha256_hex(transport.read_bytes()) != EXACT_LAMBDA_TRANSPORT_SHA256:
        raise CalibrationError("exact lambda static gate: transport pin mismatch")
    addendum = _assert_repo_regular_file(
        BTUBE_ROOT / EXACT_LAMBDA_ADDENDUM_PATH, REPO_ROOT
    )
    if (
        EXACT_LAMBDA_ADDENDUM_SHA256 != ROUTED_EXACT_LAMBDA_ADDENDUM_SHA256
        or sha256_hex(addendum.read_bytes()) != EXACT_LAMBDA_ADDENDUM_SHA256
    ):
        raise CalibrationError("exact lambda static gate: addendum pin mismatch")
    prohibited = "enclose_" + "f"
    scanned = []
    for relative in RESULT_BEARING_EXACT_LAMBDA_SOURCES:
        path = _assert_repo_regular_file(BTUBE_ROOT / relative, REPO_ROOT)
        source = path.read_text(encoding="utf-8")
        if prohibited in source:
            raise CalibrationError(
                f"exact lambda static gate: prohibited lambda-native F reference: {relative}"
            )
        scanned.append(relative)
    return {
        "addendum_sha256": EXACT_LAMBDA_ADDENDUM_SHA256,
        "frozen_file_count": len(frozen),
        "scanned_sources": scanned,
        "transport_sha256": EXACT_LAMBDA_TRANSPORT_SHA256,
    }


__all__ = [name for name in globals() if not name.startswith("__")]
