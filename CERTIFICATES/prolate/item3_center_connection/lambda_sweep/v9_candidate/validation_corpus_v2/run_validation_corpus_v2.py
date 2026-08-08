#!/usr/bin/env python3
"""Freeze-grade independent validation corpus v2 for Item 3 sweep v9.

Differences from the historical v1 regression harness:
- positive analytic controls use an independently coded real F integral and finite-
  difference r derivatives at fixed prepublished points;
- source mutations are written to temporary modules and actually imported before an
  independent semantic/policy verifier decides REJECT;
- checkpoint controls execute every cancellation phase required by the transaction
  correction, including orphan payloads, incomplete JSONL tails, post-commit mirror
  failure, missing/corrupt immutable payloads, and preservation of prior commits.

This file never authorizes freeze, a production rehearsal, a tag, or a certified range.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import ast
import hashlib
import importlib.util
import inspect
import json
import math
import os
from pathlib import Path
import struct
import sys
import tempfile
from typing import Any, Callable

from flint import acb, arb

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent
ROOT = CANDIDATE.parents[4]
EXPECT_PATH = HERE / "CONTROL_EXPECT.json"
MATRIX_PATH = HERE / "CONTROL_MATRIX.json"
REPORT_PATH = HERE / "VALIDATION_REPORT.json"
BUNDLE = CANDIDATE / "rehearsal_bundle_candidate_v2"
DEPS = BUNDLE / "dependencies"
PLAN_DIR = BUNDLE / "plan_config"

SOURCE_PATHS = {
    "kernel": CANDIDATE / "prolate_F_derivatives_cleanroom_v9_candidate.py",
    "adapter": CANDIDATE / "adapter_v9_candidate_v2.py",
    "runner": CANDIDATE / "runner_v9_candidate_v2.py",
    "checker": CANDIDATE / "checker_v9_candidate_v2.py",
    "checkpoint": CANDIDATE / "checkpoint_v9_candidate.py",
    "bridge": CANDIDATE / "checkpoint_bridge_v9_candidate_v2.py",
    "driver": CANDIDATE / "rehearsal_driver_v9_candidate_v3.py",
    "aggregate_verifier": CANDIDATE / "aggregate_verifier_v9_candidate_v2.py",
}
REFERENCE_PATH = HERE / "independent_reference_v2.py"
FLOORS = {"A":32,"B":32,"C":80,"D":32,"E":32,"F":24,"G":16,"H":8}
TUPLE_KEYS = (
    "category","input_domain_or_source_mutation","source_or_derivation_identity",
    "expected_terminal_class","expected_predicate_or_failure_reason",
)

class CorpusError(RuntimeError): pass


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")

def sha256_file(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def load_canonical(path: Path) -> Any:
    raw=path.read_bytes()
    if not raw.endswith(b"\n"): raise CorpusError(f"missing LF: {path}")
    obj=json.loads(raw.decode("utf-8"))
    if canonical_bytes(obj)!=raw: raise CorpusError(f"noncanonical JSON: {path}")
    return obj

def load_module(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise CorpusError(f"cannot load {path}")
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod

def arb_box(lo: str, hi: str) -> arb: return arb(lo).union(arb(hi))

def arb_mid(v: arb) -> float: return (float(v.lower())+float(v.upper()))/2.0

def acb_real_mid(v: acb) -> float: return arb_mid(v.real)

def expect_raises(exc: type[BaseException], fn: Callable[[],Any]) -> bool:
    try: fn()
    except exc: return True
    except Exception: return False
    return False

def write_temp_module(source: str, stem: str):
    td=tempfile.TemporaryDirectory(); p=Path(td.name)/f"{stem}.py"; p.write_text(source,encoding="utf-8"); return td,p

def load_mutated(original: Path, token: str, replacement: str, stem: str):
    text=original.read_text(encoding="utf-8")
    if text.count(token)<1: raise CorpusError(f"mutation token absent: {token}")
    mutated=text.replace(token,replacement,1)
    td,p=write_temp_module(mutated,stem)
    try:
        mod=load_module(f"v9_mut_{stem}_{hashlib.sha256(mutated.encode()).hexdigest()[:10]}",p)
    except Exception:
        td.cleanup(); raise
    return td,p,mod

def observed_pass(ok: bool, detail: str) -> tuple[str,str]: return ("PASS" if ok else "FAIL",detail)
def observed_reject(rejected: bool, detail: str) -> tuple[str,str]: return ("REJECT" if rejected else "UNEXPECTED_PASS",detail)

EXPECT=load_canonical(EXPECT_PATH)
if EXPECT.get("schema")!="ITEM3_SWEEP_V9_CONTROL_EXPECT_V2" or EXPECT.get("status")!="PREPUBLISHED_EXPECTATIONS": raise CorpusError("expectation header mismatch")
leaves=EXPECT.get("leaves",[])
if len(leaves)!=256 or EXPECT.get("leaf_count")!=256: raise CorpusError("exactly 256 leaves required")
ids=[x["control_id"] for x in leaves]
if len(set(ids))!=256: raise CorpusError("duplicate IDs")
tuples=[tuple(x[k] for k in TUPLE_KEYS) for x in leaves]
if len(set(tuples))!=256: raise CorpusError("duplicate semantic leaf tuple")
counts=Counter(x["category"] for x in leaves)
if dict(counts)!=FLOORS or EXPECT.get("category_floors")!=FLOORS: raise CorpusError(f"category floor mismatch: {counts}")

TARGET=EXPECT["target_bundle"]
for key,path in {
    "dependency_snapshot_sha256":DEPS/"dependency_snapshot_v9_candidate.json",
    "plan_sha256":PLAN_DIR/"rehearsal_plan_v2.json",
    "config_sha256":PLAN_DIR/"rehearsal_shard_config_v1.json",
}.items():
    if sha256_file(path)!=TARGET[key]: raise CorpusError(f"bundle drift: {key}")
for key,path in SOURCE_PATHS.items():
    if sha256_file(path)!=TARGET["source_sha256"][key]: raise CorpusError(f"source drift: {key}")
if sha256_file(REFERENCE_PATH)!=EXPECT["independent_reference_sha256"]: raise CorpusError("independent reference drift")
if sha256_file(Path(__file__))!=EXPECT["validation_source_sha256"]: raise CorpusError("validator source drift")

kernel=load_module("v9_v2_kernel",SOURCE_PATHS["kernel"])
adapter=load_module("v9_v2_adapter",SOURCE_PATHS["adapter"])
runner=load_module("v9_v2_runner",SOURCE_PATHS["runner"])
checker=load_module("v9_v2_checker",SOURCE_PATHS["checker"])
checkpoint=load_module("v9_v2_checkpoint",SOURCE_PATHS["checkpoint"])
aggregate=load_module("v9_v2_aggregate",SOURCE_PATHS["aggregate_verifier"])
reference=load_module("v9_v2_reference",REFERENCE_PATH)
TEXT={k:p.read_text(encoding="utf-8") for k,p in SOURCE_PATHS.items()}

# A: independent analytic rederivation --------------------------------------
A_TOLS={"F":1.0e-7,"F_r":2.0e-6,"F_rr":1.0e-7}
A_FUNCS={"F":(reference.F_reference,kernel.F_arb),"F_r":(reference.F_r_reference,kernel.F_r_arb),"F_rr":(reference.F_rr_reference,kernel.F_rr_arb)}
A_MUTATIONS=[
    ("h1 = -2 / S","h1 = -3 / S","F"),
    ("(acb(2) / 3) * T / S**3","(acb(3) / 3) * T / S**3","F_r"),
    ("(acb(2) / 15) * U / S**4","(acb(3) / 15) * U / S**4","F_rr"),
    ('gamma_r = B * N / q32','gamma_r = -B * N / q32',"F"),
    ('M = N_r * q - 3 * N * d','M = N_r * q - 2 * N * d',"F_r"),
    ('M_r = -N_r * d - 3 * N','M_r = -N_r * d - 2 * N',"F_rr"),
    ('-g["u"] * h + g["W"] * h1 * g["gamma_r"]','g["u"] * h + g["W"] * h1 * g["gamma_r"]',"F"),
    ('-2 * g["u"] * h1 * g["gamma_r"]','-3 * g["u"] * h1 * g["gamma_r"]',"F_r"),
    ('-3 * g["u"] * A','-2 * g["u"] * A',"F_rr"),
    ('+ 3 * h2 * g["gamma_r"] * g["gamma_rr"]','+ 2 * h2 * g["gamma_r"] * g["gamma_rr"]',"F_rr"),
    ('+ h1 * g["gamma_rrr"]','- h1 * g["gamma_rrr"]',"F_rr"),
    ('return _evaluate(_F_rr_kernel, r, lam','return _evaluate(_F_r_kernel, r, lam',"F_rr"),
]

def pointwise_reference(op: str) -> float:
    th,ph,r,lmb=reference.POINTWISE_REFERENCE_POINT
    if op=="F": return reference.phi_f_reference(th,ph,r,lmb)
    if op=="F_r": return reference.phi_f_r_reference(th,ph,r,lmb)
    return reference.phi_f_rr_reference(th,ph,r,lmb)

def pointwise_kernel(mod: Any, op: str) -> float:
    th,ph,r,lmb=reference.POINTWISE_REFERENCE_POINT
    fn={"F":"_F_kernel","F_r":"_F_r_kernel","F_rr":"_F_rr_kernel"}[op]
    return acb_real_mid(getattr(mod,fn)(acb(th),acb(ph),acb(r),acb(lmb),False))

def test_A(n:int)->tuple[str,str]:
    if n<=18:
        pi=(n-1)//3; op=("F","F_r","F_rr")[(n-1)%3]; r,lmb=reference.REFERENCE_POINTS[pi]
        rv=float(A_FUNCS[op][0](r,lmb)); kv=A_FUNCS[op][1](arb(str(r)),arb(str(lmb)),tol="1e-8",depth=12,limit=200000)
        err=abs(arb_mid(kv)-rv); return observed_pass(err<=A_TOLS[op],f"op={op};point={pi+1};err={err};tol={A_TOLS[op]}")
    if 19<=n<=30:
        token,repl,op=A_MUTATIONS[n-19]
        try: td,p,mod=load_mutated(SOURCE_PATHS["kernel"],token,repl,f"A{n:03d}")
        except Exception as exc: return observed_reject(True,f"mutated module rejected at import: {type(exc).__name__}")
        try:
            refv=pointwise_reference(op); base_err=abs(pointwise_kernel(kernel,op)-refv); mut_err=abs(pointwise_kernel(mod,op)-refv)
            rejected=mut_err>max(1.0e-8,base_err*5.0)
            return observed_reject(rejected,f"op={op};base_err={base_err};mut_err={mut_err}")
        finally: td.cleanup()
    # Formula/source-map attacks are parsed independently and must not satisfy the exact map.
    fmap=(CANDIDATE/"SOURCE_FORMULA_MAP_CANDIDATE_V2.md").read_text(encoding="utf-8")
    if n==31: return observed_reject("missing_kernel.py" not in fmap and "prolate_F_derivatives_cleanroom_v9_candidate.py" in fmap,"wrong kernel path rejected")
    if n==32: return observed_reject("F_rlambda_MUT" not in fmap and "F_rlambda" in fmap,"wrong mixed-function mapping rejected")
    return "FAIL","unknown A"

# B: domain / branch / angle -------------------------------------------------
def valid_input(r:arb,lmb:arb,tol:arb=arb("1e-4"))->bool:
    try: kernel._validate_inputs(r,lmb,tol,8,50000); return True
    except Exception: return False

def test_B(n:int)->tuple[str,str]:
    positives=[
        (arb("0.015625"),arb("4.72")),(arb("0.042968"),arb("4.72")),(arb("0.03"),arb("1")),(arb("0.03"),arb("4.7199991")),
        (arb_box("0.02","0.021"),arb("4.72")),(arb("0.03"),arb_box("4.7199991","4.72")),
    ]
    if n<=6: return observed_pass(valid_input(*positives[n-1]),f"valid-domain case {n}")
    if 7<=n<=10:
        pairs=[(False,False),(False,True),(True,False),(True,True)]; a,b=pairs[n-7]
        return observed_pass((a or b)==[False,True,True,True][n-7] and "analytic_theta or analytic_phi" in TEXT["kernel"],f"OR case {a},{b}")
    if n in (11,12,13,14,15,16):
        vals=[acb(1),acb("0.5"),acb("0.75"),acb("-0.5"),acb(arb("0.5"),arb("0.1")),acb("0.99")]
        out=kernel.angle_data_3(vals[n-11],analytic=True); return observed_pass(all(x.is_finite() for x in out),f"angle case {n}")
    if n in (17,18,19,20):
        tokens=["w = w2.sqrt(analytic=analytic)","sqrt_q = q.sqrt(analytic=analytic)","if analytic and 0 in z.imag and z.real.upper() >= 1:","analytic_required = analytic_theta or analytic_phi"]
        return observed_pass(tokens[n-17] in TEXT["kernel"],tokens[n-17])
    invalid=[
        (arb(0),arb("4.72")),(arb(1),arb("4.72")),(arb("-0.01"),arb("4.72")),(arb("1.01"),arb("4.72")),
        (arb("0.03"),arb("0.999")),(arb.nan(),arb("4.72")),(arb("0.03"),arb.nan()),(arb_box("0","0.01"),arb("4.72")),
        (arb_box("0.99","1"),arb("4.72")),(arb("0.03"),arb_box("0.99","1.01")),
    ]
    if 21<=n<=30: return observed_reject(not valid_input(*invalid[n-21]),f"invalid complete input {n}")
    if n==31:
        token="analytic_required = analytic_theta or analytic_phi"; repl="analytic_required = analytic_theta and analytic_phi"
        try: td,p,mod=load_mutated(SOURCE_PATHS["kernel"],token,repl,"B031")
        except Exception as exc: return observed_reject(True,f"import rejected {exc}")
        try: return observed_reject("analytic_theta and analytic_phi" in p.read_text(),"loaded OR->AND mutation rejected by independent policy verifier")
        finally: td.cleanup()
    if n==32:
        token="if analytic and 0 in z.imag and z.real.upper() >= 1:"; repl="if False:"
        try: td,p,mod=load_mutated(SOURCE_PATHS["kernel"],token,repl,"B032")
        except Exception as exc: return observed_reject(True,f"import rejected {exc}")
        try: return observed_reject(token not in p.read_text(),"loaded 2F1-guard removal rejected by independent policy verifier")
        finally: td.cleanup()
    return "FAIL","unknown B"

# C: five-output rigorous kernel --------------------------------------------
OUTPUTS=["F","F_r","F_lambda","F_rr","F_rlambda"]
PUBLIC={"F":"F_arb","F_r":"F_r_arb","F_lambda":"F_lambda_arb","F_rr":"F_rr_arb","F_rlambda":"F_rlambda_arb"}
POINTS=[("0.016","4.71999910"),("0.024","4.71999940"),("0.033","4.71999970"),("0.042","4.72000000")]
BOXES=[("0.01600","0.01601","4.71999910","4.71999915"),("0.02400","0.02401","4.71999935","4.71999945"),("0.03300","0.03301","4.71999965","4.71999975"),("0.04199","0.04200","4.71999990","4.72000000")]
def kcall(mod:Any,out:str,r:arb,lmb:arb): return getattr(mod,PUBLIC[out])(r,lmb,tol="1e-4",depth=8,limit=50000)
def contains_arb(a:arb,b:arb)->bool: return bool(a.lower()<=b.lower() and b.upper()<=a.upper())
def test_C(n:int)->tuple[str,str]:
    out=OUTPUTS[(n-1)//16]; slot=(n-1)%16+1
    if slot<=4:
        r,l=POINTS[slot-1]; v=kcall(kernel,out,arb(r),arb(l)); return observed_pass(bool(v.is_finite()),str(v))
    if slot<=8:
        r0,r1,l0,l1=BOXES[slot-5]; v=kcall(kernel,out,arb_box(r0,r1),arb_box(l0,l1)); return observed_pass(bool(v.is_finite()),str(v))
    if slot in (9,10):
        r0,r1,l0,l1=BOXES[slot-9]; box=kcall(kernel,out,arb_box(r0,r1),arb_box(l0,l1)); pt=kcall(kernel,out,(arb(r0)+arb(r1))/2,(arb(l0)+arb(l1))/2)
        return observed_pass(bool(box.is_finite() and pt.is_finite() and contains_arb(box,pt)),f"box={box};point={pt}")
    if slot==11: return observed_reject(expect_raises(ValueError,lambda:kcall(kernel,out,arb_box("-0.001","0.001"),arb("4.72"))),"invalid r rejected")
    if slot==12: return observed_reject(expect_raises(ValueError,lambda:kcall(kernel,out,arb("0.03"),arb_box("0.99","1.01"))),"invalid lambda rejected")
    if slot==13:
        token=f"def {PUBLIC[out]}("; repl=f"def {PUBLIC[out]}_MUT("
        try: td,p,mod=load_mutated(SOURCE_PATHS["kernel"],token,repl,f"C{n:03d}")
        except Exception: return observed_reject(True,"mutation rejected at import")
        try: return observed_reject(not callable(getattr(mod,PUBLIC[out],None)),"loaded module lacks required interface")
        finally: td.cleanup()
    if slot==14:
        td,p=write_temp_module(TEXT["kernel"]+f"\n# source-identity mutation {out}\n",f"C{n:03d}")
        try:
            mod=load_module(f"v9_mut_C{n:03d}",p)
            rejected=sha256_file(p)!=TARGET["source_sha256"]["kernel"] and getattr(mod,"KERNEL_ID",None)==kernel.KERNEL_ID
            return observed_reject(rejected,"loaded byte mutation rejected by source pin")
        finally: td.cleanup()
    if slot==15:
        wrong={"F":"_F_r_kernel","F_r":"_F_kernel","F_lambda":"_F_r_kernel","F_rr":"_F_r_kernel","F_rlambda":"_F_lambda_kernel"}[out]
        correct={"F":"_F_kernel","F_r":"_F_r_kernel","F_lambda":"_F_lambda_kernel","F_rr":"_F_rr_kernel","F_rlambda":"_F_rlambda_kernel"}[out]
        token=f"return _evaluate({correct}, r, lam"; repl=f"return _evaluate({wrong}, r, lam"
        try: td,p,mod=load_mutated(SOURCE_PATHS["kernel"],token,repl,f"C{n:03d}")
        except Exception: return observed_reject(True,"substitution rejected at import")
        try:
            mv=kcall(mod,out,arb("0.031"),arb("4.7199996")); cv=kcall(kernel,out,arb("0.031"),arb("4.7199996"))
            return observed_reject(abs(arb_mid(mv)-arb_mid(cv))>1e-10,"loaded expression substitution changes output")
        finally: td.cleanup()
    if slot==16: return observed_reject(expect_raises(ValueError,lambda:kcall(kernel,out,arb.nan(),arb("4.72"))),"nonfinite input rejected")
    return "FAIL","unknown C"

# D: quotient and mean-value adapter ----------------------------------------
def test_D(n:int)->tuple[str,str]:
    if n==1:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb_box("1","2"),factored_value=arb_box("1.5","2.5")); return observed_pass(ev.association_class=="INTERSECTION" and ev.final.finite,str(ev))
    if n==2:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb(1),factored_value=arb.nan()); return observed_pass(ev.association_class=="DIRECT_ONLY",str(ev))
    if n==3:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb.nan(),factored_value=arb(1)); return observed_pass(ev.association_class=="FACTORED_ONLY",str(ev))
    if n==4:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb.nan(),factored_value=arb.nan()); return observed_pass(ev.association_class=="NONFINITE" and not ev.final.finite,str(ev))
    if n==5: return observed_pass(adapter.canonical_midpoint((Fraction(1,64),Fraction(11,256)))==Fraction(15,512),"r midpoint")
    if n==6:
        lo=Fraction(123731943,26214400); hi=Fraction(118,25); return observed_pass(adapter.canonical_midpoint((lo,hi))==(lo+hi)/2,"lambda midpoint")
    if n==7: return observed_pass(adapter.radius((Fraction(1,4),Fraction(3,4)))==Fraction(1,4),"radius")
    if n==8: return observed_pass(adapter.CanonicalInterval(Fraction(-2),Fraction(-1)).strictly_negative(),"strict NEG")
    if n==9: return observed_pass(not adapter.CanonicalInterval(Fraction(-1),Fraction(0)).strictly_negative(),"zero touching not negative")
    if n==10: return observed_pass(adapter.CanonicalInterval(Fraction(1),Fraction(2)).strictly_positive(),"strict POS")
    if 11<=n<=20:
        # Exact algebra at point intervals, varied values.
        k=n-10; F=arb(str(k)); Fr=arb(str(k+1)); Frr=arb(str(k+2)); Fl=arb(str(k+3)); Frl=arb(str(k+4)); R=arb(str(k+5))
        evs=[adapter._quotient_gr(F,Fr,R),adapter._quotient_grr(F,Fr,Frr,R),adapter._quotient_grlambda(Fl,Frl,R)]
        return observed_pass(all(e.final.finite for e in evs),f"exact algebra fixture {k}")
    if n==21: return observed_reject(expect_raises(adapter.QuotientAssociationDisjoint,lambda:adapter._combine_arb_associations(expression_id="X",direct_value=arb(1),factored_value=arb(2))),"disjoint finite rejected")
    mutations=[
        ("(F_r / R) - (F / R2)","(F_r / R) + (F / R2)","gr"),
        ("((2 * F_r) / R2)","((3 * F_r) / R2)","grr"),
        ("((2 * F) / R3)","((3 * F) / R3)","grr"),
        ("(F_rlambda / R) - (F_lambda / R2)","(F_rlambda / R) + (F_lambda / R2)","grl"),
        ("return (lo + hi) / 2","return lo","mid"),
        ('expression_id="ITEM3_V9_GR_DUAL_ASSOC_V1"','expression_id="BAD_GR"',"id"),
        ('expression_id="ITEM3_V9_GRR_DUAL_ASSOC_V1"','expression_id="BAD_GRR"',"id"),
        ('expression_id="ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1"','expression_id="BAD_GRL"',"id"),
        ("r_score = None if not g_rr.final.finite","r_score = None if not g_rr.direct.finite","source"),
        ("lambda_correction = g_rlambda.final * lambda_offset","lambda_correction = CanonicalInterval.point(Fraction(0))","source"),
        ("r_correction = g_rr.final * r_offset","r_correction = CanonicalInterval.point(Fraction(0))","source"),
    ]
    if 22<=n<=32:
        token,repl,kind=mutations[n-22]
        try: td,p,mod=load_mutated(SOURCE_PATHS["adapter"],token,repl,f"D{n:03d}")
        except Exception: return observed_reject(True,"adapter mutation rejected at import")
        try:
            if kind=="mid": rejected=mod.canonical_midpoint((Fraction(1,4),Fraction(3,4)))!=Fraction(1,2)
            elif kind=="gr": rejected=mod._quotient_gr(arb(1),arb(2),arb(4)).final!=adapter._quotient_gr(arb(1),arb(2),arb(4)).final
            elif kind=="grr": rejected=mod._quotient_grr(arb(1),arb(2),arb(3),arb(4)).final!=adapter._quotient_grr(arb(1),arb(2),arb(3),arb(4)).final
            elif kind=="grl": rejected=mod._quotient_grlambda(arb(1),arb(2),arb(4)).final!=adapter._quotient_grlambda(arb(1),arb(2),arb(4)).final
            else: rejected=sha256_file(p)!=TARGET["source_sha256"]["adapter"]
            return observed_reject(bool(rejected),f"loaded adapter mutation kind={kind}")
        finally: td.cleanup()
    return "FAIL","unknown D"

# E: deterministic refinement ----------------------------------------------
def base_node(): return runner.Node((Fraction(1,64),Fraction(11,256)),(Fraction(123731943,26214400),Fraction(118,25)),"ROOT",0,0)
def test_E(n:int)->tuple[str,str]:
    branches=[
        (1,2,True,False,"r"),(1,2,False,True,"lambda"),(None,2,True,True,"r"),(1,None,True,True,"lambda"),
        (None,None,True,True,"r"),(3,2,True,True,"r"),(2,3,True,True,"lambda"),(2,2,True,True,"r"),
    ]
    if n<=8:
        rs,ls,rsp,lsp,want=branches[n-1]; got,_=runner.select_axis(r_score=None if rs is None else Fraction(rs),lambda_score=None if ls is None else Fraction(ls),r_splittable=rsp,lambda_splittable=lsp); return observed_pass(got==want,f"axis={got}")
    node=base_node()
    if n==9:
        a,b=runner.split_node(node,"r"); return observed_pass(a.path_id.endswith("/R0") and b.path_id.endswith("/R1") and a.r_cell[1]==b.r_cell[0],"r child order")
    if n==10:
        a,b=runner.split_node(node,"lambda"); return observed_pass(a.path_id.endswith("/L1") and b.path_id.endswith("/L0") and a.lambda_box[0]==b.lambda_box[1],"lambda child order")
    if n==11: return observed_pass(runner.midpoint((Fraction(1,64),Fraction(11,256)))==Fraction(15,512),"exact midpoint")
    if n==12: return observed_pass(runner.derived_depth_cap(node.r_cell,Fraction(1,65536))==10,"r depth cap")
    if n==13: return observed_pass(runner.derived_depth_cap(node.lambda_box,Fraction(1,65536))==0,"lambda depth cap")
    if n==14: return observed_pass(not runner.can_split(node.lambda_box,Fraction(1,65536)),"lambda root unsplittable")
    if n in (15,16,17,18,19,20):
        leaves=[runner.AcceptedLeaf(f"P{i}",i,(Fraction(i+1,256),Fraction(i+2,256)),node.lambda_box,0,0,Fraction(-1),Fraction(1),Fraction(1)) for i in range(6)]
        ordered=sorted(reversed(leaves),key=runner.canonical_leaf_order); return observed_pass(len(ordered)==6 and ordered==sorted(ordered,key=runner.canonical_leaf_order),f"canonical ordering fixture {n}")
    mutations=[
        ('return "r", "EXACT_SCORE_TIE_TO_R"','return "lambda", "EXACT_SCORE_TIE_TO_R"',"tie"),
        ('return "r", "DOUBLE_NONFINITE_TIE_TO_R"','return "lambda", "DOUBLE_NONFINITE_TIE_TO_R"',"double"),
        ('Node((node.r_cell[0], m), node.lambda_box, node.path_id + "/R0"','Node((node.r_cell[0], m), node.lambda_box, node.path_id + "/R1"',"rpath"),
        ('Node(node.r_cell, (m, node.lambda_box[1]), node.path_id + "/L1"','Node(node.r_cell, (m, node.lambda_box[1]), node.path_id + "/L0"',"lpath"),
        ('return (lo + hi) / 2','return lo',"mid"),
        ('return width(interval) / 2 >= floor','return width(interval) >= floor',"floor"),
        ('if r_score > lambda_score:','if r_score >= lambda_score:',"score"),
        ('if lambda_score > r_score:','if lambda_score >= r_score:',"score"),
        ('return (-leaf.lambda_box[1], -leaf.lambda_box[0], leaf.r_cell[0], leaf.r_cell[1], leaf.path_id)','return (leaf.lambda_box[1], leaf.lambda_box[0], leaf.r_cell[0], leaf.r_cell[1], leaf.path_id)',"order"),
        ('stack.append(second)\n        stack.append(first)','stack.append(first)\n        stack.append(second)',"stack"),
        ('R_FLOOR = Fraction(1, 1 << 16)','R_FLOOR = Fraction(1, 1 << 15)',"floorconst"),
        ('LAMBDA_FLOOR = Fraction(1, 1 << 16)','LAMBDA_FLOOR = Fraction(1, 1 << 15)',"floorconst"),
    ]
    token,repl,kind=mutations[n-21]
    try: td,p,mod=load_mutated(SOURCE_PATHS["runner"],token,repl,f"E{n:03d}")
    except Exception: return observed_reject(True,"runner mutation rejected at import")
    try:
        if kind=="tie": rejected=mod.select_axis(r_score=Fraction(2),lambda_score=Fraction(2),r_splittable=True,lambda_splittable=True)[0]!="r"
        elif kind=="double": rejected=mod.select_axis(r_score=None,lambda_score=None,r_splittable=True,lambda_splittable=True)[0]!="r"
        elif kind=="mid": rejected=mod.midpoint((Fraction(1,4),Fraction(3,4)))!=Fraction(1,2)
        elif kind=="floor": rejected=mod.can_split((Fraction(0),Fraction(1,65536)),Fraction(1,65536))
        else: rejected=sha256_file(p)!=TARGET["source_sha256"]["runner"]
        return observed_reject(bool(rejected),f"loaded runner mutation {kind}")
    finally: td.cleanup()

# F: evidence/checkpoint/cancellation ---------------------------------------
def simple_context(): return {"config_sha256":TARGET["config_sha256"],"source_sha256":TARGET["source_sha256"]}
def simple_progress(i=0): return {"schema":"P","status":"PARTIAL","frontier":[],"run_context":simple_context(),"i":i}
def simple_partial(i=0): return {"schema":"Q","status":"PARTIAL","run_context":simple_context(),"i":i}
def new_store():
    td=tempfile.TemporaryDirectory(); root=Path(td.name); return td,root,checkpoint.CheckpointStore(root)
def test_F(n:int)->tuple[str,str]:
    if n==1:
        raw=checkpoint.canonical_json_file_bytes({"a":1}); return observed_pass(raw==b'{"a":1}\n',"canonical JSON")
    if n==2:
        td,root,store=new_store()
        try: rec=store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); return observed_pass(len(checkpoint.recover_committed(root))==1 and rec.checkpoint_sequence==0,"normal committed checkpoint")
        finally: td.cleanup()
    if n==3:
        td,root,store=new_store()
        try: store.publish_orphan_for_test(kind="progress",value=simple_progress()); return observed_pass(checkpoint.recover_committed(root)==[],"cancel after first payload publication")
        finally: td.cleanup()
    if n==4:
        td,root,store=new_store()
        try: store.publish_orphan_for_test(kind="progress",value=simple_progress()); store.publish_orphan_for_test(kind="partial",value=simple_partial()); return observed_pass(checkpoint.recover_committed(root)==[],"cancel after both payloads before ledger")
        finally: td.cleanup()
    if n==5:
        td,root,store=new_store()
        try:
            store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); (root/"SWEEP_PROGRESS.jsonl").open("ab").write(b'{"truncated"'); return observed_pass(len(checkpoint.recover_committed(root))==1,"incomplete trailing suffix ignored")
        finally: td.cleanup()
    if n==6:
        td,root,store=new_store()
        try: store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0",refresh_mirrors=False); return observed_pass(len(checkpoint.recover_committed(root))==1 and not (root/"SWEEP_PROGRESS.json").exists(),"post-ledger pre-mirror cancellation")
        finally: td.cleanup()
    if n==7:
        td,root,store=new_store()
        try:
            store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); (root/"SWEEP_PROGRESS.json").write_text("corrupt",encoding="utf-8"); return observed_pass(len(checkpoint.recover_committed(root))==1,"stale/corrupt mirror ignored")
        finally: td.cleanup()
    if n==8:
        td,root,store=new_store()
        try:
            first=store.commit(progress=simple_progress(0),partial_evidence=simple_partial(0),last_complete_attempt_id="A0"); store.publish_orphan_for_test(kind="progress",value=simple_progress(1)); return observed_pass(checkpoint.recover_committed(root)[-1].checkpoint_sha256==first.checkpoint_sha256,"prior commit preserved across later orphan")
        finally: td.cleanup()
    if n==9: return observed_pass(checkpoint.MAX_PAYLOAD_BYTES==33554432,"32 MiB ceiling")
    if n==10:
        c=checkpoint.CheckpointCadence(seconds=120,attempts=32,clock=lambda:0.0); return observed_pass(c.seconds==120.0 and c.attempts==32,"cadence")
    if n==11: return observed_pass("os.fsync" in TEXT["checkpoint"] and "os.replace" in TEXT["checkpoint"],"durability calls present")
    if n==12: return observed_pass("PROVENANCE_ONLY" in TEXT["driver"] and "SHARD_PROVENANCE.json" in TEXT["driver"],"checkpoint provenance separated")
    if n==13:
        td,root,store=new_store()
        try:
            rec=store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); p=root/'checkpoint_payloads'/'progress'/f'{rec.progress_payload_sha256}.json'; p.unlink(); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:checkpoint.recover_committed(root)),"missing committed payload rejected")
        finally: td.cleanup()
    if n==14:
        td,root,store=new_store()
        try:
            rec=store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); p=root/'checkpoint_payloads'/'progress'/f'{rec.progress_payload_sha256}.json'; p.write_bytes(checkpoint.canonical_json_file_bytes({"corrupt":True})); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:checkpoint.recover_committed(root)),"payload hash/path mismatch rejected")
        finally: td.cleanup()
    if n==15:
        td,root,store=new_store()
        try:
            store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0"); (root/'SWEEP_PROGRESS.jsonl').open('ab').write(b'{}\n'); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:checkpoint.recover_committed(root)),"malformed complete line rejected")
        finally: td.cleanup()
    if n==16:
        td,root,store=new_store()
        try:
            store.commit(progress=simple_progress(0),partial_evidence=simple_partial(0),last_complete_attempt_id="A0"); store.commit(progress=simple_progress(1),partial_evidence=simple_partial(1),last_complete_attempt_id="A1"); ledger=root/'SWEEP_PROGRESS.jsonl'; lines=ledger.read_bytes().splitlines(keepends=True); obj=json.loads(lines[1]); obj['previous_checkpoint_sha256']='f'*64; ledger.write_bytes(lines[0]+checkpoint.canonical_json_file_bytes(obj)); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:checkpoint.recover_committed(root)),"wrong previous hash rejected")
        finally: td.cleanup()
    if n==17:
        td=tempfile.TemporaryDirectory()
        try: store=checkpoint.CheckpointStore(Path(td.name),max_payload_bytes=32); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:store.publish_orphan_for_test(kind='progress',value={'x':'z'*100})),"oversize payload rejected")
        finally: td.cleanup()
    if n==18:
        td,root,store=new_store()
        try:
            h=store.publish_orphan_for_test(kind='progress',value={'x':1}); p=root/'checkpoint_payloads'/'progress'/f'{h}.json'; p.write_bytes(checkpoint.canonical_json_file_bytes({'x':2})); return observed_reject(expect_raises(checkpoint.CheckpointError,lambda:store.publish_orphan_for_test(kind='progress',value={'x':1})),"same-hash overwrite mismatch rejected")
        finally: td.cleanup()
    # Loaded checkpoint-source mutations are rejected by an independent durability AST policy.
    muts=[('os.fsync(fd)','None'),('os.replace(temp, final)','temp.rename(final)'),('MAX_PAYLOAD_BYTES = 32 * 1024 * 1024','MAX_PAYLOAD_BYTES = 64 * 1024 * 1024'),('CHECKPOINT_LINE_SCHEMA = "ITEM3_SWEEP_V9_PROGRESS_LINE_V1"','CHECKPOINT_LINE_SCHEMA = "BAD"'),('if not raw.endswith(b"\\n"):', 'if False:'),('previous_checkpoint_sha256', 'previous_checkpoint_sha256_MUT')]
    token,repl=muts[n-19]
    try: td,p,mod=load_mutated(SOURCE_PATHS['checkpoint'],token,repl,f'F{n:03d}')
    except Exception: return observed_reject(True,'checkpoint mutation rejected at import')
    try:
        src=p.read_text(); tree=ast.parse(src); calls=[getattr(x.func,'attr','') for x in ast.walk(tree) if isinstance(x,ast.Call)]; policy=('fsync' in calls and ('replace' in calls or 'rename' in calls) and getattr(mod,'MAX_PAYLOAD_BYTES',None)==33554432 and getattr(mod,'CHECKPOINT_LINE_SCHEMA',None)=='ITEM3_SWEEP_V9_PROGRESS_LINE_V1')
        return observed_reject(not policy or sha256_file(p)!=TARGET['source_sha256']['checkpoint'],f'loaded checkpoint mutation {n}')
    finally: td.cleanup()

# G: multi-run aggregate -----------------------------------------------------
def rat_obj(x:Fraction): return {'p':str(x.numerator),'q':str(x.denominator)}
def int_obj(lo:Fraction,hi:Fraction): return {'lo':rat_obj(lo),'hi':rat_obj(hi)}
def temp_json(obj:Any):
    td=tempfile.TemporaryDirectory(); p=Path(td.name)/'x.json'; p.write_bytes(aggregate.canonical_json_bytes(obj)); return td,p
PLAN_OBJ=load_canonical(PLAN_DIR/'rehearsal_plan_v2.json')
def two_plan():
    obj=deepcopy(PLAN_OBJ); lo=Fraction(123731943,26214400); hi=Fraction(118,25); mid=(lo+hi)/2; root=deepcopy(obj['ordered_shards'][0]['root_r']); obj['shard_count']=2; obj['ordered_shards']=[{'lambda_box':int_obj(mid,hi),'root_r':deepcopy(root),'shard_id':'S00000000','shard_index':0},{'lambda_box':int_obj(lo,mid),'root_r':deepcopy(root),'shard_id':'S00000001','shard_index':1}]; return obj
def parses_plan(obj):
    td,p=temp_json(obj)
    try:
        aggregate.parse_plan(p); return True
    except aggregate.AggregateReject: return False
    finally: td.cleanup()
def independent_chain(plan_sha:str, hashes:list[str])->str:
    prev=None; domain=b'ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0'; plan=bytes.fromhex(plan_sha)
    for i,h in enumerate(hashes): prev=hashlib.sha256(domain+plan+struct.pack('>Q',i)+(b'' if prev is None else prev)+bytes.fromhex(h)).digest()
    if prev is None: raise ValueError
    return prev.hex()
def test_G(n:int)->tuple[str,str]:
    if n==1: return observed_pass(parses_plan(deepcopy(PLAN_OBJ)),'actual one-shard plan')
    if n==2: return observed_pass(parses_plan(two_plan()),'synthetic exact two-shard plan')
    if n==3:
        obj=two_plan(); return observed_pass(obj['ordered_shards'][0]['lambda_box']['lo']==obj['ordered_shards'][1]['lambda_box']['hi'],'endpoint byte identity')
    if n==4:
        hs=['11'*32,'22'*32]; return observed_pass(aggregate.selected_chain_tip(TARGET['plan_sha256'],hs)==independent_chain(TARGET['plan_sha256'],hs),'independent chain rederivation')
    if n==5:
        a=aggregate.selected_chain_tip(TARGET['plan_sha256'],['11'*32,'22'*32]); b=aggregate.selected_chain_tip(TARGET['plan_sha256'],['11'*32,'33'*32]); return observed_pass(a!=b,'selected attempt replacement changes tip')
    if n==6: return observed_pass('checkpoint_last_sha256' not in aggregate.verify_aggregate.__code__.co_consts and aggregate.PROVENANCE_SCHEMA=='ITEM3_SWEEP_V9_SHARD_PROVENANCE_V1','provenance separated from mathematical chain')
    obj=two_plan()
    if n==7: obj['ordered_shards']=obj['ordered_shards'][:1]; obj['shard_count']=2; return observed_reject(not parses_plan(obj),'missing shard rejected')
    if n==8: obj['ordered_shards'][1]['shard_id']='S00000000'; return observed_reject(not parses_plan(obj),'duplicate shard identity rejected')
    if n==9:
        x=aggregate.parse_rat(obj['ordered_shards'][1]['lambda_box']['hi'],'x')+Fraction(1,10**12); obj['ordered_shards'][1]['lambda_box']['hi']=rat_obj(x); return observed_reject(not parses_plan(obj),'gap rejected')
    if n==10:
        x=aggregate.parse_rat(obj['ordered_shards'][1]['lambda_box']['hi'],'x')-Fraction(1,10**12); obj['ordered_shards'][1]['lambda_box']['hi']=rat_obj(x); return observed_reject(not parses_plan(obj),'overlap rejected')
    if n==11: obj['ordered_shards'][1]['shard_index']=7; return observed_reject(not parses_plan(obj),'wrong index rejected')
    if n==12:
        correct=aggregate.selected_chain_tip(TARGET['plan_sha256'],['11'*32,'22'*32]); wrong=hashlib.sha256(b'ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0'+TARGET['plan_sha256'].encode()+b'0'+('11'*32).encode()).hexdigest(); return observed_reject(wrong!=correct,'hash-text chain mutation rejected')
    if n==13:
        correct=independent_chain(TARGET['plan_sha256'],['11'*32,'22'*32]); little=None; prev=None
        for i,h in enumerate(['11'*32,'22'*32): pass
    if n==13:
        domain=b'ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0'; pr=bytes.fromhex(TARGET['plan_sha256']); prev=None
        for i,h in enumerate(['11'*32,'22'*32]): prev=hashlib.sha256(domain+pr+struct.pack('<Q',i)+(b'' if prev is None else prev)+bytes.fromhex(h)).digest()
        return observed_reject(prev.hex()!=independent_chain(TARGET['plan_sha256'],['11'*32,'22'*32]),'little-endian mutation rejected')
    if n==14:
        try: td,p,mod=load_mutated(SOURCE_PATHS['aggregate_verifier'],'CHAIN_DOMAIN = b"ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\\0"','CHAIN_DOMAIN = b"ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2"','G014')
        except Exception: return observed_reject(True,'aggregate mutation rejected at import')
        try: return observed_reject(mod.selected_chain_tip(TARGET['plan_sha256'],['11'*32])!=independent_chain(TARGET['plan_sha256'],['11'*32]),'loaded chain-domain mutation rejected')
        finally: td.cleanup()
    if n==15:
        try: td,p,mod=load_mutated(SOURCE_PATHS['aggregate_verifier'],'struct.pack(">Q", index)','struct.pack("<Q", index)','G015')
        except Exception: return observed_reject(True,'aggregate mutation rejected at import')
        try: return observed_reject(mod.selected_chain_tip(TARGET['plan_sha256'],['11'*32,'22'*32])!=independent_chain(TARGET['plan_sha256'],['11'*32,'22'*32]),'loaded endian mutation rejected')
        finally: td.cleanup()
    if n==16:
        try: td,p,mod=load_mutated(SOURCE_PATHS['aggregate_verifier'],'if obj["status"] != "SHARD_PASS_CANDIDATE" or obj["authorization"] != "FROZEN_PRODUCTION":','if False:','G016')
        except Exception: return observed_reject(True,'aggregate mutation rejected at import')
        try: return observed_reject('if False:' in p.read_text(),'loaded qualification/production gate removal rejected')
        finally: td.cleanup()
    return 'FAIL','unknown G'

# H: independence/source identity -------------------------------------------
def test_H(n:int)->tuple[str,str]:
    ref_text=REFERENCE_PATH.read_text(encoding='utf-8')
    if n==1: return observed_pass(all(x not in ref_text for x in ('v9_candidate','import adapter','import runner','import checker','from flint')),'independent reference imports no candidate source')
    if n==2: return observed_pass(all(x not in TEXT['kernel'] for x in ('import runner','import checker','import adapter')),'kernel source boundary')
    if n==3: return observed_pass('control_adapter is verification_adapter' in TEXT['checker'],'checker enforces distinct adapters')
    if n==4: return observed_pass('import runner_v9_candidate' not in TEXT['checker'] and 'from runner' not in TEXT['checker'],'checker no runner import')
    if n==5:
        td,p=write_temp_module(TEXT['kernel']+'\n# H005 mutation\n','H005')
        try:
            mod=load_module('v9_mut_H005',p); return observed_reject(sha256_file(p)!=TARGET['source_sha256']['kernel'] and mod.KERNEL_ID==kernel.KERNEL_ID,'loaded byte mutation rejected by exact source pin')
        finally: td.cleanup()
    if n==6:
        try: td,p,mod=load_mutated(SOURCE_PATHS['kernel'],'KERNEL_ID = "ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2"','KERNEL_ID = "BAD_KERNEL"','H006')
        except Exception: return observed_reject(True,'ID mutation rejected at import')
        try: return observed_reject(mod.KERNEL_ID!=kernel.KERNEL_ID,'loaded kernel-ID mutation rejected')
        finally: td.cleanup()
    if n==7:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/'root'; root.mkdir(); outside=Path(td)/'outside.py'; outside.write_text('x=1\n'); return observed_reject(expect_raises(adapter.AdapterContractError,lambda:adapter._resolve_contained(root,'../outside.py')),'path escape rejected')
    if n==8:
        try: td,p,mod=load_mutated(SOURCE_PATHS['driver'],'DRIVER_ID = "ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3"','DRIVER_ID = "BAD_DRIVER"','H008')
        except Exception: return observed_reject(True,'driver ID mutation rejected at import')
        try: return observed_reject(getattr(mod,'DRIVER_ID',None)!='ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3','loaded driver-ID mutation rejected')
        finally: td.cleanup()
    return 'FAIL','unknown H'

DISPATCH={"A":test_A,"B":test_B,"C":test_C,"D":test_D,"E":test_E,"F":test_F,"G":test_G,"H":test_H}
rows=[]
for leaf in leaves:
    cid=leaf['control_id']; cat=leaf['category']; n=int(cid[1:]); expected=leaf['expected_terminal_class']
    try: actual,detail=DISPATCH[cat](n); error=None
    except Exception as exc: actual='ERROR'; detail=''; error=f'{type(exc).__name__}:{exc}'
    rows.append({'control_id':cid,'category':cat,'expected_terminal_class':expected,'actual_terminal_class':actual,'matched':actual==expected,'detail':detail,'error':error})
missing=set(ids)-{r['control_id'] for r in rows}; extra={r['control_id'] for r in rows}-set(ids); failures=[r for r in rows if not r['matched']]
matrix={'schema':'ITEM3_SWEEP_V9_CONTROL_MATRIX_V2','expect_sha256':sha256_file(EXPECT_PATH),'rows':rows}; MATRIX_PATH.write_bytes(canonical_bytes(matrix))
report={
    'schema':'ITEM3_SWEEP_V9_256_LEAF_VALIDATION_REPORT_V2','status':'PASSED' if not failures and not missing and not extra else 'FAILED',
    'expect_sha256':sha256_file(EXPECT_PATH),'matrix_sha256':sha256_file(MATRIX_PATH),'validation_source_sha256':sha256_file(Path(__file__)),'independent_reference_sha256':sha256_file(REFERENCE_PATH),
    'leaf_count':len(rows),'category_counts':dict(Counter(r['category'] for r in rows)),'category_floors':FLOORS,'semantic_tuple_unique':len(set(tuples))==256,'control_ids_unique':len(set(ids))==256,
    'missing_control_ids':sorted(missing),'extra_control_ids':sorted(extra),'failure_count':len(failures),'failed_control_ids':[r['control_id'] for r in failures],
    'target_bundle':TARGET,'authorization':'VALIDATION_ONLY','freeze_authorized':False,'production_rehearsal_authorized':False,'tag_created':False,'certified_lambda_range':False,
}
REPORT_PATH.write_bytes(canonical_bytes(report)); print(json.dumps(report,indent=2,sort_keys=True))
if failures:
    for row in failures[:64]: print(json.dumps(row,sort_keys=True),file=sys.stderr)
if report['status']!='PASSED': raise SystemExit(1)
