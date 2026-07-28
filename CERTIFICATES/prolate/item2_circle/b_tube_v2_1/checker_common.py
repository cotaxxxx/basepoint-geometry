#!/usr/bin/env python3
"""Independent fail-closed checker for B-TUBE v2.1 self-test artifacts."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from affine_geometry import (
    Q_RULE,
    AffinePredictor,
    exact_join_intersection,
    krawczyk_image,
    physical_tube,
    shifted,
)
from b_tube_selftest_runner import (
    BLOCAL_MOCK_SHA256,
    CG_ARTIFACT_SHA256,
    CG_CONFIG_SHA256,
    CG_SOURCE_HEAD,
    FG_LEMMA,
    Bundle,
)
import mock_kernel
from mock_kernel import (
    F_interval,
    MOCK_KERNEL_SHA256 as REFERENCE_F_KERNEL_SHA256,
    dFdr_interval,
)
from numeric_schema import (
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    SchemaError,
    canonical_json_bytes,
    chain_genesis,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)

SELFTEST_MOCK_KERNEL_FILE_SHA256 = "94cb10829302dea74741f019915f1d7ae225033f3cd70032c6ea19f1fd844062"


class CheckError(RuntimeError):
    exit_code = 1


class DependencyError(CheckError):
    exit_code = 2


@dataclass(frozen=True)
class CheckResult:
    verdict: str
    cells: int
    joins: int
    chain_tip_sha256: str


def _fail(message: str) -> None:
    raise CheckError(message)


def _dependency_fail(message: str) -> None:
    raise DependencyError(message)


def _check_imported_kernel_file() -> None:
    source = getattr(mock_kernel, "__file__", None)
    if not isinstance(source, str):
        _dependency_fail("imported mock kernel has no source file")
    path = Path(source)
    try:
        actual = sha256_hex(path.read_bytes())
    except OSError as exc:
        _dependency_fail(f"cannot read imported mock kernel bytes: {exc}")
    if actual != SELFTEST_MOCK_KERNEL_FILE_SHA256:
        _dependency_fail("imported mock kernel file SHA256 mismatch")


def _exact_interval_equal(left: DyadicInterval, right: DyadicInterval, where: str) -> None:
    if left != right:
        _fail(f"{where}: exact interval mismatch")


def _saved_contains(saved_obj: Any, actual: DyadicInterval, where: str) -> DyadicInterval:
    saved = DyadicInterval.from_json(saved_obj, where)
    if not saved.contains(actual):
        _fail(f"{where}: saved enclosure does not contain reconstruction")
    return saved


def _rational_equal(obj: Any, expected: Rational, where: str) -> Rational:
    actual = Rational.from_json(obj, where)
    if actual != expected:
        _fail(f"{where}: exact rational mismatch")
    return actual


def _parse_bundle(bundle: Bundle) -> tuple[dict[str, Any], dict[str, Any], list[tuple[dict[str, Any], bytes]], dict[str, Any]]:
    config = parse_canonical_json_bytes(bundle.config_bytes)
    dependencies = parse_canonical_json_bytes(bundle.dependencies_bytes)
    summary = parse_canonical_json_bytes(bundle.summary_bytes)
    records = parse_canonical_jsonl(bundle.records_jsonl)
    if not all(isinstance(value, dict) for value in (config, dependencies, summary)):
        _fail("top-level artifacts must be JSON objects")
    return config, dependencies, records, summary


def _check_config_and_dependencies(config: dict[str, Any], dependencies: dict[str, Any]) -> None:
    _check_imported_kernel_file()
    if config.get("schema") != "btube-selftest-config-v2.1" or config.get("mode") != "SELFTEST_ONLY":
        _fail("unsupported self-test config")
    dps = config.get("dps")
    checker_dps = config.get("checker_dps")
    if not isinstance(dps, int) or isinstance(dps, bool) or dps <= 0:
        _fail("invalid generator dps")
    if not isinstance(checker_dps, int) or isinstance(checker_dps, bool):
        _fail("invalid checker dps")
    if checker_dps < dps:
        _fail("CHECKER PRECISION BELOW GENERATOR PRECISION")
    if config.get("q_evaluation_rule") != Q_RULE:
        _fail("unsupported affine q evaluation rule")
    domain = config.get("chain_genesis_domain")
    if config.get("chain_genesis_sha256") != chain_genesis(domain):
        _fail("chain genesis mismatch")
    cg = config.get("cg_match_dependency")
    if not isinstance(cg, dict):
        _dependency_fail("missing C-G dependency")
    required = {
        "artifact_zip_sha256": CG_ARTIFACT_SHA256,
        "config_sha256": CG_CONFIG_SHA256,
        "source_head": CG_SOURCE_HEAD,
        "b_kernel_sha256": REFERENCE_F_KERNEL_SHA256,
        "cg_kernel_sha256": REFERENCE_F_KERNEL_SHA256,
        "paper_lemma_id": FG_LEMMA,
    }
    for key, expected in required.items():
        if cg.get(key) != expected:
            _dependency_fail(f"C-G dependency pin mismatch: {key}")
    if cg["b_kernel_sha256"] != cg["cg_kernel_sha256"]:
        _dependency_fail("B and C-G kernel SHA mismatch")
    if dependencies.get("cg_match_dependency") != cg:
        _dependency_fail("dependency snapshot differs from config pin")
    lemma_entries = dependencies.get("logical_lemmas")
    if not isinstance(lemma_entries, list):
        _dependency_fail("logical lemma list missing")
    lemma_ids = {entry.get("id") for entry in lemma_entries if isinstance(entry, dict)}
    if FG_LEMMA not in lemma_ids:
        _dependency_fail("F/G identity lemma missing")
    analytic = [entry for entry in lemma_entries if isinstance(entry, dict) and entry.get("id") == "ANALYTIC_IMPLICIT_BRANCH_V1"]
    if not analytic or analytic[0].get("machine_conclusion") is not False:
        _dependency_fail("analyticity must remain paper-only")


def _check_chain(
    config: dict[str, Any],
    records: list[tuple[dict[str, Any], bytes]],
    summary: dict[str, Any],
) -> list[dict[str, Any]]:
    previous = config["chain_genesis_sha256"]
    parsed: list[dict[str, Any]] = []
    for index, (record, raw) in enumerate(records):
        if record.get("record_index") != index:
            _fail("record index discontinuity")
        if record.get("previous_record_sha256") != previous:
            _fail("previous_record_sha256 mismatch")
        if canonical_json_bytes(record) != raw:
            _fail("record byte canonicalization mismatch")
        previous = sha256_hex(raw)
        parsed.append(record)
    if summary.get("record_count") != len(records):
        _fail("summary record count mismatch")
    if summary.get("chain_tip_sha256") != previous:
        _fail("summary chain tip mismatch")
    return parsed


__all__ = [name for name in globals() if not name.startswith("__")]
