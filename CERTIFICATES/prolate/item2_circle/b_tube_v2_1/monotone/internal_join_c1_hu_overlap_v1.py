#!/usr/bin/env python3
"""Produce a fail-closed internal monotone JOIN C1/H_U overlap receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

SCHEMA = "monotone-tube-v1.1-internal-join-c1-hu-overlap-v1"
CONTRACT = "MONOTONE_TUBE_V1_1"
COMPONENT = "INTERNAL_JOIN_C1_HU_OVERLAP_CERTIFICATE"
CHECKER_SHA256 = "b780df402758499d008c4341d00377f80ed29b91c895edc2abed604044f3d061"


def fail(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        fail("NONREGULAR_INPUT:" + str(path))
    try:
        obj = json.loads(path.read_text())
    except Exception as exc:
        fail("BAD_JSON:" + str(path) + ":" + str(exc))
    if not isinstance(obj, dict):
        fail("TOP_LEVEL_NOT_OBJECT:" + str(path))
    return obj


def fstr(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def section(q: Fraction, rho: Fraction) -> tuple[Fraction, Fraction]:
    if rho <= 0:
        fail("NONPOSITIVE_RADIUS")
    return q - rho, q + rho


def promotion_gate(obj: dict, cell: str, kind: str, geometry_sha: str) -> None:
    if obj.get("judge_verdict") != "PASS":
        fail(kind + "_PROMOTION_VERDICT")
    if obj.get("signer_role") != "HUMAN_JUDGE":
        fail(kind + "_PROMOTION_SIGNER")
    if obj.get("not_a_tube_theorem_promotion") is not True:
        fail(kind + "_PROMOTION_SCOPE")
    effect = obj.get("promotion_effect", {})
    if effect.get("binding_use_authorized") is not True:
        fail(kind + "_PROMOTION_NOT_BINDING")
    if effect.get("authorized_component") != f"{cell}_{kind}_COMPONENT_ONLY":
        fail(kind + "_AUTHORIZED_COMPONENT")
    if obj.get("component1_geometry_receipt_sha256") != geometry_sha:
        fail(kind + "_GEOMETRY_SHA")
    cross = obj.get("cross_component_identity_requirement", {})
    if cross.get("component1_geometry_receipt_sha256") != geometry_sha:
        fail(kind + "_CROSS_COMPONENT_SHA")
    if cross.get("assembly_must_fail_closed_on_sha_mismatch") is not True:
        fail(kind + "_FAIL_CLOSED")
    if "JOIN" not in cross.get("required_for", []):
        fail(kind + "_JOIN_REQUIREMENT")
    if kind == "HU":
        ni = obj.get("narrow_interface", {})
        if ni.get("all_terminal_lo_positive") is not True:
            fail("HU_LO_NOT_POSITIVE")
        if ni.get("union_equals_parent") is not True:
            fail("HU_PARENT_NOT_COVERED")
        if Fraction(ni.get("certified_cover_margin_exact", "0/1")) <= 0:
            fail("HU_MARGIN_NONPOSITIVE")
    else:
        if obj.get("producer_verdict") != "PASS_BINDING_CANDIDATE":
            fail("F_LAMBDA_PRODUCER")
        if obj.get("checker_verdict") != "PASS_BINDING_CANDIDATE_CHECK":
            fail("F_LAMBDA_CHECKER")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--left-cell", type=int, required=True)
    ap.add_argument("--right-cell", type=int, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()
    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1" or not sys.dont_write_bytecode:
        fail("LAUNCH_WITH_PYTHONDONTWRITEBYTECODE_1")
    if ns.right_cell != ns.left_cell + 1:
        fail("NONADJACENT_CELLS")
    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE_DIRTY")
    head = git(repo, "rev-parse", "HEAD")

    left_id, right_id = f"CELL{ns.left_cell}", f"CELL{ns.right_cell}"
    mon = repo / "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone"
    rels = {
        "left_geometry": f"{left_id}_COMPONENT1_TUBE_GEOMETRY_V1.json",
        "right_geometry": f"{right_id}_COMPONENT1_TUBE_GEOMETRY_V1.json",
        "left_hu_promotion": f"{left_id}_HU_PRODUCTION_PROMOTION_V1.json",
        "right_hu_promotion": f"{right_id}_HU_PRODUCTION_PROMOTION_V1.json",
        "left_f_lambda_promotion": f"{left_id}_F_LAMBDA_PRODUCTION_PROMOTION_V1.json",
        "right_f_lambda_promotion": f"{right_id}_F_LAMBDA_PRODUCTION_PROMOTION_V1.json",
        "f_joint_c1_lemma": "F_JOINT_C1_LEMMA_V1.md",
        "f_joint_c1_judge": "F_JOINT_C1_LEMMA_V1_JUDGE_SIGNATURE.json",
        "producer": "internal_join_c1_hu_overlap_v1.py",
        "checker": "internal_join_c1_hu_overlap_verify_v1.py",
    }
    pins = {key + "_sha256": sha(mon / name) for key, name in rels.items()}
    if pins["checker_sha256"] != CHECKER_SHA256:
        fail("CHECKER_SHA")

    lg, rg = load(mon / rels["left_geometry"]), load(mon / rels["right_geometry"])
    if lg.get("cell_id") != left_id or rg.get("cell_id") != right_id:
        fail("GEOMETRY_CELL_ID")
    if lg.get("candidate_inputs", {}).get("cell_index") != ns.left_cell:
        fail("LEFT_CELL_INDEX")
    if rg.get("candidate_inputs", {}).get("cell_index") != ns.right_cell:
        fail("RIGHT_CELL_INDEX")
    if lg.get("rectangle_identity_role") != "LOAD_BEARING_SINGLE_SOURCE":
        fail("LEFT_GEOMETRY_ROLE")
    if rg.get("rectangle_identity_role") != "LOAD_BEARING_SINGLE_SOURCE":
        fail("RIGHT_GEOMETRY_ROLE")

    promotion_gate(load(mon / rels["left_hu_promotion"]), left_id, "HU", pins["left_geometry_sha256"])
    promotion_gate(load(mon / rels["right_hu_promotion"]), right_id, "HU", pins["right_geometry_sha256"])
    promotion_gate(load(mon / rels["left_f_lambda_promotion"]), left_id, "F_LAMBDA", pins["left_geometry_sha256"])
    promotion_gate(load(mon / rels["right_f_lambda_promotion"]), right_id, "F_LAMBDA", pins["right_geometry_sha256"])

    judge = load(mon / rels["f_joint_c1_judge"])
    if judge.get("lemma_id") != "F_JOINT_C1":
        fail("C1_LEMMA_ID")
    if judge.get("judge_signature_status") != "APPROVED":
        fail("C1_NOT_APPROVED")
    if judge.get("binding_use_authorized") is not True:
        fail("C1_NOT_BINDING")
    if judge.get("evidence_class_after_approval") != "HUMAN_AUDITED":
        fail("C1_EVIDENCE_CLASS")
    if judge.get("lemma_sha256") != pins["f_joint_c1_lemma_sha256"]:
        fail("C1_LEMMA_LINK")

    lq = Fraction(lg["candidate_inputs"]["q_right"])
    rq = Fraction(rg["candidate_inputs"]["q_left"])
    lrho = Fraction(lg["derived_geometry"]["rho"])
    rrho = Fraction(rg["derived_geometry"]["rho"])
    llam = Fraction(lg["derived_geometry"]["lambda_hi"])
    rlam = Fraction(rg["derived_geometry"]["lambda_lo"])
    if lq != rq:
        fail("ADJACENT_Q_IDENTITY")
    if llam != rlam:
        fail("ADJACENT_LAMBDA_IDENTITY")

    ls, rs = section(lq, lrho), section(rq, rrho)
    inter = (max(ls[0], rs[0]), min(ls[1], rs[1]))
    hull = (min(ls[0], rs[0]), max(ls[1], rs[1]))
    if not inter[0] < inter[1]:
        fail("INTERSECTION_NOT_POSITIVE_WIDTH")
    for geom, sec, side in ((lg, ls, "LEFT"), (rg, rs, "RIGHT")):
        parent = (
            Fraction(geom["derived_geometry"]["r_lo"]),
            Fraction(geom["derived_geometry"]["r_hi"]),
        )
        if not (parent[0] <= sec[0] < sec[1] <= parent[1]):
            fail(side + "_SECTION_OUTSIDE_HU_PARENT")

    post_head = git(repo, "rev-parse", "HEAD")
    post_clean = not bool(git(repo, "status", "--porcelain"))
    if post_head != head:
        fail("HEAD_CHANGED_DURING_RUN")
    if not post_clean:
        fail("SOURCE_TREE_POST_DIRTY")

    geometry = {
        "lambda_join": fstr(llam),
        "q_join": fstr(lq),
        "left_section": {"r_lo": fstr(ls[0]), "r_hi": fstr(ls[1])},
        "right_section": {"r_lo": fstr(rs[0]), "r_hi": fstr(rs[1])},
        "intersection": {"r_lo": fstr(inter[0]), "r_hi": fstr(inter[1])},
        "intersection_width": fstr(inter[1] - inter[0]),
        "union_hull": {"r_lo": fstr(hull[0]), "r_hi": fstr(hull[1])},
        "adjacent_q_identity": True,
        "adjacent_lambda_identity": True,
        "positive_width_overlap": True,
    }
    receipt = {
        "schema": SCHEMA,
        "contract": CONTRACT,
        "component": COMPONENT,
        "cells": {"left": left_id, "right": right_id},
        "proof_mode": "C1_HU_OVERLAP_COMPOSITION",
        "evidence_class": "BINDING_COMPONENT_CANDIDATE",
        "binding_use_authorized": False,
        "pins": pins,
        "geometry": geometry,
        "logical_composition": {
            "left_section_hu_positive": True,
            "right_section_hu_positive": True,
            "overlap_nonempty_open_interval": True,
            "f_r_nonzero_on_both_sections": True,
            "c1_available_on_both_tube_rectangles": True,
            "conditional_branch_identity_bridge": True,
            "internal_join_ready_for_monotone_assembly": True,
            "conditional_statement": (
                "If the promoted left-cell branch reaches the shared boundary "
                "inside its endpoint section, strict F_r sign and the positive-width "
                "overlap identify the same unique local branch as the right-cell seed."
            ),
        },
        "legacy_point_krawczyk_reexecuted": False,
        "legacy_adaptive_join_contract_claimed": False,
        "nonclaims": [
            "This receipt does not promote the legacy adaptive calibration JOIN.",
            "This receipt does not authorize the complete tube theorem.",
            "Binding use requires a separate judge promotion of this exact receipt SHA256.",
        ],
        "source_tree_pre_clean": True,
        "source_tree_post_clean": post_clean,
        "head_unchanged_during_run": True,
        "execution_head": head,
        "verdict": (
            f"{left_id}_{right_id}_INTERNAL_JOIN_C1_HU_OVERLAP_PASS_"
            "READY_FOR_JUDGE_PROMOTION"
        ),
    }
    ns.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("CONTRACT=" + CONTRACT)
    print("COMPONENT=" + COMPONENT)
    print("JOIN=" + left_id + "->" + right_id)
    print("INTERSECTION_WIDTH=" + geometry["intersection_width"])
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("VERDICT=" + receipt["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
