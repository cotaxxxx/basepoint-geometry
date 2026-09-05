#!/usr/bin/env python3
"""2026-09 new certification chain: 20-decimal endpoint sign certificate for Paper 1."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
import flint, sympy, mpmath
from flint import acb, arb, ctx, fmpq
from prolate_cap_arb_certificate import q_integrand, rigorous_integral, interval_record, certify_positive, certify_negative

CERTIFICATE_ID = "PROLATE-LOCAL-AC-2026-09-NEWCHAIN-v1"
LEFT_TEXT = "4.72438340452113340672"
RIGHT_TEXT = "4.72438340452113340673"
DEN = 10**20
LEFT_NUM = 472438340452113340672
RIGHT_NUM = 472438340452113340673

def env_record():
    return {
        "python": sys.version.split()[0],
        "python_flint": flint.__version__,
        "FLINT": flint.__FLINT_VERSION__,
        "SymPy": sympy.__version__,
        "mpmath": mpmath.__version__,
    }

def run_certificate(dps: int, tolerance_text: str, subdivisions: int, depth_limit: int, eval_limit: int):
    ctx.dps = dps
    tol = arb(tolerance_text)
    points = {
        LEFT_TEXT: arb(fmpq(LEFT_NUM, DEN)),
        RIGHT_TEXT: arb(fmpq(RIGHT_NUM, DEN)),
    }
    out = {}
    for label, point in points.items():
        value = rigorous_integral(lambda theta, analytic, p=point: q_integrand(theta, acb(p), analytic), tol, depth_limit, eval_limit)
        out[label] = {**interval_record(value), "positive": certify_positive(value), "negative": certify_negative(value)}
    conditions = {
        f"Q({LEFT_TEXT}) > 0": out[LEFT_TEXT]["positive"],
        f"Q({RIGHT_TEXT}) < 0": out[RIGHT_TEXT]["negative"],
    }
    return {
        "status": "CERTIFIED" if all(conditions.values()) else "FAILED_OR_INCONCLUSIVE",
        "certificate_id": CERTIFICATE_ID,
        "certification_chain": "2026-09 new certification chain",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": env_record(),
        "arithmetic": "python-flint Arb/Acb ball arithmetic",
        "decimal_precision": dps,
        "integration_tolerance": tolerance_text,
        "parameter_subdivisions": subdivisions,
        "certified_root_bracket": f"[{LEFT_TEXT}, {RIGHT_TEXT}]",
        "conditions": conditions,
        "fixed_Q_evaluations": out,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dps", type=int, default=50)
    p.add_argument("--tolerance", default="1e-20")
    p.add_argument("--subdivisions", type=int, default=1)
    p.add_argument("--depth-limit", type=int, default=30)
    p.add_argument("--eval-limit", type=int, default=200000)
    p.add_argument("--json", type=Path, default=Path("prolate_ac_arb_certificate.json"))
    a = p.parse_args()
    report = run_certificate(a.dps, a.tolerance, a.subdivisions, a.depth_limit, a.eval_limit)
    a.json.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "CERTIFIED": raise SystemExit(1)
if __name__ == "__main__": main()
