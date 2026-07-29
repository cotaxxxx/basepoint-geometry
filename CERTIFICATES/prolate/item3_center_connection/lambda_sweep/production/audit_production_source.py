#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
_repo_override = os.environ.get("ITEM3_SWEEP_REPO_ROOT")
REPO = Path(_repo_override).resolve() if _repo_override else HERE.parents[4]
WORKFLOW = REPO / ".github/workflows/prolate-item3-lambda-sweep.yml"
WHEEL_SHA256 = "376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76"
ARTIFACT_SHA256 = "c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381"
PILOT_SOURCE_SHA256 = "9da05b2c44119c9937c19a2184ea9722de7876442235896f1f0e0dbc076f2ecc"


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    production_files = [
        "arb_adapter.py",
        "run_item3_sweep.py",
        "verify_pilot_artifact.py",
        "materialize_config.py",
        "audit_config_draft.py",
        "audit_production_source.py",
        "test_production_source.py",
    ]
    parsed_imports = {name: sorted(imports(HERE / name)) for name in production_files}
    workflow = WORKFLOW.read_text(encoding="utf-8")
    requirements = (HERE / "requirements-python-flint.txt").read_text(encoding="ascii")
    verifier = (HERE / "verify_pilot_artifact.py").read_text(encoding="utf-8")
    materializer = (HERE / "materialize_config.py").read_text(encoding="utf-8")
    entrypoint = (HERE / "run_item3_sweep.py").read_text(encoding="utf-8")
    target_raw = (HERE / "TARGET_RANGE_POLICY.json").read_bytes()
    target = json.loads(target_raw)

    anchor = Fraction(int(target["lambda_anchor"]["p"]), int(target["lambda_anchor"]["q"]))
    pipeline = Fraction(
        int(target["pipeline_validation_target"]["p"]),
        int(target["pipeline_validation_target"]["q"]),
    )
    ac_lo = Fraction(
        int(target["a_c_certified_bracket"]["lo"]["p"]),
        int(target["a_c_certified_bracket"]["lo"]["q"]),
    )

    checks = {
        "all_production_python_parses": len(parsed_imports) == len(production_files),
        "flint_import_is_adapter_only": "flint" in parsed_imports["arb_adapter.py"] and all(
            "flint" not in parsed_imports[name] for name in production_files if name != "arb_adapter.py"
        ),
        "requirements_exact_single_hash_pin": requirements == (
            "python-flint==0.9.0 --hash=sha256:" + WHEEL_SHA256 + "\n"
        ),
        "workflow_actions_read": "actions: read" in workflow,
        "workflow_setup_python_pinned": (
            "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in workflow
            and 'python-version: "3.12"' in workflow
        ),
        "workflow_require_hashes": all(
            token in workflow for token in ("--require-hashes", "--only-binary=:all:", "--no-deps")
        ),
        "workflow_pilot_artifact_pin": all(
            token in workflow for token in ("8680673043", ARTIFACT_SHA256, "verify_pilot_artifact.py")
        ),
        "workflow_passes_pilot_artifact_to_entrypoint": all(
            token in workflow for token in ("--pilot-artifact-zip", "--pilot-artifact-dir")
        ),
        "verifier_requires_internal_manifest_rederivation": all(
            token in verifier
            for token in (
                "SHA256SUMS.txt",
                PILOT_SOURCE_SHA256,
                "manifest[PILOT_SOURCE_MEMBER]",
                "source_actual",
            )
        ),
        "materializer_requires_artifact_inputs": all(
            token in materializer
            for token in (
                '--pilot-artifact-zip',
                '--pilot-artifact-dir',
                "verify_artifact(",
                'artifact-rederived pilot source SHA-256',
            )
        ),
        "materializer_binds_production_adapter": all(
            token in materializer
            for token in (
                "production/arb_adapter.py",
                "ITEM3_SWEEP_ARB_F_OVER_R_V1",
            )
        ),
        "entrypoint_fresh_checker_present": all(
            token in entrypoint
            for token in ("FreshEvidenceEvaluator", "checker_dps", "ArtifactVerifier", "SweepChecker")
        ),
        "entrypoint_adapter_import_after_preflight": (
            "from arb_adapter import" not in entrypoint
            and "PinnedSourceLoader(REPO).load_module" in entrypoint
            and entrypoint.index("PreflightVerifier(") < entrypoint.index("PinnedSourceLoader(REPO).load_module")
        ),
        "entrypoint_no_certified_range_declaration": (
            '"certified_lambda_range_declared": False' in entrypoint
            and "CERTIFIED_LAMBDA_RANGE" not in entrypoint
        ),
        "entrypoint_record_chain_directly_replayable": (
            'line = canonical_json_bytes(chained)' in entrypoint
            and '"record_sha256"' not in entrypoint
            and 'record_chain_final_sha256' in entrypoint
        ),
        "target_policy_canonical": canonical_json_bytes(target) == target_raw,
        "target_pipeline_is_downward": pipeline < anchor and pipeline == anchor - Fraction(1, 1 << 12),
        "target_ac_is_upward": anchor < ac_lo,
        "target_contract_conflict_fail_closed": (
            target["current_contract_can_reach_a_c"] is False
            and target["upward_sweep_requirement"] == "DESIGN_CONTRACT_REVISION_AND_NEW_PHASE1_FREEZE"
        ),
    }
    failures = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
        "kernel_evaluations": 0,
        "mathematical_calculations": 0,
        "python_source_sha256": {name: sha(HERE / name) for name in production_files},
        "schema": "ITEM3_SWEEP_PRODUCTION_SOURCE_STATIC_AUDIT_V1",
        "verdict": "PASS" if not failures else "FAIL",
        "workflow_sha256": sha(WORKFLOW),
    }
    raw = canonical_json_bytes(report)
    (HERE / "PRODUCTION_SOURCE_STATIC_AUDIT.json").write_bytes(raw)
    print(raw.decode("ascii"))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
