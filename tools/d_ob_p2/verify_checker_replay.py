#!/usr/bin/env python3
"""D-OB P2 smoke checker-replay verifier. READ-ONLY / NOT_EVIDENCE.

Checks the pre-registered replay outcome (chat ruling 2026-09-28) in the
frozen order:
  1 exit_code.txt == "EXIT=1"
  2 checker_report.json: pass=false, bits=192, gamma_star="5/8" (F5, SPEC V2
    L72/L76/L93), mode="smoke", certificate_sha256 == sha(certificate),
    error == PRIMARY, no accepted_leaves / initial_boxes keys
  3 checker_ledger.jsonl: newline-terminated, header identity ==
    {head, checker_sha256, certificate_sha256}; then unit_complete (7,0,0)
    ok=true; then unit_complete (7,7,0) ok=false error "ValueError: leaf
    count"; every later record is a cleanup interruption: actor signal:15,
    pid != checker parent pid (if given), at most 12 records
  4 RUN_DIR files unchanged against rd_sha_before.txt
  5 checker.LOCK absent and no live checker process
Also reports the producer ledger header identity against the pins.

Standard library only; writes nothing.
Usage: python3 verify_checker_replay.py RUN_DIR CHECKER_DIR [CHECKER_PARENT_PID]
"""
import hashlib
import json
import sys
from pathlib import Path

HEAD = "c0f099f946b28e00db95d9ece6c1da703a6dc3b9"
CHECKER_SHA = "762bcf380b091a6fa7c1da50bba06ea0d89a7a56dbe83ce7fb1477b827fc6290"
PRODUCER_SHA = "dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b"
SPEC_SHA = "19af6f7f4aa68771707bc3ffe1abf06fabbbc3098b4bfe0710db00631b8bb069"
CORRECTION_SHA_PREFIX = "315e1d9e"
PRIMARY = "ValueError: initial [7, 7, 0]: ValueError: leaf count"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: verify_checker_replay.py RUN_DIR CHECKER_DIR [CHECKER_PARENT_PID]")
    rd, cd = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    parent = int(sys.argv[3]) if len(sys.argv) == 4 else None
    results = []

    def check(name, ok, detail=""):
        results.append(ok)
        print(f"{'PASS' if ok else 'FAIL'} {name}{' : ' + detail if detail else ''}")

    print("== D-OB P2 CHECKER REPLAY CHECK / READ-ONLY / NOT_EVIDENCE ==")
    cert_sha = sha256(rd / "certificate.jsonl.gz")
    print(f"INFO certificate_sha256={cert_sha}")

    # 1 exit code
    ec = (cd / "exit_code.txt").read_text().strip() if (cd / "exit_code.txt").exists() else None
    check("1 exit_code.txt == EXIT=1", ec == "EXIT=1", repr(ec))

    # 2 report
    rep = json.loads((cd / "checker_report.json").read_text(encoding="utf-8"))
    print(f"INFO report={json.dumps(rep, sort_keys=True)}")
    check("2 report pass == false", rep.get("pass") is False)
    check("2 report bits == 192 (F5)", rep.get("bits") == 192)
    check("2 report gamma_star == 5/8 (F5)", rep.get("gamma_star") == "5/8")
    check("2 report mode == smoke", rep.get("mode") == "smoke")
    check("2 report certificate_sha256 == certificate", rep.get("certificate_sha256") == cert_sha)
    check("2 report error == PRIMARY", rep.get("error") == PRIMARY, repr(rep.get("error")))
    extra = sorted(k for k in ("accepted_leaves", "initial_boxes", "cells") if k in rep)
    check("2 report has no success-only keys", not extra, str(extra) if extra else "")

    # 3 checker ledger
    data = (cd / "checker_ledger.jsonl").read_bytes()
    check("3 ledger ends with newline", data.endswith(b"\n"))
    rows = [json.loads(x) for x in data.splitlines()]
    print(f"INFO ledger records={len(rows)}")
    want_id = {"head": HEAD, "checker_sha256": CHECKER_SHA, "certificate_sha256": cert_sha}
    check("3 ledger header identity", rows[0] == {"record_type": "header", "identity": want_id},
          json.dumps(rows[0].get("identity"), sort_keys=True))
    r1 = rows[1] if len(rows) > 1 else {}
    r2 = rows[2] if len(rows) > 2 else {}
    check("3 record1 unit_complete (7,0,0) ok=true",
          r1.get("record_type") == "unit_complete" and r1.get("initial") == [7, 0, 0]
          and r1.get("result", {}).get("ok") is True, json.dumps(r1.get("result"), sort_keys=True))
    check("3 record2 unit_complete (7,7,0) ok=false leaf count",
          r2.get("record_type") == "unit_complete" and r2.get("initial") == [7, 7, 0]
          and r2.get("result", {}).get("ok") is False
          and r2.get("result", {}).get("error") == "ValueError: leaf count",
          json.dumps(r2.get("result"), sort_keys=True))
    tail = rows[3:]
    bad = [r for r in tail if r.get("record_type") != "interruption" or r.get("actor") != "signal:15"
           or (parent is not None and r.get("pid") == parent)]
    check("3 later records are cleanup interruptions only", not bad, json.dumps(bad[:3]) if bad else f"n={len(tail)}")
    check("3 cleanup interruptions <= 12", len(tail) <= 12, f"n={len(tail)}")
    pids = [r.get("pid") for r in tail]
    print(f"INFO cleanup pids={pids} parent_pid={'unverified (not given)' if parent is None else parent}")
    early = [r for r in rows[1:3] if r.get("record_type") == "interruption"]
    check("3 no interruption before primary failure", not early)

    # 4 RUN_DIR unchanged
    before = {}
    for line in (cd / "rd_sha_before.txt").read_text().splitlines():
        h, p = line.split(None, 1)
        before[p.strip()] = h
    now = {str(p): sha256(p) for p in sorted(rd.iterdir()) if p.is_file() and not p.name.startswith(".")}
    diff = sorted(set(before.items()) ^ set(now.items()))
    check("4 RUN_DIR unchanged vs rd_sha_before.txt", not diff, str(diff[:4]) if diff else f"files={len(now)}")

    # 5 lock and process
    check("5 checker.LOCK absent", not (cd / "checker.LOCK").exists())
    live = []
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                if b"d_ob_p2_checker.py" in (d / "cmdline").read_bytes():
                    live.append(int(d.name))
            except OSError:
                pass
    check("5 no live checker process", not live, f"pids={live}" if live else "")

    # producer ledger header vs pins
    with open(rd / "producer_ledger.jsonl", "rb") as f:
        hdr = json.loads(f.readline())
    ident = hdr.get("identity", {})
    print(f"INFO producer header identity={json.dumps(ident, sort_keys=True)}")
    check("P producer header head", ident.get("head") == HEAD)
    check("P producer header producer_sha256", ident.get("producer_sha256") == PRODUCER_SHA)
    check("P producer header spec_sha256 == SPEC V2", ident.get("spec_sha256") == SPEC_SHA)
    check("P producer header correction_sha256 prefix", str(ident.get("correction_sha256", "")).startswith(CORRECTION_SHA_PREFIX))

    ok = all(results)
    print(f"VERDICT {'REPLAY_AS_PREREGISTERED' if ok else 'DEVIATION_FROM_PREREGISTRATION'} "
          f"pass={sum(results)} fail={len(results) - sum(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
