#!/usr/bin/env python3
"""Canonical F_lambda NC v1.1 execution runner.

RAW-REVIEW STAGE ONLY.

This runner reads the frozen execution classification as the sole source
of per-control execution semantics.  It does not execute mutations,
numerical evaluators, gate units, or coverage promotion at this stage.
"""

from __future__ import annotations

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[5]

MONOTONE = (
    ROOT
    / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone"
)

CLASSIFICATION = (
    MONOTONE
    / "F_LAMBDA_CHECKER_CANONICAL_NC_V1_1_EXECUTION_CLASSIFICATION.tsv"
)

PREEXEC = (
    MONOTONE
    / "F_LAMBDA_CHECKER_CANONICAL_NC_V1_1_PREEXEC_CONTROLS.tsv"
)

CHECKER = (
    ROOT
    / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
    / "flambda_transport_checker_v1.py"
)

CLASSIFICATION_SHA256 = (
    "0b479b744406e66596e0f9c6fabc7dbd421a3b5671bc95cd59347b1ad4501a4d"
)
PREEXEC_SHA256 = (
    "d8e8f4b6022d676d63b696a7d09bb046203b282ce571c14eddffaf4fc54eed55"
)
CHECKER_SHA256 = (
    "5be9dea3679f2dd9245c4df21aca7863c8743ac0395c7f8173950a7b37f5bb18"
)

EXPECTED_CONTROL_COUNT = 42
EXPECTED_CONTRACT_COUNT = 31

EXPECTED_COLUMNS = [
    "CONTROL_ID",
    "CONTRACT_ID",
    "CONTRACT_CODE",
    "EXPECTED_SPECIFIC_CODE",
    "CANONICAL_MUTATION",
    "E2E_POSSIBLE",
    "EXPECTED_UPSTREAM_CODE",
    "E2E_EXECUTED",
    "E2E_OBSERVED_CODE",
    "SPECIFIC_GATE_KIND",
    "SPECIFIC_GATE_EXECUTED",
    "SPECIFIC_GATE_CODE",
    "REPORT_ONLY_NUMERIC",
    "COVERAGE",
    "NOTE",
]


class RunnerFailure(RuntimeError):
    pass


def fail(code: str, detail: str = "") -> None:
    msg = code if not detail else f"{code}: {detail}"
    raise RunnerFailure(msg)


def need(ok: bool, code: str, detail: str = "") -> None:
    if not ok:
        fail(code, detail)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def git(*args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        fail("FAIL_GIT", f"{' '.join(args)} :: {p.stderr.strip()}")
    return p.stdout.strip()


def read_classification() -> list[dict[str, str]]:
    with CLASSIFICATION.open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        need(
            reader.fieldnames == EXPECTED_COLUMNS,
            "FAIL_CLASSIFICATION_SCHEMA",
            repr(reader.fieldnames),
        )

        rows: list[dict[str, str]] = []
        for raw in reader:
            # Frozen TSV physically trims trailing empty fields.
            row = {
                key: (raw.get(key) if raw.get(key) is not None else "")
                for key in EXPECTED_COLUMNS
            }
            rows.append(row)

    return rows


def main() -> int:
    baseline_head = "86635ea7e0a39ad55ebfde80e3f6dab8c0dcb2eb"
    source_head = git("rev-parse", "HEAD")
    source_status = git("status", "--porcelain")

    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", baseline_head, source_head],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    need(
        ancestry.returncode == 0,
        "FAIL_BASELINE_ANCESTRY",
        f"{baseline_head} !<= {source_head}",
    )

    need(
        source_status == "",
        "FAIL_SOURCE_TREE_DIRTY",
        source_status,
    )

    changed_since_baseline = set(
        filter(
            None,
            git(
                "diff",
                "--name-only",
                f"{baseline_head}..{source_head}",
            ).splitlines(),
        )
    )
    expected_runner_path = (
        "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/"
        "flambda_checker_canonical_nc_run_v1_1.py"
    )
    need(
        changed_since_baseline == {expected_runner_path},
        "FAIL_POST_BASELINE_RUNNER_FILE_SET",
        repr(sorted(changed_since_baseline)),
    )

    need(
        sha256(CLASSIFICATION) == CLASSIFICATION_SHA256,
        "FAIL_CLASSIFICATION_PIN",
    )
    need(
        sha256(PREEXEC) == PREEXEC_SHA256,
        "FAIL_PREEXEC_PIN",
    )
    need(
        sha256(CHECKER) == CHECKER_SHA256,
        "FAIL_CHECKER_PIN",
    )

    rows = read_classification()

    ids = [r["CONTROL_ID"] for r in rows]
    contracts = {r["CONTRACT_ID"] for r in rows}

    need(
        len(rows) == EXPECTED_CONTROL_COUNT,
        "FAIL_CONTROL_COUNT",
        str(len(rows)),
    )
    need(
        len(set(ids)) == EXPECTED_CONTROL_COUNT,
        "FAIL_CONTROL_ID_UNIQUENESS",
    )
    need(
        len(contracts) == EXPECTED_CONTRACT_COUNT,
        "FAIL_CONTRACT_COUNT",
        str(len(contracts)),
    )

    for r in rows:
        cid = r["CONTROL_ID"]
        possible = r["E2E_POSSIBLE"]

        need(
            possible in {"YES", "NO"},
            "FAIL_E2E_POSSIBLE_ENUM",
            cid,
        )

        if possible == "YES":
            need(
                r["EXPECTED_UPSTREAM_CODE"] == "",
                "FAIL_YES_HAS_UPSTREAM",
                cid,
            )
        else:
            need(
                r["EXPECTED_UPSTREAM_CODE"]
                == "FAIL_POST_BASELINE_FILE_SET",
                "FAIL_NO_UPSTREAM_PIN",
                cid,
            )

        need(
            r["E2E_EXECUTED"] == "NO",
            "FAIL_PREFILLED_E2E_STATE",
            cid,
        )
        need(
            r["E2E_OBSERVED_CODE"] == "",
            "FAIL_PREFILLED_E2E_CODE",
            cid,
        )
        need(
            r["SPECIFIC_GATE_EXECUTED"] == "NO",
            "FAIL_PREFILLED_GATE_STATE",
            cid,
        )
        need(
            r["SPECIFIC_GATE_CODE"] == "",
            "FAIL_PREFILLED_GATE_CODE",
            cid,
        )
        need(
            r["COVERAGE"] == "NOT_EXECUTED",
            "FAIL_PREFILLED_COVERAGE",
            cid,
        )

    pin_file_rows = {
        r["CONTROL_ID"]
        for r in rows
        if r["CANONICAL_MUTATION"].startswith("PIN_FILE:")
    }
    need(
        pin_file_rows == {"NC01", "NC19"},
        "FAIL_PIN_FILE_MUTATION_POLICY",
        repr(sorted(pin_file_rows)),
    )

    dirty_rows = {
        r["CONTROL_ID"]
        for r in rows
        if r["CANONICAL_MUTATION"] == "WORKTREE:dirty_state"
    }
    need(
        dirty_rows == {"NC25a"},
        "FAIL_DIRTY_MUTATION_POLICY",
        repr(sorted(dirty_rows)),
    )

    head_rows = {
        r["CONTROL_ID"]
        for r in rows
        if r["CANONICAL_MUTATION"] == "ARGUMENT:expected_head"
    }
    need(
        head_rows == {"NC25b"},
        "FAIL_HEAD_MUTATION_POLICY",
        repr(sorted(head_rows)),
    )

    nc04b = next(r for r in rows if r["CONTROL_ID"] == "NC04b")
    need(
        nc04b["SPECIFIC_GATE_KIND"] == "A0B_PIN_GATE",
        "FAIL_NC04b_GATE_KIND",
    )

    nc16 = next(r for r in rows if r["CONTROL_ID"] == "NC16")
    nc17 = next(r for r in rows if r["CONTROL_ID"] == "NC17")
    need(
        nc16["REPORT_ONLY_NUMERIC"] == "PLANNED",
        "FAIL_NC16_REPORT_ONLY_POLICY",
    )
    need(
        nc17["REPORT_ONLY_NUMERIC"] == "PLANNED",
        "FAIL_NC17_REPORT_ONLY_POLICY",
    )

    yes_count = sum(r["E2E_POSSIBLE"] == "YES" for r in rows)
    no_count = sum(r["E2E_POSSIBLE"] == "NO" for r in rows)

    print(f"BASELINE_HEAD={baseline_head}")
    print(f"SOURCE_HEAD={source_head}")
    print("BASELINE_ANCESTRY=PASS")
    print("POST_BASELINE_RUNNER_FILE_SET=PASS")
    print("SOURCE_TREE=CLEAN")
    print(f"CLASSIFICATION_SHA256={CLASSIFICATION_SHA256}")
    print(f"PREEXEC_SHA256={PREEXEC_SHA256}")
    print(f"CHECKER_SHA256={CHECKER_SHA256}")
    print(f"CONTROL_COUNT={len(rows)}")
    print(f"CONTRACT_COUNT={len(contracts)}")
    print(f"E2E_YES_COUNT={yes_count}")
    print(f"E2E_NO_COUNT={no_count}")
    print("PIN_FILE_ROWS=NC01,NC19")
    print("DIRTY_ROWS=NC25a")
    print("EXPECTED_HEAD_ROWS=NC25b")
    print("NC04b_SPECIFIC_GATE_KIND=A0B_PIN_GATE")
    print("NC16_REPORT_ONLY_NUMERIC=PLANNED")
    print("NC17_REPORT_ONLY_NUMERIC=PLANNED")
    print("NUMERICAL_EVALUATOR_CALLED=FALSE")
    print("CONTROL_EXECUTION_PERFORMED=FALSE")
    print("COVERAGE_PROMOTION_PERFORMED=FALSE")
    print("RUNNER_RAW_REVIEW_STAGE=PASS_NOT_EXECUTED")

    print()
    print("=== EXECUTION PLAN ===")
    for r in rows:
        print(
            "\t".join(
                [
                    r["CONTROL_ID"],
                    r["CONTRACT_ID"],
                    r["E2E_POSSIBLE"],
                    r["EXPECTED_SPECIFIC_CODE"],
                    r["EXPECTED_UPSTREAM_CODE"] or "NA",
                    r["SPECIFIC_GATE_KIND"],
                    r["CANONICAL_MUTATION"],
                ]
            )
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunnerFailure as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
