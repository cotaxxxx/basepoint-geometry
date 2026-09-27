#!/usr/bin/env python3
"""D-OB P2 smoke completion verifier. READ-ONLY / COMPLETION_CHECK / NOT_EVIDENCE.

Frozen completion criteria (chat ruling 2026-09-27):
  C1 tree identity      split + 1 == accepted + unresolved for every initial box
  C2 process ended      no live process runs d_ob_p2_producer.py on this RUN_DIR
  C3 outputs present    producer_summary.json and certificate.jsonl.gz exist
  C4 exit-code-equiv.   summary unresolved > 0 and initial_boxes == 4;
                        producer.log holds a JSON line equal (parsed) to the
                        summary, followed only by HEARTBEAT lines, no Traceback;
                        summary certificate_sha256 == sha256(certificate);
                        LOCK absent

Extra cross-checks (reported, part of the verdict):
  X1 ledger header present, no partial trailing line, no duplicate node_key
  X2 certificate: 4 records in SMOKE order; per box, box_tree is a valid
     preorder full-binary encoding with '1' == split and '0' == accepted +
     unresolved; listed leaves == ledger accepted leaves (by endpoints)
  X3 summary accepted_leaves / unresolved == ledger totals

Standard library only. Opens every file read-only and writes nothing.
Usage: python3 verify_smoke_completion.py RUN_DIR
"""
import collections
import gzip
import hashlib
import json
import os
import sys
from pathlib import Path

SMOKE = [(7, 0, 0), (7, 7, 0), (0, 0, 3), (3, 3, 1)]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def live_producers(run_dir):
    hits = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        args = [a.decode(errors="replace") for a in argv]
        if any(a.endswith("d_ob_p2_producer.py") for a in args) and any(
            os.path.realpath(a) == run_dir for a in args if a.startswith("/")
        ):
            hits.append(int(d.name))
    return sorted(hits)


def valid_preorder(bits):
    need = 1
    for b in bits:
        if need == 0 or b not in "01":
            return False
        need += 1 if b == "1" else -1
    return need == 0


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: verify_smoke_completion.py RUN_DIR")
    rd = Path(sys.argv[1]).resolve()
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{' : ' + detail if detail else ''}")

    print("== D-OB P2 SMOKE COMPLETION CHECK / READ-ONLY / NOT_EVIDENCE ==")
    print(f"RUN_DIR={rd}")

    # C2 first: a live producer makes everything else provisional.
    pids = live_producers(str(rd))
    check("C2 producer process ended", not pids, f"live pids={pids}" if pids else "none")

    # X1 + C1 ledger
    ledger = rd / "producer_ledger.jsonl"
    data = ledger.read_bytes()
    check("X1 ledger ends with newline", data.endswith(b"\n"))
    lines = data.splitlines()
    rows = []
    for x in lines:
        try:
            rows.append(json.loads(x))
        except ValueError:
            rows.append(None)
    check("X1 ledger all lines parse", None not in rows, f"unparseable={rows.count(None)}")
    rows = [r for r in rows if r is not None]
    check("X1 ledger header", bool(rows) and rows[0].get("record_type") == "header")
    kinds = collections.Counter(r.get("record_type") for r in rows[1:])
    print(f"INFO ledger lines={len(lines)} record_types={dict(kinds)}")
    nodes = [r for r in rows[1:] if r.get("record_type") == "node_decision"]
    keys = [r["node_key"] for r in nodes]
    check("X1 ledger no duplicate node_key", len(keys) == len(set(keys)))

    tally = collections.defaultdict(collections.Counter)
    ledger_leaves = collections.defaultdict(collections.Counter)
    for r in nodes:
        box = tuple(int(v) for v in r["node_key"].split("|")[0].split(","))
        tally[box][r["decision"]] += 1
        if r["decision"] == "accepted":
            ledger_leaves[box][tuple(r["leaf"]["endpoints"])] += 1
    for box in SMOKE:
        t = tally[box]
        s, a, u = t["split"], t["accepted"], t["unresolved"]
        check(f"C1 tree identity {box}", s + 1 == a + u,
              f"split={s} accepted={a} unresolved={u} open={s + 1 - a - u}")
    stray = set(tally) - set(SMOKE)
    check("X1 ledger boxes subset of SMOKE", not stray, f"stray={sorted(stray)}" if stray else "")

    # C3 outputs
    summ_p, cert_p, log_p = rd / "producer_summary.json", rd / "certificate.jsonl.gz", rd / "producer.log"
    check("C3 producer_summary.json exists", summ_p.exists())
    check("C3 certificate.jsonl.gz exists", cert_p.exists())
    if not (summ_p.exists() and cert_p.exists()):
        return verdict(results)

    # C4 exit-code equivalent
    summary = json.loads(summ_p.read_text(encoding="utf-8"))
    print(f"INFO summary={json.dumps(summary, sort_keys=True)}")
    check("C4 summary unresolved > 0", summary.get("unresolved", 0) > 0, f"unresolved={summary.get('unresolved')}")
    check("C4 summary initial_boxes == 4", summary.get("initial_boxes") == 4)
    cert_sha = sha256(cert_p)
    check("C4 certificate sha matches summary", cert_sha == summary.get("certificate_sha256"), cert_sha)
    check("C4 LOCK absent", not (rd / "LOCK").exists())
    log_lines = log_p.read_text(encoding="utf-8", errors="replace").splitlines()
    check("C4 no Traceback in producer.log", not any("Traceback" in x for x in log_lines))
    idx = None
    for i, x in enumerate(log_lines):
        if x.startswith("{"):
            try:
                if json.loads(x) == summary:
                    idx = i
            except ValueError:
                pass
    check("C4 summary JSON line in producer.log", idx is not None, f"line={idx + 1 if idx is not None else None}")
    if idx is not None:
        tail = log_lines[idx + 1:]
        bad = [x for x in tail if not x.startswith("HEARTBEAT ")]
        check("C4 only HEARTBEAT after summary line", not bad, f"non-heartbeat={bad[:3]}" if bad else f"heartbeats_after={len(tail)}")

    # X2 certificate structure vs ledger
    with gzip.open(cert_p, "rt", encoding="utf-8") as f:
        recs = [json.loads(x) for x in f]
    check("X2 certificate 4 records in SMOKE order",
          [tuple(r.get("initial", ())) for r in recs] == SMOKE,
          str([r.get("initial") for r in recs]))
    for r in recs:
        box = tuple(r["initial"])
        bits = r["box_tree"]
        t = tally[box]
        check(f"X2 box_tree preorder valid {box}", valid_preorder(bits))
        check(f"X2 box_tree bits match ledger {box}",
              bits.count("1") == t["split"] and bits.count("0") == t["accepted"] + t["unresolved"],
              f"ones={bits.count('1')} zeros={bits.count('0')}")
        cert_leaves = collections.Counter(tuple(x["endpoints"]) for x in r["leaves"])
        check(f"X2 certificate leaves == ledger accepted {box}", cert_leaves == ledger_leaves[box],
              f"cert={sum(cert_leaves.values())} ledger={sum(ledger_leaves[box].values())}")

    # X3 summary totals vs ledger
    acc = sum(tally[b]["accepted"] for b in SMOKE)
    unr = sum(tally[b]["unresolved"] for b in SMOKE)
    check("X3 summary accepted_leaves == ledger", summary.get("accepted_leaves") == acc, f"ledger={acc}")
    check("X3 summary unresolved == ledger", summary.get("unresolved") == unr, f"ledger={unr}")
    return verdict(results)


def verdict(results):
    ok = all(results)
    print(f"VERDICT {'COMPLETE_EXIT1_EQUIVALENT' if ok else 'NOT_COMPLETE_OR_ANOMALY'} "
          f"pass={sum(results)} fail={len(results) - sum(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
