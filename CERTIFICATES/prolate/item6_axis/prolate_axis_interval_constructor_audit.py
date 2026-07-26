#!/usr/bin/env python3
"""Runtime audit for exact rational Arb interval construction."""
from __future__ import annotations

import json
from pathlib import Path

from flint import arb, ctx, fmpq

ctx.dps = 50

def closed_interval(lo: fmpq, hi: fmpq) -> arb:
    if not lo <= hi:
        raise ValueError("require lo <= hi")
    return arb(str((lo + hi) / 2), str((hi - lo) / 2))

cases = [
    (fmpq(1, 200), fmpq(3, 400)),
    (fmpq(1, 20), fmpq(1, 8)),
    (fmpq(63, 64), fmpq(127, 128)),
    (fmpq(1), fmpq(100)),
    (fmpq(0), fmpq(1, 2)),
]
records = []
checks = []
for lo, hi in cases:
    box = closed_interval(lo, hi)
    lo_ball = arb(str(lo))
    hi_ball = arb(str(hi))
    record = {
        "lo": str(lo),
        "hi": str(hi),
        "box": str(box),
        "overlaps_lo": bool(box.overlaps(lo_ball)),
        "overlaps_hi": bool(box.overlaps(hi_ball)),
        "contains_zero": bool(0 in box),
    }
    records.append(record)
    checks.extend([record["overlaps_lo"], record["overlaps_hi"]])
    if lo > 0:
        checks.append(not record["contains_zero"])

legacy = "return arb((lo + hi) / 2, (hi - lo) / 2)"
legacy_files = []
audit_path = Path(__file__).resolve()
for path in sorted(Path(__file__).parent.glob("*.py")):
    if path.resolve() == audit_path:
        continue
    if legacy in path.read_text(encoding="utf-8"):
        legacy_files.append(path.name)
checks.append(not legacy_files)

result = {
    "status": "PASSED" if all(checks) else "FAILED",
    "constructor": "arb(rational_midpoint_string, rational_radius_string)",
    "cases": records,
    "legacy_files": legacy_files,
    "conclusion": (
        "Every tested endpoint ball overlaps the constructed rational "
        "box, every strictly positive test interval excludes zero, and "
        "no legacy fmpq two-argument constructor remains."
    ),
}
output = Path(__file__).with_suffix(".json")
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASSED" else 1)
