#!/usr/bin/env python3
"""B-TUBE v2.1 producer glue for native B-LOCAL v2.3 F_lambda transport.

PROTOTYPE / BINDING_CANDIDATE producer only.
This module does not authorize binding use and does not implement checker logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
V23 = HERE / "dependencies/blocal_v23_source"
PIN_FILE = V23 / "F_LAMBDA_TRANSPORT_PRODUCER_V1_PINS.json"
SOURCE_PATH = HERE / "flambda_transport_producer_v1.py"
TRANSPORT_PIN_FILE = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1_PINS.json"
TRANSPORT_RECEIPT = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1.md"
JUDGE_SIGNATURE = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1_JUDGE_SIGNATURE.json"
SOURCE_MANIFEST = V23 / "BLOCAL_V23_SOURCE_MANIFEST.json"
BOUNDARY = V23 / "blocal_v23_boundary.py"
SHARED_KERNEL = V23 / "blocal_v23_flambda_kernel.py"
ROUTE_FRAGMENT = V23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json"
BLOCAL_RUN_CONFIG = V23 / "config.blocal-v2.2-run.json"
CALIBRATION_CONFIG = HERE / "config.calibration.json"

PRODUCER_SCHEMA = "btube-flambda-transport-producer-v1"
PRODUCER_EVIDENCE_CLASS = "BINDING_CANDIDATE"
PRODUCER_STATUS = "PROTOTYPE_NOT_PROMOTED"
TRANSPORT_LEMMA_ID = "F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1"
TRANSPORT_AUDIT_STATUS = "PASS_CURRENT_STRICT_INTERIOR_SCOPE"
FLAMBDA_ROUTE_ID = "BLOCAL_FLAMBDA_ROUTE_V1"
FLAMBDA_BASE_TILE = Fraction(1, 16)
ANCHOR_CALL_CAP = 24000
FLAMBDA_CELL_CALL_CAP = 24000
TOL = "1e-20"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V23))

from calibration_context import (  # noqa: E402
    AffinePredictor,
    BLOCAL_LAMBDA_START,
    CalibrationError,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    canonical_json_bytes,
)
from calibration_config import load_config, require_blocal_dependency  # noqa: E402
from calibration_numeric import (  # noqa: E402
    _adaptive_radius,
    _candidate_pairs,
    _cell_partition,
    _load_a0_start_interval,
)
from calibration_runner import load_production_kernel  # noqa: E402
from exact_lambda_transport import (  # noqa: E402
    ExactLambdaRoutedEvaluator,
    exact_newton_predictor,
)


class ProducerFailure(RuntimeError):
    """Fail-closed producer error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), *args], text=True
    ).strip()


def _need(condition: bool, code: str, detail: str | None = None) -> None:
    if not condition:
        raise ProducerFailure(code, detail)


def _fraction_json(value: Fraction) -> dict[str, str]:
    return Rational.from_fraction(value).to_json()


def _interval_fraction_json(lo: Fraction, hi: Fraction) -> dict[str, Any]:
    _need(lo <= hi, "FAIL_INTERVAL_ORDER")
    return {"lo": _fraction_json(lo), "hi": _fraction_json(hi)}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text())
    except Exception as exc:
        raise ProducerFailure("FAIL_JSON_LOAD", path.name) from exc
    _need(isinstance(obj, dict), "FAIL_JSON_OBJECT", path.name)
    return obj


def _verify_legacy_snapshot(manifest: dict[str, Any]) -> dict[str, str]:
    snapshot = manifest.get("legacy_snapshot")
    _need(isinstance(snapshot, dict) and snapshot, "FAIL_LEGACY_SNAPSHOT_MANIFEST")
    actual: dict[str, str] = {}
    for name, expected in sorted(snapshot.items()):
        _need(isinstance(name, str) and isinstance(expected, str),
              "FAIL_LEGACY_SNAPSHOT_ENTRY")
        path = V23 / name
        _need(path.is_file(), "FAIL_LEGACY_RUNTIME_FILE_MISSING", name)
        got = _sha(path)
        _need(got == expected, "FAIL_LEGACY_RUNTIME_SHA", name)
        actual[name] = got
    return actual


def _precheck(expected_head: str) -> dict[str, Any]:
    _need(len(expected_head) == 40, "FAIL_EXPECTED_HEAD_FORMAT")
    _need(_git("rev-parse", "HEAD") == expected_head, "FAIL_HEAD_MISMATCH")
    _need(not _git("status", "--porcelain"), "FAIL_DIRTY_SOURCE_TREE")
    _need(PIN_FILE.is_file(), "FAIL_PRODUCER_PIN_FILE_MISSING")

    pins = _load_json(PIN_FILE)
    source_baseline = pins.get("source_baseline_head")
    _need(isinstance(source_baseline, str) and len(source_baseline) == 40,
          "FAIL_SOURCE_BASELINE_PIN")
    try:
        subprocess.check_call(
            ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor",
             source_baseline, expected_head],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise ProducerFailure("FAIL_SOURCE_BASELINE_ANCESTRY") from exc

    allowed_after_baseline = {
        PIN_FILE.relative_to(REPO_ROOT).as_posix(),
    }
    changed = {
        line for line in _git(
            "diff", "--name-only", f"{source_baseline}..{expected_head}"
        ).splitlines() if line
    }
    _need(changed == allowed_after_baseline, "FAIL_POST_BASELINE_FILE_SET",
          ",".join(sorted(changed)))

    actual = {
        "producer_source_sha256": _sha(SOURCE_PATH),
        "boundary_sha256": _sha(BOUNDARY),
        "shared_kernel_sha256": _sha(SHARED_KERNEL),
        "transport_receipt_sha256": _sha(TRANSPORT_RECEIPT),
        "judge_signature_sha256": _sha(JUDGE_SIGNATURE),
        "source_manifest_sha256": _sha(SOURCE_MANIFEST),
        "route_fragment_sha256": _sha(ROUTE_FRAGMENT),
        "calibration_config_sha256": _sha(CALIBRATION_CONFIG),
    }
    for key, got in actual.items():
        _need(pins.get(key) == got, "FAIL_PIN_MISMATCH", key)

    manifest = _load_json(SOURCE_MANIFEST)
    _need(manifest.get("binding_use_authorized") is False,
          "FAIL_MANIFEST_BINDING_AUTHORIZATION")
    legacy_actual = _verify_legacy_snapshot(manifest)
    native = manifest.get("native_route", {})
    _need(native.get("route_id") == FLAMBDA_ROUTE_ID, "FAIL_ROUTE_ID_PIN")
    _need(native.get("quantity") == "F_lambda", "FAIL_QUANTITY_PIN")
    _need(native.get("required_sign") == "NEG", "FAIL_REQUIRED_SIGN_PIN")
    _need(native.get("required_sign_input_policy") ==
          "EXPLICIT_MANDATORY_FAIL_CLOSED", "FAIL_REQUIRED_SIGN_POLICY")
    _need(native.get("boundary_sha256") == actual["boundary_sha256"],
          "FAIL_BOUNDARY_MANIFEST_PIN")
    _need(native.get("shared_kernel_sha256") == actual["shared_kernel_sha256"],
          "FAIL_KERNEL_MANIFEST_PIN")
    _need(native.get("transport_lemma_id") == TRANSPORT_LEMMA_ID,
          "FAIL_TRANSPORT_LEMMA_ID")
    _need(native.get("symbolic_reaudit_required") is False,
          "FAIL_SYMBOLIC_REAUDIT_REQUIRED")
    _need(native.get("symbolic_reaudit_status") == "PASS_CONTENT_LEVEL",
          "FAIL_SYMBOLIC_REAUDIT_STATUS")
    _need(isinstance(native.get("ordinary_formula_id"), str),
          "FAIL_ORDINARY_FORMULA_ID_PIN")
    _need(isinstance(native.get("duffy_formula_id"), str),
          "FAIL_DUFFY_FORMULA_ID_PIN")

    lemma_pins = _load_json(TRANSPORT_PIN_FILE)
    _need(lemma_pins.get("receipt_sha256") == actual["transport_receipt_sha256"],
          "FAIL_TRANSPORT_RECEIPT_PIN")
    _need(lemma_pins.get("judge_signature_sha256") ==
          actual["judge_signature_sha256"], "FAIL_JUDGE_SIGNATURE_PIN")
    _need(lemma_pins.get("judge_verdict") == "PASS", "FAIL_JUDGE_VERDICT")
    _need(lemma_pins.get("transport_lemma_human_audit") ==
          TRANSPORT_AUDIT_STATUS, "FAIL_TRANSPORT_HUMAN_AUDIT")

    signature = _load_json(JUDGE_SIGNATURE)
    _need(signature.get("receipt_sha256") ==
          actual["transport_receipt_sha256"], "FAIL_SIGNATURE_RECEIPT_LINK")
    _need(signature.get("judge_verdict") == "PASS", "FAIL_SIGNATURE_VERDICT")
    _need(signature.get("judge_scope") ==
          "CURRENT_STRICT_INTERIOR_ENDPOINT_SCOPE", "FAIL_SIGNATURE_SCOPE")

    _need(pins.get("anchor_call_cap") == ANCHOR_CALL_CAP,
          "FAIL_ANCHOR_CAP_PIN")
    _need(pins.get("flambda_cell_call_cap") == FLAMBDA_CELL_CALL_CAP,
          "FAIL_FLAMBDA_CAP_PIN")
    _need(pins.get("base_tile") == {"p": "1", "q": "16"},
          "FAIL_TILE_PIN")
    _need(pins.get("evidence_class") == PRODUCER_EVIDENCE_CLASS,
          "FAIL_EVIDENCE_CLASS_PIN")
    _need(pins.get("binding_use_authorized") is False,
          "FAIL_BINDING_AUTHORIZATION_STATE")
    return {
        "pins": pins,
        "actual": actual,
        "source_baseline_head": source_baseline,
        "native_manifest": native,
        "legacy_snapshot": legacy_actual,
    }


def _reconstruct_geometry(
    *,
    config: dict[str, Any],
    exact_kernel: Any,
    arb_type: Any,
    candidate_index: int,
    cell_index: int,
) -> dict[str, Any]:
    pairs = _candidate_pairs(config)
    _need(0 <= candidate_index < len(pairs), "FAIL_CANDIDATE_INDEX")
    width, radius_cap = pairs[candidate_index]
    start = Rational.from_json(
        config["blocal_dependency"]["lambda_start"],
        "blocal_dependency.lambda_start",
    ).as_fraction()
    end = Rational.from_json(config["lambda_end"], "lambda_end").as_fraction()
    cells = _cell_partition(
        start, end, width.as_fraction(), config["max_cells"]
    )
    _need(0 <= cell_index < len(cells), "FAIL_CELL_INDEX")

    a0_interval, _ = _load_a0_start_interval()
    anchor = a0_interval.midpoint()
    sigma = Dyadic.from_json(
        config["adaptive_safety_factor"], "adaptive_safety_factor"
    )
    refresh = config["predictor_refresh"]
    depth = config["max_subdivisions"]
    limit = config["evaluation_budget"]
    seed = anchor
    target: dict[str, Any] | None = None

    for index, (left, right) in enumerate(cells[: cell_index + 1]):
        q_left = anchor if index == 0 else seed
        iterations = 4 if index % refresh == 0 else 1
        q_right = exact_newton_predictor(
            exact_kernel,
            arb_type,
            right,
            q_left,
            iterations=iterations,
            tol=TOL,
            depth=depth,
            limit=limit,
        )
        predictor = AffinePredictor(
            Rational.from_fraction(left),
            Rational.from_fraction(right),
            q_left,
            q_right,
        )
        rho, boundary_left, boundary_right, domain = _adaptive_radius(
            predictor.range_hull(), radius_cap, sigma
        )
        target = {
            "lambda_left": left,
            "lambda_right": right,
            "q_left": q_left,
            "q_right": q_right,
            "rho": rho,
            "boundary_left": boundary_left,
            "boundary_right": boundary_right,
            "domain": domain,
            "nominal_width": width,
            "radius_cap": radius_cap,
        }
        seed = q_right

    assert target is not None
    domain = target["domain"]
    _need(domain.lo > D_ZERO and domain.hi.as_fraction() < 1,
          "FAIL_STRICT_INTERIOR_ENDPOINT_SCOPE")
    return target


def _residual_tiling(lo: Fraction, hi: Fraction) -> list[tuple[Fraction, Fraction]]:
    _need(lo < hi, "FAIL_PARENT_WIDTH")
    tiles: list[tuple[Fraction, Fraction]] = []
    left = lo
    while left < hi:
        right = min(left + FLAMBDA_BASE_TILE, hi)
        _need(left < right, "FAIL_TILE_NONPOSITIVE")
        tiles.append((left, right))
        left = right
    _need(tiles[0][0] == lo and tiles[-1][1] == hi, "FAIL_TILE_ENDPOINT")
    for idx in range(len(tiles) - 1):
        _need(tiles[idx][1] == tiles[idx + 1][0], "FAIL_TILE_GAP_OR_OVERLAP")
    _need(all((b - a) <= FLAMBDA_BASE_TILE for a, b in tiles),
          "FAIL_TILE_WIDTH")
    return tiles


def _load_v23_boundary_config() -> dict[str, Any]:
    bcfg = _load_json(BLOCAL_RUN_CONFIG)
    frag = _load_json(ROUTE_FRAGMENT)
    _need(frag.get("route_id") == FLAMBDA_ROUTE_ID, "FAIL_ROUTE_FRAGMENT_ID")
    _need(frag.get("native_quantity") == "F_lambda",
          "FAIL_ROUTE_FRAGMENT_QUANTITY")
    _need(frag.get("required_sign") == "NEG",
          "FAIL_ROUTE_FRAGMENT_SIGN")
    bcfg.setdefault("route_policies", {}).update(frag["route_policies"])
    return bcfg


def _anchor_record(
    *,
    evaluator: Any,
    endpoint: Any,
    lam: Fraction,
    required_sign: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    _, interval, evidence = evaluator._evaluate_exact(
        "F",
        DyadicInterval.point(endpoint),
        lam,
        lam,
        TOL,
        config["max_subdivisions"],
        config["evaluation_budget"],
        record=False,
        f_nonzero=True,
    )
    _need(isinstance(evidence, dict), "FAIL_ANCHOR_EVIDENCE")
    _need(evidence.get("quantity") == "F", "FAIL_ANCHOR_QUANTITY")
    _need(evidence.get("post_failure_fallback") is False,
          "FAIL_ANCHOR_POST_FAILURE_FALLBACK")
    used = evidence.get("boundary_route_evaluation_count_delta")
    detail = evidence.get("detail")
    _need(isinstance(used, int) and 0 <= used <= ANCHOR_CALL_CAP,
          "FAIL_ANCHOR_BUDGET")
    if required_sign == "NEG":
        _need(interval.hi < D_ZERO, "FAIL_ANCHOR_SIGN_NEG")
    elif required_sign == "POS":
        _need(D_ZERO < interval.lo, "FAIL_ANCHOR_SIGN_POS")
    else:
        raise ProducerFailure("FAIL_ANCHOR_SIGN_CONTRACT")
    return {
        "lambda": _fraction_json(lam),
        "required_sign": required_sign,
        "enclosure": interval.to_json(),
        "evaluation_count": used,
        "detail": detail,
    }


def _flambda_records(
    *,
    route: Any,
    model: Any,
    adapter: Any,
    raw_kernel: Any,
    acb_type: Any,
    arb_type: Any,
    fmpq_type: Any,
    bcfg: dict[str, Any],
    endpoint: Any,
    tiles: list[tuple[Fraction, Fraction]],
    proof_expectations: dict[str, Any],
) -> list[dict[str, Any]]:
    r = endpoint.as_fraction()
    u = Fraction(1) - r
    records: list[dict[str, Any]] = []
    for index, (llo, lhi) in enumerate(tiles):
        s0 = llo - model.LAMBDA_PLUS
        s1 = lhi - model.LAMBDA_PLUS
        try:
            enclosure, proof = route.enclose_route(
                "F_lambda",
                raw_kernel,
                adapter,
                acb_type,
                arb_type,
                fmpq_type,
                bcfg,
                u,
                u,
                s0,
                s1,
                required_sign="NEG",
                accept=None,
                evaluation_cap=FLAMBDA_CELL_CALL_CAP,
            )
        except route.ContractFailure as exc:
            raise ProducerFailure("FAIL_FLAMBDA_CONTRACT", exc.code) from exc
        except route.base.EnclosureFailure as exc:
            raise ProducerFailure("FAIL_FLAMBDA_BUDGET_OR_ENCLOSURE",
                                  exc.reason) from exc
        lo, hi = model.interval_fractions(
            enclosure, f"producer F_lambda tile {index}"
        )
        used = proof.get("evaluation_count")
        _need(hi < 0, "FAIL_FLAMBDA_SIGN", str(index))
        _need(proof.get("complete_closed_cover") is True,
              "FAIL_FLAMBDA_COVER", str(index))
        _need(proof.get("route_id") == FLAMBDA_ROUTE_ID,
              "FAIL_FLAMBDA_ROUTE", str(index))
        _need(proof.get("quantity") == "F_lambda",
              "FAIL_FLAMBDA_QUANTITY", str(index))
        _need(proof.get("required_sign") == "NEG",
              "FAIL_FLAMBDA_REQUIRED_SIGN", str(index))
        _need(proof.get("monkeypatch_used") is False,
              "FAIL_FLAMBDA_MONKEYPATCH", str(index))
        for key, expected in proof_expectations.items():
            _need(proof.get(key) == expected,
                  "FAIL_FLAMBDA_PROOF_CONTRACT", f"{index}:{key}")
        _need(proof.get("policy") == bcfg["route_policies"]["F_LAMBDA_ROUTE"],
              "FAIL_FLAMBDA_POLICY", str(index))
        _need(proof.get("effective_evaluation_cap") == FLAMBDA_CELL_CALL_CAP,
              "FAIL_FLAMBDA_EFFECTIVE_CAP", str(index))
        _need(proof.get("normalization_bits") == model.NORMALIZATION_BITS,
              "FAIL_FLAMBDA_NORMALIZATION_BITS", str(index))
        _need(isinstance(used, int) and 0 <= used <= FLAMBDA_CELL_CALL_CAP,
              "FAIL_FLAMBDA_BUDGET", str(index))
        records.append({
            "tile_index": index,
            "lambda_interval": _interval_fraction_json(llo, lhi),
            "normalized_enclosure": enclosure,
            "evaluation_count": used,
            "proof_id": proof.get("proof_id"),
            "route_id": proof.get("route_id"),
            "complete_closed_cover": proof.get("complete_closed_cover"),
            "proof_contract": {
                key: proof.get(key) for key in sorted(proof_expectations)
            },
            "policy": proof.get("policy"),
            "effective_evaluation_cap": proof.get("effective_evaluation_cap"),
            "normalization_bits": proof.get("normalization_bits"),
            "ordered_children": proof.get("ordered_children"),
            "split_reasons": proof.get("split_reasons"),
        })
    return records


def produce(
    *,
    expected_head: str,
    candidate_index: int,
    cell_index: int,
) -> dict[str, Any]:
    pre = _precheck(expected_head)
    config, _ = load_config()
    require_blocal_dependency(config)
    _need(config["dps"] > 0, "FAIL_PRODUCER_DPS")
    _need(config["checker_dps"] >= config["dps"], "FAIL_CHECKER_DPS_CONTRACT")

    raw_kernel, kernel_path = load_production_kernel()
    from flint import acb, arb, fmpq, ctx
    ctx.dps = config["dps"]

    exact_f = ExactLambdaRoutedEvaluator(raw_kernel, arb, config)
    exact_f.set_phase(f"CANDIDATE:{candidate_index}")
    geometry = _reconstruct_geometry(
        config=config,
        exact_kernel=exact_f,
        arb_type=arb,
        candidate_index=candidate_index,
        cell_index=cell_index,
    )
    llo = geometry["lambda_left"]
    lhi = geometry["lambda_right"]
    tiles = _residual_tiling(llo, lhi)
    r_lo = geometry["domain"].lo
    r_hi = geometry["domain"].hi

    anchor_hi = _anchor_record(
        evaluator=exact_f,
        endpoint=r_hi,
        lam=llo,
        required_sign="NEG",
        config=config,
    )
    anchor_lo = _anchor_record(
        evaluator=exact_f,
        endpoint=r_lo,
        lam=lhi,
        required_sign="POS",
        config=config,
    )

    import blocal_arb_adapter as adapter
    import blocal_v22_model as model
    import blocal_v23_boundary as route

    native = pre["native_manifest"]
    _need(native.get("ordinary_formula_id") == route.fk.ORDINARY_FORMULA_ID,
          "FAIL_ORDINARY_FORMULA_RUNTIME_ID")
    _need(native.get("duffy_formula_id") == route.fk.DUFFY_FORMULA_ID,
          "FAIL_DUFFY_FORMULA_RUNTIME_ID")
    _need(route.TRANSPORT_LEMMA_ID == TRANSPORT_LEMMA_ID,
          "FAIL_TRANSPORT_RUNTIME_ID")
    proof_expectations = {
        "native_quantity": True,
        "ordinary_formula_id": route.fk.ORDINARY_FORMULA_ID,
        "duffy_formula_id": route.fk.DUFFY_FORMULA_ID,
        "transport_lemma_id": TRANSPORT_LEMMA_ID,
        "angular_policy_id": route.policy.ANGULAR_POLICY_ID,
        "denominator_policy_id": route.policy.DENOMINATOR_POLICY_ID,
        "sqrt_policy_id": route.policy.SQRT_POLICY_ID,
        "gamma_policy_id": route.policy.GAMMA_POLICY_ID,
        "q_lo_policy_id": route.policy.Q_LO_POLICY_ID,
        "normalization_policy_id": route.policy.NORMALIZATION_POLICY_ID,
    }

    bcfg = _load_v23_boundary_config()
    hi_cells = _flambda_records(
        route=route, model=model, adapter=adapter, raw_kernel=raw_kernel,
        acb_type=acb, arb_type=arb, fmpq_type=fmpq, bcfg=bcfg,
        endpoint=r_hi, tiles=tiles, proof_expectations=proof_expectations,
    )
    lo_cells = _flambda_records(
        route=route, model=model, adapter=adapter, raw_kernel=raw_kernel,
        acb_type=acb, arb_type=arb, fmpq_type=fmpq, bcfg=bcfg,
        endpoint=r_lo, tiles=tiles, proof_expectations=proof_expectations,
    )

    total_anchor = anchor_hi["evaluation_count"] + anchor_lo["evaluation_count"]
    total_flambda = (
        sum(x["evaluation_count"] for x in hi_cells)
        + sum(x["evaluation_count"] for x in lo_cells)
    )
    declared_parent_cap = (
        2 * ANCHOR_CALL_CAP + 2 * len(tiles) * FLAMBDA_CELL_CALL_CAP
    )
    _need(total_anchor + total_flambda <= declared_parent_cap,
          "FAIL_PARENT_TOTAL_BUDGET")

    result = {
        "schema": PRODUCER_SCHEMA,
        "status": PRODUCER_STATUS,
        "evidence_class": PRODUCER_EVIDENCE_CLASS,
        "binding_use_authorized": False,
        "producer_role": "AI1_PRODUCER",
        "checker_required": True,
        "human_promotion_required": True,
        "execution_head": expected_head,
        "source_baseline_head": pre["source_baseline_head"],
        "producer_source_sha256": pre["actual"]["producer_source_sha256"],
        "pins": pre["pins"],
        "legacy_snapshot_verified": pre["legacy_snapshot"],
        "production_kernel": {
            "path": kernel_path.relative_to(REPO_ROOT).as_posix(),
            "sha256": hashlib.sha256(kernel_path.read_bytes()).hexdigest(),
        },
        "producer_dps": config["dps"],
        "candidate_index": candidate_index,
        "cell_index": cell_index,
        "candidate_parent": _interval_fraction_json(llo, lhi),
        "nominal_lambda_width": geometry["nominal_width"].to_json(),
        "radius_cap": geometry["radius_cap"].to_json(),
        "predictor": {
            "q_left": geometry["q_left"].to_json(),
            "q_right": geometry["q_right"].to_json(),
        },
        "adaptive_radius": geometry["rho"].to_json(),
        "tube_interval": geometry["domain"].to_json(),
        "r_lo": r_lo.to_json(),
        "r_hi": r_hi.to_json(),
        "base_tile": _fraction_json(FLAMBDA_BASE_TILE),
        "tiles": [
            _interval_fraction_json(a, b) for a, b in tiles
        ],
        "anchors": {
            "R_HI_LEFT_NEG": anchor_hi,
            "R_LO_RIGHT_POS": anchor_lo,
        },
        "flambda": {
            "route_id": FLAMBDA_ROUTE_ID,
            "required_sign": "NEG",
            "proof_expectations": proof_expectations,
            "R_HI": hi_cells,
            "R_LO": lo_cells,
        },
        "transport": {
            "lemma_id": TRANSPORT_LEMMA_ID,
            "human_audit": TRANSPORT_AUDIT_STATUS,
            "R_HI_rule": "F(r_hi,lambda)=F(r_hi,lambda_L)+integral(F_lambda)",
            "R_LO_rule": "F(r_lo,lambda)=F(r_lo,lambda_R)-integral(F_lambda)",
            "R_HI_transported_sign": "NEG",
            "R_LO_transported_sign": "POS",
        },
        "budgets": {
            "anchor_call_cap": ANCHOR_CALL_CAP,
            "flambda_cell_call_cap": FLAMBDA_CELL_CALL_CAP,
            "tile_count": len(tiles),
            "declared_parent_total_cap": declared_parent_cap,
            "anchor_evaluation_count": total_anchor,
            "flambda_evaluation_count": total_flambda,
            "total_evaluation_count": total_anchor + total_flambda,
            "post_hoc_cap_increase": "FORBIDDEN",
        },
        "producer_verdict": "PASS_BINDING_CANDIDATE",
    }

    _need(_git("rev-parse", "HEAD") == expected_head, "FAIL_POST_HEAD_MOVED")
    _need(not _git("status", "--porcelain"), "FAIL_POST_SOURCE_DIRTY")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-index", type=int, default=0)
    parser.add_argument("--cell-index", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    expected_head = os.environ.get("EXPECTED_HEAD")
    if not expected_head:
        raise SystemExit("STOP: set EXPECTED_HEAD to exact producer execution HEAD")
    try:
        result = produce(
            expected_head=expected_head,
            candidate_index=args.candidate_index,
            cell_index=args.cell_index,
        )
    except ProducerFailure as exc:
        print(f"PRODUCER_FAILURE_CODE={exc.code}")
        if exc.detail is not None:
            print(f"PRODUCER_FAILURE_DETAIL={exc.detail}")
        raise SystemExit(2) from exc
    raw = canonical_json_bytes(result)
    if args.output is not None:
        args.output.write_bytes(raw)
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())