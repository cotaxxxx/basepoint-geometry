#!/usr/bin/env python3
"""Shared semantic validator for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2 receipts.

This module contains no positive-control receipt/head pin and performs no
numerical H_U evaluation.  It reconstructs the released finite-stage semantics,
first-passing behavior, immutable terminal leaves, raw budget accounting, exact
cover, and certified cover margin from raw evidence.

The frozen release checker remains byte-identical at hu-domain-v1.2; this module
is the post-release shared semantic core for production checking.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any


class ValidationError(RuntimeError):
    pass


def fail(code: str) -> None:
    raise ValidationError(code)


def parse_exact(text: Any, where: str) -> Fraction:
    if not isinstance(text, str) or "/" not in text:
        fail("NONCANONICAL_FRACTION:" + where)
    try:
        q = Fraction(text)
    except Exception:
        fail("BAD_FRACTION:" + where)
    if text != f"{q.numerator}/{q.denominator}":
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


def validate_semantics(policy: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    if receipt.get("contract_id") != "PRODUCTION_HU_DOMAIN_CONTRACT_V1_2":
        fail("RECEIPT_CONTRACT_ID")
    if receipt.get("quantity") != "H_U" or receipt.get("required_sign") != "POS":
        fail("RECEIPT_QUANTITY_SIGN")
    if receipt.get("dps") != policy.get("dps") or receipt.get("per_box_cap") != policy.get("per_box_cap"):
        fail("RECEIPT_DPS_CAP")
    if receipt.get("final_unresolved_count") != 0 or receipt.get("final_unresolved") != []:
        fail("FINAL_UNRESOLVED_NONZERO")

    parent_rec = receipt.get("parent")
    if not isinstance(parent_rec, dict):
        fail("PARENT_RECORD")
    parent = box_from_record(parent_rec, "receipt.parent")

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

    evaluated_records = receipt.get("evaluated_boxes")
    if not isinstance(evaluated_records, list) or not evaluated_records:
        fail("EVALUATED_BOXES")
    evaluated_by_stage: dict[str, list[dict[str, Any]]] = {}
    evaluated_ids: set[str] = set()
    for i, rec in enumerate(evaluated_records):
        if not isinstance(rec, dict):
            fail("BAD_EVALUATED_RECORD")
        box_from_record(rec, f"evaluated[{i}]")
        bid = rec.get("box_id")
        if bid in evaluated_ids:
            fail("DUPLICATE_EVALUATED_ID:" + str(bid))
        evaluated_ids.add(bid)
        sid = rec.get("stage_id")
        if not isinstance(sid, str) or not sid:
            fail("EVALUATED_STAGE_ID")
        status = rec.get("status")
        if status not in ("PASS_POS", "ABORT"):
            fail("EVALUATED_STATUS:" + str(bid))
        ev = rec.get("evaluation_count")
        if not isinstance(ev, int) or ev < 0 or ev > policy["per_box_cap"]:
            fail("EVALUATED_CAP:" + str(bid))
        if rec.get("effective_evaluation_cap") != policy["per_box_cap"]:
            fail("EVALUATED_EFFECTIVE_CAP:" + str(bid))
        if status == "ABORT":
            if rec.get("abort_reason") != "ANGULAR_EVALUATION_BUDGET":
                fail("ABORT_REASON:" + str(bid))
            if rec.get("lo") is not None or rec.get("hi") is not None:
                fail("ABORT_INTERVAL_PRESENT:" + str(bid))
        else:
            if rec.get("abort_reason") is not None:
                fail("PASS_ABORT_REASON:" + str(bid))
            lo = parse_exact(rec.get("lo"), f"evaluated[{i}].lo")
            hi = parse_exact(rec.get("hi"), f"evaluated[{i}].hi")
            width = parse_exact(rec.get("width"), f"evaluated[{i}].width")
            if width != hi - lo or lo <= 0:
                fail("EVALUATED_PASS_INTERVAL:" + str(bid))
        evaluated_by_stage.setdefault(sid, []).append(rec)

    ledger = receipt.get("stage_ledger")
    stages = policy.get("stages")
    if not isinstance(ledger, list) or not isinstance(stages, list) or not ledger:
        fail("STAGE_LEDGER")
    if len(ledger) > len(stages):
        fail("TOO_MANY_STAGES")

    current = [parent]
    terminal_seen: set[str] = set()
    raw_total_eval = 0
    raw_total_boxes = 0
    raw_abort_count = 0
    ledger_stage_ids: set[str] = set()

    for i, led in enumerate(ledger):
        stage = stages[i]
        sid = stage.get("stage_id")
        if led.get("stage_id") != sid or led.get("op") != stage.get("op"):
            fail("STAGE_ORDER_OR_OP:" + str(i))
        ledger_stage_ids.add(sid)

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

        raw_stage = evaluated_by_stage.get(sid, [])
        if len(raw_stage) != expected_new:
            fail("RAW_STAGE_BOX_COUNT:" + str(i))
        raw_by_id = {rec["box_id"]: rec for rec in raw_stage}
        child_by_id = {c.box_id: c for c in children}
        if len(raw_by_id) != len(raw_stage):
            fail("RAW_STAGE_DUPLICATE_ID:" + str(i))
        if set(raw_by_id) != set(child_by_id):
            fail("RAW_STAGE_CHILD_SET:" + str(i))

        raw_stage_eval = 0
        raw_pass_count = 0
        raw_stage_abort = 0
        for bid, child in child_by_id.items():
            rec = raw_by_id[bid]
            if box_from_record(rec, "evaluated_stage." + bid) != child:
                fail("RAW_BOX_GEOMETRY:" + bid)
            raw_stage_eval += rec["evaluation_count"]
            if rec["status"] == "PASS_POS":
                raw_pass_count += 1
                if bid not in terminal_ids:
                    fail("RAW_PASS_NOT_TERMINAL:" + bid)
                terminal_rec = terminal_by_id[bid]
                for key in (
                    "r_lo", "r_hi", "lambda_lo", "lambda_hi", "lo", "hi", "width",
                    "evaluation_count", "status", "required_sign", "effective_evaluation_cap",
                ):
                    if rec.get(key) != terminal_rec.get(key):
                        fail("RAW_TERMINAL_MISMATCH:" + bid + ":" + key)
            else:
                raw_stage_abort += 1
                if not has_strict_descendant(bid, terminal_ids):
                    fail("RAW_ABORT_WITHOUT_DESCENDANT:" + bid)

        if raw_pass_count + raw_stage_abort != expected_new:
            fail("RAW_PASS_ABORT_COUNT:" + str(i))
        if raw_stage_eval != led.get("actual_stage_eval"):
            fail("RAW_STAGE_EVAL_LEDGER:" + str(i))
        if raw_stage_eval > declared:
            fail("RAW_STAGE_BUDGET:" + str(i))
        if raw_pass_count != led.get("pass_count"):
            fail("RAW_PASS_LEDGER:" + str(i))

        raw_total_eval += raw_stage_eval
        raw_total_boxes += len(raw_stage)
        raw_abort_count += raw_stage_abort

        next_current: list[Box] = []
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
        if raw_stage_abort != len(next_current):
            fail("RAW_ABORT_UNRESOLVED_COUNT:" + str(i))
        current = next_current

        if not current:
            if i != len(ledger) - 1:
                fail("NOT_FIRST_PASSING_STOP")
            break

    if set(evaluated_by_stage) != ledger_stage_ids:
        fail("RAW_UNDECLARED_STAGE_IDS")
    if current:
        fail("LEDGER_ENDED_WITH_UNRESOLVED")
    if terminal_seen != terminal_ids:
        fail("TERMINAL_SET_NOT_RECONSTRUCTED")
    if receipt.get("terminal_leaf_count") != len(terminal_ids):
        fail("TERMINAL_LEAF_COUNT")
    if raw_total_boxes != len(evaluated_records):
        fail("RAW_TOTAL_BOX_COUNT")
    if raw_total_eval != receipt.get("total_eval"):
        fail("TOTAL_EVAL")

    cover = exact_cover(parent, terminal_boxes)
    if receipt.get("cover_checks") != cover:
        fail("COVER_CHECK_MISMATCH")
    if not all(cover.values()):
        fail("COVER_NOT_EXACT")

    margin_id, margin = min(lo_by_id.items(), key=lambda kv: (kv[1], kv[0]))
    margin_text = f"{margin.numerator}/{margin.denominator}"
    if receipt.get("certified_cover_margin_exact") != margin_text:
        fail("MARGIN_EXACT")
    if receipt.get("certified_cover_margin_box_id") != margin_id:
        fail("MARGIN_BOX_ID")
    if receipt.get("cover_margin_is_true_minimum") is not False:
        fail("TRUE_MINIMUM_NONCLAIM")
    if receipt.get("all_terminal_lo_positive") is not True:
        fail("ALL_TERMINAL_POS_FLAG")
    if margin <= 0:
        fail("MARGIN_NONPOSITIVE")

    return {
        "evaluated_box_count": raw_total_boxes,
        "abort_count": raw_abort_count,
        "terminal_leaf_count": len(terminal_ids),
        "total_eval": raw_total_eval,
        "cover": cover,
        "margin_exact": margin_text,
        "margin_box_id": margin_id,
        "all_terminal_lo_positive": True,
        "union_equals_parent": True,
        "margin_positive": True,
    }
