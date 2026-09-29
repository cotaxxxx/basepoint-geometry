#!/usr/bin/env python3
"""Measure the near-column kernel enclosure under sigma-splitting on unresolved leaves.
DIAGNOSTIC / NOT_EVIDENCE.  Outputs numbers only; makes no acceptance judgement.

Near column, pinned producer: K_H(rho) = [F_rho(rho) - F_rho(-rho)]/(2 rho) is enclosed by
F_rhorho over s in S(B) = [-rho_hi, rho_hi] (mean value form).  Since
    K_H(rho) = (1/2) * int_{-1}^{1} F_rhorho(sigma*rho) dsigma,
splitting sigma in [-1,1] into k equal pieces gives the enclosure
    K_H in (1/k) * sum_j F_rhorho(S_j),  S_j = hull{sigma*rho : sigma in piece j, rho in [rho_lo, rho_hi]},
which is sound for any k.  k=1 gives [-rho_hi, rho_hi]; this is the producer's own interval,
so L_1 must reproduce the producer's L exactly (checked for each leaf).

For each selected leaf the script reruns the pinned producer's refine_cells (deterministic)
to recover the final cell partition, requires that the leaf is still not accepted, and then,
ON THAT FIXED PARTITION, recomputes for each k:
    L_k      = sum_regular area * lower(K_k)
    W_k      = sum_regular area * width(K_k)
    margin_k = lower(L_k - B_cut)
The cut set and B_cut do not depend on k.  The partition is the baseline one; a sigma-split run
would refine differently, so these are fixed-partition values, not results of candidate (a).
If a piece evaluation raises for a cell, the baseline enclosure of that cell is used (still
sound) and the event is counted in fallback_k.

Usage:
  near_sigma_split_measure.py --producer PINNED_PRODUCER.py --map UNRESOLVED_MAP.tsv \
      --select all|stride:N:OFFSET|keys:FILE --ks 1,2,4,8 --out OUT.tsv [--workers 4] [--check-only]
  near_sigma_split_measure.py --producer PINNED_PRODUCER.py --selftest
--map is the TSV written by extract_unresolved_map.py.  Rows with decision=unresolved and
column=near are the population, in file order; stride:N:OFFSET keeps population index i with
i % N == OFFSET; keys:FILE keeps the node keys (box|r0|r1|t0|t1|l0|l1) listed one per line.
--check-only prints the population and selection sizes and exits without computing.
--selftest prints only pass/fail counts (k=1 reproduction and float containment at one
accepted point box); it prints no L or width values.
"""
import argparse
import hashlib
import importlib.util
import math
import platform
import socket
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as Q
from multiprocessing import Pool
from pathlib import Path

PRODUCER_SHA = "dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b"
P = None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_producer(path):
    got = sha(path)
    if got != PRODUCER_SHA:
        sys.exit(f"ABORT producer SHA mismatch: {got}")
    spec = importlib.util.spec_from_file_location("pinned_producer", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pinned_producer"] = mod  # dataclass needs the module registered
    spec.loader.exec_module(mod)
    return mod


def init_worker(path):
    global P
    P = load_producer(path)
    P.ctx.prec = P.BITS


def q(s):
    n, d = s.split("/")
    return Q(int(n), int(d))


def s_pieces(rho_lo, rho_hi, k):
    out = []
    for j in range(k):
        a, b = Q(-1) + Q(2 * j, k), Q(-1) + Q(2 * (j + 1), k)
        c = [a * rho_lo, a * rho_hi, b * rho_lo, b * rho_hi]
        out.append(P.boxq(min(c), max(c)))
    return out


def kernel_k(cell, B, pieces, zb):
    mu, a, cp, sp, lam = P.surface_intervals(cell, B)
    vals = [P.kernel_point(s, zb, mu, a, cp, sp, lam, True) for s in pieces]
    if len(vals) == 1:
        return vals[0]  # k=1: exactly the producer's enclosure (no re-rounding via 0 + x)
    acc = vals[0]
    for v in vals[1:]:
        acc += v
    return acc / len(vals)


def same(x, y):
    return x.mid() == y.mid() and x.rad() == y.rad()


def measure(B, ks):
    """Return (reproduced_unresolved, n_regular, n_cut, Bcut, {k: (L, W, fallbacks)}, k1_exact)."""
    result, data = P.refine_cells(B)
    rho_lo, rho_hi, z_lo, z_hi = B.bounds()
    zb = P.boxq(z_lo, z_hi)
    out = {}
    for k in ks:
        pieces = s_pieces(rho_lo, rho_hi, k)
        L = P.arb(0); W = P.arb(0); fb = 0
        for cell, kval, _ in data["regular"]:
            try:
                kv = kernel_k(cell, B, pieces, zb)
                if not P.finite_ball(kv):
                    raise ValueError("nonfinite")
            except Exception:
                kv = kval; fb += 1
            area = cell.area()
            L += area * kv.lower()
            W += area * P.width(kv)
        out[k] = (L, W, fb)
    k1_exact = same(out[1][0], data["L"]) if 1 in out else None
    return result is None, len(data["regular"]), len(data["cut"]), data["Bcut"], out, k1_exact


def work(args):
    key, ends, depth, ks = args
    t0 = time.monotonic()
    B = P.PBox(*ends, depth)
    unres, nreg, ncut, Bcut, res, k1 = measure(B, ks)
    rho_lo, rho_hi, z_lo, z_hi = B.bounds()
    row = [key, str(depth), f"{float(rho_lo):.12g}", f"{float(rho_hi):.12g}",
           f"{float(z_lo):.12g}", f"{float(z_hi):.12g}",
           "yes" if unres else "NO", "n/a" if k1 is None else ("yes" if k1 else "NO"),
           str(nreg), str(ncut), f"{float(Bcut.upper()):.12e}"]
    for k in ks:
        L, W, fb = res[k]
        row += [f"{float(L.lower()):.12e}", f"{float(W.upper()):.12e}",
                f"{float((L - Bcut).lower()):.12e}", str(fb)]
    row.append(f"{time.monotonic() - t0:.1f}")
    return row


def read_population(path):
    lines = [l for l in open(path, encoding="utf-8") if not l.startswith("#")]
    hdr = lines[0].rstrip("\n").split("\t")
    need = ["box", "decision", "depth", "r0", "r1", "t0", "t1", "l0", "l1", "column"]
    for c in need:
        if hdr.count(c) != 1:
            sys.exit(f"ABORT map column {c!r} missing or duplicated")
    ix = {c: hdr.index(c) for c in need}
    pop = []
    for l in lines[1:]:
        f = l.rstrip("\n").split("\t")
        if f[ix["decision"]] != "unresolved" or f[ix["column"]] != "near":
            continue
        ends = [f[ix[c]] for c in ("r0", "r1", "t0", "t1", "l0", "l1")]
        pop.append(("|".join([f[ix["box"]]] + ends), tuple(q(s) for s in ends), int(f[ix["depth"]])))
    return pop


def select(pop, spec):
    if spec == "all":
        return pop
    if spec.startswith("stride:"):
        _, n, off = spec.split(":")
        n, off = int(n), int(off)
        if not (n >= 1 and 0 <= off < n):
            sys.exit("ABORT bad stride")
        return [p for i, p in enumerate(pop) if i % n == off]
    if spec.startswith("keys:"):
        want = [l.strip() for l in open(spec[5:], encoding="utf-8") if l.strip() and not l.startswith("#")]
        have = {p[0]: p for p in pop}
        missing = [w for w in want if w not in have]
        if missing:
            sys.exit(f"ABORT {len(missing)} keys not in population, first: {missing[0]}")
        if len(set(want)) != len(want):
            sys.exit("ABORT duplicate keys")
        return [have[w] for w in want]
    sys.exit("ABORT bad --select")


def selftest(producer):
    """Pass/fail only.  Point box (9,15,0): already accepted in the baseline probe."""
    init_worker(producer)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import independent_H_sign as h
    ir, it, il = 9, 15, 0
    r = Q(7, 8) + Q(2 * ir + 1, 256); t = Q(7, 8) + Q(2 * it + 1, 256); lam = Q(2, 5) + Q(13, 3200) * Q(2 * il + 1, 2)
    B = P.PBox(r, r, t, t, lam, lam, 12)
    ks = [1, 2, 4]
    cells, data = P.refine_cells(B)
    rho_lo, rho_hi, z_lo, z_hi = B.bounds()
    zb = P.boxq(z_lo, z_hi)
    rho, z, lf = float(rho_hi), float(z_hi), float(lam)
    ok = True
    for k in ks:
        pieces = s_pieces(rho_lo, rho_hi, k)
        L = P.arb(0); viol = 0; fb = 0
        for cell, kval, _ in data["regular"]:
            try:
                kv = kernel_k(cell, B, pieces, zb)
            except Exception:
                kv = kval; fb += 1
            L += cell.area() * kv.lower()
            mu = float((cell.m0 + cell.m1) / 2); ph = math.pi * float((cell.p0 + cell.p1) / 2)
            v = (h.Frho(mu, ph, rho, z, lf) - h.Frho(mu, ph, -rho, z, lf)) / (2 * rho)
            tol = 1e-9 * max(1.0, abs(v))
            if not (float(kv.lower()) - tol <= v <= float(kv.upper()) + tol):
                viol += 1
        line = f"k={k} cells={len(data['regular'])} containment_violations={viol} fallbacks={fb}"
        if k == 1:
            ex = same(L, data["L"]); line += f" L1_reproduces_producer_L={'yes' if ex else 'NO'}"
            ok &= ex
        ok &= viol == 0
        print(line, flush=True)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--producer", required=True)
    ap.add_argument("--map"); ap.add_argument("--select", default="all")
    ap.add_argument("--ks", default="1,2,4,8"); ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--check-only", action="store_true"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a.producer)
    if not a.map:
        sys.exit("ABORT --map required")
    ks = [int(x) for x in a.ks.split(",")]
    if ks[0] != 1 or len(set(ks)) != len(ks) or min(ks) < 1:
        sys.exit("ABORT --ks must start with 1 (reproduction check) and be distinct positive integers")
    pop = read_population(a.map)
    sel = select(pop, a.select)
    print(f"population_near_unresolved={len(pop)} selected={len(sel)} ks={ks}", flush=True)
    if a.check_only:
        return 0
    if not a.out:
        sys.exit("ABORT --out required")
    out = Path(a.out)
    if out.exists():
        sys.exit(f"ABORT output exists: {out}")
    load_producer(a.producer)  # SHA check before any work
    hdr = ["key", "depth", "rho_lo", "rho_hi", "z_lo", "z_hi", "still_unresolved", "L1_reproduces_producer",
           "n_regular", "n_cut", "Bcut_upper"]
    for k in ks:
        hdr += [f"L_k{k}_lower", f"W_k{k}_upper", f"margin_k{k}_lower", f"fallback_k{k}"]
    hdr.append("seconds")
    meta = {
        "script_sha256": sha(__file__), "producer_sha256": PRODUCER_SHA, "map_sha256": sha(a.map),
        "map": a.map, "select": a.select, "ks": ",".join(map(str, ks)),
        "population": len(pop), "selected": len(sel), "host": socket.gethostname(),
        "python": platform.python_version(), "flint": __import__("flint").__version__,
        "started_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    n = bad_unres = bad_k1 = 0
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("# DIAGNOSTIC / NOT_EVIDENCE  fixed baseline partition; no acceptance judgement\n")
        for k_, v in meta.items():
            f.write(f"# {k_}={v}\n")
        f.write("\t".join(hdr) + "\n"); f.flush()
        with Pool(a.workers, initializer=init_worker, initargs=(a.producer,)) as pool:
            for row in pool.imap(work, [(k_, e, d, ks) for k_, e, d in sel]):
                f.write("\t".join(row) + "\n"); f.flush()
                n += 1; bad_unres += row[6] != "yes"; bad_k1 += row[7] != "yes"
                print(f"[{n}/{len(sel)}] {row[0]} {row[-1]}s", flush=True)
        f.write(f"# rows={n} not_still_unresolved={bad_unres} k1_not_reproduced={bad_k1}\n")
    print(f"rows={n} not_still_unresolved={bad_unres} k1_not_reproduced={bad_k1}")
    print(f"OUT={out.resolve()}\nOUT_SHA256={sha(out)}")
    return 0 if (n == len(sel) and bad_unres == 0 and bad_k1 == 0) else 2


if __name__ == "__main__":
    raise SystemExit(main())
