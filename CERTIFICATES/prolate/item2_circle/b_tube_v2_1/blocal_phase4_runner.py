#!/usr/bin/env python3
"""Pinned B-LOCAL v2.1 production runner.

This file implements record generation but performs no work at import time.
Execution remains restricted to a separately authorized tag-only workflow.
"""
from __future__ import annotations

import argparse
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import blocal_phase4_engine as engine
import blocal_phase4_model as model
from blocal_phase4_provenance import (
    load_pinned_module,
    repo_file,
    verify_implementation_sources,
    verify_stage1_dependency,
)

DESIGN_COMMIT = "7e16c82132ed273ade7b667e3cbb6edbb18d849b"


def repository_root() -> Path:
    return Path(__file__).resolve(strict=True).parents[4]


def git_head(root: Path) -> str:
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    model.need(len(head) == 40 and all(c in "0123456789abcdef" for c in head),
               "source head format")
    return head


def _candidate_schedule(config: dict[str, Any]) -> list[tuple[Fraction, Fraction]]:
    increments = [model.fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    u_values = [model.fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    return [(increment, u_value) for increment in increments for u_value in u_values]


def _load_adapter(root: Path, config: dict[str, Any]) -> Any:
    pin = {
        "path": config["adapter"]["path"],
        "sha256": config["adapter"]["source_sha256"],
    }
    return load_pinned_module(
        root, pin, "blocal_pinned_arb_adapter",
        ("arb_ball_to_canonical_dyadic_interval",),
        {"ADAPTER_ID": model.ADAPTER_ID},
    )


def _append_candidate(
    records: list[dict[str, Any]], previous: str, candidate_index: int,
    s_start: Fraction, u_max: Fraction, config: dict[str, Any],
    kernel: Any, adapter: Any, arb_type: Any, fmpq_type: Any,
) -> tuple[str, tuple[int, Fraction, Fraction, dict[str, Any]] | None,
           dict[str, int], int]:
    lambda_start = model.LAMBDA_PLUS + s_start
    node_results = {
        "L1": engine.certify_node(
            "L1", candidate_index, u_max, s_start, config,
            lambda u0, u1, s0, s1: engine.evaluate_l1(
                kernel, adapter, arb_type, fmpq_type, config, u0, u1, s0, s1),
            config["kernel"]["sha256"],
        ),
        "L2": engine.certify_node(
            "L2", candidate_index, u_max, s_start, config,
            lambda s0, s1: engine.evaluate_l2(
                kernel, adapter, arb_type, fmpq_type, config, u_max, s0, s1),
            config["kernel"]["sha256"],
        ),
        "L3": engine.certify_node(
            "L3", candidate_index, u_max, s_start, config,
            lambda s0, s1: engine.evaluate_l3_route_a(
                kernel, adapter, arb_type, fmpq_type, config, s0, s1),
            config["kernel"]["sha256"],
        ),
    }
    coverage_counts: dict[str, int] = {}
    evaluations: dict[str, int] = {}
    first_failure: str | None = None
    all_nodes = True
    for node in ("L1", "L2", "L3"):
        leaves, certified, failure, count = node_results[node]
        for leaf in leaves:
            previous = model.append_record(records, previous, leaf)
        coverage_counts[node] = len(leaves)
        evaluations[node] = count
        all_nodes = all_nodes and certified
        first_failure = first_failure or failure

    j_start: dict[str, Any] | None = None
    j_evaluations = 0
    if all_nodes:
        j_start, j_failure, j_evaluations = engine.build_j_start(
            candidate_index, lambda_start, u_max, config,
            kernel, adapter, arb_type, fmpq_type,
        )
        first_failure = first_failure or j_failure
        if j_start is not None:
            previous = model.append_record(records, previous, j_start)
    accepted = all_nodes and j_start is not None
    previous = model.append_record(records, previous, {
        "record_type": "CANDIDATE_SUMMARY",
        "candidate_index": candidate_index,
        "lambda_start": model.rational_json(lambda_start),
        "u_max": model.dyadic_json(u_max),
        "s_start": model.dyadic_json(s_start),
        "coverage_counts": coverage_counts,
        "budgets": config["budgets"],
        "kernel_evaluations": {**evaluations, "J_START": j_evaluations},
        "node_status": {
            node: ("CERTIFIED" if node_results[node][1] else "INCOMPLETE")
            for node in ("L1", "L2", "L3")
        } | {"J_START": "CERTIFIED" if j_start else "NOT_CERTIFIED"},
        "candidate_accepted": accepted,
        "first_failure_reason": None if accepted else (
            first_failure or "CANDIDATE_INCOMPLETE"),
        "budget_exceeded": any(
            failure is not None and "BUDGET" in failure
            for _, _, failure, _ in node_results.values()
        ),
        "unresolved": not accepted,
    })
    selected = (candidate_index, lambda_start, u_max, j_start) if accepted else None
    return previous, selected, coverage_counts, 1 if j_start is not None else 0


def run(config_path: Path, output_directory: Path) -> dict[str, Any]:
    root = repository_root()
    model.need(not config_path.is_absolute(), "config path must be repository-relative")
    config_file = repo_file(root, config_path.as_posix())
    config_raw = config_file.read_bytes()
    config = model.parse_canonical_json(config_raw)
    model.validate_config(config)
    source_head = git_head(root)

    # Independent byte gates precede both dependency installation in CI and
    # the runtime import of python-flint / the mathematical kernel here.
    verify_implementation_sources(root, config["implementation"])
    verify_stage1_dependency(root, config["stage1_dependency"])
    adapter = _load_adapter(root, config)

    from flint import arb, ctx, fmpq  # type: ignore[import-not-found]

    ctx.prec = config["precision"]["bits"]
    kernel = load_pinned_module(
        root, config["kernel"], "blocal_pinned_prolate_circle_F_cleanroom",
        tuple(config["kernel"]["required_api"]),
        {"FORMULA_STATE": config["kernel"]["formula_state"]},
    )

    model.need(not output_directory.exists(), "output directory must not pre-exist")
    output_directory.mkdir(parents=True, mode=0o700)
    model.need(not any(output_directory.iterdir()), "fresh output directory required")

    config_hash = model.sha256_bytes(config_raw)
    previous = model.chain_genesis(config_hash)
    records: list[dict[str, Any]] = []
    previous = model.append_record(records, previous, {
        "record_type": "RUN_HEADER",
        "schema": model.SCHEMA,
        "design_version": model.DESIGN_VERSION,
        "blocal_run_config_sha256": config_hash,
        "source_head": source_head,
        "stage1_dependency": config["stage1_dependency"],
        "kernel_source_sha256": config["kernel"]["sha256"],
        "endpoint_route": config["endpoint_route"],
        "canonicalizer_id": model.CANONICALIZER_ID,
        "adapter_id": model.ADAPTER_ID,
        "adapter_source_sha256": config["adapter"]["source_sha2556"],
        "arb_to_dyadic_adapter_sha256": config["arb_to_dyadic_adapter_sha256"],
        "candidate_schedule": {
            "order": config["candidate_order"],
            "lambda_candidates": config["lambda_candidates"],
            "u_max_candidates": config["u_max_candidates"],
            "candidate_count": 105,
        },
        "precision": config["precision"],
        "budgets": config["budgets"],
        "chain_domain": model.CHAIN_DOMAIN,
        "chain_genesis": model.chain_genesis(config_hash),
    })

    totals = {"L1": 0, "L2": 0, "L3": 0}
    attempted = 0
    j_start_count = 0
    selected: tuple[int, Fraction, Fraction, dict[str, Any]] | None = None
    for candidate_index, (s_start, u_max) in enumerate(_candidate_schedule(config)):
        previous, selected_here, counts, j_count = _append_candidate(
            records, previous, candidate_index, s_start, u_max, config,
            kernel, adapter, arb, fmpq,
        )
        for node in totals:
            totals[node] += counts[node]
        attempted += 1
        j_start_count += j_count
        if selected_here is not None:
            selected = selected_here
            break

    chain_tip_before_summary = previous
    final_chain_tip = model.append_record(records, previous, {
        "record_type": "RUN_SUMMARY",
        "selected_candidate_index": selected[0] if selected else None,
        "lambda_start": model.rational_json(selected[1]) if selected else None,
        "u_max": model.dyadic_json(selected[2]) if selected else None,
        "start_root_interval": selected[3]["r_interval"] if selected else None,
        "exact_counts": {
            "attempted_candidates": attempted,
            "tile_records": sum(totals.values()),
            "j_start_records": j_start_count,
            "candidate_summaries": attempted,
        },
        "dependency_identities": {
            "stage1_artifact_zip_sha256": config["stage1_dependency"]["artifact_zip_sha256"],
            "stage1_config_sha256": config["stage1_dependency"]["config_sha256"],
            "kernel_source_sha256": config["kernel"]["sha256"],
            "adapter_source_sha256": config["adapter"]["source_sha256"],
            "blocal_run_config_sha256": config_hash,
            "source_head": source_head,
        },
        "records_chain_tip_before_summary_sha256": chain_tip_before_summary,
        "terminal_state": model.COMPLETE if selected else model.INCOMPLETE,
    })

    conclusion = model.machine_conclusion(selected)
    certificate = {
        "schema": model.CERTIFICATE_SCHEMA,
        "design_version": model.DESIGN_VERSION,
        "status": model.COMPLETE if selected else model.INCOMPLETE,
        "source_head": source_head,
        "design_commit": DESIGN_COMMIT,
        "blocal_run_config_sha256": config_hash,
        "stage1_dependency": config["stage1_dependency"],
        "kernel_source_sha256": config["kernel"]["sha256"],
        "endpoint_route": config["endpoint_route"],
        "arb_to_dyadic_adapter_sha256": config["adapter"]["source_sha256"],
        "candidate_schedule": {
            "order": config["candidate_order"],
            "lambda_candidates": config["lambda_candidates"],
            "u_max_candidates": config["u_max_candidates"],
        },
        "selected_candidate_index": selected[0] if selected else None,
        "lambda_start": model.rational_json(selected[1]) if selected else None,
        "u_max": model.dyadic_json(selected[2]) if selected else None,
        "s_neg": config["s_neg"],
        "s_start": model.dyadic_json(selected[1] - model.LAMBDA_PLUS) if selected else None,
        "nodes": {
            "L1": "MACHINE_CERTIFIED" if selected else "INCOMPLETE",
            "L2": "MACHINE_CERTIFIED" if selected else "INCOMPLETE",
            "L3": "MACHINE_CERTIFIED_ROUTE_A" if selected else "INCOMPLETE",
            "L4": "LOGICAL_LEMMA_NOT_MACHINE_VERIFIED" if selected else "INCOMPLETE",
            "J_START": "MACHINE_CERTIFIED" if selected else "INCOMPLETE",
        },
        "j_start": selected[3] if selected else None,
        "counts": {"records": len(records), **totals},
        "budgets": config["budgets"],
        "chain_genesis": model.chain_genesis(config_hash),
        "chain_tip": final_chain_tip,
        "machine_conclusion": conclusion,
        "logical_lemmas": model.logical_lemmas(),
        "scope": (
            "B-LOCAL/B-ENTRY only. Later B-TUBE calibration and production "
            "certification remain separate and unauthorized."
        ),
        "real_analytic": False,
        "certificate_sha256": None,
        "artifact_zip_sha256": None,
    }
    certificate_raw = model.canonical_json_bytes(certificate)
    records_raw = b"\n".join(Model.canonical_json_bytes(record) for record in records)
    summary = {
        "schema": "blocal-run-summary-v1",
        "terminal_state": model.COMPLETE if selected else model.INCOMPLETE,
        "blocal_run_config_sha256": config_hash,
        "source_head": source_head,
        "records_sha256": model.sha256_bytes(records_raw),
        "certificate_sha256": model.sha256_bytes(certificate_raw),
        "artifact_zip_sha256": None,
        "calibration_started": False,
        "tag_created": False,
    }
    outputs = config["outputs"]
    (output_directory / outputs["records"]).write_bytes(records_raw)
    (output_directory / outputs["certificate"]).write_bytes(certificate_raw)
    (output_directory / outputs["summary"]).write_bytes(
        model.canonical_json_bytes(summary))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="B-LOCAL v2.1 pinned runner")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    arguments = parser.parse_args(argv)
    summary = run(arguments.config, arguments.output_dir)
    print(model.canonical_json_bytes(summary).decode("ascii"))
    return 0 if summary["terminal_state"] == model.COMPLETE else 2


if __name__ == "__main__":
    raise SystemExit(main())
