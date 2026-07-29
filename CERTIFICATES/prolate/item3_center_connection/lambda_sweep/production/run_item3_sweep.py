#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PHASE3 = REPO / "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/phase3_impl"
if str(PHASE3) not in sys.path:
    sys.path.insert(0, str(PHASE3))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from verify_pilot_artifact import canonical_json_bytes, verify_artifact
from item3_sweep.attempts import AttemptStructuralContext, CertifiedAttemptEvaluator
from item3_sweep.budget import EvaluationBudget
from item3_sweep.canonical import CanonicalDyadic, CanonicalRational, parse_canonical_json, sha256_hex
from item3_sweep.chain import chain_genesis, chain_record
from item3_sweep.checker import SweepChecker
from item3_sweep.enums import CheckerTerminalClass, RunnerTerminalClass
from item3_sweep.frontier import FrontierMachine, LambdaBox
from item3_sweep.preflight import PreflightVerifier
from item3_sweep.provenance import PinnedSourceLoader, SourcePin
from item3_sweep.runner import RunnerResult, SweepRunner
from item3_sweep.verifier import ArtifactVerifier
from item3_sweep.windows import PredictorPoint

DESIGN_BLOB = "cafbf7b661911995008dda49bfb3ecabcecb1f12"


def rational_object(value: Fraction) -> dict[str, str]:
    return CanonicalRational(value).to_object()


def dyadic_object(value: Fraction) -> dict[str, Any]:
    return CanonicalDyadic(value).to_object()


def interval_object(value: Any) -> dict[str, Any]:
    return value.to_object()


def record_object(record: Any) -> dict[str, Any]:
    return {"payload": record.payload, "record_type": record.record_type.value}


def serialize_record_chain(result: RunnerResult, config_sha256: str) -> tuple[bytes, str]:
    previous = chain_genesis(config_sha256)
    lines: list[bytes] = []
    for record in result.records:
        body = record_object(record)
        chained = {**body, "previous_record_sha256": previous}
        current = chain_record(previous, chained)
        line = canonical_json_bytes(chained)
        lines.append(line)
        previous = current
    return b"\n".join(lines), previous


def evidence_object(evaluator: CertifiedAttemptEvaluator) -> dict[str, Any]:
    items = []
    for (box_id, stage), evidence in sorted(
        evaluator.evidence.items(), key=lambda item: (item[0][0], item[0][1].value)
    ):
        items.append({
            "anchor_icg_contained": evidence.anchor_icg_contained,
            "attempt_stage": stage.value,
            "box_id": box_id,
            "derivative_intervals": [interval_object(value) for value in evidence.derivative_intervals],
            "overlap_width": rational_object(evidence.overlap_width),
            "r_tile": {
                "accepted_leaves": [
                    {"lo": dyadic_object(cell.lo), "hi": dyadic_object(cell.hi)}
                    for cell in evidence.r_tile.accepted_leaves
                ],
                "partition_leaf_count": evidence.r_tile.partition_leaf_count,
                "split_count": evidence.r_tile.split_count,
            },
            "s1": interval_object(evidence.s1),
            "s2": interval_object(evidence.s2),
            "window": [dyadic_object(evidence.window[0]), dyadic_object(evidence.window[1])],
        })
    return {"attempt_evidence": items, "schema": "ITEM3_SWEEP_EVIDENCE_V1"}


class FreshEvidenceEvaluator:
    def __init__(
        self,
        *,
        original: CertifiedAttemptEvaluator,
        adapter: Any,
        checker_dps: int,
    ) -> None:
        self.original = original
        self.adapter = adapter
        self.checker_dps = checker_dps

    def _evidence_for(self, box: LambdaBox):
        candidates = [
            evidence for (box_id, _), evidence in self.original.evidence.items()
            if box_id == box.box_id
        ]
        if len(candidates) != 1:
            return None
        return candidates[0]

    def verify_box(self, box: LambdaBox) -> bool:
        evidence = self._evidence_for(box)
        if evidence is None:
            return False
        lambda_box = (box.lo, box.hi)
        if not self.adapter.evaluate_g(
            r=(evidence.window[0], evidence.window[0]),
            lambda_box=lambda_box,
            dps=self.checker_dps,
        ).strictly_positive():
            return False
        if not self.adapter.evaluate_g(
            r=(evidence.window[1], evidence.window[1]),
            lambda_box=lambda_box,
            dps=self.checker_dps,
        ).strictly_negative():
            return False
        return all(
            self.adapter.evaluate_gr(
                r=(cell.lo, cell.hi),
                lambda_box=lambda_box,
                dps=self.checker_dps,
            ).strictly_negative()
            for cell in evidence.r_tile.accepted_leaves
        )


def write_json(path: Path, value: object) -> str:
    raw = canonical_json_bytes(value)
    path.write_bytes(raw)
    return sha256_hex(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--config-sha256", type=Path, required=True)
    parser.add_argument("--pilot-artifact-zip", type=Path, required=True)
    parser.add_argument("--pilot-artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = args.output
    if output.exists():
        raise RuntimeError("output path must not preexist")
    output.mkdir(parents=True)

    config_bytes = args.config.read_bytes()
    config_sha = args.config_sha256.read_text(encoding="ascii").strip()
    if hashlib.sha256(config_bytes).hexdigest() != config_sha:
        raise RuntimeError("config file SHA-256 mismatch")
    config_obj = parse_canonical_json(config_bytes)

    pilot_evidence = verify_artifact(
        zip_path=args.pilot_artifact_zip,
        extracted_dir=args.pilot_artifact_dir,
    )
    if pilot_evidence.pilot_source_sha256 != config_obj["cg_pilot_source_sha256"]:
        raise RuntimeError("artifact-rederived pilot source SHA-256 does not equal config")
    pilot_report_sha = write_json(output / "PILOT_ARTIFACT_REDERIVATION.json", pilot_evidence.to_object())

    receipt_bytes = (REPO / config_obj["cg_pilot_receipt_path"]).read_bytes()
    snapshot_bytes = (REPO / config_obj["dependency_snapshot_path"]).read_bytes()
    preflight = PreflightVerifier(
        checkout_root=REPO,
        expected_design_blob_sha1=DESIGN_BLOB,
    ).verify(
        config_bytes=config_bytes,
        stored_config_sha256=config_sha,
        receipt_bytes=receipt_bytes,
        snapshot_bytes=snapshot_bytes,
    )
    cfg = preflight.config

    adapter_module, adapter_source_identity = PinnedSourceLoader(REPO).load_module(
        "item3_sweep_production_adapter",
        SourcePin(cfg.raw["adapter_source_path"], cfg.raw["adapter_sha256"]),
    )
    adapter_class = getattr(adapter_module, "ProductionArbAdapter", None)
    if adapter_class is None or getattr(adapter_class, "adapter_id", None) != cfg.raw["adapter_id"]:
        raise RuntimeError("pinned production adapter class/ID mismatch")
    adapter_kwargs = {
        "checkout_root": REPO,
        "kernel_source_path": cfg.raw["kernel_source_path"],
        "kernel_source_sha256": cfg.raw["kernel_source_sha256"],
    }
    runner_adapter = adapter_class(**adapter_kwargs)
    checker_adapter = adapter_class(**adapter_kwargs)

    frontier = FrontierMachine(
        lambda_anchor=cfg.lambda_anchor,
        lambda_target=cfg.lambda_target,
        minimum_width=cfg.minimum_lambda_width,
        max_depth=cfg.raw["max_lambda_depth"],
    )
    budget = EvaluationBudget(
        cfg.raw["global_eval_limit"],
        cfg.raw["per_box_eval_limit"],
    )
    seed_window = (cfg.w0_lo, cfg.w0_hi)
    evaluator_ref: dict[str, CertifiedAttemptEvaluator] = {}

    def context_provider(box: LambdaBox) -> AttemptStructuralContext:
        evaluator = evaluator_ref["value"]
        previous = evaluator_ref.get("runner").pass_windows[-1] if evaluator_ref.get("runner") and evaluator_ref["runner"].pass_windows else seed_window
        return AttemptStructuralContext(
            previous_window=previous,
            delta_overlap_min=cfg.delta_overlap_min,
            is_anchor_leaf=box.hi == cfg.lambda_anchor,
            require_icg_hull=box.hi == cfg.lambda_anchor,
        )

    evaluator = CertifiedAttemptEvaluator(
        adapter=runner_adapter,
        dps=cfg.raw["dps"],
        max_r_cells_per_box=cfg.raw["max_r_cells_per_box"],
        context_provider=context_provider,
    )
    evaluator_ref["value"] = evaluator
    initial_root_midpoint = (Fraction(1, 64) + Fraction(11, 256)) / 2
    runner = SweepRunner(
        frontier=frontier,
        budget=budget,
        evaluator=evaluator,
        grid=cfg.grid,
        minimum_window_width=cfg.minimum_window_width,
        delta_overlap_min=cfg.delta_overlap_min,
        anchor_seed_window=seed_window,
        predictor_points=[PredictorPoint(cfg.lambda_anchor, initial_root_midpoint, "CG-PILOT-30334858060")],
    )
    evaluator_ref["runner"] = runner
    result = runner.run()

    fresh = FreshEvidenceEvaluator(
        original=evaluator,
        adapter=checker_adapter,
        checker_dps=cfg.raw["checker_dps"],
    )
    verifier = ArtifactVerifier(SweepChecker(fresh))
    verification = verifier.verify(
        canonical_config_bytes=config_bytes,
        stored_config_sha256=config_sha,
        runner_result=result,
    )

    records_raw, chain_tip = serialize_record_chain(result, config_sha)
    (output / "SWEEP_RECORDS.jsonl").write_bytes(records_raw)
    records_sha = sha256_hex(records_raw)
    evidence_sha = write_json(output / "SWEEP_EVIDENCE.json", evidence_object(evaluator))
    checker_report = {
        "checker_failure_reason": verification.failure_reason.value if verification.failure_reason else None,
        "checker_terminal_class": verification.terminal_class.value,
        "config_sha256": verification.config_sha256,
        "runner_terminal_class": result.terminal_class.value,
        "schema": "ITEM3_SWEEP_CHECKER_REPORT_V1",
        "verified_box_ids": list(verification.verified_box_ids),
    }
    checker_report_sha = write_json(output / "SWEEP_CHECKER_REPORT.json", checker_report)

    if verification.terminal_class is not CheckerTerminalClass.VERIFY_PASS:
        return 2
    if result.terminal_class is not RunnerTerminalClass.NORMAL_COMPLETE:
        return 3

    manifest = {
        "certified_lambda_range_declared": False,
        "checker_report_sha256": checker_report_sha,
        "checker_terminal_class": verification.terminal_class.value,
        "config_sha256": config_sha,
        "evidence_sha256": evidence_sha,
        "github_ref": os.environ.get("ITEM3_SWEEP_GITHUB_REF"),
        "github_run_attempt": os.environ.get("ITEM3_SWEEP_GITHUB_RUN_ATTEMPT"),
        "github_run_id": os.environ.get("ITEM3_SWEEP_GITHUB_RUN_ID"),
        "github_sha": os.environ.get("ITEM3_SWEEP_GITHUB_SHA"),
        "lambda_anchor": rational_object(cfg.lambda_anchor),
        "lambda_reached": rational_object(result.lambda_reached),
        "lambda_target": rational_object(cfg.lambda_target),
        "machine_conclusion_scope": "VERIFIED_BOX_PASS_ONLY",
        "production_adapter_module_origin": str(adapter_source_identity.module_origin.relative_to(REPO)),
        "production_adapter_post_import_sha256": adapter_source_identity.post_import_sha256,
        "production_adapter_pre_import_sha256": adapter_source_identity.pre_import_sha256,
        "pilot_artifact_rederivation_sha256": pilot_report_sha,
        "record_chain_final_sha256": chain_tip,
        "records_sha256": records_sha,
        "runner_terminal_class": result.terminal_class.value,
        "schema": "ITEM3_SWEEP_RUN_MANIFEST_V1",
        "verified_box_ids": list(verification.verified_box_ids),
        "verdict": "VERIFY_PASS",
    }
    write_json(output / "SWEEP_RUN_MANIFEST.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
