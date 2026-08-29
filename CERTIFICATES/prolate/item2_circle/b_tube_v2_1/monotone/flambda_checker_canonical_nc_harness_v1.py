#!/usr/bin/env python3
"""Canonical NC01..NC20 harness for F_LAMBDA_TRANSPORT_CHECKER_V1.

The harness runs the frozen independent checker at its historical execution HEAD
inside a clean detached worktree. The canonical ID list is read from
F_LAMBDA_CHECKER_CANONICAL_NC_CATALOG_V1.json and must equal the literal list
below exactly. NC04b is intentionally excluded and is a later A0B q_left/q_right
pinning control.

Historical producer/checker receipt paths are optional. If omitted, this harness
locates them by exact SHA-256 under deterministic local roots. This removes the
manual path-discovery step without weakening receipt identity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import types
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
BT_REL = Path("CERTIFICATES/prolate/item2_circle/b_tube_v2_1")
CATALOG_REL = BT_REL / "monotone/F_LAMBDA_CHECKER_CANONICAL_NC_CATALOG_V1.json"
CHECKER_REL = BT_REL / "flambda_transport_checker_v1.py"
CHECKER_HEAD = "996bc349fdafe6d0c840c06e2c79a6a51e52b9b0"
COMPONENT1_SHA256 = "f60c22cbc1d4a45e5593a64e64194f7e3dbc97df69e1547aca092d2d93b7911f"
PRODUCER_RECEIPT_SHA256 = "34f1a08a334e4c62fc3071427f7d91e863341cfb4c784405d0be26ed4d927d8e"
CHECKER_RECEIPT_SHA256 = "3e1e1894604e9b99f7413cbb6d3bbdb7c7b0ecb6babe1966ae955986bebe59a9"
DELTA = Fraction(6900531025808907, 1 << 86)
EPS = Fraction(1, 1 << 100)
CANONICAL_IDS = [f"NC{i:02d}" for i in range(1, 21)]


def stop(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        stop(f"expected JSON object: {path}")
    return obj


def deep_copy(obj: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(obj))


def deterministic_search_roots(repo: Path) -> list[Path]:
    roots: list[Path] = []
    for candidate in (repo, repo.parent, Path("/tmp")):
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.exists() and resolved not in roots:
            roots.append(resolved)
    return roots


def discover_receipt(repo: Path, expected_sha: str, label: str) -> Path:
    matches: list[Path] = []
    scanned = 0
    for root in deterministic_search_roots(repo):
        try:
            candidates = sorted(root.rglob("*.json"))
        except OSError:
            continue
        for path in candidates:
            if not path.is_file():
                continue
            scanned += 1
            try:
                if sha256_path(path) == expected_sha:
                    matches.append(path.resolve())
            except (OSError, PermissionError):
                continue
    unique = sorted(set(matches))
    if not unique:
        print(f"{label}_AUTO_RESOLVE=MISSING")
        print(f"{label}_EXPECTED_SHA256={expected_sha}")
        print(f"{label}_JSON_FILES_SCANNED={scanned}")
        stop(f"{label} receipt with exact SHA-256 is not present in repo/repo-parent//tmp")
    if len(unique) > 1:
        print(f"{label}_AUTO_RESOLVE=MULTIPLE_IDENTICAL_COPIES")
        for path in unique:
            print(f"{label}_COPY={path}")
    chosen = unique[0]
    print(f"{label}_AUTO_RESOLVE=FOUND")
    print(f"{label}_PATH={chosen}")
    print(f"{label}_SHA256={expected_sha}")
    return chosen


def resolve_receipt(repo: Path, supplied: Path | None, expected_sha: str, label: str) -> Path:
    if supplied is None:
        return discover_receipt(repo, expected_sha, label)
    path = supplied.expanduser().resolve()
    if not path.is_file():
        stop(f"{label} supplied path is not a file: {path}")
    got = sha256_path(path)
    if got != expected_sha:
        stop(f"{label} SHA mismatch: expected {expected_sha}, got {got}")
    print(f"{label}_AUTO_RESOLVE=EXPLICIT_PATH")
    print(f"{label}_PATH={path}")
    print(f"{label}_SHA256={got}")
    return path


def load_checker(worktree: Path):
    bt = worktree / BT_REL
    sys.path.insert(0, str(bt))
    path = worktree / CHECKER_REL
    spec = importlib.util.spec_from_file_location("flambda_checker_nc_frozen", path)
    if spec is None or spec.loader is None:
        stop("cannot load frozen checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_failure(checker: Any, *, expected_code: str, expected_head: str, receipt: Path) -> dict[str, Any]:
    try:
        checker.check_receipt(expected_head=expected_head, producer_receipt_path=receipt)
    except checker.CheckerFailure as exc:
        if exc.code != expected_code:
            stop(f"expected {expected_code}, got {exc.code}:{exc.detail}")
        return {
            "status": "PASS",
            "expected_failure_code": expected_code,
            "observed_failure_code": exc.code,
            "observed_detail": exc.detail,
        }
    except Exception as exc:
        stop(f"expected CheckerFailure {expected_code}, got {type(exc).__name__}: {exc}")
    stop(f"expected failure {expected_code}, checker passed")


def mutate_dyadic(Dyadic: Any, obj: dict[str, Any], key: str, delta: Fraction = EPS) -> None:
    value = Dyadic.from_json(obj[key], key).as_fraction()
    obj[key] = Dyadic.from_fraction(value + delta).to_json()


def mutate_rational(Rational: Any, obj: dict[str, Any], key: str, delta: Fraction = EPS) -> None:
    value = Rational.from_json(obj[key], key).as_fraction()
    obj[key] = Rational.from_fraction(value + delta).to_json()


def mutation_table(Dyadic: Any, Rational: Any) -> dict[str, Callable[[dict[str, Any]], None]]:
    def nc01(x): x["schema"] = "INVALID_SCHEMA"
    def nc02(x): x["evidence_class"] = "INVALID"
    def nc03(x): x["binding_use_authorized"] = True
    def nc04(x):
        rlo = Dyadic.from_json(x["r_lo"], "r_lo").as_fraction() - DELTA
        rhi = Dyadic.from_json(x["r_hi"], "r_hi").as_fraction() + DELTA
        x["r_lo"] = Dyadic.from_fraction(rlo).to_json()
        x["r_hi"] = Dyadic.from_fraction(rhi).to_json()
        x["tube_interval"]["lo"] = Dyadic.from_fraction(rlo).to_json()
        x["tube_interval"]["hi"] = Dyadic.from_fraction(rhi).to_json()
    def nc05(x): x["checker_required"] = False
    def nc06(x): x["human_promotion_required"] = False
    def nc07(x): x["producer_verdict"] = "INVALID"
    def nc08(x): x["candidate_index"] = True
    def nc09(x): x["predictor"] = None
    def nc10(x): x["predictor"]["q_left"] = Dyadic.from_fraction(Fraction(0)).to_json()
    def nc11(x): mutate_dyadic(Dyadic, x, "nominal_lambda_width")
    def nc12(x): mutate_dyadic(Dyadic, x, "radius_cap")
    def nc13(x): mutate_dyadic(Dyadic, x, "adaptive_radius")
    def nc14(x): mutate_dyadic(Dyadic, x["tube_interval"], "lo")
    def nc15(x): mutate_dyadic(Dyadic, x, "r_lo")
    def nc16(x): mutate_dyadic(Dyadic, x, "r_hi")
    def nc17(x): x["cell_index"] = True
    def nc18(x): mutate_rational(Rational, x["candidate_parent"], "hi")
    def nc19(x): mutate_rational(Rational, x["tiles"][0], "hi")
    return {
        "NC01": nc01, "NC02": nc02, "NC03": nc03, "NC04": nc04,
        "NC05": nc05, "NC06": nc06, "NC07": nc07, "NC08": nc08,
        "NC09": nc09, "NC10": nc10, "NC11": nc11, "NC12": nc12,
        "NC13": nc13, "NC14": nc14, "NC15": nc15, "NC16": nc16,
        "NC17": nc17, "NC18": nc18, "NC19": nc19,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--producer-receipt", type=Path, default=None)
    ap.add_argument("--checker-receipt", type=Path, default=None)
    ap.add_argument("--output", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    output = ns.output.expanduser().resolve()

    if git(repo, "status", "--porcelain"):
        stop("SOURCE_TREE_PRE dirty")
    head_pre = git(repo, "rev-parse", "HEAD")

    catalog_path = repo / CATALOG_REL
    catalog_raw = catalog_path.read_bytes()
    catalog = json.loads(catalog_raw)
    if catalog.get("catalog_id") != "F_LAMBDA_CHECKER_CANONICAL_NC_CATALOG_V1":
        stop("catalog id mismatch")
    if catalog.get("checker_execution_head") != CHECKER_HEAD:
        stop("catalog checker head mismatch")
    if catalog.get("component1_geometry_receipt_sha256") != COMPONENT1_SHA256:
        stop("catalog Component-1 SHA mismatch")
    if catalog.get("exact_id_list") != CANONICAL_IDS:
        stop("canonical ID list mismatch")
    rows = catalog.get("controls")
    if not isinstance(rows, list) or [r.get("id") for r in rows] != CANONICAL_IDS:
        stop("catalog control order mismatch")
    if catalog.get("excluded_followup_controls") != ["NC04b"]:
        stop("NC04b exclusion mismatch")

    producer_path = resolve_receipt(repo, ns.producer_receipt, PRODUCER_RECEIPT_SHA256, "PRODUCER_RECEIPT")
    checker_receipt_path = resolve_receipt(repo, ns.checker_receipt, CHECKER_RECEIPT_SHA256, "CHECKER_RECEIPT")

    producer_raw = producer_path.read_bytes()
    producer = json.loads(producer_raw)
    checked_raw = checker_receipt_path.read_bytes()
    checked = json.loads(checked_raw)
    if checked.get("checker_verdict") != "PASS_BINDING_CANDIDATE_CHECK":
        stop("checker receipt is not PASS_BINDING_CANDIDATE_CHECK")
    if checked.get("execution_head") != CHECKER_HEAD:
        stop("checker receipt execution head mismatch")
    if checked.get("producer_receipt", {}).get("sha256") != sha256_bytes(producer_raw):
        stop("checker receipt is not linked to producer receipt")

    with tempfile.TemporaryDirectory(prefix="flambda-nc-catalog-") as td:
        td_path = Path(td)
        wt = td_path / "frozen"
        subprocess.check_call(
            ["git", "-C", str(repo), "worktree", "add", "--detach", str(wt), CHECKER_HEAD],
            stdout=subprocess.DEVNULL,
        )
        try:
            if git(wt, "status", "--porcelain"):
                stop("frozen checker worktree dirty")
            checker = load_checker(wt)
            from calibration_context import Dyadic, Rational, canonical_json_bytes

            mutations = mutation_table(Dyadic, Rational)
            results: list[dict[str, Any]] = []
            for row in rows:
                nc_id = row["id"]
                expected = row["expected_failure_code"]
                if nc_id == "NC20":
                    sentinel = types.ModuleType(checker.FORBIDDEN_PRODUCER_MODULE)
                    sentinel.__file__ = str(checker.FORBIDDEN_PRODUCER_PATH)
                    old = sys.modules.get(checker.FORBIDDEN_PRODUCER_MODULE)
                    sys.modules[checker.FORBIDDEN_PRODUCER_MODULE] = sentinel
                    try:
                        result = expected_failure(
                            checker,
                            expected_code=expected,
                            expected_head=CHECKER_HEAD,
                            receipt=producer_path,
                        )
                    finally:
                        if old is None:
                            sys.modules.pop(checker.FORBIDDEN_PRODUCER_MODULE, None)
                        else:
                            sys.modules[checker.FORBIDDEN_PRODUCER_MODULE] = old
                else:
                    mutated = deep_copy(producer)
                    mutations[nc_id](mutated)
                    receipt = td_path / f"{nc_id}.json"
                    receipt.write_bytes(canonical_json_bytes(mutated))
                    result = expected_failure(
                        checker,
                        expected_code=expected,
                        expected_head=CHECKER_HEAD,
                        receipt=receipt,
                    )
                result.update({"nc_id": nc_id, "mutation": row["mutation"]})
                results.append(result)
        finally:
            subprocess.check_call(
                ["git", "-C", str(repo), "worktree", "remove", "--force", str(wt)],
                stdout=subprocess.DEVNULL,
            )

    if [x["nc_id"] for x in results] != CANONICAL_IDS or any(x["status"] != "PASS" for x in results):
        stop("canonical NC completion invariant failed")

    head_post = git(repo, "rev-parse", "HEAD")
    if head_post != head_pre:
        stop("HEAD changed during harness")
    if git(repo, "status", "--porcelain"):
        stop("SOURCE_TREE_POST dirty")

    receipt = {
        "schema": "flambda-checker-canonical-nc-run-v1",
        "catalog_id": catalog["catalog_id"],
        "catalog_sha256": sha256_bytes(catalog_raw),
        "canonical_id_list": CANONICAL_IDS,
        "canonical_count": len(CANONICAL_IDS),
        "checker_execution_head": CHECKER_HEAD,
        "component1_geometry_receipt_sha256": COMPONENT1_SHA256,
        "producer_receipt_sha256": sha256_bytes(producer_raw),
        "checker_receipt_sha256": sha256_bytes(checked_raw),
        "producer_receipt_path": str(producer_path),
        "checker_receipt_path": str(checker_receipt_path),
        "nc04b_included": False,
        "nc04b_status": "DEFERRED_TO_A0B_Q_LEFT_Q_RIGHT_PIN_PHASE",
        "binding_use_authorized": False,
        "controls": results,
        "all_controls_pass": True,
        "source_tree_pre_clean": True,
        "source_tree_post_clean": True,
        "head_unchanged_during_run": True,
        "verdict": "CANONICAL_NC_CATALOG_PASS_NOT_PROMOTED",
    }
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("CATALOG_ID=" + catalog["catalog_id"])
    print("CATALOG_SHA256=" + receipt["catalog_sha256"])
    print("EXACT_ID_LIST=" + ",".join(CANONICAL_IDS))
    print("CANONICAL_COUNT=20")
    for row in results:
        print(f"{row['nc_id']}=PASS:{row['observed_failure_code']}")
    print("NC04b=DEFERRED_TO_A0B_Q_LEFT_Q_RIGHT_PIN_PHASE")
    print("COMPONENT1_GEOMETRY_RECEIPT_SHA256=" + COMPONENT1_SHA256)
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=CANONICAL_NC_CATALOG_PASS_NOT_PROMOTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
