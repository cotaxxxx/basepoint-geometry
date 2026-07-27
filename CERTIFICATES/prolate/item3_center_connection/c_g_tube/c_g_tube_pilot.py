#!/usr/bin/env python3
"""C-G-TUBE pilot for GitHub Actions clean-room execution.

All artifacts are generated FROM SCRATCH inside Actions from this source and
config.json; no locally computed JSON is imported. Vendor kernels are read
from the repository vendor path and SHA-pinned by config.json.

Phases (run in order by the workflow):
  endpoints -> cells -> spots
Then run_controls.py and c_g_tube_checker.py (which also finalizes).

Records are hash-chained JSONL (previous_record_sha256); every record
carries writer_id, run_uuid, process_id, hostname, phase, timestamps,
config_sha256 and dependency_sha256. Fail-closed:
  - dependency SHA mismatch -> exit 2 before any evaluation
  - a cell not certified at its method-specific depth is recorded UNCERTIFIED
  - endpoint signs must be strict

Cells 0..center_identity_cell_count-1 use the center-regular identity
    G'(r) = integral_0^1 t F_rr(t r) dt,
which avoids the 1/r and 1/r^2 cancellation in the outer Taylor evaluator.
Remaining cells retain the original Taylor enclosure.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import socket
import sys
import uuid
from fractions import Fraction as Fr
from pathlib import Path

from flint import arb, ctx

HERE = Path(__file__).resolve().parent
CONFIG = json.loads((HERE / "config.json").read_bytes())
CONFIG_SHA = hashlib.sha256((HERE / "config.json").read_bytes()).hexdigest()
REPO_ROOT = Path(os.environ.get(
    "CG_TUBE_REPO_ROOT", HERE / "../../../..")).resolve()
WRITER_ID = "github-actions-clean-room"


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def qe(x: Fr) -> arb:
    return arb(str(x.numerator)) / arb(str(x.denominator))


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_vendor() -> str:
    h = hashlib.sha256()
    for name, spec in sorted(CONFIG["vendor"].items()):
        p = REPO_ROOT / spec["path"]
        if not p.exists() or sha_file(p) != spec["sha256"]:
            print(f"VENDOR SHA MISMATCH OR MISSING: {name}", file=sys.stderr)
            sys.exit(2)
        h.update(spec["sha256"].encode())
    return h.hexdigest()


class Chain:
    def __init__(self, path: Path, run_uuid: str, phase: str,
                 dep_sha: str) -> None:
        self.path, self.run_uuid = path, run_uuid
        self.phase, self.dep_sha = phase, dep_sha
        self.started = now()
        self.prev = "GENESIS"
        if path.exists() and os.environ.get("CG_TUBE_ALLOW_EXISTING") != "1":
            print(f"CLEAN-ROOM VIOLATION: {path.name} already exists",
                  file=sys.stderr)
            sys.exit(2)
        if path.exists():
            for line in path.read_bytes().splitlines():
                rec = json.loads(line)
                if rec.get("previous_record_sha256") != self.prev or \
                   rec.get("config_sha256") != CONFIG_SHA:
                    print(f"CHAIN INTEGRITY FAILURE: {path.name}",
                          file=sys.stderr)
                    sys.exit(2)
                self.prev = hashlib.sha256(line).hexdigest()

    def append(self, payload: dict) -> None:
        rec = {"record_schema": CONFIG["record_schema"],
               "writer_id": WRITER_ID, "run_uuid": self.run_uuid,
               "process_id": os.getpid(), "hostname": socket.gethostname(),
               "phase": self.phase, "recorded_at": now(),
               "started_at": self.started, "finished_at": now(),
               "config_sha256": CONFIG_SHA,
               "dependency_sha256": self.dep_sha,
               "input_state_sha256": self.prev,
               "previous_record_sha256": self.prev}
        rec.update(payload)
        line = json.dumps(rec, separators=(",", ":")).encode()
        with self.path.open("ab") as f:
            f.write(line + b"\n")
        self.prev = hashlib.sha256(line).hexdigest()


class Kern:
    def __init__(self) -> None:
        for spec in CONFIG["vendor"].values():
            d = str((REPO_ROOT / spec["path"]).parent)
            if d not in sys.path:
                sys.path.insert(0, d)
        import prolate_circle_F_cleanroom as K
        import prolate_circle_Frr_ext as X
        self.K, self.X, self.n_evals = K, X, 0

    def F(self, r, tol, lam, *, depth=None, limit=None):
        self.n_evals += 1
        return self.K.F_arb(
            r, lam, tol=tol,
            depth=CONFIG["int_depth"] if depth is None else depth,
            limit=CONFIG["int_limit"] if limit is None else limit)

    def Fr(self, r, tol, lam, *, depth=None, limit=None):
        self.n_evals += 1
        return self.K.dFdr_arb(
            r, lam, tol=tol,
            depth=CONFIG["int_depth"] if depth is None else depth,
            limit=CONFIG["int_limit"] if limit is None else limit)

    def Frr(self, r, tol, lam, *, depth=None, limit=None):
        self.n_evals += 1
        return self.X.Frr_arb(
            r, lam, tol=tol,
            depth=CONFIG["int_depth"] if depth is None else depth,
            limit=CONFIG["int_limit"] if limit is None else limit)


def cert_sign(v: arb) -> int:
    if bool(arb(v.lower()) > 0):
        return 1
    if bool(arb(v.upper()) < 0):
        return -1
    return 0


def taylor_gprime(kern: Kern, m: Fr, rad: Fr, lam: arb):
    Fm = kern.F(qe(m), CONFIG["tol_point"], lam)
    Frm = kern.Fr(qe(m), CONFIG["tol_point"], lam)
    Gpm = Frm / qe(m) - Fm / (qe(m) * qe(m))
    rb = qe(m) + qe(rad) * arb("+/- 1.0")
    Fb = kern.F(rb, CONFIG["tol_box"], lam)
    Frb = kern.Fr(rb, CONFIG["tol_box"], lam)
    Frrb = kern.Frr(rb, CONFIG["tol_box"], lam)
    Gpp = Frrb / rb - 2 * Frb / (rb * rb) + 2 * Fb / (rb ** 3)
    c1, c2 = abs(arb(Gpp.lower())), abs(arb(Gpp.upper()))
    C = c2 if bool(c2 >= c1) else c1
    slack = C * qe(rad)
    ty_upper = arb((arb(Gpm.upper()) + slack).upper())
    ty_lower = arb((arb(Gpm.lower()) - slack).lower())
    return ty_lower, ty_upper, C, Gpm


def identity_gprime(kern: Kern, a: Fr, b: Fr, lam: arb, *,
                    partitions: int, tol: str, depth: int, limit: int,
                    keep_pieces: bool):
    """Enclose G' on J=[a,b] through the center-regular F_rr identity."""
    m, rad = (a + b) / 2, (b - a) / 2
    J = qe(m) + qe(rad) * arb("+/- 1.0")
    dt = qe(Fr(1, partitions))
    total = arb(0)
    pieces = []
    for i in range(partitions):
        ta, tb = Fr(i, partitions), Fr(i + 1, partitions)
        tm, tr = (ta + tb) / 2, (tb - ta) / 2
        tbox = qe(tm) + qe(tr) * arb("+/- 1.0")
        frr = kern.Frr(tbox * J, tol, lam, depth=depth, limit=limit)
        weighted = tbox * frr * dt
        total += weighted
        if keep_pieces:
            pieces.append({
                "t_a": str(ta), "t_b": str(tb),
                "Frr_ball": [str(arb(frr.lower())), str(arb(frr.upper()))],
                "weighted_ball": [str(arb(weighted.lower())),
                                  str(arb(weighted.upper()))],
            })
    return arb(total.lower()), arb(total.upper()), pieces


def cells_list():
    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    w = (r_hi - r_lo) / CONFIG["n_cells"]
    return ([(r_lo + i * w, r_lo + (i + 1) * w)
             for i in range(CONFIG["n_cells"])], r_lo, r_hi)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phase", required=True,
                   choices=["endpoints", "cells", "spots"])
    args = p.parse_args()
    ctx.dps = CONFIG["dps"]
    dep_sha = verify_vendor()
    run_uuid = str(uuid.uuid4())
    lam = qe(Fr(CONFIG["lambda"]))
    cells, r_lo, r_hi = cells_list()
    kern = Kern()

    if args.phase == "endpoints":
        ch = Chain(HERE / "endpoints_chain.jsonl", run_uuid,
                   "endpoints", dep_sha)
        for key, rf, want in (("lo", r_lo, 1), ("hi", r_hi, -1)):
            Fv = kern.F(qe(rf), CONFIG["tol_endpoint"], lam)
            Gv = Fv / qe(rf)
            s = cert_sign(Gv)
            ch.append({"record_type": "endpoint",
                       "endpoint": key, "r": str(rf),
                       "G": [str(Gv.lower()), str(Gv.upper())],
                       "sign": s, "want": want, "ok": s == want,
                       "n_evals": kern.n_evals})
        print("endpoints done | tip", ch.prev)
        return 0

    if args.phase == "cells":
        ch = Chain(HERE / "cells_chain.jsonl", run_uuid, "cells", dep_sha)
        center_count = CONFIG["center_identity_cell_count"]
        for idx, (a, b) in enumerate(cells):
            work = [(a, b, 0)]
            subrecs, ok_all = [], True
            while work:
                ca, cb, d = work.pop(0)
                m, rad = (ca + cb) / 2, (cb - ca) / 2
                if idx < center_count:
                    lo, hi, pieces = identity_gprime(
                        kern, ca, cb, lam,
                        partitions=CONFIG["center_t_partition_count"],
                        tol=CONFIG["center_tol"],
                        depth=CONFIG["center_int_depth"],
                        limit=CONFIG["center_int_limit"],
                        keep_pieces=True)
                    neg = bool(hi < 0)
                    subrecs.append({
                        "method": "center_identity", "a": str(ca),
                        "b": str(cb), "depth": d,
                        "partition_count": CONFIG["center_t_partition_count"],
                        "G_prime_ball": [str(lo), str(hi)],
                        "identity_pieces": pieces, "negative": neg})
                    max_depth = CONFIG["center_max_extra_depth"]
                else:
                    _tl, ty_upper, C, Gpm = taylor_gprime(
                        kern, m, rad, lam)
                    neg = bool(ty_upper < 0)
                    subrecs.append({
                        "method": "taylor", "a": str(ca), "b": str(cb),
                        "depth": d,
                        "G_prime_m": [str(Gpm.lower()), str(Gpm.upper())],
                        "C_bound": str(C), "negative": neg})
                    max_depth = CONFIG["max_extra_depth"]
                if not neg:
                    if d < max_depth:
                        work.insert(0, (ca, m, d + 1))
                        work.insert(1, (m, cb, d + 1))
                    else:
                        ok_all = False
            ch.append({"record_type": "cell", "cell_index": idx,
                       "a": str(a), "b": str(b), "sub": subrecs,
                       "certified": ok_all, "n_evals_cum": kern.n_evals})
            method = "center_identity" if idx < center_count else "taylor"
            print(f"cell {idx}: method={method} certified={ok_all} "
                  f"subs={len(subrecs)} | tip {ch.prev}", flush=True)
        print("cells done | file sha",
              sha_file(HERE / "cells_chain.jsonl"))
        return 0

    if args.phase == "spots":
        ch = Chain(HERE / "spots_chain.jsonl", run_uuid, "spots", dep_sha)
        N = CONFIG["t_partition_count"]
        center_count = CONFIG["center_identity_cell_count"]
        for idx in CONFIG["spot_cell_indices"]:
            a, b = cells[idx]
            id_lo, id_hi, _ = identity_gprime(
                kern, a, b, lam, partitions=N, tol=CONFIG["tol_box"],
                depth=CONFIG["int_depth"], limit=CONFIG["int_limit"],
                keep_pieces=False)
            if idx < center_count:
                cross_method = "identity_refined"
                cross_lo, cross_hi, _ = identity_gprime(
                    kern, a, b, lam,
                    partitions=CONFIG["center_refined_t_partition_count"],
                    tol=CONFIG["center_tol"],
                    depth=CONFIG["center_int_depth"],
                    limit=CONFIG["center_int_limit"], keep_pieces=False)
                cross_n = CONFIG["center_refined_t_partition_count"]
            else:
                cross_method = "taylor"
                m, rad = (a + b) / 2, (b - a) / 2
                cross_lo, cross_hi, _C, _Gpm = taylor_gprime(
                    kern, m, rad, lam)
                cross_n = None
            disjoint = bool(id_hi < cross_lo) or bool(cross_hi < id_lo)
            inter = not disjoint
            i_lo = cross_lo if bool(cross_lo >= id_lo) else id_lo
            i_hi = cross_hi if bool(cross_hi <= id_hi) else id_hi
            payload = {
                "record_type": "spot", "cell_index": idx,
                "cell_interval": [str(a), str(b)],
                "t_partition_count": N,
                "depth_limit": CONFIG["int_depth"],
                "evaluation_limit": CONFIG["int_limit"],
                "crosscheck_method": cross_method,
                "Gprime_identity_ball": [str(id_lo), str(id_hi)],
                "Gprime_cross_ball": [str(cross_lo), str(cross_hi)],
                "intersection_ball": [str(i_lo), str(i_hi)] if inter else None,
                "identity_negative": bool(id_hi < 0),
                "cross_negative": bool(cross_hi < 0),
                "intersection_nonempty": inter,
                "n_evals_cum": kern.n_evals,
            }
            if cross_n is not None:
                payload["cross_partition_count"] = cross_n
                payload["cross_depth_limit"] = CONFIG["center_int_depth"]
                payload["cross_evaluation_limit"] = CONFIG["center_int_limit"]
            ch.append(payload)
            print(f"spot {idx}: cross={cross_method} done | tip {ch.prev}",
                  flush=True)
        print("spots done | file sha",
              sha_file(HERE / "spots_chain.jsonl"))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
