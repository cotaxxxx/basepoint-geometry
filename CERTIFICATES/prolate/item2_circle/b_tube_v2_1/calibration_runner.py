"""Calibration runner, disabled until B-LOCAL is pinned."""
from calibration_context import *
from calibration_candidate import *
from calibration_config import *
from calibration_numeric import *
from calibration_security import *

def run_calibration(out_dir: Path) -> int:
    assert_no_stale_inputs(out_dir)
    assert_clean_source_tree()
    assert_workflow_security()
    config, config_raw = load_config()
    require_blocal_dependency(config)
    kernel, kernel_path = load_production_kernel()
    from flint import arb, ctx
    ctx.dps = config["dps"]
    out_dir.mkdir(parents=True)
    (out_dir / "config.calibration.json").write_bytes(config_raw)
    records = []
    previous = chain_genesis(CHAIN_DOMAIN)
    recommendation = None
    for candidate_index, (width, radius) in enumerate(_candidate_pairs(config)):
        passed, previous, candidate = _candidate_run(
            config=config, kernel=kernel, arb_type=arb, width=width, radius=radius,
            candidate_index=candidate_index, records=records, previous=previous,
        )
        if passed and recommendation is None:
            recommendation = candidate
    state = "CALIBRATION_COMPLETE" if recommendation is not None else "CALIBRATION_INCOMPLETE"
    summary = {
        "candidate_count": len(_candidate_pairs(config)),
        "chain_tip": previous,
        "machine_conclusion": {"real_analytic": False},
        "recommendation": recommendation,
        "record_count": len(records),
        "schema": "btube-calibration-summary-v1",
        "state": state,
    }
    assert_result_namespace(summary)
    (out_dir / "calibration_records.jsonl").write_bytes(canonical_jsonl(records))
    (out_dir / "CALIBRATION_SUMMARY.json").write_bytes(canonical_json_bytes(summary))
    source_manifest = {
        "audited_source_commit": AUDITED_SOURCE_COMMIT,
        "design_commit": DESIGN_COMMIT,
        "kernel_path": kernel_path.relative_to(REPO_ROOT).as_posix(),
        "kernel_sha256": sha256_hex(kernel_path.read_bytes()),
        "schema": "btube-calibration-source-manifest-v1",
    }
    (out_dir / "SOURCE_MANIFEST.json").write_bytes(canonical_json_bytes(source_manifest))
    return 0

__all__ = [name for name in globals() if not name.startswith("__")]
