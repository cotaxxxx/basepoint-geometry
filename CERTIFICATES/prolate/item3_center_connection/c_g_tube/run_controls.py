#!/usr/bin/env python3
"""Negative controls for the C-G-TUBE checker (Actions).

Builds synthetic hash-chained inputs in temp sandboxes and asserts the
checker's fail-closed behavior. No vendor-kernel numerics are run; the
checker itself performs Arb interval arithmetic. This validates the
CHECKER, not the mathematics. Controls:

  positive           synthetic fully-passing chains        -> exit 0
  neg_sign_flip      one cell leaf with positive upper     -> exit 1
  neg_missing_cell   cell index 30 absent                  -> exit 1
  neg_sha_tamper     config_sha256 altered in one record   -> exit 2
  neg_limit_short    cell with unresolved (non-tiling)     -> exit 1
                     certified leaves (max-depth exhaustion)

Writes CONTROLS.json (no trailing newline): PASS iff every control behaves
exactly as required. Exit 0 PASS / 1 FAIL.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_bytes())


def dep_sha_from_config():
    h = hashlib.sha256()
    for name, spec in sorted(CONFIG["vendor"].items()):
        h.update(spec["sha256"].encode())
    return h.hexdigest()


def chain_write(path: Path, payloads: list[dict], config_sha: str,
                phase: str) -> None:
    prev = "GENESIS"
    with path.open("wb") as f:
        for pl in payloads:
            rec = {"record_schema": CONFIG["record_schema"],
                   "writer_id": "controls-synthetic", "run_uuid": "ctrl",
                   "process_id": 1, "hostname": "ctrl", "phase": phase,
                   "recorded_at": "-", "started_at": "-", "finished_at": "-",
                   "config_sha256": config_sha,
                   "dependency_sha256": dep_sha_from_config(),
                   "input_state_sha256": prev,
                   "previous_record_sha256": prev}
            rec.update(pl)
            line = json.dumps(rec, separators=(",", ":")).encode()
            f.write(line + b"\n")
            prev = hashlib.sha256(line).hexdigest()


def synth(tmp: Path, *, flip_leaf=False, drop_cell=None, tamper=False,
          unresolved_cell=None) -> None:
    shutil.copy(HERE / "config.json", tmp / "config.json")
    shutil.copy(HERE / "c_g_tube_checker.py", tmp / "c_g_tube_checker.py")
    csha = hashlib.sha256((tmp / "config.json").read_bytes()).hexdigest()
    chain_write(tmp / "endpoints_chain.jsonl", [
        {"record_type": "endpoint", "endpoint": "lo", "r": CONFIG["r_lo"],
         "G": ["[0.0003 +/- 1e-6]", "[0.0004 +/- 1e-6]"],
         "sign": 1, "want": 1, "ok": True},
        {"record_type": "endpoint", "endpoint": "hi", "r": CONFIG["r_hi"],
         "G": ["[-4e-5 +/- 1e-6]", "[-3e-5 +/- 1e-6]"],
         "sign": -1, "want": -1, "ok": True}], csha, "endpoints")
    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    n = CONFIG["n_cells"]
    w = (r_hi - r_lo) / n
    cells = []
    for i in range(n):
        if drop_cell == i:
            continue
        a, b = r_lo + i * w, r_lo + (i + 1) * w
        flip = flip_leaf and i == 7
        gpm = ["[0.009 +/- 1e-9]", "[0.011 +/- 1e-9]"] if flip \
            else ["[-0.011 +/- 1e-9]", "[-0.009 +/- 1e-9]"]
        sub = [{"a": str(a), "b": str(b), "depth": 0,
                "G_prime_m": gpm, "C_bound": "10.0",
                "negative": not flip}]
        if unresolved_cell == i:
            m = (a + b) / 2
            sub = [{"a": str(a), "b": str(b), "depth": 0,
                    "G_prime_m": ["[-0.011 +/- 1e-9]", "[-0.009 +/- 1e-9]"],
                    "C_bound": "300.0", "negative": False},
                   {"a": str(a), "b": str(m), "depth": 1,
                    "G_prime_m": ["[-0.011 +/- 1e-9]", "[-0.009 +/- 1e-9]"],
                    "C_bound": "10.0", "negative": True}]  # right half missing -> non-tiling
        cells.append({"record_type": "cell", "cell_index": i,
                      "a": str(a), "b": str(b), "sub": sub,
                      "certified": True})
    chain_write(tmp / "cells_chain.jsonl", cells, csha, "cells")
    spots = []
    for i in CONFIG["spot_cell_indices"]:
        a, b = r_lo + i * w, r_lo + (i + 1) * w
        spots.append({"record_type": "spot", "cell_index": i,
                      "cell_interval": [str(a), str(b)],
                      "t_partition_count": CONFIG["t_partition_count"],
                      "depth_limit": CONFIG["int_depth"],
                      "evaluation_limit": CONFIG["int_limit"],
                      "Gprime_identity_ball": ["[-0.012 +/- 1e-9]",
                                               "[-0.008 +/- 1e-9]"],
                      "Gprime_taylor_ball": ["[-0.011 +/- 1e-9]",
                                             "[-0.009 +/- 1e-9]"],
                      "intersection_ball": ["-0.011", "-0.009"],
                      "identity_negative": True, "taylor_negative": True,
                      "intersection_nonempty": True})
    chain_write(tmp / "spots_chain.jsonl", spots, csha, "spots")
    fake = {k: {"expected_exit": v, "observed_exit": v, "ok": True}
            for k, v in {"positive": 0, "neg_sign_flip": 1,
                         "neg_missing_cell": 1, "neg_sha_tamper": 2,
                         "neg_limit_short": 1}.items()}
    (tmp / "CONTROLS.json").write_bytes(json.dumps(
        {"label": "synthetic", "verdict": "PASS",
         "checker_sha256": hashlib.sha256(
             (tmp / "c_g_tube_checker.py").read_bytes()).hexdigest(),
         "config_sha256": csha, "controls": fake},
        separators=(",", ":")).encode())
    if tamper:
        lines = (tmp / "cells_chain.jsonl").read_bytes().splitlines()
        rec = json.loads(lines[10])
        rec["config_sha256"] = "0" * 64
        lines[10] = json.dumps(rec, separators=(",", ":")).encode()
        (tmp / "cells_chain.jsonl").write_bytes(b"\n".join(lines) + b"\n")


def run_checker(tmp: Path) -> int:
    env = dict(os.environ)
    r = subprocess.run([sys.executable, str(tmp / "c_g_tube_checker.py")],
                       capture_output=True, text=True, cwd=tmp, env=env)
    return r.returncode


def main() -> int:
    results = {}
    specs = {
        "positive": (dict(), 0),
        "neg_sign_flip": (dict(flip_leaf=True), 1),
        "neg_missing_cell": (dict(drop_cell=30), 1),
        "neg_sha_tamper": (dict(tamper=True), 2),
        "neg_limit_short": (dict(unresolved_cell=3), 1),
    }
    ok = True
    for name, (kw, want) in specs.items():
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            synth(tmp, **kw)
            got = run_checker(tmp)
            results[name] = {"expected_exit": want, "observed_exit": got,
                             "ok": got == want}
            ok = ok and got == want
    (HERE / "CONTROLS.json").write_bytes(json.dumps(
        {"label": "item3_C-G-TUBE_pilot_controls",
         "role": "checker fail-closed validation on synthetic chains "
                 "(the checker itself performs Arb interval arithmetic)",
         "checker_sha256": hashlib.sha256(
             (HERE / "c_g_tube_checker.py").read_bytes()).hexdigest(),
         "config_sha256": hashlib.sha256(
             (HERE / "config.json").read_bytes()).hexdigest(),
         "controls": results,
         "verdict": "PASS" if ok else "FAIL"},
        separators=(",", ":")).encode())
    print("controls:", "PASS" if ok else "FAIL", results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
