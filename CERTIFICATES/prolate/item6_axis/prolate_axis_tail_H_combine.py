#!/usr/bin/env python3
"""Combine exact adjacent w-block certificates for one compact tail mu slab."""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_interval(text: str) -> tuple[Fraction, Fraction]:
    if not (text.startswith("[") and text.endswith("]")):
        raise ValueError(f"invalid interval: {text}")
    lo, hi = text[1:-1].split(",", 1)
    return Fraction(lo), Fraction(hi)


def lower_fraction(text: str) -> Fraction:
    token = text.split()[0].strip("[")
    return Fraction(token)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", default="prolate_axis_tail_H_block_*.json")
    parser.add_argument("--json", default="prolate_axis_tail_H_combined.json")
    args = parser.parse_args()

    paths = sorted(Path(p) for p in glob.glob(args.pattern))
    if not paths:
        raise FileNotFoundError(f"no block certificates match {args.pattern}")

    blocks = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        mu_lo, mu_hi = parse_interval(data["target_rectangle"]["mu"])
        w_lo, w_hi = parse_interval(data["target_rectangle"]["w"])
        blocks.append((w_lo, w_hi, mu_lo, mu_hi, path, data))
    blocks.sort(key=lambda item: item[0])

    common_mu = all(
        (block[2], block[3]) == (blocks[0][2], blocks[0][3])
        for block in blocks
    )
    adjacent = all(
        blocks[index][1] == blocks[index + 1][0]
        for index in range(len(blocks) - 1)
    )
    endpoints = bool(
        blocks
        and blocks[0][0] == Fraction(1, 20)
        and blocks[-1][1] == Fraction(3, 4)
    )
    all_certified = all(block[5]["status"] == "CERTIFIED" for block in blocks)
    exact_block_coverage = all(
        block[5]["conditions"].get("exact rational coverage of block", False)
        for block in blocks
    )
    zero_terminal = all(
        block[5]["counts"]["terminal_boxes"] == 0 for block in blocks
    )

    worst_candidates = [
        (
            lower_fraction(block[5]["worst_certified_leaf"]["H"]["real_lower"]),
            block,
        )
        for block in blocks
        if block[5].get("worst_certified_leaf")
    ]
    worst_block = (
        min(worst_candidates, key=lambda item: item[0])[1]
        if worst_candidates
        else None
    )

    conditions = {
        "all blocks certified": all_certified,
        "all blocks use the same mu interval": common_mu,
        "w blocks are exactly adjacent": adjacent,
        "combined w endpoints equal [1/20,3/4]": endpoints,
        "every block has exact rational coverage": exact_block_coverage,
        "zero terminal boxes across all blocks": zero_terminal,
    }
    status = "CERTIFIED" if all(conditions.values()) else "INCOMPLETE"

    result = {
        "status": status,
        "certified_statement": (
            f"H(mu,w)>0 for {blocks[0][2]}<=mu<={blocks[0][3]}, "
            "1/20<=w<=3/4"
            if status == "CERTIFIED"
            else None
        ),
        "conditions": conditions,
        "counts": {
            "blocks": len(blocks),
            "evaluations": sum(
                block[5]["counts"]["evaluations"] for block in blocks
            ),
            "certified_leaves": sum(
                block[5]["counts"]["certified_leaves"] for block in blocks
            ),
            "terminal_boxes": sum(
                block[5]["counts"]["terminal_boxes"] for block in blocks
            ),
        },
        "block_files": [
            {
                "path": block[4].name,
                "sha256": sha256_file(block[4]),
                "mu": f"[{block[2]},{block[3]}]",
                "w": f"[{block[0]},{block[1]}]",
                "status": block[5]["status"],
                "counts": block[5]["counts"],
            }
            for block in blocks
        ],
        "worst_certified_leaf": (
            worst_block[5]["worst_certified_leaf"] if worst_block else None
        ),
        "limitations": (
            "This covers only one compact mu slab. The limit mu->0, the center "
            "tail w<1/20, and the pole tail w>3/4 remain separate stages."
        ),
    }
    result["combiner_sha256"] = sha256_file(Path(__file__))

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
