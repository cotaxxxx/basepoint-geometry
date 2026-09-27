#!/usr/bin/env python3
"""Re-aggregate the (7,7,0) point-limit diagnostic TSV. DIAGNOSTIC / NOT_EVIDENCE.

Recomputes every sign and count from the TSV rows themselves (the diagnostic
log's producer_margin_signs summary is known-bad and is not used).

Reports:
  1. column mapping actually used (auto-detected from the header)
  2. stop_reason counts
  3. per stop_reason: L.lower <= 0 / L.lower > 0 but producer margin <= 0 /
     producer margin > 0, and rows with exception->cut > 0
  4. consistency: accepted <=> producer margin (L-B_cut).lower() > 0
  5. cross-tab against the fixed depth-12 decision of the same cell
     (D_OB_P2_770_INTERIM_AUDIT.md sha 4a1188..., section 5)
  6. i_r strip per (i_t, i_lambda): A accepted, C max_cell_count,
     S selected_empty, X degenerate_crash; '*' marks depth-12 accepted
  7. per (i_t, i_lambda): accepted set is an i_r prefix?  rho separation?

Standard library only; reads the TSV, writes nothing.
Usage: python3 aggregate_770_limit_tsv.py RESULT.tsv
"""
import collections
import csv
import math
import re
import sys
from fractions import Fraction

R0, T0, L0 = Fraction(7, 8), Fraction(7, 8), Fraction(2, 5)
WR, WT, WL = Fraction(1, 128), Fraction(1, 128), Fraction(13, 3200)
DEPTH12_ACCEPTED = ({(0, 15, l) for l in range(5, 16)} | {(1, 15, l) for l in range(10, 16)}
                    | {(2, 15, 15)})  # (i_r, i_t, i_lambda), fixed interim audit section 5
SYMBOL = {"accepted": "A", "max_cell_count": "C", "selected_empty": "S", "degenerate_crash": "X"}

SYNONYMS = {
    "r": ["r", "rmid", "rcentre", "rcenter"],
    "t": ["t", "tmid", "tcentre", "tcenter"],
    "lam": ["lambda", "lam", "lmid", "lambdamid"],
    "rho": ["rho"],
    "z": ["z"],
    "column": ["column", "col"],
    "L": ["llower", "lower"],
    "B": ["bcutupper", "bupper", "bcut"],
    "pm": ["producermargin", "produceracceptvalue", "producerlbcutlower", "lminusbcutlower",
           "lbcutlower", "acceptvalue", "producervalue", "producercomparison"],
    "reg": ["regular", "regularcount", "nregular", "regularcells", "regcount"],
    "cut": ["cut", "cutcount", "ncut", "cutcells"],
    "exc": ["exceptioncut", "exceptiontocut", "exccut", "exceptioncutcount", "exceptions", "exccount"],
    "stop": ["stopreason", "stop", "reason"],
    "ir": ["ir"], "it": ["it", "iy"], "il": ["ilambda", "il", "ilam"],
}
FALLBACK_SUBSTR = {"pm": ["producer"], "exc": ["exc"], "stop": ["stop"], "B": ["bcut"]}
REQUIRED = ["r", "t", "lam", "stop"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def map_columns(header):
    normed = {norm(h): h for h in header}
    out = {}
    for key, syns in SYNONYMS.items():
        for s in syns:
            if s in normed:
                out[key] = normed[s]
                break
        else:
            for sub in FALLBACK_SUBSTR.get(key, []):
                hits = [h for n, h in normed.items() if sub in n and h not in out.values()]
                if len(hits) == 1:
                    out[key] = hits[0]
                    break
    return out


def num(s):
    """Parse a rational 'a/b', decimal, or arb string like '[-0.836 +/- 1e-5]'."""
    s = s.strip().strip("[]")
    s = s.split("+/-")[0].strip()
    if not s or s.lower() in ("none", "nan", "null", "-"):
        return None
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None


def idx(value, lo, width):
    return int(math.floor((value - lo) / width))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: aggregate_770_limit_tsv.py RESULT.tsv")
    with open(sys.argv[1], newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    header = list(rows[0].keys()) if rows else []
    cols = map_columns(header)
    print("== 770 POINT-LIMIT RE-AGGREGATION / DIAGNOSTIC / NOT_EVIDENCE ==")
    print(f"rows={len(rows)} header={header}")
    print("column mapping: " + ", ".join(f"{k}->{cols[k]!r}" for k in sorted(cols)))
    missing = [k for k in REQUIRED if k not in cols]
    if missing or ("pm" not in cols and not ("L" in cols and "B" in cols)):
        sys.exit(f"ABORT unmapped required columns: {missing or ['pm or (L,B)']}")

    recs = []
    for row in rows:
        r, t, lam = num(row[cols["r"]]), num(row[cols["t"]]), num(row[cols["lam"]])
        ir = int(row[cols["ir"]]) if "ir" in cols else idx(r, R0, WR)
        it = int(row[cols["it"]]) if "it" in cols else idx(t, T0, WT)
        il = int(row[cols["il"]]) if "il" in cols else idx(lam, L0, WL)
        Lv = num(row[cols["L"]]) if "L" in cols else None
        Bv = num(row[cols["B"]]) if "B" in cols else None
        pm = num(row[cols["pm"]]) if "pm" in cols else (Lv - Bv if Lv is not None and Bv is not None else None)
        rho = num(row[cols["rho"]]) if "rho" in cols else r * (1 - t * t) / (1 + t * t)
        exc = int(float(row[cols["exc"]])) if "exc" in cols and row[cols["exc"]].strip() else None
        recs.append(dict(ir=ir, it=it, il=il, stop=row[cols["stop"]].strip(), L=Lv, pm=pm, rho=rho, exc=exc))

    print("\n-- 2. stop_reason counts --")
    for k, n in sorted(collections.Counter(x["stop"] for x in recs).items()):
        print(f"{k}\t{n}")

    print("\n-- 3. margin classes per stop_reason (from TSV values) --")
    print("stop_reason\tL<=0\tL>0&pm<=0\tpm>0\tpm_missing\texc>0")
    by = collections.defaultdict(list)
    for x in recs:
        by[x["stop"]].append(x)
    for k in sorted(by):
        xs = by[k]
        a = sum(1 for x in xs if x["L"] is not None and x["L"] <= 0)
        b = sum(1 for x in xs if x["L"] is not None and x["L"] > 0 and x["pm"] is not None and x["pm"] <= 0)
        c = sum(1 for x in xs if x["pm"] is not None and x["pm"] > 0)
        d = sum(1 for x in xs if x["pm"] is None)
        e = sum(1 for x in xs if x["exc"])
        print(f"{k}\t{a}\t{b}\t{c}\t{d}\t{e}")
    if "L" not in cols:
        print("(L column not mapped: L<=0 / L>0 split unavailable)")

    print("\n-- 4. consistency accepted <=> pm > 0 --")
    bad = [x for x in recs if x["pm"] is not None and (x["stop"] == "accepted") != (x["pm"] > 0)]
    print(f"inconsistent rows={len(bad)}")
    for x in bad[:10]:
        print(f"  (i_r,i_t,i_l)=({x['ir']},{x['it']},{x['il']}) stop={x['stop']} pm={float(x['pm']):.6g}")

    print("\n-- 5. cross-tab: depth-12 decision x point-limit stop_reason --")
    ct = collections.Counter(("accepted" if (x["ir"], x["it"], x["il"]) in DEPTH12_ACCEPTED else "unresolved",
                              x["stop"]) for x in recs)
    for k, n in sorted(ct.items()):
        print(f"depth12={k[0]}\tlimit={k[1]}\t{n}")

    print("\n-- 6. i_r strips (i_r=0..15 left to right; '*' = depth-12 accepted) --")
    cell = {(x["ir"], x["it"], x["il"]): x for x in recs}
    its = sorted({x["it"] for x in recs}, reverse=True)
    ils = sorted({x["il"] for x in recs})
    for it in its:
        for il in ils:
            s = "".join(SYMBOL.get(cell[(ir, it, il)]["stop"], "?") if (ir, it, il) in cell else "." for ir in range(16))
            m = "".join("*" if (ir, it, il) in DEPTH12_ACCEPTED else " " for ir in range(16))
            print(f"i_t={it:2d} i_l={il:2d}  {s}  [{m}]")

    print("\n-- 7. per-layer structure --")
    for it in its:
        for il in ils:
            xs = sorted((x for x in recs if x["it"] == it and x["il"] == il), key=lambda x: x["ir"])
            acc = [x for x in xs if x["stop"] == "accepted"]
            rej = [x for x in xs if x["stop"] != "accepted"]
            prefix = [x["ir"] for x in acc] == list(range(len(acc)))
            sep = (not acc or not rej) or max(x["rho"] for x in acc) < min(x["rho"] for x in rej)
            thr = f"max_rho_acc={float(max(x['rho'] for x in acc)):.6f}" if acc else "max_rho_acc=-"
            print(f"i_t={it:2d} i_l={il:2d} accepted={len(acc):2d}/{len(xs)} ir_prefix={prefix} rho_separated={sep} {thr}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
