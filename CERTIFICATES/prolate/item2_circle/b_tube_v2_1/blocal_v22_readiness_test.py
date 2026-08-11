#!/usr/bin/env python3
"""Production-shaped runtime readiness for B-LOCAL v2.2 finite F/K routes.

Readiness only; never certificate evidence. Requires python-flint and final config.
"""
from __future__ import annotations
import argparse,json
from fractions import Fraction
from pathlib import Path
from typing import Any
import blocal_phase4_provenance as provenance
import blocal_v22_model as model
import blocal_v22_policy as policy

HERE=Path(__file__).resolve(strict=True).parent
ROOT=HERE.parents[3]

def load(config:dict[str,Any])->tuple[Any,Any,Any]:
    pins=config["implementation"]["sources_sha256"]
    route_path="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/blocal_v22_boundary.py"
    route=provenance.load_pinned_module(ROOT,{"path":route_path,"sha256":pins[route_path]},"blocal_v22_readiness_route",("enclose_hu","enclose_f","validate_helper_lemmas"),{"F_ROUTE_ID":policy.F_ROUTE_ID,"K_ROUTE_ID":policy.K_ROUTE_ID})
    adapter=provenance.load_pinned_module(ROOT,{"path":config["adapter"]["path"],"sha256":config["adapter"]["source_sha256"]},"blocal_v22_readiness_adapter",("arb_ball_to_canonical_dyadic_interval","AdapterError"),{"ADAPTER_ID":model.ADAPTER_ID})
    kernel=provenance.load_pinned_module(ROOT,config["kernel"],"blocal_v22_readiness_kernel",tuple(config["kernel"]["required_api"]),{"FORMULA_STATE":config["kernel"]["formula_state"]})
    return route,adapter,kernel

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser();p.add_argument("--config",type=Path,default=Path("CERTIFICATES/prolate/item2_circle/b_tube_v2_1/config.blocal-v2.2-run.json"));a=p.parse_args(argv)
    raw=(ROOT/a.config).read_bytes();config=model.parse_canonical_json(raw);model.validate_config(config)
    from flint import acb,arb,ctx,fmpq  # type: ignore[import-not-found]
    ctx.prec=config["precision"]["bits"];route,adapter,kernel=load(config);helper=route.validate_helper_lemmas(arb,fmpq,config)
    eps=model.fraction_from_dyadic(config["geometry"]["eps"]);model.need(eps==Fraction(1,1<<8),"readiness eps")
    s_first=model.fraction_from_dyadic(config["lambda_candidates"][0]);lam=model.LAMBDA_PLUS+s_first;umax=model.fraction_from_dyadic(config["u_max_candidates"][0])
    f0,pf0=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-umax,1-umax,lam,lam,None)
    fm,pfm=route.enclose_f(kernel,adapter,acb,arb,fmpq,config,1-umax/2,1-umax/2,lam,lam,None)
    hu,phu=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,umax/2,umax,s_first,s_first,"POS")
    D=model.interval_negate(hu);dlo,dhi=model.interval_fractions(D,"readiness D");model.need(dhi<0,"readiness derivative excludes zero")
    qlo,qhi=model.interval_divide_negative_denominator(fm,D);q=model.outward_dyadic(qlo,qhi);m=1-3*umax/Fraction(4);newton=model.outward_dyadic(m-qhi,m-qlo)
    # Endpoint/L1 corner positive-width smoke with fixed eps.
    hcorner,pcorner=route.enclose_hu(kernel,adapter,acb,arb,fmpq,config,Fraction(0),Fraction(1,1<<12),-model.S_NEG,s_first,None)
    payload={"schema":"blocal-v22-readiness-v2","certificate_evidence":False,"eps":config["geometry"]["eps"],
             "helper_lemmas":helper,"initial_F":f0,"midpoint_F":fm,"positive_width_derivative_Hu":hu,"F_r":D,"quotient":q,"newton_image":newton,
             "corner_strip_Hu":hcorner,"proof_ids":{"initial_F":pf0["proof_id"],"midpoint_F":pfm["proof_id"],"derivative":phu["proof_id"],"corner":pcorner["proof_id"]},
             "direct_pinned_integrators_called":False,"status":"PASS"}
    print(json.dumps(payload,sort_keys=True,separators=(",",":")));return 0
if __name__=="__main__":raise SystemExit(main())
