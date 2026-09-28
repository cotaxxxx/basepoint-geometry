#!/usr/bin/env python3
"""Extract the full terminal-leaf map of a finished D-OB P2 smoke run.
DIAGNOSTIC / NOT_EVIDENCE.

Reads producer_ledger.jsonl read-only and writes one TSV row per terminal
leaf (accepted or unresolved) with exact endpoints, box depth, and the
derived physical bounds rho_lo, rho_hi, z_lo, z_hi and column, computed
with Fractions by the same formulas as the pinned producer
(PBox.bounds / PBox.column, RHO0 = 1/8).

Refuses to write inside the RUN_DIR.  Prints per-box x column x decision
counts and the SHA-256 of the written TSV.
Usage: python3 extract_unresolved_map.py RUN_DIR OUT.tsv
"""
import collections
import json
import sys
from fractions import Fraction as Q
from pathlib import Path
import hashlib

RHO0 = Q(1, 8)
W0 = (Q(1, 8), Q(1, 8), Q(13, 200))


def q(s):
    n, d = s.split("/")
    return Q(int(n), int(d))


def log2_exact(x):
    """x must be a power of two >= 1 (as a Fraction); return the exponent."""
    if x.denominator != 1 or x.numerator & (x.numerator - 1):
        raise ValueError(f"width ratio not a power of two: {x}")
    return x.numerator.bit_length() - 1


def bounds(r0, r1, t0, t1, l0, l1):
    rho_lo = r0 * (1 - t1 * t1) / (1 + t1 * t1)
    rho_hi = r1 * (1 - t0 * t0) / (1 + t0 * t0)
    z_lo = l0 * r0 * 2 * t0 / (1 + t0 * t0)
    z_hi = l1 * r1 * 2 * t1 / (1 + t1 * t1)
    return rho_lo, rho_hi, z_lo, z_hi


def column(rho_lo, rho_hi):
    if rho_lo >= RHO0:
        return "far"
    if rho_hi <= 2 * RHO0:
        return "near"
    return "straddle"


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: extract_unresolved_map.py RUN_DIR OUT.tsv")
    rd, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    if rd == out.parent or rd in out.parents:
        sys.exit("ABORT refusing to write inside RUN_DIR")
    if out.exists():
        sys.exit(f"ABORT output exists: {out}")

    hdr = ["box", "decision", "depth", "r0", "r1", "t0", "t1", "l0", "l1",
           "rho_lo", "rho_hi", "z_lo", "z_hi", "column", "panels", "elapsed_seconds"]
    counts = collections.Counter()
    splits = collections.Counter()
    rows = []
    with open(rd / "producer_ledger.jsonl", "rb") as f:
        for line in f:
            r = json.loads(line)
            if r.get("record_type") != "node_decision":
                continue
            parts = r["node_key"].split("|")
            box = parts[0]
            r0, r1, t0, t1, l0, l1 = (q(s) for s in parts[1:])
            if r["decision"] == "split":
                splits[box] += 1
                continue
            depth = sum(log2_exact(w0 / w) for w0, w in zip(W0, (r1 - r0, t1 - t0, l1 - l0)))
            b = bounds(r0, r1, t0, t1, l0, l1)
            col = column(b[0], b[1])
            counts[(box, col, r["decision"])] += 1
            rows.append([box, r["decision"], str(depth), *parts[1:],
                         *(f"{float(x):.12g}" for x in b), col,
                         str(r.get("panels", "")), f"{r.get('elapsed_seconds', 0):.3f}"])

    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("# DIAGNOSTIC / NOT_EVIDENCE  source=" + str(rd / "producer_ledger.jsonl") + "\n")
        f.write("\t".join(hdr) + "\n")
        for row in rows:
            f.write("\t".join(row) + "\n")

    print("== D-OB P2 FULL TERMINAL MAP / DIAGNOSTIC / NOT_EVIDENCE ==")
    print(f"terminal_rows={len(rows)}")
    for box in sorted({k[0] for k in counts} | set(splits)):
        cells = {(c, d): n for (b, c, d), n in counts.items() if b == box}
        leaves = sum(cells.values())
        print(f"box={box} split={splits[box]} leaves={leaves} tree_ok={splits[box] + 1 == leaves} "
              + " ".join(f"{c}/{d}={n}" for (c, d), n in sorted(cells.items())))
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"OUT={out}\nOUT_SHA256={h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
