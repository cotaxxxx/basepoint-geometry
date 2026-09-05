#!/usr/bin/env python3
"""Exact no-jet symbolic audit of the axial second-derivative kernel used by Paper 1."""
import sympy as sp

t = sp.symbols("t", real=True)
C, ell, v, w = sp.symbols("C ell v w", positive=True)
h = sp.Function("h")
h1, h2 = sp.symbols("h1 h2")
A = 1 - w*t
B = 1 - 2*v*t/ell + t**2/ell
g = C*A*B**sp.Rational(-1, 2)
raw = sp.diff(A*h(g), t, 2).subs(t, 0)
xi = sp.Symbol("_xi_1")
raw = raw.xreplace({
    sp.Subs(sp.Derivative(h(xi), xi), xi, C): h1,
    sp.Subs(sp.Derivative(h(xi), (xi, 2)), xi, C): h2,
    sp.Derivative(h(C), C): h1,
    sp.Derivative(h(C), (C, 2)): h2,
})
if raw.atoms(sp.Derivative, sp.Subs):
    print("FAIL: unresolved derivatives remain")
    print(raw.atoms(sp.Derivative, sp.Subs))
    raise SystemExit(1)
expected = (
    C**2*h2*(v/ell - w)**2
    + C*h1*(-1/ell + 3*v**2/ell**2 - 4*w*v/ell + 2*w**2)
)
difference = sp.simplify(sp.expand(sp.simplify(raw) - expected))
if difference != 0:
    print("FAIL")
    print("difference =", difference)
    raise SystemExit(1)
print("PASS")
print("certificate_id = PROLATE-LOCAL-QZ-SYMBOLIC-2026-09-NEWCHAIN-v2")
print("identity: raw weighted kernel second derivative - canonical kernel = 0")
print("method: abstract h, no Taylor-jet truncation")
