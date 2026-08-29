#!/usr/bin/env python3
"""Self-contained canonical NC01..NC20 runner.

Rebuilds the historical cell-0 F_lambda producer and checker receipts at the
frozen execution HEAD, verifies their exact historical SHA-256 values, then
invokes the canonical NC harness with explicit receipt paths. No filesystem-wide
receipt discovery is used.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
BT_REL = Path("CERTIFICATES/prolate/item2_circle/b_tube_v2_1")
PRODUCER_REL = BT_REL / "flambda_transport_producer_v1.py"
CHECKER_REL = BT_REL / "flambda_transport_checker_v1.py"
HARNESS_REL = BT_REL / "monotone/flambda_checker_canonical_nc_harness_v1.py"
CHECKER_HEAD = "996bc349fdafe6d0c840c06e2c79a6a51e52b9b0"
EXPECTED_PRODUCER_SHA256 = "34f1a08a334e4c62fc3071427f7d91e863341cfb4c784405d0be26ed4d927d8e"
EXPECTED_CHECKER_SHA256 = "3e1e1894604e9b99f7413cbb6d3bbdb7c7b0ecb6babe1966ae955986bebe59a9"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd), env=env)


def main() -> int:
    repo = Path.cwd().resolve()
    if git(repo, "status", "--porcelain"):
        raise SystemExit("STOP: SOURCE_TREE_PRE dirty")
    head_pre = git(repo, "rev-parse", "HEAD")

    print("PHASE=REBUILD_HISTORICAL_RECEIPTS", flush=True)
    print("FROZEN_EXECUTION_HEAD=" + CHECKER_HEAD, flush=True)

    with tempfile.TemporaryDirectory(prefix="flambda-canonical-selfcontained-") as td:
        td_path = Path(td)
        wt = td_path / "frozen"
        producer = td_path / "producer.json"
        checker = td_path / "checker.json"
        output = Path("/tmp/flambda_canonical_nc_v1.json")

        run(["git", "worktree", "add", "--detach", str(wt), CHECKER_HEAD], cwd=repo)
        try:
            if git(wt, "status", "--porcelain"):
                raise SystemExit("STOP: FROZEN_WORKTREE dirty")

            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["EXPECTED_HEAD"] = CHECKER_HEAD

            print("PHASE=PRODUCER_REPLAY", flush=True)
            run([
                sys.executable,
                str(wt / PRODUCER_REL),
                "--candidate-index", "0",
                "--cell-index", "0",
                "--output", str(producer),
            ], cwd=wt, env=env)
            producer_sha = sha(producer)
            print("PRODUCER_RECEIPT_SHA256=" + producer_sha, flush=True)
            if producer_sha != EXPECTED_PRODUCER_SHA256:
                raise SystemExit(
                    "STOP: producer replay SHA mismatch; expected "
                    + EXPECTED_PRODUCER_SHA256
                )

            print("PHASE=CHECKER_REPLAY", flush=True)
            run([
                sys.executable,
                str(wt / CHECKER_REL),
                "--producer-receipt", str(producer),
                "--output", str(checker),
                "--expected-head", CHECKER_HEAD,
            ], cwd=wt, env=env)
            checker_sha = sha(checker)
            print("CHECKER_RECEIPT_SHA256=" + checker_sha, flush=True)
            if checker_sha != EXPECTED_CHECKER_SHA256:
                raise SystemExit(
                    "STOP: checker replay SHA mismatch; expected "
                    + EXPECTED_CHECKER_SHA256
                )

            print("PHASE=CANONICAL_NC01_NC20", flush=True)
            run([
                sys.executable,
                str(repo / HARNESS_REL),
                "--repo", str(repo),
                "--producer-receipt", str(producer),
                "--checker-receipt", str(checker),
                "--output", str(output),
            ], cwd=repo, env=env)
        finally:
            subprocess.call(
                ["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    if git(repo, "rev-parse", "HEAD") != head_pre:
        raise SystemExit("STOP: HEAD changed during run")
    if git(repo, "status", "--porcelain"):
        raise SystemExit("STOP: SOURCE_TREE_POST dirty")

    print("SELF_CONTAINED_RUN=PASS", flush=True)
    print("OUTPUT=/tmp/flambda_canonical_nc_v1.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
