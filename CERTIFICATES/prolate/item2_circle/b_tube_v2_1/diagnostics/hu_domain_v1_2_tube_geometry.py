#!/usr/bin/env python3
"""Exact MONOTONE_TUBE_V1.1 geometry reconstruction for H_U production.

No parent rectangle is trusted as an input.  The parent is reconstructed from
Component-1 candidate inputs q_left, q_right, sigma, rho_cap and the exact cell
partition inputs lambda_start, W_nom, lambda_end, cell_index.
"""
from __future__ import annotations
from fractions import Fraction
from typing import Any

class GeometryError(RuntimeError):
    pass

def fail(code: str) -> None:
    raise GeometryError(code)

def exact(value: Any, where: str) -> Fraction:
    if not isinstance(value, str) or "/" not in value:
        fail("NONCANONICAL_FRACTION:" + where)
    try:
        q = Fraction(value)
    except Exception:
        fail("BAD_FRACTION:" + where)
    if value != f"{q.numerator}/{q.denominator}":
        fail("NONCANONICAL_FRACTION:" + where)
    return q

def fstr(q: Fraction) -> str:
    return f"{q.numerator}/{q.denominator}"

def derive_parent(component1: dict[str, Any]) -> dict[str, str]:
    if component1.get("contract") != "MONOTONE_TUBE_V1_1":
        fail("GEOMETRY_CONTRACT")
    if component1.get("component") != "TUBE_GEOMETRY":
        fail("GEOMETRY_COMPONENT")
    c = component1.get("candidate_inputs")
    if not isinstance(c, dict):
        fail("CANDIDATE_INPUTS")
    q_left = exact(c.get("q_left"), "q_left")
    q_right = exact(c.get("q_right"), "q_right")
    sigma = exact(c.get("sigma"), "sigma")
    rho_cap = exact(c.get("rho_cap"), "rho_cap")
    lambda_start = exact(c.get("lambda_start"), "lambda_start")
    w_nom = exact(c.get("W_nom"), "W_nom")
    lambda_end = exact(c.get("lambda_end"), "lambda_end")
    cell_index = c.get("cell_index")
    if not isinstance(cell_index, int) or cell_index < 0:
        fail("CELL_INDEX")
    if not (0 < sigma < 1 and rho_cap > 0 and w_nom > 0 and lambda_start < lambda_end):
        fail("CANDIDATE_RANGE")
    q_lo, q_hi = min(q_left, q_right), max(q_left, q_right)
    if not (0 < q_lo <= q_hi < 1):
        fail("Q_HULL_STRICT_INTERIOR")
    rho = min(rho_cap, sigma * q_lo, sigma * (1 - q_hi))
    if rho <= 0:
        fail("RHO_NONPOSITIVE")
    r_lo, r_hi = q_lo - rho, q_hi + rho
    lambda_lo = lambda_start + cell_index * w_nom
    if not lambda_lo < lambda_end:
        fail("CELL_INDEX_OUTSIDE_PARTITION")
    lambda_hi = min(lambda_lo + w_nom, lambda_end)
    if not (0 < r_lo < r_hi < 1 and lambda_lo < lambda_hi):
        fail("DERIVED_PARENT_RANGE")
    reported = component1.get("derived_geometry")
    derived = {
        "r_lo": fstr(r_lo),
        "r_hi": fstr(r_hi),
        "lambda_lo": fstr(lambda_lo),
        "lambda_hi": fstr(lambda_hi),
        "rho": fstr(rho),
        "q_hull_lo": fstr(q_lo),
        "q_hull_hi": fstr(q_hi),
    }
    if reported is not None:
        if not isinstance(reported, dict):
            fail("DERIVED_GEOMETRY_RECORD")
        for k, v in derived.items():
            if reported.get(k) != v:
                fail("DERIVED_GEOMETRY_MISMATCH:" + k)
    return derived

def parent_record(component1: dict[str, Any], box_id: str) -> dict[str, Any]:
    d = derive_parent(component1)
    return {
        "box_id": box_id,
        "parent_id": None,
        "generation": 0,
        "r_lo": d["r_lo"],
        "r_hi": d["r_hi"],
        "lambda_lo": d["lambda_lo"],
        "lambda_hi": d["lambda_hi"],
    }
