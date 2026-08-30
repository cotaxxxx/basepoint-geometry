#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE.parent / "config.calibration.json"

EXPECTED_CONFIG_SHA256 = (
    "f4ce912ac9ac8e1c78823f61454be80a778f5548a950e622955422ec25425e2d"
)
FAIL_CODE = "FAIL_LAMBDA_TILING"


class GateFailure(RuntimeError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}:{detail}")


def rat(x: dict[str, str]) -> Fraction:
    return Fraction(int(x["p"]), int(x["q"]))


def dyadic(x: dict[str, object]) -> Fraction:
    return Fraction(int(x["m"]), 2 ** int(x["e"]))


def expected_cell_count(start: Fraction, end: Fraction, width: Fraction) -> int:
    if not (start < end and width > 0):
        raise GateFailure(FAIL_CODE, "bad_geometry")
    ratio = (end - start) / width
    return (ratio.numerator + ratio.denominator - 1) // ratio.denominator


def check_count(
    start: Fraction,
    end: Fraction,
    width: Fraction,
    observed_count: int,
) -> None:
    expected = expected_cell_count(start, end, width)
    if observed_count != expected:
        raise GateFailure(
            FAIL_CODE,
            f"width={width};observed={observed_count};expected={expected}",
        )


raw = CONFIG.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED_CONFIG_SHA256:
    raise SystemExit("STOP: CONFIG_SHA_MISMATCH")

cfg = json.loads(raw)
if cfg.get("mode") != "BINDING":
    raise SystemExit("STOP: CONFIG_NOT_BINDING")

start = rat(cfg["blocal_dependency"]["lambda_start"])
end = rat(cfg["lambda_end"])
widths = [dyadic(x) for x in cfg["candidate_lambda_widths"]]

expected = {w: expected_cell_count(start, end, w) for w in widths}

assert expected[Fraction(1, 4)] == 11
assert expected[Fraction(1, 8)] == 22
assert expected[Fraction(1, 16)] == 43

for w, n in sorted(expected.items()):
    check_count(start, end, w, n)

print("NC07_POSITIVE_CONTROL=PASS")

cases = [
    ("NC07a", Fraction(1, 8), 4),
    ("NC07b", Fraction(1, 4), 2),
]

for name, width, count in cases:
    try:
        check_count(start, end, width, count)
    except GateFailure as e:
        print(f"{name}={e.code}")
        print(f"{name}_DETAIL={e.detail}")
        if e.code != FAIL_CODE:
            raise SystemExit(f"STOP: {name} unexpected subcode")
    else:
        raise SystemExit(f"STOP: {name} unexpectedly passed")

print("NC07_CELL_COUNT_GATE=PASS_NOT_PROMOTED")
