#!/usr/bin/env python3
"""Evaluate the candidate (a) sigma-split EXTENDED pilot output against its successor predeclare.
DIAGNOSTIC / NOT_EVIDENCE.  Standard library only; reads, never writes.

Implements only tools/d_ob_p2/predeclare/CANDIDATE_A_SIGMA_SPLIT_EXTENDED_PILOT_PREDECLARE.md:
  Section 4 run-validity gate (items 1-6, item 6 = exact-string bridge to the closed A4 TSV),
  Section 5 counts and k*, Section 6 fallback counts.
If any gate item fails, only the gate is printed: no count, no k*, no fallback.
Provenance: this file makes no claim about its timing relative to the extended output; that is
established only by the actual commit and output chronology.

Usage:
  evaluate_sigma_pilot_ext.py --out OUT.tsv --map MAP.tsv --log RUN.log --exit "EXIT=<n>" --bridge A4.tsv
--exit is the verbatim `EXIT=` line printed by the run command (it is not in the tee'd log).
--test-mode skips the SHA pins (synthetic inputs only) and marks every line TEST_MODE.
Exit code: 0 gate VALID, 1 RUN INVALID, 2 input/pin error.
"""
import argparse
import hashlib
import sys
from pathlib import Path

SCRIPT_SHA = "a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d"
PRODUCER_SHA = "dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b"
MAP_SHA = "0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8"
BRIDGE_SHA = "afed07837353095344befb865c3ee94c9a7020a67b2d4e86f68973dc20635d54"
POPULATION, STRIDE, OFFSET, N = 7662, 32, 0, 240
KS = [1, 8, 16, 32, 64]
CONTROLS = {1: "control: L1 reproduction", 8: "control: A4 bridge"}
CANDIDATES = [16, 32, 64]
BRIDGE_KS = [1, 2, 4, 8]
NEED = 216  # p_k >= 0.90 with denominator 240
SUMMARY = f"rows={N} not_still_unresolved=0 k1_not_reproduced=0"
NOT_READY = "candidate (a) NOT READY at fixed partition, k<=64"
TAG = ""


def header_for(ks):
    return (["key", "depth", "rho_lo", "rho_hi", "z_lo", "z_hi", "still_unresolved", "L1_reproduces_producer",
             "n_regular", "n_cut", "Bcut_upper"]
            + [c for k in ks for c in (f"L_k{k}_lower", f"W_k{k}_upper", f"margin_k{k}_lower", f"fallback_k{k}")]
            + ["seconds"])


def say(s):
    print(TAG + s, flush=True)


def fail(msg):
    say(f"INPUT_ERROR {msg}")
    sys.exit(2)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_tsv(path, ks, what):
    """Return (meta, tail comments, data rows as field lists); input error unless the header is exact."""
    meta, tail, rows, header = {}, [], [], None
    for l in open(path, encoding="utf-8"):
        l = l.rstrip("\n")
        if l.startswith("#"):
            if header is None:
                if l.startswith("# ") and "=" in l:
                    k_, v = l[2:].split("=", 1); meta[k_] = v
            else:
                tail.append(l)
        elif header is None:
            header = l.split("\t")
        else:
            rows.append(l.split("\t"))
    if header != header_for(ks):
        fail(f"{what} header differs from the expected column list")
    for k_, want in (("select", f"stride:{STRIDE}:{OFFSET}"), ("ks", ",".join(map(str, ks))),
                     ("population", str(POPULATION)), ("selected", str(N))):
        if meta.get(k_) != want:
            fail(f"{what} metadata {k_}={meta.get(k_)!r}, expected {want!r}")
    return meta, tail, rows


def expected_keys(map_path):
    lines = [l for l in open(map_path, encoding="utf-8") if not l.startswith("#")]
    hdr = lines[0].rstrip("\n").split("\t")
    need = ["box", "decision", "r0", "r1", "t0", "t1", "l0", "l1", "column"]
    for c in need:
        if hdr.count(c) != 1:
            fail(f"map column {c!r} missing or duplicated")
    ix = {c: hdr.index(c) for c in need}
    pop = []
    for l in lines[1:]:
        f = l.rstrip("\n").split("\t")
        if f[ix["decision"]] == "unresolved" and f[ix["column"]] == "near":
            pop.append("|".join([f[ix["box"]]] + [f[ix[c]] for c in ("r0", "r1", "t0", "t1", "l0", "l1")]))
    return pop, [k for i, k in enumerate(pop) if i % STRIDE == OFFSET]


def main():
    global TAG
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--map", required=True)
    ap.add_argument("--log", required=True); ap.add_argument("--exit", required=True)
    ap.add_argument("--bridge", required=True)
    ap.add_argument("--test-mode", action="store_true")
    a = ap.parse_args()
    if a.test_mode:
        TAG = "TEST_MODE "
    say("== CANDIDATE (a) SIGMA EXTENDED PILOT EVALUATION / DIAGNOSTIC / NOT_EVIDENCE ==")
    for p in (a.out, a.map, a.log, a.bridge):
        if not Path(p).is_file():
            fail(f"missing file {p}")
    for name, p in (("out", a.out), ("log", a.log), ("map", a.map), ("bridge", a.bridge)):
        say(f"{name}_sha256={sha(p)}")

    meta, tail, rows = read_tsv(a.out, KS, "output")
    _, _, brows = read_tsv(a.bridge, BRIDGE_KS, "bridge")
    if not a.test_mode:
        for name, got, want in (("map file", sha(a.map), MAP_SHA), ("bridge file", sha(a.bridge), BRIDGE_SHA),
                                ("output meta map_sha256", meta.get("map_sha256"), MAP_SHA),
                                ("output meta script_sha256", meta.get("script_sha256"), SCRIPT_SHA),
                                ("output meta producer_sha256", meta.get("producer_sha256"), PRODUCER_SHA)):
            if got != want:
                fail(f"pin mismatch: {name} = {got}")
    pop, keys = expected_keys(a.map)
    if len(pop) != POPULATION or len(keys) != N:
        fail(f"map gives population={len(pop)} selected={len(keys)}")
    bcol = {c: i for i, c in enumerate(header_for(BRIDGE_KS))}
    if len(brows) != N or any(len(r) != len(bcol) for r in brows) or [r[0] for r in brows] != keys:
        fail("bridge TSV does not hold the 240 expected keys in order")
    col = {c: i for i, c in enumerate(header_for(KS))}

    # Section 4 gate
    log_lines = [l.rstrip("\n") for l in open(a.log, encoding="utf-8")]
    ok_rows = [r for r in rows if len(r) == len(col)]
    g, detail = {}, {}
    g[1] = a.exit.strip() == "EXIT=0" and SUMMARY in log_lines and f"# {SUMMARY}" in tail
    detail[1] = f"exit_line={a.exit.strip()!r} summary_in_log={SUMMARY in log_lines} summary_in_tsv={f'# {SUMMARY}' in tail}"
    g[2] = len(rows) == N and len(ok_rows) == N and [r[0] for r in rows] == keys
    detail[2] = f"rows={len(rows)} keys_match_selection_in_order={[r[0] for r in rows] == keys}"
    v3 = sum(r[col["L1_reproduces_producer"]] != "yes" for r in ok_rows)
    v4 = sum(r[col["still_unresolved"]] != "yes" for r in ok_rows)
    v5 = sum(not (float(r[col["margin_k1_lower"]]) <= 0) for r in ok_rows)
    v6 = sum(1 for r, b in zip(ok_rows, brows)
             if r[0] != b[0] or r[col["margin_k8_lower"]] != b[bcol["margin_k8_lower"]])
    g[3], detail[3] = g[2] and v3 == 0, f"violations={v3}"
    g[4], detail[4] = g[2] and v4 == 0, f"violations={v4}"
    g[5], detail[5] = g[2] and v5 == 0, f"violations={v5}"
    g[6], detail[6] = g[2] and v6 == 0, f"exact_string_mismatches={v6}"
    for i in range(1, 7):
        dep = " (FAIL because item 2 failed)" if i >= 3 and not g[2] else ""
        say(f"gate_item_{i}={'PASS' if g[i] else 'FAIL'} {detail[i]}{dep}")
    if not all(g.values()):
        say("RUN INVALID")
        return 1
    say("RUN VALID")

    # Section 5 counts and k*
    cnt = {k: sum(float(r[col[f"margin_k{k}_lower"]]) > 0 for r in rows) for k in KS}
    for k in KS:
        say(f"count_k{k}={cnt[k]}/{N}" + (f"  ({CONTROLS[k]})" if k in CONTROLS else f"  meets_216={cnt[k] >= NEED}"))
    kstar = next((k for k in CANDIDATES if cnt[k] >= NEED), None)
    say(f"k_star={kstar}" if kstar is not None else f"k_star=none  {NOT_READY}")

    # Section 6 fallback counts
    for k in KS:
        fb = [int(r[col[f"fallback_k{k}"]]) for r in rows]
        say(f"fallback_k{k} leaves_with_fallback={sum(x > 0 for x in fb)} total_fallback_cells={sum(fb)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
