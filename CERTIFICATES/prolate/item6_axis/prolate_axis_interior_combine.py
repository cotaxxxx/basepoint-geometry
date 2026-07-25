#!/usr/bin/env python3
"""Combine exact compact-interior lambda-block certificates."""
from __future__ import annotations

import argparse
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", default="prolate_axis_interior_1_10_combined.json")
    args = parser.parse_args()

    root = Path(args.root)
    paths = sorted(root.rglob("prolate_axis_interior_block_*.json"))
    expected = [(Fraction(k), Fraction(k + 1)) for k in range(1, 10)]
    target_w = (Fraction(1, 20), Fraction(3, 4))

    records = []
    seen = []
    total_evaluations = 0
    total_leaves = 0
    total_terminal = 0
    all_certified = True
    same_w_interval = True
    worst_lower = None
    worst_record = None

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        w_interval = parse_interval(data["target_rectangle"]["w"])
        lambda_interval = parse_interval(data["target_rectangle"]["lambda"])
        seen.append(lambda_interval)
        counts = data.get("counts", {})
        total_evaluations += int(counts.get("evaluations", 0))
        total_leaves += int(counts.get("certified_leaves", 0))
        total_terminal += int(counts.get("terminal_boxes", 0))
        all_certified = all_certified and data.get("status") == "CERTIFIED"
        same_w_interval = same_w_interval and w_interval == target_w

        leaf = data.get("worst_certified_leaf")
        if leaf is not None:
            lower = Fraction(leaf["Psi"]["real_lower"])
            if worst_lower is None or lower < worst_lower:
                worst_lower = lower
                worst_record = {
                    "source": str(path),
                    "leaf": leaf,
                }

        records.append({
            "path": str(path),
            "sha256": sha256_file(path),
            "status": data.get("status"),
            "w": data["target_rectangle"]["w"],
            "lambda": data["target_rectangle"]["lambda"],
            "counts": counts,
            "script_sha256": data.get("script_sha256"),
        })

    ordered = sorted(seen)
    exact_block_set = ordered == expected
    exact_adjacency = bool(
        ordered
        and ordered[0][0] == Fraction(1)
        and ordered[-1][1] == Fraction(10)
        and all(ordered[i][1] == ordered[i + 1][0] for i in range(len(ordered) - 1))
    )
    zero_terminal = total_terminal == 0

    conditions = {
        "nine expected lambda blocks present": len(paths) == 9 and exact_block_set,
        "all block certificates are CERTIFIED": all_certified,
        "all blocks use w=[1/20,3/4]": same_w_interval,
        "lambda blocks have exact adjacency from 1 to 10": exact_adjacency,
        "zero terminal boxes across all blocks": zero_terminal,
    }
    status = "CERTIFIED" if all(conditions.values()) else "INCOMPLETE"

    result = {
        "status": status,
        "certified_statement": (
            "Psi_lambda(w)>0 for 1<=lambda<=10 and 1/20<=w<=3/4"
            if status == "CERTIFIED"
            else None
        ),
        "conditions": conditions,
        "counts": {
            "block_files": len(paths),
            "evaluations": total_evaluations,
            "certified_leaves": total_leaves,
            "terminal_boxes": total_terminal,
        },
        "worst_certified_leaf": worst_record,
        "blocks": records,
        "limitations": (
            "This is the first compact-interior tranche only. It does not cover "
            "lambda>10, w>3/4, the pole cap, tail, or full item 6 theorem."
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
