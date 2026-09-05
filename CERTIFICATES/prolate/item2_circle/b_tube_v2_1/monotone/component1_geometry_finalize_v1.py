#!/usr/bin/env python3
"""Finalize a fail-closed Component1 geometry receipt from F_lambda evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
SCHEMA = "monotone-tube-v1.1-component1-geometry-receipt-v1"
CONTRACT = "MONOTONE_TUBE_V1_1"


def fail(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail("NONREGULAR_INPUT:" + str(path))
    try:
        obj = json.loads(path.read_text())
    except Exception as exc:
        fail("BAD_JSON:" + str(path) + ":" + str(exc))
    if not isinstance(obj, dict):
        fail("TOP_LEVEL_NOT_OBJECT:" + str(path))
    return obj


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def frac(value: dict) -> Fraction:
    if set(value) == {"p", "q"}:
        return Fraction(int(value["p"]), int(value["q"]))
    if set(value) == {"e", "m"}:
        return Fraction(int(value["m"]), 1 << int(value["e"]))
    fail("BAD_EXACT_NUMBER")


def fstr(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def require(condition: bool, msg: str) -> None:
    if not condition:
        fail(msg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--producer", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--previous-geometry", type=Path, required=True)
    ap.add_argument("--cell-index", type=int, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--expected-head", required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()
    mon = repo / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone"
    finalizer_path = mon / "component1_geometry_finalize_v1.py"
    verifier_path = mon / "component1_geometry_verify_v1.py"
    require(os.environ.get("PYTHONDONTWRITEBYTECODE") == "1", "BYTECODE_POLICY")
    require(not git(repo, "status", "--porcelain"), "SOURCE_TREE_PRE_DIRTY")
    head = git(repo, "rev-parse", "HEAD")
    require(head == ns.expected_head, "EXECUTION_HEAD")
    p, c, prev = load(ns.producer), load(ns.checker), load(ns.previous_geometry)
    psha, csha, prevsha = sha(ns.producer), sha(ns.checker), sha(ns.previous_geometry)

    require(p.get("schema") == "btube-flambda-transport-producer-v1", "PRODUCER_SCHEMA")
    require(p.get("producer_verdict") == "PASS_BINDING_CANDIDATE", "PRODUCER_VERDICT")
    require(p.get("binding_use_authorized") is False, "PRODUCER_SELF_AUTHORIZED")
    require(c.get("schema") == "btube-flambda-transport-checker-v1", "CHECKER_SCHEMA")
    require(c.get("checker_verdict") == "PASS_BINDING_CANDIDATE_CHECK", "CHECKER_VERDICT")
    require(c.get("status") == "INDEPENDENT_CHECK_PASS_NOT_PROMOTED", "CHECKER_STATUS")
    require(c.get("binding_use_authorized") is False, "CHECKER_SELF_AUTHORIZED")
    require(c.get("producer_receipt", {}).get("sha256") == psha, "PRODUCER_SHA_LINK")
    require(c.get("independence", {}).get("runtime_module_free") is True, "CHECKER_RUNTIME_INDEPENDENCE")
    require(c.get("independence", {}).get("source_import_free") is True, "CHECKER_SOURCE_INDEPENDENCE")
    stages = c.get("stage_results", {})
    require(stages and all(x.get("status") == "PASS" for x in stages.values()), "CHECKER_STAGES")
    i = ns.cell_index
    require(i > 0 and p.get("cell_index") == i and c.get("cell_index") == i, "CELL_INDEX")
    require(p.get("candidate_index") == c.get("candidate_index"), "CANDIDATE_INDEX")
    prev_id, cell_id = f"CELL{i - 1}", f"CELL{i}"
    require(prev.get("cell_id") == prev_id, "PREVIOUS_CELL_ID")
    require(prev.get("candidate_inputs", {}).get("cell_index") == i - 1, "PREVIOUS_CELL_INDEX")
    require(prev.get("rectangle_identity_role") == "LOAD_BEARING_SINGLE_SOURCE", "PREVIOUS_ROLE")

    lr = c["lambda_reconstruction"]
    gr = c["geometry_reconstruction"]
    lam_lo, lam_hi = frac(lr["lambda_left"]), frac(lr["lambda_right"])
    lam_start, lam_end = frac(lr["lambda_start"]), frac(lr["lambda_end"])
    width = frac(lr["nominal_width"])
    ql, qr = frac(gr["q_left"]), frac(gr["q_right"])
    qlo, qhi = frac(gr["q_hull"]["lo"]), frac(gr["q_hull"]["hi"])
    rho, cap, sigma = frac(gr["rho"]), frac(gr["radius_cap"]), frac(gr["adaptive_safety_factor"])
    rlo, rhi = frac(gr["physical_tube"]["lo"]), frac(gr["physical_tube"]["hi"])
    require(frac(p["candidate_parent"]["lo"]) == lam_lo, "PRODUCER_LAMBDA_LO")
    require(frac(p["candidate_parent"]["hi"]) == lam_hi, "PRODUCER_LAMBDA_HI")
    require(frac(p["predictor"]["q_left"]) == ql, "PRODUCER_Q_LEFT")
    require(frac(p["predictor"]["q_right"]) == qr, "PRODUCER_Q_RIGHT")
    require(frac(p["adaptive_radius"]) == rho, "PRODUCER_RHO")
    require(frac(p["r_lo"]) == rlo and frac(p["r_hi"]) == rhi, "PRODUCER_TUBE")
    require(qlo == min(ql, qr) and qhi == max(ql, qr), "Q_HULL")
    require(rlo == qlo - rho and rhi == qhi + rho, "PHYSICAL_TUBE")
    require(Fraction(prev["derived_geometry"]["lambda_hi"]) == lam_lo, "ADJACENT_LAMBDA")
    require(Fraction(prev["candidate_inputs"]["q_right"]) == ql, "ADJACENT_Q")
    require(0 < rho <= cap, "RADIUS")

    pins = {
        "calibration_config_sha256": p["pins"]["calibration_config_sha256"],
        "flambda_checker_execution_head": c["execution_head"],
        "flambda_checker_receipt_sha256": csha,
        "flambda_checker_source_sha256": c["checker_source_sha256"],
        "flambda_producer_execution_head": p["execution_head"],
        "flambda_producer_receipt_sha256": psha,
        "flambda_producer_verdict": p["producer_verdict"],
        "geometry_finalizer_source_sha256": sha(finalizer_path),
        "geometry_verifier_source_sha256": sha(verifier_path),
        "previous_geometry_receipt_sha256": prevsha,
        "production_kernel_sha256": p["production_kernel"]["sha256"],
        "route_fragment_sha256": p["pins"]["route_fragment_sha256"],
        "shared_kernel_sha256": p["pins"]["shared_kernel_sha256"],
    }
    receipt = {
        "binding_use_authorized": False,
        "candidate_inputs": {
            "W_nom": fstr(width), "cell_index": i, "lambda_end": fstr(lam_end),
            "lambda_start": fstr(lam_start), "q_left": fstr(ql), "q_right": fstr(qr),
            "rho_cap": fstr(cap), "sigma": fstr(sigma),
        },
        "cell_id": cell_id,
        "component": "TUBE_GEOMETRY",
        "contract": CONTRACT,
        "cross_component_rectangle_identity": {
            "required_consumers": ["H_U_PRODUCTION_RECEIPT", "F_LAMBDA_RECEIPT", "JOIN_RECEIPT", "MONOTONE_ASSEMBLY"],
            "requirement": "all consumers must pin the exact same component1_geometry_receipt_sha256",
            "role": "LOAD_BEARING", "single_source": "THIS_RECEIPT_SHA256",
        },
        "derived_geometry": {
            "lambda_hi": fstr(lam_hi), "lambda_lo": fstr(lam_lo),
            "q_hull_hi": fstr(qhi), "q_hull_lo": fstr(qlo),
            "r_hi": fstr(rhi), "r_lo": fstr(rlo), "rho": fstr(rho),
        },
        "evidence_class": "PRODUCTION_CANDIDATE",
        "nonclaims": [
            "predictor provenance is reproducibility-only and is not a mathematical proof obligation of MONOTONE_TUBE_V1.1",
            "this receipt does not authorize binding use by itself",
        ],
        "provenance_role": "REPRODUCIBILITY_ONLY_NOT_LOAD_BEARING",
        "rectangle_identity_role": "LOAD_BEARING_SINGLE_SOURCE",
        "schema": SCHEMA,
        "source_provenance": {
            "candidate_index": p["candidate_index"],
            "execution_pins": pins,
            "q_left_origin": f"exact previous-cell endpoint: {prev_id} q_right = {fstr(ql)}",
            "q_right_origin": f"production predictor: cell {i} right-end Newton predictor at lambda={fstr(lam_hi)}, 4 iterations from q_left",
            "rho_cap_origin": f"binding candidate tube radius cap = {fstr(cap)}",
            "sigma_origin": f"binding calibration adaptive_safety_factor = {fstr(sigma)}",
            "source_head": p["source_baseline_head"],
            "source_sha256": p["producer_source_sha256"],
        },
    }
    require(git(repo, "rev-parse", "HEAD") == head, "HEAD_CHANGED_DURING_RUN")
    require(not git(repo, "status", "--porcelain"), "SOURCE_TREE_POST_DIRTY")
    ns.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("CELL=" + cell_id)
    print("ADJACENT_Q_IDENTITY=TRUE")
    print("ADJACENT_LAMBDA_IDENTITY=TRUE")
    print("PRODUCER_SHA256=" + psha)
    print("CHECKER_SHA256=" + csha)
    print("VERDICT=COMPONENT1_GEOMETRY_PASS_NOT_PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
