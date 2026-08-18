from __future__ import annotations

import json
import os
import sys
import time
from fractions import Fraction
from pathlib import Path


def _is_controls_invocation() -> bool:
    return (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and len(sys.argv) >= 2
        and Path(sys.argv[0]).name == "bkernel_cleanroom_audit.py"
        and sys.argv[1] == "controls"
    )


def _run() -> None:
    if not _is_controls_invocation():
        return

    vendor = Path(__file__).resolve().parent.parent / "vendor"
    sys.path.insert(0, str(vendor))

    from flint import arb, ctx
    import prolate_circle_F_cleanroom as kernel

    ctx.dps = 60
    lam = Fraction(3307749, 1600000)
    tol = "1e-20"
    depth = 12
    limit = 200000

    def exact(x: Fraction):
        return arb(str(x.numerator)) / arb(str(x.denominator))

    cache: dict[tuple[str, Fraction], dict] = {}

    def evaluate(name: str, r: Fraction) -> dict:
        key = (name, r)
        if key in cache:
            return cache[key]
        fn = getattr(kernel, name)
        started = time.time()
        try:
            value = fn(exact(r), exact(lam), tol=tol, depth=depth, limit=limit)
            text = str(value)
            lower = text.lower()
            finite = "nan" not in lower and "inf" not in lower
            result = {
                "status": "finite" if finite else "nonfinite",
                "value": text[:500],
                "elapsed_s": round(time.time() - started, 6),
            }
        except Exception as exc:
            result = {
                "status": "exception",
                "exception": type(exc).__name__,
                "message": str(exc)[:500],
                "elapsed_s": round(time.time() - started, 6),
            }
        cache[key] = result
        print(
            "NAN_FRONTIER_POINT "
            + json.dumps(
                {"function": name, "r": f"{r.numerator}/{r.denominator}", **result},
                separators=(",", ":"),
            ),
            flush=True,
        )
        return result

    def both_finite(r: Fraction) -> bool:
        f = evaluate("F_arb", r)
        d = evaluate("dFdr_arb", r)
        return f["status"] == "finite" and d["status"] == "finite"

    report: dict = {
        "schema": "btube-bkernel-nan-frontier-diagnostic-v1",
        "kernel_sha256_expected": "77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac",
        "lambda": "3307749/1600000",
        "settings": {"dps": 60, "tol": tol, "depth": depth, "limit": limit},
        "coarse": [],
        "refined_combined_frontier": None,
    }

    previous_finite: Fraction | None = None
    first_nonfinite: Fraction | None = None
    for k in range(1, 15):
        r = Fraction((1 << k) - 1, 1 << k)
        ok = both_finite(r)
        report["coarse"].append({
            "k": k,
            "r": f"{r.numerator}/{r.denominator}",
            "both_finite": ok,
        })
        if ok:
            previous_finite = r
        else:
            first_nonfinite = r
            break

    if previous_finite is not None and first_nonfinite is not None:
        lo = previous_finite
        hi = first_nonfinite
        refinement = []
        for _ in range(8):
            mid = (lo + hi) / 2
            ok = both_finite(mid)
            refinement.append({
                "r": f"{mid.numerator}/{mid.denominator}",
                "both_finite": ok,
            })
            if ok:
                lo = mid
            else:
                hi = mid
        report["refined_combined_frontier"] = {
            "last_observed_both_finite": f"{lo.numerator}/{lo.denominator}",
            "first_observed_nonfinite": f"{hi.numerator}/{hi.denominator}",
            "width": f"{(hi-lo).numerator}/{(hi-lo).denominator}",
            "refinement": refinement,
        }

    report["evaluations"] = [
        {
            "function": name,
            "r": f"{r.numerator}/{r.denominator}",
            **result,
        }
        for (name, r), result in cache.items()
    ]
    print("NAN_FRONTIER_RESULT " + json.dumps(report, separators=(",", ":")), flush=True)


try:
    _run()
except Exception as exc:
    print(
        "NAN_FRONTIER_DIAGNOSTIC_ERROR "
        + json.dumps({"exception": type(exc).__name__, "message": str(exc)}, separators=(",", ":")),
        flush=True,
    )
