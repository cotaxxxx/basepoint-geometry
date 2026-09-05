#!/usr/bin/env python3
"""Symbolic audit of the h-derivative chain used by the Arb certificate.

Verifies that the 0F1 formulas evaluated by the interval code are exactly
the first four derivatives of h(x)=acos(x)^2 after x=cos(beta), beta in (0,pi).
This closes the h -> 0F1 -> B2/H4 -> Arb link.
"""
import sympy as sp

CERTIFICATE_ID = "PROLATE-LOCAL-HCHAIN-SYMBOLIC-2026-09-R3-v1"

x, beta = sp.symbols("x beta", positive=True)
h = sp.acos(x) ** 2

derivatives = []
for order in range(1, 5):
    expr = sp.diff(h, x, order).subs(x, sp.cos(beta)).rewrite(sp.sin)
    expr = sp.simplify(sp.trigsimp(expr.subs(sp.acos(sp.cos(beta)), beta)))
    derivatives.append(expr)

z = beta ** 2

def hyp0f1(nu):
    return sp.hyperexpand(sp.hyper((), (nu,), -z / 4))

S = hyp0f1(sp.Rational(3, 2))
T = hyp0f1(sp.Rational(5, 2))
U = hyp0f1(sp.Rational(7, 2))
V = hyp0f1(sp.Rational(9, 2))

claimed = [
    -2 / S,
    2 * T / (3 * S**3),
    2 * U / (15 * S**4) - 2 * T**2 / (3 * S**5),
    2 * V / (105 * S**5) - 4 * U * T / (9 * S**6) + sp.Rational(10, 9) * T**3 / S**7,
]

ok = True
print("certificate_id:", CERTIFICATE_ID)
print("audit: h(x)=acos(x)^2 derivatives vs 0F1 formulas")
for order, (actual, expected) in enumerate(zip(derivatives, claimed), start=1):
    diff = sp.simplify(actual - expected)
    diff = diff.replace(sp.Abs(sp.sin(beta)), sp.sin(beta))
    diff = diff.replace(sp.acos(sp.cos(beta)), beta)
    diff = sp.simplify(sp.trigsimp(sp.expand_trig(diff)))
    passed = (diff == 0)
    ok = ok and passed
    print(f"h{order}: diff = {diff}; {'PASS' if passed else 'FAIL'}")

print("PASS: h1..h4 0F1 chain verified exactly" if ok else "FAIL: h-chain audit")
raise SystemExit(0 if ok else 1)
