#!/usr/bin/env python3
"""Non-binding full-site initial-margin census for B-TUBE v2.1."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from time import perf_counter

import calibration_candidate as candidate
from affine_geometry import krawczyk_image
from calibration_config import load_config
from calibration_context import (
    CHAIN_DOMAIN,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    chain_genesis,
)
from calibration_numeric import _candidate_pairs, _cell_partition
from calibration_security import load_production_kernel
from exact_lambda_transport import (
    EXACT_LAMBDA_REFINEMENT_EVAL_CAP,
    ExactLambdaRoutedEvaluator,
    _transport_evidence,
    install_exact_lambda_call_sites,
)
from routed_evaluator import _model_interval_to_dyadic
from flint import arb, ctx


DIAGNOSTIC_BUDGET = 24_000
DIAGNOSTIC_HU_WIDTH = Fraction(1, 2)
EXPECTED_CANDIDATES = 9
EXPECTED_CELLS = 228
EXPECTED_JOINS = 219
EXPECTED_TERMINALS = 9
EXPECTED_SITES = 456
OUT_DIR = Path("diagnostic-output")
OUT_JSONL = OUT_DIR / "diagnostic-census-pass1-NOT_BINDING.jsonl"
OUT_SUMMARY = OUT_DIR / "diagnostic-census-pass1-summary-NOT_BINDING.json"


def frac(value: Fraction | None) -> str | None:
    return None if value is None else str(value)


def site_identity(candidate_index: int, ordinal: int, cells: int) -> tuple[str, int]:
    if ordinal == 0:
        return "cell", 0
    if ordinal == 2 * cells - 1:
        return "terminal", 0
    if ordinal % 2 == 1:
        return "cell", (ordinal + 1) // 2
    return "join", ordinal // 2 - 1


def main() -> int:
    print("BTUBE_CENSUS_PASS1_V1")
    print("EVIDENCE_CLASS=DIAGNOSTIC_NOT_BINDING")
    print("NOT_BINDING=TRUE")
    print(f"DIAGNOSTIC_BUDGET={DIAGNOSTIC_BUDGET}")
    print(f"DIAGNOSTIC_HU_WIDTH={DIAGNOSTIC_HU_WIDTH}")
    print(f"EXPECTED_SITES={EXPECTED_SITES}")

    try:
        # Keep a durable partial census if the hosted job reaches its timeout.
        # This directory is in the controls checkout workspace, never in the
        # exact target checkout whose HEAD/TREE invariants are binding here.
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_JSONL.write_text("", encoding="utf-8")
        config, _ = load_config()
        raw_kernel, _ = load_production_kernel()
        ctx.dps = config["dps"]
        install_exact_lambda_call_sites()
        evaluator = ExactLambdaRoutedEvaluator(raw_kernel, arb, config)

        route = evaluator.modules["blocal_v22_boundary"]
        model = evaluator.modules["blocal_v22_model"]
        adapter = evaluator.modules["blocal_arb_adapter"]
        original_krawczyk = candidate._evaluate_krawczyk
        original_predictor = candidate._newton_predictor

        if EXACT_LAMBDA_REFINEMENT_EVAL_CAP != DIAGNOSTIC_BUDGET:
            raise RuntimeError("unexpected production route cap")
        for policy_name in ("F_ROUTE", "K_ROUTE"):
            policy = evaluator.boundary_config["route_policies"][policy_name]
            if policy["max_evaluations"] != DIAGNOSTIC_BUDGET:
                raise RuntimeError(f"unexpected {policy_name} evaluation cap")

        start = Rational.from_json(
            config["blocal_dependency"]["lambda_start"],
            "blocal_dependency.lambda_start",
        ).as_fraction()
        end = Rational.from_json(config["lambda_end"], "lambda_end").as_fraction()
        pairs = _candidate_pairs(config)
        if len(pairs) != EXPECTED_CANDIDATES:
            raise RuntimeError(f"candidate count mismatch: {len(pairs)}")

        cell_counts: dict[int, int] = {}
        for index, (width, _) in enumerate(pairs):
            cell_counts[index] = len(
                _cell_partition(
                    start, end, width.as_fraction(), config["max_cells"]
                )
            )
        if sum(cell_counts.values()) != EXPECTED_CELLS:
            raise RuntimeError("cell count mismatch")

        rows: list[dict] = []
        ordinals = {index: 0 for index in range(len(pairs))}
        predictor_cache: dict[tuple, Dyadic] = {}
        predictor_cache_hits = 0
        predictor_cache_misses = 0

        def cached_predictor(kernel, arb_type, lam, seed, *, iterations,
                             tol, depth, limit):
            nonlocal predictor_cache_hits, predictor_cache_misses
            key = (
                lam, seed.as_fraction(), iterations, tol, depth, limit
            )
            if key in predictor_cache:
                predictor_cache_hits += 1
                return predictor_cache[key]
            predictor_cache_misses += 1
            value = original_predictor(
                kernel, arb_type, lam, seed, iterations=iterations,
                tol=tol, depth=depth, limit=limit,
            )
            predictor_cache[key] = value
            return value

        def alternative_domain_slope(
            domain: DyadicInterval, lam_lo: Fraction, lam_hi: Fraction
        ) -> tuple[DyadicInterval | None, int, str]:
            # The H_U boundary chart is defined for r >= 3/4. Interior and
            # straddling sites retain the production slope; they need no
            # boundary-only H_U width experiment.
            if domain.lo.as_fraction() < Fraction(3, 4):
                return None, 0, "NOT_BOUNDARY_ONLY"
            r0, r1 = domain.lo.as_fraction(), domain.hi.as_fraction()
            u0, u1 = Fraction(1) - r1, Fraction(1) - r0
            s_iv, _ = _transport_evidence(model, lam_lo, lam_hi)
            s0, s1 = s_iv.lo.as_fraction(), s_iv.hi.as_fraction()

            def accept(enclosure) -> bool:
                lo, hi = model.interval_fractions(
                    enclosure, "census pass1 H_U domain"
                )
                return lo > 0 and hi - lo <= DIAGNOSTIC_HU_WIDTH

            def compute():
                return route.enclose_route(
                    "H_U", evaluator.interior_kernel, adapter,
                    evaluator.acb_type, evaluator.arb_type,
                    evaluator.fmpq_type, evaluator.boundary_config,
                    u0, u1, s0, s1, required_sign=None, accept=accept,
                    evaluation_cap=DIAGNOSTIC_BUDGET,
                )

            try:
                normalized, proof = evaluator._with_boundary_precision(compute)
            except route.EnclosureFailure as exc:
                return None, exc.evaluations, "CAP"
            interval = _model_interval_to_dyadic(
                model, normalized, "census pass1 H_U domain"
            )
            return -interval, proof["evaluation_count"], "PASS"

        def wrapped_krawczyk(*, kernel, arb_type, domain, lam_lo, lam_hi,
                             tol, depth, limit):
            phase = evaluator.phase
            if not phase.startswith("CANDIDATE:"):
                raise RuntimeError(f"unexpected phase: {phase}")
            candidate_index = int(phase.split(":", 1)[1])
            ordinal = ordinals[candidate_index]
            ordinals[candidate_index] += 1
            kind, kind_index = site_identity(
                candidate_index, ordinal, cell_counts[candidate_index]
            )

            before = evaluator.boundary_evaluation_count
            t0 = perf_counter()
            result = original_krawczyk(
                kernel=kernel, arb_type=arb_type, domain=domain,
                lam_lo=lam_lo, lam_hi=lam_hi, tol=tol,
                depth=depth, limit=limit,
            )
            initial_elapsed = perf_counter() - t0
            initial_evaluations = evaluator.boundary_evaluation_count - before
            initial_margin = min(
                result["left_margin"].as_fraction(),
                result["right_margin"].as_fraction(),
            )

            alt_t0 = perf_counter()
            alt_slope, alt_evaluations, alt_status = alternative_domain_slope(
                domain, lam_lo, lam_hi
            )
            alt_elapsed = perf_counter() - alt_t0
            alt_margin = initial_margin
            alt_passed = result["passed"]
            if alt_slope is not None and result["preconditioner"] != D_ZERO:
                alt_image = krawczyk_image(
                    m=domain.midpoint(), residual=result["residual"],
                    slope=alt_slope,
                    preconditioner=result["preconditioner"], domain=domain,
                )
                alt_margin = min(
                    (alt_image.lo - domain.lo).as_fraction(),
                    (domain.hi - alt_image.hi).as_fraction(),
                )
                alt_passed = domain.strictly_contains(alt_image) and alt_slope.hi < D_ZERO

            row = {
                "schema": "btube-census-pass1-site-v1",
                "evidence_class": "DIAGNOSTIC_NOT_BINDING",
                "candidate_index": candidate_index,
                "site_ordinal": ordinal,
                "site_kind": kind,
                "site_index": kind_index,
                "lambda_lo": str(lam_lo),
                "lambda_hi": str(lam_hi),
                "domain_lo": str(domain.lo.as_fraction()),
                "domain_hi": str(domain.hi.as_fraction()),
                "initial_passed": result["passed"],
                "initial_reason": result["reason"],
                "initial_margin": str(initial_margin),
                "initial_residual_lo": str(result["residual"].lo.as_fraction()),
                "initial_residual_hi": str(result["residual"].hi.as_fraction()),
                "initial_slope_lo": str(result["slope"].lo.as_fraction()),
                "initial_slope_hi": str(result["slope"].hi.as_fraction()),
                "initial_evaluations": initial_evaluations,
                "initial_elapsed_seconds": f"{initial_elapsed:.6f}",
                "hu_half_status": alt_status,
                "hu_half_evaluations": alt_evaluations,
                "hu_half_elapsed_seconds": f"{alt_elapsed:.6f}",
                "hu_half_margin": str(alt_margin),
                "hu_half_passed": alt_passed,
            }
            rows.append(row)
            with OUT_JSONL.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
                )
                stream.flush()
            print(
                f"SITE candidate={candidate_index} kind={kind} index={kind_index} "
                f"initial_margin={initial_margin} initial_passed={result['passed']} "
                f"hu_half_status={alt_status} hu_half_margin={alt_margin} "
                f"hu_half_passed={alt_passed}"
            )

            # Census-only continuation: enumerate every geometric site even
            # when the production predicate is negative. Recorded values are
            # never emitted as binding calibration records or certificates.
            forced = dict(result)
            forced["passed"] = True
            forced["reason"] = None
            return forced

        candidate._newton_predictor = cached_predictor
        candidate._evaluate_krawczyk = wrapped_krawczyk

        records = []
        previous = chain_genesis(CHAIN_DOMAIN)
        run_t0 = perf_counter()
        for candidate_index, (width, radius) in enumerate(pairs):
            evaluator.set_phase(f"CANDIDATE:{candidate_index}")
            _, previous, _ = candidate._candidate_run(
                config=config, kernel=evaluator, arb_type=arb,
                start=Rational.from_fraction(start), width=width,
                radius=radius, candidate_index=candidate_index,
                records=records, previous=previous,
            )
        elapsed = perf_counter() - run_t0

        counts = {
            kind: sum(row["site_kind"] == kind for row in rows)
            for kind in ("cell", "join", "terminal")
        }
        if counts != {
            "cell": EXPECTED_CELLS,
            "join": EXPECTED_JOINS,
            "terminal": EXPECTED_TERMINALS,
        }:
            raise RuntimeError(f"site distribution mismatch: {counts}")
        if len(rows) != EXPECTED_SITES:
            raise RuntimeError(f"site count mismatch: {len(rows)}")

        summary = {
            "schema": "btube-census-pass1-summary-v1",
            "evidence_class": "DIAGNOSTIC_NOT_BINDING",
            "not_binding": True,
            "diagnostic_budget": DIAGNOSTIC_BUDGET,
            "diagnostic_hu_width": str(DIAGNOSTIC_HU_WIDTH),
            "candidate_count": len(pairs),
            "site_count": len(rows),
            "site_counts": counts,
            "initial_positive_count": sum(row["initial_passed"] for row in rows),
            "hu_half_positive_count": sum(row["hu_half_passed"] for row in rows),
            "remaining_negative_count": sum(not row["hu_half_passed"] for row in rows),
            "hu_half_cap_count": sum(row["hu_half_status"] == "CAP" for row in rows),
            "predictor_cache_hits": predictor_cache_hits,
            "predictor_cache_misses": predictor_cache_misses,
            "charged_boundary_evaluations": evaluator.boundary_evaluation_count,
            "elapsed_seconds": f"{elapsed:.6f}",
        }
        OUT_SUMMARY.write_text(
            json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        for key, value in summary.items():
            print(f"SUMMARY_{key.upper()}={value}")
        print("DIAGNOSTIC_VERDICT=PASS")
        return 0
    except Exception as exc:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_SUMMARY.write_text(
            json.dumps(
                {
                    "schema": "btube-census-pass1-error-v1",
                    "evidence_class": "DIAGNOSTIC_NOT_BINDING",
                    "not_binding": True,
                    "diagnostic_verdict": "ERROR",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                sort_keys=True,
                separators=(",", ":"),
            ) + "\n",
            encoding="utf-8",
        )
        print(f"DIAGNOSTIC_ERROR={type(exc).__name__}:{exc}")
        print("DIAGNOSTIC_VERDICT=ERROR")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
