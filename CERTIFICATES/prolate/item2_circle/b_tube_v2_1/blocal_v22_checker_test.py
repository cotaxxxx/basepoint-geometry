#!/usr/bin/env python3
"""Calculation-free negative controls for the B-LOCAL v2.2 checker."""
from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path

import blocal_v22_checker as checker
import blocal_v22_model as model

HERE=Path(__file__).resolve(strict=True).parent


def rejects(fn, label: str) -> None:
    try: fn()
    except Exception: return
    raise RuntimeError(f"negative control accepted: {label}")


def main() -> int:
    config=model.parse_canonical_json((HERE/"config.blocal-v2.2-run.json").read_bytes())
    model.validate_config(config)
    rejects(lambda: checker._verify_rect_cover(
        [(Fraction(0),Fraction(1,4),Fraction(0),Fraction(1)),
         (Fraction(1,2),Fraction(1),Fraction(0),Fraction(1))],
        (Fraction(0),Fraction(1),Fraction(0),Fraction(1)),"gap"),"coverage gap")
    rejects(lambda: checker._verify_rect_cover(
        [(Fraction(0),Fraction(3,4),Fraction(0),Fraction(1)),
         (Fraction(1,2),Fraction(1),Fraction(0),Fraction(1))],
        (Fraction(0),Fraction(1),Fraction(0),Fraction(1)),"overlap"),"coverage overlap")
    bad=copy.deepcopy(config);bad["boundary_strip"]["u_cut"]={"m":"0","e":0}
    rejects(lambda:model.validate_config(bad),"u_cut <= 0")
    bad=copy.deepcopy(config);bad["boundary_strip"]["patch_type"]="CIRCULAR_PATCH"
    rejects(lambda:model.validate_config(bad),"circular patch")
    rec={
      "record_type":"BOUNDARY_STRIP_TILE","node":"L1_BOUNDARY","closed_subdomain":"L1_BOUNDARY_STRIP",
      "diagnostics":{"lemma_id":model.BOUNDARY_LEMMA_ID,"route_id":model.BOUNDARY_ROUTE_ID,
        "patch_type":model.PATCH_TYPE,"regularization_method":model.REGULARIZATION_METHOD,
        "eps":config["boundary_strip"]["eps"],"u_cut":config["boundary_strip"]["u_cut"],
        "z_den_lo":{"T1":{"p":"0","q":"1"},"T2":{"p":"1","q":"1"}},
        "q_min":{"R1":{"p":"1","q":"1"},"R2":{"p":"1","q":"1"}},
        "algebraic_bounds":{"y":"[0,1]","v":"[-1,1]","gamma":"[0,1]"},
        "duffy_triangles":["T1","T2"],"regular_regions":["R1","R2"],
        "sin_theta_dtheta_cancelled_symbolically":True,
        "independent_one_over_sqrt_one_minus_c2_evaluated":False},
      "piece_enclosures":{k:model.interval_json(Fraction(0),Fraction(0)) for k in ("T1","T2","R1","R2")},
      "enclosure":model.interval_json(Fraction(1),Fraction(2)),"certified":True,
      "strict_predicate":"LOWER_GT_ZERO",
      "boundary_route_source_sha256":config["implementation"]["sources_sha256"][
        "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"],
      "symbolic_audit_source_sha256":config["symbolic_audit"]["source_sha256"]}
    rejects(lambda:checker._verify_boundary_record(rec,config),"Z_DEN_LO <= 0")
    print("BLOCAL_V22_CHECKER_NEGATIVE_CONTROLS_PASS")
    return 0


if __name__=="__main__": raise SystemExit(main())
