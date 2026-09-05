#!/usr/bin/env python3
"""Independent verifier for a Component1 geometry receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
SCHEMA = "monotone-tube-v1.1-component1-geometry-receipt-v1"


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
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--producer", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--previous-geometry", type=Path, required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()
    require(not subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True).strip(), "SOURCE_TREE_DIRTY")
    mon = repo / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone"
    finalizer = mon / "component1_geometry_finalize_v1.py"
    verifier = mon / "component1_geometry_verify_v1.py"
    r, p, c, prev = map(load, (ns.receipt, ns.producer, ns.checker, ns.previous_geometry))
    require(r.get("schema") == SCHEMA, "RECEIPT_SCHEMA")
    require(r.get("contract") == "MONOTONE_TUBE_V1_1", "CONTRACT")
    require(r.get("component") == "TUBE_GEOMETRY", "COMPONENT")
    require(r.get("binding_use_authorized") is False, "SOURCE_RECEIPT_SELF_AUTHORIZED")
    i = r.get("candidate_inputs", {}).get("cell_index")
    require(isinstance(i, int) and i > 0 and r.get("cell_id") == f"CELL{i}", "CELL_ID")
    require(p.get("cell_index") == i and c.get("cell_index") == i, "EVIDENCE_CELL_INDEX")
    require(p.get("producer_verdict") == "PASS_BINDING_CANDIDATE", "PRODUCER_VERDICT")
    require(c.get("checker_verdict") == "PASS_BINDING_CANDIDATE_CHECK", "CHECKER_VERDICT")
    require(c.get("producer_receipt", {}).get("sha256") == sha(ns.producer), "PRODUCER_LINK")
    require(prev.get("cell_id") == f"CELL{i - 1}", "PREVIOUS_CELL")
    require(prev.get("candidate_inputs", {}).get("cell_index") == i - 1, "PREVIOUS_INDEX")

    lr, gr = c["lambda_reconstruction"], c["geometry_reconstruction"]
    lam_lo, lam_hi = frac(lr["lambda_left"]), frac(lr["lambda_right"])
    ql, qr = frac(gr["q_left"]), frac(gr["q_right"])
    qlo, qhi = min(ql, qr), max(ql, qr)
    rho = frac(gr["rho"])
    rlo, rhi = qlo - rho, qhi + rho
    require(Fraction(prev["derived_geometry"]["lambda_hi"]) == lam_lo, "ADJACENT_LAMBDA")
    require(Fraction(prev["candidate_inputs"]["q_right"]) == ql, "ADJACENT_Q")
    require(frac(p["predictor"]["q_left"]) == ql and frac(p["predictor"]["q_right"]) == qr, "PREDICTOR")
    require(frac(p["r_lo"]) == rlo and frac(p["r_hi"]) == rhi, "PHYSICAL_TUBE")
    expected_inputs = {
        "W_nom": fstr(frac(lr["nominal_width"])),
        "cell_index": i,
        "lambda_end": fstr(frac(lr["lambda_end"])),
        "lambda_start": fstr(frac(lr["lambda_start"])),
        "q_left": fstr(ql),
        "q_right": fstr(qr),
        "rho_cap": fstr(frac(gr["radius_cap"])),
        "sigma": fstr(frac(gr["adaptive_safety_factor"])),
    }
    expected_geometry = {
        "lambda_hi": fstr(lam_hi),
        "lambda_lo": fstr(lam_lo),
        "q_hull_hi": fstr(qhi),
        "q_hull_lo": fstr(qlo),
        "r_hi": fstr(rhi),
        "r_lo": fstr(rlo),
        "rho": fstr(rho),
    }
    require(r.get("candidate_inputs") == expected_inputs, "CANDIDATE_RECONSTRUCTION")
    require(r.get("derived_geometry") == expected_geometry, "GEOMETRY_RECONSTRUCTION")
    require(r.get("rectangle_identity_role") == "LOAD_BEARING_SINGLE_SOURCE", "RECTANGLE_ROLE")
    cross = r.get("cross_component_rectangle_identity", {})
    require(cross.get("single_source") == "THIS_RECEIPT_SHA256", "SINGLE_SOURCE")
    require(cross.get("role") == "LOAD_BEARING", "LOAD_BEARING_ROLE")
    required = {"H_U_PRODUCTION_RECEIPT", "F_LAMBDA_RECEIPT", "JOIN_RECEIPT", "MONOTONE_ASSEMBLY"}
    require(set(cross.get("required_consumers", [])) == required, "REQUIRED_CONSUMERS")
    pins = r.get("source_provenance", {}).get("execution_pins", {})
    expected_pins = {
        "calibration_config_sha256": p["pins"]["calibration_config_sha256"],
        "flambda_checker_execution_head": c["execution_head"],
        "flambda_checker_receipt_sha256": sha(ns.checker),
        "flambda_checker_source_sha256": c["checker_source_sha256"],
        "flambda_producer_execution_head": p["execution_head"],
        "flambda_producer_receipt_sha256": sha(ns.producer),
        "flambda_producer_verdict": p["producer_verdict"],
        "geometry_finalizer_source_sha256": sha(finalizer),
        "geometry_verifier_source_sha256": sha(verifier),
        "previous_geometry_receipt_sha256": sha(ns.previous_geometry),
        "production_kernel_sha256": p["production_kernel"]["sha256"],
        "route_fragment_sha256": p["pins"]["route_fragment_sha256"],
        "shared_kernel_sha256": p["pins"]["shared_kernel_sha256"],
    }
    require(pins == expected_pins, "EXECUTION_PINS")
    require(r.get("source_provenance", {}).get("source_head") == p["source_baseline_head"], "SOURCE_HEAD")
    require(r.get("source_provenance", {}).get("source_sha256") == p["producer_source_sha256"], "SOURCE_SHA")
    print("CHECKER_VERDICT=PASS")
    print("CELL=" + r["cell_id"])
    print("ADJACENT_Q_IDENTITY=TRUE")
    print("ADJACENT_LAMBDA_IDENTITY=TRUE")
    print("SOURCE_RECEIPT_SHA256=" + sha(ns.receipt))
    print("VERIFIER_SHA256=" + sha(verifier))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
