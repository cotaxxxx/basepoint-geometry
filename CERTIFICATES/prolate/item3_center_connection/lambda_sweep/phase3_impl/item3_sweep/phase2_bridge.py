from __future__ import annotations

import base64
import importlib.util
import sys
from pathlib import Path
from typing import Any

from .canonical import (
    CanonicalRational,
    ContractReject,
    canonical_json_bytes,
    parse_canonical_json,
    parse_canonical_jsonl,
    sha256_hex,
)
from .control_registry import CONTROL_BINDINGS, validate_control_bindings
from .enums import AttemptStage, CheckerFailureReason, WindowOrigin
from .schema import ConfigValidator
from .transitions import may_regenerate


PHASE2_TO_CHECKER = {
    "NONCANONICAL_ENCODING": CheckerFailureReason.NONCANONICAL_ARTIFACT,
    "SCHEMA_VIOLATION": CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
    "LOGICAL_DEPENDENCY_GATE_VIOLATION": CheckerFailureReason.LOGICAL_DEPENDENCY_VIOLATION,
    "FAILURE_TRANSITION_VIOLATION": CheckerFailureReason.FAILURE_TRANSITION_VIOLATION,
    "RECORD_GRAMMAR_VIOLATION": CheckerFailureReason.RECORD_GRAMMAR_VIOLATION,
    "CONTROL_SHAPE_VIOLATION": CheckerFailureReason.CONTROL_MAPPING_VIOLATION,
}


class BridgeReject(ValueError):
    def __init__(self, phase2_reason: str):
        super().__init__(phase2_reason)
        self.phase2_reason = phase2_reason


def _load_phase2_module(phase2_dir: Path):
    script = phase2_dir / "phase2_selftest.py"
    spec = importlib.util.spec_from_file_location("item3_phase2_selftest", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load phase2 self-test module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _translate_contract_reject(exc: ContractReject) -> str:
    for phase2_reason, checker_reason in PHASE2_TO_CHECKER.items():
        if exc.reason is checker_reason:
            return phase2_reason
    return "CONTROL_SHAPE_VIOLATION"


def _validate_grammar_payload(payload: dict[str, Any], grammar: dict[str, Any]) -> None:
    path_name = payload["path_name"]
    if path_name not in grammar["paths"] or payload["sequence"] != grammar["paths"][path_name]:
        raise BridgeReject("RECORD_GRAMMAR_VIOLATION")
    if path_name == "RUN_FATAL" and payload["manifest_emitted"]:
        raise BridgeReject("RECORD_GRAMMAR_VIOLATION")
    if path_name in {"NORMAL_COMPLETE", "TARGET_COMPLETE"} and not payload["stack_empty"]:
        raise BridgeReject("RECORD_GRAMMAR_VIOLATION")


def execute_fixture(
    fixture: dict[str, Any],
    *,
    grammar: dict[str, Any],
) -> tuple[str, str | None]:
    validator = fixture["validator"]
    payload = fixture["payload"]
    try:
        if validator == "PREDICATE":
            if payload["actual"] != payload["expected"]:
                raise BridgeReject(payload["failure_reason"])
        elif validator == "CONFIG":
            ConfigValidator(
                symlink_escape_prefixes=payload["symlink_escape_prefixes"]
            ).validate(payload["config"])
        elif validator == "CONFIG_HASH":
            validated = ConfigValidator(
                symlink_escape_prefixes=payload["symlink_escape_prefixes"]
            ).validate(payload["config"])
            if payload["stored_sha256"] != sha256_hex(canonical_json_bytes(validated.raw)):
                raise BridgeReject("SCHEMA_VIOLATION")
        elif validator == "TRANSITION_CASE":
            claimed = payload["claimed_regeneration"]
            try:
                reason_enum = __import__(
                    "item3_sweep.enums", fromlist=["RunnerFailureReason"]
                ).RunnerFailureReason(payload["reason"])
                stage_enum = AttemptStage(payload["stage"])
                origin_enum = WindowOrigin(payload["origin"])
            except ValueError as exc:
                raise BridgeReject("FAILURE_TRANSITION_VIOLATION") from exc
            allowed = may_regenerate(
                reason=reason_enum,
                attempt_stage=stage_enum,
                window_origin=origin_enum,
                per_box_remaining=payload["remaining"],
                regenerated_count=payload["regenerated_count"],
            )
            if claimed and not allowed:
                raise BridgeReject("RECORD_GRAMMAR_VIOLATION")
        elif validator == "GRAMMAR":
            _validate_grammar_payload(payload, grammar)
        elif validator == "CANONICAL_JSON":
            parse_canonical_json(base64.b64decode(payload["raw_base64"]))
        elif validator == "CANONICAL_JSONL":
            parse_canonical_jsonl(base64.b64decode(payload["raw_base64"]))
        elif validator == "RATIONAL":
            CanonicalRational.from_object(
                parse_canonical_json(base64.b64decode(payload["raw_base64"])),
                "rational",
            )
        else:
            raise BridgeReject("CONTROL_SHAPE_VIOLATION")
    except BridgeReject as exc:
        return "VERIFY_FAIL", exc.phase2_reason
    except ContractReject as exc:
        return "VERIFY_FAIL", _translate_contract_reject(exc)
    return "VERIFY_PASS", None


def run_phase2_fixture_bridge(phase2_dir: Path) -> dict[str, Any]:
    phase2 = _load_phase2_module(phase2_dir)
    packs, _ = phase2.unpack_all()
    expect = packs["CONTROL_EXPECT.json"]
    fixtures = packs["CONTROL_FIXTURES.json"]
    grammar = packs["RECORD_GRAMMAR.json"]
    validate_control_bindings(set(expect))

    failures: list[dict[str, Any]] = []
    for control_id in sorted(expect):
        observed_result, observed_reason = execute_fixture(
            fixtures[control_id], grammar=grammar
        )
        expected = expect[control_id]
        positive = control_id.startswith("POS_")
        ok = observed_result == expected["expected_checker_result"] and (
            positive or observed_reason == expected["expected_failure_reason"]
        )
        if control_id == "POS_RUN_FATAL":
            ok = (
                observed_result == "VERIFY_PASS"
                and expected["expected_checker_result"] == "NOT_APPLICABLE"
            )
        if not ok:
            failures.append(
                {
                    "control_id": control_id,
                    "expected": expected,
                    "observed_checker_result": observed_result,
                    "observed_failure_reason": observed_reason,
                }
            )

    return {
        "schema": "ITEM3_SWEEP_PHASE3_PHASE2_FIXTURE_BRIDGE_V1",
        "control_count": len(expect),
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
