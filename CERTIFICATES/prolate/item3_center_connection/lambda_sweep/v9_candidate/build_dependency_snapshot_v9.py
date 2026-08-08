#!/usr/bin/env python3
"""Deterministic dependency-entry/snapshot builder for Item 3 sweep v9.

The builder reads exact repository bytes and writes canonical JSON entries.  It does not
approve the mathematical content and must be rerun after any referenced proof/design/source
byte change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ENTRY_SCHEMA = "ITEM3_SWEEP_V9_DEPENDENCY_ENTRY_V1"
SNAPSHOT_SCHEMA = "ITEM3_SWEEP_V9_DEPENDENCY_SNAPSHOT_V2"
ALLOWLIST_ID = "ITEM3_SWEEP_V9_MACHINE_LEMMAS_V2"

BASE = "CERTIFICATES/prolate/item3_center_connection/lambda_sweep/"
DESIGN_PATH = BASE + "v9_draft/design_contract_v9_integrated_candidate_v2.md"
LEMMA_PATH = BASE + "v9_draft/MACHINE_LEMMAS_V9.md"
ANALYTIC_PATH = BASE + "v9_draft/ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md"
FORMULA_MAP_PATH = BASE + "v9_draft/SOURCE_FORMULA_MAP_CANDIDATE_V2.md"

SOURCE_PATHS = {
    "kernel": BASE + "v9_candidate/prolate_F_derivatives_cleanroom_v9_candidate.py",
    "adapter": BASE + "v9_candidate/adapter_v9_candidate_v2.py",
    "runner": BASE + "v9_candidate/runner_v9_candidate_v2.py",
    "checker": BASE + "v9_candidate/checker_v9_candidate_v2.py",
    "checkpoint": BASE + "v9_candidate/checkpoint_v9_candidate.py",
    "bridge": BASE + "v9_candidate/checkpoint_bridge_v9_candidate_v2.py",
    "driver": BASE + "v9_candidate/rehearsal_driver_v9_candidate_v3.py",
    "aggregate_verifier": BASE + "v9_candidate/aggregate_verifier_v9_candidate_v2.py",
}

STATEMENTS = {
    "L-CONT": "G=F/r is continuous on every compact machine rectangle contained in 0<r<1, lambda>=1.",
    "L-DERIV": "On the machine domain, G_r = F_r/r - F/r^2, with F_r obtained by justified differentiation under the fixed-domain integral.",
    "L-ENCL": "Validated kernel/adapter enclosures and the frozen dual-association rule contain the exact analytic target; strict signs of the final canonical interval imply the same strict sign for the target.",
    "L-IVT": "Continuous G with positive lower-window endpoint, negative upper-window endpoint, and G_r<0 throughout the window has exactly one zero in the window.",
    "L-SIGN": "A rigorous real enclosure with positive lower endpoint or negative upper endpoint implies the corresponding strict sign of every represented exact value; touching zero or nonfinite gives no strict sign.",
    "L-SECOND-DERIV": "The exact F_rr fixed-domain integral and G_rr = F_rr/r - 2 F_r/r^2 + 2 F/r^3 are valid and continuous on compact machine rectangles.",
    "L-MIXED-DERIV": "The exact F_lambda and F_rlambda fixed-domain integrals and G_rlambda = F_rlambda/r - F_lambda/r^2 are valid on compact machine rectangles, with the required mixed differentiation order justified.",
    "L-MEAN-VALUE-ENCL": "For H=G_r, the canonical-center two-variable mean-value enclosure using whole-rectangle G_rr and G_rlambda ranges contains H on the full rectangle; strict negative upper endpoint certifies G_r<0 there.",
}

PROOF_SOURCES = {
    "L-CONT": [LEMMA_PATH, ANALYTIC_PATH],
    "L-DERIV": [LEMMA_PATH, ANALYTIC_PATH, FORMULA_MAP_PATH],
    "L-ENCL": [LEMMA_PATH, DESIGN_PATH],
    "L-IVT": [LEMMA_PATH, DESIGN_PATH],
    "L-SIGN": [LEMMA_PATH, DESIGN_PATH],
    "L-SECOND-DERIV": [LEMMA_PATH, ANALYTIC_PATH, FORMULA_MAP_PATH],
    "L-MIXED-DERIV": [LEMMA_PATH, ANALYTIC_PATH, FORMULA_MAP_PATH],
    "L-MEAN-VALUE-ENCL": [LEMMA_PATH, ANALYTIC_PATH, DESIGN_PATH],
}

MACHINE_SOURCE_KEYS = {
    "L-CONT": ["kernel", "adapter"],
    "L-DERIV": ["kernel", "adapter"],
    "L-ENCL": ["kernel", "adapter"],
    "L-IVT": ["runner", "checker"],
    "L-SIGN": ["adapter", "runner", "checker"],
    "L-SECOND-DERIV": ["kernel", "adapter", "runner", "checker"],
    "L-MIXED-DERIV": ["kernel", "adapter", "runner", "checker"],
    "L-MEAN-VALUE-ENCL": ["adapter", "runner", "checker"],
}

ASSUMPTIONS = {
    "L-CONT": ["0<r<1", "lambda>=1", "fixed integration domain"],
    "L-DERIV": ["0<r<1", "lambda>=1", "L-CONT"],
    "L-ENCL": ["pinned validated interval-library semantics", "source identity gates pass"],
    "L-IVT": ["L-CONT", "L-DERIV", "L-SIGN"],
    "L-SIGN": ["L-ENCL"],
    "L-SECOND-DERIV": ["compact machine rectangle", "analytic domain/interchange proof"],
    "L-MIXED-DERIV": ["compact machine rectangle", "analytic domain/interchange proof"],
    "L-MEAN-VALUE-ENCL": ["L-SECOND-DERIV", "L-MIXED-DERIV", "L-ENCL", "canonical centers"],
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def require_file(root: Path, relative: str) -> Path:
    root = root.resolve(strict=True)
    path = (root / relative).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"path escapes repository root: {relative}") from exc
    if not path.is_file():
        raise RuntimeError(f"required file missing: {relative}")
    return path


def source_record(root: Path, relative: str) -> dict[str, str]:
    path = require_file(root, relative)
    return {"path": relative, "sha256": sha256_file(path)}


def build(repo_root: Path, output_dir: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve(strict=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    common_records = {
        "design": source_record(repo_root, DESIGN_PATH),
        "lemmas": source_record(repo_root, LEMMA_PATH),
        "analytic": source_record(repo_root, ANALYTIC_PATH),
        "formula_map": source_record(repo_root, FORMULA_MAP_PATH),
    }
    machine_sources = {
        key: source_record(repo_root, path) for key, path in SOURCE_PATHS.items()
    }

    entry_index: dict[str, dict[str, str]] = {}
    for lemma_id in STATEMENTS:
        proof_records = [source_record(repo_root, p) for p in PROOF_SOURCES[lemma_id]]
        machine_records = [machine_sources[key] for key in MACHINE_SOURCE_KEYS[lemma_id]]
        entry = {
            "allowlist_id": ALLOWLIST_ID,
            "assumptions": ASSUMPTIONS[lemma_id],
            "lemma_id": lemma_id,
            "machine_sources": machine_records,
            "nonclaims": [
                "This dependency entry does not authorize a workflow run or a certified lambda range."
            ],
            "proof_sources": proof_records,
            "schema": ENTRY_SCHEMA,
            "statement": STATEMENTS[lemma_id],
            "supports_machine_conclusion": True,
        }
        data = canonical_bytes(entry)
        filename = f"{lemma_id}.json"
        path = output_dir / filename
        path.write_bytes(data)
        entry_index[lemma_id] = {
            "path": filename,
            "sha256": hashlib.sha256(data).hexdigest(),
        }

    snapshot = {
        "allowlist_id": ALLOWLIST_ID,
        "analytic_source": common_records["analytic"],
        "design": common_records["design"],
        "entries": entry_index,
        "formula_map": common_records["formula_map"],
        "lemma_source": common_records["lemmas"],
        "machine_source_sha256": {
            key: value["sha256"] for key, value in machine_sources.items()
        },
        "nonclaim": (
            "Snapshot identity is a candidate until the referenced final bytes pass the "
            "external v9 freeze gate. Any referenced byte change requires regeneration."
        ),
        "schema": SNAPSHOT_SCHEMA,
    }
    snapshot_data = canonical_bytes(snapshot)
    snapshot_path = output_dir / "dependency_snapshot_v9_candidate.json"
    snapshot_path.write_bytes(snapshot_data)
    snapshot_sha = hashlib.sha256(snapshot_data).hexdigest()
    (output_dir / "dependency_snapshot_v9_candidate.json.sha256").write_text(
        snapshot_sha + "\n", encoding="ascii"
    )

    manifest = {
        "entry_count": len(entry_index),
        "entry_sha256": {key: value["sha256"] for key, value in entry_index.items()},
        "schema": "ITEM3_SWEEP_V9_DEPENDENCY_BUILD_REPORT_V1",
        "snapshot_sha256": snapshot_sha,
        "source_sha256": snapshot["machine_source_sha256"],
        "status": "BUILT_CANDIDATE",
    }
    (output_dir / "dependency_build_report.json").write_bytes(canonical_bytes(manifest))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.repo_root, args.output_dir)
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
