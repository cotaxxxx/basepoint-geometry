#!/usr/bin/env python3
"""B-LOCAL/B-ENTRY Phase-3 contract implementation.

Status: CHAT_SIDE_AUDIT_WAITING. Calculation-free only.
"""
from __future__ import annotations

import ast
import json
import subprocess
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any

from numeric_schema import (
    D_ZERO,
    Dyadic,
    DyadicInterval,
    Rational,
    arb_ball_to_exact_interval,
    canonical_json_bytes,
    parse_canonical_json_bytes,
    parse_canonical_jsonl,
    sha256_hex,
)

ERR = RuntimeError
DV = "2.1"
CFG = "blocal-run-config-v1"
CERT = "blocal-certificate-v1"
MCS = "btube-blocal-machine-conclusion-v1"
COMPLETE = "BLOCAL_COMPLETE"
INCOMPLETE = "BLOCAL_INCOMPLETE"
CHAIN = "BLOCAL-COVERAGE-CHAIN-v1"
CANON = "BTUBE_NUMERIC_SCHEMA_CANONICAL_JSON_V1"
ADAPTER = "ARB_TO_CANONICAL_DYADIC_INTERVAL_V1"
LP = Fraction(206539, 100000)
LM = Fraction(206538, 100000)
SN = Dyadic(1, 16)
RANGE = "(lambda_partial,lambda_start]"
STATEMENT = (
    "B(103/50)>0, B(207/100)<0, B(206538/100000)>0, "
    "B(206539/100000)<0, and B'(lambda)<0 on "
    "[206538/100000,206539/100000]. Hence lambda_partial is the unique "
    "root in (206538/100000,206539/100000)."
)
STAGE1_CONCLUSION = {
    "lambda_partial": "(206538/100000,206539/100000)",
    "strict_upper_bound": "206539/100000",
    "unique_on_interval": True,
}
SCOPE = (
    "Boundary-entry parameter only. Item 2 proper, requiring the single sign "
    "change of F_r, remains open."
)
L4_PREMISES = [
    "STAGE1_UNIQUE_BOUNDARY_ROOT_IN_OPEN_BRACKET",
    "STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET",
    "STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO",
    "L1_EXTENDED_HU_STRICT_POSITIVITY",
    "L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY",
    "L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY",
    "S_NEG_STRICTLY_EXCEEDS_STAGE1_BRACKET_WIDTH",
    "H_CONTINUITY_FROM_FIXED_FORMULA",
]
CLAIM_KEYS = {
    "stage1_dependency_exact",
    "l1_extended_exact_coverage",
    "l1_Hu_strictly_positive",
    "l2_extended_exact_coverage",
    "l2_inner_face_strictly_positive",
    "l3_nonnegative_exact_coverage",
    "l3_boundary_face_strictly_negative",
    "start_root_interval_certified",
    "supplies_binding_lambda_start",
    "real_analytic_claimed",
}
COMPLETE_MC_KEYS = {
    "schema",
    "status",
    "selected_candidate_index",
    "lambda_start",
    "start_root_interval",
    "machine_claims",
    "coverage",
}
INCOMPLETE_MC_KEYS = COMPLETE_MC_KEYS
COVERAGE_KEYS = {
    "l1_leaf_count",
    "l2_leaf_count",
    "l3_leaf_count",
    "record_count",
    "chain_tip_sha256",
}
FORBIDDEN_STAGE1_MODULE_PARTS = {
    "unverified_provenance",
    "prolate_boundary_entry_arb",
}
FORBIDDEN_STAGE1_CALLS = {
    "open",
    "read_text",
    "read_bytes",
    "import_module",
    "spec_from_file_location",
    "run_path",
    "exec_module",
}


def need(value: Any, message: str) -> None:
    if not value:
        raise ERR(message)


def exact_keys(value: Any, expected: set[str], where: str) -> dict[str, Any]:
    need(isinstance(value, dict) and set(value) == expected, f"{where}: exact keys")
    return value


def cbytes(value: Any) -> bytes:
    return canonical_json_bytes(value)


def d(mantissa: int, exponent: int) -> dict[str, Any]:
    return Dyadic.canonical(mantissa, exponent).to_json()


def q(value: Fraction) -> dict[str, str]:
    return Rational.from_fraction(value).to_json()


def iv(lo: tuple[int, int], hi: tuple[int, int]) -> dict[str, Any]:
    return DyadicInterval(Dyadic.canonical(*lo), Dyadic.canonical(*hi)).to_json()


def df(value: Any, where: str = "dyadic") -> Fraction:
    return Dyadic.from_json(value, where).as_fraction()


def qf(value: Any, where: str = "rational") -> Fraction:
    return Rational.from_json(value, where).as_fraction()


def interval_fraction(value: Any, where: str = "interval") -> tuple[Fraction, Fraction]:
    interval = DyadicInterval.from_json(value, where)
    return interval.lo.as_fraction(), interval.hi.as_fraction()


def canonicalizer_test() -> None:
    need(cbytes({"scope": "α"}) == b'{"scope":"\\u03b1"}', "canonicalizer policy")


def adapter(ball: Any) -> DyadicInterval:
    return arb_ball_to_exact_interval(ball)


def adapter_source_sha(path: Path | None = None) -> str:
    source = Path(__file__) if path is None else Path(path)
    need(not source.is_symlink(), "adapter symlink")
    source = source.resolve(strict=True)
    need(source.is_file(), "adapter regular file")
    return sha256_hex(source.read_bytes())


def sneg_proof() -> dict[str, Any]:
    need(100000 > (1 << 16), "integer s_neg proof")
    need(SN.as_fraction() > LP - LM, "fraction s_neg proof")
    return {"lhs": 100000, "rhs": 65536, "strict": True}


def json_pointer(value: Any, pointer: str) -> Any:
    need(pointer.startswith("/"), "JSON pointer")
    current = value
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        need(isinstance(current, dict) and token in current, "pointer component")
        current = current[token]
    return current


def extract_object(raw: bytes, pointer: str) -> tuple[dict[str, Any], bytes]:
    parsed = parse_canonical_json_bytes(raw, allow_display=False)
    selected = json_pointer(parsed, pointer)
    need(isinstance(selected, dict), f"{pointer}: object required")
    return selected, cbytes(selected)


def machine_conclusion(raw: bytes) -> tuple[dict[str, Any], bytes]:
    return extract_object(raw, "/machine_conclusion")


def _stage1_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        need(key not in result, f"Stage-1 duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_stage1_json_bytes(raw: bytes) -> dict[str, Any]:
    need(isinstance(raw, bytes), "Stage-1 JSON bytes")
    need(not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw, "Stage-1 JSON encoding")
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_stage1_pairs,
            parse_float=Decimal,
            parse_constant=lambda value: (_ for _ in ()).throw(ERR(f"Stage-1 constant: {value}")),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, InvalidOperation) as exc:
        raise ERR("Stage-1 JSON parse") from exc
    need(isinstance(parsed, dict), "Stage-1 JSON object")
    return parsed


def stage1_conclusion(raw: bytes) -> tuple[dict[str, Any], bytes]:
    parsed = parse_stage1_json_bytes(raw)
    conclusion = json_pointer(parsed, "/conclusion")
    need(isinstance(conclusion, dict), "/conclusion: object required")
    return conclusion, cbytes(conclusion)


def parse_sha256_manifest(raw: bytes, where: str) -> dict[str, str]:
    need(b"\r" not in raw, f"{where}: CR")
    entries: dict[str, str] = {}
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line:
            continue
        pieces = line.split(maxsplit=1)
        need(len(pieces) == 2, f"{where}:{line_number}")
        digest, name = pieces[0], pieces[1].lstrip(" *")
        need(
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            f"{where}: hash",
        )
        need(
            name
            and name not in entries
            and not name.startswith("/")
            and ".." not in Path(name).parts,
            f"{where}: path",
        )
        entries[name] = digest
    need(entries, f"{where}: empty")
    return entries


def repo_file(repository_root: Path, relative_path: str) -> Path:
    need(
        isinstance(relative_path, str)
        and relative_path
        and not relative_path.startswith("/"),
        "repo path",
    )
    root = repository_root.resolve(strict=True)
    candidate = repository_root / relative_path
    need(not candidate.is_symlink(), f"symlink {relative_path}")
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ERR(f"escape {relative_path}") from exc
    need(resolved.is_file(), f"file {relative_path}")
    return resolved


def decimal_value(value: Any, where: str) -> Decimal:
    need(isinstance(value, str), f"{where}: decimal string")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ERR(f"{where}: invalid decimal") from exc


def dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def constant_strings(node: ast.AST) -> list[str]:
    return [
        item.value
        for item in ast.walk(node)
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    ]


def audit_independent_source(raw: bytes, relative_path: str) -> None:
    try:
        source = raw.decode("utf-8")
        tree = ast.parse(source, filename=relative_path)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ERR(f"independence source parse: {relative_path}") from exc
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                lowered = alias.name.lower()
                need(
                    not any(part in lowered for part in FORBIDDEN_STAGE1_MODULE_PARTS),
                    f"independence import: {relative_path}",
                )
        elif isinstance(node, ast.ImportFrom):
            lowered = (node.module or "").lower()
            need(
                not any(part in lowered for part in FORBIDDEN_STAGE1_MODULE_PARTS),
                f"independence import-from: {relative_path}",
            )
        elif isinstance(node, ast.Call):
            call_name = dotted_name(node.func)
            leaf = call_name.rsplit(".", 1)[-1] if call_name else ""
            if leaf in FORBIDDEN_STAGE1_CALLS:
                for literal in constant_strings(node):
                    lowered = literal.lower().replace("\\", "/")
                    need(
                        not any(part in lowered for part in FORBIDDEN_STAGE1_MODULE_PARTS),
                        f"independence path access: {relative_path}",
                    )


def audit_stage1(plan: dict[str, Any]) -> dict[str, Any]:
    expected_plan_keys = {
        "repository_root",
        "certificate_path",
        "inner_manifest_path",
        "outer_manifest_path",
        "source_head",
        "certificate_sha256",
        "inner_manifest_sha256",
        "outer_manifest_sha256",
    }
    exact_keys(plan, expected_plan_keys, "plan")
    root = Path(plan["repository_root"])
    actual_head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    need(actual_head == plan["source_head"], "01 source head mismatch")
    need(
        len(plan["source_head"]) == 40
        and all(character in "0123456789abcdef" for character in plan["source_head"]),
        "01 source head format",
    )
    completed = [1]

    certificate_path = repo_file(root, plan["certificate_path"])
    inner_manifest_path = repo_file(root, plan["inner_manifest_path"])
    outer_manifest_path = repo_file(root, plan["outer_manifest_path"])
    certificate_raw = certificate_path.read_bytes()
    inner_raw = inner_manifest_path.read_bytes()
    outer_raw = outer_manifest_path.read_bytes()

    need(sha256_hex(certificate_raw) == plan["certificate_sha256"], "02 cert hash")
    completed.append(2)
    need(sha256_hex(inner_raw) == plan["inner_manifest_sha256"], "03 inner hash")
    completed.append(3)
    need(sha256_hex(outer_raw) == plan["outer_manifest_sha256"], "04 outer hash")
    completed.append(4)

    certificate = parse_stage1_json_bytes(certificate_raw)
    need(certificate.get("status") == "CERTIFIED", "05 status")
    completed.append(5)
    need(certificate.get("certified_statement") == STATEMENT, "06 statement")
    completed.append(6)

    conclusion, conclusion_raw = stage1_conclusion(certificate_raw)
    need(
        conclusion == STAGE1_CONCLUSION
        and conclusion_raw == cbytes(STAGE1_CONCLUSION),
        "07 conclusion",
    )
    completed.append(7)
    need(certificate.get("scope") == SCOPE, "08 scope")
    completed.append(8)

    evaluations = certificate.get("evaluations")
    required_evaluations = {
        "B(206538/100000)": "POSITIVE",
        "B(206539/100000)": "NEGATIVE",
        "Bprime([206538/100000,206539/100000])": "NEGATIVE",
    }
    need(isinstance(evaluations, dict), "09 evaluations")
    for evaluation_name, expected_sign in required_evaluations.items():
        entry = evaluations.get(evaluation_name)
        need(isinstance(entry, dict), f"09 evaluation {evaluation_name}")
        need(entry.get("sign") == expected_sign, f"09 sign {evaluation_name}")
    need(
        decimal_value(evaluations["B(206538/100000)"]["lower"], "09 lambda_minus lower") > 0,
        "09 lambda_minus strict positivity",
    )
    need(
        decimal_value(evaluations["B(206539/100000)"]["upper"], "09 lambda_plus upper") < 0,
        "09 lambda_plus strict negativity",
    )
    need(
        decimal_value(
            evaluations["Bprime([206538/100000,206539/100000])"]["upper"],
            "09 Bprime upper",
        )
        < 0,
        "09 Bprime strict negativity",
    )
    need(
        conclusion["lambda_partial"] == "(206538/100000,206539/100000)"
        and conclusion["unique_on_interval"] is True
        and conclusion["strict_upper_bound"] == "206539/100000",
        "09 conclusion-derived bracket",
    )
    completed.append(9)

    inner_entries = parse_sha256_manifest(inner_raw, "inner")
    outer_entries = parse_sha256_manifest(outer_raw, "outer")
    implementation_hashes = certificate.get("implementation_files_sha256")
    need(
        isinstance(implementation_hashes, dict)
        and set(implementation_hashes)
        == {
            "boundary_entry_independent.py",
            "bprime_independent.py",
            "run_enclosure.py",
            "verify_change_of_variables.py",
        },
        "10 implementation map",
    )
    independent_directory = Path(plan["certificate_path"]).parent
    for filename, expected_digest in sorted(implementation_hashes.items()):
        relative_path = (independent_directory / filename).as_posix()
        actual_raw = repo_file(root, relative_path).read_bytes()
        need(sha256_hex(actual_raw) == expected_digest, f"10 implementation {filename}")
        need(inner_entries.get(filename) == expected_digest, f"10 inner implementation {filename}")
        audit_independent_source(actual_raw, relative_path)
    completed.append(10)

    independence = certificate.get("independence")
    need(
        isinstance(independence, dict)
        and independence.get("unverified_provenance_file_read") is False,
        "11 independence flag",
    )
    completed.append(11)

    inner_base = Path(plan["inner_manifest_path"]).parent
    for relative_name, expected_digest in inner_entries.items():
        actual = repo_file(root, (inner_base / relative_name).as_posix()).read_bytes()
        need(sha256_hex(actual) == expected_digest, f"12 inner payload {relative_name}")
    outer_base = Path(plan["outer_manifest_path"]).parent
    for relative_name, expected_digest in outer_entries.items():
        actual = repo_file(root, (outer_base / relative_name).as_posix()).read_bytes()
        need(sha256_hex(actual) == expected_digest, f"12 outer payload {relative_name}")
    certificate_name = Path(plan["certificate_path"]).name
    need(inner_entries.get(certificate_name) == plan["certificate_sha256"], "12 cert inner")
    need(
        outer_entries.get(
            Path(plan["inner_manifest_path"]).relative_to(outer_base).as_posix()
        )
        == plan["inner_manifest_sha256"],
        "12 inner outer",
    )
    need(
        outer_entries.get(
            Path(plan["certificate_path"]).relative_to(outer_base).as_posix()
        )
        == plan["certificate_sha256"],
        "12 cert outer",
    )
    completed.append(12)
    return {
        "checks": completed,
        "count": 12,
        "state": "STAGE1_CONTENT_AUDIT_CANDIDATE",
    }


def interval_cover(
    intervals: list[tuple[Fraction, Fraction]],
    lower: Fraction,
    upper: Fraction,
    where: str,
) -> None:
    for left, right in intervals:
        need(lower <= left < right <= upper, f"{where}: outside")
    endpoints = sorted({lower, upper, *[point for interval in intervals for point in interval]})
    for left, right in zip(endpoints, endpoints[1:]):
        count = sum(a <= left and right <= b for a, b in intervals)
        need(count == 1, f"{where}: gap/overlap")


def rectangle_cover(
    rectangles: list[tuple[Fraction, Fraction, Fraction, Fraction]],
    u_lower: Fraction,
    u_upper: Fraction,
    s_lower: Fraction,
    s_upper: Fraction,
    where: str,
) -> None:
    for u0, u1, s0, s1 in rectangles:
        need(
            u_lower <= u0 < u1 <= u_upper and s_lower <= s0 < s1 <= s_upper,
            f"{where}: outside",
        )
    u_points = sorted({u_lower, u_upper, *[point for u0, u1, _, _ in rectangles for point in (u0, u1)]})
    s_points = sorted({s_lower, s_upper, *[point for _, _, s0, s1 in rectangles for point in (s0, s1)]})
    for u0, u1 in zip(u_points, u_points[1:]):
        for s0, s1 in zip(s_points, s_points[1:]):
            count = sum(
                a <= u0 and u1 <= b and c <= s0 and s1 <= e
                for a, b, c, e in rectangles
            )
            need(count == 1, f"{where}: gap/overlap")


def strict_sign(node: str, enclosure: Any, certified: bool) -> bool:
    interval = DyadicInterval.from_json(enclosure)
    if not certified:
        return False
    return D_ZERO < interval.lo if node in ("L1", "L2") else interval.hi < D_ZERO


def record_hash(record: dict[str, Any]) -> str:
    return sha256_hex(cbytes({key: value for key, value in record.items() if key != "record_sha256"}))


def chain_genesis(config_hash: str) -> str:
    return sha256_hex(CHAIN.encode("ascii") + b"\0" + bytes.fromhex(config_hash))


def candidate_schedule(config: dict[str, Any]) -> list[tuple[Dyadic, Dyadic]]:
    increments = [Dyadic.from_json(value) for value in config["lambda_candidates"]]
    u_values = [Dyadic.from_json(value) for value in config["u_max_candidates"]]
    need(increments == [Dyadic(1, exponent) for exponent in range(24, 3, -1)], "lambda schedule")
    need(u_values == [Dyadic(1, exponent) for exponent in (8, 7, 6, 5, 4)], "u schedule")
    return [(increment, u_value) for increment in increments for u_value in u_values]


def verify_tiles(
    records: list[dict[str, Any]],
    cursor: int,
    candidate_index: int,
    node: str,
    u_max: Fraction,
    s_start: Fraction,
    s_neg: Fraction,
    budgets: dict[str, int],
) -> tuple[int, bool, bool, int]:
    selected: list[dict[str, Any]] = []
    while (
        cursor < len(records)
        and records[cursor].get("record_type") == "TILE"
        and records[cursor].get("node") == node
    ):
        record = records[cursor]
        need(record.get("candidate_index") == candidate_index, f"{node}: index")
        for field in ("depth", "evaluations"):
            value = record.get(field)
            need(
                isinstance(value, int) and not isinstance(value, bool) and value >= 0,
                f"{node}: {field}",
            )
        selected.append(record)
        cursor += 1
    need(selected, f"{node}: count")
    sign_ok = all(
        strict_sign(node, record["enclosure"], record.get("certified") is True)
        for record in selected
    )
    budget_ok = len(selected) <= budgets["max_tiles"] and all(
        record["depth"] <= budgets["max_depth"]
        and record["evaluations"] <= budgets["max_evaluations"]
        for record in selected
    )
    if node == "L1":
        rectangle_cover(
            [
                (*interval_fraction(record["u_interval"]), *interval_fraction(record["s_interval"]))
                for record in selected
            ],
            Fraction(0),
            u_max,
            -s_neg,
            s_start,
            "L1",
        )
    else:
        interval_cover(
            [interval_fraction(record["s_interval"]) for record in selected],
            -s_neg if node == "L2" else Fraction(0),
            s_start,
            node,
        )
        expected_face = u_max if node == "L2" else Fraction(0)
        for record in selected:
            need(df(record["u_face"]) == expected_face, f"{node}: face")
    return cursor, sign_ok, budget_ok, len(selected)


def verify_j_start(record: dict[str, Any], candidate_index: int, lambda_start: Fraction) -> Any:
    expected_keys = {
        "record_type",
        "node",
        "selected_candidate_index",
        "lambda_start",
        "r_interval",
        "F_at_r_lo",
        "F_at_r_hi",
        "F_r_on_interval",
        "claim",
        "interval_method",
        "strict_self_containment",
        "certified",
        "previous_record_sha256",
        "record_sha256",
    }
    exact_keys(record, expected_keys, "J_START")
    need(
        record["record_type"] == record["node"] == "J_START"
        and record["selected_candidate_index"] == candidate_index
        and qf(record["lambda_start"]) == lambda_start,
        "J_START identity",
    )
    r_lower, r_upper = interval_fraction(record["r_interval"])
    f_lower = DyadicInterval.from_json(record["F_at_r_lo"])
    f_upper = DyadicInterval.from_json(record["F_at_r_hi"])
    derivative = DyadicInterval.from_json(record["F_r_on_interval"])
    need(
        0 < r_lower < r_upper < 1
        and D_ZERO < f_lower.lo
        and f_upper.hi < D_ZERO
        and derivative.hi < D_ZERO,
        "J_START signs",
    )
    need(
        record["claim"] == "J_START_UNIQUE_NONDEGENERATE_ROOT"
        and record["interval_method"] == "INTERVAL_NEWTON_OR_KRAWCZYK_V1"
        and record["strict_self_containment"] is True
        and record["certified"] is True,
        "J_START proof",
    )
    return record["r_interval"]


def verify_machine_claims(value: Any) -> None:
    claims = exact_keys(value, CLAIM_KEYS, "machine_claims")
    need(claims["real_analytic_claimed"] is False, "real analytic claim")
    for key, item in claims.items():
        if key != "real_analytic_claimed":
            need(isinstance(item, bool), f"machine claim {key}")


def complete_machine_conclusion(
    candidate_index: int,
    lambda_start: Fraction,
    root_interval: Any,
    counts: dict[str, int],
    record_count: int,
    chain_tip: str,
) -> dict[str, Any]:
    return {
        "schema": MCS,
        "status": COMPLETE,
        "selected_candidate_index": candidate_index,
        "lambda_start": q(lambda_start),
        "start_root_interval": root_interval,
        "machine_claims": {
            "stage1_dependency_exact": True,
            "l1_extended_exact_coverage": True,
            "l1_Hu_strictly_positive": True,
            "l2_extended_exact_coverage": True,
            "l2_inner_face_strictly_positive": True,
            "l3_nonnegative_exact_coverage": True,
            "l3_boundary_face_strictly_negative": True,
            "start_root_interval_certified": True,
            "supplies_binding_lambda_start": True,
            "real_analytic_claimed": False,
        },
        "coverage": {
            "l1_leaf_count": counts["L1"],
            "l2_leaf_count": counts["L2"],
            "l3_leaf_count": counts["L3"],
            "record_count": record_count,
            "chain_tip_sha256": chain_tip,
        },
    }


def incomplete_machine_conclusion(
    counts: dict[str, int], record_count: int, chain_tip: str
) -> dict[str, Any]:
    return {
        "schema": MCS,
        "status": INCOMPLETE,
        "selected_candidate_index": None,
        "lambda_start": None,
        "start_root_interval": None,
        "machine_claims": {
            "stage1_dependency_exact": False,
            "l1_extended_exact_coverage": False,
            "l1_Hu_strictly_positive": False,
            "l2_extended_exact_coverage": False,
            "l2_inner_face_strictly_positive": False,
            "l3_nonnegative_exact_coverage": False,
            "l3_boundary_face_strictly_negative": False,
            "start_root_interval_certified": False,
            "supplies_binding_lambda_start": False,
            "real_analytic_claimed": False,
        },
        "coverage": {
            "l1_leaf_count": counts["L1"],
            "l2_leaf_count": counts["L2"],
            "l3_leaf_count": counts["L3"],
            "record_count": record_count,
            "chain_tip_sha256": chain_tip,
        },
    }


def logical_lemmas() -> list[dict[str, Any]]:
    return [
        {
            "lemma_id": "BLOCAL_IVT_MONOTONE_ENTRY_V1",
            "machine_verified": False,
            "premises": list(L4_PREMISES),
            "conclusion": {
                "unique_non_degenerate_root_for_every_lambda_in": RANGE,
            },
        }
    ]


def verify_certificate(certificate_raw: bytes, expected_conclusion: dict[str, Any]) -> None:
    certificate = parse_canonical_json_bytes(certificate_raw, allow_display=False)
    need(certificate.get("schema") == CERT, "certificate schema")
    conclusion, conclusion_raw = machine_conclusion(certificate_raw)
    exact_keys(
        conclusion,
        COMPLETE_MC_KEYS if expected_conclusion["status"] == COMPLETE else INCOMPLETE_MC_KEYS,
        "machine_conclusion",
    )
    need(
        conclusion == expected_conclusion and conclusion_raw == cbytes(expected_conclusion),
        "certificate conclusion",
    )
    need(conclusion["schema"] == MCS, "machine conclusion schema")
    need(conclusion["status"] in {COMPLETE, INCOMPLETE}, "machine conclusion status")
    verify_machine_claims(conclusion["machine_claims"])
    exact_keys(conclusion["coverage"], COVERAGE_KEYS, "coverage")
    forbidden = {
        "binding_to_final_lambda_start",
        "coverage_claim",
        "unique_non_degenerate_root_for_every_lambda_in",
        "real_analytic",
        "state",
    }
    need(not forbidden.intersection(conclusion), "machine/logical separation")
    lemmas = certificate.get("logical_lemmas")
    need(lemmas == logical_lemmas(), "logical lemma contract")
    need(
        isinstance(lemmas, list)
        and len(lemmas) == 1
        and lemmas[0].get("machine_verified") is False,
        "logical lemma machine flag",
    )


def verify_run(config_raw: bytes, records_raw: bytes, certificate_raw: bytes | None = None) -> dict[str, Any]:
    config = parse_canonical_json_bytes(config_raw, allow_display=False)
    expected_config_keys = {
        "schema",
        "design_version",
        "lambda_plus",
        "s_neg",
        "lambda_candidates",
        "u_max_candidates",
        "budgets",
        "canonicalizer_id",
        "adapter_id",
        "adapter_source_sha256",
        "terminal_state_before_run",
    }
    exact_keys(config, expected_config_keys, "config")
    need(
        config["schema"] == CFG
        and config["design_version"] == DV
        and config["canonicalizer_id"] == CANON
        and config["adapter_id"] == ADAPTER
        and config["terminal_state_before_run"] == INCOMPLETE,
        "config identity",
    )
    need(qf(config["lambda_plus"]) == LP, "lambda_plus")
    need(Dyadic.from_json(config["s_neg"]) == SN, "s_neg")
    sneg_proof()
    budgets = exact_keys(
        config["budgets"],
        {"max_depth", "max_evaluations", "max_tiles"},
        "budgets",
    )
    for value in budgets.values():
        need(isinstance(value, int) and not isinstance(value, bool) and value > 0, "budget")
    schedule = candidate_schedule(config)
    parsed_records = parse_canonical_jsonl(records_raw)
    records = [record for record, _ in parsed_records]
    need(records, "records")
    config_hash = sha256_hex(config_raw)
    previous = chain_genesis(config_hash)
    for record in records:
        need(record.get("previous_record_sha256") == previous, "chain previous")
        need(record.get("record_sha256") == record_hash(record), "chain record hash")
        previous = record["record_sha256"]
    header = records[0]
    need(
        header.get("record_type") == "RUN_HEADER"
        and header.get("blocal_run_config_sha256") == config_hash
        and header.get("chain_genesis") == chain_genesis(config_hash)
        and header.get("canonicalizer_id") == CANON
        and header.get("adapter_source_sha256") == config["adapter_source_sha256"],
        "header",
    )
    cursor = 1
    totals = {"L1": 0, "L2": 0, "L3": 0}
    selected: tuple[int, Fraction, Fraction, Any] | None = None
    attempted = 0
    j_start_count = 0
    for candidate_index, (increment, u_value) in enumerate(schedule):
        s_start = increment.as_fraction()
        u_max = u_value.as_fraction()
        lambda_start = LP + s_start
        cursor, l1_sign, l1_budget, n1 = verify_tiles(
            records, cursor, candidate_index, "L1", u_max, s_start, SN.as_fraction(), budgets
        )
        cursor, l2_sign, l2_budget, n2 = verify_tiles(
            records, cursor, candidate_index, "L2", u_max, s_start, SN.as_fraction(), budgets
        )
        cursor, l3_sign, l3_budget, n3 = verify_tiles(
            records, cursor, candidate_index, "L3", u_max, s_start, SN.as_fraction(), budgets
        )
        totals["L1"] += n1
        totals["L2"] += n2
        totals["L3"] += n3
        signs_ok = l1_sign and l2_sign and l3_sign
        budgets_ok = l1_budget and l2_budget and l3_budget
        root_interval = None
        if cursor < len(records) and records[cursor].get("record_type") == "J_START":
            need(signs_ok and budgets_ok, "J_START failed candidate")
            root_interval = verify_j_start(records[cursor], candidate_index, lambda_start)
            cursor += 1
            j_start_count += 1
        need(
            cursor < len(records)
            and records[cursor].get("record_type") == "CANDIDATE_SUMMARY",
            "candidate summary",
        )
        summary = records[cursor]
        cursor += 1
        attempted += 1
        need(
            summary.get("candidate_index") == candidate_index
            and qf(summary.get("lambda_start")) == lambda_start
            and df(summary.get("u_max")) == u_max,
            "candidate summary identity",
        )
        need(
            summary.get("coverage_counts") == {"L1": n1, "L2": n2, "L3": n3},
            "coverage counts",
        )
        accepted = summary.get("candidate_accepted") is True
        need(accepted == (signs_ok and budgets_ok and root_interval is not None), "acceptance")
        need(summary.get("budget_exceeded") is (not budgets_ok), "budget summary")
        need(summary.get("unresolved") is (not signs_ok), "unresolved summary")
        if accepted:
            selected = (candidate_index, lambda_start, u_max, root_interval)
            break
        need(summary.get("first_failure_reason") not in (None, ""), "failure reason")
    need(
        cursor < len(records) and records[cursor].get("record_type") == "RUN_SUMMARY",
        "run summary",
    )
    run_summary = records[cursor]
    cursor += 1
    need(cursor == len(records), "record after summary")
    need(
        run_summary.get("records_chain_tip_sha256")
        == run_summary.get("previous_record_sha256"),
        "summary chain tip",
    )
    expected_counts = {
        "attempted_candidates": attempted,
        "tile_records": sum(totals.values()),
        "j_start_records": j_start_count,
        "candidate_summaries": attempted,
    }
    need(run_summary.get("exact_counts") == expected_counts, "summary counts")
    if selected is not None:
        candidate_index, lambda_start, u_max, root_interval = selected
        need(run_summary.get("terminal_state") == COMPLETE, "complete state")
        need(
            run_summary.get("selected_candidate_index") == candidate_index
            and qf(run_summary.get("lambda_start")) == lambda_start
            and df(run_summary.get("u_max")) == u_max
            and run_summary.get("start_root_interval") == root_interval,
            "complete summary",
        )
        expected_conclusion = complete_machine_conclusion(
            candidate_index,
            lambda_start,
            root_interval,
            totals,
            len(records),
            run_summary["previous_record_sha256"],
        )
        state = COMPLETE
    else:
        need(attempted == len(schedule), "incomplete attempted candidates")
        need(j_start_count == 0, "incomplete J_START")
        need(
            run_summary.get("terminal_state") == INCOMPLETE
            and run_summary.get("selected_candidate_index") is None
            and run_summary.get("lambda_start") is None
            and run_summary.get("u_max") is None
            and run_summary.get("start_root_interval") is None,
            "incomplete summary",
        )
        expected_conclusion = incomplete_machine_conclusion(
            totals, len(records), run_summary["previous_record_sha256"]
        )
        state = INCOMPLETE
    if certificate_raw is not None:
        verify_certificate(certificate_raw, expected_conclusion)
    return {
        "attempted_candidates": attempted,
        "selected_candidate_index": selected[0] if selected else None,
        "tile_records": sum(totals.values()),
        "terminal_state": state,
        "state": "BLOCAL_VERIFICATION_CANDIDATE",
    }
