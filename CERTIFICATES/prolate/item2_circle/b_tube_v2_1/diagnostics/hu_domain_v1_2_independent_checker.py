#!/usr/bin/env python3
"""Independent raw-evidence checker for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

No H_U numerical evaluation is performed. The checker reconstructs the finite
stage policy, first-passing semantics, budget accounting, exact rectangle cover,
and certified cover margin from the producer receipt's raw terminal leaves and
stage ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

REL_DIR = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics"
REL_POLICY = REL_DIR + "/hu_domain_v1_2_stage_policy.json"
REL_RUNNER = REL_DIR + "/hu_domain_v1_2_cell0_positive_control.py"
REL_CONTRACT = REL_DIR + "/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
REL_CHECKER = REL_DIR + "/hu_domain_v1_2_independent_checker.py"


def fail(code: str) -> None:
    raise SystemExit("FAIL:" + code)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_exact(text: Any, where: str) -> Fraction:
    if not isinstance(text, str) or "/" not in text:
        fail("NONCANONICAL_FRACTION:" + where)
    try:
        q = Fraction(text)
    except Exception:
        fail("BAD_FRACTION:" + where)
    canonical = f"{q.numerator}/{q.denominator}"
    if text != canonical:
        fail("NONCANONICAL_FRACTION:" + where)
    return q


@dataclass(frozen=True)
class Box:
    box_id: str
    r_lo: Fraction
    r_hi: Fraction
    l_lo: Fraction
    l_hi: Fraction

    def child_r(self, bit: int) -> "Box":
        m = (self.r_lo + self.r_hi) / 2
        if bit == 0:
            return Box(self.box_id + "/r0", self.r_lo, m, self.l_lo, self.l_hi)
        return Box(self.box_id + "/r1", m, self.r_hi, self.l_lo, self.l_hi)

    def child_l(self, k: int, n: int, tag: str) -> "Box":
        w = (self.l_hi - self.l_lo) / n
        return Box(
            f"{self.box_id}/{tag}{k}",
            self.r_lo,
            self.r_hi,
            self.l_lo + k * w,
            self.l_lo + (k + 1) * w,
        )


def box_from_record(rec: dict[str, Any], where: str) -> Box:
    bid = rec.get("box_id")
    if not isinstance(bid, str) or not bid:
        fail("BAD_BOX_ID:" + where)
    b = Box(
        bid,
        parse_exact(rec.get("r_lo"), where + ".r_lo"),
        parse_exact(rec.get("r_hi"), where + ".r_hi"),
        parse_exact(rec.get("lambda_lo"), where + ".lambda_lo"),
        parse_exact(rec.get("lambda_hi"), where + ".lambda_hi"),
    )
    if not (b.r_lo < b.r_hi and b.l_lo < b.l_hi):
        fail("BAD_BOX_GEOMETRY:" + where)
    return b


def split_by_stage(box: Box, stage: dict[str, Any]) -> list[Box]:
    op = stage.get("op")
    if op == "R_BISECT":
        return [box.child_r(0), box.child_r(1)]
    if op == "LAMBDA_SUBDIVIDE":
        if stage.get("division") != 32:
            fail("L32_DIVISION_MISMATCH")
        return [box.child_l(k, 32, "l32_") for k in range(32)]
    if op == "LAMBDA_REFINE_BY_4":
        return [box.child_l(k, 4, "l4_") for k in range(4)]
    fail("UNDECLARED_STAGE_OP:" + str(op))


def has_strict_descendant(prefix: str, terminal_ids: set[str]) -> bool:
    p = prefix + "/"
    return any(t.startswith(p) for t in terminal_ids)


def exact_cover(parent: Box, leaves: list[Box]) -> dict[str, bool]:
    if not leaves:
        return {
            "r_endpoints_exact": False,
            "lambda_endpoints_exact": False,
            "no_gaps": False,
            "no_interior_overlaps": False,
            "union_equals_parent": False,
        }
    contained = all(
        parent.r_lo <= b.r_lo < b.r_hi <= parent.r_hi
        and parent.l_lo <= b.l_lo < b.l_hi <= parent.l_hi
        for b in leaves
    )
    r_exact = contained and min(b.r_lo for b in leaves) == parent.r_lo and max(b.r_hi for b in leaves) == parent.r_hi
    l_exact = contained and min(b.l_lo for b in leaves) == parent.l_lo and max(b.l_hi for b in leaves) == parent.l_hi

    lambdas = sorted({parent.l_lo, parent.l_hi, *[b.l_lo for b in leaves], *[b.l_hi for b in leaves]})
    no_gaps = contained
    no_overlaps = contained
    for a, c in zip(lambdas, lambdas[1:]):
        if a == c:
            continue
        active = sorted(
            ((b.r_lo, b.r_hi) for b in leaves if b.l_lo <= a and c <= b.l_hi),
            key=lambda x: (x[0], x[1]),
        )
        if not active:
            no_gaps = False
            continue
        cursor = parent.r_lo
        for lo, hi in active:
            if lo > cursor:
                no_gaps = False
            if lo < cursor:
                no_overlaps = False
            if lo == cursor:
                cursor = hi
            elif lo < cursor and hi > cursor:
                cursor = hi
            elif lo > cursor:
                cursor = hi
        if cursor != parent.r_hi:
            no_gaps = False

    return {
        "r_endpoints_exact": r_exact,
        "lambda_endpoints_exact": l_exact,
        "no_gaps": no_gaps,
        "no_interior_overlaps": no_overlaps,
        "union_equals_parent": r_exact and l_exact and no_gaps and no_overlaps,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    policy_path = repo / REL_POLICY
    runner_path = repo / REL_RUNNER
    contract_path = repo / REL_CONTRACT
    checker_path = repo / REL_CHECKER

    for p, code in (
        (policy_path, "MISSING_POLICY"),
        (runner_path, "MISSING_RUNNER"),
        (contract_path, "MISSING_CONTRACT"),
        (checker_path, "MISSING_CHECKER"),
        (ns.receipt, "MISSING_RECEIPT"),
    ):
        if not p.is_file():
            fail(code)

    policy = json.loads(policy_path.read_text())
    contract = json.loads(contract_path.read_text())
    receipt = json.loads(ns.receipt.read_text())

    if contract.get("schema") != "production-hu-domain-contract-v1.2-release-v1":
        fail("CONTRACT_SCHEMA")
    if contract.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("CONTRACT_ID")
    if contract.get("release_status") != "RELEASED_AFTER_POSITIVE_CONTROL_PASS":
        fail("RELEASE_STATUS")

    pins = contract.get("pins", {})
    observed = {
        "stage_policy_sha256": sha256_file(policy_path),
        "producer_runner_sha256": sha256_file(runner_path),
        "independent_checker_sha256": sha256_file(checker_path),
    }
    for key, actual in observed.items():
        if pins.get(key) != actual:
            fail("PIN_MISMATCH:" + key)

    if receipt.get("contract_id") != contract["contract_id"]:
        fail("RECEIPT_CONTRACT_ID")
    if receipt.get("policy_sha256") != pins["stage_policy_sha256"]:
        fail("RECEIPT_POLICY_SHA")
    if receipt.get("runner_sha256") != pins["producer_runner_sha256"]:
        fail("RECEIPT_RUNNER_SHA")
    if receipt.get("source_baseline_commit") != contract["positive_control"]["source_baseline_commit"]:
        fail("RECEIPT_SOURCE_BASELINE")
    if receipt.get("execution_head") != contract["positive_control"]["execution_head"]:
        fail("RECEIPT_EXECUTION_HEAD")
    if sha256_file(ns.receipt) != contract["positive_control"]["result_json_sha256"]:
        fail("RECEIPT_FILE_SHA256")
    if receipt.get("quantity") != "H_U" or receipt.get("required_sign") != "POS":
        fail("RECEIPT_QUANTITY_SIGN")
    if receipt.get("dps") != policy.get("dps") or receipt.get("per_box_cap") != policy.get("per_box_cap"):
        fail("RECEIPT_DPS_CAP")
    if receipt.get("verdict") != "POSITIVE_CONTROL_PASS":
        fail("PRODUCER_VERDICT_NOT_PASS")
    if receipt.get("final_unresolved_count") != 0 or receipt.get("final_unresolved") != []:
        fail("FINAL_UNRESOLVED_NONZERO")

    p = policy["parent"]
    parent = Box(
        "CELL0",
        parse_exact(p["r_lo"], "policy.parent.r_lo"),
        parse_exact(p["r_hi"], "policy.parent.r_hi"),
        parse_exact(p["lambda_lo"], "policy.parent.lambda_lo"),
        parse_exact(p["lambda_hi"], "policy.parent.lambda_hi"),
    )

    terminal_records = receipt.get("terminal_leaves")
    if not isinstance(terminal_records, list) or not terminal_records:
        fail("TERMINAL_LEAVES")
    terminal_by_id: dict[str, dict[str, Any]] = {}
    terminal_boxes: list[Box] = []
    lo_by_id: dict[str, Fraction] = {}
    for i, rec in enumerate(terminal_records):
        if not isinstance(rec, dict):
            fail("BAD_TERMINAL_RECORD")
        b = box_from_record(rec, f"terminal[{i}]")
        if b.box_id in terminal_by_id:
            fail("DUPLICATE_TERMINAL_ID")
        if rec.get("status") != "PASS_POS":
            fail("TERMINAL_STATUS")
        if rec.get("required_sign") != "POS":
            fail("TERMINAL_REQUIRED_SIGN")
        if rec.get("effective_evaluation_cap") != policy["per_box_cap"]:
            fail("TERMINAL_CAP")
        if rec.get("complete_closed_cover") is not True:
            fail("TERMINAL_ANGULAR_COVER")
        lo = parse_exact(rec.get("lo"), f"terminal[{i}].lo")
        hi = parse_exact(rec.get("hi"), f"terminal[{i}].hi")
        width = parse_exact(rec.get("width"), f"terminal[{i}].width")
        if width != hi - lo:
            fail("TERMINAL_WIDTH")
        if lo <= 0:
            fail("NONPOSITIVE_TERMINAL_LO")
        terminal_by_id[b.box_id] = rec
        terminal_boxes.append(b)
        lo_by_id[b.box_id] = lo

    terminal_ids = set(terminal_by_id)
    for tid in terminal_ids:
        if has_strict_descendant(tid, terminal_ids):
            fail("RESOLVED_LEAF_REFINED:" + tid)

    ledger = receipt.get("stage_ledger")
    stages = policy.get("stages")
    if not isinstance(ledger, list) or not isinstance(stages, list) or not ledger:
        fail("STAGE_LEDGER")
    if len(ledger) > len(stages):
        fail("TOO_MANY_STAGES")

    current = [parent]
    reconstructed = []
    terminal_seen: set[str] = set()
    total_eval = 0

    for i, led in enumerate(ledger):
        stage = stages[i]
        if led.get("stage_id") != stage.get("stage_id") or led.get("op") != stage.get("op"):
            fail("STAGE_ORDER_OR_OP:" + str(i))

        unresolved_parent_count = len(current)
        if i == 0:
            if stage.get("op") != "BASE":
                fail("S0_NOT_BASE")
            children = [parent]
        else:
            children = [c for b in current for c in split_by_stage(b, stage)]

        expected_new = 1 if i == 0 else int(stage["child_factor"]) * unresolved_parent_count
        if len(children) != expected_new:
            fail("INTERNAL_NEW_BOX_COUNT:" + str(i))

        declared = expected_new * int(policy["per_box_cap"])
        if led.get("unresolved_parent_count") != unresolved_parent_count:
            fail("LEDGER_UNRESOLVED_PARENT_COUNT:" + str(i))
        if led.get("new_child_count") != expected_new:
            fail("LEDGER_NEW_CHILD_COUNT:" + str(i))
        if led.get("per_box_cap") != policy["per_box_cap"]:
            fail("LEDGER_CAP:" + str(i))
        if led.get("declared_stage_max_eval") != declared:
            fail("LEDGER_DECLARED_BUDGET:" + str(i))

        actual = led.get("actual_stage_eval")
        if not isinstance(actual, int) or actual < 0 or actual > declared:
            fail("LEDGER_ACTUAL_BUDGET:" + str(i))
        total_eval += actual

        next_current = []
        pass_count = 0
        for child in children:
            if child.box_id in terminal_ids:
                pass_count += 1
                terminal_seen.add(child.box_id)
            elif has_strict_descendant(child.box_id, terminal_ids):
                next_current.append(child)
            else:
                fail("UNACCOUNTED_GENERATED_CHILD:" + child.box_id)

        if led.get("pass_count") != pass_count:
            fail("LEDGER_PASS_COUNT:" + str(i))
        if led.get("unresolved_count_after_stage") != len(next_current):
            fail("LEDGER_UNRESOLVED_AFTER:" + str(i))

        reconstructed.append({
            "stage_id": stage["stage_id"],
            "unresolved_parent_count": unresolved_parent_count,
            "new_child_count": expected_new,
            "declared_stage_max_eval": declared,
            "actual_stage_eval": actual,
            "pass_count": pass_count,
            "unresolved_count_after_stage": len(next_current),
        })
        current = next_current

        if not current:
            if i != len(ledger) - 1:
                fail("NOT_FIRST_PASSING_STOP")
            break

    if current:
        fail("LEDGER_ENDED_WITH_UNRESOLVED")
    if terminal_seen != terminal_ids:
        fail("TERMINAL_SET_NOT_RECONSTRUCTED")
    if receipt.get("terminal_leaf_count") != len(terminal_ids):
        fail("TERMINAL_LEAF_COUNT")
    if sum(x["pass_count"] for x in reconstructed) != len(terminal_ids):
        fail("PASS_COUNT_SUM")
    if receipt.get("total_eval") != total_eval:
        fail("TOTAL_EVAL")

    cover = exact_cover(parent, terminal_boxes)
    reported_cover = receipt.get("cover_checks")
    if reported_cover != cover:
        fail("COVER_CHECK_MISMATCH")
    if not all(cover.values()):
        fail("COVER_NOT_EXACT")

    margin_id, margin = min(lo_by_id.items(), key=lambda kv: (kv[1], kv[0]))
    if receipt.get("certified_cover_margin_exact") != f"{margin.numerator}/{margin.denominator}":
        fail("MARGIN_EXACT")
    if receipt.get("certified_cover_margin_box_id") != margin_id:
        fail("MARGIN_BOX_ID")
    if receipt.get("cover_margin_is_true_minimum") is not False:
        fail("TRUE_MINIMUM_NONCLAIM")
    if receipt.get("all_terminal_lo_positive") is not True:
        fail("ALL_TERMINAL_POS_FLAG")

    print("CHECKER_ID=PRODUCTION_HU_DOMAIN_V1_2_INDEPENDENT_CHECKER_V1")
    print("NUMERICAL_REEVALUATION=NO")
    print("CONTRACT_PIN_CHECK=PASS")
    print("STAGE_ORDER=PASS")
    print("FIRST_PASSING=PASS")
    print("RESOLVED_LEAF_IMMUTABLE=PASS")
    print("BUDGET_ACCOUNTING=PASS")
    print("TERMINAL_LEAF_COUNT=" + str(len(terminal_ids)))
    print("TOTAL_EVAL=" + str(total_eval))
    print("R_ENDPOINTS_EXACT=TRUE")
    print("LAMBDA_ENDPOINTS_EXACT=TRUE")
    print("NO_GAPS=TRUE")
    print("NO_INTERIOR_OVERLAPS=TRUE")
    print("UNION_EQUALS_PARENT=TRUE")
    print("CERTIFIED_COVER_MARGIN_EXACT=" + f"{margin.numerator}/{margin.denominator}")
    print("CERTIFIED_COVER_MARGIN_BOX_ID=" + margin_id)
    print("COVER_MARGIN_IS_TRUE_MINIMUM=NO")
    print("INDEPENDENT_CHECKER_VERDICT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
