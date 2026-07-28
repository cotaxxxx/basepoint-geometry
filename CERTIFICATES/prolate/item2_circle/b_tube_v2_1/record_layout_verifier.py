#!/usr/bin/env python3
"""Independent full record-layout verifier for B-TUBE calibration."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import calibration
from numeric_schema import Rational, canonical_json_bytes, chain_genesis, parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex
from record_layout_contract import _partition, _positive_width, candidate_pairs_from_config

def verify_record_layout(out_dir: Path, *, source_head: str | None = None,
                         update_checker: bool = False,
                         allow_unbound_fixture: bool = False) -> dict:
    """Independently verify every candidate/start/cell/JOIN/end record in order."""
    config, _ = calibration.load_config(out_dir / "config.calibration.json")
    if not allow_unbound_fixture:
        calibration.require_blocal_dependency(config)
    parsed = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    records = [record for record, _ in parsed]

    previous = chain_genesis(calibration.CHAIN_DOMAIN)
    for record, raw in parsed:
        if record.get("previous_record_sha256") != previous:
            raise calibration.CalibrationError("layout verifier: record chain mismatch")
        calibration.assert_result_namespace(record)
        previous = sha256_hex(raw)

    pairs = candidate_pairs_from_config(config)
    start = Rational.from_json(config["lambda_start"]).as_fraction()
    end = Rational.from_json(config["lambda_end"]).as_fraction()
    cursor = 0
    pass_flags = []

    for candidate_index, (width, radius) in enumerate(pairs):
        if cursor >= len(records):
            raise calibration.CalibrationError("layout verifier: missing candidate_start")
        candidate_start = records[cursor]
        cursor += 1
        expected_start = {
            "candidate_index": candidate_index,
            "lambda_width": width.to_json(),
            "record_type": "candidate_start",
            "tube_radius": radius.to_json(),
        }
        for key, value in expected_start.items():
            if candidate_start.get(key) != value:
                raise calibration.CalibrationError(
                    f"layout verifier: candidate_start mismatch at {candidate_index}"
                )

        cells = _partition(start, end, width.as_fraction())
        cell_records = []
        for cell_index, (left, right) in enumerate(cells):
            if cursor >= len(records):
                raise calibration.CalibrationError("layout verifier: missing cell record")
            record = records[cursor]
            cursor += 1
            if record.get("record_type") != "cell":
                raise calibration.CalibrationError("layout verifier: expected cell record")
            if record.get("candidate_index") != candidate_index or record.get("cell_index") != cell_index:
                raise calibration.CalibrationError("layout verifier: cell index mismatch")
            expected_interval = {
                "lo": Rational.from_fraction(left).to_json(),
                "hi": Rational.from_fraction(right).to_json(),
            }
            if record.get("lambda_interval") != expected_interval:
                raise calibration.CalibrationError("layout verifier: cell coverage mismatch")
            if not isinstance(record.get("passed"), bool):
                raise calibration.CalibrationError("layout verifier: cell passed must be bool")
            cell_records.append(record)

        join_records = []
        for join_index in range(max(len(cells) - 1, 0)):
            if cursor >= len(records):
                raise calibration.CalibrationError("layout verifier: missing JOIN record")
            record = records[cursor]
            cursor += 1
            if record.get("record_type") != "join":
                raise calibration.CalibrationError("layout verifier: expected JOIN record")
            if record.get("candidate_index") != candidate_index or record.get("join_index") != join_index:
                raise calibration.CalibrationError("layout verifier: JOIN index mismatch")
            join_records.append(record)

        if cursor >= len(records):
            raise calibration.CalibrationError("layout verifier: missing candidate_end")
        candidate_end = records[cursor]
        cursor += 1
        if candidate_end.get("record_type") != "candidate_end":
            raise calibration.CalibrationError("layout verifier: expected candidate_end")
        if candidate_end.get("candidate_index") != candidate_index:
            raise calibration.CalibrationError("layout verifier: candidate_end index mismatch")

        cell_pass_count = sum(record["passed"] for record in cell_records)
        joins_pass = all(record.get("failure_reason") is None and _positive_width(record)
                         for record in join_records)
        expected_pass = cell_pass_count == len(cell_records) and joins_pass
        final_evaluation_count = cell_records[-1].get("evaluation_count", 0) if cell_records else 0
        expected_end = {
            "cells_attempted": len(cell_records),
            "cells_passed": cell_pass_count,
            "evaluation_count": final_evaluation_count,
            "joins_passed": joins_pass,
            "passed": expected_pass,
        }
        for key, value in expected_end.items():
            if candidate_end.get(key) != value:
                raise calibration.CalibrationError(
                    f"layout verifier: candidate_end {key} mismatch at {candidate_index}"
                )
        pass_flags.append(expected_pass)

    if cursor != len(records):
        raise calibration.CalibrationError("layout verifier: extra record after final candidate")

    summary = parse_canonical_json_bytes(
        (out_dir / "CALIBRATION_SUMMARY.json").read_bytes(), allow_display=False
    )
    calibration.assert_result_namespace(summary)
    if summary.get("record_count") != len(records) or summary.get("chain_tip") != previous:
        raise calibration.CalibrationError("layout verifier: summary chain/count mismatch")
    if summary.get("candidate_count") != len(pairs):
        raise calibration.CalibrationError("layout verifier: summary candidate count mismatch")
    first = next((index for index, passed in enumerate(pass_flags) if passed), None)
    recommendation = None
    if first is not None:
        width, radius = pairs[first]
        recommendation = {
            "candidate_index": first,
            "lambda_width": width.to_json(),
            "tube_radius": radius.to_json(),
        }
    expected_state = "CALIBRATION_COMPLETE" if recommendation is not None else "CALIBRATION_INCOMPLETE"
    if summary.get("recommendation") != recommendation or summary.get("state") != expected_state:
        raise calibration.CalibrationError("layout verifier: recommendation/state mismatch")

    if source_head is not None:
        checker_path = out_dir / "CHECKER_REPORT.json"
        checker = parse_canonical_json_bytes(checker_path.read_bytes(), allow_display=False)
        if checker.get("source_head") != source_head or checker.get("verifier") != "PASS":
            raise calibration.CalibrationError("layout verifier: checker/source-head mismatch")
        if update_checker:
            checker["record_layout_verifier"] = "PASS"
            checker_path.write_bytes(canonical_json_bytes(checker))
    return summary


def _main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("verify-output")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-head", required=True)
    args = parser.parse_args()
    verify_record_layout(args.out, source_head=args.source_head, update_checker=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
