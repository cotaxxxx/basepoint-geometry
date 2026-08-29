#!/usr/bin/env python3
"""Cell-0 positive control for PRODUCTION_HU_DOMAIN_CONTRACT_V1_2.

This runner is intentionally diagnostic/positive-control evidence only.
It implements the pinned finite stage list in hu_domain_v1_2_stage_policy.json:
BASE -> R x6 -> L32 -> R x2 -> L128, first-passing and unresolved-only.

No stage may be added at runtime. Any final unresolved leaf yields UNRESOLVED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

REL_RUNNER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics/hu_domain_v1_2_cell0_positive_control.py"
REL_POLICY = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics/hu_domain_v1_2_stage_policy.json"
REL_BT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
REL_V23 = REL_BT + "/dependencies/blocal_v23_source"


def fail(msg: str):
    raise SystemExit("STOP: " + msg)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(text: str) -> Fraction:
    return Fraction(text)


def fstr(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


@dataclass(frozen=True)
class Box:
    box_id: str
    r_lo: Fraction
    r_hi: Fraction
    lambda_lo: Fraction
    lambda_hi: Fraction
    generation: int
    parent_id: str | None

    def as_json(self) -> dict[str, Any]:
        return {
            "box_id": self.box_id,
            "parent_id": self.parent_id,
            "generation": self.generation,
            "r_lo": fstr(self.r_lo),
            "r_hi": fstr(self.r_hi),
            "lambda_lo": fstr(self.lambda_lo),
            "lambda_hi": fstr(self.lambda_hi),
        }


def split_r(box: Box) -> list[Box]:
    m = (box.r_lo + box.r_hi) / 2
    return [
        Box(box.box_id + "/r0", box.r_lo, m, box.lambda_lo, box.lambda_hi, box.generation + 1, box.box_id),
        Box(box.box_id + "/r1", m, box.r_hi, box.lambda_lo, box.lambda_hi, box.generation + 1, box.box_id),
    ]


def split_lambda_equal(box: Box, n: int, tag: str) -> list[Box]:
    width = (box.lambda_hi - box.lambda_lo) / n
    return [
        Box(
            f"{box.box_id}/{tag}{k}",
            box.r_lo,
            box.r_hi,
            box.lambda_lo + k * width,
            box.lambda_lo + (k + 1) * width,
            box.generation + 1,
            box.box_id,
        )
        for k in range(n)
    ]


def exact_cover_check(parent: Box, leaves: list[Box]) -> dict[str, bool]:
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
        and parent.lambda_lo <= b.lambda_lo < b.lambda_hi <= parent.lambda_hi
        for b in leaves
    )
    r_endpoints_exact = contained and min(b.r_lo for b in leaves) == parent.r_lo and max(b.r_hi for b in leaves) == parent.r_hi
    lambda_endpoints_exact = contained and min(b.lambda_lo for b in leaves) == parent.lambda_lo and max(b.lambda_hi for b in leaves) == parent.lambda_hi

    ys = sorted({parent.lambda_lo, parent.lambda_hi, *[b.lambda_lo for b in leaves], *[b.lambda_hi for b in leaves]})
    no_gaps = contained
    no_overlaps = contained
    if ys[0] != parent.lambda_lo or ys[-1] != parent.lambda_hi:
        no_gaps = False
    for y0, y1 in zip(ys, ys[1:]):
        if y0 == y1:
            continue
        active = sorted(
            [(b.r_lo, b.r_hi, b.box_id) for b in leaves if b.lambda_lo <= y0 and y1 <= b.lambda_hi],
            key=lambda x: (x[0], x[1], x[2]),
        )
        if not active:
            no_gaps = False
            continue
        cursor = parent.r_lo
        for x0, x1, _ in active:
            if x0 > cursor:
                no_gaps = False
            if x0 < cursor:
                no_overlaps = False
            if x0 == cursor:
                cursor = x1
            elif x0 < cursor:
                if x1 > cursor:
                    cursor = x1
            else:
                cursor = x1
        if cursor != parent.r_hi:
            no_gaps = False

    union_equals_parent = r_endpoints_exact and lambda_endpoints_exact and no_gaps and no_overlaps
    return {
        "r_endpoints_exact": r_endpoints_exact,
        "lambda_endpoints_exact": lambda_endpoints_exact,
        "no_gaps": no_gaps,
        "no_interior_overlaps": no_overlaps,
        "union_equals_parent": union_equals_parent,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--policy", type=Path)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()

    repo = ns.repo.resolve()
    runner_path = repo / REL_RUNNER
    policy_path = (ns.policy.resolve() if ns.policy else repo / REL_POLICY)
    if not runner_path.is_file():
        fail("runner must execute from committed diagnostics path")
    if not policy_path.is_file():
        fail("missing stage policy JSON")

    policy_raw = policy_path.read_bytes()
    policy = json.loads(policy_raw)
    print("EVIDENCE_CLASS=" + policy["evidence_class"])
    print("BINDING_USE_AUTHORIZED=" + str(policy["binding_use_authorized"]).upper())
    print("CONTRACT_ID=" + policy["contract_id"])
    print("POLICY_SHA256=" + hashlib.sha256(policy_raw).hexdigest())
    print("RUNNER_SHA256=" + sha256_file(runner_path))

    baseline = policy["source_baseline_commit"]
    head = git(repo, "rev-parse", "HEAD")
    print("SOURCE_BASELINE_COMMIT=" + baseline)
    print("EXECUTION_HEAD=" + head)
    try:
        subprocess.check_call(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", baseline, head],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        fail("source baseline is not ancestor of execution HEAD")

    changed = [x for x in git(repo, "diff", "--name-only", f"{baseline}..{head}").splitlines() if x]
    allowed = sorted(policy["allowed_changes_after_source_baseline"])
    if sorted(changed) != allowed:
        fail("post-baseline changed-path set mismatch: " + ",".join(changed))
    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE dirty")
    print("SOURCE_TREE_PRE=CLEAN")
    print("POST_BASELINE_CHANGED_PATHS_EXACT=TRUE")

    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        fail("launch with PYTHONDONTWRITEBYTECODE=1")
    if not sys.dont_write_bytecode:
        fail("sys.dont_write_bytecode is false")
    print("BYTECODE_SUPPRESSION=TRUE")

    bt = repo / REL_BT
    v23 = repo / REL_V23
    sys.path.insert(0, str(v23))
    sys.path.insert(1, str(bt))

    import flint
    from flint import arb, acb, fmpq, ctx
    import blocal_v22_model as model
    import blocal_arb_adapter as adapter
    import blocal_v23_boundary as route
    import calibration_runner

    pyver = platform.python_version()
    pyflint = getattr(flint, "__version__", "UNKNOWN")
    flintver = getattr(flint, "__FLINT_VERSION__", "UNKNOWN")
    print("PYTHON_VERSION=" + pyver)
    print("PYTHON_FLINT_VERSION=" + str(pyflint))
    print("FLINT_VERSION=" + str(flintver))
    expected_tc = policy["toolchain"]
    if pyver != expected_tc["python"]:
        fail("Python version mismatch")
    if str(pyflint) != expected_tc["python_flint"]:
        fail("python-flint version mismatch")
    if str(flintver) != expected_tc["flint"]:
        fail("FLINT version mismatch")

    if policy["quantity"] != "H_U" or policy["required_sign"] != "POS":
        fail("quantity/sign policy mismatch")
    cap = int(policy["per_box_cap"])
    dps = int(policy["dps"])
    if cap != 24000 or dps != 60:
        fail("cap/dps policy mismatch")
    ctx.dps = dps

    raw_kernel, kernel_path = calibration_runner.load_production_kernel()
    bcfg = json.loads((v23 / "config.blocal-v2.2-run.json").read_text())
    frag = json.loads((v23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
    bcfg["route_policies"].update(frag["route_policies"])
    print("PRODUCTION_KERNEL_PATH=" + kernel_path.relative_to(repo).as_posix())
    print("PRODUCTION_KERNEL_SHA256=" + sha256_file(kernel_path))
    print("V23_BOUNDARY_SHA256=" + sha256_file(v23 / "blocal_v23_boundary.py"))
    print("V22_BOUNDARY_SHA256=" + sha256_file(v23 / "blocal_v22_boundary.py"))
    print("BLOCAL_CONFIG_SHA256=" + sha256_file(v23 / "config.blocal-v2.2-run.json"))
    print("H_U_API=blocal_v23_boundary.base.enclose_hu")
    print("REQUIRED_SIGN=POS")
    print("DPS=" + str(dps))
    print("PER_BOX_CAP=" + str(cap))

    p = policy["parent"]
    parent = Box(
        "CELL0",
        frac(p["r_lo"]),
        frac(p["r_hi"]),
        frac(p["lambda_lo"]),
        frac(p["lambda_hi"]),
        0,
        None,
    )
    if not (parent.r_lo < parent.r_hi and parent.lambda_lo < parent.lambda_hi):
        fail("invalid parent geometry")
    print("PARENT_R_LO=" + fstr(parent.r_lo))
    print("PARENT_R_HI=" + fstr(parent.r_hi))
    print("PARENT_LAMBDA_LO=" + fstr(parent.lambda_lo))
    print("PARENT_LAMBDA_HI=" + fstr(parent.lambda_hi))

    terminal: dict[str, dict[str, Any]] = {}
    stage_ledger: list[dict[str, Any]] = []
    total_eval = 0

    def evaluate_box(box: Box) -> dict[str, Any]:
        nonlocal total_eval
        u0 = Fraction(1) - box.r_hi
        u1 = Fraction(1) - box.r_lo
        s0 = box.lambda_lo - model.LAMBDA_PLUS
        s1 = box.lambda_hi - model.LAMBDA_PLUS
        rec = box.as_json()
        rec.update({
            "status": "ABORT",
            "required_sign": "POS",
            "effective_evaluation_cap": cap,
            "lo": None,
            "hi": None,
            "width": None,
            "evaluation_count": 0,
            "proof_id": None,
            "abort_reason": None,
        })
        try:
            iv, proof = route.base.enclose_hu(
                raw_kernel, adapter, acb, arb, fmpq, bcfg,
                u0, u1, s0, s1,
                required_sign="POS",
                accept=None,
                evaluation_cap=cap,
            )
            lo, hi = model.interval_fractions(iv, box.box_id)
            ev = int(proof["evaluation_count"])
            total_eval += ev
            rec.update({
                "status": "PASS_POS" if lo > 0 else "UNRESOLVED",
                "lo": fstr(lo),
                "hi": fstr(hi),
                "width": fstr(hi - lo),
                "evaluation_count": ev,
                "proof_id": proof.get("proof_id"),
                "complete_closed_cover": bool(proof.get("complete_closed_cover")),
                "route_id": proof.get("route_id"),
            })
            if not proof.get("complete_closed_cover"):
                rec["status"] = "ABORT"
                rec["abort_reason"] = "INCOMPLETE_ANGULAR_COVER"
        except route.base.EnclosureFailure as exc:
            ev = int(exc.evaluations)
            total_eval += ev
            rec["evaluation_count"] = ev
            rec["abort_reason"] = exc.reason
        except Exception:
            raise
        print("BOX=" + box.box_id)
        print("R_LO=" + fstr(box.r_lo) + " R_HI=" + fstr(box.r_hi))
        print("LAMBDA_LO=" + fstr(box.lambda_lo) + " LAMBDA_HI=" + fstr(box.lambda_hi))
        print("STATUS=" + rec["status"])
        print("LO=" + str(rec["lo"]) + " HI=" + str(rec["hi"]) + " WIDTH=" + str(rec["width"]))
        print("EVAL=" + str(rec["evaluation_count"]))
        if rec["abort_reason"]:
            print("ABORT_REASON=" + rec["abort_reason"])
        return rec

    stages = policy["stages"]
    if [s["stage_id"] for s in stages] != [
        "S0_BASE","S1_R1","S2_R2","S3_R3","S4_R4","S5_R5","S6_R6",
        "S7_L32","S8_R_POST_L32_1","S9_R_POST_L32_2","S10_L128"
    ]:
        fail("stage list does not match V1.2 pinned release candidate")

    current_unresolved: list[Box] = []
    for stage_index, stage in enumerate(stages):
        sid = stage["stage_id"]
        op = stage["op"]

        if stage_index == 0:
            parents = [parent]
            children = [parent]
            unresolved_parent_count = 1
        else:
            parents = list(current_unresolved)
            unresolved_parent_count = len(parents)
            if op == "R_BISECT":
                children = [c for b in parents for c in split_r(b)]
            elif op == "LAMBDA_SUBDIVIDE":
                if int(stage["division"]) != 32:
                    fail("L32 division mismatch")
                children = [c for b in parents for c in split_lambda_equal(b, 32, "l32_")]
            elif op == "LAMBDA_REFINE_BY_4":
                children = [c for b in parents for c in split_lambda_equal(b, 4, "l4_")]
            else:
                fail("undeclared stage op " + op)

        factor = int(stage["child_factor"])
        expected_new = 1 if stage_index == 0 else factor * unresolved_parent_count
        if len(children) != expected_new:
            fail(f"{sid} MAX_NEW_BOXES rule mismatch")

        declared_stage_max_eval = len(children) * cap
        print("STAGE=" + sid)
        print("UNRESOLVED_PARENT_COUNT=" + str(unresolved_parent_count))
        print("NEW_CHILD_COUNT=" + str(len(children)))
        print("PER_BOX_CAP=" + str(cap))
        print("DECLARED_STAGE_MAX_EVAL=" + str(declared_stage_max_eval))

        stage_eval_before = total_eval
        next_unresolved: list[Box] = []
        passed = 0
        for child in children:
            rec = evaluate_box(child)
            if rec["status"] == "PASS_POS":
                terminal[child.box_id] = rec
                passed += 1
            else:
                next_unresolved.append(child)

        used = total_eval - stage_eval_before
        ledger = {
            "stage_id": sid,
            "op": op,
            "unresolved_parent_count": unresolved_parent_count,
            "new_child_count": len(children),
            "per_box_cap": cap,
            "declared_stage_max_eval": declared_stage_max_eval,
            "actual_stage_eval": used,
            "pass_count": passed,
            "unresolved_count_after_stage": len(next_unresolved),
        }
        stage_ledger.append(ledger)
        print("ACTUAL_STAGE_EVAL=" + str(used))
        print("PASS_COUNT=" + str(passed))
        print("UNRESOLVED_COUNT_AFTER_STAGE=" + str(len(next_unresolved)))

        current_unresolved = next_unresolved
        if not current_unresolved:
            print("FIRST_PASSING_STAGE=" + sid)
            break

    final_unresolved = current_unresolved
    terminal_boxes = [
        Box(
            rec["box_id"],
            frac(rec["r_lo"]),
            frac(rec["r_hi"]),
            frac(rec["lambda_lo"]),
            frac(rec["lambda_hi"]),
            int(rec["generation"]),
            rec["parent_id"],
        )
        for rec in terminal.values()
    ]

    cover = exact_cover_check(parent, terminal_boxes) if not final_unresolved else {
        "r_endpoints_exact": False,
        "lambda_endpoints_exact": False,
        "no_gaps": False,
        "no_interior_overlaps": False,
        "union_equals_parent": False,
    }

    lo_pairs = [(frac(rec["lo"]), bid) for bid, rec in terminal.items() if rec.get("lo") is not None]
    margin = min(lo_pairs) if lo_pairs else None
    all_terminal_pos = bool(terminal) and all(frac(rec["lo"]) > 0 for rec in terminal.values())
    positive_control_pass = (
        not final_unresolved
        and all_terminal_pos
        and cover["r_endpoints_exact"]
        and cover["lambda_endpoints_exact"]
        and cover["no_gaps"]
        and cover["no_interior_overlaps"]
        and cover["union_equals_parent"]
        and margin is not None
        and margin[0] > 0
    )
    verdict = "POSITIVE_CONTROL_PASS" if positive_control_pass else "UNRESOLVED"

    print("TERMINAL_LEAF_COUNT=" + str(len(terminal)))
    print("FINAL_UNRESOLVED_COUNT=" + str(len(final_unresolved)))
    print("TOTAL_EVAL=" + str(total_eval))
    print("R_ENDPOINTS_EXACT=" + str(cover["r_endpoints_exact"]).upper())
    print("LAMBDA_ENDPOINTS_EXACT=" + str(cover["lambda_endpoints_exact"]).upper())
    print("NO_GAPS=" + str(cover["no_gaps"]).upper())
    print("NO_INTERIOR_OVERLAPS=" + str(cover["no_interior_overlaps"]).upper())
    print("UNION_EQUALS_PARENT=" + str(cover["union_equals_parent"]).upper())
    if margin is None:
        print("CERTIFIED_COVER_MARGIN_EXACT=NA")
        print("CERTIFIED_COVER_MARGIN_BOX_ID=NA")
    else:
        print("CERTIFIED_COVER_MARGIN_EXACT=" + fstr(margin[0]))
        print("CERTIFIED_COVER_MARGIN_BOX_ID=" + margin[1])
    print("COVER_MARGIN_IS_TRUE_MINIMUM=NO")
    print("VERDICT=" + verdict)

    receipt = {
        "schema": "production-hu-domain-v1.2-cell0-positive-control-receipt-v1",
        "contract_id": policy["contract_id"],
        "evidence_class": policy["evidence_class"],
        "binding_use_authorized": policy["binding_use_authorized"],
        "policy_sha256": hashlib.sha256(policy_raw).hexdigest(),
        "runner_sha256": sha256_file(runner_path),
        "source_baseline_commit": baseline,
        "execution_head": head,
        "quantity": "H_U",
        "required_sign": "POS",
        "dps": dps,
        "per_box_cap": cap,
        "parent": parent.as_json(),
        "stage_ledger": stage_ledger,
        "terminal_leaves": sorted(terminal.values(), key=lambda r: r["box_id"]),
        "final_unresolved": [b.as_json() for b in final_unresolved],
        "terminal_leaf_count": len(terminal),
        "final_unresolved_count": len(final_unresolved),
        "total_eval": total_eval,
        "cover_checks": cover,
        "all_terminal_lo_positive": all_terminal_pos,
        "certified_cover_margin_exact": None if margin is None else fstr(margin[0]),
        "certified_cover_margin_box_id": None if margin is None else margin[1],
        "cover_margin_is_true_minimum": False,
        "verdict": verdict,
    }

    if git(repo, "rev-parse", "HEAD") != head:
        fail("HEAD changed during run")
    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_POST dirty")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")

    ns.out_json.parent.mkdir(parents=True, exist_ok=True)
    ns.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("RESULT_JSON=" + str(ns.out_json))
    print("RESULT_JSON_SHA256=" + sha256_file(ns.out_json))
    return 0 if positive_control_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
