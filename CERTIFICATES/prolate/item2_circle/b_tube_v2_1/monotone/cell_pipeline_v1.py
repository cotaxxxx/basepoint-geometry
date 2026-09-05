#!/usr/bin/env python3
"""Fail-closed Cell1+ candidate pipeline; human promotions are out of scope."""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
PRODUCER_HEAD = "ccc386f6288107aab74111e4372232719a2897cd"
CHECKER_HEAD = "996bc349fdafe6d0c840c06e2c79a6a51e52b9b0"
ROOT_REL = Path("CERTIFICATES/prolate/item2_circle/b_tube_v2_1")
MON_REL = ROOT_REL / "monotone"
FLAMBDA_PRODUCER = ROOT_REL / "flambda_transport_producer_v1.py"
FLAMBDA_CHECKER = ROOT_REL / "flambda_transport_checker_v1.py"
HU_PRODUCER = ROOT_REL / "diagnostics/hu_domain_v1_2_production_producer.py"
HU_FINALIZER = MON_REL / "hu_domain_v1_2_production_finalize.py"
GEOM_FINALIZER = MON_REL / "component1_geometry_finalize_v1.py"
GEOM_VERIFIER = MON_REL / "component1_geometry_verify_v1.py"
HU_ATTESTER = MON_REL / "hu_production_attest_v1.py"


def fail(code: str) -> None:
    raise SystemExit("STOP:" + code)

def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def env() -> dict[str, str]:
    out = dict(os.environ)
    out["PYTHONDONTWRITEBYTECODE"] = "1"
    return out


def run(cmd: list[str], cwd: Path, log: Path | None = None) -> None:
    if log is None:
        subprocess.run(cmd, cwd=cwd, env=env(), check=True)
        return
    with log.open("w") as stream:
        subprocess.run(cmd, cwd=cwd, env=env(), stdout=stream, stderr=subprocess.STDOUT, check=True)


def clean_repo(repo: Path) -> str:
    if platform.python_version() != "3.13.14":
        fail("PYTHON_VERSION")
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        fail("BYTECODE_POLICY")
    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_DIRTY")
    return git(repo, "rev-parse", "HEAD")

def detached_run(repo: Path, head: str, cmd: list[str], log: Path) -> None:
    parent = Path(tempfile.mkdtemp(prefix="cell-pipeline-wt.", dir="/tmp"))
    parent.rmdir()
    try:
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(parent), head],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
        )
        run(cmd, parent, log)
    finally:
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", "--force", str(parent)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )


def names(out: Path, cell: int) -> dict[str, Path]:
    prefix = f"CELL{cell}"
    return {
        "fp": out / f"{prefix}_F_LAMBDA_PRODUCER_V1.json",
        "fc": out / f"{prefix}_F_LAMBDA_CHECKER_V1.json",
        "geom": out / f"{prefix}_COMPONENT1_TUBE_GEOMETRY_V1.json",
        "hu_raw": out / f"{prefix}_HU_PRODUCTION_RAW_V2.json",
        "hu_att": out / f"{prefix}_HU_PRODUCTION_ATTESTATION_V1.json",
        "hu_log": out / f"{prefix}_HU_PRODUCTION_CHECKER.log",
        "hu_receipt": out / f"{prefix}_HU_PRODUCTION_RECEIPT_V1.json",
    }

def flambda_stage(repo: Path, out: Path, cell: int, previous: Path) -> None:
    head = clean_repo(repo)
    if cell < 1 or not previous.is_file():
        fail("PREVIOUS_GEOMETRY")
    p = names(out, cell)
    detached_run(repo, PRODUCER_HEAD, [
        sys.executable, str(FLAMBDA_PRODUCER), "--candidate-index", "0",
        "--cell-index", str(cell), "--output", str(p["fp"]),
        "--expected-head", PRODUCER_HEAD,
    ], out / f"CELL{cell}_F_LAMBDA_PRODUCER.log")
    detached_run(repo, CHECKER_HEAD, [
        sys.executable, str(FLAMBDA_CHECKER), "--producer-receipt", str(p["fp"]),
        "--output", str(p["fc"]), "--expected-head", CHECKER_HEAD,
    ], out / f"CELL{cell}_F_LAMBDA_CHECKER.log")
    run([
        sys.executable, str(repo / GEOM_FINALIZER), "--repo", str(repo),
        "--producer", str(p["fp"]), "--checker", str(p["fc"]),
        "--previous-geometry", str(previous), "--cell-index", str(cell),
        "--out-json", str(p["geom"]), "--expected-head", head,
    ], repo, out / f"CELL{cell}_GEOMETRY_FINALIZER.log")
    run([
        sys.executable, str(repo / GEOM_VERIFIER), "--repo", str(repo),
        "--receipt", str(p["geom"]), "--producer", str(p["fp"]),
        "--checker", str(p["fc"]), "--previous-geometry", str(previous),
    ], repo, out / f"CELL{cell}_GEOMETRY_VERIFIER.log")
    if clean_repo(repo) != head:
        fail("HEAD_CHANGED")
    print("STAGE=F_LAMBDA_AND_GEOMETRY_PASS_NOT_PROMOTED")
    print("CELL=" + str(cell))
    print("F_LAMBDA_PRODUCER_SHA256=" + sha(p["fp"]))
    print("F_LAMBDA_CHECKER_SHA256=" + sha(p["fc"]))
    print("COMPONENT1_GEOMETRY_SHA256=" + sha(p["geom"]))
    print("NEXT=REVIEW_AND_COMMIT_GEOMETRY_THEN_RUN_HU")


def hu_stage(repo: Path, out: Path, cell: int, geometry: Path) -> None:
    head = clean_repo(repo)
    if cell < 1 or not geometry.is_file():
        fail("TUBE_GEOMETRY")
    p = names(out, cell)
    run([
        sys.executable, str(repo / HU_PRODUCER), "--repo", str(repo),
        "--expected-head", head, "--tube-geometry", str(geometry),
        "--box-id", f"CELL{cell}_PARENT", "--out-json", str(p["hu_raw"]),
    ], repo, out / f"CELL{cell}_HU_PRODUCER.log")
    run([
        sys.executable, str(repo / HU_ATTESTER), "--repo", str(repo),
        "--raw-result", str(p["hu_raw"]), "--tube-geometry", str(geometry),
        "--cell-id", f"CELL{cell}", "--cell-index", str(cell),
        "--out-json", str(p["hu_att"]),
    ], repo, out / f"CELL{cell}_HU_ATTESTER.log")
    run([
        sys.executable, str(repo / HU_FINALIZER), "--repo", str(repo),
        "--raw-result", str(p["hu_raw"]),
        "--production-attestation", str(p["hu_att"]),
        "--tube-geometry", str(geometry), "--checker-log", str(p["hu_log"]),
        "--cell-id", f"CELL{cell}", "--cell-index", str(cell),
        "--out-json", str(p["hu_receipt"]),
    ], repo, out / f"CELL{cell}_HU_FINALIZER.log")
    if clean_repo(repo) != head:
        fail("HEAD_CHANGED")
    print("STAGE=H_U_PASS_READY_FOR_JUDGE_PROMOTION")
    print("CELL=" + str(cell))
    print("H_U_RAW_SHA256=" + sha(p["hu_raw"]))
    print("H_U_ATTESTATION_SHA256=" + sha(p["hu_att"]))
    print("H_U_CHECKER_LOG_SHA256=" + sha(p["hu_log"]))
    print("H_U_PRODUCTION_RECEIPT_SHA256=" + sha(p["hu_receipt"]))
    print("NEXT=HUMAN_JUDGE_PROMOTION_REQUIRED")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    sub = ap.add_subparsers(dest="stage", required=True)
    fp = sub.add_parser("flambda")
    fp.add_argument("--cell-index", type=int, required=True)
    fp.add_argument("--previous-geometry", type=Path, required=True)
    hp = sub.add_parser("hu")
    hp.add_argument("--cell-index", type=int, required=True)
    hp.add_argument("--tube-geometry", type=Path, required=True)
    ns = ap.parse_args()
    repo, out = ns.repo.resolve(), ns.out_dir.resolve()
    try:
        out.relative_to(repo)
    except ValueError:
        pass
    else:
        fail("OUT_DIR_MUST_BE_OUTSIDE_REPO")
    clean_repo(repo)
    out.mkdir(parents=True, exist_ok=True)
    if ns.stage == "flambda":
        flambda_stage(repo, out, ns.cell_index, ns.previous_geometry.resolve())
    else:
        hu_stage(repo, out, ns.cell_index, ns.tube_geometry.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
