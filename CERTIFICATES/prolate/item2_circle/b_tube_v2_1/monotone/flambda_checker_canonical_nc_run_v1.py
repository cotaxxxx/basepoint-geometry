#!/usr/bin/env python3
"""Self-contained canonical NC01..NC20 runner.

Rebuild the historical producer receipt at the producer replay HEAD and the
historical checker receipt at the checker replay HEAD, verify both exact SHA-256
values, then invoke the canonical NC harness. The producer and checker have
different historical execution HEADs by design.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

BT_REL = Path("CERTIFICATES/prolate/item2_circle/b_tube_v2_1")
PRODUCER_REL = BT_REL / "flambda_transport_producer_v1.py"
CHECKER_REL = BT_REL / "flambda_transport_checker_v1.py"
HARNESS_REL = BT_REL / "monotone/flambda_checker_canonical_nc_harness_v1.py"

PRODUCER_HEAD = "ccc386f6288107aab74111e4372232719a2897cd"
CHECKER_HEAD = "996bc349fdafe6d0c840c06e2c79a6a51e52b9b0"
EXPECTED_PRODUCER_SHA256 = "34f1a08a334e4c62fc3071427f7d91e863341cfb4c784405d0be26ed4d927d8e"
HISTORICAL_CHECKER_SHA256 = "3e1e1894604e9b99f7413cbb6d3bbdb7c7b0ecb6babe1966ae955986bebe59a9"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd), env=env)


def remove_worktree(repo: Path, wt: Path) -> None:
    subprocess.call(
        ["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    repo = Path.cwd().resolve()
    if git(repo, "status", "--porcelain"):
        raise SystemExit("STOP: SOURCE_TREE_PRE dirty")
    head_pre = git(repo, "rev-parse", "HEAD")

    print("PHASE=REBUILD_HISTORICAL_RECEIPTS", flush=True)
    print("PRODUCER_REPLAY_HEAD=" + PRODUCER_HEAD, flush=True)
    print("CHECKER_REPLAY_HEAD=" + CHECKER_HEAD, flush=True)

    with tempfile.TemporaryDirectory(prefix="flambda-canonical-selfcontained-") as td:
        td_path = Path(td)
        producer_wt = td_path / "producer-frozen"
        checker_wt = td_path / "checker-frozen"
        producer = td_path / "producer.json"
        checker = td_path / "checker.json"
        output = Path("/tmp/flambda_canonical_nc_v1.json")

        print("PHASE=PRODUCER_REPLAY", flush=True)
        run(["git", "worktree", "add", "--detach", str(producer_wt), PRODUCER_HEAD], cwd=repo)
        try:
            if git(producer_wt, "status", "--porcelain"):
                raise SystemExit("STOP: PRODUCER_FROZEN_WORKTREE dirty")
            env_prod = os.environ.copy()
            env_prod["PYTHONDONTWRITEBYTECODE"] = "1"
            env_prod["EXPECTED_HEAD"] = PRODUCER_HEAD
            run([
                sys.executable,
                str(producer_wt / PRODUCER_REL),
                "--candidate-index", "0",
                "--cell-index", "0",
                "--output", str(producer),
            ], cwd=producer_wt, env=env_prod)
        finally:
            remove_worktree(repo, producer_wt)

        producer_sha = sha(producer)
        print("PRODUCER_RECEIPT_SHA256=" + producer_sha, flush=True)
        if producer_sha != EXPECTED_PRODUCER_SHA256:
            raise SystemExit(
                "STOP: producer replay SHA mismatch; expected "
                + EXPECTED_PRODUCER_SHA256
            )

        print("PHASE=CHECKER_REPLAY", flush=True)
        run(["git", "worktree", "add", "--detach", str(checker_wt), CHECKER_HEAD], cwd=repo)
        try:
            if git(checker_wt, "status", "--porcelain"):
                raise SystemExit("STOP: CHECKER_FROZEN_WORKTREE dirty")
            env_check = os.environ.copy()
            env_check["PYTHONDONTWRITEBYTECODE"] = "1"
            env_check["EXPECTED_HEAD"] = CHECKER_HEAD
            run([
                sys.executable,
                str(checker_wt / CHECKER_REL),
                "--producer-receipt", str(producer),
                "--output", str(checker),
                "--expected-head", CHECKER_HEAD,
            ], cwd=checker_wt, env=env_check)
        finally:
            remove_worktree(repo, checker_wt)

        checker_sha = sha(checker)
        print("CHECKER_RECEIPT_SHA256=" + checker_sha, flush=True)
        print("HISTORICAL_CHECKER_RECEIPT_SHA256=" + HISTORICAL_CHECKER_SHA256, flush=True)

        import json
        checker_obj = json.loads(checker.read_text(encoding="utf-8"))
        if checker_obj.get("checker_verdict") != "PASS_BINDING_CANDIDATE_CHECK":
            raise SystemExit("STOP: checker replay semantic verdict mismatch")
        if checker_obj.get("status") != "INDEPENDENT_CHECK_PASS_NOT_PROMOTED":
            raise SystemExit("STOP: checker replay semantic status mismatch")
        if checker_obj.get("execution_head") != CHECKER_HEAD:
            raise SystemExit("STOP: checker replay execution HEAD mismatch")
        if checker_obj.get("binding_use_authorized") is not False:
            raise SystemExit("STOP: checker replay binding state mismatch")
        if checker_obj.get("producer_receipt", {}).get("sha256") != EXPECTED_PRODUCER_SHA256:
            raise SystemExit("STOP: checker replay producer linkage mismatch")
        if checker_obj.get("transport_gate", {}).get("transport_gate_pass") is not True:
            raise SystemExit("STOP: checker replay transport gate mismatch")

        print("CHECKER_REPLAY_SEMANTIC_VALIDATION=PASS", flush=True)
        print("CHECKER_REPLAY_BYTE_SHA_REQUIRED=NO", flush=True)

        print("PHASE=CANONICAL_NC01_NC20", flush=True)
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        run([
            sys.executable,
            str(repo / HARNESS_REL),
            "--repo", str(repo),
            "--producer-receipt", str(producer),
            "--checker-receipt", str(checker),
            "--output", str(output),
        ], cwd=repo, env=env)

    if git(repo, "rev-parse", "HEAD") != head_pre:
        raise SystemExit("STOP: HEAD changed during run")
    if git(repo, "status", "--porcelain"):
        raise SystemExit("STOP: SOURCE_TREE_POST dirty")

    print("SELF_CONTAINED_RUN=PASS", flush=True)
    print("OUTPUT=/tmp/flambda_canonical_nc_v1.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
