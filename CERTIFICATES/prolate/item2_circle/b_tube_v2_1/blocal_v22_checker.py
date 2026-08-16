#!/usr/bin/env python3
"""Independent structural/exact-arithmetic checker for B-LOCAL v2.2 finite routes."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

import blocal_v22_model as model
import blocal_v22_policy as policy

CHECKER_ID = model.CHECKER_ID


def verify_symbolic_audit_result(result: dict[str, Any]) -> None:
    model.need(isinstance(result, dict) and result.get("exact_algebra") is True,
               "symbolic exact algebra")
    model.need(result.get("F_route_exact") is True and result.get("J_equals_rho_K") is True,
               "symbolic route identities")
    model.need(result.get("numeric_substitution_used_as_proof") is False,
               "symbolic numeric substitution forbidden")


def _strict_overlap(a: tuple[Fraction, Fraction, Fraction, Fraction],
                    b: tuple[Fraction, Fraction, Fraction, Fraction]) -> bool:
    return (max(a[0], b[0]) < min(a[1], b[1])
            and max(a[2], b[2]) < min(a[3], b[3]))


def _cover(rects: list[tuple[Fraction, Fraction, Fraction, Fraction]],
           target: tuple[Fraction, Fraction, Fraction, Fraction],
           where: str) -> None:
    model.need(rects, f"{where}: nonempty")
    a0, a1, b0, b1 = target
    area = Fraction(0)
    for i, r in enumerate(rects):
        model.need(a0 <= r[0] < r[1] <= a1 and b0 <= r[2] < r[3] <= b1,
                   f"{where}: containment")
        area += (r[1]-r[0]) * (r[3]-r[2])
        for q in rects[:i]:
            model.need(not _strict_overlap(r, q), f"{where}: overlap")
    model.need(area == (a1-a0)*(b1-b0), f"{where}: exact cover")


def _cover1(records: list[dict[str, Any]], lo: Fraction, hi: Fraction,
            node: str) -> None:
    intervals: list[tuple[Fraction, Fraction]] = []
    for r in records:
        a, b = model.interval_fractions(r["s_interval"], f"{node}.s")
        model.need(lo <= a < b <= hi, f"{node}: containment")
        intervals.append((a, b))
    intervals.sort()
    model.need(intervals and intervals[0][0] == lo and intervals[-1][1] == hi,
               f"{node}: endpoints")
    for i in range(1, len(intervals)):
        model.need(intervals[i-1][1] == intervals[i][0],
                   f"{node}: adjacency")


def _proof_hash(body: dict[str, Any]) -> str:
    x = {k: v for k, v in body.items() if k != "proof_id"}
    return model.sha256_bytes(model.canonical_json_bytes(x))


def _check_gamma_detail(detail: dict[str, Any]) -> None:
    model.need(detail["gamma_policy"] == policy.GAMMA_POLICY_ID,
               "child gamma policy")
    splits = detail["gamma_subdivisions"]
    model.need(isinstance(splits, list), "gamma subdivisions list")
    model.need(splits,"gamma bin record required")
    model.need(detail["gamma_fallback_used"] is any(x["bin_count"]>1 for x in splits), "gamma fallback marker")
    model.need(detail["gamma_clamp"]=="[0,1]" and detail["gamma_clamp_fail_closed"] is True,"gamma clamp")
    for row in splits:
        lo,hi=model.interval_fractions(row["initial_interval"],"gamma initial")
        cuts=[model.fraction_from_rational(x) for x in row["cuts"]]
        model.need(Fraction(0)<=lo<=hi<=1 and cuts[0]==lo and cuts[-1]==hi,"gamma range/endpoints")
        model.need(all(cuts[i]<cuts[i+1] for i in range(len(cuts)-1)),"gamma ordered cuts")
        model.need(row["bin_count"]==len(cuts)-1 and row["bin_count"]>=1,"gamma bin count")
        model.need(0<=row["max_bin_depth"]<=12 and row["use_count"]>0,"gamma depth/use")


def _check_floor_registry(reg:dict[str,Any])->None:
    model.need(reg["call_sites"]==list(policy.EFFECTIVE_FLOOR_SITES),"exact six floor sites")
    model.need(set(reg["per_site"])==set(policy.EFFECTIVE_FLOOR_SITES),"floor per-site keys")
    c1=reg["c1_structural_uses"]
    model.need(isinstance(c1,int) and not isinstance(c1,bool) and c1>=0,"C1 structural use accounting")
    model.need(isinstance(reg["total_use_count"],int) and not isinstance(reg["total_use_count"],bool)
               and reg["total_use_count"]>=0,"floor total use type")
    total=0
    for site,row in reg["per_site"].items():
        model.need(row["calls"]==row["natural"]+row["structural"] and row["calls"]>=0,"floor site accounting")
        total+=row["calls"]
    model.need(total+c1==reg["total_use_count"],"floor total uses")
    retained=reg["retained"];model.need(len(retained)<=reg["retained_limit"]==64,"floor retained bound")
    model.need(reg["unique_count"]==len(retained)+reg["omitted_count"],"floor unique accounting")
    model.need(reg["truncated"] is (reg["omitted_count"]>0),"floor truncation")
    retained_c1=sum(1 for rec in retained.values() if rec.get("site")=="C1_STRUCTURAL_Q")
    model.need(c1>=retained_c1,"C1 structural retained/use accounting")
    if not reg["truncated"]:
        model.need((c1==0)==(retained_c1==0),"C1 structural presence accounting")
        ordered={k:retained[k] for k in sorted(retained)}
        model.need(model.sha256_bytes(model.canonical_json_bytes(ordered))==reg["canonical_sha256"],"floor canonical digest")
    for dig,rec in retained.items():
        model.need(model.sha256_bytes(model.canonical_json_bytes(rec))==dig,"floor record digest")
        if rec.get("site")=="C1_STRUCTURAL_Q":continue
        model.need(rec["site"] in policy.EFFECTIVE_FLOOR_SITES,"floor enumerated site")
        structural=model.fraction_from_rational(rec["structural"]);effective=model.fraction_from_rational(rec["effective"])
        natural=None if rec["natural"] is None else model.fraction_from_rational(rec["natural"])
        expected=structural if natural is None else max(structural,natural)
        model.need(effective==expected and rec["shared_by"]==["f0","f1","f2"],"effective floor max/shared")
        model.need(rec["selected_source"]==("natural" if natural is not None and natural>structural else "structural"),"floor source")


def verify_route_proof(p: dict[str, Any], config: dict[str, Any],
                       quantity: str) -> None:
    model.need(isinstance(p, dict), "route proof object")
    expected_route = policy.F_ROUTE_ID if quantity == "F" else policy.K_ROUTE_ID
    model.need(p["route_id"] == expected_route, "route id")
    model.need(p["quantity"] == quantity, "route quantity")
    model.need(p["direct_pinned_integrator_called"] is False,
               "direct integrator forbidden")
    model.need(p["angular_policy_id"] == policy.ANGULAR_POLICY_ID,
               "angular policy id")
    model.need(p["denominator_policy_id"] == policy.DENOMINATOR_POLICY_ID,
               "denominator policy id")
    model.need(p["sqrt_policy_id"] == policy.SQRT_POLICY_ID,
               "sqrt policy id")
    model.need(p["gamma_policy_id"] == policy.GAMMA_POLICY_ID,
               "gamma policy id")
    model.need(p["q_lo_policy_id"] == policy.Q_LO_POLICY_ID,
               "q policy id")
    model.need(p["normalization_policy_id"] == policy.NORMALIZATION_POLICY_ID,
               "normalization policy")
    model.need(p["one_over_pi_enclosure"] == {
        "lo": model.rational_json(model.ONE_OVER_PI_LO),
        "hi": model.rational_json(model.ONE_OVER_PI_HI),
    }, "1/pi bounds")
    model.need(p["normalization_bits"] == model.NORMALIZATION_BITS,
               "normalization bits")
    model.need(p["eps"] == config["geometry"]["eps"]
               and p["patch_type"] == model.PATCH_TYPE, "eps/patch")
    model.need(p["complete_closed_cover"] is True, "complete cover marker")
    model.need(p["method_selection_addendum_sha256"]=="7fafe5f465f9f38e61831b804a4bc95090af41b8fe31347897e7b2f40bf3d316","addendum pin")
    _check_floor_registry(p["effective_floor_registry"])

    eps = model.fraction_from_dyadic(config["geometry"]["eps"])
    children = p["ordered_children"]
    model.need(isinstance(children, list) and children, "children")
    contributions: list[dict[str, Any]] = []

    for region in ("T1", "T2", "R2", "C1", "TH"):
        rects: list[tuple[Fraction, Fraction, Fraction, Fraction]] = []
        for child in children:
            if child["region"] != region:
                continue
            a0, a1 = model.interval_fractions(child["box"]["a"], "child a")
            b0, b1 = model.interval_fractions(child["box"]["b"], "child b")
            rects.append((a0, a1, b0, b1))
            model.need(child["status"] == "ACCEPTED", "child accepted")
            d = child["detail"]
            _check_gamma_detail(d)
            model.need(d["sqrt_policy"] == policy.SQRT_POLICY_ID,
                       "child sqrt policy")
            model.need(d["measure_identity"] == policy.MEASURE_ID,
                       "measure identity")

            if region in ("R2", "C1", "TH"):
                qlo = model.fraction_from_rational(d["q_lo"])
                qhi = model.fraction_from_rational(d["q_hi"])
                model.need(qlo > 0 and qhi >= qlo,
                           "regular exact q endpoint bounds")
                model.need(d["q_lo_policy"] == policy.Q_LO_POLICY_ID,
                           "regular q policy")
                model.need(d["denominator_policy"] == policy.DENOMINATOR_POLICY_ID,
                           "regular exact-endpoint reciprocal denominator")
                model.need(d["taylor_order"]==2 and "area*w^2/24" in d["remainder_rule"],"Taylor2 remainder")
                model.need(isinstance(d["effective_floor_record_sha256"],list),"Taylor floor refs")
                if region=="C1":model.need(d["c1_q_floor_source"].startswith("C1_"),"C1 structural floor")
            else:
                zden = model.fraction_from_rational(d["Z_DEN_LO"])
                model.need(zden > 0, "Z_DEN_LO positive")
                model.need(d["duffy_id"] == policy.DUFFY_ID, "Duffy id")
                model.need(d["local_geometry"]==["S","U","W","B","q"],"Duffy local geometry")
                model.need(d["triangle_substitution"] == region,
                           "triangle substitution")
                comps=d["Duffy_Z_components"]
                aa=model.fraction_from_rational(comps["Ahat_lo"]);rb=model.fraction_from_rational(comps["r_lo2_Bhat_lo"]);ww=model.fraction_from_rational(comps["u0_2_over_rho2_hi"])
                model.need(zden==max(Fraction(0),aa)+max(Fraction(0),rb)+max(Fraction(0),ww),"Duffy strengthened Z")
                if a0 == 0:
                    model.need(
                        d["bounded_extensions"]["y_h"] == "[0,1]"
                        and d["bounded_extensions"]["z"]
                        == "[0,1/sqrt(Z_DEN_LO)]",
                        "corner bounded extensions")
                else:
                    model.need(d["denominator_policy"]
                               == policy.DENOMINATOR_POLICY_ID,
                               "Duffy exact-endpoint reciprocal denominator")
                    qhi = model.fraction_from_rational(d["q_hi"])
                    rho2_lo = eps*eps*a0*a0*(1+b0*b0)
                    qlo = rho2_lo*zden
                    model.need(qlo > 0 and qhi >= qlo,
                               "Duffy child exact q endpoint bounds")

            model.interval_fractions(child["contribution_enclosure"],
                                     "child contribution")
            contributions.append(child["contribution_enclosure"])
        _cover(rects,
               (Fraction(0), Fraction(1), Fraction(0), Fraction(1)),
               f"route {region}")

    slo, shi = model.interval_add_exact(contributions)
    expected_unnorm = model.outward_dyadic(slo, shi)
    model.need(p["unnormalized_sum"] == expected_unnorm,
               "unnormalized reconstruction")
    model.need(p["normalized_enclosure"]
               == model.normalize_interval(expected_unnorm),
               "normalized reconstruction")
    model.need(p["proof_id"] == _proof_hash(p), "proof id")


def _rect_from_l1(r: dict[str, Any]
                  ) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    u0, u1 = model.interval_fractions(r["u_interval"], "L1 u")
    s0, s1 = model.interval_fractions(r["s_interval"], "L1 s")
    return u0, u1, s0, s1


def _check_tile(r: dict[str, Any], config: dict[str, Any], node: str) -> None:
    model.need(r["record_type"] == f"{node}_TILE" and r["node"] == node,
               "tile identity")
    sign = "POS" if node in ("L1", "L2") else "NEG"
    lo, hi = model.interval_fractions(r["enclosure"], "tile enclosure")
    model.need(bool(r["certified"])
               == ((lo > 0) if sign == "POS" else (hi < 0)),
               "tile predicate")
    if r["route_proof"] is not None:
        verify_route_proof(r["route_proof"], config,
                           "H_U" if node == "L1" else "F")
        model.need(r["enclosure"]
                   == r["route_proof"]["normalized_enclosure"],
                   "tile/proof enclosure")


def _check_j(j: dict[str, Any], u_max: Fraction, lambda_start: Fraction,
             config: dict[str, Any]) -> None:
    model.need(j["record_type"] == "J_START" and j["certified"] is True,
               "J identity")
    model.need(j["direct_pinned_F_arb_called"] is False
               and j["direct_pinned_dFdr_arb_called"] is False,
               "J direct integrators")
    b0, b1 = model.interval_fractions(j["initial_bracket"], "J initial")
    model.need((b0, b1) == (1-u_max, Fraction(1)), "J initial bracket")
    points=j["ordered_bisection_records"];model.need(points,"J signed points")
    first=points[0];model.need(model.fraction_from_rational(first["r"])==b0 and first["sign"]=="POSITIVE","J left")
    ss=lambda_start-model.LAMBDA_PLUS
    def check_point(point:dict[str,Any],rr:Fraction)->None:
        verify_route_proof(point["route_proof"],config,"F")
        model.need(point["normalized_F"]==point["route_proof"]["normalized_enclosure"],"J F proof binding")
        pu0,pu1=model.interval_fractions(point["route_proof"]["u_interval"],"J F u")
        ps0,ps1=model.interval_fractions(point["route_proof"]["s_interval"],"J F s")
        model.need((pu0,pu1)==(1-rr,1-rr) and (ps0,ps1)==(ss,ss),"J F exact domain")
    check_point(first,b0)
    full=j["condition5_derivative_record"];verify_route_proof(full["route_proof"],config,"H_U")
    model.need(full["H_u"]==full["route_proof"]["normalized_enclosure"] and full["F_r"]==model.interval_negate(full["H_u"]),"condition5 endpoint reversal")
    fu0,fu1=model.interval_fractions(full["u_interval"],"condition5 u")
    _,fhi=model.interval_fractions(full["F_r"],"condition5 Fr")
    model.need((fu0,fu1)==(0,u_max) and fhi<0 and full["endpoint_transform"]=={"rule":"[H_lo,H_hi] -> [-H_hi,-H_lo]","label_only":False},"condition5")
    left,right=b0,Fraction(1);signed_index=1;steps=j["newton_steps"]
    model.need(0<len(steps)<=config["budgets"]["J_START"]["max_bisections"],"Newton step budget")
    derivative_total=full["route_proof"]["evaluation_count"]
    for i,step in enumerate(steps):
        model.need(step["step_index"]==i and model.interval_fractions(step["bracket"],"step bracket")== (left,right),"step bracket")
        mid=model.fraction_from_rational(step["midpoint"]);model.need(mid==(left+right)/2,"step midpoint")
        u0,u1=model.interval_fractions(step["coordinate_map"]["u_interval"],"step u")
        model.need((u0,u1)==(1-right,1-left) and step["coordinate_map"]["exact_rational"] is True,"exact r-u map")
        trials=step["derivative_target_trials"];seen=[]
        for trial in trials:
            target=model.fraction_from_rational(trial["target"]);seen.append(target)
            model.need(trial["status"] in ("REACHED","NOT_REACHED") and trial["evaluations"]>0,"target trial")
        model.need(seen==[Fraction(x) for x in policy.DERIVATIVE_TARGET_LADDER[:len(seen)]],"target descending prefix")
        reached=step["derivative_lower_target_reached"]
        if reached is None:model.need(step["derivative_sign_only_fallback"] is True and all(t["status"]=="NOT_REACHED" for t in trials),"sign fallback")
        else:
            theta=model.fraction_from_rational(reached);model.need(trials[-1]["status"]=="REACHED" and theta==seen[-1],"verified theta")
        verify_route_proof(step["derivative_route_proof"],config,"H_U")
        if reached is not None:model.need(trials[-1]["evaluations"]==step["derivative_route_proof"]["evaluation_count"],"reached trial accounting")
        failed_trials=trials if reached is None else trials[:-1]
        derivative_total+=sum(t["evaluations"] for t in failed_trials)+step["derivative_route_proof"]["evaluation_count"]
        model.need(step["F_r"]==model.interval_negate(step["H_u"]),"step endpoint reversal")
        dlo,dhi=model.interval_fractions(step["F_r"],"step Fr");model.need(dhi<0 and not(dlo<=0<=dhi),"step negative derivative")
        if reached is not None:model.need(dhi<=-model.fraction_from_rational(reached),"theta achieved")
        mp=step["F_midpoint_record"];check_point(mp,mid)
        model.need(mp["normalized_F"]==mp["route_proof"]["normalized_enclosure"],"midpoint enclosure")
        qlo,qhi=model.interval_divide_negative_denominator(mp["normalized_F"],step["F_r"])
        model.need(step["negative_denominator_rule"]=={"reciprocal_endpoint_rule":"[1/F_r_hi,1/F_r_lo]","midpoint_only":False},"negative denominator endpoint rule")
        qiv=model.outward_dyadic(qlo,qhi);niv=model.outward_dyadic(mid-qhi,mid-qlo)
        model.need(step["quotient"]==qiv and step["newton_image"]==niv,"negative denominator quotient")
        nlo,nhi=model.interval_fractions(niv,"Newton image");contained=left<nlo<=nhi<right
        model.need(step["strict_self_containment"] is contained,"containment predicate")
        model.need(step["containment_margins"]=={"left":model.rational_json(nlo-left),"right":model.rational_json(right-nhi)},"exact margins")
        strict=mp["sign"] in ("POSITIVE","NEGATIVE")
        model.need(step["strict_sign_certified"] is strict and step["sign_required_for_continuation"] is (not contained),"containment-first flags")
        if contained:
            model.need(i==len(steps)-1 and step["F_stop_reason"]=="NEWTON_CONTAINMENT","terminal containment");break
        model.need(strict and step["F_stop_reason"]=="STRICT_SIGN","sign required to continue")
        model.need(signed_index<len(points) and points[signed_index]==mp,"ordered signed midpoint")
        signed_index+=1
        if mp["sign"]=="POSITIVE":left=mid
        else:right=mid
    model.need(steps[-1]["strict_self_containment"] is True and signed_index==len(points),"complete J path")
    rlo,rhi=model.interval_fractions(j["r_interval"],"J final");model.need((rlo,rhi)==(left,right),"J final bracket")
    acct=j["evaluation_accounting"]
    model.need(acct["derivative_counted_in_outer_budget"] is False and acct["outer_budget_counts_only"]=="f_point_outer_evaluations","evaluation attribution")
    model.need(acct["f_point_outer_evaluations"]==1+len(steps)<=config["budgets"]["J_START"]["max_evaluations"],"F outer count")
    model.need(acct["derivative_evaluations"]==derivative_total,"derivative count")


def _poly_clean(p: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    return {m: c for m, c in p.items() if c}


def _poly_add(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    out = dict(a)
    for monomial, coeff in b.items():
        out[monomial] = out.get(monomial, 0) + coeff
    return _poly_clean(out)


def _poly_scale(a: dict[tuple[int, int, int], int], k: int) -> dict[tuple[int, int, int], int]:
    return _poly_clean({m: k*c for m, c in a.items()})


def _poly_sub(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    return _poly_add(a, _poly_scale(b, -1))


def _poly_mul(a: dict[tuple[int, int, int], int],
              b: dict[tuple[int, int, int], int]) -> dict[tuple[int, int, int], int]:
    out: dict[tuple[int, int, int], int] = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            monomial = tuple(x+y for x, y in zip(ma, mb))
            out[monomial] = out.get(monomial, 0) + ca*cb
    return _poly_clean(out)


def _poly_pow(a: dict[tuple[int, int, int], int], n: int) -> dict[tuple[int, int, int], int]:
    out = {(0, 0, 0): 1}
    for _ in range(n):
        out = _poly_mul(out, a)
    return out


def _poly_substitute_q(a: dict[tuple[int, int, int], int], value: int) -> dict[tuple[int, int, int], int]:
    out: dict[tuple[int, int, int], int] = {}
    for (et, eq, ed), coeff in a.items():
        monomial = (et, 0, ed)
        out[monomial] = out.get(monomial, 0) + coeff*(value**eq)
    return _poly_clean(out)


def _poly_q_coefficient(a: dict[tuple[int, int, int], int], degree: int) -> dict[tuple[int, int, int], int]:
    return _poly_clean({(et, 0, ed): coeff
                        for (et, eq, ed), coeff in a.items() if eq == degree})


def _verify_domain_algebra_exact() -> dict[str, bool]:
    one = {(0, 0, 0): 1}
    T = {(1, 0, 0): 1}
    Q = {(0, 1, 0): 1}
    D = {(0, 0, 1): 1}
    one_minus_T = _poly_sub(one, T)
    c2 = _poly_scale(_poly_mul(_poly_mul(T, one_minus_T), Q), 4)
    A = _poly_add(one, _poly_mul(_poly_mul(D, one_minus_T), Q))
    J = _poly_add(one, _poly_mul(_poly_mul(D, _poly_sub(one, _poly_scale(T, 2))), Q))
    N = _poly_add(_poly_mul(D, c2), _poly_scale(T, 4))
    K = _poly_add(
        _poly_mul(_poly_mul(D, c2), _poly_sub(one, _poly_scale(T, 2))),
        _poly_mul(_poly_scale(T, 2), _poly_sub(_poly_scale(one, 2), _poly_scale(T, 2))),
    )
    W = _poly_sub(_poly_add(one, D), _poly_mul(D, c2))
    R = {
        (2, 2, 2): 4, (1, 2, 2): -4, (1, 1, 1): -4,
        (0, 1, 2): 1, (0, 1, 1): 1, (0, 0, 1): 1, (0, 0, 0): 1,
    }
    two_TD_minus_D_minus_1 = _poly_sub(
        _poly_sub(_poly_mul(_poly_scale(T, 2), D), D), one)
    checks = {
        'N_EQ_4T_A': not _poly_sub(N, _poly_scale(_poly_mul(T, A), 4)),
        'K_EQ_4T1MT_J': not _poly_sub(K, _poly_scale(_poly_mul(_poly_mul(T, one_minus_T), J), 4)),
        'W_EQ_1_PLUS_D_1MC2': not _poly_sub(W, _poly_add(one, _poly_mul(D, _poly_sub(one, c2)))),
        'C2_BOUND_IDENTITY': not _poly_sub(
            _poly_sub(one, _poly_scale(_poly_mul(T, one_minus_T), 4)),
            _poly_pow(_poly_sub(_poly_scale(T, 2), one), 2)),
        'X_RANGE_FACTOR': not _poly_sub(
            _poly_sub(_poly_mul(W, A), _poly_mul(_poly_add(one, D), T)),
            _poly_mul(one_minus_T, R)),
        'R_Q0': not _poly_sub(_poly_substitute_q(R, 0), _poly_add(D, one)),
        'R_Q1': not _poly_sub(_poly_substitute_q(R, 1), _poly_pow(two_TD_minus_D_minus_1, 2)),
        'R_Q2_CONCAVITY_COEFF': not _poly_sub(
            _poly_q_coefficient(R, 2),
            _poly_scale(_poly_mul(_poly_mul(T, _poly_sub(T, one)), _poly_pow(D, 2)), 4)),
    }
    model.need(all(checks.values()), 'checker L3 exact domain algebra audit')
    return checks


def _check_l3(r: dict[str, Any], config: dict[str, Any], idx: int,
              s_start: Fraction) -> bool:
    lambda_start = model.LAMBDA_PLUS + s_start
    model.need(r["record_type"] == "L3_MONOTONICITY" and r["node"] == "L3",
               "L3 record identity")
    model.need(r["candidate_index"] == idx, "L3 candidate index")
    model.need(r["route_id"] == model.L3_BPRIME_ROUTE_ID
               and r["policy_id"] == model.L3_BPRIME_POLICY_ID, "L3 route/policy")
    model.need(r["identity_lemma_id"] == model.L3_BOUNDARY_IDENTITY_ID
               and r["inference_id"] == model.L3_MONOTONICITY_INFERENCE_ID,
               "L3 identity/inference")
    model.need(model.fraction_from_rational(r["lambda_plus"]) == model.LAMBDA_PLUS,
               "L3 lambda_plus")
    model.need(model.fraction_from_rational(r["s_start"]) == s_start
               and model.fraction_from_rational(r["lambda_start"]) == lambda_start,
               "L3 candidate lambda relation")
    sd0, sd1 = model.interval_fractions(r["s_domain"], "L3 s domain")
    model.need((sd0, sd1) == (Fraction(0), s_start), "L3 complete closed s domain")

    dep = r["stage1_dependency"]
    cfgdep = config["stage1_dependency"]
    model.need(dep == {
        "source_head": cfgdep["source_head"],
        "artifact_zip_sha256": cfgdep["artifact_zip_sha256"],
        "descriptor_sha256": cfgdep["config_sha256"],
        "certificate_sha256": cfgdep["certificate_sha256"],
        "manifest_sha256": cfgdep["manifest_sha256"],
        "bprime_source_sha256": config["l3_bprime_route"]["stage1_bprime_member_sha256"],
        "identity_source_sha256": config["l3_bprime_route"]["stage1_verify_change_of_variables_sha256"],
    }, "L3 Stage-1 provenance")
    ep = r["stage1_endpoint_evidence"]
    model.need(ep["evaluation_key"] == "B(206539/100000)", "L3 endpoint key")
    model.need(ep["enclosure"] == config["l3_bprime_route"]["endpoint_evidence"]["enclosure"],
               "L3 endpoint exact evidence")
    _, ehi = model.rational_interval_fractions(ep["enclosure"], "L3 endpoint")
    model.need(ep["strict_upper_lt_zero"] is (ehi < 0) and ehi < 0,
               "L3 endpoint strict negative")

    dp = r["derivative_policy"]
    cfgp = config["l3_bprime_route"]
    model.need(dp == {k: cfgp[k] for k in (
        "python_flint","dps","bands","rel_tol","eval_limit","depth_limit",
        "max_interval_calls","max_subdivision_depth","subdivision_enabled")},
        "L3 derivative policy binding")
    independent_algebra = _verify_domain_algebra_exact()
    audit = r["extended_domain_audit"]
    model.need(audit["audit_id"] == model.L3_BPRIME_DOMAIN_AUDIT_ID
               and audit["status"] == "PASS", "L3 domain audit")
    model.need(audit.get("exact_algebra_checks") in (None, independent_algebra),
               "L3 recorded exact algebra checks")
    ad0, ad1 = model.rational_interval_fractions(audit["lambda_domain"], "L3 audit domain")
    model.need((ad0, ad1) == (model.LAMBDA_PLUS, lambda_start), "L3 audit coverage")
    model.need(audit["lambda_gt_1_exact"] is True
               and audit["A_positive_lemma"] == "A=1+(lambda^2-1)(1-T)q >= 1"
               and audit["W_positive_lemma"] == "W=lambda^2(1-c2)+c2 >= 1"
               and audit["c2_range_lemma"] == "c2=4T(1-T)q in [0,1]"
               and audit["x_range_lemma"] == "W*A-lambda^2*T=(1-T)R; R concave in q; R(0)=D+1; R(1)=(2TD-D-1)^2"
               and audit["angle_data_domain"] == "0<=x<=1; x=1 handled by pinned hypergeometric branch"
               and audit["identity_id"] == model.L3_BOUNDARY_IDENTITY_ID
               and audit["identity_source_sha256"] == model.STAGE1_VERIFY_CHANGE_SHA256
               and audit["no_new_singularity_or_branch_crossing"] is True,
               "L3 domain hypotheses")
    guard = r["inherited_branch_guard_audit"]
    model.need(guard["audit_id"] == model.L3_BPRIME_BRANCH_GUARD_AUDIT_ID
               and guard["status"] == "PASS" and guard["float_call_count"] == 3
               and guard["allowed_functions"] == ["_abs_upper", "_h_data"]
               and guard["proof_decision_use"] is False, "L3 inherited float guards")
    model.need(len(guard["locations"]) == 3
               and all(x["function"] in ("_abs_upper", "_h_data") for x in guard["locations"]),
               "L3 float guard locations")

    pd0, pd1 = model.rational_interval_fractions(r["derivative_proof_domain"], "L3 derivative domain")
    model.need((pd0, pd1) == (model.LAMBDA_PLUS, lambda_start), "L3 derivative full domain")
    leaves = r["derivative_interval_records"]
    model.need(isinstance(leaves, list) and leaves, "L3 derivative leaves")
    intervals: list[tuple[Fraction, Fraction]] = []
    all_negative = True
    enclosures: list[tuple[Fraction, Fraction]] = []
    for i, leaf in enumerate(leaves):
        model.need(leaf["call_index"] == i, "L3 derivative call order")
        lo, hi = model.rational_interval_fractions(leaf["lambda_interval"], "L3 leaf lambda")
        model.need(model.LAMBDA_PLUS <= lo < hi <= lambda_start, "L3 leaf containment")
        intervals.append((lo, hi))
        iv = leaf["Bprime_enclosure"]
        if iv is None:
            model.need(leaf["strict_upper_lt_zero"] is False
                       and leaf["status"] == "UNRESOLVED"
                       and isinstance(leaf["failure_reason"], str), "L3 unresolved leaf")
            all_negative = False
        else:
            blo, bhi = model.interval_fractions(iv, "L3 Bprime leaf")
            strict = bhi < 0
            model.need(leaf["strict_upper_lt_zero"] is strict, "L3 leaf sign predicate")
            model.need(leaf["status"] == ("CERTIFIED" if strict else "UNRESOLVED"),
                       "L3 leaf status")
            model.need((leaf["failure_reason"] is None) is strict, "L3 leaf failure reason")
            all_negative = all_negative and strict
            enclosures.append((blo, bhi))
    intervals.sort()
    model.need(intervals[0][0] == model.LAMBDA_PLUS and intervals[-1][1] == lambda_start,
               "L3 derivative endpoints")
    for i in range(1, len(intervals)):
        model.need(intervals[i-1][1] == intervals[i][0], "L3 derivative exact adjacency")
    model.need(len(leaves) <= cfgp["max_interval_calls"], "L3 derivative call budget")
    if cfgp["subdivision_enabled"] is False:
        model.need(len(leaves) == 1, "L3 whole-interval V1")

    if all_negative:
        expected = model.interval_json(min(x[0] for x in enclosures),
                                       max(x[1] for x in enclosures))
        model.need(r["final_Bprime_enclosure"] == expected, "L3 final Bprime hull")
    else:
        model.need(r["final_Bprime_enclosure"] is None or
                   isinstance(r["final_Bprime_enclosure"], dict), "L3 unresolved final enclosure")
    model.need(r["Bprime_upper_lt_zero"] is all_negative, "L3 final derivative predicate")
    certified = all_negative and ehi < 0
    model.need(r["certified"] is certified, "L3 certified predicate")
    model.need(r["monotonicity_inference_applied"] is certified
               and r["boundary_identity_applied"] is certified, "L3 inference application")
    model.need(r["direct_F_route_used"] is False
               and r["sampled_or_finite_difference_used"] is False
               and r["float_proof_decision_used"] is False, "L3 prohibited proof paths")
    model.need(r["final_claim"] == ("H(0,s)<0 on [0,s_start]" if certified else None),
               "L3 final claim")
    model.need((r["failure_reason"] is None) is certified, "L3 failure state")
    return certified


def _candidate(block: list[dict[str, Any]], summary: dict[str, Any],
               config: dict[str, Any]) -> bool:
    idx = summary["candidate_index"]
    s_start = (model.fraction_from_rational(summary["lambda_start"])
               - model.LAMBDA_PLUS)
    u_max = model.fraction_from_dyadic(summary["u_max"])
    l1 = [r for r in block if r.get("node") == "L1"]
    l2 = [r for r in block if r.get("node") == "L2"]
    l3 = [r for r in block if r.get("node") == "L3"]
    for r in l1+l2:
        model.need(r["candidate_index"] == idx, "candidate index")
        _check_tile(r, config, r["node"])
    model.need(len(l3) == 1, "single L3 monotonicity record")
    ok3 = _check_l3(l3[0], config, idx, s_start)
    _cover([_rect_from_l1(r) for r in l1],
           (Fraction(0), u_max, -model.S_NEG, s_start), "L1")
    _cover1(l2, -model.S_NEG, s_start, "L2")
    ok1 = all(r["certified"] for r in l1)
    ok2 = all(r["certified"] for r in l2)
    js = [r for r in block if r.get("record_type") == "J_START"]
    if js:
        model.need(len(js) == 1, "single J_START")
        _check_j(js[0], u_max, model.LAMBDA_PLUS+s_start, config)
    accepted = ok1 and ok2 and ok3 and len(js) == 1
    model.need(summary["candidate_accepted"] is accepted,
               "candidate accepted")
    return accepted


def verify_records(records: list[dict[str, Any]], config: dict[str, Any],
                   config_hash: str) -> dict[str, Any]:
    model.validate_config(config)
    model.need(isinstance(records, list) and len(records) >= 2, "records")
    prev = model.chain_genesis(config_hash)
    for r in records:
        model.need(r.get("previous_record_sha256") == prev,
                   "chain predecessor")
        model.need(r.get("record_sha256") == model.record_hash(r),
                   "record hash")
        prev = r["record_sha256"]

    h, f = records[0], records[-1]
    model.need(h["record_type"] == "RUN_HEADER"
               and h["chain_genesis"] == model.chain_genesis(config_hash),
               "header")
    model.need(f["record_type"] == "RUN_SUMMARY", "summary")

    accepted: list[int] = []
    block: list[dict[str, Any]] = []
    expected = 0
    for r in records[1:-1]:
        if r.get("record_type") == "CANDIDATE_SUMMARY":
            model.need(r["candidate_index"] == expected, "candidate order")
            if _candidate(block, r, config):
                accepted.append(expected)
            expected += 1
            block = []
        else:
            block.append(r)

    model.need(not block and len(accepted) <= 1, "candidate blocks")
    if accepted:
        model.need(accepted[0] == expected-1
                   and f["selected_candidate_index"] == accepted[0]
                   and f["terminal_state"] == model.COMPLETE,
                   "first passing")
    else:
        model.need(f["selected_candidate_index"] is None
                   and f["terminal_state"] == model.INCOMPLETE,
                   "incomplete")

    return {
        "checker_id": CHECKER_ID,
        "valid": True,
        "candidate_summaries": expected,
        "accepted_candidate_index": accepted[0] if accepted else None,
        "all_F_Fr_consumers_finite_routes": True,
        "l3_boundary_monotonicity_checked": True,
        "all_required_consumers_authorized_routes": True,
        "closed_coverage_checked": True,
        "route_trees_checked": True,
        "R1_R4_runtime_repairs_bound": True,
        "J_START_reconstructed": True,
    }
