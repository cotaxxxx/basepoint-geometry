#!/usr/bin/env python3
"""B-LOCAL v2.2 pinned runner with explicit L1 boundary-strip regularization."""
from __future__ import annotations

import argparse
import subprocess
from collections import deque
from fractions import Fraction
from pathlib import Path
from typing import Any

import blocal_phase4_engine as v21_engine
import blocal_phase4_provenance as provenance
import blocal_v22_model as model

DESIGN_COMMIT = "85f453d8b216e98ad9eadea54ab7a7dca1cc31fd"
CERTIFICATE_SCHEMA = "blocal-certificate-v2"
SUMMARY_SCHEMA = "blocal-run-summary-v2"
MACHINE_SCHEMA = "btube-blocal-machine-conclusion-v2"


def repository_root() -> Path:
    return Path(__file__).resolve(strict=True).parents[4]


def git_head(root: Path) -> str:
    head = subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                          check=True,capture_output=True,text=True).stdout.strip()
    model.need(len(head)==40 and all(c in "0123456789abcdef" for c in head), "source head")
    return head


def _schedule(config: dict[str, Any]) -> list[tuple[Fraction,Fraction]]:
    ds=[model.fraction_from_dyadic(x) for x in config["lambda_candidates"]]
    us=[model.fraction_from_dyadic(x) for x in config["u_max_candidates"]]
    return [(d,u) for d in ds for u in us]


def _load_adapter(root: Path, config: dict[str, Any]) -> Any:
    return provenance.load_pinned_module(
        root,{"path":config["adapter"]["path"],"sha256":config["adapter"]["source_sha256"]},
        "blocal_v22_pinned_adapter",("arb_ball_to_canonical_dyadic_interval",),
        {"ADAPTER_ID":model.ADAPTER_ID})


def _load_auxiliary(root: Path, config: dict[str, Any]) -> tuple[Any,Any,Any]:
    pins=config["implementation"]["sources_sha256"]
    boundary_path="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"
    audit_path=config["symbolic_audit"]["path"]
    checker_path=config["checker"]["path"]
    boundary=provenance.load_pinned_module(
        root,{"path":boundary_path,"sha256":pins[boundary_path]},"blocal_v22_pinned_boundary",
        ("enclose_boundary_hu",),{"BOUNDARY_ROUTE_ID":model.BOUNDARY_ROUTE_ID,"LEMMA_ID":model.BOUNDARY_LEMMA_ID})
    audit=provenance.load_pinned_module(
        root,{"path":audit_path,"sha256":config["symbolic_audit"]["source_sha256"]},
        "blocal_v22_pinned_symbolic_audit",("run_audit",),{"AUDIT_ID":model.SYMBOLIC_AUDIT_ID})
    checker=provenance.load_pinned_module(
        root,{"path":checker_path,"sha256":config["checker"]["source_sha256"]},
        "blocal_v22_pinned_checker",("verify_records",),{"CHECKER_ID":model.CHECKER_ID})
    result=audit.run_audit()
    model.need(result.get("exact_algebra") is True and result.get("J_equals_rho_K") is True,
               "symbolic audit gate")
    return boundary,audit,checker


def _split_domain(domain: tuple[Fraction,Fraction,Fraction,Fraction]) -> list[tuple[Fraction,Fraction,Fraction,Fraction]]:
    return v21_engine.split_l1(*domain)


def _certify_l1_interior(candidate_index: int,u_cut: Fraction,u_max: Fraction,s_start: Fraction,
                         config: dict[str,Any],kernel: Any,adapter: Any,
                         arb_type: Any,fmpq_type: Any) -> tuple[list[dict[str,Any]],bool,str|None,int]:
    budget=config["budgets"]["L1_INTERIOR"]
    pending: deque[tuple[tuple[Fraction,Fraction,Fraction,Fraction],int]]=deque([
        ((u_cut,u_max,-model.S_NEG,s_start),0)])
    leaves=[]; evaluations=0; first_failure=None
    while pending:
        domain,depth=pending.popleft(); u0,u1,s0,s1=domain
        did=evaluations < budget["max_evaluations"]
        if did:
            enclosure=v21_engine.evaluate_l1(kernel,adapter,arb_type,fmpq_type,config,u0,u1,s0,s1)
            evaluations+=1
            certified=v21_engine.strict_sign("L1",enclosure)
        else:
            enclosure=model.interval_json(Fraction(-1),Fraction(1)); certified=False
            first_failure=first_failure or "L1_INTERIOR_EVALUATION_BUDGET_EXHAUSTED"
        can=(not certified and first_failure is None and depth<budget["max_depth"]
             and len(leaves)+len(pending)+2<=budget["max_tiles"]
             and evaluations<budget["max_evaluations"])
        if can:
            pending.extend((child,depth+1) for child in _split_domain(domain)); continue
        if not certified:
            first_failure=first_failure or (
                "L1_INTERIOR_DEPTH_LIMIT" if depth>=budget["max_depth"] else
                "L1_INTERIOR_TILE_LIMIT" if len(leaves)+len(pending)+1>=budget["max_tiles"] else
                "L1_INTERIOR_STRICT_SIGN_UNRESOLVED")
        leaves.append({
            "record_type":"TILE","node":"L1_INTERIOR","candidate_index":candidate_index,
            "u_interval":model.interval_json(u0,u1),"s_interval":model.interval_json(s0,s1),
            "enclosure":enclosure,"certified":certified,"depth":depth,
            "evaluations":1 if did else 0,"adapter_id":model.ADAPTER_ID,
            "kernel_source_sha256":config["kernel"]["sha256"],
            "strict_predicate":"LOWER_GT_ZERO","quantity":"H_u_EQUALS_NEGATIVE_F_r",
            "failure_reason":None if certified else first_failure,
            "closed_subdomain":"L1_INTERIOR",
        })
    return leaves,all(x["certified"] for x in leaves),first_failure,evaluations


def _certify_l1_boundary(candidate_index: int,u_cut: Fraction,s_start: Fraction,
                         config: dict[str,Any],kernel: Any,adapter: Any,boundary: Any,
                         acb_type: Any,arb_type: Any,fmpq_type: Any) -> tuple[list[dict[str,Any]],bool,str|None,int]:
    budget=config["budgets"]["L1_BOUNDARY"]
    pending: deque[tuple[tuple[Fraction,Fraction,Fraction,Fraction],int]]=deque([
        ((Fraction(0),u_cut,-model.S_NEG,s_start),0)])
    leaves=[]; evaluations=0; first_failure=None
    while pending:
        domain,depth=pending.popleft(); u0,u1,s0,s1=domain
        did=evaluations < budget["max_evaluations"]
        diagnostics: dict[str,Any]={}; pieces_json: dict[str,Any]={}
        if did:
            ball,diagnostics,pieces=boundary.enclose_boundary_hu(
                kernel,acb_type,arb_type,fmpq_type,config,u0,u1,s0,s1)
            enclosure=adapter.arb_ball_to_canonical_dyadic_interval(ball)
            for name,piece in pieces.items():
                pieces_json[name]=adapter.arb_ball_to_canonical_dyadic_interval(piece)
            evaluations+=1
            certified=model.interval_fractions(enclosure,"boundary enclosure")[0]>0
        else:
            enclosure=model.interval_json(Fraction(-1),Fraction(1)); certified=False
            first_failure=first_failure or "L1_BOUNDARY_EVALUATION_BUDGET_EXHAUSTED"
        can=(not certified and first_failure is None and depth<budget["max_depth"]
             and len(leaves)+len(pending)+2<=budget["max_tiles"]
             and evaluations<budget["max_evaluations"])
        if can:
            pending.extend((child,depth+1) for child in _split_domain(domain)); continue
        if not certified:
            first_failure=first_failure or (
                "L1_BOUNDARY_DEPTH_LIMIT" if depth>=budget["max_depth"] else
                "L1_BOUNDARY_TILE_LIMIT" if len(leaves)+len(pending)+1>=budget["max_tiles"] else
                "L1_BOUNDARY_STRICT_SIGN_UNRESOLVED")
        leaves.append({
            "record_type":"BOUNDARY_STRIP_TILE","node":"L1_BOUNDARY","candidate_index":candidate_index,
            "u_interval":model.interval_json(u0,u1),"s_interval":model.interval_json(s0,s1),
            "enclosure":enclosure,"piece_enclosures":pieces_json,"diagnostics":diagnostics,
            "certified":certified,"depth":depth,"evaluations":1 if did else 0,
            "adapter_id":model.ADAPTER_ID,"kernel_source_sha256":config["kernel"]["sha256"],
            "boundary_route_source_sha256":config["implementation"]["sources_sha256"][
                "CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"],
            "symbolic_audit_source_sha256":config["symbolic_audit"]["source_sha256"],
            "strict_predicate":"LOWER_GT_ZERO","quantity":"H_u_EQUALS_NEGATIVE_F_r",
            "failure_reason":None if certified else first_failure,"closed_subdomain":"L1_BOUNDARY_STRIP",
        })
    return leaves,all(x["certified"] for x in leaves),first_failure,evaluations


def _append_candidate(records: list[dict[str,Any]],previous: str,candidate_index: int,
                      s_start: Fraction,u_max: Fraction,config: dict[str,Any],kernel: Any,
                      adapter: Any,boundary: Any,acb_type: Any,arb_type: Any,fmpq_type: Any
                      ) -> tuple[str,tuple[int,Fraction,Fraction,dict[str,Any]]|None,dict[str,int],int]:
    u_cut=model.fraction_from_dyadic(config["boundary_strip"]["u_cut"])
    lambda_start=model.LAMBDA_PLUS+s_start
    li=_certify_l1_interior(candidate_index,u_cut,u_max,s_start,config,kernel,adapter,arb_type,fmpq_type)
    lb=_certify_l1_boundary(candidate_index,u_cut,s_start,config,kernel,adapter,boundary,acb_type,arb_type,fmpq_type)
    l2=v21_engine.certify_node("L2",candidate_index,u_max,s_start,config,
        lambda s0,s1:v21_engine.evaluate_l2(kernel,adapter,arb_type,fmpq_type,config,u_max,s0,s1),
        config["kernel"]["sha256"])
    l3=v21_engine.certify_node("L3",candidate_index,u_max,s_start,config,
        lambda s0,s1:v21_engine.evaluate_l3_route_a(kernel,adapter,arb_type,fmpq_type,config,s0,s1),
        config["kernel"]["sha256"])
    results={"L1_INTERIOR":li,"L1_BOUNDARY":lb,"L2":l2,"L3":l3}
    counts={}; evaluations={}; first_failure=None; all_nodes=True
    for node in ("L1_BOUNDARY","L1_INTERIOR","L2","L3"):
        leaves,certified,failure,count=results[node]
        for leaf in leaves: previous=model.append_record(records,previous,leaf)
        counts[node]=len(leaves); evaluations[node]=count
        all_nodes=all_nodes and certified; first_failure=first_failure or failure
    j_start=None; j_count=0
    if all_nodes:
        j_start,j_failure,j_count=v21_engine.build_j_start(candidate_index,lambda_start,u_max,config,
                                                           kernel,adapter,arb_type,fmpq_type)
        first_failure=first_failure or j_failure
        if j_start is not None: previous=model.append_record(records,previous,j_start)
    accepted=all_nodes and j_start is not None
    previous=model.append_record(records,previous,{
        "record_type":"CANDIDATE_SUMMARY","candidate_index":candidate_index,
        "lambda_start":model.rational_json(lambda_start),"u_max":model.dyadic_json(u_max),
        "u_cut":config["boundary_strip"]["u_cut"],"coverage_counts":counts,
        "kernel_evaluations":{**evaluations,"J_START":j_count},
        "node_status":{node:("CERTIFIED" if results[node][1] else "INCOMPLETE") for node in results}
                      | {"L1":"CERTIFIED" if li[1] and lb[1] else "INCOMPLETE",
                         "J_START":"CERTIFIED" if j_start else "NOT_CERTIFIED"},
        "candidate_accepted":accepted,"first_failure_reason":None if accepted else (first_failure or "CANDIDATE_INCOMPLETE"),
        "unresolved":not accepted,
    })
    selected=(candidate_index,lambda_start,u_max,j_start) if accepted else None
    return previous,selected,counts,1 if j_start is not None else 0


def run(config_path: Path,output_directory: Path) -> dict[str,Any]:
    root=repository_root(); model.need(not config_path.is_absolute(),"relative config path")
    config_file=provenance.repo_file(root,config_path.as_posix()); raw=config_file.read_bytes()
    config=model.parse_canonical_json(raw); model.validate_config(config); source_head=git_head(root)
    provenance.verify_implementation_sources(root,config["implementation"])
    provenance.verify_stage1_dependency(root,config["stage1_dependency"])
    boundary,audit,checker=_load_auxiliary(root,config); adapter=_load_adapter(root,config)
    from flint import acb,arb,ctx,fmpq  # type: ignore[import-not-found]
    ctx.prec=config["precision"]["bits"]
    kernel=provenance.load_pinned_module(root,config["kernel"],"blocal_v22_pinned_kernel",
                                         tuple(config["kernel"]["required_api"]),
                                         {"FORMULA_STATE":config["kernel"]["formula_state"]})
    model.need(not output_directory.exists(),"output directory must not pre-exist")
    output_directory.mkdir(parents=True,mode=0o700); model.need(not any(output_directory.iterdir()),"fresh output")
    config_hash=model.sha256_bytes(raw); previous=model.chain_genesis(config_hash); records=[]
    previous=model.append_record(records,previous,{
        "record_type":"RUN_HEADER","schema":model.SCHEMA,"design_version":model.DESIGN_VERSION,
        "blocal_run_config_sha256":config_hash,"source_head":source_head,
        "stage1_dependency":config["stage1_dependency"],"kernel_source_sha256":config["kernel"]["sha256"],
        "adapter_source_sha256":config["adapter"]["source_sha256"],"endpoint_route":config["endpoint_route"],
        "boundary_strip":config["boundary_strip"],"checker":config["checker"],"symbolic_audit":config["symbolic_audit"],
        "candidate_schedule":{"order":config["candidate_order"],"lambda_candidates":config["lambda_candidates"],
                              "u_max_candidates":config["u_max_candidates"],"candidate_count":105},
        "precision":config["precision"],"budgets":config["budgets"],"chain_domain":model.CHAIN_DOMAIN,
        "chain_genesis":model.chain_genesis(config_hash),
    })
    totals={"L1_INTERIOR":0,"L1_BOUNDARY":0,"L2":0,"L3":0}; attempted=0;j_total=0;selected=None
    for idx,(s_start,u_max) in enumerate(_schedule(config)):
        previous,here,counts,jc=_append_candidate(records,previous,idx,s_start,u_max,config,kernel,adapter,boundary,acb,arb,fmpq)
        for k in totals: totals[k]+=counts[k]
        attempted+=1;j_total+=jc
        if here is not None: selected=here;break
    chain_tip=previous
    previous=model.append_record(records,previous,{
        "record_type":"RUN_SUMMARY","selected_candidate_index":selected[0] if selected else None,
        "lambda_start":model.rational_json(selected[1]) if selected else None,
        "u_max":model.dyadic_json(selected[2]) if selected else None,
        "u_cut":config["boundary_strip"]["u_cut"],"start_root_interval":selected[3]["r_interval"] if selected else None,
        "exact_counts":{"attempted_candidates":attempted,"records_before_summary":len(records),
                        "j_start_records":j_total,**totals},
        "records_chain_tip_sha256":chain_tip,"terminal_state":model.COMPLETE if selected else model.INCOMPLETE,
    })
    checker_result=checker.verify_records(records,config,config_hash)
    model.need(checker_result["valid"] is True,"independent checker rejected generated records")
    machine={
        "schema":MACHINE_SCHEMA,"status":model.COMPLETE if selected else model.INCOMPLETE,
        "selected_candidate_index":selected[0] if selected else None,
        "lambda_start":model.rational_json(selected[1]) if selected else None,
        "start_root_interval":selected[3]["r_interval"] if selected else None,
        "machine_claims":{
            "stage1_dependency_exact":selected is not None,
            "l1_closed_union_exact":selected is not None,
            "l1_boundary_strip_strictly_positive":selected is not None,
            "l1_interior_strictly_positive":selected is not None,
            "l2_inner_face_strictly_positive":selected is not None,
            "l3_boundary_face_strictly_negative":selected is not None,
            "start_root_interval_certified":selected is not None,
            "real_analytic_claimed":False,
        },"checker":checker_result,"chain_tip_sha256":chain_tip,
    }
    certificate={
        "schema":CERTIFICATE_SCHEMA,"design_version":model.DESIGN_VERSION,
        "status":model.COMPLETE if selected else model.INCOMPLETE,"source_head":source_head,
        "design_commit":DESIGN_COMMIT,"blocal_run_config_sha256":config_hash,
        "kernel_source_sha256":config["kernel"]["sha256"],"arb_to_dyadic_adapter_sha256":config["adapter"]["source_sha256"],
        "boundary_strip":config["boundary_strip"],"selected_candidate_index":selected[0] if selected else None,
        "lambda_start":model.rational_json(selected[1]) if selected else None,
        "u_max":model.dyadic_json(selected[2]) if selected else None,"u_cut":config["boundary_strip"]["u_cut"],
        "s_start":model.dyadic_json(selected[1]-model.LAMBDA_PLUS) if selected else None,
        "j_start":selected[3] if selected else None,"counts":totals,"budgets":config["budgets"],
        "chain_genesis":model.chain_genesis(config_hash),"chain_tip":chain_tip,
        "machine_conclusion":machine,"scope":"B-LOCAL/B-ENTRY only; calibration and B-TUBE production remain unauthorized.",
        "real_analytic":False,"certificate_sha256":None,"artifact_zip_sha256":None,
    }
    records_raw=b"\n".join(model.canonical_json_bytes(r) for r in records)
    cert_raw=model.canonical_json_bytes(certificate)
    summary={"schema":SUMMARY_SCHEMA,"terminal_state":model.COMPLETE if selected else model.INCOMPLETE,
             "blocal_run_config_sha256":config_hash,"source_head":source_head,
             "records_sha256":model.sha256_bytes(records_raw),"certificate_sha256":model.sha256_bytes(cert_raw),
             "artifact_zip_sha256":None,"calibration_started":False,"tag_created":False}
    out=config["outputs"]
    (output_directory/out["records"]).write_bytes(records_raw)
    (output_directory/out["certificate"]).write_bytes(cert_raw)
    (output_directory/out["summary"]).write_bytes(model.canonical_json_bytes(summary))
    return summary


def main(argv: list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description="B-LOCAL v2.2 pinned runner")
    parser.add_argument("--config",required=True,type=Path);parser.add_argument("--output-dir",required=True,type=Path)
    args=parser.parse_args(argv);summary=run(args.config,args.output_dir)
    print(model.canonical_json_bytes(summary).decode("ascii"))
    return 0 if summary["terminal_state"]==model.COMPLETE else 2


if __name__=="__main__":
    raise SystemExit(main())
