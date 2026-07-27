#!/usr/bin/env python3
"""Independent checker + finalize for the C-G-TUBE pilot (Actions), v3.

v3: record_schema cgtube-rec-v3 only; legacy 'upper' rejected RECURSIVELY at
every record level; endpoint records are an explicit record_type; endpoint
expected signs fixed in this checker; C_bound requires lower >= 0.

Trusts NOTHING self-reported. From raw chain records it re-derives:
  - hash-chain integrity; config_sha256 equality; single dependency_sha256
  - mandatory provenance fields present and non-empty on every record
  - endpoints: exactly one 'lo' and one 'hi'; exact rational r equality
    with config; strict signs recomputed from stored G balls
  - cells: index 0..55 exactly once (duplicates -> FAIL, never overwritten);
    exact expected grid a_i = r_lo + i*w, b_i = a_i + w; leaf tiling of each
    cell by negative leaves where negativity is RECONSTRUCTED as
        upper(G'(m)) + C_J * rho < 0
    from stored G_prime_m upper, stored C_bound, and rho recomputed from the
    leaf's exact endpoints (Arb + exact rationals only; legacy 'upper' is
    rejected recursively, while stored 'negative' is cross-checked for
    consistency and is not trusted)
  - spots: exactly the configured indices; cell_interval matches the
    expected grid; t_partition_count / depth_limit / evaluation_limit match
    config; identity and Taylor negativity and intersection recomputed from
    stored balls with strict Arb endpoint comparisons
  - vendor kernels re-hashed at finalize time against config pins, and the
    chains' dependency_sha256 recomputed from those pins
  - calibration JSON re-hashed against the config pin (repo root via
    CG_TUBE_REPO_ROOT, default ../../../..)
  - CONTROLS.json deep-checked: exact control set, expected exit codes
    {positive:0, neg_sign_flip:1, neg_missing_cell:1, neg_sha_tamper:2,
    neg_limit_short:1}, observed == expected, all ok, and its recorded
    checker_sha256 / config_sha256 match the current files
Emits C_G_ENDPOINT_SIGNS.json, C_G_IDENTITY_CROSSCHECK.json,
DEPENDENCIES.json, C_G_TUBE_PILOT.json (all without trailing newline).
Exit 0 PASS / 1 FAIL / 2 structural or provenance error.
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
REQUIRED_FIELDS = ("writer_id", "run_uuid", "process_id", "hostname",
                   "phase", "recorded_at", "started_at", "finished_at",
                   "config_sha256", "dependency_sha256",
                   "input_state_sha256", "previous_record_sha256")
CONTROL_EXPECT = {"positive": 0, "neg_sign_flip": 1, "neg_missing_cell": 1,
                  "neg_sha_tamper": 2, "neg_limit_short": 1}


def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    sys.exit(code)


def qa(x: Fr) -> arb:
    return arb(str(x.numerator)) / arb(str(x.denominator))


def reject_legacy_upper(obj) -> None:
    if isinstance(obj, dict):
        if "upper" in obj:
            die("LEGACY upper FIELD PRESENT (schema v1/v2 rejected)", 1)
        for value in obj.values():
            reject_legacy_upper(value)
    elif isinstance(obj, list):
        for value in obj:
            reject_legacy_upper(value)


def load_chain(name: str, phase: str) -> list[dict]:
    prev, out = "GENESIS", []
    for line in (HERE / name).read_bytes().splitlines():
        rec = json.loads(line)
        reject_legacy_upper(rec)
        if rec.get("previous_record_sha256") != prev:
            die(f"CHAIN BROKEN: {name}")
        if rec.get("input_state_sha256") != prev:
            die(f"INPUT STATE SHA MISMATCH IN {name}")
        if rec.get("config_sha256") != CONFIG_SHA:
            die(f"CONFIG SHA MISMATCH IN {name}")
        if rec.get("record_schema") != CONFIG["record_schema"]:
            die(f"RECORD SCHEMA MISMATCH IN {name} "
                f"(v1/v2 and unknown formats are rejected)")
        if rec.get("phase") != phase:
            die(f"PHASE MISMATCH IN {name}")
        for f in REQUIRED_FIELDS:
            if f not in rec or rec[f] in ("", None):
                die(f"MISSING PROVENANCE FIELD {f} IN {name}")
        prev = hashlib.sha256(line).hexdigest()
        out.append(rec)
    return out


def leaf_negative(sub: dict) -> bool:
    C = arb(sub["C_bound"])
    if not bool(arb(C.lower()) >= 0):
        # 負または符号不定の C_bound は偽の負性を作れるため即 FAIL
        die(f"NONNEGATIVITY OF C_bound NOT CERTIFIED at leaf "
            f"{sub['a']}..{sub['b']}", 1)
    rho = (Fr(sub["b"]) - Fr(sub["a"])) / 2
    upper2 = arb((arb(arb(sub["G_prime_m"][1]).upper())
                  + C * qa(rho)).upper())
    neg2 = bool(upper2 < 0)
    if neg2 != bool(sub.get("negative")):
        # 保存フラグは診断値。再構成との不一致は改変兆候として即 FAIL
        die(f"TAYLOR RECONSTRUCTION MISMATCH at leaf {sub['a']}..{sub['b']}",
            1)
    return neg2


def wj(path: Path, obj) -> None:
    path.write_bytes(json.dumps(obj, separators=(",", ":")).encode())


def main() -> int:
    eps = load_chain("endpoints_chain.jsonl", "endpoints")
    cls = load_chain("cells_chain.jsonl", "cells")
    sps = load_chain("spots_chain.jsonl", "spots")
    # レコード種別と件数の完全固定（fail-closed）
    if len(eps) != 2 or any(
            r.get("record_type") != "endpoint" for r in eps):
        die("ENDPOINTS CHAIN MUST CONTAIN EXACTLY 2 ENDPOINT RECORDS", 1)
    if len(cls) != CONFIG["n_cells"] or \
       any(r.get("record_type") != "cell" for r in cls):
        die("CELLS CHAIN MUST CONTAIN EXACTLY n_cells CELL RECORDS", 1)
    if len(sps) != len(CONFIG["spot_cell_indices"]) or \
       any(r.get("record_type") != "spot" for r in sps):
        die("SPOTS CHAIN MUST CONTAIN EXACTLY THE SPOT RECORDS", 1)
    dep_shas = {r["dependency_sha256"] for r in eps + cls + sps}
    if len(dep_shas) != 1:
        die("DEPENDENCY SHA VARIES ACROSS CHAINS")
    dep_sha = next(iter(dep_shas))

    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    n = CONFIG["n_cells"]
    w = (r_hi - r_lo) / n

    # --- endpoints (duplicates rejected; exact r; strict recomputed sign)
    ep_recs = [r for r in eps if "endpoint" in r]
    if [r["endpoint"] for r in ep_recs].count("lo") != 1 or \
       [r["endpoint"] for r in ep_recs].count("hi") != 1 or len(ep_recs) != 2:
        die("ENDPOINT RECORD MULTIPLICITY", 1)
    EXPECTED_SIGN = {"lo": 1, "hi": -1}  # checker 側で固定（正本）
    ep = {}
    for r in ep_recs:
        want_r = r_lo if r["endpoint"] == "lo" else r_hi
        if Fr(r["r"]) != want_r:
            die("ENDPOINT r MISMATCH", 1)
        if r.get("want") != EXPECTED_SIGN[r["endpoint"]]:
            die("ENDPOINT WANT FIELD TAMPERED", 1)  # 診断値の照合
        s = 1 if bool(arb(arb(r["G"][0]).lower()) > 0) else \
            (-1 if bool(arb(arb(r["G"][1]).upper()) < 0) else 0)
        ep[r["endpoint"]] = {"r": r["r"], "G": r["G"], "sign": s,
                             "want": EXPECTED_SIGN[r["endpoint"]],
                             "ok": s == EXPECTED_SIGN[r["endpoint"]]}
    ep_ok = ep["lo"]["ok"] and ep["hi"]["ok"]
    wj(HERE / "C_G_ENDPOINT_SIGNS.json",
       {"label": "item3_C-G-TUBE_pilot_endpoint_signs",
        "role": "existence", "lambda": CONFIG["lambda"],
        "config_sha256": CONFIG_SHA, "endpoints": ep,
        "verdict": "PASS" if ep_ok else "FAIL"})

    # --- cells
    cell_recs = [r for r in cls if r.get("record_type") == "cell"]
    idxs = [r["cell_index"] for r in cell_recs]
    if len(idxs) != len(set(idxs)):
        die("DUPLICATE CELL INDEX", 1)
    grid_ok = sorted(idxs) == list(range(n))
    by = {r["cell_index"]: r for r in cell_recs}
    cells_neg_ok, unresolved = True, 0
    for i in range(n):
        r = by.get(i)
        a_exp, b_exp = r_lo + i * w, r_lo + (i + 1) * w
        if r is None or Fr(r["a"]) != a_exp or Fr(r["b"]) != b_exp:
            grid_ok = False
            continue
        leaves = sorted(((Fr(s["a"]), Fr(s["b"])) for s in r["sub"]
                         if leaf_negative(s)))
        cur, tile = a_exp, True
        for la, lb in leaves:
            if la != cur:
                tile = False
                break
            cur = lb
        if not (tile and cur == b_exp):
            cells_neg_ok = False
            unresolved += 1

    # --- spots
    spot_recs = [r for r in sps if r.get("record_type") == "spot"]
    sp_idx = [r["cell_index"] for r in spot_recs]
    if len(sp_idx) != len(set(sp_idx)):
        die("DUPLICATE SPOT INDEX", 1)
    spots_ok = sorted(sp_idx) == sorted(CONFIG["spot_cell_indices"])
    spot_out = []
    for r in spot_recs:
        i = r["cell_index"]
        a_exp, b_exp = r_lo + i * w, r_lo + (i + 1) * w
        meta_ok = (Fr(r["cell_interval"][0]) == a_exp
                   and Fr(r["cell_interval"][1]) == b_exp
                   and r["t_partition_count"] == CONFIG["t_partition_count"]
                   and r["depth_limit"] == CONFIG["int_depth"]
                   and r["evaluation_limit"] == CONFIG["int_limit"])
        id_lo = arb(arb(r["Gprime_identity_ball"][0]).lower())
        id_hi = arb(arb(r["Gprime_identity_ball"][1]).upper())
        ty_lo = arb(arb(r["Gprime_taylor_ball"][0]).lower())
        ty_hi = arb(arb(r["Gprime_taylor_ball"][1]).upper())
        id_neg = bool(id_hi < 0)
        ty_neg = bool(ty_hi < 0)
        inter = not (bool(id_hi < ty_lo) or bool(ty_hi < id_lo))
        spot_out.append({"cell_index": i, "metadata_ok": meta_ok,
                         "identity_negative": id_neg,
                         "taylor_negative": ty_neg,
                         "intersection_nonempty": inter,
                         "Gprime_identity_ball": r["Gprime_identity_ball"],
                         "Gprime_taylor_ball": r["Gprime_taylor_ball"]})
        spots_ok = spots_ok and meta_ok and id_neg and ty_neg and inter
    wj(HERE / "C_G_IDENTITY_CROSSCHECK.json",
       {"label": "item3_C-G-TUBE_pilot_identity_crosscheck",
        "role": "independent evaluator audit; not a proof node for "
                "unchecked cells; a failure here fails the whole pilot",
        "config_sha256": CONFIG_SHA, "spots": spot_out,
        "verdict": "PASS" if spots_ok else "FAIL"})

    # --- vendor re-verify at finalize time
    repo_root_v = Path(os.environ.get(
        "CG_TUBE_REPO_ROOT", HERE / "../../../..")).resolve()
    vendor_ok, vendor_actual, h = True, {}, hashlib.sha256()
    for name, spec in sorted(CONFIG["vendor"].items()):
        p = repo_root_v / spec["path"]
        got = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        vendor_actual[name] = got
        vendor_ok = vendor_ok and got == spec["sha256"]
        h.update(spec["sha256"].encode())
    vendor_ok = vendor_ok and h.hexdigest() == dep_sha

    # --- calibration pin re-verify
    repo_root = Path(os.environ.get(
        "CG_TUBE_REPO_ROOT", HERE / "../../../..")).resolve()
    cal = CONFIG.get("calibration", {})
    cal_path = repo_root / cal.get("path", "")
    cal_got = hashlib.sha256(cal_path.read_bytes()).hexdigest() \
        if cal_path.exists() else None
    cal_ok = bool(cal.get("sha256")) and cal_got == cal.get("sha256")

    # --- controls deep check
    ctrl_ok = False
    ctrl = {}
    if (HERE / "CONTROLS.json").exists():
        ctrl = json.loads((HERE / "CONTROLS.json").read_bytes())
        cs = ctrl.get("controls", {})
        ctrl_ok = (set(cs) == set(CONTROL_EXPECT)
                   and all(cs[k]["expected_exit"] == CONTROL_EXPECT[k]
                           and cs[k]["observed_exit"] == CONTROL_EXPECT[k]
                           and cs[k]["ok"] is True for k in CONTROL_EXPECT)
                   and ctrl.get("checker_sha256") == hashlib.sha256(
                       (HERE / "c_g_tube_checker.py").read_bytes()).hexdigest()
                   and ctrl.get("config_sha256") == CONFIG_SHA
                   and ctrl.get("verdict") == "PASS")

    wj(HERE / "DEPENDENCIES.json", {
        "label": "item3_C-G-TUBE_pilot_dependencies",
        "config_sha256": CONFIG_SHA,
        "dependency_sha256_pinned": h.hexdigest(),
        "dependency_sha256_in_chains": dep_sha,
        "vendor_pinned": CONFIG["vendor"],
        "vendor_actual_at_finalize": vendor_actual,
        "calibration_pinned": cal,
        "calibration_actual_sha256": cal_got,
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(HERE.iterdir())
                          if p.is_file() and p.suffix in (".py", ".json",
                                                          ".yml", ".md")
                          and not p.name.startswith(("C_G_", "DEPENDENCIES",
                                                     "CONTROLS"))}})

    conds = {
        "endpoint_lo_positive": ep["lo"]["ok"],
        "endpoint_hi_negative": ep["hi"]["ok"],
        "coverage_complete_no_gap_no_overlap": grid_ok,
        "all_cells_taylor_negative_reconstructed": cells_neg_ok,
        "spot_crosscheck_pass": spots_ok,
        "vendor_and_calibration_reverified": vendor_ok and cal_ok,
        "negative_controls_deep_pass": ctrl_ok,
        "terminal_unresolved_zero": unresolved == 0,
    }
    verdict = "PASS" if all(conds.values()) else "FAIL"
    wj(HERE / "C_G_TUBE_PILOT.json", {
        "label": "item3_C-G-TUBE_pilot",
        "scope": CONFIG["scope"],
        "lambda": CONFIG["lambda"],
        "interval": [CONFIG["r_lo"], CONFIG["r_hi"]],
        "conclusion": ("exists unique r_c in (1/64, 11/256) with "
                       "G(r_c, 118/25) = 0") if verdict == "PASS" else None,
        "config_sha256": CONFIG_SHA, "dependency_sha256": dep_sha,
        "conditions": conds, "cells": cell_recs, "verdict": verdict})
    print(f"checker/finalize v3: {verdict} {conds}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
