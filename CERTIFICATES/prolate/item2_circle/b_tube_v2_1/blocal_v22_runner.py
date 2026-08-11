#!/usr/bin/env python3
"""B-LOCAL v2.2 runner: finite F/K routes for L1/L2/L3/J_START."""
from __future__ import annotations
import argparse, subprocess
from collections import deque
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
]
CERTIFICATE_SCHEMA="blocal-certificate-v2-finite-routes"
SUMMARY_SCHEMA="blocal-run-summary-v2-finite-routes"
MACHINE_SCHEMA="btube-blocal-machine-conclusion-v2-finite-routes"


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

def _load_aux(root:Path,config:dict[str,Any])->tuple[Any,Any,Any]:
    pins=config["implementation"]["sources_sha256"]
    route_path="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"
    route=provenance.load_pinned_module(root,{"path":route_path,"sha256":pins[route_path]},"blocal_v22_pinned_finite_route",
        ("enclose_hu","enclose_f","validate_helper_lemmas"),{"F_ROUTE_ID":policy.F_ROUTE_ID,"K_ROUTE_ID":policy.K_ROUTE_ID})
    audit=provenance.load_pinned_module(root,{"path":config["symbolic_audit"]["path"],"sha256":config["symbolic_audit"]["source_sha256"]},
        "blocal_v22_pinned_symbolic_audit",("run_audit",),{"AUDIT_ID":model.SYMBOLIC_AUDIT_ID})
    checker=provenance.load_pinned_module(root,{"path":config["checker"]["path"],"sha256":config["checker"]["source_sha256"]},
        "blocal_v22_pinned_checker",("verify_records",),{"CHECKER_ID":model.CHECKER_ID})
    a=audit.run_audit();model.need(a.get("exact_algebra") is True and a.get("F_route_exact") is True and a.get("J_equals_rho_K") is True,"symbolic audit gate")
    return route,audit,checker

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
    budget=config["budgets"]["J_START"];count=0;points=[]
    def f_at(r:Fraction,role:str)->tuple[dict[str,Any],dict[str,Any]]:
        nonlocal count
        model.need(count<budget["max_evaluations"],"J_START evaluation budget")
        iv,proof=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,r,r,lambda_start,lambda_start,None);count+=1
        lo,hi=model.interval_fractions(iv,"J F");sign="POSITIVE" if lo>0 else "NEGATIVE" if hi<0 else "UNRESOLVED"
        rec={"evaluation_id":f"J-F-{count:03d}","r":model.rational_json(r),"lambda_start":model.rational_json(lambda_start),
             "route_id":policy.F_ROUTE_ID,"route_proof":proof,"normalized_F":iv,"sign":sign,"role":role}
        points.append(rec);return iv,rec
    left,right=1-u_max,Fraction(1);fleft,leftrec=f_at(left,"INITIAL_LEFT")
    if model.interval_fractions(fleft)[0]<=0:return None,"J_START_LEFT_SIGN_UNRESOLVED",count
    fright=None;rightrec=None
    for _ in range(budget["max_bisections"]):
        m=(left+right)/2;fm,mrec=f_at(m,"BISECTION_MIDPOINT");lo,hi=model.interval_fractions(fm)
        if hi<0:right,fright,rightrec=m,fm,mrec;rightrec["role"]="RETAINED_RIGHT";break
        if lo>0:left,fleft,leftrec=m,fm,mrec;leftrec["role"]="RETAINED_LEFT";continue
        return None,"J_START_BISECTION_SIGN_UNRESOLVED",count
    if fright is None or right>=1:return None,"J_START_INTERIOR_NEGATIVE_ENDPOINT_NOT_FOUND",count
    model.need(count<budget["max_evaluations"],"J_START derivative budget")
    u0,u1=1-right,1-left;s=lambda_start-model.LAMBDA_PLUS
    hu,huproof=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s,s,"POS");count+=1
    D=model.interval_negate(hu);dlo,dhi=model.interval_fractions(D,"J derivative")
    if dhi>=0:return None,"J_START_DERIVATIVE_NEGATIVITY_UNRESOLVED",count
    derivative={"record_id":"J-DERIVATIVE","r_interval":model.interval_json(left,right),"u_interval":model.interval_json(u0,u1),
                "lambda_start":model.rational_json(lambda_start),"s":model.rational_json(s),"route_id":policy.K_ROUTE_ID,
                "route_proof":huproof,"H_u":hu,"negation_rule_id":policy.NEGATION_RULE_ID,"F_r":D,"sup_F_r_lt_zero":True}
    mid=(left+right)/2;Fm,midrec=f_at(mid,"NEWTON_MIDPOINT")
    quotient,newton=_newton_image(mid,Fm,D);nlo,nhi=model.interval_fractions(newton,"Newton")
    if not(left<nlo<=nhi<right):return None,"J_START_STRICT_SELF_CONTAINMENT_UNRESOLVED",count
    newtonrec={"record_id":"J-NEWTON","bracket":model.interval_json(left,right),"midpoint":model.rational_json(mid),
               "midpoint_F_record_id":midrec["evaluation_id"],"F_m":Fm,"derivative_record_id":derivative["record_id"],"D":D,
               "interval_arithmetic_policy_id":policy.NEWTON_POLICY_ID,"quotient":quotient,"newton_image":newton,
               "strict_self_containment":True,"method_id":"INTERVAL_NEWTON_V2"}
    return {"record_type":"J_START","node":"J_START","candidate_index":candidate_index,"lambda_start":model.rational_json(lambda_start),
            "initial_bracket":model.interval_json(1-u_max,Fraction(1)),"r_interval":model.interval_json(left,right),
            "ordered_bisection_records":points,"derivative_record":derivative,"newton_record":newtonrec,
            "claim":"J_START_UNIQUE_NONDEGENERATE_ROOT","certified":True,
            "direct_pinned_F_arb_called":False,"direct_pinned_dFdr_arb_called":False},None,count

def _append_candidate(records:list[dict[str,Any]],previous:str,index:int,s_start:Fraction,u_max:Fraction,config:dict[str,Any],
                      route:Any,kernel:Any,adapter:Any,acb:Any,arb:Any,fmpq:Any)->tuple[str,tuple|None,dict[str,int],int]:
    lam_start=model.LAMBDA_PLUS+s_start
    l1=_certify_outer("L1",index,(Fraction(0),u_max,-model.S_NEG,s_start),config,
        lambda u0,u1,s0,s1:route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,u0,u1,s0,s1,"POS"),"POS")
    l2=_certify_outer("L2",index,(-model.S_NEG,s_start),config,
        lambda s0,s1:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-u_max,1-u_max,model.LAMBDA_PLUS+s0,model.LAMBDA_PLUS+s1,"POS"),"POS")
    l3=_certify_outer("L3",index,(Fraction(0),s_start),config,
        lambda s0,s1:route.enclose_f(kernel,adapter,acb,arb,fmpq,config,Fraction(1),Fraction(1),model.LAMBDA_PLUS+s0,model.LAMBDA_PLUS+s1,"NEG"),"NEG")
    results={"L1":l1,"L2":l2,"L3":l3};counts={};evals={};failure=None;allok=True
    for node in ("L1","L2","L3"):
        leaves,ok,why,n=results[node]
        for rec in leaves:previous=model.append_record(records,previous,rec)
        counts[node]=len(leaves);evals[node]=n;allok=allok and ok;failure=failure or why
    j=None;jn=0
    if allok:
        j,jwhy,jn=_build_j_start(index,lam_start,u_max,config,route,kernel,adapter,acb,arb,fmpq);failure=failure or jwhy
        if j is not None:previous=model.append_record(records,previous,j)
    accepted=allok and j is not None
    previous=model.append_record(records,previous,{"record_type":"CANDIDATE_SUMMARY","candidate_index":index,
        "lambda_start":model.rational_json(lam_start),"u_max":model.dyadic_json(u_max),"coverage_counts":counts,
        "route_evaluations":{**evals,"J_START":jn},"node_status":{n:("CERTIFIED" if results[n][1] else "INCOMPLETE") for n in results}|{"J_START":"CERTIFIED" if j else "NOT_CERTIFIED"},
        "candidate_accepted":accepted,"first_failure_reason":None if accepted else (failure or "CANDIDATE_INCOMPLETE")})
    return previous,(index,lam_start,u_max,j) if accepted else None,counts,1 if j else 0

def run(config_path:Path,output_directory:Path)->dict[str,Any]:
    root=repository_root();model.need(not config_path.is_absolute(),"relative config")
    raw=provenance.repo_file(root,config_path.as_posix()).read_bytes();config=model.parse_canonical_json(raw);model.validate_config(config)
    source_head=git_head(root);provenance.verify_implementation_sources(root,config["implementation"]);provenance.verify_stage1_dependency(root,config["stage1_dependency"])
    route,audit,checker=_load_aux(root,config);adapter=_load_adapter(root,config)
    from flint import acb,arb,ctx,fmpq  # type: ignore[import-not-found]
    ctx.prec=config["precision"]["bits"]
    kernel=provenance.load_pinned_module(root,config["kernel"],"blocal_v22_pinned_kernel",tuple(config["kernel"]["required_api"]),{"FORMULA_STATE":config["kernel"]["formula_state"]})
    helper=route.validate_helper_lemmas(arb,fmpq,config)
    model.need(not output_directory.exists(),"fresh output required");output_directory.mkdir(parents=True,mode=0o700)
    config_hash=model.sha256_bytes(raw);records=[];previous=model.chain_genesis(config_hash)
    previous=model.append_record(records,previous,{"record_type":"RUN_HEADER","schema":model.SCHEMA,"design_version":model.DESIGN_VERSION,
        "source_head":source_head,"blocal_run_config_sha256":config_hash,"design_contracts":config["design_contracts"],"design_commits":DESIGN_COMMITS,
        "kernel_source_sha256":config["kernel"]["sha256"],"adapter_source_sha256":config["adapter"]["source_sha256"],
        "helper_lemma_validation":helper,"route_policies":config["route_policies"],"geometry":config["geometry"],"budgets":config["budgets"],
        "chain_domain":model.CHAIN_DOMAIN,"chain_genesis":model.chain_genesis(config_hash)})
    totals={"L1":0,"L2":0,"L3":0};selected=None;attempted=0;jtotal=0
    for idx,(s,u) in enumerate(_schedule(config)):
        previous,here,counts,jc=_append_candidate(records,previous,idx,s,u,config,route,kernel,adapter,acb,arb,fmpq)
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
             "start_root_interval":selected[3]["r_interval"] if selected else None,"all_F_Fr_consumers_finite_routes":True}
    certificate={"schema":CERTIFICATE_SCHEMA,"design_version":model.DESIGN_VERSION,"status":machine["status"],"source_head":source_head,
        "design_commits":DESIGN_COMMITS,"design_contracts":config["design_contracts"],"blocal_run_config_sha256":config_hash,
        "kernel_source_sha256":config["kernel"]["sha256"],"selected_candidate_index":machine["selected_candidate_index"],"lambda_start":machine["lambda_start"],
        "u_max":machine["u_max"],"j_start":selected[3] if selected else None,"counts":totals,"budgets":config["budgets"],"machine_conclusion":machine,
        "scope":"B-LOCAL/B-ENTRY only; workflow/tag/production remain separately unauthorized."}
    records_raw=b"\n".join(model.canonical_json_bytes(r) for r in records);cert_raw=model.canonical_json_bytes(certificate)
    summary={"schema":SUMMARY_SCHEMA,"terminal_state":machine["status"],"blocal_run_config_sha256":config_hash,"source_head":source_head,
             "records_sha256":model.sha256_bytes(records_raw),"certificate_sha256":model.sha256_bytes(cert_raw),"calibration_started":False,"tag_created":False}
    out=config["outputs"];(output_directory/out["records"]).write_bytes(records_raw);(output_directory/out["certificate"]).write_bytes(cert_raw);(output_directory/out["summary"]).write_bytes(model.canonical_json_bytes(summary))
    return summary

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--config",required=True,type=Path);p.add_argument("--output-dir",required=True,type=Path);a=p.parse_args(argv)
    s=run(a.config,a.output_dir);print(model.canonical_json_bytes(s).decode("ascii"));return 0 if s["terminal_state"]==model.COMPLETE else 2
if __name__=="__main__":raise SystemExit(main())
