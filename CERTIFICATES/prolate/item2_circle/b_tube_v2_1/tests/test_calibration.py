from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import (
    canonical_json_bytes,
    canonical_jsonl,
    chain_genesis,
    parse_canonical_json_bytes,
    sha256_hex,
)


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
        records = []
        previous = chain_genesis(calibration.CHAIN_DOMAIN)
        for index, passed in enumerate(passes):
            previous = calibration._append_record(
                records,
                previous,
                {
                    "candidate_index": index,
                    "cells_attempted": 1,
                    "cells_passed": 1 if passed else 0,
                    "evaluation_count": 1,
                    "joins_passed": passed,
                    "passed": passed,
                    "record_type": "candidate_end",
                },
            )
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

    def test_incomplete_positive_control_has_no_recommendation(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            _, summary, _ = calibration._verify_records(out)
            self.assertEqual(summary["state"], "CALIBRATION_INCOMPLETE")
            self.assertIsNone(summary["recommendation"])

    def test_missing_attempted_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "case"
            count = len(calibration._candidate_pairs(calibration.load_config()[0]))
            self._write_case(out, [False] * count)
            raw = (out / "calibration_records.jsonl").read_bytes().split(b"\n")
            (out / "calibration_records.jsonl").write_bytes(b"\n".join(raw[:-1]))
            with self.assertRaises(calibration.CalibrationError):
                calibration._verify_records(out)

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


if __name__ == "__main__":
    unittest.main()
