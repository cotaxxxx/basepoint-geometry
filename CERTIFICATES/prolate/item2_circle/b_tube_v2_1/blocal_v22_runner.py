#!/usr/bin/env python3
"""B-LOCAL v2.2 runner: finite F/K routes for L1/L2/L3/J_START."""
from __future__ import annotations
import argparse, os, subprocess, time
from collections import deque
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import blocal_phase4_engine as v21_engine
import blocal_phase4_provenance as provenance
import blocal_v22_model as model
import blocal_v22_policy as policy

DESIGN_COMMITS=[
    "9b62f3453e4878dae262c69f545f0ea8bac93d5f",
    "d608794d140426e49cafbe4279f48fb00fd1077a",
    "f21704b2cbd2954acb492ec2a58dbb0765773f1f",
    "4752e7114d2c6b65fa7be749aad8561ab37791fc",
]
CERTIFICATE_SCHEMA="blocal-certificate-v2-finite-routes"
SUMMARY_SCHEMA="blocal-run-summary-v2-finite-routes"
MACHINE_SCHEMA="btube-blocal-machine-conclusion-v2-finite-routes"
PROGRESS_SCHEMA="blocal-progress-v1-diagnostic-only"
PROGRESS_FILE="progress.blocal.jsonl"


def _utc_now()->str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00","Z")


class _ProgressJournal:
    """Durable diagnostic progress; never part of the certificate record chain."""
    def __init__(self,path:Path)->None:
        model.need(not path.exists(),"fresh progress journal")
        self.path=path;self.sequence=0

    def append(self,event_type:str,**fields:Any)->None:
        record={"schema":PROGRESS_SCHEMA,"evidence_role":"DIAGNOSTIC_PROGRESS_ONLY",
                "certificate_evidence":False,"sequence":self.sequence,
                "event_type":event_type,"timestamp_utc":_utc_now(),**fields}
        raw=model.canonical_json_bytes(record)+b"\n"
        fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
        try:
            written=os.write(fd,raw);model.need(written==len(raw),"progress append")
            os.fsync(fd)
        finally:os.close(fd)
        self.sequence+=1


def repository_root()->Path:return Path(__file__).resolve(strict=True).parents[4]
def git_head(root:Path)->str:
    h=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
    model.need(len(h)==40 and all(c in "0123456789abcdef" for c in h),"source head");return h

def _schedule(config:dict[str,Any])->list[tuple[Fraction,Fraction]]:
    ds=[model.fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    us=[model.fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    return [(d,u) for d in ds for u in us]

def _load_adapter(root:Path,config:dict[str,Any])->Any:
    return provenance.load_pinned_module(root,{"path":config["adapter"]["path"],"sha256":config["adapter"]["source_sha256"]},
        "blocal_v22_pinned_adapter",("arb_ball_to_canonical_dyadic_interval","AdapterError"),{"ADAPTER_ID":model.ADAPTER_ID})

def _load_aux(root:Path,config:dict[str,Any])->tuple[Any,Any,Any,Any]:
    pins=config["implementation"]["sources_sha256"]
    route_path="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"
    route=provenance.load_pinned_module(root,{"path":route_path,"sha256":pins[route_path]},"blocal_v22_pinned_finite_route",
        ("enclose_hu","enclose_f","validate_helper_lemmas","EnclosureFailure"),{"F_ROUTE_ID":policy.F_ROUTE_ID,"K_ROUTE_ID":policy.K_ROUTE_ID})
    audit=provenance.load_pinned_module(root,{"path":config["symbolic_audit"]["path"],"sha256":config["symbolic_audit"]["source_sha256"]},
        "blocal_v22_pinned_symbolic_audit",("run_audit",),{"AUDIT_ID":model.SYMBOLIC_AUDIT_ID})
    checker=provenance.load_pinned_module(root,{"path":config["checker"]["path"],"sha256":config["checker"]["source_sha256"]},
        "blocal_v22_pinned_checker",("verify_records",),{"CHECKER_ID":model.CHECKER_ID})
    lp=config["l3_bprime_route"]
    l3=provenance.load_pinned_module(root,{"path":lp["path"],"sha256":lp["source_sha256"]},
        "blocal_v22_pinned_l3_bprime",("prepare","certify_l3"),
        {"ROUTE_ID":model.L3_BPRIME_ROUTE_ID,"POLICY_ID":model.L3_BPRIME_POLICY_ID,
         "DOMAIN_AUDIT_ID":model.L3_BPRIME_DOMAIN_AUDIT_ID,
         "BRANCH_GUARD_AUDIT_ID":model.L3_BPRIME_BRANCH_GUARD_AUDIT_ID,
         "IDENTITY_ID":model.L3_BOUNDARY_IDENTITY_ID,"INFERENCE_ID":model.L3_MONOTONICITY_INFERENCE_ID})
    a=audit.run_audit();model.need(a.get("exact_algebra") is True and a.get("F_route_exact") is True and a.get("J_equals_rho_K") is True,"symbolic audit gate")
    return route,audit,checker,l3

def _strict(iv:dict[str,Any],sign:str)->bool:
    lo,hi=model.interval_fractions(iv,"strict");return lo>0 if sign=="POS" else hi<0

def _outer_split_2d(dom:tuple[Fraction,Fraction,Fraction,Fraction])->list[tuple[Fraction,Fraction,Fraction,Fraction]]:
    return v21_engine.split_l1(*dom)
def _outer_split_1d(dom:tuple[Fraction,Fraction])->list[tuple[Fraction,Fraction]]:
    a,b=dom;m=(a+b)/2;model.need(a<m<b,"1d split");return [(a,m),(m,b)]

def _certify_outer(node:str,candidate_index:int,initial:Any,config:dict[str,Any],
                   evaluate:Callable[...,tuple[dict[str,Any],dict[str,Any]]],sign:str)->tuple[list[dict[str,Any]],bool,str|None,int]:
    budget=config["budgets"][node];pending=deque([(initial,0)]);leaves=[];evaluations=0;failure=None
    while pending:
        dom,depth=pending.popleft();did=evaluations<budget["max_evaluations"]
        proof=None
        if did:
            try:
                enclosure,proof=evaluate(*dom);evaluations+=1;cert=_strict(enclosure,sign)
            except Exception as exc:
                # Fail closed; outer subdivision is allowed but no alternate formula is selected.
                enclosure=model.interval_json(Fraction(-1),Fraction(1));cert=False
                local_reason=f"{node}_ROUTE_{type(exc).__name__}"
        else:
            enclosure=model.interval_json(Fraction(-1),Fraction(1));cert=False;local_reason=f"{node}_EVALUATION_BUDGET"
        can=(not cert and depth<budget["max_depth"] and len(leaves)+len(pending)+2<=budget["max_tiles"]
             and evaluations<budget["max_evaluations"])
        if can:
            children=_outer_split_2d(dom) if node=="L1" else _outer_split_1d(dom)
            pending.extend((x,depth+1) for x in children);continue
        if not cert:
            failure=failure or locals().get("local_reason") or (f"{node}_DEPTH" if depth>=budget["max_depth"] else f"{node}_STRICT_SIGN_UNRESOLVED")
        rec={"record_type":f"{node}_TILE","node":node,"candidate_index":candidate_index,
             "depth":depth,"enclosure":enclosure,"certified":cert,"strict_predicate":"LOWER_GT_ZERO" if sign=="POS" else "UPPER_LT_ZERO",
             "route_proof":proof,"failure_reason":None if cert else failure}
        if node=="L1":rec["u_interval"]=model.interval_json(dom[0],dom[1]);rec["s_interval"]=model.interval_json(dom[2],dom[3]);rec["quantity"]="H_u=-F_r"
        else:rec["s_interval"]=model.interval_json(dom[0],dom[1]);rec["quantity"]="F"
        leaves.append(rec)
    return leaves,all(r["certified"] for r in leaves),failure,evaluations

def _newton_image(mid:Fraction,Fm:dict[str,Any],D:dict[str,Any])->tuple[dict[str,Any],dict[str,Any]]:
    qlo,qhi=model.interval_divide_negative_denominator(Fm,D)
    qiv=model.outward_dyadic(qlo,qhi);nlo,nhi=mid-qhi,mid-qlo
    niv=model.outward_dyadic(nlo,nhi)
    return qiv,niv

def _build_j_start(candidate_index:int,lambda_start:Fraction,u_max:Fraction,config:dict[str,Any],
                   route:Any,kernel:Any,adapter:Any,acb:Any,arb:Any,fmpq:Any)->tuple[dict[str,Any]|None,str|None,int]:
    budget=config["budgets"]["J_START"];f_count=0;derivative_count=0;ordered=[];steps=[]
    s=lambda_start-model.LAMBDA_PLUS
    def sign(iv:dict[str,Any])->str:
        lo,hi=model.interval_fractions(iv,"J F")
        return "POSITIVE" if lo>0 else "NEGATIVE" if hi<0 else "UNRESOLVED"
    def f_at(r:Fraction,role:str,required_sign:str|None=None,
             accept:Callable[[dict[str,Any]],bool]|None=None)->tuple[dict[str,Any],dict[str,Any]]:
        nonlocal f_count
        model.need(f_count<budget["max_evaluations"],"J_START outer evaluation budget")
        iv,proof=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,r,r,lambda_start,lambda_start,required_sign,accept)
        f_count+=1;sgn=sign(iv)
        rec={"evaluation_id":f"J-F-{f_count:03d}","r":model.rational_json(r),"lambda_start":model.rational_json(lambda_start),
             "route_id":policy.F_ROUTE_ID,"route_proof":proof,"normalized_F":iv,"sign":sgn,"role":role}
        return iv,rec
    full_hu,full_proof=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,Fraction(0),u_max,s,s,"POS")
    derivative_count+=full_proof["evaluation_count"]
    full_fr=model.interval_negate(full_hu);_,full_hi=model.interval_fractions(full_fr,"full derivative")
    if full_hi>=0:return None,"J_START_FULL_DERIVATIVE_NEGATIVITY_UNRESOLVED",f_count
    full_cond5={"record_id":"J-DERIVATIVE-FULL","r_interval":model.interval_json(1-u_max,Fraction(1)),
        "u_interval":model.interval_json(Fraction(0),u_max),"H_u":full_hu,"F_r":full_fr,"route_proof":full_proof,
        "endpoint_transform":{"rule":"[H_lo,H_hi] -> [-H_hi,-H_lo]","label_only":False},
        "sup_F_r_lt_zero":True,"zero_not_in_F_r":True}
    left,right=1-u_max,Fraction(1);fleft,leftrec=f_at(left,"INITIAL_LEFT","POS")
    if sign(fleft)!="POSITIVE":return None,"J_START_LEFT_SIGN_UNRESOLVED",f_count
    ordered.append(leftrec)
    target_cap=min(config["route_policies"]["K_ROUTE"]["max_evaluations"],
                   max(4,config["budgets"]["L1"]["max_evaluations"]//4))
    for step_index in range(budget["max_bisections"]):
        u0,u1=1-right,1-left;trials=[];chosen=None
        for theta_text in policy.DERIVATIVE_TARGET_LADDER:
            theta=Fraction(theta_text);before=derivative_count
            def derivative_accept(iv:dict[str,Any],theta:Fraction=theta)->bool:
                lo,_=model.interval_fractions(iv,"H_u target");return lo>=theta
            try:
                hu,hproof=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s,s,None,derivative_accept,target_cap)
                derivative_count+=hproof["evaluation_count"]
                hlo,_=model.interval_fractions(hu,"H_u reached")
                reached=hlo>=theta
                trials.append({"target":model.rational_json(theta),"status":"REACHED" if reached else "NOT_REACHED",
                    "evaluations":hproof["evaluation_count"],"failure_reason":None if reached else "TARGET_NOT_REACHED"})
                if reached:chosen=(theta,hu,hproof);break
            except route.EnclosureFailure as exc:
                derivative_count+=exc.evaluations
                trials.append({"target":model.rational_json(theta),"status":"NOT_REACHED","evaluations":exc.evaluations,"failure_reason":exc.reason})
            model.need(derivative_count>=before,"derivative accounting")
        if chosen is None:
            hu,hproof=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s,s,"POS")
            derivative_count+=hproof["evaluation_count"];theta=None
        else:theta,hu,hproof=chosen
        D=model.interval_negate(hu);dlo,dhi=model.interval_fractions(D,"step derivative")
        if not(dhi<0 and not(dlo<=0<=dhi)):return None,"J_START_DERIVATIVE_NEGATIVITY_UNRESOLVED",f_count
        midpoint=(left+right)/2;captured={}
        def f_accept(iv:dict[str,Any])->bool:
            if sign(iv)!="UNRESOLVED":
                return True
            try:
                q,n=_newton_image(midpoint,iv,D);nlo,nhi=model.interval_fractions(n,"Newton trial")
                captured.update({"quotient":q,"newton_image":n,"contained":left<nlo<=nhi<right})
                return captured["contained"]
            except Exception:
                return False
        Fm,mrec=f_at(midpoint,"BISECTION_MIDPOINT",None,f_accept);sgn=sign(Fm)
        quotient,newton=_newton_image(midpoint,Fm,D);nlo,nhi=model.interval_fractions(newton,"Newton")
        contained=left<nlo<=nhi<right
        qlo,qhi=model.interval_fractions(quotient,"quotient")
        step={"step_index":step_index,"bracket":model.interval_json(left,right),"midpoint":model.rational_json(midpoint),
            "coordinate_map":{"u_interval":model.interval_json(u0,u1),"u_lo_equals":"1-r_right","u_hi_equals":"1-r_left","exact_rational":True},
            "derivative_lower_target_reached":model.rational_json(theta) if theta is not None else None,
            "derivative_target_trials":trials,"derivative_sign_only_fallback":theta is None,"H_u":hu,"F_r":D,"derivative_route_proof":hproof,
            "endpoint_transform":{"rule":"[H_lo,H_hi] -> [-H_hi,-H_lo]","label_only":False},
            "F_midpoint_record":mrec,"strict_sign_certified":sgn!="UNRESOLVED","sign_required_for_continuation":not contained,
            "F_stop_reason":"NEWTON_CONTAINMENT" if contained else "STRICT_SIGN" if sgn!="UNRESOLVED" else "UNRESOLVED",
            "quotient":quotient,"quotient_width":model.rational_json(qhi-qlo),
            "negative_denominator_rule":{"reciprocal_endpoint_rule":"[1/F_r_hi,1/F_r_lo]","midpoint_only":False},
            "newton_image":newton,"containment_margins":{"left":model.rational_json(nlo-left),"right":model.rational_json(right-nhi)},
            "strict_self_containment":contained}
        steps.append(step)
        if contained:
            return {"record_type":"J_START","node":"J_START","candidate_index":candidate_index,"lambda_start":model.rational_json(lambda_start),
                "initial_bracket":model.interval_json(1-u_max,Fraction(1)),"r_interval":model.interval_json(left,right),
                "ordered_bisection_records":ordered,"condition5_derivative_record":full_cond5,"newton_steps":steps,"newton_record":step,
                "evaluation_accounting":{"f_point_outer_evaluations":f_count,"derivative_evaluations":derivative_count,
                    "outer_budget_counts_only":"f_point_outer_evaluations","derivative_counted_in_outer_budget":False},
                "claim":"J_START_UNIQUE_NONDEGENERATE_ROOT","certified":True,
                "direct_pinned_F_arb_called":False,"direct_pinned_dFdr_arb_called":False},None,f_count
        if sgn=="POSITIVE":left=midpoint;ordered.append(mrec);mrec["role"]="RETAINED_LEFT"
        elif sgn=="NEGATIVE":right=midpoint;ordered.append(mrec);mrec["role"]="RETAINED_RIGHT"
        else:return None,"J_START_BISECTION_SIGN_UNRESOLVED",f_count
    return None,"J_START_MAX_BISECTIONS",f_count

def _append_candidate(records:list[dict[str,Any]],previous:str,index:int,s_start:Fraction,u_max:Fraction,config:dict[str,Any],
                      route:Any,l3_route:Any,l3_prepared:Any,kernel:Any,adapter:Any,acb:Any,arb:Any,fmpq:Any,
                      progress:_ProgressJournal)->tuple[str,tuple|None,dict[str,int],int]:
    lam_start=model.LAMBDA_PLUS+s_start
    pair_started=time.monotonic()
    progress.append("PAIR_START",candidate_index=index,lambda_increment=model.dyadic_json(s_start),
                    lambda_start=model.rational_json(lam_start),u_max=model.dyadic_json(u_max))
    node_started=time.monotonic();progress.append("NODE_START",candidate_index=index,node="L1",
        lambda_start=model.rational_json(lam_start),u_max=model.dyadic_json(u_max),evaluation_count=0)
    l1=_certify_outer("L1",index,(Fraction(0),u_max,-model.S_NEG,s_start),config,
        lambda u0,u1,s0,s1:route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s0,s1,"POS"),"POS")
    progress.append("NODE_COMPLETE",candidate_index=index,node="L1",status="CERTIFIED" if l1[1] else "INCOMPLETE",
        evaluation_count=l1[3],evaluation_scope="OUTER_CELLS",leaf_count=len(l1[0]),failure_reason=l1[2],
        elapsed_seconds=f"{time.monotonic()-node_started:.6f}")
    node_started=time.monotonic();progress.append("NODE_START",candidate_index=index,node="L2",
        lambda_start=model.rational_json(lam_start),u_max=model.dyadic_json(u_max),evaluation_count=0)
    l2=_certify_outer("L2",index,(-model.S_NEG,s_start),config,
        lambda s0,s1:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-u_max,1-u_max,model.LAMBDA_PLUS+s0,model.LAMBDA_PLUS+s1,"POS"),"POS")
    progress.append("NODE_COMPLETE",candidate_index=index,node="L2",status="CERTIFIED" if l2[1] else "INCOMPLETE",
        evaluation_count=l2[3],evaluation_scope="OUTER_CELLS",leaf_count=len(l2[0]),failure_reason=l2[2],
        elapsed_seconds=f"{time.monotonic()-node_started:.6f}")
    node_started=time.monotonic();progress.append("NODE_START",candidate_index=index,node="L3",
        lambda_start=model.rational_json(lam_start),u_max=model.dyadic_json(u_max),evaluation_count=0)
    l3rec,l3ok,l3why,l3n=l3_route.certify_l3(l3_prepared,adapter,index,lam_start,s_start,config)
    progress.append("NODE_COMPLETE",candidate_index=index,node="L3",status="CERTIFIED" if l3ok else "INCOMPLETE",
        evaluation_count=l3n,evaluation_scope="BPRIME_INTERVAL_CALLS",leaf_count=len(l3rec["derivative_interval_records"]),failure_reason=l3why,
        elapsed_seconds=f"{time.monotonic()-node_started:.6f}")
    counts={"L1":len(l1[0]),"L2":len(l2[0]),"L3":1};evals={"L1":l1[3],"L2":l2[3],"L3":l3n}
    failure=l1[2] or l2[2] or l3why;allok=l1[1] and l2[1] and l3ok
    for rec in l1[0]+l2[0]:previous=model.append_record(records,previous,rec)
    previous=model.append_record(records,previous,l3rec)
    j=None;jn=0
    if allok:
        node_started=time.monotonic();progress.append("NODE_START",candidate_index=index,node="J_START",
            lambda_start=model.rational_json(lam_start),u_max=model.dyadic_json(u_max),evaluation_count=0)
        j,jwhy,jn=_build_j_start(index,lam_start,u_max,config,route,kernel,adapter,acb,arb,fmpq);failure=failure or jwhy
        if j is not None:previous=model.append_record(records,previous,j)
        progress.append("NODE_COMPLETE",candidate_index=index,node="J_START",status="CERTIFIED" if j else "INCOMPLETE",
            evaluation_count=jn,evaluation_scope="F_POINT_OUTER_EVALUATIONS",failure_reason=jwhy,
            elapsed_seconds=f"{time.monotonic()-node_started:.6f}")
    else:
        progress.append("NODE_SKIPPED",candidate_index=index,node="J_START",status="PREREQUISITE_INCOMPLETE",
            evaluation_count=0,evaluation_scope="F_POINT_OUTER_EVALUATIONS",failure_reason=failure)
    accepted=allok and j is not None
    node_status={"L1":"CERTIFIED" if l1[1] else "INCOMPLETE",
                 "L2":"CERTIFIED" if l2[1] else "INCOMPLETE",
                 "L3":"CERTIFIED" if l3ok else "INCOMPLETE",
                 "J_START":"CERTIFIED" if j else "NOT_CERTIFIED"}
    previous=model.append_record(records,previous,{"record_type":"CANDIDATE_SUMMARY","candidate_index":index,
        "lambda_start":model.rational_json(lam_start),"u_max":model.dyadic_json(u_max),"coverage_counts":counts,
        "route_evaluations":{**evals,"J_START":jn},"node_status":node_status,
        "candidate_accepted":accepted,"first_failure_reason":None if accepted else (failure or "CANDIDATE_INCOMPLETE")})
    progress.append("PAIR_COMPLETE",candidate_index=index,status="ACCEPTED" if accepted else "INCOMPLETE",
        evaluation_count=sum(evals.values())+jn,evaluation_scope="NODE_REPORTED_EVALUATIONS",
        first_failure_reason=None if accepted else (failure or "CANDIDATE_INCOMPLETE"),
        elapsed_seconds=f"{time.monotonic()-pair_started:.6f}")
    return previous,(index,lam_start,u_max,j) if accepted else None,counts,1 if j else 0

def run(config_path:Path,output_directory:Path)->dict[str,Any]:
    root=repository_root();model.need(not config_path.is_absolute(),"relative config")
    raw=provenance.repo_file(root,config_path.as_posix()).read_bytes();config=model.parse_canonical_json(raw);model.validate_config(config)
    source_head=git_head(root);provenance.verify_implementation_sources(root,config["implementation"]);provenance.verify_stage1_dependency(root,config["stage1_dependency"])
    model.need(not output_directory.exists(),"fresh output required");output_directory.mkdir(parents=True,mode=0o700)
    config_hash=model.sha256_bytes(raw);progress=_ProgressJournal(output_directory/PROGRESS_FILE)
    progress.append("RUN_START",source_head=source_head,blocal_run_config_sha256=config_hash,
                    lambda_candidate_count=len(config["lambda_candidates"]),u_max_candidate_count=len(config["u_max_candidates"]))
    route,audit,checker,l3_route=_load_aux(root,config);adapter=_load_adapter(root,config)
    from flint import acb,arb,ctx,fmpq  # type: ignore[import-not-found]
    ctx.prec=config["precision"]["bits"]
    kernel=provenance.load_pinned_module(root,config["kernel"],"blocal_v22_pinned_kernel",tuple(config["kernel"]["required_api"]),{"FORMULA_STATE":config["kernel"]["formula_state"]})
    helper=route.validate_helper_lemmas(arb,fmpq,config);l3_prepared=l3_route.prepare(root,config)
    records=[];previous=model.chain_genesis(config_hash)
    previous=model.append_record(records,previous,{"record_type":"RUN_HEADER","schema":model.SCHEMA,"design_version":model.DESIGN_VERSION,
        "source_head":source_head,"blocal_run_config_sha256":config_hash,"design_contracts":config["design_contracts"],"design_commits":DESIGN_COMMITS,
        "kernel_source_sha256":config["kernel"]["sha256"],"adapter_source_sha256":config["adapter"]["source_sha256"],
        "helper_lemma_validation":helper,"route_policies":config["route_policies"],"l3_bprime_route":config["l3_bprime_route"],"geometry":config["geometry"],"budgets":config["budgets"],
        "chain_domain":model.CHAIN_DOMAIN,"chain_genesis":model.chain_genesis(config_hash)})
    totals={"L1":0,"L2":0,"L3":0};selected=None;attempted=0;jtotal=0
    for idx,(s,u) in enumerate(_schedule(config)):
        previous,here,counts,jc=_append_candidate(records,previous,idx,s,u,config,route,l3_route,l3_prepared,kernel,adapter,acb,arb,fmpq,progress)
        for k in totals:totals[k]+=counts[k]
        attempted+=1;jtotal+=jc
        if here is not None:selected=here;break
    chain_tip=previous
    previous=model.append_record(records,previous,{"record_type":"RUN_SUMMARY","selected_candidate_index":selected[0] if selected else None,
        "lambda_start":model.rational_json(selected[1]) if selected else None,"u_max":model.dyadic_json(selected[2]) if selected else None,
        "start_root_interval":selected[3]["r_interval"] if selected else None,"exact_counts":{"attempted_candidates":attempted,"j_start_records":jtotal,**totals},
        "records_chain_tip_sha256":chain_tip,"terminal_state":model.COMPLETE if selected else model.INCOMPLETE})
    check=checker.verify_records(records,config,config_hash);model.need(check["valid"] is True,"checker gate")
    machine={"schema":MACHINE_SCHEMA,"status":model.COMPLETE if selected else model.INCOMPLETE,"selected_candidate_index":selected[0] if selected else None,
             "lambda_start":model.rational_json(selected[1]) if selected else None,"u_max":model.dyadic_json(selected[2]) if selected else None,
             "start_root_interval":selected[3]["r_interval"] if selected else None,"all_F_Fr_consumers_finite_routes":True,
             "l3_boundary_monotonicity_route":True,"all_required_consumers_authorized_routes":True}
    certificate={"schema":CERTIFICATE_SCHEMA,"design_version":model.DESIGN_VERSION,"status":machine["status"],"source_head":source_head,
        "design_commits":DESIGN_COMMITS,"design_contracts":config["design_contracts"],"blocal_run_config_sha256":config_hash,
        "kernel_source_sha256":config["kernel"]["sha256"],"selected_candidate_index":machine["selected_candidate_index"],"lambda_start":machine["lambda_start"],
        "u_max":machine["u_max"],"j_start":selected[3] if selected else None,"counts":totals,"budgets":config["budgets"],"machine_conclusion":machine,
        "scope":"B-LOCAL/B-ENTRY only; workflow/tag/production remain separately unauthorized."}
    records_raw=b"\n".join(model.canonical_json_bytes(r) for r in records);cert_raw=model.canonical_json_bytes(certificate)
    summary={"schema":SUMMARY_SCHEMA,"terminal_state":machine["status"],"blocal_run_config_sha256":config_hash,"source_head":source_head,
             "records_sha256":model.sha256_bytes(records_raw),"certificate_sha256":model.sha256_bytes(cert_raw),"calibration_started":False,"tag_created":False}
    out=config["outputs"];(output_directory/out["records"]).write_bytes(records_raw);(output_directory/out["certificate"]).write_bytes(cert_raw);(output_directory/out["summary"]).write_bytes(model.canonical_json_bytes(summary))
    progress.append("RUN_COMPLETE",status=machine["status"],selected_candidate_index=machine["selected_candidate_index"])
    return summary

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--config",required=True,type=Path);p.add_argument("--output-dir",required=True,type=Path);a=p.parse_args(argv)
    s=run(a.config,a.output_dir);print(model.canonical_json_bytes(s).decode("ascii"));return 0 if s["terminal_state"]==model.COMPLETE else 2
if __name__=="__main__":raise SystemExit(main())
