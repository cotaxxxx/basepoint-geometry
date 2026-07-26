#!/usr/bin/env python3
"""Runtime audit for exact rational Arb interval construction.

The audit compares the historical direct-fmpq constructor with the explicit
rational-string constructor, verifies endpoint overlap and positivity, and
ensures no historical constructor remains in production item-6 sources.
"""
from __future__ import annotations

import json
from pathlib import Path

from flint import arb, ctx, fmpq

ctx.dps = 50


def historical_interval(lo: fmpq, hi: fmpq) -> arb:
    midpoint = (lo + hi) / 2
    radius = (hi - lo) / 2
    return arb(midpoint, radius)


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
    old_box = historical_interval(lo, hi)
    box = closed_interval(lo, hi)
    lo_ball = arb(str(lo))
    hi_ball = arb(str(hi))
    record = {
        "lo": str(lo),
        "hi": str(hi),
        "historical_box": str(old_box),
        "string_box": str(box),
        "historical_contains_zero": bool(0 in old_box),
        "string_contains_zero": bool(0 in box),
        "string_overlaps_lo": bool(box.overlaps(lo_ball)),
        "string_overlaps_hi": bool(box.overlaps(hi_ball)),
        "historical_equals_string": bool(old_box == box),
        "historical_overlaps_string": bool(old_box.overlaps(box)),
    }
    records.append(record)
    checks.extend([record["string_overlaps_lo"], record["string_overlaps_hi"]])
    if lo > 0:
        checks.append(not record["string_contains_zero"])

legacy = "return arb((lo + hi) / 2, (hi - lo) / 2)"
legacy_files = []
audit_path = Path(__file__).resolve()
for path in sorted(Path(__file__).parent.glob("*.py")):
    if path.resolve() == audit_path:
        continue
    if legacy in path.read_text(encoding="utf-8"):
        legacy_files.append(path.name)
checks.append(not legacy_files)

all_equal = all(item["historical_equals_string"] for item in records)
result = {
    "status": "PASSED" if all(checks) else "FAILED",
    "production_constructor": "arb(rational_midpoint_string, rational_radius_string)",
    "historical_constructor_equivalent_on_test_cases": all_equal,
    "cases": records,
    "legacy_files": legacy_files,
    "conclusion": (
        "The production constructor encloses every tested rational endpoint, "
        "strictly positive test boxes exclude zero, and no historical constructor "
        "remains in production files. Equality with the historical constructor is "
        "reported separately and is not assumed."
    ),
}
output = Path(__file__).with_suffix(".json")
output.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASSED" else 1)
