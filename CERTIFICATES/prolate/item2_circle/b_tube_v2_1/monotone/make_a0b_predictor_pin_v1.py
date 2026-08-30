#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

REPO_COMPONENT1 = Path(
    "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/"
    "CELL0_COMPONENT1_TUBE_GEOMETRY_V1.json"
)

A0_CERT_REL = Path(
    "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/"
    "A0_BOUNDARY_DISTANCE_CERTIFICATE.json"
)

OUT_REL = Path(
    "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/monotone/"
    "A0B_CELL0_PREDICTOR_INPUT_PIN_V1.json"
)

HISTORICAL_HEAD = "891a7ff"
HISTORICAL_RUN = "33010418300"

EXPECTED_A0_SHA256 = (
    "03b20c172c6562ed32ea66f35dcd177bb887e17e60b7c49f632e91e0e1183b81"
)

EXPECTED_Q_LEFT = Fraction(16379, 16384)
EXPECTED_Q_RIGHT = Fraction(
    37146414903064381231074827,
    38685626227668133590597632,
)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json_bytes(obj: object) -> bytes:
    return (
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode()

def as_fraction(obj, label: str) -> Fraction:
    if isinstance(obj, str):
        try:
            return Fraction(obj)
        except Exception:
            pass
    if isinstance(obj, dict):
        if "p" in obj and "q" in obj:
            return Fraction(int(obj["p"]), int(obj["q"]))
        if "m" in obj and "e" in obj:
            return Fraction(int(obj["m"]), 1 << int(obj["e"]))
    raise SystemExit(f"FAIL_FRACTION_PARSE {label}={obj!r}")

def find_cell0_q_pair(obj):
    matches = []

    def walk(x):
        if isinstance(x, dict):
            if "q_left" in x and "q_right" in x:
                idx = x.get("cell_index", x.get("candidate_index", x.get("index")))
                try:
                    ql = as_fraction(x["q_left"], "q_left")
                    qr = as_fraction(x["q_right"], "q_right")
                except SystemExit:
                    pass
                else:
                    if idx in (0, "0", None):
                        matches.append((idx, ql, qr))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(obj)

    exact = [
        (idx, ql, qr)
        for idx, ql, qr in matches
        if ql == EXPECTED_Q_LEFT and qr == EXPECTED_Q_RIGHT
    ]

    if len(exact) != 1:
        raise SystemExit(
            f"FAIL_A0B_CELL0_Q_PAIR_RESOLUTION "
            f"candidate_matches={len(matches)} exact_matches={len(exact)}"
        )

    return exact[0]

def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo), *args],
        text=True,
    ).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--anchors", required=True, type=Path)
    args = ap.parse_args()

    repo = args.repo.resolve()
    anchors = args.anchors.resolve()

    head_before = git(repo, "rev-parse", "HEAD")

    component1_path = repo / REPO_COMPONENT1
    if not component1_path.is_file():
        raise SystemExit(f"FAIL_COMPONENT1_MISSING path={component1_path}")

    component1_bytes = component1_path.read_bytes()
    component1_sha = sha256_bytes(component1_bytes)
    component1 = json.loads(component1_bytes)

    ci = component1.get("candidate_inputs")
    if not isinstance(ci, dict):
        raise SystemExit("FAIL_COMPONENT1_CANDIDATE_INPUTS")

    c_q_left = as_fraction(ci.get("q_left"), "component1.q_left")
    c_q_right = as_fraction(ci.get("q_right"), "component1.q_right")

    if c_q_left != EXPECTED_Q_LEFT:
        raise SystemExit("FAIL_COMPONENT1_Q_LEFT")
    if c_q_right != EXPECTED_Q_RIGHT:
        raise SystemExit("FAIL_COMPONENT1_Q_RIGHT")

    if not anchors.is_file():
        raise SystemExit(f"FAIL_A0B_ARTIFACT_MISSING path={anchors}")

    anchors_bytes = anchors.read_bytes()
    anchors_sha = sha256_bytes(anchors_bytes)

    try:
        anchors_obj = json.loads(anchors_bytes)
    except Exception as exc:
        raise SystemExit(f"FAIL_A0B_JSON {exc}")

    _, a_q_left, a_q_right = find_cell0_q_pair(anchors_obj)

    if a_q_left != c_q_left:
        raise SystemExit("FAIL_A0B_COMPONENT1_Q_LEFT_MISMATCH")
    if a_q_right != c_q_right:
        raise SystemExit("FAIL_A0B_COMPONENT1_Q_RIGHT_MISMATCH")

    a0_bytes = subprocess.check_output([
        "git", "-C", str(repo), "show",
        f"{HISTORICAL_HEAD}:{A0_CERT_REL.as_posix()}",
    ])
    a0_sha = sha256_bytes(a0_bytes)

    if a0_sha != EXPECTED_A0_SHA256:
        raise SystemExit("FAIL_A0_CERT_SHA")

    a0 = json.loads(a0_bytes)
    operational = a0.get("operational_refined_start_root_interval")
    if not isinstance(operational, dict):
        raise SystemExit("FAIL_A0_OPERATIONAL_INTERVAL")

    a0_lo = as_fraction(operational.get("lo"), "a0.lo")
    a0_hi = as_fraction(operational.get("hi"), "a0.hi")
    derived_q_left = (a0_lo + a0_hi) / 2

    if derived_q_left != EXPECTED_Q_LEFT:
        raise SystemExit("FAIL_A0_MIDPOINT")

    receipt = {
        "schema": "a0b-cell0-predictor-input-pin-v1",
        "contract": "F_LAMBDA_CONTRACT_V1.1",
        "control_id": "NC04b",
        "evidence_class": "PIN_RECORD",
        "binding_use_authorized": False,
        "historical_provenance": {
            "run": HISTORICAL_RUN,
            "head": HISTORICAL_HEAD,
            "role": "PROVENANCE_METADATA",
            "load_bearing_for_candidate_geometry": False,
        },
        "a0_certificate": {
            "historical_head": HISTORICAL_HEAD,
            "path": A0_CERT_REL.as_posix(),
            "sha256": a0_sha,
            "q_left": f"{derived_q_left.numerator}/{derived_q_left.denominator}",
        },
        "a0b_start_anchors": {
            "input_path_report_only": str(anchors),
            "sha256": anchors_sha,
            "cell_index": 0,
            "q_left": f"{a_q_left.numerator}/{a_q_left.denominator}",
            "q_right": f"{a_q_right.numerator}/{a_q_right.denominator}",
            "q_right_source": "EXACT_VALUE_EXTRACTED_FROM_RUN_ARTIFACT",
        },
        "component1": {
            "path": REPO_COMPONENT1.as_posix(),
            "sha256": component1_sha,
            "q_left": f"{c_q_left.numerator}/{c_q_left.denominator}",
            "q_right": f"{c_q_right.numerator}/{c_q_right.denominator}",
            "q_left_exact_match": True,
            "q_right_exact_match": True,
            "component1_match": True,
        },
        "nc04b": {
            "mutation_target": "q_left_or_q_right",
            "expected_contract_code": "FAIL_PREDICTOR_INPUT_PIN",
            "ready_for_execution": True,
        },
        "q_right_newton_replay": {
            "role": "OPTIONAL_REPORT_ONLY",
            "required_for_nc04b": False,
            "required_for_execution_authorization": False,
        },
        "source_state": {
            "creation_head": head_before,
        },
    }

    out = repo / OUT_REL
    if out.exists():
        raise SystemExit(f"FAIL_OUTPUT_ALREADY_EXISTS path={out}")

    data = canonical_json_bytes(receipt)
    out.write_bytes(data)

    print(f"A0B_PIN={out}")
    print(f"A0B_PIN_SHA256={sha256_bytes(data)}")
    print(f"A0B_START_ANCHORS_SHA256={anchors_sha}")
    print(f"Q_LEFT={EXPECTED_Q_LEFT.numerator}/{EXPECTED_Q_LEFT.denominator}")
    print(f"Q_RIGHT={EXPECTED_Q_RIGHT.numerator}/{EXPECTED_Q_RIGHT.denominator}")
    print("COMPONENT1_EXACT_MATCH=TRUE")
    print("Q_RIGHT_NEWTON_REPLAY=OPTIONAL_REPORT_ONLY")
    print("NC04b=READY_FOR_EXECUTION")

if __name__ == "__main__":
    main()
