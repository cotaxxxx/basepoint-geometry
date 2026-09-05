#!/usr/bin/env python3
"""Create the non-binding provenance attestation required by H_U V1.2."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
CONTRACT = "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2"
PRODUCER_SHA256 = "d5d54e31daa6aa45c75782b54f40db92a7075c24f567d1d9acf7b481021e22d8"
REL_PRODUCER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics/hu_domain_v1_2_production_producer.py"


def fail(code: str) -> None:
    raise SystemExit("STOP:" + code)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail("NONREGULAR_INPUT:" + str(path))
    obj = json.loads(path.read_text())
    if not isinstance(obj, dict):
        fail("TOP_LEVEL_NOT_OBJECT")
    return obj
def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def require(condition: bool, code: str) -> None:
    if not condition:
        fail(code)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--raw-result", type=Path, required=True)
    ap.add_argument("--tube-geometry", type=Path, required=True)
    ap.add_argument("--cell-id", required=True)
    ap.add_argument("--cell-index", type=int, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()
    require(not git(repo, "status", "--porcelain"), "SOURCE_TREE_DIRTY")
    raw, geom = load(ns.raw_result), load(ns.tube_geometry)
    raw_sha, geom_sha = sha(ns.raw_result), sha(ns.tube_geometry)
    require(sha(repo / REL_PRODUCER) == PRODUCER_SHA256, "PRODUCER_SOURCE_SHA")
    require(raw.get("schema") == "production-hu-domain-v1.2-production-raw-v2", "RAW_SCHEMA")
    require(raw.get("contract_id") == CONTRACT, "RAW_CONTRACT")
    require(raw.get("evidence_class") == "PRODUCTION_CANDIDATE", "RAW_EVIDENCE_CLASS")
    require(raw.get("binding_use_authorized") is False, "RAW_SELF_AUTHORIZED")
    require(raw.get("runner_sha256") == PRODUCER_SHA256, "RAW_PRODUCER_SHA")
    require(raw.get("geometry_source_sha256") == geom_sha, "RAW_GEOMETRY_SHA")
    require(raw.get("verdict") == "PRODUCTION_CANDIDATE_PASS", "RAW_VERDICT")
    require(raw.get("final_unresolved_count") == 0, "RAW_UNRESOLVED")
    require(raw.get("all_terminal_lo_positive") is True, "RAW_POSITIVITY")
    require(raw.get("cover_checks", {}).get("union_equals_parent") is True, "RAW_COVER")
    require(geom.get("schema") == "monotone-tube-v1.1-component1-geometry-receipt-v1", "GEOMETRY_SCHEMA")
    require(geom.get("binding_use_authorized") is False, "GEOMETRY_SELF_AUTHORIZED")
    require(geom.get("cell_id") == ns.cell_id, "CELL_ID")
    require(geom.get("candidate_inputs", {}).get("cell_index") == ns.cell_index, "CELL_INDEX")
    head = raw.get("execution_head")
    require(isinstance(head, str) and len(head) == 40, "PRODUCER_HEAD_FORMAT")
    require(subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", head + "^{commit}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0, "PRODUCER_HEAD_MISSING")

    attestation = {
        "schema": "production-hu-domain-v1.2-production-attestation-v1",
        "contract_id": CONTRACT,
        "evidence_class": "PRODUCTION_CANDIDATE",
        "binding_use_authorized": False,
        "raw_result_sha256": raw_sha,
        "tube_geometry_receipt_sha256": geom_sha,
        "production_producer_sha256": PRODUCER_SHA256,
        "producer_execution_head": head,
        "checker_status": "PENDING",
        "attestation_builder_sha256": sha(Path(__file__).resolve()),
    }
    require(not git(repo, "status", "--porcelain"), "SOURCE_TREE_CHANGED")
    ns.out_json.write_text(json.dumps(attestation, indent=2, sort_keys=True) + "\n")
    print("CELL_ID=" + ns.cell_id)
    print("RAW_RESULT_SHA256=" + raw_sha)
    print("TUBE_GEOMETRY_RECEIPT_SHA256=" + geom_sha)
    print("BINDING_USE_AUTHORIZED=FALSE")
    print("CHECKER_STATUS=PENDING")
    print("ATTESTATION_SHA256=" + sha(ns.out_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
