#!/usr/bin/env python3
"""2026-09 new certification chain: rigorous axial Qz positivity certificate for Paper 1."""
from __future__ import annotations
import argparse, json, sys
from datetime import datetime, timezone
from pathlib import Path
import flint, sympy, mpmath
from flint import acb, arb, ctx, fmpq
from prolate_cap_arb_certificate import h_derivatives_from_t, local_scalar, rigorous_integral, interval_record, certify_positive, rational_partition

CERTIFICATE_ID = "PROLATE-LOCAL-QZ-2026-09-NEWCHAIN-v1"
MANUSCRIPT_LOWER = arb("0.0885587746621582")

def env_record():
    return {
        "python": sys.version.split()[0],
        "python_flint": flint.__version__,
        "FLINT": flint.__FLINT_VERSION__,
        "SymPy": sympy.__version__,
        "mpmath": mpmath.__version__,
    }

def qz_integrand(theta: acb, a_interval: arb, analytic: bool) -> acb:
    a = acb(a_interval)
    s, ell, C, tangent = local_scalar(theta, a, analytic)
    c = theta.cos()
    wz = c / a
    v = a * c
    h1, h2, _, _ = h_derivatives_from_t(tangent, analytic)
    d = v / ell - wz
    f2 = C**2 * h2 * d**2 + C * h1 * (
        -1/ell + 3*v**2/ell**2 - 4*wz*v/ell + 2*wz**2
    )
    return s * f2

def run_certificate(dps: int, tolerance_text: str, subdivisions: int, depth_limit: int, eval_limit: int):
    ctx.dps = dps
    tol = arb(tolerance_text)
    partition = rational_partition(fmpq(47,10), fmpq(19,4), subdivisions)
    records = []
    all_positive = True
    threshold_pass = True
    worst_lower = None
    worst_interval = None
    for left, right, a_interval in partition:
        value = rigorous_integral(lambda theta, analytic, A=a_interval: qz_integrand(theta, A, analytic), tol, depth_limit, eval_limit)
        positive = certify_positive(value)
        lower = value.real.lower()
        all_positive = all_positive and positive
        threshold_pass = threshold_pass and bool(lower >= MANUSCRIPT_LOWER)
        if worst_lower is None or lower < worst_lower:
            worst_lower = lower
            worst_interval = f"[{left}, {right}]"
        records.append({
            "a_interval": f"[{left}, {right}]",
            **interval_record(value),
            "certified_positive": positive,
            "meets_manuscript_lower_bound": bool(lower >= MANUSCRIPT_LOWER),
        })
    conditions = {
        "Qz(a) > 0 on every partition interval": all_positive,
        "worst lower bound >= 0.0885587746621582": threshold_pass,
    }
    return {
        "status": "CERTIFIED" if (all_positive and threshold_pass) else "FAILED_OR_INCONCLUSIVE",
        "certificate_id": CERTIFICATE_ID,
        "certification_chain": "2026-09 new certification chain",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": env_record(),
        "arithmetic": "python-flint Arb/Acb ball arithmetic",
        "decimal_precision": dps,
        "integration_tolerance": tolerance_text,
        "parameter_subdivisions": subdivisions,
        "proof_interval": "[4.7, 4.75]",
        "manuscript_required_lower_bound": "0.0885587746621582",
        "conditions": conditions,
        "worst_interval": worst_interval,
        "worst_lower": str(worst_lower),
        "Qz_partition": records,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dps", type=int, default=50)
    p.add_argument("--tolerance", default="1e-20")
    p.add_argument("--subdivisions", type=int, default=5)
    p.add_argument("--depth-limit", type=int, default=30)
    p.add_argument("--eval-limit", type=int, default=200000)
    p.add_argument("--json", type=Path, default=Path("prolate_Qz_arb_certificate.json"))
    a = p.parse_args()
    report = run_certificate(a.dps, a.tolerance, a.subdivisions, a.depth_limit, a.eval_limit)
    a.json.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "CERTIFIED": raise SystemExit(1)
if __name__ == "__main__": main()
