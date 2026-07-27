#!/usr/bin/env python3
"""B-SEED: non-rigorous float Newton predictor for the stationary-circle
branch r_c(lambda). Output is a draft grid only and is NEVER cited in a
proof. Requires the vendored item-0 kernels (B-KERNEL debt)."""
from __future__ import annotations
import json, math, sys
from fractions import Fraction as Fr

sys.path.insert(0, "vendor")
from prolate_circle_kernels import F_float, dFdr_float  # wired by B-KERNEL

def newton(lam: float, r0: float, iters: int = 60, tol: float = 1e-14):
    r = r0
    for _ in range(iters):
        f, df = F_float(r, lam), dFdr_float(r, lam)
        if df == 0.0 or not math.isfinite(f) or not math.isfinite(df):
            return None
        step = f / df
        r -= step
        if not (0.0 < r < 1.0):
            return None
        if abs(step) < tol:
            return r
    return None

def main():
    lam_lo, lam_hi, n = Fr(5), Fr(100), 380  # dyadic-friendly grid
    seeds, r_prev = [], 0.5
    for k in range(n + 1):
        lam = lam_lo + (lam_hi - lam_lo) * Fr(k, n)
        r = newton(float(lam), r_prev)
        if r is not None:
            r_prev = r
        seeds.append({"lambda": str(lam), "r_seed": r})
    payload = json.dumps({"role": "B-SEED (non-rigorous draft)",
                          "grid": seeds}, indent=2)
    # no trailing newline: hash discipline
    with open("prolate_circle_seed.json", "w", encoding="utf-8") as fh:
        fh.write(payload)
    print("seeds written:", sum(1 for s in seeds if s["r_seed"] is not None))

if __name__ == "__main__":
    main()
