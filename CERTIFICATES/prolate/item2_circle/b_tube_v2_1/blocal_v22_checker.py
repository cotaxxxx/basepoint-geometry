#!/usr/bin/env python3
"""Independent structural/exact-arithmetic checker for B-LOCAL v2.2 finite routes."""
from __future__ import annotations
from fractions import Fraction
from typing import Any
import blocal_v22_model as model
import blocal_v22_policy as policy

CHECKER_ID=model.CHECKER_ID

def verify_symbolic_audit_result(result:dict[str,Any])->None:
    model.need(isinstance(result,dict) and result.get("exact_algebra") is True,"symbolic exact algebra")
    model.need(result.get("F_route_exact") is True and result.get("J_equals_rho_K") is True,"symbolic route identities")
    model.need(result.get("numeric_substitution_used_as_proof") is False,"symbolic numeric substitution forbidden")


def _strict_overlap(a:tuple[Fraction,Fraction,Fraction,Fraction],b:tuple[Fraction,Fraction,Fraction,Fraction])->bool:
    return max(a[0],b[0])<min(a[1],b[1]) and max(a[2],b[2])<min(a[3],b[3])
def _cover(rects:list[tuple[Fraction,Fraction,Fraction,Fraction]],target:tuple[Fraction,Fraction,Fraction,Fraction],where:str)->None:
    model.need(rects,f"{where}: nonempty");area=Fraction(0);a0,a1,b0,b1=target
    for i,r in enumerate(rects):
        model.need(a0<=r[0]<r[1]<=a1 and b0<=r[2]<r[3]<=b1,f"{where}: containment");area+=(r[1]-r[0])*(r[3]-r[2])
        for q in rects[:i]:model.need(not _strict_overlap(r,q),f"{where}: overlap")
    model.need(area==(a1-a0)*(b1-b0),f"{where}: exact cover")
def _cover1(records:list[dict[str,Any]],lo:Fraction,hi:Fraction,node:str)->None:
    iv=[]
    for r in records:
        a,b=model.interval_fractions(r["s_interval"],f"{node}.s");model.need(lo<=a<b<=hi,f"{node}: containment");iv.append((a,b))
    iv.sort();model.need(iv and iv[0][0]==lo and iv[-1][1]==hi,f"{node}: endpoints")
    for i in range(1,len(iv)):model.need(iv[i-1][1]==iv[i][0],f"{node}: adjacency")

def _proof_hash(body:dict[str,Any])->str:
    x={k:v for k,v in body.items() if k!="proof_id"};return model.sha256_bytes(model.canonical_json_bytes(x))

def verify_route_proof(p:dict[str,Any],config:dict[str,Any],quantity:str)->None:
    model.need(isinstance(p,dict),"route proof object")
    model.need(p["route_id"]==(policy.F_ROUTE_ID if quantity=="F" else policy.K_ROUTE_ID),"route id")
    model.need(p["quantity"]==quantity,"route quantity");model.need(p["direct_pinned_integrator_called"] is False,"direct integrator forbidden")
    model.need(p["angular_policy_id"]==policy.ANGULAR_POLICY_ID and p["denominator_policy_id"]==policy.DENOMINATOR_POLICY_ID,"policy ids")
    model.need(p["gamma_policy_id"]==policy.GAMMA_POLICY_ID and p["q_lo_policy_id"]==policy.Q_LO_POLICY_ID,"gamma/q policies")
    model.need(p["normalization_policy_id"]==policy.NORMALIZATION_POLICY_ID,"normalization policy")
    model.need(p["one_over_pi_enclosure"]=={"lo":model.rational_json(model.ONE_OVER_PI_LO),"hi":model.rational_json(model.ONE_OVER_PI_HI)},"1/pi bounds")
    model.need(p["normalization_bits"]==model.NORMALIZATION_BITS,"normalization bits")
    model.need(p["eps"]==config["geometry"]["eps"] and p["patch_type"]==model.PATCH_TYPE,"eps/patch")
    model.need(p["complete_closed_cover"] is True,"complete cover marker")
    children=p["ordered_children"];model.need(isinstance(children,list) and children,"children")
    contributions=[]
    for region in ("T1","T2","R1","R2"):
        rects=[]
        for c in children:
            if c["region"]!=region:continue
            a0,a1=model.interval_fractions(c["box"]["a"],"child a");b0,b1=model.interval_fractions(c["box"]["b"],"child b")
            rects.append((a0,a1,b0,b1));model.need(c["status"]=="ACCEPTED","child accepted")
            d=c["detail"];model.need(d["gamma_policy"]==policy.GAMMA_POLICY_ID,"child gamma policy")
            if region in ("R1","R2"):
                model.need(model.fraction_from_rational(d["q_lo"])>0,"q_lo positive");model.need(d["denominator_policy"]==policy.DENOMINATOR_POLICY_ID,"sequential denominator")
            else:
                model.need(model.fraction_from_rational(d["Z_DEN_LO"])>0,"Z_DEN_LO positive");model.need(d["duffy_id"]==policy.DUFFY_ID,"Duffy id")
                model.need(d["triangle_substitution"]==region,"triangle substitution")
                if a0==0:model.need(d["bounded_extensions"]["y_h"]=="[0,1]" and d["bounded_extensions"]["z"]=="[0,1/sqrt(Z_DEN_LO)]","corner bounded extensions")
            model.need(d["measure_identity"]==policy.MEASURE_ID,"measure identity")
            model.interval_fractions(c["contribution_enclosure"],"child contribution");contributions.append(c["contribution_enclosure"])
        _cover(rects,(Fraction(0),Fraction(1),Fraction(0),Fraction(1)),f"route {region}")
    slo,shi=model.interval_add_exact(contributions);expected_unnorm=model.outward_dyadic(slo,shi)
    model.need(p["unnormalized_sum"]==expected_unnorm,"unnormalized reconstruction")
    model.need(p["normalized_enclosure"]==model.normalize_interval(expected_unnorm),"normalized reconstruction")
    model.need(p["proof_id"]==_proof_hash(p),"proof id")

def _rect_from_l1(r:dict[str,Any])->tuple[Fraction,Fraction,Fraction,Fraction]:
    u0,u1=model.interval_fractions(r["u_interval"],"L1 u");s0,s1=model.interval_fractions(r["s_interval"],"L1 s");return u0,u1,s0,s1

def _check_tile(r:dict[str,Any],config:dict[str,Any],node:str)->None:
    model.need(r["record_type"]==f"{node}_TILE" and r["node"]==node,"tile identity")
    sign="POS" if node in ("L1","L2") else "NEG";lo,hi=model.interval_fractions(r["enclosure"],"tile enclosure")
    model.need(bool(r["certified"])==((lo>0) if sign=="POS" else (hi<0)),"tile predicate")
    if r["route_proof"] is not None:
        verify_route_proof(r["route_proof"],config,"H_U" if node=="L1" else "F")
        model.need(r["enclosure"]==r["route_proof"]["normalized_enclosure"],"tile/proof enclosure")

def _check_j(j:dict[str,Any],u_max:Fraction,lambda_start:Fraction,config:dict[str,Any])->None:
    model.need(j["record_type"]=="J_START" and j["certified"] is True,"J identity")
    model.need(j["direct_pinned_F_arb_called"] is False and j["direct_pinned_dFdr_arb_called"] is False,"J direct integrators")
    b0,b1=model.interval_fractions(j["initial_bracket"],"J initial");model.need((b0,b1)==(1-u_max,Fraction(1)),"J initial bracket")
    points=j["ordered_bisection_records"];model.need(points,"J points")
    first=points[0];model.need(model.fraction_from_rational(first["r"])==b0 and first["sign"]=="POSITIVE","J left")
    verify_route_proof(first["route_proof"],config,"F")
    left,right=b0,Fraction(1);negative_found=False
    by_id={p["evaluation_id"]:p for p in points}
    for p in points:
        model.need(model.fraction_from_rational(p["lambda_start"])==lambda_start,"J lambda")
        verify_route_proof(p["route_proof"],config,"F");model.need(p["normalized_F"]==p["route_proof"]["normalized_enclosure"],"J point enclosure")
        rr=model.fraction_from_rational(p["r"]);pu0,pu1=model.interval_fractions(p["route_proof"]["u_interval"],"J point proof u")
        ps0,ps1=model.interval_fractions(p["route_proof"]["s_interval"],"J point proof s");ss=lambda_start-model.LAMBDA_PLUS
        model.need((pu0,pu1)==(1-rr,1-rr) and (ps0,ps1)==(ss,ss),"J point route domain")
        lo,hi=model.interval_fractions(p["normalized_F"],"J point");expected="POSITIVE" if lo>0 else "NEGATIVE" if hi<0 else "UNRESOLVED";model.need(p["sign"]==expected,"J point sign")
        if p is first or p["role"]=="NEWTON_MIDPOINT":continue
        r=model.fraction_from_rational(p["r"]);model.need(r==(left+right)/2,"J exact midpoint")
        if p["role"]=="RETAINED_LEFT":model.need(expected=="POSITIVE","J left update sign");left=r
        elif p["role"]=="RETAINED_RIGHT":model.need(expected=="NEGATIVE","J right update sign");right=r;negative_found=True;break
        else:model.need(False,"J bisection role")
    model.need(negative_found and right<1,"J interior right")
    rlo,rhi=model.interval_fractions(j["r_interval"],"J final");model.need((rlo,rhi)==(left,right),"J final bracket")
    d=j["derivative_record"];model.need(d["route_id"]==policy.K_ROUTE_ID,"J derivative route");verify_route_proof(d["route_proof"],config,"H_U")
    ulo,uhi=model.interval_fractions(d["u_interval"],"J u map");model.need((ulo,uhi)==(1-right,1-left),"J u map")
    model.need(d["negation_rule_id"]==policy.NEGATION_RULE_ID and d["F_r"]==model.interval_negate(d["H_u"]),"J negation")
    dlo,dhi=model.interval_fractions(d["F_r"],"J D");model.need(dhi<0 and d["sup_F_r_lt_zero"] is True,"J derivative negative")
    n=j["newton_record"];model.need(n["interval_arithmetic_policy_id"]==policy.NEWTON_POLICY_ID,"Newton policy")
    mid=model.fraction_from_rational(n["midpoint"]);model.need(mid==(left+right)/2,"Newton midpoint")
    model.need(n["midpoint_F_record_id"] in by_id,"Newton F ref");mp=by_id[n["midpoint_F_record_id"]];model.need(mp["role"]=="NEWTON_MIDPOINT","Newton role")
    Fm=mp["normalized_F"];model.need(n["F_m"]==Fm and n["D"]==d["F_r"],"Newton operands")
    qlo,qhi=model.interval_divide_negative_denominator(Fm,d["F_r"]);qiv=model.outward_dyadic(qlo,qhi);model.need(n["quotient"]==qiv,"Newton quotient")
    niv=model.outward_dyadic(mid-qhi,mid-qlo);model.need(n["newton_image"]==niv,"Newton image")
    x0,x1=model.interval_fractions(niv,"Newton image");model.need(left<x0<=x1<right and n["strict_self_containment"] is True,"Newton self containment")

def _candidate(block:list[dict[str,Any]],summary:dict[str,Any],config:dict[str,Any])->bool:
    idx=summary["candidate_index"];s_start=model.fraction_from_rational(summary["lambda_start"])-model.LAMBDA_PLUS;u_max=model.fraction_from_dyadic(summary["u_max"])
    l1=[r for r in block if r.get("node")=="L1"];l2=[r for r in block if r.get("node")=="L2"];l3=[r for r in block if r.get("node")=="L3"]
    for r in l1+l2+l3:model.need(r["candidate_index"]==idx,"candidate index");_check_tile(r,config,r["node"])
    _cover([_rect_from_l1(r) for r in l1],(Fraction(0),u_max,-model.S_NEG,s_start),"L1")
    _cover1(l2,-model.S_NEG,s_start,"L2");_cover1(l3,Fraction(0),s_start,"L3")
    ok1=all(r["certified"] for r in l1);ok2=all(r["certified"] for r in l2);ok3=all(r["certified"] for r in l3)
    js=[r for r in block if r.get("record_type")=="J_START"]
    if js:_check_j(js[0],u_max,model.LAMBDA_PLUS+s_start,config)
    accepted=ok1 and ok2 and ok3 and len(js)==1
    model.need(summary["candidate_accepted"] is accepted,"candidate accepted")
    return accepted

def verify_records(records:list[dict[str,Any]],config:dict[str,Any],config_hash:str)->dict[str,Any]:
    model.validate_config(config);model.need(isinstance(records,list) and len(records)>=2,"records")
    prev=model.chain_genesis(config_hash)
    for r in records:
        model.need(r.get("previous_record_sha256")==prev,"chain predecessor");model.need(r.get("record_sha256")==model.record_hash(r),"record hash");prev=r["record_sha256"]
    h,f=records[0],records[-1];model.need(h["record_type"]=="RUN_HEADER" and h["chain_genesis"]==model.chain_genesis(config_hash),"header")
    model.need(f["record_type"]=="RUN_SUMMARY","summary")
    accepted=[];block=[];expected=0
    for r in records[1:-1]:
        if r.get("record_type")=="CANDIDATE_SUMMARY":
            model.need(r["candidate_index"]==expected,"candidate order")
            if _candidate(block,r,config):accepted.append(expected)
            expected+=1;block=[]
        else:block.append(r)
    model.need(not block and len(accepted)<=1,"candidate blocks")
    if accepted:
        model.need(accepted[0]==expected-1 and f["selected_candidate_index"]==accepted[0] and f["terminal_state"]==model.COMPLETE,"first passing")
    else:model.need(f["selected_candidate_index"] is None and f["terminal_state"]==model.INCOMPLETE,"incomplete")
    return {"checker_id":CHECKER_ID,"valid":True,"candidate_summaries":expected,"accepted_candidate_index":accepted[0] if accepted else None,
            "all_F_Fr_consumers_finite_routes":True,"closed_coverage_checked":True,"route_trees_checked":True,"J_START_reconstructed":True}
