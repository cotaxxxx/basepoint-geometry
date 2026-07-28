#!/usr/bin/env python3
"""Single-dictionary runner for every B-TUBE v2.1 control."""
from __future__ import annotations

from typing import Any

from controls_common import CONTROL_EXPECT
from controls_positive import *
from controls_negative_a import *
from controls_negative_b import *


def run_all_controls() -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for name, expected in CONTROL_EXPECT.items():
        fn = globals().get(name)
        if not callable(fn):
            raise RuntimeError(f"control implementation missing: {name}")
        observed = fn()
        results[name] = {
            "expected_exit": expected,
            "observed_exit": observed,
            "ok": observed == expected,
        }
    return results


def main() -> None:
    results = run_all_controls()
    failed = {name: value for name, value in results.items() if not value["ok"]}
    for name, value in results.items():
        print(name, value)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
