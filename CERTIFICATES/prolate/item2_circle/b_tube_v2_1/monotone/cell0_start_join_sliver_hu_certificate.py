#!/usr/bin/env python3
"""Cell-0 start-join sliver H_U certificate for MONOTONE_TUBE_V1.1.

Primary evaluation: exactly one H_U enclosure call on
    [32763/32768, 8191/8192] x {lambda_start}.

If that primary call is unresolved, only unresolved r-leaves may be bisected,
with the finite predeclared ladder R1..R6. No lambda refinement is permitted.
The certificate is fail-closed and pins the promoted cell-0 H_U component and
Component-1 geometry receipt. Assembly is a separate proof step.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

RELEASE_SHA = "6d705c6fbf37ae77d35232a40842692a3e92713e"
RELEASE_CONTRACT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/diagnostics/PRODUCTION_HU_DOMAIN_CONTRACT_V1_2_RELEASE.json"
F_JOINT_C1_JUDGE = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/F_JOINT_C1_LEMMA_V1_JUDGE_SIGNATURE.json"
HU_PROMOTION = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/CELL0_HU_PRODUCTION_PROMOTION_V1.json"
COMPONENT1 = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/CELL0_COMPONENT1_TUBE_GEOMETRY_V1.json"
REL_RUNNER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/cell0_start_join_sliver_hu_certificate.py"
REL_BT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
REL_V23 = REL_BT + "/dependencies/blocal_v23_source"

EXPECTED_POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
EXPECTED_KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
EXPECTED_COMPONENT1_SHA256 = "f60c22cbc1d4a45e5593a64e64194f7e3dbc97df69e1547aca092d2d93b7911f"
EXPECTED_HU_PROMOTION_SHA256 = "ea688d25c1d6000c6708249cc99036284721e10daa9e0bb27c80af9c3e3147ad"
EXPECTED_PRODUCTION_RECEIPT_SHA256 = "5f3feb5ec12aa09d40eb906d6023efa51676327b0b6af3f51d3c5439a765d39b"
EXPECTED_PRODUCTION_CHECKER_SHA256 = "9d8ad733677826411635fd266cc5ad052aca8f9aaa6e9c3f65c16a4ff808dbaa"

CELL0_R_LO = Fraction(37140511944960794174557707, 38685626227668133590597632)
CELL0_R_HI = Fraction(32763, 32768)
A0_R_HI = Fraction(8191, 8192)
LAMBDA_START = Fraction(3307749, 1600000)
SLIVER_R_LO = CELL0_R_HI
SLIVER_R_HI = A0_R_HI
HULL_R_LO = CELL0_R_LO
HULL_R_HI = A0_R_HI
CAP = 24000
DPS = 60
MAX_R_BISECTION_DEPTH = 6
STAGE_SEQUENCE = ["S0_BASE"] + [f"S{i}_R{i}" for i in range(1, MAX_R_BISECTION_DEPTH + 1)]


def fail(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


def bisect(box: tuple[Fraction, Fraction]) -> list[tuple[Fraction, Fraction]]:
    lo, hi = box
    mid = (lo + hi) / 2
    return [(lo, mid), (mid, hi)]


def exact_geometry_gate() -> None:
    if not (CELL0_R_LO < CELL0_R_HI < A0_R_HI < 1):
        fail("START_JOIN_GEOMETRY_ORDER")
    if SLIVER_R_LO != CELL0_R_HI or SLIVER_R_HI != A0_R_HI:
        fail("SLIVER_ENDPOINT_IDENTITY")
    # TUBE=[CELL0_R_LO,CELL0_R_HI], SLIVER=[CELL0_R_HI,A0_R_HI].
    # Exact closed-interval composition therefore has singleton intersection and hull union.
    if max(CELL0_R_LO, SLIVER_R_LO) != min(CELL0_R_HI, SLIVER_R_HI):
        fail("TUBE_SLIVER_INTERSECTION_NOT_SINGLETON")
    if min(CELL0_R_LO, SLIVER_R_LO) != HULL_R_LO:
        fail("TUBE_SLIVER_UNION_LO")
    if max(CELL0_R_HI, SLIVER_R_HI) != HULL_R_HI:
        fail("TUBE_SLIVER_UNION_HI")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()

    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1" or not sys.dont_write_bytecode:
        fail("launch with PYTHONDONTWRITEBYTECODE=1")
    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE_DIRTY")
    head = git(repo, "rev-parse", "HEAD")
    subprocess.check_call(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", RELEASE_SHA, head],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    release = json.loads((repo / RELEASE_CONTRACT).read_text())
    if release.get("release_status") != "RELEASED_AFTER_POSITIVE_CONTROL_PASS":
        fail("HU_RELEASE_STATUS")
    if release.get("pins", {}).get("stage_policy_sha256") != EXPECTED_POLICY_SHA256:
        fail("HU_POLICY_SHA")

    if sha256_file(repo / COMPONENT1) != EXPECTED_COMPONENT1_SHA256:
        fail("COMPONENT1_SHA")
    component1 = json.loads((repo / COMPONENT1).read_text())
    if component1.get("rectangle_identity_role") != "LOAD_BEARING_SINGLE_SOURCE":
        fail("COMPONENT1_RECTANGLE_ROLE")

    if sha256_file(repo / HU_PROMOTION) != EXPECTED_HU_PROMOTION_SHA256:
        fail("HU_PROMOTION_SHA")
    promotion = json.loads((repo / HU_PROMOTION).read_text())
    if promotion.get("judge_receipt") != "CELL0_HU_PRODUCTION_PROMOTION_V1":
        fail("HU_PROMOTION_ID")
    if promotion.get("judge_verdict") != "PASS":
        fail("HU_PROMOTION_VERDICT")
    if promotion.get("signer_role") != "HUMAN_JUDGE":
        fail("HU_PROMOTION_SIGNER_ROLE")
    if promotion.get("production_receipt_sha256") != EXPECTED_PRODUCTION_RECEIPT_SHA256:
        fail("HU_PRODUCTION_RECEIPT_SHA")
    if promotion.get("component1_geometry_receipt_sha256") != EXPECTED_COMPONENT1_SHA256:
        fail("HU_PROMOTION_COMPONENT1_SHA")
    if promotion.get("production_checker_sha256") != EXPECTED_PRODUCTION_CHECKER_SHA256:
        fail("HU_PROMOTION_CHECKER_SHA")
    ni = promotion.get("narrow_interface", {})
    if ni.get("all_terminal_lo_positive") is not True or ni.get("union_equals_parent") is not True:
        fail("HU_PROMOTION_NARROW_INTERFACE")
    try:
        if Fraction(ni.get("certified_cover_margin_exact", "0/1")) <= 0:
            fail("HU_PROMOTION_MARGIN_NONPOSITIVE")
    except Exception:
        fail("HU_PROMOTION_MARGIN_BAD")

    joint = json.loads((repo / F_JOINT_C1_JUDGE).read_text())
    if joint.get("lemma_id") != "F_JOINT_C1" or joint.get("judge_signature_status") != "APPROVED":
        fail("F_JOINT_C1_NOT_APPROVED")
    if joint.get("binding_use_authorized") is not True:
        fail("F_JOINT_C1_NOT_BINDING")

    exact_geometry_gate()

    bt = repo / REL_BT
    v23 = repo / REL_V23
    sys.path.insert(0, str(v23))
    sys.path.insert(1, str(bt))

    import flint
    from flint import acb, arb, fmpq, ctx
    import blocal_v22_model as model
    import blocal_arb_adapter as adapter
    import blocal_v23_boundary as route
    import calibration_runner

    if platform.python_version() != "3.13.14":
        fail("PYTHON_VERSION")
    if str(getattr(flint, "__version__", "UNKNOWN")) != "0.9.0":
        fail("PYTHON_FLINT_VERSION")
    if str(getattr(flint, "__FLINT_VERSION__", "UNKNOWN")) != "3.6.0":
        fail("FLINT_VERSION")
    ctx.dps = DPS

    raw_kernel, kernel_path = calibration_runner.load_production_kernel()
    if sha256_file(kernel_path) != EXPECTED_KERNEL_SHA256:
        fail("PRODUCTION_KERNEL_SHA")
    bcfg = json.loads((v23 / "config.blocal-v2.2-run.json").read_text())
    frag = json.loads((v23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
    bcfg["route_policies"].update(frag["route_policies"])
    s = LAMBDA_START - model.LAMBDA_PLUS

    def evaluate(r_lo: Fraction, r_hi: Fraction, box_id: str) -> dict:
        u0 = Fraction(1) - r_hi
        u1 = Fraction(1) - r_lo
        try:
            iv, proof = route.base.enclose_hu(
                raw_kernel, adapter, acb, arb, fmpq, bcfg,
                u0, u1, s, s,
                required_sign="POS",
                accept=None,
                evaluation_cap=CAP,
            )
            lo, hi = model.interval_fractions(iv, box_id)
            evaluations = int(proof["evaluation_count"])
            if evaluations > CAP:
                fail("EVALUATION_CAP_EXCEEDED")
            if not proof.get("complete_closed_cover"):
                status = "ABORT_INCOMPLETE_COVER"
                reason = "INCOMPLETE_ANGULAR_COVER"
            elif lo > 0:
                status = "PASS_POS"
                reason = None
            else:
                status = "UNRESOLVED_SIGN"
                reason = "NONPOSITIVE_LOWER_BOUND"
            return {
                "box_id": box_id, "r_lo": fstr(r_lo), "r_hi": fstr(r_hi),
                "status": status, "reason": reason, "lo": fstr(lo), "hi": fstr(hi),
                "evaluation_count": evaluations,
                "complete_closed_cover": bool(proof.get("complete_closed_cover")),
                "proof_id": proof.get("proof_id"),
            }
        except route.base.EnclosureFailure as exc:
            evaluations = int(exc.evaluations)
            if evaluations > CAP:
                fail("EVALUATION_CAP_EXCEEDED")
            if exc.reason == "ANGULAR_EVALUATION_BUDGET":
                status = "ABORT_BUDGET"
            elif exc.reason == "INCOMPLETE_ANGULAR_COVER":
                status = "ABORT_INCOMPLETE_COVER"
            else:
                fail("HARD_ENCLOSURE_FAILURE:" + str(exc.reason))
            return {
                "box_id": box_id, "r_lo": fstr(r_lo), "r_hi": fstr(r_hi),
                "status": status, "reason": exc.reason, "lo": None, "hi": None,
                "evaluation_count": evaluations,
                "complete_closed_cover": False, "proof_id": None,
            }

    evaluated: list[dict] = []
    terminal: list[dict] = []
    unresolved: list[tuple[Fraction, Fraction, str]] = [(SLIVER_R_LO, SLIVER_R_HI, "S0_BASE/r0")]
    first_passing_stage = None

    for depth, stage_id in enumerate(STAGE_SEQUENCE):
        current = unresolved
        unresolved = []
        if depth > 0:
            refined: list[tuple[Fraction, Fraction, str]] = []
            for r_lo, r_hi, parent_id in current:
                for j, (a, b) in enumerate(bisect((r_lo, r_hi))):
                    refined.append((a, b, parent_id + f"/{stage_id.lower()}_{j}"))
            current = refined
        for r_lo, r_hi, box_id in current:
            row = evaluate(r_lo, r_hi, box_id)
            row["stage_id"] = stage_id
            evaluated.append(row)
            if row["status"] == "PASS_POS":
                terminal.append(row)
            else:
                unresolved.append((r_lo, r_hi, box_id))
        if not unresolved:
            first_passing_stage = stage_id
            break

    if unresolved:
        verdict = "UNRESOLVED"
        sliver_pass = False
    else:
        # Exact terminal closed cover of the sliver; interiors may not overlap.
        ordered = sorted(terminal, key=lambda x: Fraction(x["r_lo"]))
        if not ordered or Fraction(ordered[0]["r_lo"]) != SLIVER_R_LO or Fraction(ordered[-1]["r_hi"]) != SLIVER_R_HI:
            fail("SLIVER_COVER_ENDPOINTS")
        for a, b in zip(ordered, ordered[1:]):
            if Fraction(a["r_hi"]) != Fraction(b["r_lo"]):
                fail("SLIVER_COVER_GAP_OR_OVERLAP")
        if any(Fraction(x["lo"]) <= 0 for x in terminal):
            fail("TERMINAL_NONPOSITIVE_LO")
        verdict = "START_JOIN_SLIVER_HU_PASS"
        sliver_pass = True

    margin = None if not terminal else min(Fraction(x["lo"]) for x in terminal)
    total_eval = sum(int(x["evaluation_count"]) for x in evaluated)

    post_head = git(repo, "rev-parse", "HEAD")
    post_clean = not bool(git(repo, "status", "--porcelain"))
    if post_head != head:
        fail("HEAD_CHANGED_DURING_RUN")
    if not post_clean:
        fail("SOURCE_TREE_POST_DIRTY")

    receipt = {
        "schema": "monotone-tube-v1.1-cell0-start-join-sliver-hu-v1",
        "contract": "MONOTONE_TUBE_V1_1",
        "component": "START_JOIN_SLIVER_HU_CERTIFICATE",
        "evidence_class": "BINDING_COMPONENT_CANDIDATE",
        "binding_use_authorized": False,
        "component1_geometry_receipt_sha256": EXPECTED_COMPONENT1_SHA256,
        "cell0_hu_production_receipt_sha256": EXPECTED_PRODUCTION_RECEIPT_SHA256,
        "cell0_hu_promotion_receipt_sha256": EXPECTED_HU_PROMOTION_SHA256,
        "composition_requires": "CELL0_HU_PRODUCTION_PROMOTION_V1_WITH_SAME_COMPONENT1_SHA",
        "geometry": {
            "tube": {"r_lo": fstr(CELL0_R_LO), "r_hi": fstr(CELL0_R_HI)},
            "sliver": {"r_lo": fstr(SLIVER_R_LO), "r_hi": fstr(SLIVER_R_HI)},
            "hull": {"r_lo": fstr(HULL_R_LO), "r_hi": fstr(HULL_R_HI)},
            "lambda_start": fstr(LAMBDA_START),
            "tube_union_sliver_equals_hull": True,
            "tube_intersection_sliver": {"r": fstr(CELL0_R_HI)},
        },
        "quantity": "H_U",
        "required_sign": "POS",
        "dps": DPS,
        "per_box_cap": CAP,
        "primary_call_count": 1,
        "fallback_policy": {
            "enabled_only_if_primary_unresolved": True,
            "axis": "R_ONLY",
            "exact_bisection": True,
            "max_depth": MAX_R_BISECTION_DEPTH,
            "stage_sequence": STAGE_SEQUENCE,
            "refine_only_unresolved": True,
            "lambda_refinement": "FORBIDDEN",
        },
        "first_passing_stage": first_passing_stage,
        "evaluated_boxes": evaluated,
        "terminal_box_count": len(terminal),
        "total_evaluation_count": total_eval,
        "sliver_lo": None if margin is None else fstr(margin),
        "all_terminal_lo_positive": sliver_pass,
        "sliver_union_equals_parent": sliver_pass,
        "union_monotonicity_claim": "DEFERRED_TO_ASSEMBLY_COMPOSITION",
        "source_tree_pre_clean": True,
        "source_tree_post_clean": post_clean,
        "head_unchanged_during_run": True,
        "verdict": verdict,
        "runner_sha256": sha256_file(repo / REL_RUNNER),
        "execution_head": head,
    }
    ns.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    print("CONTRACT=MONOTONE_TUBE_V1_1")
    print("COMPONENT=START_JOIN_SLIVER_HU_CERTIFICATE")
    print("COMPONENT1_GEOMETRY_RECEIPT_SHA256=" + EXPECTED_COMPONENT1_SHA256)
    print("CELL0_HU_PROMOTION_RECEIPT_SHA256=" + EXPECTED_HU_PROMOTION_SHA256)
    print("TUBE_UNION_SLIVER_EQUALS_HULL=TRUE")
    print("TUBE_INTERSECTION_SLIVER={" + fstr(CELL0_R_HI) + "}")
    print("SLIVER_R_LO=" + fstr(SLIVER_R_LO))
    print("SLIVER_R_HI=" + fstr(SLIVER_R_HI))
    print("LAMBDA_START=" + fstr(LAMBDA_START))
    print("PRIMARY_CALL_COUNT=1")
    print("FIRST_PASSING_STAGE=" + str(first_passing_stage))
    print("TERMINAL_BOX_COUNT=" + str(len(terminal)))
    print("TOTAL_EVAL=" + str(total_eval))
    print("SLIVER_LO=" + str(receipt["sliver_lo"]))
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=" + verdict)
    return 0 if sliver_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
