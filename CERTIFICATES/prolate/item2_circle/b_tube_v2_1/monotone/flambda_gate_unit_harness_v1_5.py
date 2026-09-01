#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE.parent / "flambda_transport_checker_v1.py"
DEFS = HERE / "F_LAMBDA_CHECKER_GATE_UNIT_TESTS_V1_1.json"
NC07 = HERE / "flambda_nc07_cell_count_gate_v1.py"

EXPECTED = {
    "NC07":  "FAIL_LAMBDA_TILING",
    "NC10":  "FAIL_SIGN",
    "NC11":  "FAIL_UNRESOLVED",
    "NC15a": "FAIL_ANCHOR_SIGN_NEG",
    "NC15b": "FAIL_ANCHOR_SIGN_POS",
    "NC18":  "FAIL_CHECKER_PARENT_TOTAL_BUDGET",
    "NC19":  "FAIL_CHECKER_FLAMBDA_CAP_PIN",
    "NC22":  "FAIL_PRODUCER_EVIDENCE_CLASS",
    "NC28a": "FAIL_TRANSPORT_LEMMA_ID",
    "NC28b": "FAIL_TRANSPORT_HUMAN_AUDIT",
    "NC28c": "FAIL_JUDGE_VERDICT",
    "NC28d": "FAIL_SIGNATURE_RECEIPT_LINK",
}


def fail_codes(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))

    constants: dict[str, str] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            constants[node.targets[0].id] = node.value.value

    out: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"_need", "CheckerFailure", "GateFailure"}
        ):
            for arg in node.args:
                value = None
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    value = arg.value
                elif isinstance(arg, ast.Name):
                    value = constants.get(arg.id)

                if isinstance(value, str) and value.startswith("FAIL_"):
                    out.add(value)

    return out



import importlib.util
import tempfile


def load_checker():
    spec = importlib.util.spec_from_file_location("flambda_checker_raw", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def expect_checker_failure(fn, expected_code: str) -> None:
    try:
        fn()
    except Exception as exc:
        code = getattr(exc, "code", None)
        assert code == expected_code, (expected_code, code, repr(exc))
    else:
        raise AssertionError(f"expected failure {expected_code}")


checker = load_checker()

# V1.5 / NC23:
# Exercise the real check_receipt precision-contract predicate.  Dependencies
# that occur before the gate are replaced with deterministic synthetic values
# and restored immediately afterward.  The gate fires before geometry
# reconstruction, production-kernel loading, or flint import.
_nc23_originals = {
    "_assert_checker_independence": checker._assert_checker_independence,
    "_precheck": checker._precheck,
    "_load_producer_receipt": checker._load_producer_receipt,
    "load_config": checker.load_config,
    "require_blocal_dependency": checker.require_blocal_dependency,
}

try:
    checker._assert_checker_independence = lambda: {}
    checker._precheck = lambda expected_head: {}
    checker._load_producer_receipt = (
        lambda path: ({}, "0" * 64)
    )
    checker.load_config = lambda: (
        {
            "dps": 60,
            "checker_dps": 59,
        },
        None,
    )
    checker.require_blocal_dependency = lambda config: None

    expect_checker_failure(
        lambda: checker.check_receipt(
            expected_head="NC23_SYNTHETIC_HEAD",
            producer_receipt_path=Path("NC23_SYNTHETIC_RECEIPT.json"),
        ),
        "FAIL_CHECKER_DPS_CONTRACT",
    )
finally:
    for name, value in _nc23_originals.items():
        setattr(checker, name, value)

print("NC23_DIRECT_GATE=PASS")

# V1.4 / NC16:
# Exercise the exact real-checker _flambda_check budget predicate with a
# synthetic route proof.  This is a gate-unit test only; it does not replace
# the contract-level NUMERIC_TINY_CAP control.  No numerical evaluator or
# kernel is called.  All preceding proof fields are valid and only the
# reported evaluation_count exceeds the checker cell-call cap.
class NC16Model:
    LAMBDA_PLUS = 0
    NORMALIZATION_BITS = 8

    @staticmethod
    def interval_fractions(enclosure, where):
        return Fraction(-2), Fraction(-1)


class NC16Endpoint:
    @staticmethod
    def as_fraction():
        return Fraction(1, 2)


class NC16Route:
    class ContractFailure(Exception):
        pass

    class base:
        class EnclosureFailure(Exception):
            pass

    @staticmethod
    def enclose_route(*args, **kwargs):
        proof = {
            "evaluation_count": checker.CHECKER_FLAMBDA_CELL_CALL_CAP + 1,
            "complete_closed_cover": True,
            "route_id": checker.FLAMBDA_ROUTE_ID,
            "quantity": "F_lambda",
            "required_sign": "NEG",
            "monkeypatch_used": False,
            "policy": {"synthetic": "nc16"},
            "effective_evaluation_cap": checker.CHECKER_FLAMBDA_CELL_CALL_CAP,
            "normalization_bits": NC16Model.NORMALIZATION_BITS,
        }
        return {"synthetic": "strict_negative"}, proof


expect_checker_failure(
    lambda: checker._flambda_check(
        route=NC16Route,
        model=NC16Model,
        adapter=None,
        raw_kernel=None,
        acb_type=None,
        arb_type=None,
        fmpq_type=None,
        bcfg={"route_policies": {"F_LAMBDA_ROUTE": {"synthetic": "nc16"}}},
        endpoint=NC16Endpoint(),
        tiles=[(Fraction(0), Fraction(1, 16))],
        proof_expectations={},
        side="NC16_SYNTHETIC",
    ),
    "FAIL_FLAMBDA_BUDGET",
)

print("NC16_DIRECT_GATE=PASS")

# V1.3 / NC03:
# Exercise the real checker _flambda_check predicate with a synthetic route.
# No numerical evaluator or kernel is called.  All proof fields needed before
# the quantity gate are valid; quantity alone is deliberately mismatched.
class NC03Model:
    LAMBDA_PLUS = 0
    NORMALIZATION_BITS = 8

    @staticmethod
    def interval_fractions(enclosure, where):
        return Fraction(-2), Fraction(-1)


class NC03Endpoint:
    @staticmethod
    def as_fraction():
        return Fraction(1, 2)


class NC03Route:
    class ContractFailure(Exception):
        pass

    class base:
        class EnclosureFailure(Exception):
            pass

    @staticmethod
    def enclose_route(*args, **kwargs):
        proof = {
            "evaluation_count": 0,
            "complete_closed_cover": True,
            "route_id": checker.FLAMBDA_ROUTE_ID,
            "quantity": "F",
            "required_sign": "NEG",
            "monkeypatch_used": False,
            "policy": {"synthetic": "nc03"},
            "effective_evaluation_cap": checker.CHECKER_FLAMBDA_CELL_CALL_CAP,
            "normalization_bits": NC03Model.NORMALIZATION_BITS,
        }
        return {"synthetic": "strict_negative"}, proof


expect_checker_failure(
    lambda: checker._flambda_check(
        route=NC03Route,
        model=NC03Model,
        adapter=None,
        raw_kernel=None,
        acb_type=None,
        arb_type=None,
        fmpq_type=None,
        bcfg={"route_policies": {"F_LAMBDA_ROUTE": {"synthetic": "nc03"}}},
        endpoint=NC03Endpoint(),
        tiles=[(Fraction(0), Fraction(1, 16))],
        proof_expectations={},
        side="NC03_SYNTHETIC",
    ),
    "FAIL_FLAMBDA_QUANTITY",
)

print("NC03_DIRECT_GATE=PASS")

# V1.2 / NC12:
# Exercise the real checker _flambda_check predicate with a synthetic route.
# No numerical evaluator or kernel is called.  All proof fields are valid
# except normalization_bits, which is deliberately mismatched.
class NC12Model:
    LAMBDA_PLUS = 0
    NORMALIZATION_BITS = 8

    @staticmethod
    def interval_fractions(enclosure, where):
        return Fraction(-2), Fraction(-1)


class NC12Endpoint:
    @staticmethod
    def as_fraction():
        return Fraction(1, 2)


class NC12Route:
    class ContractFailure(Exception):
        pass

    class base:
        class EnclosureFailure(Exception):
            pass

    @staticmethod
    def enclose_route(*args, **kwargs):
        proof = {
            "evaluation_count": 0,
            "complete_closed_cover": True,
            "route_id": checker.FLAMBDA_ROUTE_ID,
            "quantity": "F_lambda",
            "required_sign": "NEG",
            "monkeypatch_used": False,
            "policy": {"synthetic": "nc12"},
            "effective_evaluation_cap": checker.CHECKER_FLAMBDA_CELL_CALL_CAP,
            "normalization_bits": NC12Model.NORMALIZATION_BITS + 1,
        }
        return {"synthetic": "strict_negative"}, proof


expect_checker_failure(
    lambda: checker._flambda_check(
        route=NC12Route,
        model=NC12Model,
        adapter=None,
        raw_kernel=None,
        acb_type=None,
        arb_type=None,
        fmpq_type=None,
        bcfg={"route_policies": {"F_LAMBDA_ROUTE": {"synthetic": "nc12"}}},
        endpoint=NC12Endpoint(),
        tiles=[(Fraction(0), Fraction(1, 16))],
        proof_expectations={},
        side="NC12_SYNTHETIC",
    ),
    "FAIL_FLAMBDA_NORMALIZATION_BITS",
)

print("NC12_DIRECT_GATE=PASS")

# NC22: real _load_producer_receipt predicate, synthetic canonical JSON.
with tempfile.TemporaryDirectory() as td:
    rp = Path(td) / "producer.json"
    obj = {
        "schema": checker.PRODUCER_SCHEMA,
        "evidence_class": "BINDING",
        "binding_use_authorized": False,
        "checker_required": True,
        "human_promotion_required": True,
        "producer_verdict": checker.PRODUCER_PASS,
    }
    rp.write_bytes(checker.canonical_json_bytes(obj))
    expect_checker_failure(
        lambda: checker._load_producer_receipt(rp),
        "FAIL_PRODUCER_EVIDENCE_CLASS",
    )
print("NC22_DIRECT_GATE=PASS")

# NC28a-c: real _verify_transport_gate predicates using synthetic pin file.
original_load_json = checker._load_json

class FK:
    ORDINARY_FORMULA_ID = "ordinary"
    DUFFY_FORMULA_ID = "duffy"

class Route:
    fk = FK()
    TRANSPORT_LEMMA_ID = checker.TRANSPORT_LEMMA_ID

class Policy:
    ANGULAR_POLICY_ID = "a"
    DENOMINATOR_POLICY_ID = "d"
    SQRT_POLICY_ID = "s"
    GAMMA_POLICY_ID = "g"
    Q_LO_POLICY_ID = "q"
    NORMALIZATION_POLICY_ID = "n"

Route.policy = Policy()

class Model:
    NORMALIZATION_BITS = 1

pre = {
    "actual": {
        "transport_receipt_sha256": "receipt",
        "judge_signature_sha256": "judge",
    },
    "native_manifest": {
        "ordinary_formula_id": "ordinary",
        "duffy_formula_id": "duffy",
    },
}
bcfg = {"route_policies": {"F_LAMBDA_ROUTE": {}}}

def run_transport_case(pin_overrides=None, signature_overrides=None):
    pins = {
        "receipt_sha256": "receipt",
        "judge_signature_sha256": "judge",
        "judge_verdict": "PASS",
        "transport_lemma_human_audit": checker.TRANSPORT_AUDIT_STATUS,
        "lemma_id": checker.TRANSPORT_LEMMA_ID,
        "scope": checker.TRANSPORT_SCOPE,
    }
    sig = {
        "receipt_sha256": "receipt",
        "judge_verdict": "PASS",
        "judge_scope": checker.TRANSPORT_SCOPE,
        "signer_role": "HUMAN_JUDGE",
    }
    if pin_overrides:
        pins.update(pin_overrides)
    if signature_overrides:
        sig.update(signature_overrides)

    def fake_load_json(path):
        if path == checker.TRANSPORT_PIN_FILE:
            return pins
        if path == checker.JUDGE_SIGNATURE:
            return sig
        return original_load_json(path)

    checker._load_json = fake_load_json
    try:
        return checker._verify_transport_gate(pre, Route, Model, bcfg)
    finally:
        checker._load_json = original_load_json

expect_checker_failure(
    lambda: run_transport_case({"lemma_id": "MUTATED"}),
    "FAIL_TRANSPORT_LEMMA_ID",
)
print("NC28a_DIRECT_GATE=PASS")

expect_checker_failure(
    lambda: run_transport_case({"transport_lemma_human_audit": "MUTATED"}),
    "FAIL_TRANSPORT_HUMAN_AUDIT",
)
print("NC28b_DIRECT_GATE=PASS")

expect_checker_failure(
    lambda: run_transport_case({"judge_verdict": "FAIL"}),
    "FAIL_JUDGE_VERDICT",
)
print("NC28c_DIRECT_GATE=PASS")

expect_checker_failure(
    lambda: run_transport_case(
        signature_overrides={"receipt_sha256": "MUTATED"}
    ),
    "FAIL_SIGNATURE_RECEIPT_LINK",
)
print("NC28d_DIRECT_GATE=PASS")

defs = json.loads(DEFS.read_text())
tests = defs["tests"]

ids = [t["id"] for t in tests]
assert len(ids) == 12
assert len(set(ids)) == 12
assert set(ids) == set(EXPECTED)

for t in tests:
    assert t["expected_code"] == EXPECTED[t["id"]]
    assert t["end_to_end"] is False


def function_node(path: Path, name: str) -> ast.FunctionDef:
    tree = ast.parse(path.read_text(), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function not found: {name}")


def need_predicates(fn: ast.FunctionDef) -> dict[str, str]:
    out: dict[str, str] = {}
    for node in ast.walk(fn):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_need"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and isinstance(node.args[1].value, str)
        ):
            out[node.args[1].value] = ast.unparse(node.args[0])
    return out


precheck_predicates = need_predicates(function_node(CHECKER, "_precheck"))
receipt_predicates = need_predicates(function_node(CHECKER, "check_receipt"))

assert precheck_predicates["FAIL_CHECKER_FLAMBDA_CAP_PIN"] == (
    "pins.get('checker_flambda_cell_call_cap') == CHECKER_FLAMBDA_CELL_CALL_CAP"
)
print("NC19_STRUCTURAL_PREDICATE=PASS")

assert receipt_predicates["FAIL_CHECKER_PARENT_TOTAL_BUDGET"] == (
    "total_anchor + total_flambda <= declared_parent_cap"
)
print("NC18_STRUCTURAL_PREDICATE=PASS")

checker_codes = fail_codes(CHECKER)
nc07_codes = fail_codes(NC07)

for cid, code in EXPECTED.items():
    if cid == "NC07":
        assert code in nc07_codes, (cid, code)
    elif cid in {"NC10", "NC11"}:
        # These are logical sign-decision unit gates, not literal checker
        # implementation subcodes.
        continue
    else:
        assert code in checker_codes, (cid, code)

print("GATE_DEFINITION_COUNT=12")
print("GATE_DEFINITION_IDS=PASS")
print("EXPECTED_SUBCODES=PASS")
print("IMPLEMENTATION_EMIT_SITES_EXCEPT_NC10_NC11=PASS")
print("NC10_NC11_LOGICAL_GATE_ONLY=TRUE")
print("NUMERICAL_EVALUATOR_CALLED=FALSE")
print("END_TO_END_CLAIM=FALSE")
print("GATE_HARNESS=PASS_NOT_PROMOTED")
