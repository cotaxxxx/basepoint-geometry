from __future__ import annotations
from fractions import Fraction
import io
import json
from pathlib import Path
import sys
import tokenize
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import a0_boundary_distance as producer
import a0_boundary_distance_verify as verifier

CERT_PATH = ROOT / "A0_BOUNDARY_DISTANCE_CERTIFICATE.json"


class A0BoundaryDistanceTests(unittest.TestCase):
    def _certificate(self):
        raw = CERT_PATH.read_bytes()
        self.assertFalse(raw.endswith(b"\n"))
        obj = json.loads(raw)
        self.assertEqual(producer._canonical_json_bytes(obj), raw)
        return obj

    def test_static_certificate_exact_bound(self):
        c = self._certificate()
        self.assertTrue(verifier.verify_certificate_algebra(c))
        delta = verifier.rat(c["delta_start_exact"], "delta")
        self.assertGreater(delta, Fraction(1, 8192))
        self.assertLess(delta, Fraction(1, 4096))
        self.assertEqual(
            verifier.dy(c["operational_refined_start_root_interval"]["lo"], "lo"),
            Fraction(2047, 2048),
        )
        self.assertEqual(
            verifier.dy(c["operational_refined_start_root_interval"]["hi"], "hi"),
            Fraction(8191, 8192),
        )

    def test_tampered_delta_rejected(self):
        c = self._certificate()
        c["delta_start_exact"] = {"p": "0", "q": "1"}
        with self.assertRaises(verifier.VerifyError):
            verifier.verify_certificate_algebra(c)

    def test_tampered_refined_bracket_rejected(self):
        c = self._certificate()
        c["operational_refined_start_root_interval"]["hi"] = {"e": 0, "m": "1"}
        with self.assertRaises(verifier.VerifyError):
            verifier.verify_certificate_algebra(c)

    def test_tampered_B_start_rejected(self):
        c = self._certificate()
        c["B_lambda_start_upper"] = {"p": "0", "q": "1"}
        with self.assertRaises(verifier.VerifyError):
            verifier.verify_certificate_algebra(c)

    def test_source_tree_scan_patterns_absent(self):
        patterns = (
            "flo" + "at(", "Dec" + "imal(", "." + "str(",
            "arb(" + "str", "arf(" + "str", "mag(" + "str",
        )
        for path in (ROOT / "a0_boundary_distance.py", ROOT / "a0_boundary_distance_verify.py"):
            source = path.read_text(encoding="utf-8")
            code = "".join(
                token.string
                for token in tokenize.generate_tokens(io.StringIO(source).readline)
                if token.type not in {tokenize.STRING, tokenize.COMMENT}
            )
            self.assertEqual([p for p in patterns if p in code], [])

    def test_independent_verifier_does_not_import_producer(self):
        source = (ROOT / "a0_boundary_distance_verify.py").read_text(encoding="utf-8")
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        code_tokens = [
            token.string
            for token in tokens
            if token.type not in {tokenize.STRING, tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
        ]
        joined = " ".join(code_tokens)
        self.assertNotIn("import a0_boundary_distance", joined)
        self.assertNotIn("from a0_boundary_distance", joined)


if __name__ == "__main__":
    unittest.main()
