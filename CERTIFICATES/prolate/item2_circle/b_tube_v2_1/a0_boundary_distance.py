#!/usr/bin/env python3
"""B-TUBE A0: derive a start-root distance from the frozen B-LOCAL artifact."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from fractions import Fraction as Q
from pathlib import Path

ART="7c1748148470426648dd03a483a076b043ed70558258358834671451267e64dc"
REC="07b7190d003bb07ef7b2b87be26edd3ee505c717fba238e4ffa7b6529b909c90"
BCERT="b8d27c01d63f3ea53bfeb165f7e140d739fab6b3949115e0aac3fd64b2d05cb6"
BSUM="de080aa321aec0b665dbe0bdbba704cfd7a4de8c77c03b41393f153338e82535"
CFG="dab371fa62ed10a00029cd31b0002e503952277ef072fb8f5d7fd5222965d469"
SRC="a8997d11850dbd5b63e3064560a1c311e5c9c267"
KER="77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac"
S1A="ab7112ae7ae570555d1add5c48adb72100562c71aff6b74c94883f58da0f495b"
S1C="d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188"
S1S="b0582728d3f8fd3508ba8574a898017212a28caa"
BPS="f5f2fe68773423e7ff037e4be9e31094a4ceff5489abd5aff8b14fc1361cd671"
IDS="ee77ba15192a288491eb8b0fe9ecfac5ce0275808ac83f65a36503dc27cc1233"
ID="BLOCAL_L3_BOUNDARY_IDENTITY_B_EQ_F_R1_V1"
ROUTE="BLOCAL_L3_STAGE1_ENDPOINT_PLUS_BPRIME_MONOTONICITY_V1"
LP=Q(206539,100000); LS=Q(3307749,1600000); RLO=Q(2047,2048)

class A0Error(RuntimeError): pass
def need(x,m):
    if not x: raise A0Error(m)
def sh(b): return hashlib.sha256(b).hexdigest()
def rat(x): return Q(int(x["p"]),int(x["q"]))
def dy(x): return Q(int(x["m"]),1<<int(x["e"]))
def rj(x): return {"p":str(x.numerator),"q":str(x.denominator)}
def dj(m,e): return {"e":e,"m":str(m)}
def canon(x): return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
_canonical_json_bytes=canon

def evidence(path:Path):
    raw=path.read_bytes(); need(sh(raw)==ART,"B-LOCAL artifact digest")
    with zipfile.ZipFile(path) as z:
        rr=z.read("records.blocal.jsonl"); cr=z.read("certificate.blocal.json"); sr=z.read("run-summary.blocal.json")
    need(sh(rr)==REC and sh(cr)==BCERT and sh(sr)==BSUM,"B-LOCAL member digest")
    rs=[json.loads(x) for x in rr.split(b"\n")]; need(len(rs)==7,"B-LOCAL record count")
    cert=json.loads(cr); summ=json.loads(sr); h,_,_,l3,j,cand,last=rs
    need(summ.get("source_head")==SRC and summ.get("blocal_run_config_sha256")==CFG and summ.get("terminal_state")=="BLOCAL_COMPLETE","B-LOCAL summary")
    need(cert.get("source_head")==SRC and cert.get("blocal_run_config_sha256")==CFG and cert.get("kernel_source_sha256")==KER and cert.get("status")=="BLOCAL_COMPLETE","B-LOCAL certificate")
    need(h.get("source_head")==SRC and h.get("blocal_run_config_sha256")==CFG and h.get("kernel_source_sha256")==KER,"B-LOCAL header")
    need(cand.get("candidate_accepted") is True and last.get("terminal_state")=="BLOCAL_COMPLETE","B-LOCAL conclusion")
    need(l3.get("certified") is True and l3.get("route_id")==ROUTE and l3.get("identity_lemma_id")==ID and l3.get("boundary_identity_applied") is True,"L3 route/identity")
    need(rat(l3["lambda_plus"])==LP and rat(l3["lambda_start"])==LS and rat(l3["derivative_proof_domain"]["lo"])==LP and rat(l3["derivative_proof_domain"]["hi"])==LS,"L3 lambda domain")
    s1=l3["stage1_dependency"]
    need((s1.get("artifact_zip_sha256"),s1.get("certificate_sha256"),s1.get("source_head"),s1.get("bprime_source_sha256"),s1.get("identity_source_sha256"))==(S1A,S1C,S1S,BPS,IDS),"Stage-1 provenance")
    ep=l3["stage1_endpoint_evidence"]; blo=rat(ep["enclosure"]["lo"]); bhi=rat(ep["enclosure"]["hi"])
    bp=l3["final_Bprime_enclosure"]; bplo=dy(bp["lo"]); bphi=dy(bp["hi"])
    need(ep.get("strict_upper_lt_zero") is True and blo<=bhi<0 and l3.get("Bprime_upper_lt_zero") is True and bplo<=bphi<0,"B/B-prime signs")
    need(j.get("certified") is True and j.get("claim")=="J_START_UNIQUE_NONDEGENERATE_ROOT" and rat(j["lambda_start"])==LS,"J_START identity")
    need(dy(j["r_interval"]["lo"])==RLO and dy(j["r_interval"]["hi"])==1,"J_START bracket")
    d=j["condition5_derivative_record"]
    need(d.get("record_id")=="J-DERIVATIVE-FULL" and dy(d["r_interval"]["lo"])<=RLO and dy(d["r_interval"]["hi"])>=1,"derivative domain")
    flo=dy(d["F_r"]["lo"]); fhi=dy(d["F_r"]["hi"]); need(flo<=fhi<0,"derivative sign")
    return ep,bp,d,bhi,bphi,max(abs(flo),abs(fhi)),j

def derive(path:Path):
    ep,bp,d,bhi,bphi,M,j=evidence(path); gap=LS-LP; need(gap==Q(1,512),"lambda gap")
    bu=bhi+gap*bphi; need(bu<0,"B(lambda_start) sign"); al=-bu; delta=al/M
    need(delta>Q(1,8192),"delta_start <= 2^-13"); need(delta<=Q(1,2048),"delta_start > 2^-11 inconsistent with B-LOCAL bracket"); rhi=1-delta; need(RLO<rhi<Q(8191,8192),"refined bracket")
    return {"B_lambda_plus_enclosure":ep["enclosure"],"B_lambda_start_abs_lower":rj(al),"B_lambda_start_upper":rj(bu),"Bprime_enclosure":bp,"F_r_enclosure":d["F_r"],"M_abs_F_r_upper":rj(M),"blocal_artifact_sha256":ART,"blocal_certificate_sha256":BCERT,"blocal_config_sha256":CFG,"blocal_records_sha256":REC,"blocal_source_head":SRC,"boundary_identity_id":ID,"claim":"1-r_*(lambda_start)>=delta_start_exact>2^-13","delta_start_dyadic_floor":dj(1,13),"delta_start_exact":rj(delta),"derivative_domain_r":d["r_interval"],"derivative_record_id":d["record_id"],"lambda_gap":dj(1,9),"lambda_plus":rj(LP),"lambda_start":rj(LS),"operational_refined_start_root_interval":{"hi":dj(8191,13),"lo":dj(2047,11)},"refined_start_root_upper_exact":rj(rhi),"schema":"btube-a0-boundary-distance-v1","stage1_artifact_sha256":S1A,"stage1_certificate_sha256":S1C,"stage1_source_head":S1S,"status":"A0_CERTIFIED","target_start_root_interval":j["r_interval"]}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("--artifact",required=True,type=Path); p.add_argument("--out",required=True,type=Path); a=p.parse_args(argv)
    try: c=derive(a.artifact)
    except (A0Error,OSError,zipfile.BadZipFile,KeyError,ValueError) as e: print(f"A0Error: {e}"); return 2
    a.out.write_bytes(canon(c)); print("A0_CERTIFIED"); return 0
if __name__=="__main__": raise SystemExit(main())
