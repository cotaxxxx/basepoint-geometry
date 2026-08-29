#!/usr/bin/env python3
"""Independent B-TUBE v2.1 checker glue for native B-LOCAL v2.3 F_lambda transport.

AI2 checker.  This module deliberately does not import producer glue.
Producer/checker byte or evaluation-count agreement is report-only; independently
reconstructed geometry, strict signs, closed covers, proof contracts, budgets,
and the human-audited transport-lemma gate are binding-candidate gates.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
V23 = HERE / "dependencies/blocal_v23_source"

CHECKER_SOURCE = HERE / "flambda_transport_checker_v1.py"
NC_SOURCE = HERE / "flambda_transport_checker_v1_negative_controls.py"
PIN_FILE = V23 / "F_LAMBDA_TRANSPORT_CHECKER_V1_PINS.json"
SOURCE_MANIFEST = V23 / "BLOCAL_V23_SOURCE_MANIFEST.json"
BOUNDARY = V23 / "blocal_v23_boundary.py"
SHARED_KERNEL = V23 / "blocal_v23_flambda_kernel.py"
ROUTE_FRAGMENT = V23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json"
BLOCAL_RUN_CONFIG = V23 / "config.blocal-v2.2-run.json"
TRANSPORT_PIN_FILE = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1_PINS.json"
TRANSPORT_RECEIPT = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1.md"
JUDGE_SIGNATURE = V23 / "F_LAMBDA_TRANSPORT_LEMMA_V1_JUDGE_SIGNATURE.json"
CALIBRATION_CONFIG = HERE / "config.calibration.json"

CHECKER_SCHEMA = "btube-flambda-transport-checker-v1"
CHECKER_STATUS = "INDEPENDENT_CHECK_PASS_NOT_PROMOTED"
CHECKER_EVIDENCE_CLASS = "BINDING_CANDIDATE_CHECK"
PRODUCER_SCHEMA = "btube-flambda-transport-producer-v1"
PRODUCER_PASS = "PASS_BINDING_CANDIDATE"

FLAMBDA_ROUTE_ID = "BLOCAL_FLAMBDA_ROUTE_V1"
TRANSPORT_LEMMA_ID = "F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1"
TRANSPORT_AUDIT_STATUS = "PASS_CURRENT_STRICT_INTERIOR_SCOPE"
TRANSPORT_SCOPE = "CURRENT_STRICT_INTERIOR_ENDPOINT_SCOPE"
FLAMBDA_BASE_TILE = Fraction(1, 16)
CHECKER_ANCHOR_CALL_CAP = 24000
CHECKER_FLAMBDA_CELL_CALL_CAP = 24000
TOL = "1e-20"

FORBIDDEN_PRODUCER_MODULE = "flambda_transport_producer_v1"
FORBIDDEN_PRODUCER_PATH = HERE / "flambda_transport_producer_v1.py"

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V23))

from calibration_context import (  # noqa: E402
    CalibrationError,
    D_ONE,
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    canonical_json_bytes,
)
from calibration_config import load_config, require_blocal_dependency  # noqa: E402
from calibration_runner import load_production_kernel  # noqa: E402
from exact_lambda_transport import ExactLambdaRoutedEvaluator  # noqa: E402
from numeric_schema import parse_canonical_json_bytes  # noqa: E402


class CheckerFailure(RuntimeError):
    """Fail-closed checker error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str | None = None):
        self.code = code
        self.detail = detail
        super().__init__(code if detail is None else f"{code}:{detail}")


def _need(condition: bool, code: str, detail: str | None = None) -> None:
    if not condition:
        raise CheckerFailure(code, detail)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO_ROOT), *args], text=True
    ).strip()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CheckerFailure("FAIL_JSON_LOAD", path.name) from exc
    _need(isinstance(obj, dict), "FAIL_JSON_OBJECT", path.name)
    return obj


def _fraction_json(value: Fraction) -> dict[str, str]:
    return Rational.from_fraction(value).to_json()


def _interval_fraction_json(lo: Fraction, hi: Fraction) -> dict[str, Any]:
    _need(lo <= hi, "FAIL_INTERVAL_ORDER")
    return {"lo": _fraction_json(lo), "hi": _fraction_json(hi)}


def _fraction_from_json(obj: Any, where: str) -> Fraction:
    return Rational.from_json(obj, where).as_fraction()


def _dyadic_from_json(obj: Any, where: str) -> Dyadic:
    return Dyadic.from_json(obj, where)


def _dyadic_interval_from_json(obj: Any, where: str) -> DyadicInterval:
    return DyadicInterval.from_json(obj, where)


def _assert_checker_independence() -> dict[str, Any]:
    """NC20 contract: source and runtime producer-glue independence."""
    try:
        tree = ast.parse(CHECKER_SOURCE.read_text(encoding="utf-8"))
    except Exception as exc:
        raise CheckerFailure("FAIL_CHECKER_SOURCE_PARSE") from exc

    forbidden_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_PRODUCER_MODULE:
                    forbidden_imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module == FORBIDDEN_PRODUCER_MODULE:
                forbidden_imports.append(node.module)
    _need(
        not forbidden_imports,
        "FAIL_PRODUCER_GLUE_DEPENDENCY",
        "source_import:" + ",".join(forbidden_imports),
    )

    runtime_hits: list[str] = []
    producer_path = FORBIDDEN_PRODUCER_PATH.resolve()
    for name, module in list(sys.modules.items()):
        if name == FORBIDDEN_PRODUCER_MODULE:
            runtime_hits.append(name)
            continue
        path = getattr(module, "__file__", None)
        if not path:
            continue
        try:
            if Path(path).resolve() == producer_path:
                runtime_hits.append(name)
        except (OSError, RuntimeError):
            continue
    _need(
        not runtime_hits,
        "FAIL_PRODUCER_GLUE_DEPENDENCY",
        "runtime_module:" + ",".join(sorted(set(runtime_hits))),
    )
    return {
        "source_import_free": True,
        "runtime_module_free": True,
        "forbidden_module": FORBIDDEN_PRODUCER_MODULE,
    }


def _verify_legacy_snapshot(manifest: dict[str, Any]) -> dict[str, str]:
    snapshot = manifest.get("legacy_snapshot")
    _need(
        isinstance(snapshot, dict) and snapshot,
        "FAIL_LEGACY_SNAPSHOT_MANIFEST",
    )
    actual: dict[str, str] = {}
    for name, expected in sorted(snapshot.items()):
        _need(
            isinstance(name, str) and isinstance(expected, str),
            "FAIL_LEGACY_SNAPSHOT_ENTRY",
        )
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
    _need(PIN_FILE.is_file(), "FAIL_CHECKER_PIN_FILE_MISSING")

    pins = _load_json(PIN_FILE)
    _need(
        pins.get("schema") == "btube-flambda-transport-checker-v1-pins",
        "FAIL_CHECKER_PIN_SCHEMA",
    )
    source_baseline = pins.get("source_baseline_head")
    _need(
        isinstance(source_baseline, str) and len(source_baseline) == 40,
        "FAIL_SOURCE_BASELINE_PIN",
    )
    try:
        subprocess.check_call(
            [
                "git",
                "-C",
                str(REPO_ROOT),
                "merge-base",
                "--is-ancestor",
                source_baseline,
                expected_head,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise CheckerFailure("FAIL_SOURCE_BASELINE_ANCESTRY") from exc

    allowed_after_baseline = {
        PIN_FILE.relative_to(REPO_ROOT).as_posix(),
    }
    changed = {
        line
        for line in _git(
            "diff", "--name-only", f"{source_baseline}..{expected_head}"
        ).splitlines()
        if line
    }
    _need(
        changed == allowed_after_baseline,
        "FAIL_POST_BASELINE_FILE_SET",
        ",".join(sorted(changed)),
    )

    actual = {
        "checker_source_sha256": _sha(CHECKER_SOURCE),
        "negative_controls_source_sha256": _sha(NC_SOURCE),
        "boundary_sha256": _sha(BOUNDARY),
        "shared_kernel_sha256": _sha(SHARED_KERNEL),
        "source_manifest_sha256": _sha(SOURCE_MANIFEST),
        "route_fragment_sha256": _sha(ROUTE_FRAGMENT),
        "calibration_config_sha256": _sha(CALIBRATION_CONFIG),
        "transport_pin_file_sha256": _sha(TRANSPORT_PIN_FILE),
        "transport_receipt_sha256": _sha(TRANSPORT_RECEIPT),
        "judge_signature_sha256": _sha(JUDGE_SIGNATURE),
    }
    for key, got in actual.items():
        _need(pins.get(key) == got, "FAIL_PIN_MISMATCH", key)

    _need(
        pins.get("checker_anchor_call_cap") == CHECKER_ANCHOR_CALL_CAP,
        "FAIL_CHECKER_ANCHOR_CAP_PIN",
    )
    _need(
        pins.get("checker_flambda_cell_call_cap")
        == CHECKER_FLAMBDA_CELL_CALL_CAP,
        "FAIL_CHECKER_FLAMBDA_CAP_PIN",
    )
    _need(
        pins.get("base_tile") == {"p": "1", "q": "16"},
        "FAIL_CHECKER_TILE_PIN",
    )
    _need(
        pins.get("binding_use_authorized") is False,
        "FAIL_BINDING_AUTHORIZATION_STATE",
    )

    manifest = _load_json(SOURCE_MANIFEST)
    _need(
        manifest.get("binding_use_authorized") is False,
        "FAIL_MANIFEST_BINDING_AUTHORIZATION",
    )
    legacy = _verify_legacy_snapshot(manifest)
    native = manifest.get("native_route")
    _need(isinstance(native, dict), "FAIL_NATIVE_MANIFEST")
    _need(native.get("route_id") == FLAMBDA_ROUTE_ID, "FAIL_ROUTE_ID_PIN")
    _need(native.get("quantity") == "F_lambda", "FAIL_QUANTITY_PIN")
    _need(native.get("required_sign") == "NEG", "FAIL_REQUIRED_SIGN_PIN")
    _need(
        native.get("required_sign_input_policy")
        == "EXPLICIT_MANDATORY_FAIL_CLOSED",
        "FAIL_REQUIRED_SIGN_POLICY",
    )
    _need(
        native.get("boundary_sha256") == actual["boundary_sha256"],
        "FAIL_BOUNDARY_MANIFEST_PIN",
    )
    _need(
        native.get("shared_kernel_sha256") == actual["shared_kernel_sha256"],
        "FAIL_KERNEL_MANIFEST_PIN",
    )
    _need(
        native.get("transport_lemma_id") == TRANSPORT_LEMMA_ID,
        "FAIL_TRANSPORT_LEMMA_ID",
    )
    _need(
        native.get("symbolic_reaudit_required") is False,
        "FAIL_SYMBOLIC_REAUDIT_REQUIRED",
    )
    _need(
        native.get("symbolic_reaudit_status") == "PASS_CONTENT_LEVEL",
        "FAIL_SYMBOLIC_REAUDIT_STATUS",
    )
    _need(
        isinstance(native.get("ordinary_formula_id"), str),
        "FAIL_ORDINARY_FORMULA_ID_PIN",
    )
    _need(
        isinstance(native.get("duffy_formula_id"), str),
        "FAIL_DUFFY_FORMULA_ID_PIN",
    )

    return {
        "pins": pins,
        "actual": actual,
        "source_baseline_head": source_baseline,
        "manifest": manifest,
        "native_manifest": native,
        "legacy_snapshot_verified": legacy,
    }


def _load_producer_receipt(path: Path) -> tuple[dict[str, Any], str]:
    _need(path.is_file(), "FAIL_PRODUCER_RECEIPT_MISSING")
    raw = path.read_bytes()
    try:
        obj = parse_canonical_json_bytes(raw)
    except Exception as exc:
        raise CheckerFailure("FAIL_PRODUCER_RECEIPT_CANONICAL_JSON") from exc
    _need(isinstance(obj, dict), "FAIL_PRODUCER_RECEIPT_OBJECT")
    _need(obj.get("schema") == PRODUCER_SCHEMA, "FAIL_PRODUCER_SCHEMA")
    _need(
        obj.get("evidence_class") == "BINDING_CANDIDATE",
        "FAIL_PRODUCER_EVIDENCE_CLASS",
    )
    _need(obj.get("binding_use_authorized") is False, "FAIL_PRODUCER_BINDING_STATE")
    _need(obj.get("checker_required") is True, "FAIL_PRODUCER_CHECKER_REQUIRED")
    _need(
        obj.get("human_promotion_required") is True,
        "FAIL_PRODUCER_HUMAN_PROMOTION_REQUIRED",
    )
    _need(obj.get("producer_verdict") == PRODUCER_PASS, "FAIL_PRODUCER_VERDICT")
    return obj, hashlib.sha256(raw).hexdigest()


def _candidate_pair(config: dict[str, Any], candidate_index: int) -> tuple[Dyadic, Dyadic]:
    widths_raw = config.get("candidate_lambda_widths")
    radii_raw = config.get("candidate_tube_radii")
    _need(
        isinstance(widths_raw, list)
        and widths_raw
        and isinstance(radii_raw, list)
        and radii_raw,
        "FAIL_CANDIDATE_CONFIG",
    )
    widths = [
        Dyadic.from_json(x, f"candidate_lambda_widths[{i}]")
        for i, x in enumerate(widths_raw)
    ]
    radii = [
        Dyadic.from_json(x, f"candidate_tube_radii[{i}]")
        for i, x in enumerate(radii_raw)
    ]
    count = len(widths) * len(radii)
    _need(0 <= candidate_index < count, "FAIL_CANDIDATE_INDEX")
    wi, ri = divmod(candidate_index, len(radii))
    return widths[wi], radii[ri]


def _reconstruct_tube_geometry(
    producer: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Stage 3: q inputs -> q_hull, rho, exact physical tube."""
    candidate_index = producer.get("candidate_index")
    _need(
        isinstance(candidate_index, int) and not isinstance(candidate_index, bool),
        "FAIL_CANDIDATE_INDEX",
    )
    width, radius_cap = _candidate_pair(config, candidate_index)

    predictor = producer.get("predictor")
    _need(isinstance(predictor, dict), "FAIL_PREDICTOR_INPUT")
    q_left = _dyadic_from_json(predictor.get("q_left"), "predictor.q_left")
    q_right = _dyadic_from_json(predictor.get("q_right"), "predictor.q_right")
    q_lo = q_left if q_left <= q_right else q_right
    q_hi = q_right if q_left <= q_right else q_left
    q_hull = DyadicInterval(q_lo, q_hi)

    sigma = Dyadic.from_json(
        config["adaptive_safety_factor"], "adaptive_safety_factor"
    )
    _need(D_ZERO < sigma and sigma < D_ONE, "FAIL_ADAPTIVE_SIGMA")
    _need(D_ZERO < radius_cap, "FAIL_RADIUS_CAP")

    left_margin = q_hull.lo
    right_margin = D_ONE - q_hull.hi
    _need(
        D_ZERO < left_margin and D_ZERO < right_margin,
        "FAIL_PREDICTOR_HULL_INTERIOR",
    )
    candidates = [
        radius_cap,
        sigma * left_margin,
        sigma * right_margin,
    ]
    rho = candidates[0]
    for candidate in candidates[1:]:
        if candidate < rho:
            rho = candidate
    _need(D_ZERO < rho, "FAIL_ADAPTIVE_RADIUS")

    domain = DyadicInterval(q_hull.lo - rho, q_hull.hi + rho)
    _need(
        D_ZERO < domain.lo and domain.hi < D_ONE,
        "FAIL_STRICT_INTERIOR_ENDPOINT_SCOPE",
    )

    expected = {
        "nominal_lambda_width": width,
        "radius_cap": radius_cap,
        "adaptive_radius": rho,
        "tube_interval": domain,
        "r_lo": domain.lo,
        "r_hi": domain.hi,
    }

    try:
        observed_width = _dyadic_from_json(
            producer["nominal_lambda_width"], "nominal_lambda_width"
        )
        observed_cap = _dyadic_from_json(producer["radius_cap"], "radius_cap")
        observed_rho = _dyadic_from_json(
            producer["adaptive_radius"], "adaptive_radius"
        )
        observed_tube = _dyadic_interval_from_json(
            producer["tube_interval"], "tube_interval"
        )
        observed_lo = _dyadic_from_json(producer["r_lo"], "r_lo")
        observed_hi = _dyadic_from_json(producer["r_hi"], "r_hi")
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckerFailure("FAIL_TUBE_GEOMETRY_RECONSTRUCTION", "missing_or_bad_field") from exc

    _need(
        observed_width == width
        and observed_cap == radius_cap
        and observed_rho == rho
        and observed_tube == domain
        and observed_lo == domain.lo
        and observed_hi == domain.hi,
        "FAIL_TUBE_GEOMETRY_RECONSTRUCTION",
    )

    return {
        "q_left": q_left,
        "q_right": q_right,
        "q_hull": q_hull,
        "sigma": sigma,
        "radius_cap": radius_cap,
        "rho": rho,
        "left_margin": left_margin,
        "right_margin": right_margin,
        "domain": domain,
        "nominal_width": width,
    }


def _reconstruct_lambda_geometry(
    producer: dict[str, Any],
    config: dict[str, Any],
    nominal_width: Dyadic,
) -> dict[str, Any]:
    """Stage 4: lambda_start, W_nom, cell index -> parent and exact tiling."""
    cell_index = producer.get("cell_index")
    _need(
        isinstance(cell_index, int) and not isinstance(cell_index, bool) and cell_index >= 0,
        "FAIL_CELL_INDEX",
    )
    _need(cell_index < config["max_cells"], "FAIL_CELL_INDEX")

    start = Rational.from_json(
        config["blocal_dependency"]["lambda_start"],
        "blocal_dependency.lambda_start",
    ).as_fraction()
    end = Rational.from_json(config["lambda_end"], "lambda_end").as_fraction()
    width = nominal_width.as_fraction()
    _need(width > 0 and start < end, "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION")

    lambda_left = start + cell_index * width
    _need(lambda_left < end, "FAIL_CELL_INDEX")
    lambda_right = min(lambda_left + width, end)
    _need(lambda_left < lambda_right, "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION")

    tiles: list[tuple[Fraction, Fraction]] = []
    left = lambda_left
    while left < lambda_right:
        right = min(left + FLAMBDA_BASE_TILE, lambda_right)
        _need(left < right, "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION")
        tiles.append((left, right))
        left = right

    try:
        parent = producer["candidate_parent"]
        observed_left = _fraction_from_json(parent["lo"], "candidate_parent.lo")
        observed_right = _fraction_from_json(parent["hi"], "candidate_parent.hi")
        observed_base = _fraction_from_json(producer["base_tile"], "base_tile")
        observed_tiles = [
            (
                _fraction_from_json(x["lo"], f"tiles[{i}].lo"),
                _fraction_from_json(x["hi"], f"tiles[{i}].hi"),
            )
            for i, x in enumerate(producer["tiles"])
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise CheckerFailure(
            "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION", "missing_or_bad_field"
        ) from exc

    _need(
        observed_left == lambda_left
        and observed_right == lambda_right
        and observed_base == FLAMBDA_BASE_TILE
        and observed_tiles == tiles,
        "FAIL_LAMBDA_GEOMETRY_RECONSTRUCTION",
    )

    return {
        "lambda_start": start,
        "lambda_end": end,
        "lambda_left": lambda_left,
        "lambda_right": lambda_right,
        "nominal_width": width,
        "tiles": tiles,
    }


def _load_v23_boundary_config() -> dict[str, Any]:
    bcfg = _load_json(BLOCAL_RUN_CONFIG)
    frag = _load_json(ROUTE_FRAGMENT)
    _need(frag.get("route_id") == FLAMBDA_ROUTE_ID, "FAIL_ROUTE_FRAGMENT_ID")
    _need(
        frag.get("native_quantity") == "F_lambda",
        "FAIL_ROUTE_FRAGMENT_QUANTITY",
    )
    _need(frag.get("required_sign") == "NEG", "FAIL_ROUTE_FRAGMENT_SIGN")
    policies = frag.get("route_policies")
    _need(isinstance(policies, dict), "FAIL_ROUTE_FRAGMENT_POLICY")
    bcfg.setdefault("route_policies", {}).update(policies)
    return bcfg


def _verify_transport_gate(
    pre: dict[str, Any],
    route: Any,
    model: Any,
    bcfg: dict[str, Any],
) -> dict[str, Any]:
    """Stage 5: runtime formula identities plus receipt/signature SHA gate."""
    actual = pre["actual"]
    native = pre["native_manifest"]

    _need(
        native.get("ordinary_formula_id") == route.fk.ORDINARY_FORMULA_ID,
        "FAIL_ORDINARY_FORMULA_RUNTIME_ID",
    )
    _need(
        native.get("duffy_formula_id") == route.fk.DUFFY_FORMULA_ID,
        "FAIL_DUFFY_FORMULA_RUNTIME_ID",
    )
    _need(
        route.TRANSPORT_LEMMA_ID == TRANSPORT_LEMMA_ID,
        "FAIL_TRANSPORT_RUNTIME_ID",
    )

    lemma_pins = _load_json(TRANSPORT_PIN_FILE)
    _need(
        lemma_pins.get("receipt_sha256") == actual["transport_receipt_sha256"],
        "FAIL_TRANSPORT_RECEIPT_PIN",
    )
    _need(
        lemma_pins.get("judge_signature_sha256")
        == actual["judge_signature_sha256"],
        "FAIL_JUDGE_SIGNATURE_PIN",
    )
    _need(lemma_pins.get("judge_verdict") == "PASS", "FAIL_JUDGE_VERDICT")
    _need(
        lemma_pins.get("transport_lemma_human_audit") == TRANSPORT_AUDIT_STATUS,
        "FAIL_TRANSPORT_HUMAN_AUDIT",
    )
    _need(
        lemma_pins.get("lemma_id") == TRANSPORT_LEMMA_ID,
        "FAIL_TRANSPORT_LEMMA_ID",
    )
    _need(
        lemma_pins.get("scope") == TRANSPORT_SCOPE,
        "FAIL_TRANSPORT_SCOPE",
    )

    signature = _load_json(JUDGE_SIGNATURE)
    _need(
        signature.get("receipt_sha256") == actual["transport_receipt_sha256"],
        "FAIL_SIGNATURE_RECEIPT_LINK",
    )
    _need(signature.get("judge_verdict") == "PASS", "FAIL_SIGNATURE_VERDICT")
    _need(
        signature.get("judge_scope") == TRANSPORT_SCOPE,
        "FAIL_SIGNATURE_SCOPE",
    )
    _need(
        signature.get("signer_role") == "HUMAN_JUDGE",
        "FAIL_SIGNATURE_ROLE",
    )

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
    _need(
        isinstance(
            bcfg.get("route_policies", {}).get("F_LAMBDA_ROUTE"),
            dict,
        ),
        "FAIL_FLAMBDA_POLICY_RUNTIME",
    )
    _need(
        model.NORMALIZATION_BITS > 0,
        "FAIL_FLAMBDA_NORMALIZATION_BITS",
    )
    return {
        "receipt_sha256": actual["transport_receipt_sha256"],
        "judge_signature_sha256": actual["judge_signature_sha256"],
        "judge_verdict": signature["judge_verdict"],
        "judge_scope": signature["judge_scope"],
        "human_audit": lemma_pins["transport_lemma_human_audit"],
        "ordinary_formula_id": route.fk.ORDINARY_FORMULA_ID,
        "duffy_formula_id": route.fk.DUFFY_FORMULA_ID,
        "proof_expectations": proof_expectations,
        "transport_gate_pass": True,
    }


def _derive_anchor_contract(
    target_sign: str, derivative_sign: str
) -> dict[str, str]:
    """Stage 10: derive anchor side from monotonicity, not producer fields."""
    _need(derivative_sign == "NEG", "FAIL_TRANSPORT_DERIVATIVE_SIGN_CONTRACT")
    if target_sign == "NEG":
        return {
            "target_sign": "NEG",
            "derivative_sign": "NEG",
            "anchor_side": "LEFT",
            "anchor_required_sign": "NEG",
            "transport_direction": "ADDITIVE_FROM_LEFT",
        }
    if target_sign == "POS":
        return {
            "target_sign": "POS",
            "derivative_sign": "NEG",
            "anchor_side": "RIGHT",
            "anchor_required_sign": "POS",
            "transport_direction": "SUBTRACTIVE_FROM_RIGHT",
        }
    raise CheckerFailure("FAIL_TARGET_SIGN_CONTRACT")


def _anchor_check(
    *,
    evaluator: Any,
    endpoint: Dyadic,
    lam: Fraction,
    required_sign: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    try:
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
    except CalibrationError as exc:
        raise CheckerFailure("FAIL_ANCHOR_EVALUATION", str(exc)) from exc

    _need(isinstance(evidence, dict), "FAIL_ANCHOR_EVIDENCE")
    _need(evidence.get("quantity") == "F", "FAIL_ANCHOR_QUANTITY")
    _need(
        evidence.get("post_failure_fallback") is False,
        "FAIL_ANCHOR_POST_FAILURE_FALLBACK",
    )
    used = evidence.get("boundary_route_evaluation_count_delta")
    _need(
        isinstance(used, int) and 0 <= used <= CHECKER_ANCHOR_CALL_CAP,
        "FAIL_ANCHOR_BUDGET",
    )
    if required_sign == "NEG":
        _need(interval.hi < D_ZERO, "FAIL_ANCHOR_SIGN_NEG")
    elif required_sign == "POS":
        _need(D_ZERO < interval.lo, "FAIL_ANCHOR_SIGN_POS")
    else:
        raise CheckerFailure("FAIL_ANCHOR_SIGN_CONTRACT")

    return {
        "lambda": _fraction_json(lam),
        "required_sign": required_sign,
        "enclosure": interval.to_json(),
        "evaluation_count": used,
        "detail": evidence.get("detail"),
    }


def _flambda_check(
    *,
    route: Any,
    model: Any,
    adapter: Any,
    raw_kernel: Any,
    acb_type: Any,
    arb_type: Any,
    fmpq_type: Any,
    bcfg: dict[str, Any],
    endpoint: Dyadic,
    tiles: list[tuple[Fraction, Fraction]],
    proof_expectations: dict[str, Any],
    side: str,
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
                evaluation_cap=CHECKER_FLAMBDA_CELL_CALL_CAP,
            )
        except route.ContractFailure as exc:
            raise CheckerFailure("FAIL_FLAMBDA_CONTRACT", exc.code) from exc
        except route.base.EnclosureFailure as exc:
            raise CheckerFailure(
                "FAIL_FLAMBDA_BUDGET_OR_ENCLOSURE", f"{side}:{index}:{exc.reason}"
            ) from exc

        lo, hi = model.interval_fractions(
            enclosure, f"checker {side} F_lambda tile {index}"
        )
        used = proof.get("evaluation_count")
        _need(hi < 0, "FAIL_FLAMBDA_SIGN", f"{side}:{index}")
        _need(
            proof.get("complete_closed_cover") is True,
            "FAIL_FLAMBDA_COVER",
            f"{side}:{index}",
        )
        _need(
            proof.get("route_id") == FLAMBDA_ROUTE_ID,
            "FAIL_FLAMBDA_ROUTE",
            f"{side}:{index}",
        )
        _need(
            proof.get("quantity") == "F_lambda",
            "FAIL_FLAMBDA_QUANTITY",
            f"{side}:{index}",
        )
        _need(
            proof.get("required_sign") == "NEG",
            "FAIL_FLAMBDA_REQUIRED_SIGN",
            f"{side}:{index}",
        )
        _need(
            proof.get("monkeypatch_used") is False,
            "FAIL_FLAMBDA_MONKEYPATCH",
            f"{side}:{index}",
        )
        for key, expected in proof_expectations.items():
            _need(
                proof.get(key) == expected,
                "FAIL_FLAMBDA_PROOF_CONTRACT",
                f"{side}:{index}:{key}",
            )
        _need(
            proof.get("policy") == bcfg["route_policies"]["F_LAMBDA_ROUTE"],
            "FAIL_FLAMBDA_POLICY",
            f"{side}:{index}",
        )
        _need(
            proof.get("effective_evaluation_cap")
            == CHECKER_FLAMBDA_CELL_CALL_CAP,
            "FAIL_FLAMBDA_EFFECTIVE_CAP",
            f"{side}:{index}",
        )
        _need(
            proof.get("normalization_bits") == model.NORMALIZATION_BITS,
            "FAIL_FLAMBDA_NORMALIZATION_BITS",
            f"{side}:{index}",
        )
        _need(
            isinstance(used, int)
            and 0 <= used <= CHECKER_FLAMBDA_CELL_CALL_CAP,
            "FAIL_FLAMBDA_BUDGET",
            f"{side}:{index}",
        )
        records.append(
            {
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
            }
        )
    return records


def _report_tile_matches(
    producer: dict[str, Any],
    checker_records: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    """Producer/checker identity is explicitly report-only."""
    out: dict[str, Any] = {"gating": False, "sides": {}}
    p_flambda = producer.get("flambda")
    if not isinstance(p_flambda, dict):
        out["available"] = False
        return out
    out["available"] = True
    for side in ("R_HI", "R_LO"):
        p_rows = p_flambda.get(side)
        c_rows = checker_records[side]
        rows = []
        if not isinstance(p_rows, list):
            out["sides"][side] = {"available": False, "rows": []}
            continue
        for i, c in enumerate(c_rows):
            p = p_rows[i] if i < len(p_rows) and isinstance(p_rows[i], dict) else None
            rows.append(
                {
                    "tile_index": i,
                    "producer_available": p is not None,
                    "enclosure_equal": (
                        p is not None
                        and p.get("normalized_enclosure")
                        == c["normalized_enclosure"]
                    ),
                    "evaluation_count_equal": (
                        p is not None
                        and p.get("evaluation_count") == c["evaluation_count"]
                    ),
                    "ordered_children_equal": (
                        p is not None
                        and p.get("ordered_children") == c["ordered_children"]
                    ),
                }
            )
        out["sides"][side] = {
            "available": True,
            "row_count_equal": len(p_rows) == len(c_rows),
            "rows": rows,
        }
    return out


def _report_anchor_matches(
    producer: dict[str, Any],
    checker_anchors: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    out: dict[str, Any] = {"gating": False, "anchors": {}}
    p_anchors = producer.get("anchors")
    if not isinstance(p_anchors, dict):
        out["available"] = False
        return out
    out["available"] = True
    for name, c in checker_anchors.items():
        p = p_anchors.get(name)
        out["anchors"][name] = {
            "producer_available": isinstance(p, dict),
            "enclosure_equal": isinstance(p, dict)
            and p.get("enclosure") == c["enclosure"],
            "evaluation_count_equal": isinstance(p, dict)
            and p.get("evaluation_count") == c["evaluation_count"],
            "required_sign_equal": isinstance(p, dict)
            and p.get("required_sign") == c["required_sign"],
            "lambda_equal": isinstance(p, dict)
            and p.get("lambda") == c["lambda"],
        }
    return out


def check_receipt(
    *,
    expected_head: str,
    producer_receipt_path: Path,
) -> dict[str, Any]:
    independence = _assert_checker_independence()
    pre = _precheck(expected_head)
    producer, producer_receipt_sha256 = _load_producer_receipt(
        producer_receipt_path
    )

    config, _ = load_config()
    require_blocal_dependency(config)
    _need(config["dps"] > 0, "FAIL_PRODUCER_DPS")
    _need(
        config["checker_dps"] >= config["dps"],
        "FAIL_CHECKER_DPS_CONTRACT",
    )

    geometry = _reconstruct_tube_geometry(producer, config)
    lambda_geometry = _reconstruct_lambda_geometry(
        producer, config, geometry["nominal_width"]
    )

    raw_kernel, kernel_path = load_production_kernel()
    from flint import acb, arb, fmpq, ctx

    ctx.dps = config["checker_dps"]

    import blocal_arb_adapter as adapter
    import blocal_v22_model as model
    import blocal_v23_boundary as route

    bcfg = _load_v23_boundary_config()
    transport_gate = _verify_transport_gate(pre, route, model, bcfg)

    target_contracts = {
        "R_HI": _derive_anchor_contract("NEG", "NEG"),
        "R_LO": _derive_anchor_contract("POS", "NEG"),
    }
    _need(
        transport_gate["transport_gate_pass"] is True,
        "FAIL_TRANSPORT_GATE",
    )

    exact_f = ExactLambdaRoutedEvaluator(raw_kernel, arb, config)
    exact_f.set_phase(
        f"CHECKER:CANDIDATE:{producer['candidate_index']}:CELL:{producer['cell_index']}"
    )

    checker_anchors: dict[str, dict[str, Any]] = {}
    hi_contract = target_contracts["R_HI"]
    lo_contract = target_contracts["R_LO"]
    _need(
        hi_contract["anchor_side"] == "LEFT"
        and lo_contract["anchor_side"] == "RIGHT",
        "FAIL_ANCHOR_SIDE_DERIVATION",
    )

    checker_anchors["R_HI_LEFT_NEG"] = _anchor_check(
        evaluator=exact_f,
        endpoint=geometry["domain"].hi,
        lam=lambda_geometry["lambda_left"],
        required_sign=hi_contract["anchor_required_sign"],
        config=config,
    )
    checker_anchors["R_LO_RIGHT_POS"] = _anchor_check(
        evaluator=exact_f,
        endpoint=geometry["domain"].lo,
        lam=lambda_geometry["lambda_right"],
        required_sign=lo_contract["anchor_required_sign"],
        config=config,
    )

    proof_expectations = transport_gate["proof_expectations"]
    checker_flambda = {
        "R_HI": _flambda_check(
            route=route,
            model=model,
            adapter=adapter,
            raw_kernel=raw_kernel,
            acb_type=acb,
            arb_type=arb,
            fmpq_type=fmpq,
            bcfg=bcfg,
            endpoint=geometry["domain"].hi,
            tiles=lambda_geometry["tiles"],
            proof_expectations=proof_expectations,
            side="R_HI",
        ),
        "R_LO": _flambda_check(
            route=route,
            model=model,
            adapter=adapter,
            raw_kernel=raw_kernel,
            acb_type=acb,
            arb_type=arb,
            fmpq_type=fmpq,
            bcfg=bcfg,
            endpoint=geometry["domain"].lo,
            tiles=lambda_geometry["tiles"],
            proof_expectations=proof_expectations,
            side="R_LO",
        ),
    }

    total_anchor = sum(x["evaluation_count"] for x in checker_anchors.values())
    total_flambda = sum(
        x["evaluation_count"]
        for side in ("R_HI", "R_LO")
        for x in checker_flambda[side]
    )
    tile_count = len(lambda_geometry["tiles"])
    declared_parent_cap = (
        2 * CHECKER_ANCHOR_CALL_CAP
        + 2 * tile_count * CHECKER_FLAMBDA_CELL_CALL_CAP
    )
    _need(
        total_anchor + total_flambda <= declared_parent_cap,
        "FAIL_CHECKER_PARENT_TOTAL_BUDGET",
    )

    tile_match_report = _report_tile_matches(producer, checker_flambda)
    anchor_match_report = _report_anchor_matches(producer, checker_anchors)

    stage_results = {
        "stage_1": {
            "status": "PASS",
            "responsibility": "checker source/pin/runtime bundle and NC20 independence",
            "gating": True,
        },
        "stage_2": {
            "status": "PASS",
            "responsibility": "producer receipt schema/nonbinding state and native explicit-NEG contract",
            "gating": True,
        },
        "stage_3": {
            "status": "PASS",
            "responsibility": "independent exact q_hull/rho/physical-tube reconstruction",
            "gating": True,
        },
        "stage_4": {
            "status": "PASS",
            "responsibility": "independent lambda parent and residual-tiling reconstruction",
            "gating": True,
        },
        "stage_5": {
            "status": "PASS",
            "responsibility": "shared-kernel/formula/transport-receipt/external-signature gate",
            "gating": True,
        },
        "stage_6": {
            "status": "PASS",
            "responsibility": "strict-interior endpoint scope and native route-policy contract",
            "gating": True,
        },
        "stage_7": {
            "status": "PASS",
            "responsibility": "independent 8-tile F_lambda strict-NEG closed-cover reevaluation",
            "gating": True,
            "producer_identity_comparison": "REPORTED_NOT_GATING",
        },
        "stage_8": {
            "status": "PASS",
            "responsibility": "F_lambda proof-object formula/policy/normalization/cap contract",
            "gating": True,
        },
        "stage_9": {
            "status": "PASS",
            "responsibility": "independent two-anchor strict-sign reevaluation and checker budget",
            "gating": True,
            "producer_identity_comparison": "REPORTED_NOT_GATING",
        },
        "stage_10": {
            "status": "PASS",
            "responsibility": "independent target-sign to anchor-side derivation with transport lemma gate",
            "gating": True,
        },
    }

    result = {
        "schema": CHECKER_SCHEMA,
        "status": CHECKER_STATUS,
        "evidence_class": CHECKER_EVIDENCE_CLASS,
        "binding_use_authorized": False,
        "checker_role": "AI2_CHECKER",
        "human_promotion_required": True,
        "checker_verdict": "PASS_BINDING_CANDIDATE_CHECK",
        "execution_head": expected_head,
        "source_baseline_head": pre["source_baseline_head"],
        "checker_source_sha256": pre["actual"]["checker_source_sha256"],
        "negative_controls_source_sha256": pre["actual"][
            "negative_controls_source_sha256"
        ],
        "producer_receipt": {
            "path": str(producer_receipt_path),
            "sha256": producer_receipt_sha256,
            "producer_verdict_observed": producer.get("producer_verdict"),
            "producer_verdict_used_as_mathematical_evidence": False,
        },
        "independence": independence,
        "pins": pre["pins"],
        "legacy_snapshot_verified": pre["legacy_snapshot_verified"],
        "production_kernel": {
            "path": kernel_path.relative_to(REPO_ROOT).as_posix(),
            "sha256": hashlib.sha256(kernel_path.read_bytes()).hexdigest(),
        },
        "checker_dps": config["checker_dps"],
        "candidate_index": producer["candidate_index"],
        "cell_index": producer["cell_index"],
        "geometry_reconstruction": {
            "q_left": geometry["q_left"].to_json(),
            "q_right": geometry["q_right"].to_json(),
            "q_hull": geometry["q_hull"].to_json(),
            "adaptive_safety_factor": geometry["sigma"].to_json(),
            "radius_cap": geometry["radius_cap"].to_json(),
            "rho": geometry["rho"].to_json(),
            "left_margin": geometry["left_margin"].to_json(),
            "right_margin": geometry["right_margin"].to_json(),
            "physical_tube": geometry["domain"].to_json(),
            "producer_endpoint_fields_role": "REDUNDANCY_ONLY",
        },
        "lambda_reconstruction": {
            "lambda_start": _fraction_json(lambda_geometry["lambda_start"]),
            "lambda_end": _fraction_json(lambda_geometry["lambda_end"]),
            "lambda_left": _fraction_json(lambda_geometry["lambda_left"]),
            "lambda_right": _fraction_json(lambda_geometry["lambda_right"]),
            "nominal_width": _fraction_json(lambda_geometry["nominal_width"]),
            "base_tile": _fraction_json(FLAMBDA_BASE_TILE),
            "tiles": [
                _interval_fraction_json(a, b)
                for a, b in lambda_geometry["tiles"]
            ],
        },
        "transport_gate": transport_gate,
        "target_contracts": target_contracts,
        "checker_anchors": checker_anchors,
        "checker_flambda": {
            "route_id": FLAMBDA_ROUTE_ID,
            "required_sign": "NEG",
            "proof_expectations": proof_expectations,
            "R_HI": checker_flambda["R_HI"],
            "R_LO": checker_flambda["R_LO"],
        },
        "budgets": {
            "checker_anchor_call_cap": CHECKER_ANCHOR_CALL_CAP,
            "checker_anchor_evaluation_count": total_anchor,
            "checker_flambda_cell_call_cap": CHECKER_FLAMBDA_CELL_CALL_CAP,
            "checker_flambda_evaluation_count": total_flambda,
            "tile_count": tile_count,
            "declared_parent_total_cap": declared_parent_cap,
            "total_evaluation_count": total_anchor + total_flambda,
            "post_hoc_cap_increase": "FORBIDDEN",
        },
        "producer_comparison": {
            "gating": False,
            "classification": "REPORTED_NOT_GATING",
            "anchors": anchor_match_report,
            "flambda": tile_match_report,
        },
        "stage_results": stage_results,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--producer-receipt", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--expected-head",
        default=None,
        help="Exact 40-hex execution HEAD; defaults to EXPECTED_HEAD env.",
    )
    args = parser.parse_args()

    expected_head = args.expected_head
    if expected_head is None:
        import os

        expected_head = os.environ.get("EXPECTED_HEAD")
    if not isinstance(expected_head, str):
        print("FAIL_EXPECTED_HEAD_MISSING")
        return 2

    try:
        result = check_receipt(
            expected_head=expected_head,
            producer_receipt_path=Path(args.producer_receipt).expanduser().resolve(),
        )
    except CheckerFailure as exc:
        print(exc.code if exc.detail is None else f"{exc.code}:{exc.detail}")
        return 2
    except CalibrationError as exc:
        print(f"FAIL_CALIBRATION_API:{exc}")
        return 2

    output = Path(args.output).expanduser().resolve()
    output.write_bytes(canonical_json_bytes(result))
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
