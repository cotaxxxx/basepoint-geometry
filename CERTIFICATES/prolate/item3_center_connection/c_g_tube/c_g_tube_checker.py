#!/usr/bin/env python3
"""Independent fail-closed checker and finalizer for C-G-TUBE pilot v5.

The checker trusts no self-reported sign or coverage verdict. It reconstructs
endpoint signs, cell leaf negativity and tilings, adaptive spot Taylor leaf
negativity and tiling, spot intersections, dependency pins, calibration, and
negative-control outcomes from the stored raw records.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path

from flint import arb

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_bytes())
CONFIG_SHA = hashlib.sha256((HERE / "config.json").read_bytes()).hexdigest()
REQUIRED_FIELDS = (
    "writer_id", "run_uuid", "process_id", "hostname", "phase",
    "recorded_at", "started_at", "finished_at", "config_sha256",
    "dependency_sha256", "input_state_sha256", "previous_record_sha256",
)
CONTROL_EXPECT = {
    "positive": 0,
    "neg_sign_flip": 1,
    "neg_missing_cell": 1,
    "neg_sha_tamper": 2,
    "neg_limit_short": 1,
    "neg_spot_leaf_missing": 1,
    "neg_spot_sign_flip": 1,
}


def die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def qa(value: Fr) -> arb:
    return arb(str(value.numerator)) / arb(str(value.denominator))


def endpoint_lo(text: str) -> arb:
    return arb(arb(text).lower())


def endpoint_hi(text: str) -> arb:
    return arb(arb(text).upper())


def reject_legacy_upper(obj) -> None:
    if isinstance(obj, dict):
        if "upper" in obj:
            die("LEGACY upper FIELD PRESENT", 1)
        for value in obj.values():
            reject_legacy_upper(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_legacy_upper(value)


def load_chain(name: str, phase: str) -> list[dict]:
    path = HERE / name
    if not path.exists():
        die(f"MISSING CHAIN: {name}", 1)
    previous = "GENESIS"
    out = []
    for line in path.read_bytes().splitlines():
        rec = json.loads(line)
        reject_legacy_upper(rec)
        if rec.get("previous_record_sha256") != previous:
            die(f"CHAIN BROKEN: {name}")
        if rec.get("input_state_sha256") != previous:
            die(f"INPUT STATE SHA MISMATCH IN {name}")
        if rec.get("config_sha256") != CONFIG_SHA:
            die(f"CONFIG SHA MISMATCH IN {name}")
        if rec.get("record_schema") != CONFIG["record_schema"]:
            die(f"RECORD SCHEMA MISMATCH IN {name}")
        if rec.get("phase") != phase:
            die(f"PHASE MISMATCH IN {name}")
        for field in REQUIRED_FIELDS:
            if field not in rec or rec[field] in ("", None):
                die(f"MISSING PROVENANCE FIELD {field} IN {name}")
        previous = hashlib.sha256(line).hexdigest()
        out.append(rec)
    return out


def taylor_bounds(rec: dict) -> tuple[arb, arb]:
    try:
        a, b = Fr(rec["a"]), Fr(rec["b"])
        gpm = rec["G_prime_m"]
        C = arb(rec["C_bound"])
    except (KeyError, TypeError, ValueError) as exc:
        die(f"MALFORMED TAYLOR RECORD: {exc}", 1)
    if b <= a:
        die(f"NONPOSITIVE TAYLOR INTERVAL {a}..{b}", 1)
    if not isinstance(gpm, list) or len(gpm) != 2:
        die("TAYLOR G_prime_m BALL MISSING", 1)
    if not bool(arb(C.lower()) >= 0):
        die(f"NONNEGATIVITY OF C_bound NOT CERTIFIED at {a}..{b}", 1)
    radius = (b - a) / 2
    lower = arb((endpoint_lo(gpm[0]) - C * qa(radius)).lower())
    upper = arb((endpoint_hi(gpm[1]) + C * qa(radius)).upper())
    return lower, upper


def taylor_record_negative(rec: dict) -> bool:
    lower, upper = taylor_bounds(rec)
    negative = bool(upper < 0)
    if negative != bool(rec.get("negative")):
        die(f"TAYLOR NEGATIVITY MISMATCH at {rec.get('a')}..{rec.get('b')}", 1)
    stored = rec.get("reconstructed_ball")
    if stored is not None:
        if not isinstance(stored, list) or len(stored) != 2:
            die("MALFORMED reconstructed_ball", 1)
        slo, shi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
        if bool(slo > lower) or bool(shi < upper):
            die("STORED TAYLOR BALL DOES NOT CONTAIN RECONSTRUCTION", 1)
    return negative


def weighted_product_bounds(ta: Fr, tb: Fr, flo: arb, fhi: arb):
    a, b = qa(ta), qa(tb)
    if bool(flo >= 0):
        return arb((a * flo).lower()), arb((b * fhi).upper())
    if bool(fhi <= 0):
        return arb((b * flo).lower()), arb((a * fhi).upper())
    return arb((b * flo).lower()), arb((b * fhi).upper())


def identity_record_negative(rec: dict) -> bool:
    n = rec.get("partition_count")
    if not isinstance(n, int) or n != CONFIG["center_t_partition_count"]:
        die(f"CENTER IDENTITY PARTITION MISMATCH at {rec.get('a')}..{rec.get('b')}", 1)
    pieces = rec.get("identity_pieces")
    if not isinstance(pieces, list) or len(pieces) != n:
        die("CENTER IDENTITY PIECE COUNT MISMATCH", 1)
    dt = qa(Fr(1, n))
    total_lo, total_hi = arb(0), arb(0)
    for i, piece in enumerate(pieces):
        ta, tb = Fr(piece["t_a"]), Fr(piece["t_b"])
        if ta != Fr(i, n) or tb != Fr(i + 1, n):
            die("CENTER IDENTITY t-PARTITION MISMATCH", 1)
        fball = piece.get("Frr_ball")
        if not isinstance(fball, list) or len(fball) != 2:
            die("CENTER IDENTITY Frr BALL MISSING", 1)
        flo, fhi = endpoint_lo(fball[0]), endpoint_hi(fball[1])
        if bool(flo > fhi):
            die("CENTER IDENTITY Frr BALL REVERSED", 1)
        plo, phi = weighted_product_bounds(ta, tb, flo, fhi)
        total_lo = arb((total_lo + plo * dt).lower())
        total_hi = arb((total_hi + phi * dt).upper())
    stored = rec.get("G_prime_ball")
    if not isinstance(stored, list) or len(stored) != 2:
        die("CENTER IDENTITY SUMMARY BALL MISSING", 1)
    stored_lo, stored_hi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
    if bool(stored_hi < total_lo) or bool(total_hi < stored_lo):
        die("CENTER IDENTITY SUMMARY DISJOINT FROM RECONSTRUCTION", 1)
    negative = bool(total_hi < 0)
    if negative != bool(rec.get("negative")):
        die("CENTER IDENTITY NEGATIVITY MISMATCH", 1)
    return negative


def cell_record_negative(rec: dict, cell_index: int) -> bool:
    method = rec.get("method", "taylor")
    center = cell_index < CONFIG["center_identity_cell_count"]
    if method == "center_identity":
        if not center:
            die(f"CENTER IDENTITY METHOD OUTSIDE CENTER REGION: cell {cell_index}", 1)
        return identity_record_negative(rec)
    if method == "taylor":
        if center:
            die(f"TAYLOR METHOD IN CENTER REGION: cell {cell_index}", 1)
        return taylor_record_negative(rec)
    die(f"UNKNOWN CELL METHOD {method!r}", 1)
    return False


def exact_tile(intervals: list[tuple[Fr, Fr]], a: Fr, b: Fr) -> bool:
    current = a
    for left, right in sorted(intervals):
        if left != current or right <= left:
            return False
        current = right
    return current == b


def taylor_tile_and_hull(records: list[dict], a: Fr, b: Fr,
                          max_depth: int) -> tuple[bool, arb, arb]:
    if not isinstance(records, list) or not records:
        return False, arb(0), arb(0)
    intervals = []
    lower = None
    upper = None
    for rec in records:
        if rec.get("method", "taylor") != "taylor":
            die("NON-TAYLOR RECORD IN ADAPTIVE TAYLOR LEAVES", 1)
        depth = rec.get("depth")
        if not isinstance(depth, int) or depth < 0 or depth > max_depth:
            die("ADAPTIVE TAYLOR DEPTH OUT OF RANGE", 1)
        ra, rb = Fr(rec["a"]), Fr(rec["b"])
        if ra < a or rb > b:
            die("ADAPTIVE TAYLOR LEAF OUTSIDE SPOT CELL", 1)
        if not taylor_record_negative(rec):
            return False, arb(0), arb(0)
        lo, hi = taylor_bounds(rec)
        intervals.append((ra, rb))
        if lower is None or bool(lo < lower):
            lower = lo
        if upper is None or bool(hi > upper):
            upper = hi
    tiled = exact_tile(intervals, a, b)
    return tiled, arb(lower.lower()), arb(upper.upper())


def write_json(path: Path, obj) -> None:
    path.write_bytes(json.dumps(obj, separators=(",", ":")).encode())


def main() -> int:
    endpoints = load_chain("endpoints_chain.jsonl", "endpoints")
    cells = load_chain("cells_chain.jsonl", "cells")
    spots = load_chain("spots_chain.jsonl", "spots")
    if len(endpoints) != 2 or any(r.get("record_type") != "endpoint" for r in endpoints):
        die("ENDPOINTS CHAIN MUST CONTAIN EXACTLY 2 ENDPOINT RECORDS", 1)
    if len(cells) != CONFIG["n_cells"] or any(r.get("record_type") != "cell" for r in cells):
        die("CELLS CHAIN MUST CONTAIN EXACTLY n_cells CELL RECORDS", 1)
    if len(spots) != len(CONFIG["spot_cell_indices"]) or any(r.get("record_type") != "spot" for r in spots):
        die("SPOTS CHAIN MUST CONTAIN EXACTLY THE CONFIGURED SPOT RECORDS", 1)

    dependency_shas = {r["dependency_sha256"] for r in endpoints + cells + spots}
    if len(dependency_shas) != 1:
        die("DEPENDENCY SHA VARIES ACROSS CHAINS")
    dependency_sha = next(iter(dependency_shas))

    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    n_cells = CONFIG["n_cells"]
    width = (r_hi - r_lo) / n_cells

    expected_sign = {"lo": 1, "hi": -1}
    if [r["endpoint"] for r in endpoints].count("lo") != 1 or \
       [r["endpoint"] for r in endpoints].count("hi") != 1:
        die("ENDPOINT RECORD MULTIPLICITY", 1)
    endpoint_out = {}
    for rec in endpoints:
        key = rec["endpoint"]
        wanted_r = r_lo if key == "lo" else r_hi
        if Fr(rec["r"]) != wanted_r or rec.get("want") != expected_sign[key]:
            die("ENDPOINT METADATA TAMPERED", 1)
        sign = 1 if bool(endpoint_lo(rec["G"][0]) > 0) else \
            (-1 if bool(endpoint_hi(rec["G"][1]) < 0) else 0)
        endpoint_out[key] = {
            "r": rec["r"], "G": rec["G"], "sign": sign,
            "want": expected_sign[key], "ok": sign == expected_sign[key],
        }
    endpoints_ok = endpoint_out["lo"]["ok"] and endpoint_out["hi"]["ok"]
    write_json(HERE / "C_G_ENDPOINT_SIGNS.json", {
        "label": "item3_C-G-TUBE_pilot_endpoint_signs",
        "role": "existence",
        "lambda": CONFIG["lambda"],
        "config_sha256": CONFIG_SHA,
        "endpoints": endpoint_out,
        "verdict": "PASS" if endpoints_ok else "FAIL",
    })

    indices = [r["cell_index"] for r in cells]
    if len(indices) != len(set(indices)):
        die("DUPLICATE CELL INDEX", 1)
    grid_ok = sorted(indices) == list(range(n_cells))
    by_index = {r["cell_index"]: r for r in cells}
    cells_ok = True
    unresolved_count = 0
    for i in range(n_cells):
        rec = by_index.get(i)
        a_exp, b_exp = r_lo + i * width, r_lo + (i + 1) * width
        if rec is None or Fr(rec["a"]) != a_exp or Fr(rec["b"]) != b_exp:
            grid_ok = False
            cells_ok = False
            unresolved_count += 1
            continue
        leaves = []
        for sub in rec.get("sub", []):
            if cell_record_negative(sub, i):
                leaves.append((Fr(sub["a"]), Fr(sub["b"])))
        tiled = exact_tile(leaves, a_exp, b_exp)
        if not tiled:
            cells_ok = False
            unresolved_count += 1
        if bool(rec.get("certified")) != tiled:
            die(f"CELL CERTIFIED FIELD MISMATCH: cell {i}", 1)

    spot_indices = [r["cell_index"] for r in spots]
    if len(spot_indices) != len(set(spot_indices)):
        die("DUPLICATE SPOT INDEX", 1)
    spots_ok = sorted(spot_indices) == sorted(CONFIG["spot_cell_indices"])
    adaptive_indices = set(CONFIG["spot_adaptive_taylor_indices"])
    spot_out = []
    for rec in spots:
        i = rec["cell_index"]
        a_exp, b_exp = r_lo + i * width, r_lo + (i + 1) * width
        meta_ok = (
            Fr(rec["cell_interval"][0]) == a_exp and
            Fr(rec["cell_interval"][1]) == b_exp and
            rec["t_partition_count"] == CONFIG["t_partition_count"] and
            rec["depth_limit"] == CONFIG["int_depth"] and
            rec["evaluation_limit"] == CONFIG["int_limit"]
        )
        id_lo = endpoint_lo(rec["Gprime_identity_ball"][0])
        id_hi = endpoint_hi(rec["Gprime_identity_ball"][1])
        identity_negative = bool(id_hi < 0)
        method = rec.get("crosscheck_method")

        if i < CONFIG["center_identity_cell_count"]:
            meta_ok = meta_ok and method == "identity_refined"
            meta_ok = meta_ok and (
                rec.get("cross_partition_count") == CONFIG["center_refined_t_partition_count"] and
                rec.get("cross_depth_limit") == CONFIG["center_int_depth"] and
                rec.get("cross_evaluation_limit") == CONFIG["center_int_limit"]
            )
            cross_ball = rec.get("Gprime_cross_ball")
            if not isinstance(cross_ball, list) or len(cross_ball) != 2:
                die("REFINED IDENTITY SPOT BALL MISSING", 1)
            cross_lo, cross_hi = endpoint_lo(cross_ball[0]), endpoint_hi(cross_ball[1])
            tiling_complete = None
            terminal_unresolved = None
        elif i in adaptive_indices:
            meta_ok = meta_ok and method == "taylor_adaptive"
            max_depth = CONFIG["spot_taylor_max_extra_depth"]
            meta_ok = meta_ok and rec.get("cross_max_depth") == max_depth
            terminal = rec.get("cross_terminal_unresolved")
            if not isinstance(terminal, list):
                die("ADAPTIVE SPOT TERMINAL LIST MISSING", 1)
            tiling_complete, cross_lo, cross_hi = taylor_tile_and_hull(
                rec.get("cross_leaves"), a_exp, b_exp, max_depth)
            terminal_unresolved = len(terminal)
            if terminal_unresolved != 0:
                tiling_complete = False
            stored = rec.get("Gprime_cross_ball")
            if not isinstance(stored, list) or len(stored) != 2:
                die("ADAPTIVE SPOT SUMMARY BALL MISSING", 1)
            stored_lo, stored_hi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
            if bool(stored_lo > cross_lo) or bool(stored_hi < cross_hi):
                die("ADAPTIVE SPOT SUMMARY DOES NOT CONTAIN RECONSTRUCTION", 1)
        else:
            meta_ok = meta_ok and method == "taylor"
            leaf = rec.get("cross_leaf")
            if not isinstance(leaf, dict):
                die("SINGLE TAYLOR SPOT LEAF MISSING", 1)
            if Fr(leaf["a"]) != a_exp or Fr(leaf["b"]) != b_exp or leaf.get("depth") != 0:
                die("SINGLE TAYLOR SPOT LEAF METADATA MISMATCH", 1)
            taylor_record_negative(leaf)
            cross_lo, cross_hi = taylor_bounds(leaf)
            stored = rec.get("Gprime_cross_ball")
            if not isinstance(stored, list) or len(stored) != 2:
                die("SINGLE TAYLOR SPOT SUMMARY BALL MISSING", 1)
            stored_lo, stored_hi = endpoint_lo(stored[0]), endpoint_hi(stored[1])
            if bool(stored_lo > cross_lo) or bool(stored_hi < cross_hi):
                die("SINGLE TAYLOR SUMMARY DOES NOT CONTAIN RECONSTRUCTION", 1)
            tiling_complete = True
            terminal_unresolved = 0

        cross_negative = bool(cross_hi < 0)
        intersection = not (bool(id_hi < cross_lo) or bool(cross_hi < id_lo))
        reported_ok = (
            bool(rec.get("identity_negative")) == identity_negative and
            bool(rec.get("cross_negative")) == cross_negative and
            bool(rec.get("intersection_nonempty")) == intersection
        )
        if method == "taylor_adaptive":
            reported_ok = reported_ok and \
                bool(rec.get("cross_tiling_complete")) == bool(tiling_complete)
        spot_ok = meta_ok and identity_negative and cross_negative and \
            intersection and reported_ok and tiling_complete is not False
        spots_ok = spots_ok and spot_ok
        spot_out.append({
            "cell_index": i,
            "metadata_ok": meta_ok,
            "crosscheck_method": method,
            "identity_negative": identity_negative,
            "cross_negative": cross_negative,
            "intersection_nonempty": intersection,
            "tiling_complete": tiling_complete,
            "terminal_unresolved": terminal_unresolved,
            "Gprime_identity_ball": rec["Gprime_identity_ball"],
            "Gprime_cross_ball_reconstructed": [str(cross_lo), str(cross_hi)],
            "verdict": "PASS" if spot_ok else "FAIL",
        })
    write_json(HERE / "C_G_IDENTITY_CROSSCHECK.json", {
        "label": "item3_C-G-TUBE_pilot_identity_crosscheck",
        "role": "independent evaluator audit; failure fails the pilot",
        "config_sha256": CONFIG_SHA,
        "spots": spot_out,
        "verdict": "PASS" if spots_ok else "FAIL",
    })

    repo_root = Path(os.environ.get(
        "CG_TUBE_REPO_ROOT", HERE / "../../../..")).resolve()
    vendor_ok = True
    vendor_actual = {}
    dependency_hash = hashlib.sha256()
    for name, spec in sorted(CONFIG["vendor"].items()):
        path = repo_root / spec["path"]
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        vendor_actual[name] = actual
        vendor_ok = vendor_ok and actual == spec["sha256"]
        dependency_hash.update(spec["sha256"].encode())
    vendor_ok = vendor_ok and dependency_hash.hexdigest() == dependency_sha

    calibration = CONFIG["calibration"]
    calibration_path = repo_root / calibration["path"]
    calibration_actual = hashlib.sha256(calibration_path.read_bytes()).hexdigest() \
        if calibration_path.exists() else None
    calibration_ok = calibration_actual == calibration["sha256"]

    controls_ok = False
    controls = {}
    controls_path = HERE / "CONTROLS.json"
    if controls_path.exists():
        controls = json.loads(controls_path.read_bytes())
        control_results = controls.get("controls", {})
        controls_ok = (
            set(control_results) == set(CONTROL_EXPECT) and
            all(control_results[name]["expected_exit"] == expected and
                control_results[name]["observed_exit"] == expected and
                control_results[name]["ok"] is True
                for name, expected in CONTROL_EXPECT.items()) and
            controls.get("checker_sha256") == hashlib.sha256(
                (HERE / "c_g_tube_checker.py").read_bytes()).hexdigest() and
            controls.get("config_sha256") == CONFIG_SHA and
            controls.get("verdict") == "PASS"
        )

    write_json(HERE / "DEPENDENCIES.json", {
        "label": "item3_C-G-TUBE_pilot_dependencies",
        "config_sha256": CONFIG_SHA,
        "dependency_sha256_pinned": dependency_hash.hexdigest(),
        "dependency_sha256_in_chains": dependency_sha,
        "vendor_pinned": CONFIG["vendor"],
        "vendor_actual_at_finalize": vendor_actual,
        "calibration_pinned": calibration,
        "calibration_actual_sha256": calibration_actual,
        "source_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(HERE.iterdir())
            if path.is_file() and path.suffix in (".py", ".json", ".yml", ".md")
            and not path.name.startswith(("C_G_", "DEPENDENCIES", "CONTROLS"))
        },
    })

    conditions = {
        "endpoint_lo_positive": endpoint_out["lo"]["ok"],
        "endpoint_hi_negative": endpoint_out["hi"]["ok"],
        "coverage_complete_no_gap_no_overlap": grid_ok,
        "all_cells_negative_reconstructed": cells_ok,
        "spot_crosscheck_pass": spots_ok,
        "vendor_and_calibration_reverified": vendor_ok and calibration_ok,
        "negative_controls_deep_pass": controls_ok,
        "terminal_unresolved_zero": unresolved_count == 0,
    }
    verdict = "PASS" if all(conditions.values()) else "FAIL"
    write_json(HERE / "C_G_TUBE_PILOT.json", {
        "label": "item3_C-G-TUBE_pilot",
        "scope": CONFIG["scope"],
        "lambda": CONFIG["lambda"],
        "interval": [CONFIG["r_lo"], CONFIG["r_hi"]],
        "conclusion": (
            "exists unique r_c in (1/64, 11/256) with G(r_c, 118/25) = 0"
            if verdict == "PASS" else None
        ),
        "config_sha256": CONFIG_SHA,
        "dependency_sha256": dependency_sha,
        "conditions": conditions,
        "cells": cells,
        "verdict": verdict,
    })
    print(f"checker/finalize v5: {verdict} {conditions}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
