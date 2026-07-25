#!/usr/bin/env python3
"""Combine exact adjacent item 6 center-cap block certificates."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_interval(text: str) -> tuple[Fraction, Fraction]:
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError(f"invalid interval: {text}")
    lo, hi = text[1:-1].split(",", 1)
    return Fraction(lo), Fraction(hi)


def lower_fraction(real_lower: str) -> Fraction:
    token = real_lower.split()[0].strip("[")
    return Fraction(token)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="prolate_axis_center_cap_block_*.json")
    parser.add_argument("--json", default="prolate_axis_center_cap_combined.json")
    args = parser.parse_args()

    paths = sorted(Path(p) for p in glob.glob(args.pattern))
    if not paths:
        raise FileNotFoundError(f"no block certificates match {args.pattern}")

    blocks = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        lam_lo, lam_hi = parse_interval(data["target_rectangle"]["lambda"])
        v_lo, v_hi = parse_interval(data["target_rectangle"]["v"])
        blocks.append((lam_lo, lam_hi, v_lo, v_hi, path, data))
    blocks.sort(key=lambda item: item[0])

    common_v = all((b[2], b[3]) == (blocks[0][2], blocks[0][3]) for b in blocks)
    adjacent = all(blocks[i][1] == blocks[i + 1][0] for i in range(len(blocks) - 1))
    all_certified = all(b[5]["status"] == "CERTIFIED" for b in blocks)
    zero_terminal = all(b[5]["counts"]["terminal_boxes"] == 0 for b in blocks)
    exact_block_coverage = all(
        b[5]["conditions"].get("exact rational coverage of block", False)
        for b in blocks
    )

    worst_candidates = [
        (lower_fraction(b[5]["worst_certified_leaf"]["A_second"]["real_lower"]), b)
        for b in blocks
        if b[5].get("worst_certified_leaf")
    ]
    worst_block = min(worst_candidates, key=lambda item: item[0])[1] if worst_candidates else None

    conditions = {
        "all blocks certified": all_certified,
        "all blocks use the same v interval": common_v,
        "lambda blocks are exactly adjacent": adjacent,
        "every block has exact rational coverage": exact_block_coverage,
        "zero terminal boxes across all blocks": zero_terminal,
    }
    status = "CERTIFIED" if all(conditions.values()) else "INCOMPLETE"

    result = {
        "status": status,
        "scope": (
            f"A_lambda''(v)>0 for {blocks[0][2]}<=v<={blocks[0][3]}, "
            f"{blocks[0][0]}<=lambda<={blocks[-1][1]}"
        ),
        "derived_conclusion": (
            f"If status is CERTIFIED, Psi_lambda(w)>0 for "
            f"{blocks[0][0]}<=lambda<={blocks[-1][1]} and "
            f"0<w<={blocks[0][3]}."
        ),
        "conditions": conditions,
        "counts": {
            "blocks": len(blocks),
            "evaluations": sum(b[5]["counts"]["evaluations"] for b in blocks),
            "certified_leaves": sum(b[5]["counts"]["certified_leaves"] for b in blocks),
            "terminal_boxes": sum(b[5]["counts"]["terminal_boxes"] for b in blocks),
        },
        "block_files": [
            {
                "path": b[4].name,
                "sha256": sha256_file(b[4]),
                "lambda": f"[{b[0]},{b[1]}]",
                "status": b[5]["status"],
                "counts": b[5]["counts"],
            }
            for b in blocks
        ],
        "worst_certified_leaf": (
            worst_block[5]["worst_certified_leaf"] if worst_block else None
        ),
    }

    output = Path(args.json)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{sha256_file(Path(__file__))}  {Path(__file__).name}\n"
        f"{sha256_file(output)}  {output.name}\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if status == "CERTIFIED" else 1)


if __name__ == "__main__":
    main()
