#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(HERE / "tests"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "schema": "ITEM3_SWEEP_PHASE3_TEST_REPORT_V1",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "kernel_evaluations": 0,
        "arb_imported": False,
        "mathematical_calculations": 0,
        "verdict": "PASS" if result.wasSuccessful() else "FAIL",
    }
    raw = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    print(raw)
    if args.write_report:
        (HERE / "PHASE3_TEST_REPORT.json").write_text(raw, encoding="ascii")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
