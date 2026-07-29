#!/usr/bin/env python3
"""B-LOCAL/B-ENTRY v2.1 calculation-free contract self-test.

Synthetic integer fixtures only: no production kernel, workflow, tag, or
archive.  Covers canonical exact objects, adapter contract, chain/record order,
L1/L2/L3 domains, complete J_START, mode guards, and 46 negative controls.
"""
from __future__ import annotations
from copy import deepcopy
from fractions import Fraction
import hashlib, json, math, re
from typing import Any, Callable

class Reject(Exception): pass
def bad(s:str)->None: raise Reject(s)
def H(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def nofloat(x:Any)->None:
    if isinstance(x,float): bad("float")
    if isinstance(x,dict):
        for k,v in x.items():
            if not isinstance(k,str): bad("key")
            nofloat(v)
    elif isinstance(x,list):
        for v in x: nofloat(v)
def canon(x:Any)->bytes:
    nofloat(x); return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def parse(b:bytes)->Any:
    if b.startswith(b"\xef\xbb\xbf") or b"\r" in b or b.endswith(b"\n"): bad("bytes")
    def pairs(xs):
        d={}
        for k,v in xs:
            if k in d: bad("dup")
            d[k]=v
        return d
    try: x=json.loads(b.decode(),object_pairs_hook=pairs,parse_float=lambda _:bad("float"))
    except Reject: raise
    except Exception as e: raise Reject("json") from e
    if canon(x)!=b: bad("noncanonical")
    return x
I=re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
def integer(s:Any)->int:
    if not isinstance(s,str) or not I.fullmatch(s) or s=="-0": bad("int")
    return int(s)
def D(m:int,e:int)->dict[str,Any]:
    if not isinstance(e,int) or isinstance(e,bool) or e<0: bad("e")
    if m==0: return {"m":"0","e":0}
    while e and m%2==0: m//=2; e-=1
    return {"m":str(m),"e":e}
def dval(x:Any)->Fraction:
    if not isinstance(x,dict) or set(x)!={"m","e"}: bad("dyadic")
    m,e=integer(x["m"]),x["e"]
    if not isinstance(e,int) or isinstance(e,bool) or e<0 or (m==0 and e) or (e and m%2==0): bad("dyadic")
    return Fraction(m,1<<e)
def Q(f:Fraction)->dict[str,str]: return {"p":str(f.numerator),"q":str(f.denominator)}
def qval(x:Any)->Fraction:
    if not isinstance(x,dict) or set(x)!={"p","q"}: bad("rational")
    p,q=integer(x["p"]),integer(x["q"])
    if q<=0 or math.gcd(abs(p),q)!=1: bad("rational")
    return Fraction(p,q)
def IV(a:tuple[int,int],b:tuple[int,int])->dict[str,Any]: return {"lo":D(*a),"hi":D(*b)}
def iv(x:Any)->tuple[Fraction,Fraction]:
    if not isinstance(x,dict) or set(x)!={"lo","hi"}: bad("interval")
    a,b=dval(x["lo"]),dval(x["hi"])
    if a>b: bad("interval")
    return a,b

def adapter(mm:int,me:int,rm:int,re_:int)->dict[str,Any]:
    if not all(isinstance(z,int) and not isinstance(z,bool) for z in (mm,me,rm,re_)) or min(me,re_,rm)<0: bad("adapter")
    e=max(me,re_); m=mm*(1<<(e-me)); r=rm*(1<<(e-re_))
    return {"lo":D(m-r,e),"hi":D(m+r,e)}

SCHEMA="BLOCAL_BENTRY_SELFTEST_V2_1"; DOMAIN=b"BLOCAL-COVERAGE-CHAIN-v1"
ASH="a"*64; SCSH="1"*64
STAGE1={"path":"CERTIFICATES/prolate/item2_branch/independent_recheck/certificate_item2_independent.json","source_head":"b0582728d3f8fd3508ba8574a898017212a28caa","certificate_sha256":"d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188","manifest_sha256":"f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069","config_sha256":SCSH,"certified_statement":"B(103/50)>0, B(207/100)<0, B(206538/100000)>0, B(206539/100000)<0, and B'(lambda)<0 on [206538/100000,206539/100000]. Hence lambda_partial is the unique root in (206538/100000,206539/100000).","machine_conclusion":{"lambda_partial":"(206538/100000,206539/100000)","strict_upper_bound":"206539/100000","unique_on_interval":True},"scope":"Boundary-entry parameter only. Item 2 proper, requiring the single sign change of F_r, remains open.","status":"STAGE1_CONTENT_AUDITED"}
PREM=["STAGE1_UNIQUE_BOUNDARY_ROOT_IN_OPEN_BRACKET","STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET","STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO","L1_EXTENDED_HU_STRICT_POSITIVITY","L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY","L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY","S_NEG_STRICTLY_EXCEEDS_STAGE1_BRACKET_WIDTH","H_CONTINUITY_FROM_FIXED_FORMULA"]
def lstart(k:int)->Fraction: return Fraction(206539,100000)+Fraction(1,1<<k)
def rcfg()->dict[str,Any]: return {"schema":SCHEMA,"design_version":"2.1","stage1_dependency":deepcopy(STAGE1),"stage1_archive_deterministic":True,"stage1_archive_created":False,"s_neg":D(1,16),"s_neg_comparison_method":"INTEGER_ONLY","section6_relation":"lambda_partial > lambda_plus - s_neg","bracket_width_proof":{"lhs":100000,"rhs":65536,"strict":True},"lambda_candidates":[D(1,k) for k in range(24,3,-1)],"u_max_candidates":[D(1,k) for k in (8,7,6,5,4)],"candidate_order":"LAMBDA_MAJOR_U_MAX_MINOR","adapter_id":"ARB_TO_CANONICAL_DYADIC_INTERVAL_V1","adapter_sha256":ASH,"adapter_rejects_nonfinite":True,"enclosure_source":"PINNED_ADAPTER_ONLY","display_is_nonnormative":True,"stage1_dependency_config_sha256":SCSH,"l4_premises":list(PREM),"mode":"SELFTEST_ONLY","dependency_status":"UNPINNED","binding_to_final_lambda_start":False,"coverage_claim":False,"recommendation":None,"terminal_state":"BLOCAL_INCOMPLETE","no_production_kernel":True,"no_workflow":True,"no_tag":True,"no_dependency_archive":True,"budgets":{"max_depth":8,"max_evaluations":1000,"max_tiles":100}}
def wrap(r:dict[str,Any])->dict[str,Any]:
    h=H(canon(r)); return {"run_config":r,"blocal_run_config_sha256":h,"chain_genesis":H(DOMAIN+b"\0"+bytes.fromhex(h))}
def chkcfg(c:Any)->dict[str,Any]:
    if not isinstance(c,dict) or set(c)!={"run_config","blocal_run_config_sha256","chain_genesis"}: bad("config")
    r=c["run_config"]; h=H(canon(r))
    if c["blocal_run_config_sha256"]!=h or c["chain_genesis"]!=H(DOMAIN+b"\0"+bytes.fromhex(h)): bad("hash")
    if r!=rcfg(): bad("contract")
    if r["stage1_dependency_config_sha256"]==h: bad("hash names")
    return r

def tile(node:str,ci:int,k:int,ue:int,ok=True)->dict[str,Any]:
    sd={"lo":D(-1,16),"hi":D(1,k)} if node in ("L1","L2") else {"lo":D(0,0),"hi":D(1,k)}
    ud={"lo":D(0,0),"hi":D(1,ue)} if node=="L1" else {"lo":D(1,ue),"hi":D(1,ue)} if node=="L2" else {"lo":D(0,0),"hi":D(0,0)}
    enc=IV((1,4),(1,3)) if node in ("L1","L2") else IV((-1,3),(-1,4)) if ok else IV((-1,3),(1,3))
    return {"record_type":"TILE","node":node,"candidate_index":ci,"u_domain":ud,"s_domain":sd,"enclosure":enc,"enclosure_source":"PINNED_ADAPTER_ONLY","display_normative":False,"coverage":{"gap":False,"overlap":False,"outside":False},"depth":1,"evaluations":1,"tiles":1,"unresolved":not ok,"failure_reason":None if ok else "STRICT_SIGN_UNRESOLVED","certified":ok}
def cs(ci:int,k:int,ue:int,ok:bool)->dict[str,Any]: return {"record_type":"CANDIDATE_SUMMARY","candidate_index":ci,"lambda_increment":D(1,k),"lambda_start":Q(lstart(k)),"u_max":D(1,ue),"node_status":{"L1":"CERTIFIED","L2":"CERTIFIED","L3":"CERTIFIED" if ok else "INCOMPLETE","J_START":"CERTIFIED" if ok else "NOT_ATTEMPTED"},"coverage_counts":{"L1":1,"L2":1,"L3":1},"budgets":{"depth":1,"evaluations":3,"tiles":3},"first_failure_reason":None if ok else "L3_STRICT_SIGN_UNRESOLVED","unresolved":not ok,"budget_exceeded":False,"candidate_accepted":ok}
def chain(rs:list[dict[str,Any]],c:dict[str,Any])->None:
    p=c["chain_genesis"]
    for r in rs:
        r["previous_record_sha256"]=p
        if r["record_type"]=="RUN_SUMMARY": r["records_chain_tip_sha256"]=p
        r["record_sha256"]=H(canon({k:v for k,v in r.items() if k!="record_sha256"})); p=r["record_sha256"]
def bundle()->tuple[dict[str,Any],list[dict[str,Any]]]:
    c=wrap(rcfg()); lam=Q(lstart(24)); ri=IV((3,2),(7,3)); r=c["run_config"]
    rs=[{"record_type":"RUN_HEADER","schema":SCHEMA,"design_version":"2.1","blocal_run_config_sha256":c["blocal_run_config_sha256"],"stage1_dependency":deepcopy(STAGE1),"arb_to_dyadic_adapter_sha256":ASH,"candidate_schedule":{"order":r["candidate_order"],"lambda_candidates":r["lambda_candidates"],"u_max_candidates":r["u_max_candidates"],"candidate_count":105},"precision":{"fixture_bits":256},"budgets":r["budgets"],"chain_domain":DOMAIN.decode(),"chain_genesis":c["chain_genesis"]},tile("L1",0,24,8),tile("L2",0,24,8),tile("L3",0,24,8,False),cs(0,24,8,False),tile("L1",1,24,7),tile("L2",1,24,7),tile("L3",1,24,7),{"record_type":"J_START","node":"J_START","selected_candidate_index":1,"lambda_start":lam,"r_interval":ri,"F_at_r_lo":IV((1,4),(1,3)),"F_at_r_hi":IV((-1,3),(-1,4)),"F_r_on_interval":IV((-1,2),(-1,3)),"claim":"J_START_UNIQUE_NONDEGENERATE_ROOT","interval_method":"INTERVAL_NEWTON_OR_KRAWCZYK_V1","strict_self_containment":True,"certified":True},cs(1,24,7,True),{"record_type":"RUN_SUMMARY","selected_candidate_index":1,"lambda_start":lam,"u_max":D(1,7),"j_start_interval":ri,"exact_counts":{"attempted_candidates":2,"tile_records":6,"j_start_records":1,"candidate_summaries":2},"budgets":r["budgets"],"dependency_identities":{"stage1_source_head":STAGE1["source_head"],"stage1_certificate_sha256":STAGE1["certificate_sha256"],"stage1_manifest_sha256":STAGE1["manifest_sha256"],"stage1_config_sha256":SCSH,"arb_to_dyadic_adapter_sha256":ASH},"records_chain_tip_sha256":"0"*64,"terminal_state":"BLOCAL_INCOMPLETE","coverage_claim":False,"recommendation":None,"selftest_fixture_accepted":True}]
    chain(rs,c); return c,rs
def enc(c,rs): return canon(c),b"\n".join(canon(r) for r in rs)
def lines(b):
    if not b or b.endswith(b"\n") or b"\r" in b: bad("jsonl")
    xs=[parse(x) for x in b.split(b"\n")]
    if not all(isinstance(x,dict) for x in xs): bad("record")
    return xs

def vtile(r,n,ci,k,ue,ok):
    e=tile(n,ci,k,ue,ok)
    for x in ("previous_record_sha256","record_sha256"): e.pop(x,None)
    for x in ("previous_record_sha256","record_sha256"): r=dict(r); r.pop(x,None)
    if r!=e: bad("tile")
def vcs(r,ci,k,ue,ok):
    e=cs(ci,k,ue,ok); a={k:v for k,v in r.items() if k not in ("previous_record_sha256","record_sha256")}
    if a!=e: bad("candidate")
def verify(cb:bytes,rb:bytes)->None:
    c=parse(cb); cfg=chkcfg(c); rs=lines(rb)
    if len(rs)!=11: bad("count")
    p=c["chain_genesis"]
    for r in rs:
        if r.get("previous_record_sha256")!=p: bad("previous")
        if r["record_type"]=="RUN_SUMMARY" and r.get("records_chain_tip_sha256")!=p: bad("tip")
        if r.get("record_sha256")!=H(canon({k:v for k,v in r.items() if k!="record_sha256"})): bad("record hash")
        p=r["record_sha256"]
    hdr={k:v for k,v in rs[0].items() if k not in ("previous_record_sha256","record_sha256")}
    exp={"record_type":"RUN_HEADER","schema":SCHEMA,"design_version":"2.1","blocal_run_config_sha256":c["blocal_run_config_sha256"],"stage1_dependency":STAGE1,"arb_to_dyadic_adapter_sha256":ASH,"candidate_schedule":{"order":cfg["candidate_order"],"lambda_candidates":cfg["lambda_candidates"],"u_max_candidates":cfg["u_max_candidates"],"candidate_count":105},"precision":{"fixture_bits":256},"budgets":cfg["budgets"],"chain_domain":DOMAIN.decode(),"chain_genesis":c["chain_genesis"]}
    if hdr!=exp: bad("header")
    vtile(rs[1],"L1",0,24,8,True); vtile(rs[2],"L2",0,24,8,True); vtile(rs[3],"L3",0,24,8,False); vcs(rs[4],0,24,8,False)
    vtile(rs[5],"L1",1,24,7,True); vtile(rs[6],"L2",1,24,7,True); vtile(rs[7],"L3",1,24,7,True)
    j={k:v for k,v in rs[8].items() if k not in ("previous_record_sha256","record_sha256")}
    if j.get("record_type")!="J_START" or j.get("node")!="J_START" or j.get("selected_candidate_index")!=1 or qval(j.get("lambda_start"))!=lstart(24): bad("j identity")
    a,b=iv(j.get("r_interval")); flo=iv(j.get("F_at_r_lo")); fhi=iv(j.get("F_at_r_hi")); fr=iv(j.get("F_r_on_interval"))
    if not (0<a<b<1 and flo[0]>0 and fhi[1]<0 and fr[1]<0 and j.get("strict_self_containment") is True and j.get("certified") is True and j.get("claim")=="J_START_UNIQUE_NONDEGENERATE_ROOT" and j.get("interval_method")=="INTERVAL_NEWTON_OR_KRAWCZYK_V1"): bad("j proof")
    vcs(rs[9],1,24,7,True)
    s=rs[10]
    if s.get("record_type")!="RUN_SUMMARY" or s.get("selected_candidate_index")!=1 or qval(s.get("lambda_start"))!=lstart(24) or dval(s.get("u_max"))!=Fraction(1,128) or s.get("j_start_interval")!=IV((3,2),(7,3)) or s.get("exact_counts")!={"attempted_candidates":2,"tile_records":6,"j_start_records":1,"candidate_summaries":2} or s.get("budgets")!=cfg["budgets"] or s.get("terminal_state")!="BLOCAL_INCOMPLETE" or s.get("coverage_claim") is not False or s.get("recommendation") is not None or s.get("selftest_fixture_accepted") is not True: bad("summary")
    dep={"stage1_source_head":STAGE1["source_head"],"stage1_certificate_sha256":STAGE1["certificate_sha256"],"stage1_manifest_sha256":STAGE1["manifest_sha256"],"stage1_config_sha256":SCSH,"arb_to_dyadic_adapter_sha256":ASH}
    if s.get("dependency_identities")!=dep: bad("dependencies")

def mutate(base,fn:Callable,which="r",rech=True):
    c=parse(base[0]); rs=lines(base[1]); fn(c if which=="c" else rs)
    if which=="c": c=wrap(c["run_config"])
    if rech: chain(rs,c)
    return enc(c,rs)
def controls(base):
    z={}; C=lambda n,s,b:z.__setitem__(f"{n:02d}_{s}",b)
    cm=[("stage1_source_head_tamper",lambda c:c["run_config"]["stage1_dependency"].__setitem__("source_head","f"*40)),("stage1_certificate_sha_tamper",lambda c:c["run_config"]["stage1_dependency"].__setitem__("certificate_sha256","f"*64)),("stage1_manifest_sha_tamper",lambda c:c["run_config"]["stage1_dependency"].__setitem__("manifest_sha256","e"*64)),("stage1_path_mismatch",lambda c:c["run_config"]["stage1_dependency"].__setitem__("path","wrong")),("stage1_status_not_certified",lambda c:c["run_config"]["stage1_dependency"].__setitem__("status","UNPINNED")),("stage1_statement_mismatch",lambda c:c["run_config"]["stage1_dependency"].__setitem__("certified_statement","bad")),("stage1_machine_conclusion_mismatch",lambda c:c["run_config"]["stage1_dependency"]["machine_conclusion"].__setitem__("unique_on_interval",False)),("stage1_scope_mismatch",lambda c:c["run_config"]["stage1_dependency"].__setitem__("scope","bad")),("stage1_content_audit_missing",lambda c:c["run_config"]["stage1_dependency"].__setitem__("status","CERTIFIED")),("dependency_archive_mutated",lambda c:c["run_config"].__setitem__("stage1_archive_deterministic",False))]
    for i,(s,f) in enumerate(cm,1): C(i,s,mutate(base,f,"c"))
    rm=[("display_fraction_without_object",lambda r:r[8].__setitem__("lambda_start","206539/100000")),("lambda_candidate_order_changed",None),("u_max_order_changed",None),("l1_domain_starts_zero",lambda r:r[1]["s_domain"].__setitem__("lo",D(0,0))),("l2_domain_starts_zero",lambda r:r[2]["s_domain"].__setitem__("lo",D(0,0))),("l1_l2_old_global_endpoint",lambda r:(r[5]["s_domain"].__setitem__("lo",D(0,0)),r[6]["s_domain"].__setitem__("lo",D(0,0)))),("s_neg_wrong",None),("s_neg_float_comparison",None),("section6_relation_reversed",None),("bracket_width_proof_missing",None),("l3_extended_negative",lambda r:r[7]["s_domain"].__setitem__("lo",D(-1,16))),("l4_missing_boundary_zero",None),("l4_missing_strict_decrease",None),("enclosure_freeform_string",lambda r:r[5].__setitem__("enclosure","[0.1,0.2]")),("adapter_pin_mismatch",None),("noncanonical_dyadic",lambda r:r[5]["enclosure"]["lo"].update({"m":"2","e":5})),("adapter_accepts_nonfinite",None),("display_enclosure_normative",lambda r:r[5].__setitem__("display_normative",True))]
    cfgfix={12:lambda c:c["run_config"]["lambda_candidates"].reverse(),13:lambda c:c["run_config"]["u_max_candidates"].reverse(),17:lambda c:c["run_config"].__setitem__("s_neg",D(1,15)),18:lambda c:c["run_config"].__setitem__("s_neg_comparison_method","FLOAT"),19:lambda c:c["run_config"].__setitem__("section6_relation","lambda_partial < lambda_plus - s_neg"),20:lambda c:c["run_config"].__setitem__("bracket_width_proof",{"strict":False}),22:lambda c:c["run_config"]["l4_premises"].remove("STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO"),23:lambda c:c["run_config"]["l4_premises"].remove("STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET"),25:lambda c:c["run_config"].__setitem__("adapter_sha256","b"*64),27:lambda c:c["run_config"].__setitem__("adapter_rejects_nonfinite",False)}
    for n,(s,f) in enumerate(rm,11): C(n,s,mutate(base,cfgfix[n],"c") if n in cfgfix else mutate(base,f))
    c=parse(base[0]); r=lines(base[1]); c["chain_genesis"]=H(DOMAIN+b"\0"+bytes.fromhex(SCSH)); chain(r,c); C(29,"genesis_uses_stage1_hash",enc(c,r))
    C(30,"config_hash_names_conflated",mutate(base,lambda c:c["run_config"].__setitem__("stage1_dependency_config_sha256",c["blocal_run_config_sha256"]),"c"))
    C(31,"record_order_changed",mutate(base,lambda r:r.__setitem__(slice(8,10),[r[9],r[8]])))
    C(32,"previous_hash_tamper",mutate(base,lambda r:r[5].__setitem__("previous_record_sha256","f"*64),rech=False))
    C(33,"jsonl_crlf",(base[0],base[1].replace(b"\n",b"\r\n",1)))
    C(34,"duplicate_key_or_float",(b'{"blocal_run_config_sha256":"x","blocal_run_config_sha256":"y","run_config":1.5,"chain_genesis":"z"}',base[1]))
    tail=[("coverage_gap",lambda r:r[5]["coverage"].__setitem__("gap",True)),("coverage_overlap",lambda r:r[5]["coverage"].__setitem__("overlap",True)),("tile_outside_rectangle",lambda r:r[5]["u_domain"].__setitem__("hi",D(1,3))),("unresolved_leaf_promoted",lambda r:r[5].__setitem__("unresolved",True)),("budget_exceeded_success",lambda r:r[5].__setitem__("evaluations",1001)),("jstart_missing",lambda r:r.pop(8)),("jstart_duplicated",lambda r:r.insert(9,deepcopy(r[8]))),("jstart_misplaced",lambda r:r.insert(5,r.pop(8))),("jstart_self_containment_missing",lambda r:r[8].__setitem__("strict_self_containment",False)),("invalid_mode_state",None),("incomplete_promoted",lambda r:(r[10].__setitem__("terminal_state","BLOCAL_CERTIFIED"),r[10].__setitem__("coverage_claim",True))),("jstart_lambda_mismatch",lambda r:r[8].__setitem__("lambda_start",Q(Fraction(206539,100000))))]
    for n,(s,f) in enumerate(tail,35):
        if n==44: C(n,s,mutate(base,lambda c:(c["run_config"].__setitem__("mode","BINDING"),c["run_config"].__setitem__("binding_to_final_lambda_start",True)),"c"))
        else: C(n,s,mutate(base,f))
    return z

def main():
    for x in [(0,0,0,0),(5,0,0,0),(-5,0,0,0),(3,2,0,0),(-3,2,0,0),(3,4,1,6),(7,3,1,3),(-7,3,1,3),(0,0,1,8),(2**200+1,17,2**120+1,91)]: iv(adapter(*x))
    try: adapter(0,0,-1,0); bad("adapter negative radius accepted")
    except Reject: pass
    c,r=bundle(); base=enc(c,r); verify(*base); cs=controls(base)
    if len(cs)!=46: bad("control count")
    for n,b in cs.items():
        try: verify(*b)
        except Reject: continue
        bad("accepted "+n)
    print("POSITIVE 1/1 PASS\nADAPTER_AUDIT 10/10 PASS\nNEGATIVE 46/46 PASS\nSELFTEST_ONLY PASS — no production kernel, workflow, tag, or archive")
if __name__=="__main__": main()
