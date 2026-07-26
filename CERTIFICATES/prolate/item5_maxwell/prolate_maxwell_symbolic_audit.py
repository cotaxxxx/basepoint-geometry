#!/usr/bin/env python3
"""Exact SymPy audit for the lambda derivatives used in prolate item 5."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


lam, x, t, s2 = sp.symbols("lam x t s2", positive=True)
x2 = x**2
ell = 1 + (lam**2 - 1) * x2
w2 = lam**2 * (1 - x2) + x2
c0 = lam / sp.sqrt(ell * w2)
c0_claim = c0 * (
    1 / lam - lam * x2 / ell - lam * (1 - x2) / w2
)

c2 = 1 - s2
t2 = t**2
a = 1 - 2 * t2
L2 = c2 + lam**2 * s2
J2 = c2 + s2 / lam**2
R2 = t2 + (1 - t2) * L2
eta2 = a**2 + 4 * t2 * (1 - t2) * J2
cb = t / sp.sqrt(R2 * eta2)
R2_lam = 2 * lam * (1 - t2) * s2
eta2_lam = -8 * t2 * (1 - t2) * s2 / lam**3
cb_claim = -cb * (R2_lam / R2 + eta2_lam / eta2) / 2

checks = {
    "center_c_lambda": sp.simplify(sp.diff(c0, lam) - c0_claim) == 0,
    "boundary_R2_lambda": sp.simplify(sp.diff(R2, lam) - R2_lam) == 0,
    "boundary_eta2_lambda": sp.simplify(sp.diff(eta2, lam) - eta2_lam) == 0,
    "boundary_c_lambda": sp.simplify(sp.diff(cb, lam) - cb_claim) == 0,
}

result = {
    "status": "PASSED" if all(checks.values()) else "FAILED",
    "checks": checks,
    "formulas": {
        "center_c": str(c0),
        "center_c_lambda": str(c0_claim),
        "boundary_c": str(cb),
        "boundary_c_lambda": str(cb_claim),
    },
}
result["script_sha256"] = sha256_file(Path(__file__))
out = Path("prolate_maxwell_symbolic_audit.json")
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASSED" else 1)
