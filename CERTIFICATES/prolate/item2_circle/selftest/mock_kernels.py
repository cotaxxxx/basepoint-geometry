#!/usr/bin/env python3
"""HARNESS SELF-TEST ONLY — mathematically meaningless mock of the item-0
kernel interface. Lets B-SEED and B-TUBE be exercised end-to-end before the
real vendored kernels arrive. The mock branch is r_c(lam) = 1/2 + (lam-5)/200
with a strictly increasing cubic in r around it."""
import math
from flint import arb

def _rc_float(lam): return 0.5 + (lam - 5.0) / 200.0

def F_float(r, lam):
    d = r - _rc_float(lam)
    return d + d * d * d

def dFdr_float(r, lam):
    d = r - _rc_float(lam)
    return 1.0 + 3.0 * d * d

def _rc_arb(lam: arb) -> arb:
    return arb(1) / 2 + (lam - 5) / 200

def F_arb(r: arb, lam: arb) -> arb:
    d = r - _rc_arb(lam)
    return d + d * d * d

def dFdr_arb(r: arb, lam: arb) -> arb:
    d = r - _rc_arb(lam)
    return 1 + 3 * d * d
