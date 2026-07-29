#!/usr/bin/env python3
"""B-LOCAL/B-ENTRY Phase-3 implementation candidate.

Status: CHAT_SIDE_AUDIT_WAITING. Calculation-free only: no production kernel,
archive creation, tag, workflow, or mathematical run.
"""
from __future__ import annotations
import argparse, json, subprocess, tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any
from numeric_schema import (CanonicalBytesError,D_ZERO,Dyadic,DyadicInterval,
 Rational,SchemaError,arb_ball_to_exact_interval,canonical_json_bytes,
 parse_canonical_json_bytes,parse_canonical_jsonl,sha256_hex)

ERR=RuntimeError
DV="2.1"; CFG="blocal-run-config-v1"; CERT="blocal-certificate-v1"
CHAIN="BLOCAL-COVERAGE-CHAIN-v1"; CANON="BTUBE_NUMERIC_SCHEMA_CANONICAL_JSON_V1"
ADAPTER="ARB_TO_CANONICAL_DYADIC_INTERVAL_V1"; LP=Fraction(206539,100000)
LM=Fraction(206538,100000); SN=Dyadic(1,16); RANGE="(lambda_partial,lambda_start]"
STATEMENT=("B(103/50)>0, B(207/100)<0, B(206538/100000)>0, "
 "B(206539/100000)<0, and B'(lambda)<0 on [206538/100000,206539/100000]. "
 "Hence lambda_partial is the unique root in (206538/100000,206539/100000).")
MC={"lambda_partial":"(206538/100000,206539/100000)",
 "strict_upper_bound":"206539/100000","unique_on_interval":True}
SCOPE=("Boundary-entry parameter only. Item 2 proper, requiring the single sign "
 "change of F_r, remains open.")

def need(x,msg):
    if not x: raise ERR(msg)
def keys(x,k,w): need(isinstance(x,dict) and set(x)==k,f"{w}: exact keys")
def cbytes(x): return canonical_json_bytes(x) # sole pin canonicalizer, ensure_ascii=True
def d(m,e): return Dyadic.canonical(m,e).to_json()
def q(x): return Rational.from_fraction(x).to_json()
def iv(a,b): return DyadicInterval(Dyadic.canonical(*a),Dyadic.canonical(*b)).to_json()
def df(x,w="dyadic"): return Dyadic.from_json(x,w).as_fraction()
def qf(x,w="rational"): return Rational.from_json(x,w).as_fraction()
def inf(x,w="interval"):
    z=DyadicInterval.from_json(x,w); return z.lo.as_fraction(),z.hi.as_fraction()
def canonicalizer_test():
    need(cbytes({"scope":"α"})==b'{"scope":"\\u03b1"}',"canonicalizer policy")
def adapter(ball): return arb_ball_to_exact_interval(ball)
def adapter_source_sha(path=None):
    p=Path(__file__) if path is None else Path(path); need(not p.is_symlink(),"adapter symlink")
    p=p.resolve(strict=True); need(p.is_file(),"adapter regular file"); return sha256_hex(p.read_bytes())
def sneg_proof():
    need(100000>(1<<16),"integer s_neg proof"); need(SN.as_fraction()>LP-LM,"fraction s_neg proof")
    return {"lhs":100000,"rhs":65536,"strict":True}
def pointer(x,p):
    need(p.startswith("/"),"JSON pointer")
    for t in p[1:].split("/"):
        t=t.replace("~1","/").replace("~0","~"); need(isinstance(x,dict) and t in x,"pointer component"); x=x[t]
    return x
def machine_conclusion(raw):
    x=parse_canonical_json_bytes(raw,allow_display=False); y=pointer(x,"/machine_conclusion")
    need(isinstance(y,dict),"machine conclusion object"); return y,cbytes(y)

def sums(raw,where):
    need(b"\r" not in raw,f"{where}: CR"); out={}
    for n,line in enumerate(raw.decode().splitlines(),1):
        if not line: continue
        p=line.split(maxsplit=1); need(len(p)==2,f"{where}:{n}"); h,name=p[0],p[1].lstrip(" *")
        need(len(h)==64 and all(c in "0123456789abcdef" for c in h),f"{where}: hash")
        need(name and name not in out and not name.startswith("/") and ".." not in Path(name).parts,f"{where}: path")
        out[name]=h
    need(out,f"{where}: empty"); return out
def repo_file(root,rel):
    need(isinstance(rel,str) and rel and not rel.startswith("/"),"repo path")
    p=Path(root)/rel; need(not p.is_symlink(),f"symlink {rel}"); rr=Path(root).resolve(strict=True); p=p.resolve(strict=True)
    try: p.relative_to(rr)
    except ValueError as e: raise ERR(f"escape {rel}") from e
    need(p.is_file(),f"file {rel}"); return p

def audit_stage1(plan):
    req={"repository_root","certificate_path","inner_manifest_path","outer_manifest_path",
     "implementation_path","source_head","certificate_sha256","inner_manifest_sha256",
     "outer_manifest_sha256","implementation_sha256"}; keys(plan,req,"plan")
    root=Path(plan["repository_root"]); actual=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip(); need(actual==plan["source_head"],"01 source head mismatch"); cp=repo_file(root,plan["certificate_path"])
    ip=repo_file(root,plan["inner_manifest_path"]); op=repo_file(root,plan["outer_manifest_path"])
    xp=repo_file(root,plan["implementation_path"]); cr,ir,orr,xr=cp.read_bytes(),ip.read_bytes(),op.read_bytes(),xp.read_bytes(); done=[]
    need(len(plan["source_head"])==40 and all(c in "0123456789abcdef" for c in plan["source_head"]),"01 source head format"); done.append(1)
    need(sha256_hex(cr)==plan["certificate_sha256"],"02 cert hash"); done.append(2)
    need(sha256_hex(ir)==plan["inner_manifest_sha256"],"03 inner hash"); done.append(3)
    need(sha256_hex(orr)==plan["outer_manifest_sha256"],"04 outer hash"); done.append(4)
    cert=parse_canonical_json_bytes(cr,allow_display=False); need(cert.get("status")=="CERTIFIED","05 status"); done.append(5)
    need(cert.get("certified_statement")==STATEMENT,"06 statement"); done.append(6)
    mc,mcb=machine_conclusion(cr); need(mc==MC and mcb==cbytes(MC),"07 conclusion"); done.append(7)
    need(cert.get("scope")==SCOPE,"08 scope"); done.append(8)
    br=cert.get("lambda_partial_bracket"); need(isinstance(br,dict) and set(br)=={"lo","hi"},"09 bracket")
    need(qf(br["lo"])==LM and qf(br["hi"])==LP and mc["unique_on_interval"] is True and mc["strict_upper_bound"]=="206539/100000","09 bracket"); done.append(9)
    need(sha256_hex(xr)==plan["implementation_sha256"],"10 implementation hash")
    need(cert.get("implementation_sha256") in (None,plan["implementation_sha256"]),"10 certificate implementation pin"); done.append(10)
    need(b"UNVERIFIED_PROVENANCE" not in cr+ir+orr+xr,"11 provenance dependency"); done.append(11)
    inn,outer=sums(ir,"inner"),sums(orr,"outer")
    for rel,h in inn.items(): need(sha256_hex(repo_file(root,rel).read_bytes())==h,f"12 payload {rel}")
    need(inn.get(plan["certificate_path"])==plan["certificate_sha256"],"12 cert inner")
    need(inn.get(plan["implementation_path"])==plan["implementation_sha256"],"12 impl inner")
    need(outer.get(plan["inner_manifest_path"])==plan["inner_manifest_sha256"],"12 inner outer")
    need(outer.get(plan["certificate_path"])==plan["certificate_sha256"],"12 cert outer"); done.append(12)
    return {"checks":done,"count":12,"state":"STAGE1_CONTENT_AUDIT_CANDIDATE"}

def interval_cover(xs,lo,hi,w):
    for a,b in xs: need(lo<=a<b<=hi,f"{w}: outside")
    ep=sorted({lo,hi,*[z for x in xs for z in x]})
    for a,b in zip(ep,ep[1:]): need(sum(x<=a and b<=y for x,y in xs)==1,f"{w}: gap/overlap")
def rect_cover(xs,ulo,uhi,slo,shi,w):
    for a,b,c,e in xs: need(ulo<=a<b<=uhi and slo<=c<e<=shi,f"{w}: outside")
    us=sorted({ulo,uhi,*[z for a,b,_,_ in xs for z in (a,b)]}); ss=sorted({slo,shi,*[z for _,_,c,e in xs for z in (c,e)]})
    for a,b in zip(us,us[1:]):
        for c,e in zip(ss,ss[1:]): need(sum(x<=a and b<=y and z<=c and e<=t for x,y,z,t in xs)==1,f"{w}: gap/overlap")
def sign(node,x,ok):
    z=DyadicInterval.from_json(x); return ok and ((D_ZERO<z.lo) if node in ("L1","L2") else (z.hi<D_ZERO))
def rhash(r): return sha256_hex(cbytes({k:v for k,v in r.items() if k!="record_sha256"}))
def genesis(h): return sha256_hex(CHAIN.encode()+b"\0"+bytes.fromhex(h))
def schedule(cfg):
    ls=[Dyadic.from_json(x) for x in cfg["lambda_candidates"]]; us=[Dyadic.from_json(x) for x in cfg["u_max_candidates"]]
    need(ls==[Dyadic(1,k) for k in range(24,3,-1)],"lambda schedule"); need(us==[Dyadic(1,k) for k in (8,7,6,5,4)],"u schedule")
    return [(l,u) for l in ls for u in us]
def tiles(rs,cur,ci,node,u,s,sn,bud):
    a=[]
    while cur<len(rs) and rs[cur].get("record_type")=="TILE" and rs[cur].get("node")==node:
        r=rs[cur]; need(r.get("candidate_index")==ci,f"{node}: index"); need(r.get("depth",0)<=bud["max_depth"] and r.get("evaluations",0)<=bud["max_evaluations"],f"{node}: budget"); a.append(r); cur+=1
    need(a and len(a)<=bud["max_tiles"],f"{node}: count"); ok=all(sign(node,r["enclosure"],r.get("certified") is True) for r in a)
    if node=="L1": rect_cover([(*inf(r["u_interval"]),*inf(r["s_interval"])) for r in a],Fraction(0),u,-sn,s,"L1")
    else:
        interval_cover([inf(r["s_interval"]) for r in a],-sn if node=="L2" else Fraction(0),s,node)
        face=u if node=="L2" else Fraction(0)
        for r in a: need(df(r["u_face"])==face,f"{node}: face")
    return cur,ok,len(a)
def jstart(r,ci,lam):
    req={"record_type","node","selected_candidate_index","lambda_start","r_interval","F_at_r_lo","F_at_r_hi","F_r_on_interval","claim","interval_method","strict_self_containment","certified","previous_record_sha256","record_sha256"}; keys(r,req,"J_START")
    need(r["record_type"]==r["node"]=="J_START" and r["selected_candidate_index"]==ci and qf(r["lambda_start"])==lam,"J_START identity")
    a,b=inf(r["r_interval"]); x=DyadicInterval.from_json(r["F_at_r_lo"]); y=DyadicInterval.from_json(r["F_at_r_hi"]); z=DyadicInterval.from_json(r["F_r_on_interval"])
    need(0<a<b<1 and D_ZERO<x.lo and y.hi<D_ZERO and z.hi<D_ZERO,"J_START signs")
    need(r["claim"]=="J_START_UNIQUE_NONDEGENERATE_ROOT" and r["interval_method"]=="INTERVAL_NEWTON_OR_KRAWCZYK_V1" and r["strict_self_containment"] is True and r["certified"] is True,"J_START proof")
    return r["r_interval"]
def verify_run(cb,rb,certb=None):
    cfg=parse_canonical_json_bytes(cb,allow_display=False); req={"schema","design_version","lambda_plus","s_neg","lambda_candidates","u_max_candidates","budgets","canonicalizer_id","adapter_id","adapter_source_sha256","terminal_state_before_run"}; keys(cfg,req,"config")
    need(cfg["schema"]==CFG and cfg["design_version"]==DV and cfg["canonicalizer_id"]==CANON and cfg["adapter_id"]==ADAPTER and cfg["terminal_state_before_run"]=="BLOCAL_INCOMPLETE","config identity")
    need(qf(cfg["lambda_plus"])==LP and Dyadic.from_json(cfg["s_neg"])==SN,"config endpoints"); sneg_proof(); bud=cfg["budgets"]; keys(bud,{"max_depth","max_evaluations","max_tiles"},"budgets")
    for v in bud.values(): need(isinstance(v,int) and not isinstance(v,bool) and v>0,"budget")
    sch=schedule(cfg); parsed=parse_canonical_jsonl(rb); rs=[x for x,_ in parsed]; need(rs,"records"); h=sha256_hex(cb); prev=genesis(h)
    for r in rs: need(r.get("previous_record_sha256")==prev and r.get("record_sha256")==rhash(r),"chain"); prev=r["record_sha256"]
    hd=rs[0]; need(hd.get("record_type")=="RUN_HEADER" and hd.get("blocal_run_config_sha256")==h and hd.get("chain_genesis")==genesis(h) and hd.get("canonicalizer_id")==CANON and hd.get("adapter_source_sha256")==cfg["adapter_source_sha256"],"header")
    cur=1; total=0; selected=None
    for ci,(inc,um) in enumerate(sch):
        s,u=inc.as_fraction(),um.as_fraction(); lam=LP+s
        cur,a,n1=tiles(rs,cur,ci,"L1",u,s,SN.as_fraction(),bud); total+=n1
        cur,b,n2=tiles(rs,cur,ci,"L2",u,s,SN.as_fraction(),bud); total+=n2
        cur,c,n3=tiles(rs,cur,ci,"L3",u,s,SN.as_fraction(),bud); total+=n3; good=a and b and c; ji=None
        if cur<len(rs) and rs[cur].get("record_type")=="J_START": need(good,"J_START failed candidate"); ji=jstart(rs[cur],ci,lam); cur+=1
        need(cur<len(rs) and rs[cur].get("record_type")=="CANDIDATE_SUMMARY","candidate summary"); x=rs[cur]; cur+=1
        need(x.get("candidate_index")==ci and qf(x.get("lambda_start"))==lam and df(x.get("u_max"))==u,"candidate summary identity")
        need(x.get("coverage_counts")=={"L1":n1,"L2":n2,"L3":n3},"coverage counts")
        accepted=x.get("candidate_accepted") is True; need(accepted==(good and ji is not None),"acceptance")
        if accepted: selected=(ci,lam,u,ji,ci+1); break
        need(x.get("first_failure_reason") not in (None,""),"failure reason")
    need(selected is not None,"no selected candidate"); ci,lam,u,ji,attempted=selected
    need(cur<len(rs) and rs[cur].get("record_type")=="RUN_SUMMARY","run summary"); x=rs[cur]; cur+=1; need(cur==len(rs),"record after summary")
    need(x.get("selected_candidate_index")==ci and qf(x.get("lambda_start"))==lam and df(x.get("u_max"))==u and x.get("j_start_interval")==ji,"summary identity")
    need(x.get("exact_counts")=={"attempted_candidates":attempted,"tile_records":total,"j_start_records":1,"candidate_summaries":attempted} and x.get("records_chain_tip_sha256")==x.get("previous_record_sha256") and x.get("terminal_state")=="BLOCAL_CERTIFIED","summary contract")
    if certb:
        cert=parse_canonical_json_bytes(certb,allow_display=False); need(cert.get("schema")==CERT,"certificate schema"); mc,mcb=machine_conclusion(certb)
        exp={"binding_to_final_lambda_start":True,"coverage_claim":True,"lambda_start":q(lam),"real_analytic":False,"state":"BLOCAL_CERTIFIED","unique_non_degenerate_root_for_every_lambda_in":RANGE}; need(mc==exp and mcb==cbytes(exp),"certificate conclusion")
    return {"attempted_candidates":attempted,"selected_candidate_index":ci,"tile_records":total,"state":"BLOCAL_VERIFICATION_CANDIDATE"}

DESIGN_CODES=["STAGE1_SOURCE_HEAD","STAGE1_CERT_SHA","STAGE1_MANIFEST_SHA","STAGE1_PATH","STAGE1_STATUS","STAGE1_STATEMENT","STAGE1_CONCLUSION","STAGE1_SCOPE","STAGE1_CONTENT_AUDIT","DEPENDENCY_ARCHIVE","EXACT_RATIONAL","LAMBDA_ORDER","UMAX_ORDER","L1_NEGATIVE_STRIP","L2_NEGATIVE_STRIP","L1L2_GLOBAL_ENDPOINT","SNEG_VALUE","SNEG_INTEGER_PROOF","SECTION6_DIRECTION","BRACKET_WIDTH_PROOF","L3_NONNEGATIVE","L4_BOUNDARY_ZERO","L4_STRICT_DECREASE","ENCLOSURE_OBJECT","ADAPTER_PIN","DYADIC_CANONICAL","ADAPTER_NONFINITE","DISPLAY_NONNORMATIVE","GENESIS_CONFIG_HASH","CONFIG_HASH_NAMES","RECORD_ORDER","PREVIOUS_HASH","JSONL_BYTES","JSON_CANONICAL","COVERAGE_GAP","COVERAGE_OVERLAP","DOMAIN_OUTSIDE","UNRESOLVED","BUDGET","JSTART_MISSING","JSTART_DUPLICATE","JSTART_POSITION","JSTART_PROOF","MODE_STATE","INCOMPLETE_PROMOTION"]
SELFTEST=["stage1_source_head_tamper","stage1_certificate_sha_tamper","stage1_manifest_sha_tamper","stage1_path_mismatch","stage1_status_not_certified","stage1_statement_mismatch","stage1_machine_conclusion_mismatch","stage1_scope_mismatch","stage1_content_audit_missing","dependency_archive_mutated","display_fraction_without_object","lambda_candidate_order_changed","u_max_order_changed","l1_domain_starts_zero","l2_domain_starts_zero","l1_l2_old_global_endpoint","s_neg_wrong","s_neg_float_comparison","section6_relation_reversed","bracket_width_proof_missing","l3_extended_negative","l4_missing_boundary_zero","l4_missing_strict_decrease","enclosure_freeform_string","adapter_pin_mismatch","noncanonical_dyadic","adapter_accepts_nonfinite","display_enclosure_normative","genesis_uses_stage1_hash","config_hash_names_conflated","record_order_changed","previous_hash_tamper","jsonl_crlf","duplicate_key_or_float","coverage_gap","coverage_overlap","tile_outside_rectangle","unresolved_leaf_promoted","budget_exceeded_success","jstart_missing","jstart_duplicated","jstart_misplaced","jstart_self_containment_missing","invalid_mode_state","incomplete_promoted"]
CONTROL_MAP=tuple({"design_id":i,"design_code":a,"selftest_control":b} for i,(a,b) in enumerate(zip(DESIGN_CODES,SELFTEST),1)); EXTRA={"selftest_id":46,"selftest_control":"jstart_lambda_mismatch","relationship":"D3 extra equality control"}
def mapping_test(source=None):
    need(len(CONTROL_MAP)==45 and [x["design_id"] for x in CONTROL_MAP]==list(range(1,46)) and len(set(SELFTEST))==45 and EXTRA["selftest_control"] not in SELFTEST,"control map")
    if source:
        t=source.decode()
        for n in [*SELFTEST,EXTRA["selftest_control"]]: need(n in t,f"control absent {n}")

class ME:
    def __init__(self,m,e): self.x=(m,e)
    def man_exp(self): return self.x
class Ball:
    def __init__(self,mm,me,rm,re): self.a=ME(mm,me); self.b=ME(rm,re)
    def mid(self): return self.a
    def rad(self): return self.b
def add(rs,p,x): x=dict(x,previous_record_sha256=p); x["record_sha256"]=rhash(x); rs.append(x); return x["record_sha256"]
def fixture():
    cfg={"schema":CFG,"design_version":DV,"lambda_plus":q(LP),"s_neg":SN.to_json(),"lambda_candidates":[d(1,k) for k in range(24,3,-1)],"u_max_candidates":[d(1,k) for k in (8,7,6,5,4)],"budgets":{"max_depth":8,"max_evaluations":1000,"max_tiles":100},"canonicalizer_id":CANON,"adapter_id":ADAPTER,"adapter_source_sha256":"a"*64,"terminal_state_before_run":"BLOCAL_INCOMPLETE"}; cb=cbytes(cfg); p=genesis(sha256_hex(cb)); rs=[]
    p=add(rs,p,{"record_type":"RUN_HEADER","blocal_run_config_sha256":sha256_hex(cb),"chain_genesis":genesis(sha256_hex(cb)),"canonicalizer_id":CANON,"adapter_source_sha256":"a"*64}); pos=iv((1,4),(1,3)); neg=iv((-1,3),(-1,4)); unk=iv((-1,4),(1,4))
    for ci,ue,rejected in ((0,8,True),(1,7,False)):
        zero=d(0,0); um=d(1,ue+1); uh=d(1,ue); sl=d(-1,16); sm=zero; sh=d(1,24)
        for ua,ub,sa,sb in ((zero,um,sl,sm),(um,uh,sl,sm),(zero,um,sm,sh),(um,uh,sm,sh)): p=add(rs,p,{"record_type":"TILE","node":"L1","candidate_index":ci,"u_interval":{"lo":ua,"hi":ub},"s_interval":{"lo":sa,"hi":sb},"enclosure":pos,"certified":True,"depth":2,"evaluations":3})
        for sa,sb in ((sl,sm),(sm,sh)): p=add(rs,p,{"record_type":"TILE","node":"L2","candidate_index":ci,"u_face":uh,"s_interval":{"lo":sa,"hi":sb},"enclosure":pos,"certified":True,"depth":2,"evaluations":3})
        half=d(1,25); p=add(rs,p,{"record_type":"TILE","node":"L3","candidate_index":ci,"u_face":zero,"s_interval":{"lo":sm,"hi":half},"enclosure":neg,"certified":True,"depth":2,"evaluations":3}); p=add(rs,p,{"record_type":"TILE","node":"L3","candidate_index":ci,"u_face":zero,"s_interval":{"lo":half,"hi":sh},"enclosure":unk if rejected else neg,"certified":not rejected,"depth":2,"evaluations":3}); lam=LP+Fraction(1,1<<24)
        if not rejected: p=add(rs,p,{"record_type":"J_START","node":"J_START","selected_candidate_index":ci,"lambda_start":q(lam),"r_interval":iv((3,2),(7,3)),"F_at_r_lo":pos,"F_at_r_hi":neg,"F_r_on_interval":iv((-1,2),(-1,3)),"claim":"J_START_UNIQUE_NONDEGENERATE_ROOT","interval_method":"INTERVAL_NEWTON_OR_KRAWCZYK_V1","strict_self_containment":True,"certified":True})
        p=add(rs,p,{"record_type":"CANDIDATE_SUMMARY","candidate_index":ci,"lambda_start":q(lam),"u_max":uh,"coverage_counts":{"L1":4,"L2":2,"L3":2},"candidate_accepted":not rejected,"first_failure_reason":"L3_STRICT_SIGN_UNRESOLVED" if rejected else None})
    p=add(rs,p,{"record_type":"RUN_SUMMARY","selected_candidate_index":1,"lambda_start":q(LP+Fraction(1,1<<24)),"u_max":d(1,7),"j_start_interval":iv((3,2),(7,3)),"exact_counts":{"attempted_candidates":2,"tile_records":16,"j_start_records":1,"candidate_summaries":2},"records_chain_tip_sha256":p,"terminal_state":"BLOCAL_CERTIFIED"}); rb=b"\n".join(cbytes(x) for x in rs); mc={"binding_to_final_lambda_start":True,"coverage_claim":True,"lambda_start":q(LP+Fraction(1,1<<24)),"real_analytic":False,"state":"BLOCAL_CERTIFIED","unique_non_degenerate_root_for_every_lambda_in":RANGE}; return cb,rb,cbytes({"schema":CERT,"machine_conclusion":mc})
def stage1_fixture():
    with tempfile.TemporaryDirectory() as td:
        r=Path(td); (r/"i").mkdir(); impl=b"# independent implementation\n"; (r/"i/x.py").write_bytes(impl); cert={"status":"CERTIFIED","certified_statement":STATEMENT,"machine_conclusion":MC,"scope":SCOPE,"lambda_partial_bracket":{"lo":q(LM),"hi":q(LP)},"implementation_sha256":sha256_hex(impl)}; cr=cbytes(cert); (r/"i/c.json").write_bytes(cr); ir=f"{sha256_hex(cr)}  i/c.json\n{sha256_hex(impl)}  i/x.py\n".encode(); (r/"i/SHA256SUMS.txt").write_bytes(ir); oraw=f"{sha256_hex(cr)}  i/c.json\n{sha256_hex(ir)}  i/SHA256SUMS.txt\n".encode(); (r/"SHA256SUMS.txt").write_bytes(oraw); subprocess.run(["git","init","-q",str(r)],check=True); subprocess.run(["git","-C",str(r),"config","user.email","fixture@example.invalid"],check=True); subprocess.run(["git","-C",str(r),"config","user.name","fixture"],check=True); subprocess.run(["git","-C",str(r),"add","."],check=True); subprocess.run(["git","-C",str(r),"commit","-q","-m","fixture"],check=True); head=subprocess.run(["git","-C",str(r),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip(); plan={"repository_root":str(r),"certificate_path":"i/c.json","inner_manifest_path":"i/SHA256SUMS.txt","outer_manifest_path":"SHA256SUMS.txt","implementation_path":"i/x.py","source_head":head,"certificate_sha256":sha256_hex(cr),"inner_manifest_sha256":sha256_hex(ir),"outer_manifest_sha256":sha256_hex(oraw),"implementation_sha256":sha256_hex(impl)}; need(audit_stage1(plan)["count"]==12,"stage1 fixture")
def selftest():
    canonicalizer_test(); margin=sneg_proof(); sp=Path(__file__).with_name("blocal_bentry_selftest.py"); mapping_test(sp.read_bytes() if sp.exists() else None)
    cases=[(0,0,0,0),(5,0,0,0),(-5,0,0,0),(3,-2,0,0),(-3,-2,0,0),(3,-4,1,-6),(7,-3,1,-3),(-7,-3,1,-3),(0,0,1,-8),(2**200+1,-17,2**120+1,-91)]
    for x in cases: adapter(Ball(*x))
    cb,rb,cert=fixture(); out=verify_run(cb,rb,cert); rs=[x for x,_ in parse_canonical_jsonl(rb)]; del rs[2]; p=genesis(sha256_hex(cb))
    for x in rs: x.pop("previous_record_sha256",None); x.pop("record_sha256",None); x["previous_record_sha256"]=p; x["record_sha256"]=rhash(x); p=x["record_sha256"]
    try: verify_run(cb,b"\n".join(cbytes(x) for x in rs),cert)
    except RuntimeError: pass
    else: raise RuntimeError("missing tile accepted")
    stage1_fixture(); return {"adapter_cases":10,"control_map":45,"extra_control":46,"margin":margin,"run_fixture":out,"stage1_checks":12,"status":"CHAT_SIDE_AUDIT_WAITING"}
def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True); s.add_parser("selftest"); v=s.add_parser("verify-run"); v.add_argument("--config",type=Path,required=True); v.add_argument("--records",type=Path,required=True); v.add_argument("--certificate",type=Path); a=s.add_parser("audit-stage1"); a.add_argument("--plan",type=Path,required=True); s.add_parser("control-map"); z=p.parse_args()
    if z.cmd=="selftest": out=selftest()
    elif z.cmd=="verify-run": out=verify_run(z.config.read_bytes(),z.records.read_bytes(),z.certificate.read_bytes() if z.certificate else None); out["status"]="CHAT_SIDE_AUDIT_WAITING"
    elif z.cmd=="audit-stage1": out=audit_stage1(parse_canonical_json_bytes(z.plan.read_bytes(),allow_display=False)); out["status"]="CHAT_SIDE_AUDIT_WAITING"
    else: out={"mapping":CONTROL_MAP,"extension":EXTRA,"status":"CHAT_SIDE_AUDIT_WAITING"}
    print(cbytes(out).decode("ascii"))
if __name__=="__main__":
    try: main()
    except (RuntimeError,CanonicalBytesError,SchemaError,OSError,KeyError,ValueError,json.JSONDecodeError) as e: print(f"BLOCAL ERROR: {e}"); raise SystemExit(2)
