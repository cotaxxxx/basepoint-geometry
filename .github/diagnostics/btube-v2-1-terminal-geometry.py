#!/usr/bin/env python3
"""Non-binding, Krawczyk-free terminal geometry census for nine candidates."""
from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import calibration_candidate as candidate
from flint import arb, ctx

from calibration_config import load_config, require_blocal_dependency
from calibration_context import CHAIN_DOMAIN, D_ZERO, DyadicInterval, Rational, chain_genesis
from calibration_numeric import _candidate_pairs
from calibration_security import load_production_kernel
from exact_lambda_transport import ExactLambdaRoutedEvaluator, install_exact_lambda_call_sites


OUT = Path("diagnostic-output/terminal-geometry-NOT_BINDING.json")
SOFT_DEADLINE_SECONDS = 280 * 60


def synthetic_krawczyk(*, domain, **kwargs):
    midpoint = domain.midpoint()
    return {
        "image": DyadicInterval.point(midpoint),
        "left_margin": D_ZERO,
        "passed": True,
        "preconditioner": D_ZERO,
        "reason": None,
        "residual": DyadicInterval.point(D_ZERO),
        "right_margin": D_ZERO,
        "slope": DyadicInterval.point(D_ZERO),
    }


def main() -> int:
    print("BTUBE_TERMINAL_GEOMETRY_V1")
    print("EVIDENCE_CLASS=DIAGNOSTIC_NOT_BINDING")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t0 = perf_counter()
    report = {"schema": "btube-terminal-geometry-v1",
              "evidence_class": "DIAGNOSTIC_NOT_BINDING", "candidates": []}
    try:
        config, _ = load_config()
        raw_kernel, _ = load_production_kernel()
        ctx.dps = config["dps"]
        install_exact_lambda_call_sites()
        pairs = _candidate_pairs(config)
        if len(pairs) != 9:
            raise RuntimeError(f"candidate count mismatch: {len(pairs)}")
        original_krawczyk = candidate._evaluate_krawczyk
        candidate._evaluate_krawczyk = synthetic_krawczyk
        candidate.require_blocal_dependency = require_blocal_dependency
        start = Rational.from_json(
            config["blocal_dependency"]["lambda_start"], "lambda_start"
        )
        try:
            for index, (width, radius) in enumerate(pairs):
                if perf_counter() - t0 >= SOFT_DEADLINE_SECONDS:
                    report["soft_deadline_reached"] = True
                    break
                row = {"candidate_index": index, "lambda_width": width.to_json(),
                       "tube_radius": radius.to_json()}
                try:
                    evaluator = ExactLambdaRoutedEvaluator(raw_kernel, arb, config)
                    evaluator.set_phase(f"TERMINAL_GEOMETRY:{index}")
                    records = []
                    candidate._candidate_run(
                        config=config, kernel=evaluator, arb_type=arb, start=start,
                        width=width, radius=radius, candidate_index=index,
                        records=records, previous=chain_genesis(CHAIN_DOMAIN),
                    )
                    end = next(r for r in records if r["record_type"] == "candidate_end")
                    row.update({
                        "status": "PASS",
                        "cells_attempted": end["cells_attempted"],
                        "terminal_failure_reason": end["terminal_failure_reason"],
                        "terminal_intersection": end["terminal_cg_intersection"],
                        "terminal_krawczyk_called": end["terminal_failure_reason"] is None,
                        "charged_boundary_evaluations": evaluator.boundary_evaluation_count,
                    })
                except Exception as exc:
                    row.update({"status": "ERROR", "error_type": type(exc).__name__,
                                "error": str(exc)})
                report["candidates"].append(row)
                print(f"CANDIDATE={index} STATUS={row['status']} ")
        finally:
            candidate._evaluate_krawczyk = original_krawczyk
        report["candidate_count"] = len(report["candidates"])
        report["terminal_call_count"] = sum(
            r.get("terminal_krawczyk_called") is True for r in report["candidates"]
        )
        report["candidate_error_count"] = sum(
            r["status"] == "ERROR" for r in report["candidates"]
        )
        report["soft_deadline_seconds"] = SOFT_DEADLINE_SECONDS
        complete = len(report["candidates"]) == len(pairs)
        report["diagnostic_verdict"] = (
            "PASS" if complete and report["candidate_error_count"] == 0 else "PARTIAL"
        )
        rc = 0 if report["diagnostic_verdict"] == "PASS" else 7
    except Exception as exc:
        report.update({"diagnostic_verdict": "ERROR", "error_type": type(exc).__name__,
                       "error": str(exc)})
        rc = 4
    report["elapsed_seconds"] = f"{perf_counter() - t0:.6f}"
    OUT.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"DIAGNOSTIC_VERDICT={report['diagnostic_verdict']}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
