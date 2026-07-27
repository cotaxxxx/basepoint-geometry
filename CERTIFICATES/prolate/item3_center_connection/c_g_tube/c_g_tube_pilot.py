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
  - a cell not certified at max_extra_depth is recorded UNCERTIFIED
  - endpoint signs must be strict
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

    def F(self, r, tol, lam):
        self.n_evals += 1
        return self.K.F_arb(r, lam, tol=tol, depth=CONFIG["int_depth"],
                            limit=CONFIG["int_limit"])

    def Fr(self, r, tol, lam):
        self.n_evals += 1
        return self.K.dFdr_arb(r, lam, tol=tol, depth=CONFIG["int_depth"],
                               limit=CONFIG["int_limit"])

    def Frr(self, r, tol, lam):
        self.n_evals += 1
        return self.X.Frr_arb(r, lam, tol=tol, depth=CONFIG["int_depth"],
                              limit=CONFIG["int_limit"])


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
    # C >= sup|G''| を Arb と厳密有理数のみで構成（binary float 不使用）
    c1, c2 = abs(arb(Gpp.lower())), abs(arb(Gpp.upper()))
    C = c2 if bool(c2 >= c1) else c1
    slack = C * qe(rad)
    ty_upper = arb((arb(Gpm.upper()) + slack).upper())
    ty_lower = arb((arb(Gpm.lower()) - slack).lower())
    return ty_lower, ty_upper, C, Gpm


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
        for idx, (a, b) in enumerate(cells):
            work = [(a, b, 0)]
            subrecs, ok_all = [], True
            while work:
                ca, cb, d = work.pop(0)
                m, rad = (ca + cb) / 2, (cb - ca) / 2
                _tl, ty_upper, C, Gpm = taylor_gprime(kern, m, rad, lam)
                neg = bool(ty_upper < 0)
                subrecs.append({"a": str(ca), "b": str(cb), "depth": d,
                                "G_prime_m": [str(Gpm.lower()),
                                              str(Gpm.upper())],
                                "C_bound": str(C),
                                "negative": neg})
                if not neg:
                    if d < CONFIG["max_extra_depth"]:
                        work.insert(0, (ca, m, d + 1))
                        work.insert(1, (m, cb, d + 1))
                    else:
                        ok_all = False
            ch.append({"record_type": "cell", "cell_index": idx,
                       "a": str(a), "b": str(b), "sub": subrecs,
                       "certified": ok_all, "n_evals_cum": kern.n_evals})
            print(f"cell {idx}: certified={ok_all} subs={len(subrecs)} "
                  f"| tip {ch.prev}", flush=True)
        print("cells done | file sha",
              sha_file(HERE / "cells_chain.jsonl"))
        return 0

    if args.phase == "spots":
        ch = Chain(HERE / "spots_chain.jsonl", run_uuid, "spots", dep_sha)
        N = CONFIG["t_partition_count"]
        for idx in CONFIG["spot_cell_indices"]:
            a, b = cells[idx]
            m, rad = (a + b) / 2, (b - a) / 2
            J = qe(m) + qe(rad) * arb("+/- 1.0")
            total = arb(0)
            for i in range(N):
                t_m, t_r = Fr(2 * i + 1, 2 * N), Fr(1, 2 * N)
                tb = qe(t_m) + qe(t_r) * arb("+/- 1.0")
                total += tb * kern.Frr(tb * J, CONFIG["tol_box"], lam) \
                    * qe(Fr(1, N))
            ty_lower, ty_upper, C, _ = taylor_gprime(kern, m, rad, lam)
            id_lo, id_hi = arb(total.lower()), arb(total.upper())
            # 厳密交差判定（Arb 端点比較のみ）
            disjoint = bool(id_hi < ty_lower) or bool(ty_upper < id_lo)
            inter = not disjoint
            i_lo = ty_lower if bool(ty_lower >= id_lo) else id_lo
            i_hi = ty_upper if bool(ty_upper <= id_hi) else id_hi
            ch.append({"record_type": "spot", "cell_index": idx,
                       "cell_interval": [str(a), str(b)],
                       "t_partition_count": N,
                       "depth_limit": CONFIG["int_depth"],
                       "evaluation_limit": CONFIG["int_limit"],
                       "Gprime_identity_ball": [str(arb(total.lower())),
                                                str(arb(total.upper()))],
                       "Gprime_taylor_ball": [str(ty_lower),
                                              str(ty_upper)],
                       "intersection_ball":
                           [str(i_lo), str(i_hi)] if inter else None,
                       "identity_negative": bool(id_hi < 0),
                       "taylor_negative": bool(ty_upper < 0),
                       "intersection_nonempty": inter,
                       "n_evals_cum": kern.n_evals})
            print(f"spot {idx} done | tip {ch.prev}", flush=True)
        print("spots done | file sha",
              sha_file(HERE / "spots_chain.jsonl"))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
