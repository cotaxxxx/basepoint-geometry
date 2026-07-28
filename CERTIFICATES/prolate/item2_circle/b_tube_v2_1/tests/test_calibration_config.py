from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import D_ZERO, Dyadic, Rational, canonical_json_bytes, canonical_jsonl, chain_genesis, parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex
from record_layout_contract import _partition
from record_layout_verifier import verify_record_layout

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
        self.assertEqual(
            config["lambda_start_status"], calibration.LAMBDA_START_STATUS
        )
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

    def test_lambda_start_placeholder_is_not_frozen_blocal_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["lambda_start"] = {"p": "3", "q": "1"}
            loaded, _ = calibration.load_config(self._write(Path(temporary), config))
            self.assertEqual(loaded["lambda_start"], {"p": "3", "q": "1"})

    def test_lambda_start_status_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["lambda_start_status"] = "BLOCAL_PINNED"
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_dependency_gate_is_fail_closed(self):
        with self.assertRaisesRegex(
            calibration.CalibrationError, "B-LOCAL/B-ENTRY dependency is not pinned"
        ):
            calibration.require_blocal_dependency(self._config())

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
