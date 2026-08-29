#!/usr/bin/env python3
"""Native B-LOCAL v2.3 F_lambda route glue.

DESIGN_DRAFT_ONLY / NOT_BINDING / NOT_PROMOTED.
The shared derivative mathematics is in blocal_v23_flambda_kernel.py.
"""
from __future__ import annotations
import heapq
from fractions import Fraction
from typing import Any, Callable
import blocal_v22_boundary as base
import blocal_v22_model as model
import blocal_v22_policy as policy
import blocal_v23_flambda_kernel as fk

FLAMBDA_ROUTE_ID="BLOCAL_FLAMBDA_ROUTE_V1"
TRANSPORT_LEMMA_ID="F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1"


def _taylor_cell(kernel,adapter,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps,max_gamma_depth):
    base._reset_gamma_trace(); rb=base._r_ball(arb_type,fmpq_type,u0,u1); lb=base._lambda_ball(arb_type,fmpq_type,s0,s1); z=arb_type(0)
    rj=base.J2(rb,z,z,z,z,z); lj=base.J2(lb,z,z,z,z,z); am=(cell.a0+cell.a1)/2; bm=(cell.b0+cell.b1)/2
    fc,detail=fk.geometry_jet_flambda("F_lambda",kernel,adapter,acb_type,arb_type,fmpq_type,cell.region,
        base._jvar(base._arb_exact(arb_type,fmpq_type,am),0),base._jvar(base._arb_exact(arb_type,fmpq_type,bm),1),rj,lj,cell,u0,s0,eps,"center",max_gamma_depth)
    fb,_=fk.geometry_jet_flambda("F_lambda",kernel,adapter,acb_type,arb_type,fmpq_type,cell.region,
        base._jvar(base._arb_interval(arb_type,fmpq_type,cell.a0,cell.a1),0),base._jvar(base._arb_interval(arb_type,fmpq_type,cell.b0,cell.b1),1),rj,lj,cell,u0,s0,eps,"box",max_gamma_depth)
    da=cell.a1-cell.a0; db=cell.b1-cell.b0; area=da*db; caa=area*da*da/Fraction(24); cbb=area*db*db/Fraction(24); cab=area*da*db/Fraction(16)
    hlo,hhi=base._jet_fracs(adapter,fb.hab,"F_lambda Taylor Hab"); cross=max(abs(hlo),abs(hhi))*cab
    src=fc.v*base._arb_exact(arb_type,fmpq_type,area)+fb.haa*base._arb_exact(arb_type,fmpq_type,caa)+fb.hbb*base._arb_exact(arb_type,fmpq_type,cbb)+base._arb_interval(arb_type,fmpq_type,-cross,cross)
    factor=(base._arb_exact(arb_type,fmpq_type,base.HALF-eps)*arb_type.pi() if cell.region=="C1" else
            (arb_type.pi()/3)*arb_type.pi() if cell.region=="TH" else
            base._arb_exact(arb_type,fmpq_type,eps)*(arb_type.pi()-base._arb_exact(arb_type,fmpq_type,eps)))
    out=src*factor; base._canonical(adapter,out,"F_lambda Taylor contribution")
    aa0,aa1=base._jet_fracs(adapter,fb.haa,"F_lambda Taylor Haa"); bb0,bb1=base._jet_fracs(adapter,fb.hbb,"F_lambda Taylor Hbb")
    detail.update({"_score_a":max(abs(aa0),abs(aa1))*caa+cross/2,"_score_b":max(abs(bb0),abs(bb1))*cbb+cross/2,
                   "remainder_rule":"diag area*w^2/24 + cross supabs*area*wa*wb/16",
                   "gamma_subdivisions":[base._GAMMA_TRACE[k] for k in sorted(base._GAMMA_TRACE)],
                   "gamma_fallback_used":any(x["bin_count"]>1 for x in base._GAMMA_TRACE.values())})
    return out,detail


def _cell_eval(kernel,adapter,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps,max_gamma_depth):
    if cell.region in ("T1","T2"):
        return fk.duffy_eval_flambda(kernel,adapter,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps)
    return _taylor_cell(kernel,adapter,acb_type,arb_type,fmpq_type,cell,u0,u1,s0,s1,eps,max_gamma_depth)


def _policy(config):
    pcfg=config.get("route_policies",{}).get("F_LAMBDA_ROUTE")
    model.need(pcfg is not None,"missing native F_LAMBDA_ROUTE policy")
    policy.validate_route_policy(pcfg,"F_LAMBDA_ROUTE policy")
    return pcfg


def enclose_flambda(kernel:Any,adapter:Any,acb_type:Any,arb_type:Any,fmpq_type:Any,
                    config:dict[str,Any],u0:Fraction,u1:Fraction,s0:Fraction,s1:Fraction,
                    required_sign:str="NEG",evaluation_cap:int|None=None):
    model.need(required_sign=="NEG","F_lambda required_sign must be NEG")
    model.need(Fraction(0)<=u0<=u1<=Fraction(1,4),"route u"); model.need(-model.S_NEG<=s0<=s1,"route s")
    pcfg=_policy(config); cap=pcfg["max_evaluations"] if evaluation_cap is None else evaluation_cap
    model.need(isinstance(cap,int) and 0<cap<=pcfg["max_evaluations"],"route evaluation cap")
    eps=model.fraction_from_dyadic(config["geometry"]["eps"]); base._reset_floor_trace(); evaluations=0
    leaves={}; canonical={}; meta={}; split_reasons={}; unevaluated=[]; shallow=[]; widths=[]; sum_lo=sum_hi=Fraction(0)
    def add_leaf(c):
        leaves[c.path]=c; key=(policy.REGION_ORDER[c.region],c.path); heapq.heappush(unevaluated,key)
        if c.depth<pcfg["min_depth"]: heapq.heappush(shallow,key)
    def remove_leaf(c):
        nonlocal sum_lo,sum_hi
        leaves.pop(c.path); detail=meta.pop(c.path,None); iv=canonical.pop(c.path,None)
        if iv is not None:
            lo,hi=model.interval_fractions(iv,"remove cached child"); sum_lo-=lo; sum_hi-=hi
        return detail
    def split_leaf(c,reason):
        model.need(c.depth<pcfg["max_depth"],f"angular depth: {reason}"); model.need(len(leaves)+1<=pcfg["max_children"],"angular child budget")
        detail=remove_leaf(c)
        for child in base._split(c,detail): add_leaf(child)
        split_reasons[c.path]=reason
    def eval_one(c):
        nonlocal evaluations,sum_lo,sum_hi
        if evaluations>=cap: raise base.EnclosureFailure("ANGULAR_EVALUATION_BUDGET",evaluations)
        value,detail=_cell_eval(kernel,adapter,acb_type,arb_type,fmpq_type,c,u0,u1,s0,s1,eps,pcfg["max_depth"])
        iv=base._canonical(adapter,value,"accepted F_lambda child"); lo,hi=model.interval_fractions(iv,"cached child")
        evaluations+=1; canonical[c.path]=iv; meta[c.path]=detail; sum_lo+=lo; sum_hi+=hi
        if c.depth<pcfg["max_depth"]: heapq.heappush(widths,base._WidthEntry(hi-lo,-policy.REGION_ORDER[c.region],c.path))
    for root in base._root_initial(): add_leaf(root)
    while True:
        forced=None
        while unevaluated:
            _,path=heapq.heappop(unevaluated); c=leaves.get(path)
            if c is None or path in canonical: continue
            try: eval_one(c)
            except base.SplitRequired as exc: forced=(c,exc.reason); break
        if forced is not None: split_leaf(*forced); continue
        shallow_cell=None
        while shallow:
            _,path=heapq.heappop(shallow); c=leaves.get(path)
            if c is not None and c.depth<pcfg["min_depth"]: shallow_cell=c; break
        if shallow_cell is not None: split_leaf(shallow_cell,"MIN_DEPTH"); continue
        normalized=model.normalize_interval(model.outward_dyadic(sum_lo,sum_hi)); _,hi=model.interval_fractions(normalized,"F_lambda root normalized")
        if hi<0: break
        model.need(len(leaves)+1<=pcfg["max_children"],"angular sign child budget"); chosen=None
        while widths:
            e=heapq.heappop(widths); c=leaves.get(e.path)
            if c is not None and c.depth<pcfg["max_depth"] and e.path in canonical: chosen=c; break
        model.need(chosen is not None,"angular sign unresolved at depth limit"); split_leaf(chosen,"ROOT_NEG_PREDICATE_UNRESOLVED")
    leaf_list=list(leaves.values()); model.need(all(base._cover_ok(leaf_list,r) for r in policy.REGION_ORDER),"exact angular cover")
    ordered=sorted(leaf_list,key=lambda c:(policy.REGION_ORDER[c.region],c.path)); children=[]
    for c in ordered:
        children.append({"child_id":c.path,"parent_id":c.path[:-1] if len(c.path)>2 else None,"region":c.region,"depth":c.depth,
                         "box":{"a":model.interval_json(c.a0,c.a1),"b":model.interval_json(c.b0,c.b1)},
                         "source_coordinates":"(x,y_D)" if c.region in ("T1","T2") else "NORMALIZED_SOURCE_BOX",
                         "detail":{k:v for k,v in meta[c.path].items() if not k.startswith("_score_")},
                         "contribution_enclosure":canonical[c.path],"status":"ACCEPTED"})
    ulo,uhi=model.interval_add_exact([x["contribution_enclosure"] for x in children]); model.need((ulo,uhi)==(sum_lo,sum_hi),"incremental sum reconstruction")
    unnormalized=model.outward_dyadic(ulo,uhi); normalized=model.normalize_interval(unnormalized); _,final_hi=model.interval_fractions(normalized,"F_lambda final normalized")
    model.need(final_hi<0,"F_lambda final sign must be NEG")
    body={"route_id":FLAMBDA_ROUTE_ID,"quantity":"F_lambda","required_sign":"NEG","native_quantity":True,"monkeypatch_used":False,
          "ordinary_formula_id":fk.ORDINARY_FORMULA_ID,"duffy_formula_id":fk.DUFFY_FORMULA_ID,"transport_lemma_id":TRANSPORT_LEMMA_ID,
          "angular_policy_id":policy.ANGULAR_POLICY_ID,"policy":pcfg,"denominator_policy_id":policy.DENOMINATOR_POLICY_ID,
          "effective_evaluation_cap":cap,"sqrt_policy_id":policy.SQRT_POLICY_ID,"gamma_policy_id":policy.GAMMA_POLICY_ID,
          "q_lo_policy_id":policy.Q_LO_POLICY_ID,"normalization_policy_id":policy.NORMALIZATION_POLICY_ID,
          "one_over_pi_enclosure":{"lo":model.rational_json(model.ONE_OVER_PI_LO),"hi":model.rational_json(model.ONE_OVER_PI_HI)},
          "normalization_bits":model.NORMALIZATION_BITS,"u_interval":model.interval_json(u0,u1),"s_interval":model.interval_json(s0,s1),
          "eps":config["geometry"]["eps"],"patch_type":model.PATCH_TYPE,"ordered_children":children,"split_reasons":split_reasons,
          "evaluation_count":evaluations,"unnormalized_sum":unnormalized,"normalized_enclosure":normalized,"complete_closed_cover":True,
          "direct_pinned_integrator_called":False,"effective_floor_registry":base._floor_summary(),
          "method_selection_addendum_sha256":base.METHOD_SELECTION_ADDENDUM_SHA256,"c1_floor_spec_sha256":base.C1_FLOOR_SPEC_SHA256}
    body["proof_id"]=base._proof_id(body); return normalized,body


def enclose_route(quantity:str,kernel:Any,adapter:Any,acb_type:Any,arb_type:Any,fmpq_type:Any,config:dict[str,Any],
                  u0:Fraction,u1:Fraction,s0:Fraction,s1:Fraction,required_sign:str|None=None,
                  accept:Callable[[dict[str,Any]],bool]|None=None,evaluation_cap:int|None=None):
    if quantity=="F_lambda":
        model.need(accept is None,"binding F_lambda custom accept forbidden")
        return enclose_flambda(kernel,adapter,acb_type,arb_type,fmpq_type,config,u0,u1,s0,s1,"NEG" if required_sign is None else required_sign,evaluation_cap)
    return base.enclose_route(quantity,kernel,adapter,acb_type,arb_type,fmpq_type,config,u0,u1,s0,s1,required_sign,accept,evaluation_cap)

__all__=["FLAMBDA_ROUTE_ID","TRANSPORT_LEMMA_ID","enclose_flambda","enclose_route"]
