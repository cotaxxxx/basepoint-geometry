#!/usr/bin/env python3
"""Fail-closed synthetic controls for the C-G-TUBE v5 checker.

These controls validate checker behavior, not the mathematical certificate.
The positive case exercises center-identity cells, outer Taylor cells, refined
identity spot 0, adaptive Taylor spot 18, and single-Taylor spots 37 and 55.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, localcontext
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_bytes())
EXPECT = {
    "positive": 0,
    "neg_sign_flip": 1,
    "neg_missing_cell": 1,
    "neg_sha_tamper": 2,
    "neg_limit_short": 1,
    "neg_spot_leaf_missing": 1,
    "neg_spot_sign_flip": 1,
}


def dependency_sha() -> str:
    h = hashlib.sha256()
    for _, spec in sorted(CONFIG["vendor"].items()):
        h.update(spec["sha256"].encode())
    return h.hexdigest()


def write_chain(path: Path, payloads: list[dict], config_sha: str,
                phase: str) -> None:
    previous = "GENESIS"
    with path.open("wb") as handle:
        for payload in payloads:
            rec = {
                "record_schema": CONFIG["record_schema"],
                "writer_id": "controls-synthetic",
                "run_uuid": "ctrl",
                "process_id": 1,
                "hostname": "ctrl",
                "phase": phase,
                "recorded_at": "-",
                "started_at": "-",
                "finished_at": "-",
                "config_sha256": config_sha,
                "dependency_sha256": dependency_sha(),
                "input_state_sha256": previous,
                "previous_record_sha256": previous,
            }
            rec.update(payload)
            line = json.dumps(rec, separators=(",", ":")).encode()
            handle.write(line + b"\n")
            previous = hashlib.sha256(line).hexdigest()


def center_identity_leaf(a: Fr, b: Fr, *, positive: bool = False) -> dict:
    n = CONFIG["center_t_partition_count"]
    fball = ["0.008", "0.012"] if positive else ["-0.012", "-0.008"]
    summary = ["0.003", "0.007"] if positive else ["-0.007", "-0.003"]
    pieces = [
        {"t_a": str(Fr(i, n)), "t_b": str(Fr(i + 1, n)),
         "Frr_ball": fball}
        for i in range(n)
    ]
    return {
        "method": "center_identity",
        "a": str(a), "b": str(b), "depth": 0,
        "partition_count": n,
        "G_prime_ball": summary,
        "identity_pieces": pieces,
        "negative": not positive,
    }


def taylor_leaf(a: Fr, b: Fr, *, depth: int = 0,
                positive: bool = False, large_c: bool = False) -> dict:
    gpm = (["0.009", "0.011"] if positive
           else ["-0.011", "-0.009"])
    C = "300.0" if large_c else "10.0"
    # Build a deliberately outward decimal enclosure.  The checker performs
    # its reconstruction with Arb-directed rounding, so binary-float reprs
    # are not suitable as containment witnesses.
    with localcontext() as context:
        context.prec = 80
        radius = Decimal((b - a).numerator) / Decimal(2 * (b - a).denominator)
        c = Decimal(C)
        padding = Decimal("1e-12")
        lower = Decimal(gpm[0]) - c * radius - padding
        upper = Decimal(gpm[1]) + c * radius + padding
    negative = upper < 0
    return {
        "method": "taylor",
        "a": str(a), "b": str(b), "depth": depth,
        "G_prime_m": gpm,
        "C_bound": C,
        "reconstructed_ball": [format(lower, "f"), format(upper, "f")],
        "negative": negative,
    }


def adaptive_spot_record(index: int, a: Fr, b: Fr, *,
                         missing: bool = False,
                         sign_flip: bool = False) -> dict:
    mid = (a + b) / 2
    leaves = [taylor_leaf(a, mid, depth=1)]
    if not missing:
        leaves.append(taylor_leaf(mid, b, depth=1, positive=sign_flip))
    tiled = not missing
    all_negative = all(leaf["negative"] for leaf in leaves)
    cross_lo = min(Decimal(leaf["reconstructed_ball"][0]) for leaf in leaves)
    cross_hi = max(Decimal(leaf["reconstructed_ball"][1]) for leaf in leaves)
    return {
        "record_type": "spot",
        "cell_index": index,
        "cell_interval": [str(a), str(b)],
        "t_partition_count": CONFIG["t_partition_count"],
        "depth_limit": CONFIG["int_depth"],
        "evaluation_limit": CONFIG["int_limit"],
        "Gprime_identity_ball": ["-0.012", "-0.008"],
        "identity_negative": True,
        "crosscheck_method": "taylor_adaptive",
        "cross_max_depth": CONFIG["spot_taylor_max_extra_depth"],
        "cross_leaves": leaves,
        "cross_terminal_unresolved": [],
        "cross_tiling_complete": tiled,
        "Gprime_cross_ball": [format(cross_lo, "f"), format(cross_hi, "f")],
        "cross_negative": all_negative and tiled,
        "intersection_ball": ["-0.011", "-0.009"],
        "intersection_nonempty": True,
    }


def synth(tmp: Path, *, flip_cell: bool = False, drop_cell: int | None = None,
          tamper: bool = False, unresolved_cell: int | None = None,
          missing_spot_leaf: bool = False,
          flip_spot_leaf: bool = False) -> None:
    shutil.copy(HERE / "config.json", tmp / "config.json")
    shutil.copy(HERE / "c_g_tube_checker.py", tmp / "c_g_tube_checker.py")
    config_sha = hashlib.sha256((tmp / "config.json").read_bytes()).hexdigest()

    write_chain(tmp / "endpoints_chain.jsonl", [
        {"record_type": "endpoint", "endpoint": "lo", "r": CONFIG["r_lo"],
         "G": ["0.000299", "0.000401"], "sign": 1, "want": 1,
         "ok": True},
        {"record_type": "endpoint", "endpoint": "hi", "r": CONFIG["r_hi"],
         "G": ["-0.000041", "-0.000029"], "sign": -1, "want": -1,
         "ok": True},
    ], config_sha, "endpoints")

    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    n = CONFIG["n_cells"]
    width = (r_hi - r_lo) / n
    center_count = CONFIG["center_identity_cell_count"]
    cells = []
    for index in range(n):
        if index == drop_cell:
            continue
        a, b = r_lo + index * width, r_lo + (index + 1) * width
        if index < center_count:
            sub = [center_identity_leaf(a, b,
                                        positive=flip_cell and index == 7)]
        else:
            sub = [taylor_leaf(a, b)]
        certified = all(rec["negative"] for rec in sub)
        if index == unresolved_cell:
            mid = (a + b) / 2
            sub = [taylor_leaf(a, b, large_c=True),
                   taylor_leaf(a, mid, depth=1)]
            certified = False
        cells.append({
            "record_type": "cell", "cell_index": index,
            "a": str(a), "b": str(b), "sub": sub,
            "certified": certified,
        })
    write_chain(tmp / "cells_chain.jsonl", cells, config_sha, "cells")

    spots = []
    adaptive = set(CONFIG["spot_adaptive_taylor_indices"])
    for index in CONFIG["spot_cell_indices"]:
        a, b = r_lo + index * width, r_lo + (index + 1) * width
        if index in adaptive:
            spots.append(adaptive_spot_record(
                index, a, b, missing=missing_spot_leaf,
                sign_flip=flip_spot_leaf))
            continue
        base = {
            "record_type": "spot",
            "cell_index": index,
            "cell_interval": [str(a), str(b)],
            "t_partition_count": CONFIG["t_partition_count"],
            "depth_limit": CONFIG["int_depth"],
            "evaluation_limit": CONFIG["int_limit"],
            "Gprime_identity_ball": ["-0.012", "-0.008"],
            "identity_negative": True,
            "intersection_ball": ["-0.011", "-0.009"],
            "intersection_nonempty": True,
        }
        if index < center_count:
            base.update({
                "crosscheck_method": "identity_refined",
                "cross_partition_count":
                    CONFIG["center_refined_t_partition_count"],
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "Gprime_cross_ball": ["-0.011", "-0.009"],
                "cross_negative": True,
            })
        else:
            leaf = taylor_leaf(a, b)
            base.update({
                "crosscheck_method": "taylor",
                "cross_leaf": leaf,
                "Gprime_cross_ball": leaf["reconstructed_ball"],
                "cross_negative": leaf["negative"],
            })
        spots.append(base)
    write_chain(tmp / "spots_chain.jsonl", spots, config_sha, "spots")

    fake_controls = {
        name: {"expected_exit": expected, "observed_exit": expected,
               "ok": True}
        for name, expected in EXPECT.items()
    }
    (tmp / "CONTROLS.json").write_bytes(json.dumps({
        "label": "synthetic",
        "verdict": "PASS",
        "checker_sha256": hashlib.sha256(
            (tmp / "c_g_tube_checker.py").read_bytes()).hexdigest(),
        "config_sha256": config_sha,
        "controls": fake_controls,
    }, separators=(",", ":")).encode())

    if tamper:
        lines = (tmp / "cells_chain.jsonl").read_bytes().splitlines()
        rec = json.loads(lines[10])
        rec["config_sha256"] = "0" * 64
        lines[10] = json.dumps(rec, separators=(",", ":")).encode()
        (tmp / "cells_chain.jsonl").write_bytes(b"\n".join(lines) + b"\n")


def run_checker(tmp: Path) -> int:
    env = dict(os.environ)
    result = subprocess.run(
        [sys.executable, str(tmp / "c_g_tube_checker.py")],
        capture_output=True, text=True, cwd=tmp, env=env)
    return result.returncode


def main() -> int:
    specs = {
        "positive": {},
        "neg_sign_flip": {"flip_cell": True},
        "neg_missing_cell": {"drop_cell": 30},
        "neg_sha_tamper": {"tamper": True},
        "neg_limit_short": {"unresolved_cell": 40},
        "neg_spot_leaf_missing": {"missing_spot_leaf": True},
        "neg_spot_sign_flip": {"flip_spot_leaf": True},
    }
    results = {}
    all_ok = True
    for name, kwargs in specs.items():
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            synth(tmp, **kwargs)
            observed = run_checker(tmp)
            expected = EXPECT[name]
            results[name] = {
                "expected_exit": expected,
                "observed_exit": observed,
                "ok": observed == expected,
            }
            all_ok = all_ok and observed == expected

    (HERE / "CONTROLS.json").write_bytes(json.dumps({
        "label": "item3_C-G-TUBE_pilot_controls",
        "role": "checker fail-closed validation on synthetic v5 hybrid chains",
        "checker_sha256": hashlib.sha256(
            (HERE / "c_g_tube_checker.py").read_bytes()).hexdigest(),
        "config_sha256": hashlib.sha256(
            (HERE / "config.json").read_bytes()).hexdigest(),
        "controls": results,
        "verdict": "PASS" if all_ok else "FAIL",
    }, separators=(",", ":")).encode())
    print("controls:", "PASS" if all_ok else "FAIL", results)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
