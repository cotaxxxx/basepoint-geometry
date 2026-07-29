from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .canonical import ContractReject, canonical_json_bytes, parse_canonical_json, sha256_hex
from .checker import CheckerResult, SweepChecker
from .enums import CheckerFailureReason, CheckerTerminalClass
from .runner import RunnerResult
from .schema import ConfigValidator, ValidatedConfig


@dataclass(frozen=True)
class VerificationReport:
    terminal_class: CheckerTerminalClass
    failure_reason: CheckerFailureReason | None
    config_sha256: str | None
    verified_box_ids: tuple[str, ...]


class ArtifactVerifier:
    def __init__(self, checker: SweepChecker, config_validator: ConfigValidator | None = None) -> None:
        self.checker = checker
        self.config_validator = config_validator or ConfigValidator()

    def verify(
        self,
        *,
        canonical_config_bytes: bytes,
        stored_config_sha256: str,
        runner_result: RunnerResult,
    ) -> VerificationReport:
        try:
            config_obj: Any = parse_canonical_json(canonical_config_bytes)
            validated: ValidatedConfig = self.config_validator.validate(config_obj)
            actual_sha = sha256_hex(canonical_json_bytes(validated.raw))
            if actual_sha != stored_config_sha256:
                raise ContractReject(
                    CheckerFailureReason.CONFIG_SCHEMA_VIOLATION,
                    "complete config SHA-256 mismatch",
                )
            checked: CheckerResult = self.checker.verify_runner_result(runner_result)
            if checked.terminal_class is CheckerTerminalClass.VERIFY_FAIL:
                return VerificationReport(
                    checked.terminal_class,
                    checked.failure_reason,
                    actual_sha,
                    (),
                )
            return VerificationReport(
                CheckerTerminalClass.VERIFY_PASS,
                None,
                actual_sha,
                checked.verified_box_ids,
            )
        except ContractReject as exc:
            return VerificationReport(
                CheckerTerminalClass.VERIFY_FAIL,
                exc.reason,
                None,
                (),
            )
