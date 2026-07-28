from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import (
    D_ZERO,
    Dyadic,
    Rational,
    canonical_json_bytes,
    canonical_jsonl,
    chain_genesis,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)


def _partition(start: Fraction, end: Fraction, width: Fraction) -> list[tuple[Fraction, Fraction]]:
    cells = []
    left = start
    while left < end:
        right = min(left + width, end)
        cells.append((left, right))
        left = right
    return cells


def _positive_width(record: dict) -> bool:
    try:
        return D_ZERO < Dyadic.from_json(record["width"], "join.width")
    except (KeyError, ValueError):
        return False


def verify_record_layout(out_dir: Path, *, source_head: str | None = None,
                         update_checker: bool = False) -> dict:
    """Independently verify every candidate/start/cell/JOIN/end record in order."""
    config, _ = calibration.load_config(out_dir / "config.calibration.json")
    parsed = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    records = [record for record, _ in parsed]

    previous = chain_genesis(calibration.CHAIN_DOMAIN)
    for record, raw in parsed:
        if record.get("previous_record_sha256") != previous:
            raise calibration.CalibrationError("layout verifier: record chain mismatch")
        calibration.assert_result_namespace(record)
        previous = sha256_hex(raw)

    pairs = calibration._candidate_pairs(config)
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


def _rechain(records: list[dict]) -> tuple[list[dict], str]:
    chained = []
    previous = chain_genesis(calibration.CHAIN_DOMAIN)
    for original in records:
        body = dict(original)
        body.pop("previous_record_sha256", None)
        previous = calibration._append_record(chained, previous, body)
    return chained, previous


class CalibrationConfigTests(unittest.TestCase):
    def _config(self):
        return calibration.load_config()[0]

    def _write(self, directory: Path, obj) -> Path:
        path = directory / "config.json"
        path.write_bytes(canonical_json_bytes(obj))
        return path

    def test_valid_config_and_precision_equality(self):
        config, raw = calibration.load_config()
        self.assertEqual(config["checker_dps"], config["dps"])
        self.assertEqual(raw, canonical_json_bytes(config))

    def test_kernel_pin_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["production_kernel_sha256"] = "0" * 64
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_cg_tuple_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["cg_match_dependency"]["source_head"] = "0" * 40
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_lambda_start_frozen(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["lambda_start"] = {"p": "3", "q": "1"}
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_lambda_end_exact(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["lambda_end"] = {"p": "19", "q": "4"}
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_checker_precision_not_below_runner(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["checker_dps"] = config["dps"] - 1
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_duplicate_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["candidate_lambda_widths"][1] = config["candidate_lambda_widths"][0]
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_unordered_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["candidate_tube_radii"] = list(reversed(config["candidate_tube_radii"]))
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_floating_json_number_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["evaluation_budget"] = 1.5
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(config, sort_keys=True, separators=(",", ":")))
            with self.assertRaises(ValueError):
                calibration.load_config(path)


class CalibrationGuardTests(unittest.TestCase):
    def test_all_repository_python_sources_self_scan_clean(self):
        calibration.assert_clean_source_tree()

    def test_all_python_self_scan_detects_forbidden_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            token = "flo" + "at("
            (root / "bad.py").write_text("x = " + token + "1)")
            with self.assertRaises(calibration.CalibrationError):
                calibration.assert_clean_source_tree(root)

    def test_result_namespace_rejects_production_prefix(self):
        with self.assertRaises(calibration.CalibrationError):
            calibration.assert_result_namespace({"state": "CERT" + "IFIED_X"})

    def test_result_namespace_rejects_production_key(self):
        with self.assertRaises(calibration.CalibrationError):
            calibration.assert_result_namespace({"verdict": "x"})

    def test_stale_output_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "existing"
            path.mkdir()
            with self.assertRaises(calibration.CalibrationError):
                calibration.assert_no_stale_inputs(path)

    def test_symlink_dependency_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.py"
            target.write_text("pass\n")
            link = root / "link.py"
            link.symlink_to(target)
            with self.assertRaises(calibration.CalibrationError):
                calibration._assert_repo_regular_file(link, root)

    def test_affine_rule_is_frozen(self):
        config = calibration.load_config()[0]
        self.assertEqual(config["q_evaluation_rule"], "exact_endpoint_convex_hull_v1")

    def test_workflow_has_tag_head_guard_and_no_dispatch(self):
        calibration.assert_workflow_security()

    def test_result_merge_rejects_surviving_workflow(self):
        with self.assertRaises(calibration.CalibrationError):
            calibration.assert_no_workflow_in_result_merge(
                [".github/workflows/prolate-item2-btube-v2-1-calibration.yml"]
            )

    def test_receipt_noncanonical_bytes_rejected(self):
        with self.assertRaises(ValueError):
            parse_canonical_json_bytes(b'{"a":1, "b":2}')

    def test_payload_digest_detects_change(self):
        original = b"alpha"
        recorded = sha256_hex(original)
        self.assertNotEqual(sha256_hex(original + b"x"), recorded)


class CalibrationRecordTests(unittest.TestCase):
    def _write_case(self, directory: Path, passes: list[bool]):
        config, config_raw = calibration.load_config()
        pairs = calibration._candidate_pairs(config)
        self.assertEqual(len(passes), len(pairs))
        start = Rational.from_json(config["lambda_start"]).as_fraction()
        end = Rational.from_json(config["lambda_end"]).as_fraction()
        records = []
        previous = chain_genesis(calibration.CHAIN_DOMAIN)
        for index, (passed, pair) in enumerate(zip(passes, pairs)):
            width, radius = pair
            previous = calibration._append_record(records, previous, {
                "candidate_index": index,
                "lambda_width": width.to_json(),
                "record_type": "candidate_start",
                "tube_radius": radius.to_json(),
            })
            cells = _partition(start, end, width.as_fraction())
            for cell_index, (left, right) in enumerate(cells):
                previous = calibration._append_record(records, previous, {
                    "candidate_index": index,
                    "cell_index": cell_index,
                    "evaluation_count": 3 * (cell_index + 1),
                    "lambda_interval": {
                        "lo": Rational.from_fraction(left).to_json(),
                        "hi": Rational.from_fraction(right).to_json(),
                    },
                    "passed": passed,
                    "record_type": "cell",
                })
            for join_index in range(max(len(cells) - 1, 0)):
                previous = calibration._append_record(records, previous, {
                    "candidate_index": index,
                    "failure_reason": None,
                    "join_index": join_index,
                    "record_type": "join",
                    "width": Dyadic(1, 20).to_json(),
                })
            previous = calibration._append_record(records, previous, {
                "candidate_index": index,
                "cells_attempted": len(cells),
                "cells_passed": len(cells) if passed else 0,
                "evaluation_count": 3 * len(cells),
                "joins_passed": True,
                "passed": passed,
                "record_type": "candidate_end",
            })
        first = next((index for index, passed in enumerate(passes) if passed), None)
        recommendation = None
        if first is not None:
            width, radius = pairs[first]
            recommendation = {
                "candidate_index": first,
                "lambda_width": width.to_json(),
                "tube_radius": radius.to_json(),
            }
        summary = {
            "candidate_count": len(pairs),
            "chain_tip": previous,
            "machine_conclusion": {"real_analytic": False},
            "recommendation": recommendation,
            "record_count": len(records),
            "schema": "btube-calibration-summary-v1",
            "state": "CALIBRATION_COMPLETE" if recommendation is not None else "CALIBRATION_INCOMPLETE",
        }
        directory.mkdir()
        (directory / "config.calibration.json").write_bytes(config_raw)
        (directory / "calibration_records.jsonl").write_bytes(canonical_jsonl(records))
        (directory / "CALIBRATION_SUMMARY.json").write_bytes(canonical_json_bytes(summary))

    def test_first_passing_candidate_is_deterministic(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            passes = [False] * count
            passes[3] = True
            passes[5] = True
            self._write_case(out, passes)
            _, summary, _ = calibration._verify_records(out)
            self.assertEqual(summary["recommendation"]["candidate_index"], 3)
            self.assertEqual(verify_record_layout(out)["recommendation"]["candidate_index"], 3)

    def test_incomplete_positive_control_has_no_recommendation(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            _, summary, _ = calibration._verify_records(out)
            self.assertEqual(summary["state"], "CALIBRATION_INCOMPLETE")
            self.assertIsNone(summary["recommendation"])
            self.assertEqual(verify_record_layout(out)["state"], "CALIBRATION_INCOMPLETE")

    def test_missing_attempted_cell_rejected_after_rechain(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            parsed = parse_canonical_jsonl((out / "calibration_records.jsonl").read_bytes())
            records = [record for record, _ in parsed]
            missing = next(
                index for index, record in enumerate(records)
                if record.get("record_type") == "cell" and record.get("candidate_index") == 0
            )
            del records[missing]
            chained, tip = _rechain(records)
            (out / "calibration_records.jsonl").write_bytes(canonical_jsonl(chained))
            summary = parse_canonical_json_bytes((out / "CALIBRATION_SUMMARY.json").read_bytes())
            summary["record_count"] = len(chained)
            summary["chain_tip"] = tip
            (out / "CALIBRATION_SUMMARY.json").write_bytes(canonical_json_bytes(summary))
            with self.assertRaises(calibration.CalibrationError):
                verify_record_layout(out)

    def test_record_chain_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            records = (out / "calibration_records.jsonl").read_bytes().split(b"\n")
            record = parse_canonical_json_bytes(records[1])
            record["previous_record_sha256"] = "0" * 64
            records[1] = canonical_json_bytes(record)
            (out / "calibration_records.jsonl").write_bytes(b"\n".join(records))
            with self.assertRaises(calibration.CalibrationError):
                calibration._verify_records(out)

    def test_machine_conclusion_present_and_false(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            summary = parse_canonical_json_bytes((out / "CALIBRATION_SUMMARY.json").read_bytes())
            summary["machine_conclusion"]["real_analytic"] = True
            (out / "CALIBRATION_SUMMARY.json").write_bytes(canonical_json_bytes(summary))
            with self.assertRaises(calibration.CalibrationError):
                calibration._verify_records(out)


def _main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "verify-output":
        parser = argparse.ArgumentParser()
        parser.add_argument("verify-output")
        parser.add_argument("--out", type=Path, required=True)
        parser.add_argument("--source-head", required=True)
        args = parser.parse_args()
        verify_record_layout(args.out, source_head=args.source_head, update_checker=True)
        return 0
    unittest.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
