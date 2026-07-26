#!/usr/bin/env python3
"""B-TUBE pilot: 1-D interval-Krawczyk verification of F(r, lambda) = 0
inside a tube around the seeded branch, uniform over a lambda box.

CERTIFIED criterion for one (lambda-box, r-box) pair:
    K(X) = m - F(m, L)/c + (1 - F_r(X, L)/c) * (X - m)  strictly inside X,
with m the exact rational midpoint of X, L the full lambda box, c an exact
rational approximation of F_r at (m, mid L), and all evaluations rigorous
Arb enclosures. Strict inclusion gives existence + uniqueness +
nondegeneracy of the zero of F(., lambda) in X for EVERY lambda in L."""
from __future__ import annotations
import argparse, json, sys
from fractions import Fraction as Fr
from flint import arb, ctx

sys.path.insert(0, "vendor")
from prolate_circle_kernels import F_arb, dFdr_arb  # rigorous enclosures

def rat_arb(q: Fr) -> arb:
    return arb(q.numerator) / arb(q.denominator)

def box(lo: Fr, hi: Fr) -> arb:
    mid, rad = (lo + hi) / 2, (hi - lo) / 2
    return rat_arb(mid) + rat_arb(rad) * arb("+/- 1.0")

def krawczyk_once(r_lo: Fr, r_hi: Fr, lam_lo: Fr, lam_hi: Fr):
    """Return (certified, note). certified=True only if the Krawczyk image
    is STRICTLY inside the r-box for every lambda in the lambda box."""
    m = (r_lo + r_hi) / 2
    L = box(lam_lo, lam_hi)
    X = box(r_lo, r_hi)
    lam_mid = (lam_lo + lam_hi) / 2
    dF_m = dFdr_arb(rat_arb(m), rat_arb(lam_mid))
    if dF_m.contains(arb(0)):
        return False, "slope_center_contains_zero"
    c = arb(dF_m.mid())  # exact dyadic constant; rigor lives in enclosures
    dF_X = dFdr_arb(X, L)
    K = rat_arb(m) - F_arb(rat_arb(m), L) / c \
        + (1 - dF_X / c) * (X - rat_arb(m))
    strictly_inside = bool(K < rat_arb(r_hi)) and bool(K > rat_arb(r_lo))
    return strictly_inside, None if strictly_inside else "no_contraction"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dps", type=int, default=35)
    ap.add_argument("--lam-lo", default="5"); ap.add_argument("--lam-hi", default="6")
    ap.add_argument("--lam-splits", type=int, default=16)
    ap.add_argument("--seed-file", default="prolate_circle_seed.json")
    ap.add_argument("--tube-num", type=int, default=1)
    ap.add_argument("--tube-den", type=int, default=64)
    args = ap.parse_args()
    ctx.dps = args.dps

    seeds = json.load(open(args.seed_file, encoding="utf-8"))["grid"]
    lam_lo, lam_hi = Fr(args.lam_lo), Fr(args.lam_hi)
    rho = Fr(args.tube_num, args.tube_den)
    results = []
    for k in range(args.lam_splits):
        a = lam_lo + (lam_hi - lam_lo) * Fr(k, args.lam_splits)
        b = lam_lo + (lam_hi - lam_lo) * Fr(k + 1, args.lam_splits)
        mid_lam = float((a + b) / 2)
        near = min((s for s in seeds if s["r_seed"] is not None),
                   key=lambda s: abs(float(Fr(s["lambda"])) - mid_lam))
        r0 = Fr(near["r_seed"]).limit_denominator(1 << 20)
        ok, why = krawczyk_once(r0 - rho, r0 + rho, a, b)
        results.append({"lambda": [str(a), str(b)],
                        "r_box": [str(r0 - rho), str(r0 + rho)],
                        "certified": bool(ok), "note": why})
    n_ok = sum(1 for r in results if r["certified"])
    payload = json.dumps({"role": "B-TUBE pilot", "dps": args.dps,
                          "tube_radius": str(rho),
                          "certified_boxes": n_ok,
                          "total_boxes": len(results),
                          "status": "CERTIFIED-SUBNODE" if n_ok == len(results)
                                    else "INCOMPLETE",
                          "boxes": results}, indent=2)
    with open("prolate_circle_tube_pilot.json", "w", encoding="utf-8") as fh:
        fh.write(payload)  # no trailing newline
    print(f"certified {n_ok}/{len(results)} lambda boxes")
    raise SystemExit(0 if n_ok == len(results) else 1)

if __name__ == "__main__":
    main()
