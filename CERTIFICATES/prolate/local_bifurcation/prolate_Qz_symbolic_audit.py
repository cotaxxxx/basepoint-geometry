#!/usr/bin/env python3
"""Exact symbolic audit of the axial second-derivative kernel used by Paper 1."""
import sympy as sp

t = sp.symbols("t")
C, ell, v, w = sp.symbols("C ell v w", nonzero=True)
h0, h1, h2 = sp.symbols("h0 h1 h2")
A = 1 - w*t
B = 1 - 2*v*t/ell + t**2/ell
g = C*A*B**sp.Rational(-1,2)
delta = g - C
# Second-order jet of h(g); sufficient and independent for F(0).
hjet = h0 + h1*delta + sp.Rational(1,2)*h2*delta**2
raw = sp.simplify(sp.diff(A*hjet, t, 2).subs(t, 0))
expected = sp.simplify(
    C**2*h2*(v/ell - w)**2
    + C*h1*(-1/ell + 3*v**2/ell**2 - 4*w*v/ell + 2*w**2)
)
difference = sp.factor(sp.together(raw - expected))
if difference != 0:
    print("FAIL")
    print("difference =", difference)
    raise SystemExit(1)
print("PASS")
print("certificate_id = PROLATE-LOCAL-QZ-SYMBOLIC-2026-09-NEWCHAIN-v1")
print("identity: raw Fz(0) - canonical kernel = 0")
