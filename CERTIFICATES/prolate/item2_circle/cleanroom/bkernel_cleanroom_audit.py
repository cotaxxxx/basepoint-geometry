#!/usr/bin/env python3
"""Integrated clean-room audit for the prolate item2 B-KERNEL.

This auditor is derived from the independently verified clean-room package
(SHA-256 a7d46705fbdf7b1702a8040ad81d4f13fc9a1cc89d25ccbf53bc1dcc832b40fd).
It rebuilds the exact 224-leaf regression fixture from the certified item0d
archive, runs independent formula checks, and emits no-newline JSON reports.

This is not the unrecovered historical kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import zipfile
from fractions import Fraction as Fr
from pathlib import Path

ZIP_SHA256 = "db1c68e4bbf43fcb49bd5f27de5d45a36b44f1f8e77141477832ce16ae68df2a"
CERT_SHA256 = "9961090dffca4c78eeca51d5aa97e1d72a71e62b67709396cdd6eb6b856d31a8"
FIXTURE_SHA256 = "800b12fd6850f1b3dde0d22d3afa13918dbb46687f98ae99f5c8097083ed47eb"
HISTORICAL_KERNEL_SHA256 = "ef065381abd802239f5fb107c3e87f64a12259deccbf98d6909bcd975da7157d"


def write_json(path: str | Path, payload: dict) -> None:
    Path(path).write_bytes(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    )


def driver_leaf(record: dict, source: str) -> dict:
    box, value = record["box"], record["result"]["value"]
    return {"kind": "driver_interval", "source": source,
            "r": box["r"], "lambda": box["lambda"],
            "lower": value["real_lower"], "upper": value["real_upper"]}


def riemann_leaf(record: dict, source: str) -> dict:
    box, result = record["box"], record["result"]
    return {"kind": "riemann_mean", "source": source,
            "r": box["r"], "lambda": box["lambda"],
            "lower": result["real_lower"], "upper": result["real_upper"]}


def build_fixture(zip_path: Path, output: Path) -> dict:
    zip_raw = zip_path.read_bytes()
    zip_sha = hashlib.sha256(zip_raw).hexdigest()
    if zip_sha != ZIP_SHA256:
        raise RuntimeError(f"item0d ZIP SHA mismatch: {zip_sha}")
    with zipfile.ZipFile(zip_path) as archive:
        cert_raw = archive.read("certificate_0d_combined.json")
        cert_sha = hashlib.sha256(cert_raw).hexdigest()
        if cert_sha != CERT_SHA256:
            raise RuntimeError(f"combined certificate SHA mismatch: {cert_sha}")
        cert = json.loads(cert_raw)
        checkpoint = json.loads(archive.read("checkpoint_0d.json"))
        mixed = json.loads(archive.read("mixed_queue_0d.json"))
        riemann = json.loads(archive.read("riemann_0d.json"))
        patch = json.loads(archive.read("riemann_patch_0d.json"))
    if cert["provenance"]["kernel_module_sha256"] != HISTORICAL_KERNEL_SHA256:
        raise RuntimeError("historical kernel provenance hash mismatch")
    leaves = [driver_leaf(x, "checkpoint_0d") for x in checkpoint["certified"]]
    for record in mixed["records"]:
        leaves.append(
            riemann_leaf(record, "mixed_queue_0d")
            if record.get("label") == "F_positive_riemann"
            else driver_leaf(record, "mixed_queue_0d")
        )
    leaves.extend(riemann_leaf(x, "riemann_0d") for x in riemann["records"])
    leaves.extend(riemann_leaf(x, "riemann_patch_0d") for x in patch["records"])
    fixture = {
        "label": "item0d_regression_fixture",
        "provenance": {
            "zip_sha256": zip_sha,
            "combined_certificate_sha256": cert_sha,
            "kernel_module_sha256_historical": HISTORICAL_KERNEL_SHA256,
        },
        "theorem": checkpoint["metadata"]["theorem"],
        "leaves": leaves,
    }
    raw = json.dumps(fixture, ensure_ascii=False, separators=(",", ":")).encode()
    sha = hashlib.sha256(raw).hexdigest()
    if len(leaves) != 224 or sha != FIXTURE_SHA256:
        raise RuntimeError(f"fixture invariant failed: leaves={len(leaves)} sha={sha}")
    output.write_bytes(raw)
    print(f"fixture PASS: leaves=224 sha256={sha}")
    return fixture


def symbolic_checks() -> tuple[bool, dict, object, tuple]:
    import sympy as sp
    r, lam, theta, phi = sp.symbols("r lam theta phi", real=True)
    x = sp.symbols("x", real=True)
    hfun = sp.Function("h")
    s, c = sp.sin(theta), sp.cos(theta)
    u = s * sp.cos(phi)
    ell = s**2 + lam**2 * c**2
    w = sp.sqrt(lam**2 * s**2 + c**2)
    q = ell - 2 * r * u + r**2
    W = 1 - r * u
    gamma = lam * W / (w * sp.sqrt(q))
    N = u * (1 - ell) + r * (u**2 - 1)
    gamma_r = (lam / w) * N / q ** sp.Rational(3, 2)
    gamma_rr = (lam / w) * ((u**2 - 1) * q - 3 * N * (r - u)) / q ** sp.Rational(5, 2)
    h0 = hfun(gamma)
    h1 = sp.diff(hfun(x), x).subs(x, gamma)
    h2 = sp.diff(hfun(x), x, 2).subs(x, gamma)
    fint = s * (-u * h0 + W * h1 * gamma_r)
    dfint = s * (-2 * u * h1 * gamma_r + W * (h2 * gamma_r**2 + h1 * gamma_rr))
    checks = {
        "gamma_r": sp.simplify(sp.diff(gamma, r) - gamma_r),
        "gamma_rr": sp.simplify(sp.diff(gamma_r, r) - gamma_rr),
        "dFdr_integrand": sp.simplify(sp.together(sp.diff(fint, r) - dfint)),
    }
    return all(v == 0 for v in checks.values()), checks, fint, (r, lam, theta, phi)


def run_symbolic_pure() -> int:
    passed, checks, _, _ = symbolic_checks()
    report = {"label": "cleanroom_formula_symbolic_audit",
              "checks": {k: str(v) for k, v in checks.items()},
              "verdict": "PASS" if passed else "FAIL"}
    write_json("symbolic_formula_audit_pure.json", report)
    print(report["verdict"], report["checks"])
    return 0 if passed else 1


def parse_ball_float(text: str) -> tuple[float, float]:
    text = text.strip()
    if not text.startswith("["):
        value = float(text)
        return value, value
    match = re.fullmatch(r"\[([^\s]+)\s+\+/-\s+([^\]]+)\]", text)
    if not match:
        raise ValueError(f"unrecognized ball: {text}")
    mid, rad = float(match.group(1)), float(match.group(2))
    return mid - rad, mid + rad


def run_reference(fixture: dict, theta_order: int, phi_order: int) -> int:
    import numpy as np
    from numpy.polynomial.legendre import leggauss
    xt, wt = leggauss(theta_order)
    xp, wp = leggauss(phi_order)
    theta, phi = (xt + 1) * math.pi / 4, (xp + 1) * math.pi
    wt, wp = wt * math.pi / 4, wp * math.pi
    s, c = np.sin(theta)[:, None], np.cos(theta)[:, None]
    u = s * np.cos(phi)[None, :]
    weights = wt[:, None] * wp[None, :]
    records, failures, min_margin = [], 0, math.inf
    for index, leaf in enumerate(fixture["leaves"]):
        r = float((Fr(leaf["r"][0]) + Fr(leaf["r"][1])) / 2)
        lam = float((Fr(leaf["lambda"][0]) + Fr(leaf["lambda"][1])) / 2)
        ell = s * s + lam * lam * c * c
        w = np.sqrt(lam * lam * s * s + c * c)
        q, W = ell - 2 * r * u + r * r, 1 - r * u
        gamma = np.clip(lam * W / (w * np.sqrt(q)), -1.0, 1.0)
        beta, h = np.arccos(gamma), np.arccos(gamma) ** 2
        denom = np.sqrt(np.maximum(1 - gamma * gamma, 0.0))
        h1 = np.where(denom > 1e-13, -2 * beta / denom, -2.0)
        N = u * (1 - ell) + r * (u * u - 1)
        gamma_r = (lam / w) * N / q**1.5
        value = float(np.sum(s * (-u * h + W * h1 * gamma_r) * weights) / (2 * math.pi))
        lower, upper = parse_ball_float(leaf["lower"])[0], parse_ball_float(leaf["upper"])[1]
        if leaf["kind"] == "driver_interval":
            accept_lo, accept_hi = lower, upper
        else:
            width = upper - lower
            accept_lo, accept_hi = lower - width, upper + width
        passed = accept_lo <= value <= accept_hi
        failures += not passed
        margin = min(value - accept_lo, accept_hi - value)
        min_margin = min(min_margin, margin)
        records.append({"index": index, "kind": leaf["kind"], "source": leaf["source"],
                        "r_mid": r, "lambda_mid": lam, "quadrature_value": value,
                        "acceptance_interval": [accept_lo, accept_hi],
                        "margin": margin, "passed": passed})
    report = {"label": "item0d_cleanroom_nonrigorous_midpoint_reference",
              "logical_status": "REFERENCE_ONLY_NOT_A_CERTIFICATE",
              "formula_source": "manuscript Section 3 fixed-domain integral",
              "theta_order": theta_order, "phi_order": phi_order,
              "n_leaves": len(records), "n_failed": failures,
              "minimum_acceptance_margin": min_margin,
              "verdict": "PASS" if failures == 0 else "FAIL", "records": records}
    write_json("reference_midpoint_audit.json", report)
    print(f"{report['verdict']}: {len(records)} leaves, {failures} failed, min_margin={min_margin:.6e}")
    return 0 if failures == 0 else 1


def flint_helpers():
    from flint import arb
    def exact(x: Fr): return arb(str(x.numerator)) / arb(str(x.denominator))
    def interval(lo: Fr, hi: Fr):
        mid, rad = (lo + hi) / 2, (hi - lo) / 2
        return exact(mid) + exact(rad) * arb("+/- 1.0")
    return arb, exact, interval


def run_controls(fixture: dict) -> int:
    arb, _, _ = flint_helpers()
    positive, negative = 0, 0
    for leaf in fixture["leaves"]:
        lo, hi = arb(leaf["lower"]), arb(leaf["upper"])
        mid = (arb(lo.lower()) + arb(hi.upper())) / 2
        if bool(arb(lo.lower()) <= arb(mid.lower())) and bool(arb(mid.upper()) <= arb(hi.upper())):
            positive += 1
        wrong = arb(2)
        width = arb(hi.upper()) - arb(lo.lower())
        accept_lo, accept_hi = (arb(lo.lower()), arb(hi.upper())) if leaf["kind"] == "driver_interval" else (arb(lo.lower()) - width, arb(hi.upper()) + width)
        if not (bool(accept_lo <= arb(wrong.lower())) and bool(arb(wrong.upper()) <= accept_hi)):
            negative += 1
    passed = positive == 224 and negative == 224
    report = {"label": "regression_harness_controls", "positive_passed": positive,
              "negative_rejected": negative, "verdict": "PASS" if passed else "FAIL"}
    write_json("regression_harness_controls.json", report)
    print(report)
    return 0 if passed else 1


def run_regression(fixture: dict, args) -> int:
    from flint import arb, ctx
    import prolate_circle_F_cleanroom as kernel
    _, exact, interval = flint_helpers()
    ctx.dps = args.dps
    records, failures = [], 0
    leaves = fixture["leaves"][:args.limit_leaves or None]
    for i, leaf in enumerate(leaves):
        rlo, rhi = Fr(leaf["r"][0]), Fr(leaf["r"][1])
        llo, lhi = Fr(leaf["lambda"][0]), Fr(leaf["lambda"][1])
        rec_lo, rec_hi = arb(leaf["lower"]), arb(leaf["upper"])
        box_val = kernel.F_arb(interval(rlo, rhi), interval(llo, lhi), tol=args.tol, depth=args.depth_limit, limit=args.eval_limit)
        mid_val = kernel.F_arb(exact((rlo+rhi)/2), exact((llo+lhi)/2), tol=args.tol, depth=args.depth_limit, limit=args.eval_limit)
        overlap = not (bool(arb(box_val.upper()) < arb(rec_lo.lower())) or bool(arb(rec_hi.upper()) < arb(box_val.lower())))
        if leaf["kind"] == "driver_interval":
            midpoint = bool(arb(rec_lo.lower()) <= arb(mid_val.lower())) and bool(arb(mid_val.upper()) <= arb(rec_hi.upper()))
        else:
            width = arb(rec_hi.upper()) - arb(rec_lo.lower())
            midpoint = bool(arb(rec_lo.lower()) - width <= arb(mid_val.lower())) and bool(arb(mid_val.upper()) <= arb(rec_hi.upper()) + width)
        passed = overlap and midpoint
        failures += not passed
        records.append({"index": i, "kind": leaf["kind"], "source": leaf["source"],
                        "r": leaf["r"], "lambda": leaf["lambda"],
                        "recorded": [str(rec_lo), str(rec_hi)],
                        "new_box_enclosure": [str(box_val.lower()), str(box_val.upper())],
                        "new_midpoint": [str(mid_val.lower()), str(mid_val.upper())],
                        "criteria": {"overlap": overlap, "midpoint": midpoint}, "passed": passed})
        print(f"leaf {i+1}/{len(leaves)} {'PASS' if passed else 'FAIL'}")
    report = {"label": "item0d_cleanroom_regression", "fixture_sha256": FIXTURE_SHA256,
              "settings": {"dps": args.dps, "tol": args.tol,
                           "depth_limit": args.depth_limit, "eval_limit": args.eval_limit},
              "n_leaves": len(records), "n_failed": failures,
              "verdict": "PASS" if failures == 0 else "FAIL", "records": records}
    write_json("regression_item0d_report.json", report)
    print(f"{report['verdict']}: {len(records)} leaves, {failures} failed")
    return 0 if failures == 0 else 1


def run_dq(args) -> int:
    from flint import arb, ctx
    import prolate_circle_F_cleanroom as kernel
    symbolic_ok, checks, _, _ = symbolic_checks()
    _, exact, interval = flint_helpers()
    ctx.dps = args.dps
    rng, h = random.Random(args.seed), Fr(args.h)
    lo_r, hi_r, lo_l, hi_l = Fr(9,20), Fr(3,4), Fr(1), Fr(206539,100000)
    points, failures = [], 0
    for i in range(args.points):
        rr = lo_r + Fr(rng.randrange(1,4095),4096) * (hi_r-lo_r)
        ll = lo_l + Fr(rng.randrange(1,4095),4096) * (hi_l-lo_l)
        fp = kernel.F_arb(exact(rr+h), exact(ll), tol=args.tol, depth=args.depth_limit, limit=args.eval_limit)
        fm = kernel.F_arb(exact(rr-h), exact(ll), tol=args.tol, depth=args.depth_limit, limit=args.eval_limit)
        dq = (fp-fm)/(2*exact(h))
        dv = kernel.dFdr_arb(interval(rr-h,rr+h), exact(ll), tol=args.tol, depth=args.depth_limit, limit=args.eval_limit)
        ok = bool(arb(dv.lower()) <= arb(dq.lower())) and bool(arb(dq.upper()) <= arb(dv.upper()))
        failures += not ok
        points.append({"r": str(rr), "lambda": str(ll), "r_interval": [str(rr-h),str(rr+h)],
                       "difference_quotient": [str(dq.lower()),str(dq.upper())],
                       "dFdr_interval": [str(dv.lower()),str(dv.upper())], "dq_subset_dFdr_interval": ok})
        print(f"dq {i+1}/{args.points} {'PASS' if ok else 'FAIL'}")
    verdict = "PASS" if symbolic_ok and failures == 0 else "FAIL"
    report = {"label": "cleanroom_dFdr_symbolic_audit",
              "symbolic_identity_zero": symbolic_ok,
              "symbolic_residuals": {k: str(v) for k,v in checks.items()},
              "difference_quotient": {"method": "mean-value enclosure over [r-h,r+h]",
                                       "h": args.h, "seed": args.seed, "points": points,
                                       "n_failed": failures}, "verdict": verdict}
    write_json("symbolic_audit_dFdr_report.json", report)
    print(f"{verdict}: symbolic={'OK' if symbolic_ok else 'NG'}, dq_fails={failures}")
    return 0 if verdict == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fixture", "nonrigorous", "controls", "regression", "dq"])
    parser.add_argument("--zip", default="../../item0d_interior/item0d_certified.zip")
    parser.add_argument("--fixture", default="item0d_regression_fixture.json")
    parser.add_argument("--dps", type=int, default=40)
    parser.add_argument("--tol", default="1e-10")
    parser.add_argument("--depth-limit", type=int, default=12)
    parser.add_argument("--eval-limit", type=int, default=200000)
    parser.add_argument("--limit-leaves", type=int, default=0)
    parser.add_argument("--points", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument("--h", default="1/4096")
    parser.add_argument("--theta-order", type=int, default=100)
    parser.add_argument("--phi-order", type=int, default=200)
    args = parser.parse_args()
    fixture = build_fixture(Path(args.zip), Path(args.fixture))
    if args.mode == "fixture": return 0
    if args.mode == "nonrigorous": return run_symbolic_pure() or run_reference(fixture, args.theta_order, args.phi_order)
    if args.mode == "controls": return run_controls(fixture)
    if args.mode == "regression": return run_regression(fixture, args)
    return run_dq(args)


if __name__ == "__main__":
    raise SystemExit(main())
