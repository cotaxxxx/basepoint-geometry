#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from item3_sweep.phase2_bridge import run_phase2_fixture_bridge


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--phase2-dir",
        type=Path,
        default=HERE.parent / "phase2_selftest",
    )
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    report = run_phase2_fixture_bridge(args.phase2_dir.resolve())
    raw = json.dumps(report, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    print(raw)
    if args.write_report:
        (HERE / "PHASE3_PHASE2_FIXTURE_BRIDGE.json").write_text(raw, encoding="ascii")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
