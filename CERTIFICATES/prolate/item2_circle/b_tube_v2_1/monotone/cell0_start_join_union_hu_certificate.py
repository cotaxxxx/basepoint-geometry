#!/usr/bin/env python3
"""Cell-0 start-join union monotonicity certificate for MONOTONE_TUBE_V1.1.

Exactly one production H_U enclosure call is made on
hull(I_0 union I_A0) x {lambda_start}.  The runner is fail-closed and refuses
to evaluate numerically until the F_JOINT_C1 Judge receipt is approved.
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
JUDGE_RECEIPT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/F_JOINT_C1_LEMMA_V1_JUDGE_SIGNATURE.json"
REL_RUNNER = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/cell0_start_join_union_hu_certificate.py"
REL_BT = "CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
REL_V23 = REL_BT + "/dependencies/blocal_v23_source"

EXPECTED_POLICY_SHA256 = "ce1a4c3415e976f69ebd71c3ab97a4e642b9d91219d3e0dbd19de202ea3a5876"
EXPECTED_HU_CHECKER_SHA256 = "d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327"
EXPECTED_PRODUCER_SHA256 = "e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50"
EXPECTED_KERNEL_SHA256 = "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"

CELL0_R_LO = Fraction(37140511944960794174557707, 38685626227668133590597632)
CELL0_R_HI = Fraction(32763, 32768)
A0_R_LO = Fraction(2047, 2048)
A0_R_HI = Fraction(8191, 8192)
LAMBDA_START = Fraction(3307749, 1600000)
HULL_R_LO = min(CELL0_R_LO, A0_R_LO)
HULL_R_HI = max(CELL0_R_HI, A0_R_HI)
CAP = 24000
DPS = 60


def fail(msg: str) -> None:
    raise SystemExit("STOP: " + msg)


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ns = ap.parse_args()
    repo = ns.repo.resolve()

    if git(repo, "status", "--porcelain"):
        fail("SOURCE_TREE_PRE dirty")
    head = git(repo, "rev-parse", "HEAD")
    try:
        subprocess.check_call(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", RELEASE_SHA, head],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        fail("HU V1.2 release SHA is not ancestor of execution HEAD")

    release = json.loads((repo / RELEASE_CONTRACT).read_text())
    if release.get("release_status") != "RELEASED_AFTER_POSITIVE_CONTROL_PASS":
        fail("HU V1.2 release status mismatch")
    pins = release.get("pins", {})
    if pins.get("stage_policy_sha256") != EXPECTED_POLICY_SHA256:
        fail("HU policy SHA mismatch")
    if pins.get("independent_checker_sha256") != EXPECTED_HU_CHECKER_SHA256:
        fail("HU checker SHA mismatch")
    if pins.get("producer_runner_sha256") != EXPECTED_PRODUCER_SHA256:
        fail("HU producer SHA mismatch")

    judge = json.loads((repo / JUDGE_RECEIPT).read_text())
    if judge.get("lemma_id") != "F_JOINT_C1":
        fail("F_JOINT_C1 judge receipt lemma id mismatch")
    if judge.get("judge_signature_status") != "APPROVED":
        fail("F_JOINT_C1 Judge signature not approved")
    if judge.get("binding_use_authorized") is not True:
        fail("F_JOINT_C1 binding use not authorized")
    if judge.get("evidence_class_after_approval") != "HUMAN_AUDITED":
        fail("F_JOINT_C1 evidence class mismatch")
    lemma_sha = judge.get("lemma_sha256")
    lemma_path = repo / judge.get("lemma_path", "")
    if not lemma_path.is_file() or not isinstance(lemma_sha, str) or sha256_file(lemma_path) != lemma_sha:
        fail("F_JOINT_C1 lemma SHA mismatch")

    if os.environ.get("PYTHONDONTWRITEBYTECODE") != "1" or not sys.dont_write_bytecode:
        fail("launch with PYTHONDONTWRITEBYTECODE=1")

    if HULL_R_LO != CELL0_R_LO:
        fail("unexpected start hull lower endpoint")
    if HULL_R_HI != A0_R_HI:
        fail("unexpected start hull upper endpoint")
    if not (HULL_R_LO <= CELL0_R_LO < CELL0_R_HI <= HULL_R_HI):
        fail("cell0 interval not contained in hull")
    if not (HULL_R_LO <= A0_R_LO < A0_R_HI <= HULL_R_HI):
        fail("A0 interval not contained in hull")

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
        fail("Python version mismatch")
    if str(getattr(flint, "__version__", "UNKNOWN")) != "0.9.0":
        fail("python-flint version mismatch")
    if str(getattr(flint, "__FLINT_VERSION__", "UNKNOWN")) != "3.6.0":
        fail("FLINT version mismatch")
    ctx.dps = DPS

    raw_kernel, kernel_path = calibration_runner.load_production_kernel()
    if sha256_file(kernel_path) != EXPECTED_KERNEL_SHA256:
        fail("production kernel SHA mismatch")
    bcfg = json.loads((v23 / "config.blocal-v2.2-run.json").read_text())
    frag = json.loads((v23 / "BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
    bcfg["route_policies"].update(frag["route_policies"])

    u0 = Fraction(1) - HULL_R_HI
    u1 = Fraction(1) - HULL_R_LO
    s = LAMBDA_START - model.LAMBDA_PLUS

    numerical_call_count = 0
    status = "ABORT"
    lo = hi = None
    proof = None
    abort_reason = None
    evaluations = 0
    try:
        numerical_call_count += 1
        iv, proof = route.base.enclose_hu(
            raw_kernel, adapter, acb, arb, fmpq, bcfg,
            u0, u1, s, s,
            required_sign="POS",
            accept=None,
            evaluation_cap=CAP,
        )
        lo, hi = model.interval_fractions(iv, "CELL0_START_JOIN_UNION")
        evaluations = int(proof["evaluation_count"])
        if not proof.get("complete_closed_cover"):
            abort_reason = "INCOMPLETE_ANGULAR_COVER"
        elif lo <= 0:
            abort_reason = "NONPOSITIVE_LOWER_BOUND"
        else:
            status = "PASS_POS"
    except route.base.EnclosureFailure as exc:
        evaluations = int(exc.evaluations)
        abort_reason = exc.reason
    except Exception:
        raise

    if numerical_call_count != 1:
        fail("numerical call count is not exactly one")
    if evaluations > CAP:
        fail("evaluation cap exceeded")

    post_head = git(repo, "rev-parse", "HEAD")
    post_clean = not bool(git(repo, "status", "--porcelain"))
    head_unchanged = post_head == head
    if not head_unchanged:
        fail("HEAD changed during run")
    if not post_clean:
        fail("SOURCE_TREE_POST dirty")

    verdict = "START_JOIN_UNION_MONOTONICITY_PASS" if status == "PASS_POS" else "UNRESOLVED"
    receipt = {
        "schema": "monotone-tube-v1.1-cell0-start-join-union-hu-v1",
        "contract": "MONOTONE_TUBE_V1_1",
        "component": "START_JOIN_UNION_MONOTONICITY_CERTIFICATE",
        "evidence_class": "BINDING_COMPONENT_CANDIDATE",
        "hu_contract_release_sha": RELEASE_SHA,
        "f_joint_c1_lemma_sha256": lemma_sha,
        "execution_head": head,
        "runner_sha256": sha256_file(repo / REL_RUNNER),
        "quantity": "H_U",
        "required_sign": "POS",
        "dps": DPS,
        "per_box_cap": CAP,
        "numerical_call_count": numerical_call_count,
        "geometry": {
            "cell0_interval": {"lo": fstr(CELL0_R_LO), "hi": fstr(CELL0_R_HI)},
            "a0_interval": {"lo": fstr(A0_R_LO), "hi": fstr(A0_R_HI)},
            "hull_interval": {"lo": fstr(HULL_R_LO), "hi": fstr(HULL_R_HI)},
            "lambda_start": fstr(LAMBDA_START),
            "lambda_width": "0/1"
        },
        "status": status,
        "lo": None if lo is None else fstr(lo),
        "hi": None if hi is None else fstr(hi),
        "width": None if lo is None or hi is None else fstr(hi - lo),
        "evaluation_count": evaluations,
        "abort_reason": abort_reason,
        "complete_closed_cover": bool(proof and proof.get("complete_closed_cover")),
        "proof_id": None if proof is None else proof.get("proof_id"),
        "start_join_mode": "JOIN_UNION_MONOTONICITY_CERTIFICATE",
        "start_join_union_monotonicity": "PASS" if status == "PASS_POS" else "UNRESOLVED",
        "verdict": verdict,
        "source_tree_pre_clean": True,
        "source_tree_post_clean": post_clean,
        "head_unchanged_during_run": head_unchanged,
    }
    ns.out_json.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    print("CONTRACT=MONOTONE_TUBE_V1_1")
    print("COMPONENT=START_JOIN_UNION_MONOTONICITY_CERTIFICATE")
    print("F_JOINT_C1_PIN_PASS=TRUE")
    print("HU_RELEASE_PIN_PASS=TRUE")
    print("NUMERICAL_CALL_COUNT=1")
    print("HULL_R_LO=" + fstr(HULL_R_LO))
    print("HULL_R_HI=" + fstr(HULL_R_HI))
    print("LAMBDA_START=" + fstr(LAMBDA_START))
    print("STATUS=" + status)
    print("LO=" + str(receipt["lo"]))
    print("HI=" + str(receipt["hi"]))
    print("EVAL=" + str(evaluations))
    if abort_reason:
        print("ABORT_REASON=" + abort_reason)
    print("SOURCE_TREE_PRE=CLEAN")
    print("SOURCE_TREE_POST=CLEAN")
    print("HEAD_UNCHANGED_DURING_RUN=TRUE")
    print("START_JOIN_UNION_MONOTONICITY=" + receipt["start_join_union_monotonicity"])
    print("VERDICT=" + verdict)
    return 0 if status == "PASS_POS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
