"""Canonical calibration configuration and B-LOCAL gate."""
from calibration_context import *


def _validate_unpinned_blocal(config: dict[str, Any]) -> dict[str, Any]:
    dependency = _require_exact_keys(
        config["blocal_dependency"], EXPECTED_BLOCAL_KEYS, "blocal_dependency"
    )
    if dependency["status"] != BLOCAL_UNPINNED_STATUS:
        raise CalibrationError("config: B-LOCAL diagnostic status mismatch")
    for key in (
        "artifact_zip_sha256", "certificate_sha256", "config_sha256",
        "lambda_start", "machine_conclusion", "source_head",
    ):
        if dependency[key] is not None:
            raise CalibrationError(f"config: unpinned B-LOCAL field must be null: {key}")
    if config["binding_to_final_lambda_start"] is not False:
        raise CalibrationError("config: diagnostic profile must not bind final lambda_start")
    return dependency


def _expected_pinned_blocal() -> dict[str, Any]:
    return {
        "artifact_zip_sha256": BLOCAL_ARTIFACT_SHA256,
        "certificate_sha256": BLOCAL_CERTIFICATE_SHA256,
        "config_sha256": BLOCAL_CONFIG_SHA256,
        "lambda_start": BLOCAL_LAMBDA_START.to_json(),
        "machine_conclusion": BLOCAL_MACHINE_CONCLUSION,
        "source_head": BLOCAL_SOURCE_HEAD,
        "status": BLOCAL_PINNED_STATUS,
    }


def _validate_pinned_blocal(config: dict[str, Any]) -> dict[str, Any]:
    dependency = _require_exact_keys(
        config["blocal_dependency"], EXPECTED_BLOCAL_KEYS, "blocal_dependency"
    )
    if config["binding_to_final_lambda_start"] is not True:
        raise CalibrationError("config: binding profile must bind final lambda_start")
    expected = _expected_pinned_blocal()
    if dependency != expected:
        raise CalibrationError("config: pinned B-LOCAL tuple mismatch")
    start = Rational.from_json(dependency["lambda_start"], "blocal_dependency.lambda_start")
    if start != BLOCAL_LAMBDA_START:
        raise CalibrationError("config: B-LOCAL lambda_start mismatch")
    machine = _require_exact_keys(
        dependency["machine_conclusion"],
        set(BLOCAL_MACHINE_CONCLUSION),
        "blocal_dependency.machine_conclusion",
    )
    if machine != BLOCAL_MACHINE_CONCLUSION:
        raise CalibrationError("config: B-LOCAL machine conclusion mismatch")
    if machine["lambda_start"] != dependency["lambda_start"]:
        raise CalibrationError("config: B-LOCAL machine/config lambda mismatch")
    return dependency


def load_config(path: Path = CONFIG_PATH) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    obj = parse_canonical_json_bytes(raw, allow_display=False)
    _require_exact_keys(obj, EXPECTED_CONFIG_KEYS, "config")
    if obj["schema"] != CONFIG_SCHEMA or obj["design_version"] != DESIGN_VERSION:
        raise CalibrationError("config: schema/design mismatch")
    if obj["audited_source_commit"] != AUDITED_SOURCE_COMMIT:
        raise CalibrationError("config: audited source mismatch")
    if obj["design_commit"] != DESIGN_COMMIT:
        raise CalibrationError("config: design commit mismatch")
    if obj["production_kernel_sha256"] != KERNEL_SHA256:
        raise CalibrationError("config: production kernel pin mismatch")
    if obj["record_chain_genesis_domain"] != CHAIN_DOMAIN:
        raise CalibrationError("config: chain domain mismatch")
    if obj["q_evaluation_rule"] != Q_RULE:
        raise CalibrationError("config: affine evaluation rule mismatch")

    mode = obj["mode"]
    if mode == CALIBRATION_MODE:
        dependency = _validate_unpinned_blocal(obj)
    elif mode == BINDING_MODE:
        dependency = _validate_pinned_blocal(obj)
    else:
        raise CalibrationError("config: calibration mode mismatch")

    diagnostic_start = Rational.from_json(
        obj["diagnostic_lambda_start"], "diagnostic_lambda_start"
    )
    if diagnostic_start != Rational(21, 10):
        raise CalibrationError("config: diagnostic endpoint mismatch")
    end = Rational.from_json(obj["lambda_end"], "lambda_end")
    if end != CG_LAMBDA:
        raise CalibrationError("config: terminal endpoint mismatch")
    if mode == CALIBRATION_MODE:
        if not BLOCAL_STAGE1_UPPER < diagnostic_start < end:
            raise CalibrationError("config: diagnostic/terminal endpoint ordering mismatch")
    else:
        start = Rational.from_json(
            dependency["lambda_start"], "blocal_dependency.lambda_start"
        )
        if not BLOCAL_STAGE1_UPPER < start < end:
            raise CalibrationError("config: B-LOCAL/terminal endpoint ordering mismatch")

    dps = _positive_int(obj["dps"], "dps")
    checker_dps = _positive_int(obj["checker_dps"], "checker_dps")
    if checker_dps < dps:
        raise CalibrationError("config: checker_dps < dps")
    for key in ("predictor_refresh", "max_cells", "max_subdivisions", "evaluation_budget"):
        _positive_int(obj[key], key)
    _dyadic_list(obj["candidate_lambda_widths"], "candidate_lambda_widths")
    _dyadic_list(obj["candidate_tube_radii"], "candidate_tube_radii")

    cg = _require_exact_keys(obj["cg_match_dependency"], EXPECTED_CG_KEYS, "cg_match_dependency")
    if cg["artifact_zip_sha256"] != CG_ARTIFACT_SHA256:
        raise CalibrationError("config: C-G artifact mismatch")
    if cg["source_head"] != CG_SOURCE_HEAD:
        raise CalibrationError("config: C-G source mismatch")
    if cg["config_sha256"] != CG_CONFIG_SHA256:
        raise CalibrationError("config: C-G config mismatch")
    if cg["b_kernel_sha256"] != KERNEL_SHA256 or cg["cg_kernel_sha256"] != KERNEL_SHA256:
        raise CalibrationError("config: C-G/reference kernel mismatch")
    if cg["paper_lemma_id"] != CG_LEMMA:
        raise CalibrationError("config: C-G lemma mismatch")
    if Rational.from_json(cg["lambda"], "cg.lambda") != CG_LAMBDA:
        raise CalibrationError("config: C-G lambda mismatch")
    root = _require_exact_keys(cg["root_interval"], {"lo", "hi"}, "cg.root_interval")
    if (Rational.from_json(root["lo"]) != CG_ROOT[0]
            or Rational.from_json(root["hi"]) != CG_ROOT[1]):
        raise CalibrationError("config: C-G root interval mismatch")
    return obj, raw


def require_blocal_dependency(config: dict[str, Any]) -> None:
    if (config.get("mode") != BINDING_MODE
            or config.get("binding_to_final_lambda_start") is not True):
        raise CalibrationError(
            "B-LOCAL/B-ENTRY dependency is not pinned; binding calibration is disabled"
        )
    _validate_pinned_blocal(config)


def require_diagnostic_mode(config: dict[str, Any]) -> Rational:
    if config.get("mode") != CALIBRATION_MODE:
        raise CalibrationError("diagnostic mode is not enabled")
    _validate_unpinned_blocal(config)
    start = Rational.from_json(config["diagnostic_lambda_start"], "diagnostic_lambda_start")
    if not BLOCAL_STAGE1_UPPER < start:
        raise CalibrationError("diagnostic start is not safely above the Stage-1 upper bracket")
    return start


__all__ = [name for name in globals() if not name.startswith("__")]
