from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import Rational, canonical_json_bytes


class CalibrationConfigTests(unittest.TestCase):
    def _config(self):
        return calibration.load_config()[0]

    def _write(self, directory: Path, obj) -> Path:
        path = directory / "config.json"
        path.write_bytes(canonical_json_bytes(obj))
        return path

    def _diagnostic_profile(self):
        config = self._config()
        config["mode"] = calibration.CALIBRATION_MODE
        config["binding_to_final_lambda_start"] = False
        config["blocal_dependency"] = {
            "artifact_zip_sha256": None,
            "certificate_sha256": None,
            "config_sha256": None,
            "lambda_start": None,
            "machine_conclusion": None,
            "source_head": None,
            "status": calibration.BLOCAL_UNPINNED_STATUS,
        }
        return config

    def test_valid_binding_profile_and_precision_equality(self):
        config, raw = calibration.load_config()
        self.assertEqual(config["checker_dps"], config["dps"])
        self.assertEqual(config["mode"], calibration.BINDING_MODE)
        self.assertIs(config["binding_to_final_lambda_start"], True)
        self.assertNotIn("lambda_start", config)
        self.assertEqual(raw, canonical_json_bytes(config))

    def test_blocal_tuple_exactly_pinned(self):
        config = self._config()
        self.assertEqual(
            config["blocal_dependency"],
            calibration._expected_pinned_blocal(),
        )
        self.assertEqual(
            Rational.from_json(config["blocal_dependency"]["lambda_start"]),
            Rational(3307749, 1600000),
        )
        self.assertEqual(
            config["blocal_dependency"]["machine_conclusion"],
            calibration.BLOCAL_MACHINE_CONCLUSION,
        )

    def test_blocal_dependency_gate_accepts_exact_tuple(self):
        calibration.require_blocal_dependency(self._config())

    def test_blocal_source_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["source_head"] = "0" * 40
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_artifact_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["artifact_zip_sha256"] = "0" * 64
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_certificate_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["certificate_sha256"] = "0" * 64
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_config_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["config_sha256"] = "0" * 64
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_lambda_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["lambda_start"] = {"p": "21", "q": "10"}
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_machine_conclusion_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["machine_conclusion"]["selected_candidate_index"] = 1
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_blocal_status_demotion_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["blocal_dependency"]["status"] = "UNPINNED"
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_binding_flag_must_be_true(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._config()
            config["binding_to_final_lambda_start"] = False
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(self._write(Path(temporary), config))

    def test_diagnostic_profile_remains_fail_closed_and_nonbinding(self):
        with tempfile.TemporaryDirectory() as temporary:
            config = self._diagnostic_profile()
            path = self._write(Path(temporary), config)
            loaded, raw = calibration.load_config(path)
            self.assertEqual(raw, canonical_json_bytes(loaded))
            self.assertEqual(
                calibration.require_diagnostic_mode(loaded),
                Rational(21, 10),
            )
            with self.assertRaisesRegex(
                calibration.CalibrationError, "B-LOCAL/B-ENTRY dependency is not pinned"
            ):
                calibration.require_blocal_dependency(loaded)

    def test_binding_profile_cannot_enter_diagnostic_mode(self):
        with self.assertRaisesRegex(
            calibration.CalibrationError, "diagnostic mode is not enabled"
        ):
            calibration.require_diagnostic_mode(self._config())

    def test_diagnostic_start_is_exact_and_above_stage1_upper(self):
        config = self._config()
        start = Rational.from_json(config["diagnostic_lambda_start"])
        self.assertEqual(start, Rational(21, 10))
        self.assertLess(calibration.BLOCAL_STAGE1_UPPER, start)
        self.assertLess(start, Rational.from_json(config["lambda_end"]))

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


if __name__ == "__main__":
    unittest.main()
