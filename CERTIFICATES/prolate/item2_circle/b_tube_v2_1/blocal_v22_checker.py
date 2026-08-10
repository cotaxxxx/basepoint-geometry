#!/usr/bin/env python3
"""Independent structural checker for B-LOCAL v2.2 coverage records."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

import blocal_v22_model as model

CHECKER_ID = model.CHECKER_ID


def _rect(record: dict[str,Any]) -> tuple[Fraction,Fraction,Fraction,Fraction]:
    u0,u1=model.interval_fractions(record["u_interval"],"u_interval")
    s0,s1=model.interval_fractions(record["s_interval"],"s_interval")
    return u0,u1,s0,s1


def _strict_interior_overlap(a: tuple[Fraction,Fraction,Fraction,Fraction],
                             b: tuple[Fraction,Fraction,Fraction,Fraction]) -> bool:
    return max(a[0],b[0]) < min(a[1],b[1]) and max(a[2],b[2]) < min(a[3],b[3])


def _verify_rect_cover(rects: list[tuple[Fraction,Fraction,Fraction,Fraction]],
                       target: tuple[Fraction,Fraction,Fraction,Fraction],where: str) -> None:
    model.need(rects, f"{where}: nonempty")
    tu0,tu1,ts0,ts1=target
    area=Fraction(0)
    for i,r in enumerate(rects):
        u0,u1,s0,s1=r
        model.need(tu0<=u0<=u1<=tu1 and ts0<=s0<=s1<=ts1,f"{where}: containment")
        model.need(u0<u1 and s0<s1,f"{where}: positive tile area")
        area+=(u1-u0)*(s1-s0)
        for other in rects[:i]:
            model.need(not _strict_interior_overlap(r,other),f"{where}: interior overlap")
    model.need(area==(tu1-tu0)*(ts1-ts0),f"{where}: exact area cover")


def _verify_1d_cover(records: list[dict[str,Any]],lower: Fraction,upper: Fraction,node: str) -> None:
    intervals=[]
    for r in records:
        s0,s1=model.interval_fractions(r["s_interval"],f"{node}.s")
        model.need(lower<=s0<s1<=upper,f"{node}: interval containment")
        intervals.append((s0,s1))
    intervals.sort()
    model.need(intervals and intervals[0][0]==lower and intervals[-1][1]==upper,f"{node}: endpoints")
    total=Fraction(0)
    for i,(a,b) in enumerate(intervals):
        total+=b-a
        if i: model.need(intervals[i-1][1]==a,f"{node}: exact adjacency")
    model.need(total==upper-lower,f"{node}: exact length")


def _verify_boundary_record(r: dict[str,Any],config: dict[str,Any]) -> None:
    model.need(r["record_type"]=="BOUNDARY_STRIP_TILE" and r["node"]=="L1_BOUNDARY",
               "boundary record identity")
    model.need(r["closed_subdomain"]=="L1_BOUNDARY_STRIP", "boundary subdomain")
    d=r["diagnostics"]
    model.need(d["lemma_id"]==model.BOUNDARY_LEMMA_ID and d["route_id"]==model.BOUNDARY_ROUTE_ID,
               "boundary IDs")
    model.need(d["patch_type"]==model.PATCH_TYPE and d["regularization_method"]==model.REGULARIZATION_METHOD,
               "boundary method")
    model.need(d["eps"]==config["boundary_strip"]["eps"] and d["u_cut"]==config["boundary_strip"]["u_cut"],
               "boundary exact eps/u_cut")
    model.need(set(d["z_den_lo"])=={"T1","T2"} and set(d["q_min"])=={"R1","R2"},
               "boundary lower-bound fields")
    for value in d["z_den_lo"].values():
        model.need(model.fraction_from_rational(value)>0,"Z_DEN_LO > 0")
    for value in d["q_min"].values():
        model.need(model.fraction_from_rational(value)>0,"q_min > 0")
    model.need(d["algebraic_bounds"]=={"y":"[0,1]","v":"[-1,1]","gamma":"[0,1]"},
               "algebraic bounded extensions")
    model.need(d["duffy_triangles"]==["T1","T2"] and d["regular_regions"]==["R1","R2"],
               "exact angular partition labels")
    model.need(d["sin_theta_dtheta_cancelled_symbolically"] is True,
               "sin theta Jacobian cancellation")
    model.need(d["independent_one_over_sqrt_one_minus_c2_evaluated"] is False,
               "forbidden independent c Jacobian")
    model.need(set(r["piece_enclosures"])=={"T1","T2","R1","R2"},"piece enclosures")
    for key,value in r["piece_enclosures"].items():
        model.interval_fractions(value,f"piece {key}")
    lo,_=model.interval_fractions(r["enclosure"],"boundary enclosure")
    model.need((lo>0)==bool(r["certified"]),"boundary strict predicate consistency")
    model.need(r["strict_predicate"]=="LOWER_GT_ZERO","boundary predicate")
    model.need(r["boundary_route_source_sha256"]==config["implementation"]["sources_sha256"][
        "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"],"boundary source pin")
    model.need(r["symbolic_audit_source_sha256"]==config["symbolic_audit"]["source_sha256"],
               "symbolic source pin")


def _verify_candidate(block: list[dict[str,Any]],summary: dict[str,Any],config: dict[str,Any]) -> bool:
    idx=summary["candidate_index"]
    s_start=model.fraction_from_rational(summary["lambda_start"])-model.LAMBDA_PLUS
    u_max=model.fraction_from_dyadic(summary["u_max"])
    u_cut=model.fraction_from_dyadic(summary["u_cut"])
    model.need(summary["u_cut"]==config["boundary_strip"]["u_cut"],"candidate u_cut")
    boundary=[r for r in block if r.get("node")=="L1_BOUNDARY"]
    interior=[r for r in block if r.get("node")=="L1_INTERIOR"]
    l2=[r for r in block if r.get("node")=="L2"]
    l3=[r for r in block if r.get("node")=="L3"]
    for r in boundary:
        model.need(r["candidate_index"]==idx,"boundary candidate index");_verify_boundary_record(r,config)
    for r in interior:
        model.need(r["candidate_index"]==idx and r["closed_subdomain"]=="L1_INTERIOR",
                   "interior candidate/subdomain")
        lo,_=model.interval_fractions(r["enclosure"],"interior enclosure")
        model.need((lo>0)==bool(r["certified"]),"interior strict predicate")
    _verify_rect_cover([_rect(r) for r in boundary],(Fraction(0),u_cut,-model.S_NEG,s_start),"L1 boundary")
    _verify_rect_cover([_rect(r) for r in interior],(u_cut,u_max,-model.S_NEG,s_start),"L1 interior")
    model.need(max(r[1] for r in [_rect(x) for x in boundary])==u_cut,"boundary reaches u_cut")
    model.need(min(r[0] for r in [_rect(x) for x in interior])==u_cut,"interior begins u_cut")
    _verify_1d_cover(l2,-model.S_NEG,s_start,"L2")
    _verify_1d_cover(l3,Fraction(0),s_start,"L3")
    boundary_ok=all(r["certified"] for r in boundary)
    interior_ok=all(r["certified"] for r in interior)
    l2_ok=all(r["certified"] for r in l2); l3_ok=all(r["certified"] for r in l3)
    j=[r for r in block if r.get("record_type")=="J_START"]
    accepted=boundary_ok and interior_ok and l2_ok and l3_ok and len(j)==1
    model.need(summary["node_status"]["L1"]==("CERTIFIED" if boundary_ok and interior_ok else "INCOMPLETE"),
               "combined L1 status")
    model.need(summary["candidate_accepted"] is accepted,"candidate acceptance")
    return accepted


def verify_records(records: list[dict[str,Any]],config: dict[str,Any],config_hash: str) -> dict[str,Any]:
    model.validate_config(config)
    model.need(isinstance(records,list) and len(records)>=2,"record list")
    previous=model.chain_genesis(config_hash)
    for record in records:
        model.need(record.get("previous_record_sha256")==previous,"record chain predecessor")
        model.need(record.get("record_sha256")==model.record_hash(record),"record hash")
        previous=record["record_sha256"]
    header=records[0]; final=records[-1]
    model.need(header["record_type"]=="RUN_HEADER" and header["schema"]==model.SCHEMA,"header")
    model.need(header["chain_genesis"]==model.chain_genesis(config_hash),"header genesis")
    model.need(final["record_type"]=="RUN_SUMMARY","terminal run summary")

    accepted_indices=[]; block=[]; expected_idx=0
    for record in records[1:-1]:
        if record.get("record_type")=="CANDIDATE_SUMMARY":
            model.need(record["candidate_index"]==expected_idx,"candidate order")
            if _verify_candidate(block,record,config): accepted_indices.append(expected_idx)
            expected_idx+=1; block=[]
        else:
            block.append(record)
    model.need(not block,"records after last candidate without summary")
    model.need(len(accepted_indices)<=1,"at most one accepted candidate")
    if accepted_indices:
        model.need(accepted_indices[0]==expected_idx-1,"runner stopped at first accepted candidate")
        model.need(final["selected_candidate_index"]==accepted_indices[0],"selected candidate summary")
        model.need(final["terminal_state"]==model.COMPLETE,"complete terminal state")
    else:
        model.need(final["selected_candidate_index"] is None and final["terminal_state"]==model.INCOMPLETE,
                   "incomplete terminal state")
    return {
        "checker_id":CHECKER_ID,"valid":True,"candidate_summaries":expected_idx,
        "accepted_candidate_index":accepted_indices[0] if accepted_indices else None,
        "l1_boundary_strip_required":True,"l1_interior_required":True,
        "closed_union_checked":True,"chain_checked":True,
    }
