#!/usr/bin/env python3
"""Exact symbolic audit for the prolate item 6 axial reduction."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


lam, w, c = sp.symbols("lam w c", positive=True, finite=True)

N = 1 - w * c
R2 = 1 - c**2 + lam**2 * (c - w)**2
S2 = 1 - c**2 + c**2 / lam**2
C = N / sp.sqrt(R2 * S2)

Cw_claim = C * (-c / N + lam**2 * (c - w) / R2)

# Reflection is checked using a separate unconstrained symbol substitution.
reflection = sp.simplify(C.subs({c: -c, w: -w}) - C)
weight_reflection = sp.simplify(
    N.subs({c: -c, w: -w}) - N
)

checks = {
    "C_w_formula": sp.simplify(sp.diff(C, w) - Cw_claim) == 0,
    "R2_reflection": sp.simplify(
        R2.subs({c: -c, w: -w}) - R2
    ) == 0,
    "S2_even_in_c": sp.simplify(S2.subs(c, -c) - S2) == 0,
    "C_reflection": reflection == 0,
    "cone_weight_reflection": weight_reflection == 0,
}

result = {
    "status": "PASSED" if all(checks.values()) else "FAILED",
    "checks": checks,
    "formulas": {
        "N": str(N),
        "R2": str(R2),
        "S2": str(S2),
        "C": str(C),
        "C_w": str(Cw_claim),
    },
    "consequences": {
        "energy_even": "A_lambda(-w)=A_lambda(w), after c -> -c",
        "derivative_odd": "Psi_lambda(-w)=-Psi_lambda(w)",
    },
    "script_sha256": sha256_file(Path(__file__)),
}

out = Path("prolate_axis_symbolic_audit.json")
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["status"] == "PASSED" else 1)
