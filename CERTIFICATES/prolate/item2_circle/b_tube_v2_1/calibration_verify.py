"""Independent record and pre-delivery verification."""
from calibration_context import *
from calibration_config import *
from calibration_numeric import *
from calibration_security import *

def _verify_records(out_dir: Path):
    config, config_raw = load_config(out_dir / "config.calibration.json")
    parsed = parse_canonical_jsonl((out_dir / "calibration_records.jsonl").read_bytes())
    previous = chain_genesis(CHAIN_DOMAIN)
    for record, raw in parsed:
        if record.get("previous_record_sha256") != previous:
            raise CalibrationError("record chain mismatch")
        assert_result_namespace(record)
        previous = sha256_hex(raw)
    summary = parse_canonical_json_bytes(
        (out_dir / "CALIBRATION_SUMMARY.json").read_bytes(), allow_display=False,
    )
    _require_exact_keys(summary, {
        "candidate_count", "chain_tip", "machine_conclusion", "recommendation",
        "record_count", "schema", "state",
    }, "summary")
    assert_result_namespace(summary)
    if summary["schema"] != "btube-calibration-summary-v1":
        raise CalibrationError("summary schema mismatch")
    if summary["machine_conclusion"] != {"real_analytic": False}:
        raise CalibrationError("machine_conclusion must be exactly present-and-false")
    if summary["state"] not in TERMINAL_STATES:
        raise CalibrationError("invalid terminal state")
    if summary["chain_tip"] != previous or summary["record_count"] != len(parsed):
        raise CalibrationError("summary chain/count mismatch")
    ends = [record for record, _ in parsed if record.get("record_type") == "candidate_end"]
    pairs = _candidate_pairs(config)
    if len(ends) != summary["candidate_count"] or len(ends) != len(pairs):
        raise CalibrationError("candidate completeness mismatch")
    passing = [record["candidate_index"] for record in ends if record.get("passed") is True]
    expected = None
    if passing:
        first = min(passing)
        width, radius = pairs[first]
        expected = {
            "candidate_index": first,
            "lambda_width": width.to_json(),
            "tube_radius": radius.to_json(),
        }
    expected_state = "CALIBRATION_COMPLETE" if expected is not None else "CALIBRATION_INCOMPLETE"
    if summary["recommendation"] != expected or summary["state"] != expected_state:
        raise CalibrationError("deterministic recommendation mismatch")
    return config, summary, config_raw

def verify_pre(out_dir: Path, source_head: str) -> int:
    assert_clean_source_tree()
    assert_workflow_security()
    config, summary, config_raw = _verify_records(out_dir)
    require_blocal_dependency(config)
    load_production_kernel()
    report = {
        "config_sha256": sha256_hex(config_raw),
        "kernel_sha256": KERNEL_SHA256,
        "record_chain_tip": summary["chain_tip"],
        "schema": "btube-calibration-checker-report-v1",
        "source_head": source_head,
        "state": summary["state"],
        "verifier": "PASS",
    }
    assert_result_namespace(report)
    (out_dir / "CHECKER_REPORT.json").write_bytes(canonical_json_bytes(report))
    return 0

__all__ = [name for name in globals() if not name.startswith("__")]
