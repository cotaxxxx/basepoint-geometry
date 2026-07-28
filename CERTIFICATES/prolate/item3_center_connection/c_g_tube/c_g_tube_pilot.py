#!/usr/bin/env python3
"""C-G-TUBE single-slice pilot for clean-room GitHub Actions execution.

Artifacts are generated from scratch. Vendor kernels and calibration are
SHA-pinned by config.json. Cells 0..center_identity_cell_count-1 use the
center-regular identity

    G'(r) = integral_0^1 t F_rr(t r) dt,

and the remaining cells use Taylor enclosures. Spot crosschecks use a refined
identity evaluation near the center, an adaptive Taylor tiling at configured
indices (currently spot 18), and a single Taylor enclosure elsewhere.
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


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_vendor() -> str:
    h = hashlib.sha256()
    for name, spec in sorted(CONFIG["vendor"].items()):
        path = REPO_ROOT / spec["path"]
        if not path.exists() or sha_file(path) != spec["sha256"]:
            print(f"VENDOR SHA MISMATCH OR MISSING: {name}", file=sys.stderr)
            sys.exit(2)
        h.update(spec["sha256"].encode())
    return h.hexdigest()


class Chain:
    def __init__(self, path: Path, run_uuid: str, phase: str,
                 dependency_sha: str) -> None:
        self.path = path
        self.run_uuid = run_uuid
        self.phase = phase
        self.dependency_sha = dependency_sha
        self.started = now()
        self.prev = "GENESIS"
        if path.exists() and os.environ.get("CG_TUBE_ALLOW_EXISTING") != "1":
            print(f"CLEAN-ROOM VIOLATION: {path.name} already exists",
                  file=sys.stderr)
            sys.exit(2)
        if path.exists():
            for line in path.read_bytes().splitlines():
                rec = json.loads(line)
                if (rec.get("previous_record_sha256") != self.prev or
                        rec.get("config_sha256") != CONFIG_SHA):
                    print(f"CHAIN INTEGRITY FAILURE: {path.name}",
                          file=sys.stderr)
                    sys.exit(2)
                self.prev = hashlib.sha256(line).hexdigest()

    def append(self, payload: dict) -> None:
        rec = {
            "record_schema": CONFIG["record_schema"],
            "writer_id": WRITER_ID,
            "run_uuid": self.run_uuid,
            "process_id": os.getpid(),
            "hostname": socket.gethostname(),
            "phase": self.phase,
            "recorded_at": now(),
            "started_at": self.started,
            "finished_at": now(),
            "config_sha256": CONFIG_SHA,
            "dependency_sha256": self.dependency_sha,
            "input_state_sha256": self.prev,
            "previous_record_sha256": self.prev,
        }
        rec.update(payload)
        line = json.dumps(rec, separators=(",", ":")).encode()
        with self.path.open("ab") as handle:
            handle.write(line + b"\n")
        self.prev = hashlib.sha256(line).hexdigest()


class Kern:
    def __init__(self) -> None:
        for spec in CONFIG["vendor"].values():
            directory = str((REPO_ROOT / spec["path"]).parent)
            if directory not in sys.path:
                sys.path.insert(0, directory)
        import prolate_circle_F_cleanroom as K
        import prolate_circle_Frr_ext as X
        self.K = K
        self.X = X
        self.n_evals = 0

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


def cert_sign(value: arb) -> int:
    if bool(arb(value.lower()) > 0):
        return 1
    if bool(arb(value.upper()) < 0):
        return -1
    return 0


def text_lower(text: str) -> arb:
    """Parse a stored Arb string and return its directed lower endpoint."""
    return arb(arb(text).lower())


def text_upper(text: str) -> arb:
    """Parse a stored Arb string and return its directed upper endpoint."""
    return arb(arb(text).upper())


def reconstruct_taylor_bounds(a: Fr, b: Fr, gpm: list[str],
                              c_text: str) -> tuple[arb, arb]:
    """Reconstruct exactly from the strings consumed by the checker."""
    radius = (b - a) / 2
    C = arb(c_text)
    lower = arb((text_lower(gpm[0]) - C * qe(radius)).lower())
    upper = arb((text_upper(gpm[1]) + C * qe(radius)).upper())
    return lower, upper


def outward_pair(lower: arb, upper: arb) -> tuple[list[str], arb, arb]:
    """Serialize an interval with a verified outward round-trip guard."""
    guard_exponent = max(12, CONFIG["dps"] - 8)
    guard = arb(f"1e-{guard_exponent}")
    for _ in range(12):
        lo_text = str(arb((lower - guard).lower()))
        hi_text = str(arb((upper + guard).upper()))
        stored_lo, stored_hi = text_lower(lo_text), text_upper(hi_text)
        if not bool(stored_lo > lower) and not bool(stored_hi < upper):
            return [lo_text, hi_text], stored_lo, stored_hi
        guard = guard * 10
    raise RuntimeError("could not serialize an outward Taylor enclosure")


def taylor_gprime(kern: Kern, m: Fr, radius: Fr, lam: arb):
    Fm = kern.F(qe(m), CONFIG["tol_point"], lam)
    Frm = kern.Fr(qe(m), CONFIG["tol_point"], lam)
    Gpm = Frm / qe(m) - Fm / (qe(m) * qe(m))
    rbox = qe(m) + qe(radius) * arb("+/- 1.0")
    Fb = kern.F(rbox, CONFIG["tol_box"], lam)
    Frb = kern.Fr(rbox, CONFIG["tol_box"], lam)
    Frrb = kern.Frr(rbox, CONFIG["tol_box"], lam)
    Gpp = Frrb / rbox - 2 * Frb / (rbox * rbox) + 2 * Fb / (rbox ** 3)
    c1, c2 = abs(arb(Gpp.lower())), abs(arb(Gpp.upper()))
    C = c2 if bool(c2 >= c1) else c1
    slack = C * qe(radius)
    lower = arb((arb(Gpm.lower()) - slack).lower())
    upper = arb((arb(Gpm.upper()) + slack).upper())
    return lower, upper, C, Gpm


def taylor_record(kern: Kern, a: Fr, b: Fr, depth: int, lam: arb) -> dict:
    m, radius = (a + b) / 2, (b - a) / 2
    _, _, C, Gpm = taylor_gprime(kern, m, radius, lam)
    gpm_text = [str(Gpm.lower()), str(Gpm.upper())]
    c_text = str(C)
    lower, upper = reconstruct_taylor_bounds(a, b, gpm_text, c_text)
    stored_ball, _, _ = outward_pair(lower, upper)
    return {
        "method": "taylor",
        "a": str(a),
        "b": str(b),
        "depth": depth,
        "G_prime_m": gpm_text,
        "C_bound": c_text,
        "reconstructed_ball": stored_ball,
        "negative": bool(upper < 0),
    }


def adaptive_taylor(kern: Kern, a: Fr, b: Fr, lam: arb,
                    max_depth: int) -> tuple[list[dict], list[dict], arb, arb]:
    work = [(a, b, 0)]
    leaves: list[dict] = []
    unresolved: list[dict] = []
    while work:
        ca, cb, depth = work.pop(0)
        rec = taylor_record(kern, ca, cb, depth, lam)
        if rec["negative"]:
            leaves.append(rec)
        elif depth < max_depth:
            mid = (ca + cb) / 2
            work.insert(0, (ca, mid, depth + 1))
            work.insert(1, (mid, cb, depth + 1))
        else:
            unresolved.append(rec)
    if leaves:
        bounds = [reconstruct_taylor_bounds(
            Fr(rec["a"]), Fr(rec["b"]), rec["G_prime_m"], rec["C_bound"])
            for rec in leaves]
        hull_lo, hull_hi = bounds[0]
        for lower, upper in bounds[1:]:
            if bool(lower < hull_lo):
                hull_lo = lower
            if bool(upper > hull_hi):
                hull_hi = upper
        return leaves, unresolved, arb(hull_lo.lower()), arb(hull_hi.upper())
    return leaves, unresolved, arb(0), arb(0)


def identity_gprime(kern: Kern, a: Fr, b: Fr, lam: arb, *,
                    partitions: int, tol: str, depth: int, limit: int,
                    keep_pieces: bool):
    """Enclose G' on J=[a,b] using the center-regular F_rr identity."""
    m, radius = (a + b) / 2, (b - a) / 2
    J = qe(m) + qe(radius) * arb("+/- 1.0")
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
                "t_a": str(ta),
                "t_b": str(tb),
                "Frr_ball": [str(arb(frr.lower())), str(arb(frr.upper()))],
                # Diagnostic only.  The checker reconstructs this term
                # independently from t_a, t_b and Frr_ball.
                "weighted_ball": [str(arb(weighted.lower())),
                                  str(arb(weighted.upper()))],
            })
    return arb(total.lower()), arb(total.upper()), pieces


def cells_list():
    r_lo, r_hi = Fr(CONFIG["r_lo"]), Fr(CONFIG["r_hi"])
    width = (r_hi - r_lo) / CONFIG["n_cells"]
    cells = [(r_lo + i * width, r_lo + (i + 1) * width)
             for i in range(CONFIG["n_cells"])]
    return cells, r_lo, r_hi


def exact_tiling(leaves: list[dict], a: Fr, b: Fr) -> bool:
    intervals = sorted((Fr(rec["a"]), Fr(rec["b"])) for rec in leaves)
    cur = a
    for left, right in intervals:
        if left != cur or right <= left:
            return False
        cur = right
    return cur == b


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True,
                        choices=["endpoints", "cells", "spots"])
    args = parser.parse_args()
    ctx.dps = CONFIG["dps"]
    dependency_sha = verify_vendor()
    run_uuid = str(uuid.uuid4())
    lam = qe(Fr(CONFIG["lambda"]))
    cells, r_lo, r_hi = cells_list()
    kern = Kern()

    if args.phase == "endpoints":
        chain = Chain(HERE / "endpoints_chain.jsonl", run_uuid,
                      "endpoints", dependency_sha)
        for key, rvalue, wanted in (("lo", r_lo, 1), ("hi", r_hi, -1)):
            Fv = kern.F(qe(rvalue), CONFIG["tol_endpoint"], lam)
            Gv = Fv / qe(rvalue)
            sign = cert_sign(Gv)
            chain.append({
                "record_type": "endpoint",
                "endpoint": key,
                "r": str(rvalue),
                "G": [str(Gv.lower()), str(Gv.upper())],
                "sign": sign,
                "want": wanted,
                "ok": sign == wanted,
                "n_evals": kern.n_evals,
            })
        print("endpoints done | tip", chain.prev)
        return 0

    if args.phase == "cells":
        chain = Chain(HERE / "cells_chain.jsonl", run_uuid,
                      "cells", dependency_sha)
        center_count = CONFIG["center_identity_cell_count"]
        for index, (a, b) in enumerate(cells):
            work = [(a, b, 0)]
            subrecords: list[dict] = []
            certified = True
            while work:
                ca, cb, depth = work.pop(0)
                if index < center_count:
                    lo, hi, pieces = identity_gprime(
                        kern, ca, cb, lam,
                        partitions=CONFIG["center_t_partition_count"],
                        tol=CONFIG["center_tol"],
                        depth=CONFIG["center_int_depth"],
                        limit=CONFIG["center_int_limit"],
                        keep_pieces=True)
                    negative = bool(hi < 0)
                    subrecords.append({
                        "method": "center_identity",
                        "a": str(ca),
                        "b": str(cb),
                        "depth": depth,
                        "partition_count": CONFIG["center_t_partition_count"],
                        "G_prime_ball": [str(lo), str(hi)],
                        "identity_pieces": pieces,
                        "negative": negative,
                    })
                    max_depth = CONFIG["center_max_extra_depth"]
                else:
                    rec = taylor_record(kern, ca, cb, depth, lam)
                    negative = rec["negative"]
                    subrecords.append(rec)
                    max_depth = CONFIG["max_extra_depth"]
                if not negative:
                    if depth < max_depth:
                        mid = (ca + cb) / 2
                        work.insert(0, (ca, mid, depth + 1))
                        work.insert(1, (mid, cb, depth + 1))
                    else:
                        certified = False
            chain.append({
                "record_type": "cell",
                "cell_index": index,
                "a": str(a),
                "b": str(b),
                "sub": subrecords,
                "certified": certified,
                "n_evals_cum": kern.n_evals,
            })
            method = "center_identity" if index < center_count else "taylor"
            print(f"cell {index}: method={method} certified={certified} "
                  f"subs={len(subrecords)} | tip {chain.prev}", flush=True)
        print("cells done | file sha", sha_file(HERE / "cells_chain.jsonl"))
        return 0

    chain = Chain(HERE / "spots_chain.jsonl", run_uuid,
                  "spots", dependency_sha)
    base_partitions = CONFIG["t_partition_count"]
    center_count = CONFIG["center_identity_cell_count"]
    adaptive_indices = set(CONFIG["spot_adaptive_taylor_indices"])
    for index in CONFIG["spot_cell_indices"]:
        a, b = cells[index]
        id_lo, id_hi, _ = identity_gprime(
            kern, a, b, lam,
            partitions=base_partitions,
            tol=CONFIG["tol_box"],
            depth=CONFIG["int_depth"],
            limit=CONFIG["int_limit"],
            keep_pieces=False)
        payload = {
            "record_type": "spot",
            "cell_index": index,
            "cell_interval": [str(a), str(b)],
            "t_partition_count": base_partitions,
            "depth_limit": CONFIG["int_depth"],
            "evaluation_limit": CONFIG["int_limit"],
            "Gprime_identity_ball": [str(id_lo), str(id_hi)],
            "identity_negative": bool(id_hi < 0),
            "n_evals_cum": kern.n_evals,
        }

        if index < center_count:
            cross_method = "identity_refined"
            cross_lo, cross_hi, cross_pieces = identity_gprime(
                kern, a, b, lam,
                partitions=CONFIG["center_refined_t_partition_count"],
                tol=CONFIG["center_tol"],
                depth=CONFIG["center_int_depth"],
                limit=CONFIG["center_int_limit"],
                keep_pieces=True)
            payload.update({
                "crosscheck_method": cross_method,
                "cross_partition_count":
                    CONFIG["center_refined_t_partition_count"],
                "cross_depth_limit": CONFIG["center_int_depth"],
                "cross_evaluation_limit": CONFIG["center_int_limit"],
                "cross_identity_pieces": cross_pieces,
                "Gprime_cross_ball": [str(cross_lo), str(cross_hi)],
                "cross_negative": bool(cross_hi < 0),
            })
        elif index in adaptive_indices:
            cross_method = "taylor_adaptive"
            max_depth = CONFIG["spot_taylor_max_extra_depth"]
            leaves, unresolved, cross_lo, cross_hi = adaptive_taylor(
                kern, a, b, lam, max_depth)
            tiled = exact_tiling(leaves, a, b)
            cross_summary, _, _ = outward_pair(cross_lo, cross_hi)
            payload.update({
                "crosscheck_method": cross_method,
                "cross_max_depth": max_depth,
                "cross_leaves": leaves,
                "cross_terminal_unresolved": unresolved,
                "cross_tiling_complete": tiled,
                "Gprime_cross_ball": cross_summary,
                "cross_negative": bool(tiled and not unresolved and
                                       leaves and cross_hi < 0),
            })
        else:
            cross_method = "taylor"
            rec = taylor_record(kern, a, b, 0, lam)
            cross_lo, cross_hi = reconstruct_taylor_bounds(
                a, b, rec["G_prime_m"], rec["C_bound"])
            cross_summary, _, _ = outward_pair(cross_lo, cross_hi)
            payload.update({
                "crosscheck_method": cross_method,
                "cross_leaf": rec,
                "Gprime_cross_ball": cross_summary,
                "cross_negative": bool(cross_hi < 0),
            })

        disjoint = bool(id_hi < cross_lo) or bool(cross_hi < id_lo)
        intersection = not disjoint
        i_lo = cross_lo if bool(cross_lo >= id_lo) else id_lo
        i_hi = cross_hi if bool(cross_hi <= id_hi) else id_hi
        payload.update({
            "intersection_ball": [str(i_lo), str(i_hi)] if intersection else None,
            "intersection_nonempty": intersection,
            "n_evals_cum": kern.n_evals,
        })
        chain.append(payload)
        print(f"spot {index}: cross={cross_method} done | tip {chain.prev}",
              flush=True)
    print("spots done | file sha", sha_file(HERE / "spots_chain.jsonl"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
