"""Final receipt verification and lifecycle guards."""
from calibration_context import *
from calibration_config import *
from calibration_security import *
from routed_record_verifier import (
    verify_route_consistency_certificate_structure,
    verify_routed_manifest_object,
    verify_routed_trace_bytes,
)


def verify_final(archive_path: Path, receipt_path: Path, source_head: str) -> int:
    receipt = parse_canonical_json_bytes(receipt_path.read_bytes(), allow_display=False)
    _require_exact_keys(receipt, {
        "archive_name", "archive_sha256", "configuration_sha256",
        "kernel_file_sha256", "payload_manifest_sha256", "schema", "source_head",
        "state", "workflow_source_sha256",
    }, "receipt")
    assert_result_namespace(receipt)
    if receipt["schema"] != "btube-calibration-delivery-receipt-v1":
        raise CalibrationError("receipt schema mismatch")
    if receipt["source_head"] != source_head:
        raise CalibrationError("receipt source-head mismatch")
    if receipt["kernel_file_sha256"] != KERNEL_SHA256:
        raise CalibrationError("receipt kernel mismatch")
    if receipt["state"] not in {"CALIBRATION_COMPLETE", "CALIBRATION_INCOMPLETE"}:
        raise CalibrationError("receipt terminal state invalid")
    if (
        receipt["archive_name"] != archive_path.name
        or sha256_hex(archive_path.read_bytes()) != receipt["archive_sha256"]
    ):
        raise CalibrationError("archive byte mismatch")
    if sha256_hex(WORKFLOW_PATH.read_bytes()) != receipt["workflow_source_sha256"]:
        raise CalibrationError("workflow source mismatch")

    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if names != sorted(names) or len(names) != len(set(names)):
            raise CalibrationError("archive paths not unique/sorted")
        manifest_raw = archive.read("PAYLOAD_SHA256SUMS.json")
        if sha256_hex(manifest_raw) != receipt["payload_manifest_sha256"]:
            raise CalibrationError("payload manifest digest mismatch")
        manifest = parse_canonical_json_bytes(manifest_raw, allow_display=False)
        _require_exact_keys(manifest, {"files", "schema"}, "payload manifest")
        if manifest["schema"] != "btube-calibration-payload-manifest-v1":
            raise CalibrationError("payload manifest schema mismatch")
        expected_names = sorted(set(manifest["files"]) | {"PAYLOAD_SHA256SUMS.json"})
        if names != expected_names:
            raise CalibrationError("archive payload file set mismatch")
        for relative, digest in manifest["files"].items():
            if sha256_hex(archive.read(relative)) != digest:
                raise CalibrationError(f"archive payload digest mismatch: {relative}")

        config_raw = archive.read("config.calibration.json")
        if sha256_hex(config_raw) != receipt["configuration_sha256"]:
            raise CalibrationError("configuration digest mismatch")
        config = parse_canonical_json_bytes(config_raw, allow_display=False)
        require_blocal_dependency(config)

        bridge_raw = archive.read("ROUTE_CONSISTENCY_CERTIFICATE.json")
        bridge_pin = config.get("route_consistency_certificate_sha256")
        if bridge_pin is None or sha256_hex(bridge_raw) != bridge_pin:
            raise CalibrationError("archive route consistency certificate pin mismatch")
        bridge = parse_canonical_json_bytes(bridge_raw, allow_display=False)
        verify_route_consistency_certificate_structure(
            bridge, expected_source_head=config["audited_source_commit"]
        )
        if bridge["producer_settings"]["dps"] != config["checker_dps"]:
            raise CalibrationError("archive route consistency checker precision mismatch")

        trace = verify_routed_trace_bytes(archive.read(ROUTED_TRACE_NAME), config)
        routed_manifest = parse_canonical_json_bytes(
            archive.read(ROUTED_MANIFEST_NAME), allow_display=False
        )
        verify_routed_manifest_object(routed_manifest, trace, config)

        checker = parse_canonical_json_bytes(
            archive.read("CHECKER_REPORT.json"), allow_display=False
        )
        if (
            checker.get("verifier") != "PASS"
            or checker.get("routed_evaluator_verifier") != "PASS"
            or checker.get("routed_boundary_evaluation_count")
            != trace["boundary_route_evaluation_count"]
            or checker.get("source_head") != source_head
        ):
            raise CalibrationError("archive checker/routed trace mismatch")

        load_production_kernel()
        summary = parse_canonical_json_bytes(
            archive.read("CALIBRATION_SUMMARY.json"), allow_display=False
        )
        if summary.get("state") != receipt["state"]:
            raise CalibrationError("receipt/summary state mismatch")
        assert_result_namespace(summary)
    return 0


def assert_no_workflow_in_result_merge(changed_paths: Iterable[str]) -> None:
    workflow = ".github/workflows/prolate-item2-btube-v2-1-calibration.yml"
    if workflow in set(changed_paths):
        raise CalibrationError("temporary calibration workflow survives result merge")


def verify_config_only() -> int:
    config, _ = load_config()
    assert_clean_source_tree()
    assert_workflow_security()
    load_production_kernel()
    if config["mode"] == BINDING_MODE:
        from routed_record_verifier import require_route_consistency_certificate
        require_route_consistency_certificate(config)
    return 0


__all__ = [name for name in globals() if not name.startswith("__")]
