from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import calibration
from numeric_schema import Dyadic, DyadicInterval, Rational, canonical_json_bytes, sha256_hex
from routed_evaluator import (
    exact_straddle_children,
    routed_bundle_pins,
    selector_for_r_interval,
    trace_genesis,
)
from routed_record_verifier import (
    bridge_grid_sha256,
    verify_route_consistency_certificate_structure,
    verify_routed_trace,
)


class RoutedEvaluatorContractTests(unittest.TestCase):
    def test_selector_and_exact_tie(self):
        r0 = calibration.ROUTED_SELECTOR
        self.assertEqual(
            selector_for_r_interval(DyadicInterval.point(Dyadic(1, 1))),
            calibration.ROUTED_INTERIOR_ROUTE_ID,
        )
        self.assertEqual(
            selector_for_r_interval(DyadicInterval.point(r0)),
            calibration.ROUTED_INTERIOR_ROUTE_ID,
        )
        self.assertEqual(
            selector_for_r_interval(DyadicInterval.point(Dyadic(7, 3))),
            calibration.ROUTED_BOUNDARY_ROUTE_ID,
        )
        self.assertEqual(
            selector_for_r_interval(DyadicInterval(Dyadic(1, 1), Dyadic(7, 3))),
            calibration.ROUTED_STRADDLE_ROUTE_ID,
        )

    def test_exact_straddle_split(self):
        domain = DyadicInterval(Dyadic(1, 1), Dyadic(7, 3))
        left, right = exact_straddle_children(domain)
        self.assertEqual(left, DyadicInterval(Dyadic(1, 1), Dyadic(3, 2)))
        self.assertEqual(right, DyadicInterval(Dyadic(3, 2), Dyadic(7, 3)))

    def test_boundary_budget_exact(self):
        config = calibration.load_config()[0]
        self.assertEqual(config["boundary_route_evaluation_budget"], 123336000)
        self.assertEqual(
            calibration.expected_boundary_route_evaluation_budget(config),
            123336000,
        )

    def _write_config(self, config):
        temporary = tempfile.TemporaryDirectory()
        path = Path(temporary.name) / "config.json"
        path.write_bytes(canonical_json_bytes(config))
        return temporary, path

    def test_boundary_source_pin_tamper_rejected(self):
        config = calibration.load_config()[0]
        config["routed_evaluator_contract"]["boundary_source_sha256"] = "0" * 64
        temporary, path = self._write_config(config)
        with temporary:
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(path)

    def test_adapter_pin_tamper_rejected(self):
        config = calibration.load_config()[0]
        config["routed_evaluator_contract"]["boundary_adapter_sha256"] = "0" * 64
        temporary, path = self._write_config(config)
        with temporary:
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(path)

    def test_boundary_budget_tamper_rejected(self):
        config = calibration.load_config()[0]
        config["boundary_route_evaluation_budget"] -= 1
        temporary, path = self._write_config(config)
        with temporary:
            with self.assertRaises(calibration.CalibrationError):
                calibration.load_config(path)

    def test_pinned_bridge_opens_binding_gate_and_tamper_is_rejected(self):
        config = calibration.load_config()[0]
        self.assertEqual(
            config["route_consistency_certificate_sha256"],
            "b04c92fb264b6ce7bb7d36ed75475fe4fb00bc75a72994281e9a17648b18ac07",
        )
        certificate = calibration.require_route_consistency_certificate(config)
        self.assertEqual(certificate["status"], "PASS")
        self.assertEqual(
            certificate["implementation_source_head"],
            config["audited_source_commit"],
        )

        tampered = dict(config)
        tampered["route_consistency_certificate_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            calibration.CalibrationError,
            "route consistency certificate byte SHA mismatch",
        ):
            calibration.require_route_consistency_certificate(tampered)

    def _trace_record(
        self, *, route_id, r_interval, quantity="F", phase="CANDIDATE:0",
        transform=None, fallback=False,
    ):
        boundary = route_id in {
            calibration.ROUTED_BOUNDARY_ROUTE_ID,
            calibration.ROUTED_STRADDLE_ROUTE_ID,
        }
        detail = (
            {
                "boundary_proof_id": "synthetic",
                "boundary_route_evaluation_count": 1,
                "boundary_route_id": (
                    calibration.ROUTED_F_ROUTE_ID
                    if quantity == "F"
                    else calibration.ROUTED_HU_ROUTE_ID
                ),
                "source_quantity": "F" if quantity == "F" else "H_U",
                "transform": transform,
            }
            if route_id == calibration.ROUTED_BOUNDARY_ROUTE_ID
            else {"interior_kernel_sha256": calibration.KERNEL_SHA256, "source_quantity": quantity}
        )
        body = {
            "boundary_route_evaluation_count_delta": 1 if boundary else 0,
            "boundary_route_evaluation_count_total": 1 if boundary else 0,
            "children": [],
            "contract_id": calibration.ROUTED_CONTRACT_ID,
            "detail": detail,
            "enclosure": DyadicInterval(Dyadic(-1, 4), Dyadic(1, 4)).to_json(),
            "lambda_interval": DyadicInterval.point(Dyadic(5, 1)).to_json(),
            "phase": phase,
            "pins": routed_bundle_pins(),
            "post_failure_fallback": fallback,
            "previous_trace_sha256": trace_genesis(),
            "quantity": quantity,
            "r_interval": r_interval.to_json(),
            "route_id": route_id,
            "schema": calibration.ROUTED_TRACE_SCHEMA,
            "selector_r": calibration.ROUTED_SELECTOR.to_json(),
            "sequence": 0,
        }
        body["trace_record_sha256"] = sha256_hex(canonical_json_bytes(body))
        return body

    def _verify_one_trace(self, record):
        config = calibration.load_config()[0]
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            (out / calibration.ROUTED_TRACE_NAME).write_bytes(
                canonical_json_bytes(record)
            )
            return verify_routed_trace(out, config)

    def test_route_domain_tamper_rejected(self):
        domain = DyadicInterval.point(Dyadic(7, 3))
        record = self._trace_record(
            route_id=calibration.ROUTED_INTERIOR_ROUTE_ID, r_interval=domain
        )
        with self.assertRaisesRegex(calibration.CalibrationError, "route/domain mismatch"):
            self._verify_one_trace(record)

    def test_post_failure_fallback_rejected(self):
        domain = DyadicInterval.point(Dyadic(1, 1))
        record = self._trace_record(
            route_id=calibration.ROUTED_INTERIOR_ROUTE_ID,
            r_interval=domain,
            fallback=True,
        )
        with self.assertRaisesRegex(calibration.CalibrationError, "fallback forbidden"):
            self._verify_one_trace(record)

    def test_derivative_negation_tamper_rejected(self):
        domain = DyadicInterval.point(Dyadic(7, 3))
        record = self._trace_record(
            route_id=calibration.ROUTED_BOUNDARY_ROUTE_ID,
            r_interval=domain,
            quantity="F_r",
            transform=None,
        )
        with self.assertRaisesRegex(
            calibration.CalibrationError, "boundary quantity/negation contract mismatch"
        ):
            self._verify_one_trace(record)

    def test_a0b_interior_route_rejected(self):
        domain = DyadicInterval.point(Dyadic(1, 1))
        record = self._trace_record(
            route_id=calibration.ROUTED_INTERIOR_ROUTE_ID,
            r_interval=domain,
            phase="A0B",
        )
        with self.assertRaisesRegex(
            calibration.CalibrationError, "A0B must use boundary backend"
        ):
            self._verify_one_trace(record)

    def _synthetic_bridge(self):
        rows = []
        lambdas = (
            Fraction(17, 8), Fraction(5, 2), Fraction(3, 1),
            Fraction(7, 2), Fraction(4, 1), Fraction(9, 2),
        )
        for index, (r, lam) in enumerate(
            (pair for k in range(48, 64) for pair in [(Fraction(k, 64), x) for x in lambdas])
        ):
            iv = DyadicInterval(Dyadic(-1, 4), Dyadic(1, 4))
            rows.append({
                "F": {
                    "boundary": iv.to_json(),
                    "interior": iv.to_json(),
                    "intersection": iv.to_json(),
                },
                "F_r": {
                    "boundary": iv.to_json(),
                    "interior": iv.to_json(),
                    "intersection": iv.to_json(),
                },
                "index": index,
                "lambda": Rational.from_fraction(lam).to_json(),
                "r": Rational.from_fraction(r).to_json(),
            })
        config = calibration.load_config()[0]
        return {
            "boundary_route_evaluation_count": 1,
            "contract_id": calibration.ROUTED_CONTRACT_ID,
            "grid_id": calibration.ROUTE_CONSISTENCY_GRID_ID,
            "grid_sha256": bridge_grid_sha256(),
            "implementation_source_head": config["audited_source_commit"],
            "pins": routed_bundle_pins(),
            "producer_settings": {
                "depth": calibration.ROUTE_CONSISTENCY_DEPTH,
                "dps": config["checker_dps"],
                "limit": calibration.ROUTE_CONSISTENCY_LIMIT,
                "tol": calibration.ROUTE_CONSISTENCY_TOL,
            },
            "row_count": 96,
            "rows": rows,
            "schema": calibration.ROUTE_CONSISTENCY_SCHEMA,
            "status": "PASS",
        }

    def test_bridge_empty_intersection_rejected(self):
        certificate = self._synthetic_bridge()
        verify_route_consistency_certificate_structure(certificate)
        certificate = copy.deepcopy(certificate)
        certificate["rows"][0]["F"]["boundary"] = DyadicInterval(
            Dyadic(1, 1), Dyadic(3, 2)
        ).to_json()
        with self.assertRaisesRegex(
            calibration.CalibrationError, "empty/tampered intersection"
        ):
            verify_route_consistency_certificate_structure(certificate)


if __name__ == "__main__":
    unittest.main()
