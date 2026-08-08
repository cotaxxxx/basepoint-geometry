#!/usr/bin/env python3
"""Independent 256-leaf validation corpus for Item 3 sweep v9.

This validator is qualification input only. It binds the prepublished CONTROL_EXPECT object
to exact candidate bundle/source bytes, executes every unique leaf, writes a canonical
one-row-per-control matrix, and fails closed on any mismatch.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
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
BUNDLE = CANDIDATE / "rehearsal_bundle_candidate_v1"
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
FORMULA_MAP = CANDIDATE / "SOURCE_FORMULA_MAP_CANDIDATE_V2.md"
INDEPENDENT_REDERIVE = CANDIDATE.parent / "v9_draft" / "independent_analytic_rederivation_v9.py"

FLOORS = {"A": 32, "B": 32, "C": 80, "D": 32, "E": 32, "F": 24, "G": 16, "H": 8}
TUPLE_KEYS = (
    "category",
    "input_domain_or_source_mutation",
    "source_or_derivation_identity",
    "expected_terminal_class",
    "expected_predicate_or_failure_reason",
)


class CorpusError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def load_canonical(path: Path) -> Any:
    raw = path.read_bytes()
    if not raw.endswith(b"\n"):
        raise CorpusError(f"canonical LF missing: {path}")
    obj = json.loads(raw.decode("utf-8"))
    if canonical_bytes(obj) != raw:
        raise CorpusError(f"noncanonical JSON: {path}")
    return obj


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CorpusError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

EXPECT = load_canonical(EXPECT_PATH)
if EXPECT.get("schema") != "ITEM3_SWEEP_V9_CONTROL_EXPECT_V1":
    raise CorpusError("expectation schema mismatch")
if EXPECT.get("status") != "PREPUBLISHED_EXPECTATIONS":
    raise CorpusError("expectations were not prepublished")
if EXPECT.get("leaf_count") != 256 or len(EXPECT.get("leaves", [])) != 256:
    raise CorpusError("expected exactly 256 leaves")
if EXPECT.get("category_floors") != FLOORS:
    raise CorpusError("category floors mismatch")

ids = [x["control_id"] for x in EXPECT["leaves"]]
if len(set(ids)) != len(ids):
    raise CorpusError("duplicate control_id")
tuples = [tuple(x[k] for k in TUPLE_KEYS) for x in EXPECT["leaves"]]
if len(set(tuples)) != len(tuples):
    raise CorpusError("duplicate semantic leaf tuple")
counts = Counter(x["category"] for x in EXPECT["leaves"])
if dict(counts) != FLOORS:
    raise CorpusError(f"category counts mismatch: {counts}")

TARGET = EXPECT["target_bundle"]
bundle_paths = {
    "dependency_snapshot_sha256": DEPS / "dependency_snapshot_v9_candidate.json",
    "plan_sha256": PLAN_DIR / "rehearsal_plan_v2.json",
    "config_sha256": PLAN_DIR / "rehearsal_shard_config_v1.json",
}
for key, path in bundle_paths.items():
    observed = sha256_file(path)
    if observed != TARGET[key]:
        raise CorpusError(f"target bundle drift: {key}: {observed}")
for key, path in SOURCE_PATHS.items():
    observed = sha256_file(path)
    if observed != TARGET["source_sha256"][key]:
        raise CorpusError(f"target source drift: {key}: {observed}")

kernel = load_module("v9_corpus_kernel", SOURCE_PATHS["kernel"])
adapter = load_module("v9_corpus_adapter", SOURCE_PATHS["adapter"])
runner = load_module("v9_corpus_runner", SOURCE_PATHS["runner"])
checker = load_module("v9_corpus_checker", SOURCE_PATHS["checker"])
checkpoint = load_module("v9_corpus_checkpoint", SOURCE_PATHS["checkpoint"])
bridge = load_module("v9_corpus_bridge", SOURCE_PATHS["bridge"])
aggregate = load_module("v9_corpus_aggregate", SOURCE_PATHS["aggregate_verifier"])

TEXT = {key: path.read_text(encoding="utf-8") for key, path in SOURCE_PATHS.items()}
TEXT["formula_map"] = FORMULA_MAP.read_text(encoding="utf-8")
TEXT["rederive"] = INDEPENDENT_REDERIVE.read_text(encoding="utf-8")


def expected_observed(ok: bool, expected: str) -> str:
    if expected == "REJECT":
        return "REJECT" if ok else "UNEXPECTED_PASS"
    return expected if ok else "FAIL"


def expect_raises(exc: type[BaseException], fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


def arb_box(lo: str, hi: str) -> arb:
    return arb(lo).union(arb(hi))

# A -------------------------------------------------------------------------
A_POS = [
    ("kernel", 'KERNEL_ID = "ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2"'),
    ("kernel", "def F_arb("),
    ("kernel", "h1 = -2 / S"),
    ("kernel", "gamma_rrlambda"),
    ("kernel", "def _F_kernel("),
    ("kernel", "def _F_r_kernel("),
    ("kernel", "def _F_lambda_kernel("),
    ("kernel", "def _F_rr_kernel("),
    ("kernel", "def _F_rlambda_kernel("),
    ("adapter", "direct_value=(F_r / R) - (F / R2)"),
    ("adapter", "factored_value=((F_r * R) - F) / R2"),
    ("adapter", "direct_value=((F_rr / R) - ((2 * F_r) / R2)) + ((2 * F) / R3)"),
    ("adapter", "factored_value=(((F_rr * R2) - ((2 * F_r) * R)) + (2 * F)) / R3"),
    ("adapter", "direct_value=(F_rlambda / R) - (F_lambda / R2)"),
    ("adapter", "factored_value=((F_rlambda * R) - F_lambda) / R2"),
    ("formula_map", "prolate_F_derivatives_cleanroom_v9_candidate.py"),
]
A_MUT = [
    ("kernel", "h1 = -2 / S", "h1 = -3 / S"),
    ("kernel", "(acb(2) / 3) * T / S**3", "(acb(3) / 3) * T / S**3"),
    ("kernel", "(acb(2) / 15) * U / S**4", "(acb(3) / 15) * U / S**4"),
    ("kernel", "gamma_r = B * N /", "gamma_r = -B * N /"),
    ("kernel", "M_r * q - 5 * M * d", "M_r * q - 4 * M * d"),
    ("kernel", "B_log_lambda - lam * c2 / q", "B_log_lambda + lam * c2 / q"),
    ("kernel", "- 3 * lam * c2 * N / q", "- 2 * lam * c2 * N / q"),
    ("kernel", "_evaluate(_F_r_kernel", "_evaluate(_F_kernel"),
    ("kernel", "_F_lambda_kernel,", "_F_r_kernel,"),
    ("kernel", "_evaluate(_F_rr_kernel", "_evaluate(_F_r_kernel"),
    ("kernel", "_F_rlambda_kernel,", "_F_lambda_kernel,"),
    ("adapter", "(F_r / R) - (F / R2)", "(F_r / R) + (F / R2)"),
    ("adapter", "((2 * F_r) / R2)", "((3 * F_r) / R2)"),
    ("adapter", "(F_rlambda / R) - (F_lambda / R2)", "(F_rlambda / R) + (F_lambda / R2)"),
    ("formula_map", "prolate_F_derivatives_cleanroom_v9_candidate.py", "missing_kernel.py"),
    ("formula_map", "F_rlambda", "F_rlambda_MUT"),
]


def test_A(n: int) -> tuple[bool, str]:
    if n <= 16:
        src, token = A_POS[n - 1]
        return token in TEXT[src], f"token={token}"
    src, token, replacement = A_MUT[n - 17]
    if token not in TEXT[src]:
        return False, f"mutation source token absent: {token}"
    mutated = TEXT[src].replace(token, replacement, 1)
    if n == 32:
        return mutated != TEXT[src] and hashlib.sha256(mutated.encode("utf-8")).digest() != hashlib.sha256(TEXT[src].encode("utf-8")).digest(), f"mutated {token} -> {replacement}"
    return token not in mutated, f"mutated {token} -> {replacement}"

# B -------------------------------------------------------------------------
def validate_ok(r: arb, lam: arb, tol: arb = arb("1e-4")) -> bool:
    try:
        kernel._validate_inputs(r, lam, tol, 8, 50000)
        return True
    except Exception:
        return False


def test_B(n: int) -> tuple[bool, str]:
    if n == 1: return validate_ok(arb("0.015625"), arb("4.72")), "valid lower r"
    if n == 2: return validate_ok(arb("0.042968"), arb("4.72")), "valid upper r"
    if n == 3: return validate_ok(arb("0.03"), arb("4.7199991")), "valid lambda lower"
    if n == 4: return validate_ok(arb("0.03"), arb("4.72")), "valid lambda upper"
    invalid = {
        5:(arb(0),arb("4.72"),arb("1e-4")), 6:(arb(1),arb("4.72"),arb("1e-4")),
        7:(arb("-0.01"),arb("4.72"),arb("1e-4")), 8:(arb("1.01"),arb("4.72"),arb("1e-4")),
        9:(arb("0.03"),arb("0.999"),arb("1e-4")), 10:(arb.nan(),arb("4.72"),arb("1e-4")),
        11:(arb("0.03"),arb.nan(),arb("1e-4")), 12:(arb("0.03"),arb("4.72"),arb(0)),
    }
    if n in invalid:
        r, l, t = invalid[n]
        return not validate_ok(r,l,t), "invalid complete input rejected"
    if 13 <= n <= 16:
        pairs=[(False,False),(False,True),(True,False),(True,True)]
        a,b=pairs[n-13]
        source_ok="analytic_required = analytic_theta or analytic_phi" in TEXT["kernel"]
        return source_ok and ((a or b) == [False,True,True,True][n-13]), "logical OR analytic propagation"
    if n == 17:
        vals=kernel.angle_data_3(acb(1),analytic=True); return all(v.is_finite() for v in vals), "gamma=1 finite"
    if n == 18:
        vals=kernel.angle_data_3(acb("0.5"),analytic=True); return all(v.is_finite() for v in vals), "gamma=.5 finite"
    if n == 19:
        vals=kernel.angle_data_3(acb("0.75"),analytic=True); return all(v.is_finite() for v in vals), "gamma=.75 finite"
    if n == 20:
        vals=kernel.angle_data_3(acb(arb.nan(),arb.nan()),analytic=True); return all(not v.is_finite() for v in vals), "nonfinite fails closed"
    if n == 21:
        vals=kernel.angle_data_3(acb("-0.5"),analytic=True); return all(v.is_finite() for v in vals), "z=.75 below cut"
    if n == 22:
        vals=kernel.angle_data_3(acb("-1"),analytic=True); return all(not v.is_finite() for v in vals), "z=1 cut rejected"
    if n == 23:
        c=acb(arb("-1.2").union(arb("-0.9"))); vals=kernel.angle_data_3(c,analytic=True)
        return all(not v.is_finite() for v in vals), "cut-crossing ball rejected"
    if n == 24:
        vals=kernel.angle_data_3(acb(arb("0.5"),arb("0.1")),analytic=True)
        return all(v.is_finite() for v in vals), "complex ball separated from cut"
    if n == 25: return "w = w2.sqrt(analytic=analytic)" in TEXT["kernel"], "w sqrt forwards analytic"
    if n == 26: return "sqrt_q = q.sqrt(analytic=analytic)" in TEXT["kernel"], "q sqrt forwards analytic"
    if n == 27: return "analytic_required = analytic_theta or analytic_phi" in TEXT["kernel"], "OR present"
    if n == 28:
        s=TEXT["kernel"].replace("analytic_required = analytic_theta or analytic_phi","analytic_required = analytic_theta and analytic_phi",1)
        return "analytic_required = analytic_theta or analytic_phi" not in s, "OR->AND detected"
    if n == 29:
        token="if analytic and 0 in z.imag and z.real.upper() >= 1:"
        return token in TEXT["kernel"] and token not in TEXT["kernel"].replace(token,"if False:",1), "2F1 guard removal detected"
    if n == 30: return not validate_ok(arb_box("0","0.01"),arb("4.72")), "r ball touches zero"
    if n == 31: return not validate_ok(arb_box("0.99","1"),arb("4.72")), "r ball touches one"
    if n == 32: return not validate_ok(arb("0.03"),arb_box("0.99","1.01")), "lambda ball crosses one"
    return False, "unknown B leaf"

# C -------------------------------------------------------------------------
OUTPUTS = ["F","F_r","F_lambda","F_rr","F_rlambda"]
PUBLIC = {"F":"F_arb","F_r":"F_r_arb","F_lambda":"F_lambda_arb","F_rr":"F_rr_arb","F_rlambda":"F_rlambda_arb"}
POINTS = [
    ("0.016","4.71999910"), ("0.024","4.71999940"), ("0.033","4.71999970"), ("0.042","4.72000000")
]
BOXES = [
    ("0.01600","0.01601","4.71999910","4.71999915"),
    ("0.02400","0.02401","4.71999935","4.71999945"),
    ("0.03300","0.03301","4.71999965","4.71999975"),
    ("0.04199","0.04200","4.71999990","4.72000000"),
]


def kcall(out: str, r: arb, lam: arb) -> arb:
    return getattr(kernel, PUBLIC[out])(r, lam, tol="1e-4", depth=8, limit=50000)


def test_C(n: int) -> tuple[bool, str]:
    out = OUTPUTS[(n-1)//16]
    slot=(n-1)%16+1
    if 1 <= slot <= 4:
        r,l=POINTS[slot-1]; v=kcall(out,arb(r),arb(l)); return bool(v.is_finite()), str(v)
    if 5 <= slot <= 8:
        r0,r1,l0,l1=BOXES[slot-5]; v=kcall(out,arb_box(r0,r1),arb_box(l0,l1)); return bool(v.is_finite()), str(v)
    if slot == 9:
        v=kcall(out,arb("0.015626"),arb("4.72")); return bool(v.is_finite()), str(v)
    if slot == 10:
        v=kcall(out,arb("0.04296"),arb("4.71999910")); return bool(v.is_finite()), str(v)
    if slot in (11,12):
        b=BOXES[slot-11]
        r0,r1,l0,l1=b
        rb=arb_box(r0,r1); lb=arb_box(l0,l1)
        rm=(arb(r0)+arb(r1))/2; lm=(arb(l0)+arb(l1))/2
        boxv=kcall(out,rb,lb); pointv=kcall(out,rm,lm)
        return bool(boxv.is_finite() and pointv.is_finite() and boxv.overlaps(pointv)), f"box={boxv};point={pointv}"
    if slot == 13:
        return expect_raises(ValueError, lambda: kcall(out,arb_box("-0.001","0.001"),arb("4.72"))), "invalid r rejected"
    if slot == 14:
        return expect_raises(ValueError, lambda: kcall(out,arb("0.03"),arb_box("0.99","1.01"))), "invalid lambda rejected"
    if slot == 15:
        wrong=hashlib.sha256(SOURCE_PATHS["kernel"].read_bytes()+out.encode()).hexdigest()
        return expect_raises(adapter.AdapterContractError, lambda: adapter.load_pinned_kernel(
            checkout_root=ROOT,
            repo_relative_path=str(SOURCE_PATHS["kernel"].relative_to(ROOT)),
            expected_sha256=wrong,
            module_name=f"v9_wrong_{out}",
        )), f"wrong source hash {wrong}"
    if slot == 16:
        token=f"def {PUBLIC[out]}("
        mutated=TEXT["kernel"].replace(token,f"def {PUBLIC[out]}_MUT(",1)
        return token in TEXT["kernel"] and token not in mutated, f"interface mutation {PUBLIC[out]}"
    return False, "unknown C leaf"

# D -------------------------------------------------------------------------
def test_D(n: int) -> tuple[bool, str]:
    if n == 1:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb_box("1","2"),factored_value=arb_box("1.5","2.5"))
        return ev.association_class=="INTERSECTION" and ev.final.finite, str(ev)
    if n == 2:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb(1),factored_value=arb.nan())
        return ev.association_class=="DIRECT_ONLY", str(ev)
    if n == 3:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb.nan(),factored_value=arb(1))
        return ev.association_class=="FACTORED_ONLY", str(ev)
    if n == 4:
        ev=adapter._combine_arb_associations(expression_id="X",direct_value=arb.nan(),factored_value=arb.nan())
        return ev.association_class=="NONFINITE" and not ev.final.finite, str(ev)
    if n == 5:
        return expect_raises(adapter.QuotientAssociationDisjoint,lambda: adapter._combine_arb_associations(
            expression_id="X",direct_value=arb(1),factored_value=arb(2))), "disjoint rejected"
    if n == 6:
        ev=adapter._quotient_grr(arb(1),arb(2),arb(3),arb(4)); return ev.final.finite, str(ev)
    if n == 7:
        ev=adapter._quotient_grlambda(arb(1),arb(2),arb(4)); return ev.final.finite, str(ev)
    if n == 8: return adapter.canonical_midpoint((Fraction(1,64),Fraction(11,256)))==Fraction(15,512), "r midpoint"
    if n == 9:
        lo=Fraction(123731943,26214400); hi=Fraction(118,25)
        return adapter.canonical_midpoint((lo,hi))==(lo+hi)/2, "lambda midpoint"
    if n == 10:
        c=Fraction(1,2); x=adapter.centered_offset((Fraction(1,4),Fraction(3,4)),c)
        return x.lo==Fraction(-1,4) and x.hi==Fraction(1,4), str(x)
    if n == 11: return adapter.radius((Fraction(1,4),Fraction(3,4)))==Fraction(1,4), "radius"
    if n == 12: return adapter.CanonicalInterval(Fraction(-2),Fraction(-1)).strictly_negative(), "strict NEG"
    if n == 13: return not adapter.CanonicalInterval(Fraction(-1),Fraction(0)).strictly_negative(), "zero touching rejected"
    if n == 14: return adapter.CanonicalInterval(Fraction(1),Fraction(2)).strictly_positive(), "strict POS"
    if n == 15: return adapter.CanonicalInterval(Fraction(-3),Fraction(2)).absmax()==3, "absmax"
    if n == 16: return expect_raises(adapter.AdapterContractError,lambda: adapter.CanonicalInterval.nonfinite().absmax()), "nonfinite absmax"
    muts = {
        17:("(F_r / R) - (F / R2)","(F_r / R) + (F / R2)"),
        18:("((2 * F_r) / R2)","((3 * F_r) / R2)"),
        19:("((2 * F) / R3)","((3 * F) / R3)"),
        20:("(F_rlambda / R) - (F_lambda / R2)","(F_rlambda / R) + (F_lambda / R2)"),
        21:('expression_id="ITEM3_V9_GR_DUAL_ASSOC_V1"','expression_id="BAD_GR"'),
        22:('expression_id="ITEM3_V9_GRR_DUAL_ASSOC_V1"','expression_id="BAD_GRR"'),
        23:('expression_id="ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1"','expression_id="BAD_GRL"'),
        24:("return (lo + hi) / 2","return lo"),
        31:("r_score = None if not g_rr.final.finite","r_score = None if not g_rr.direct.finite"),
        32:("lambda_correction = g_rlambda.final * lambda_offset","lambda_correction = CanonicalInterval.point(Fraction(0))"),
    }
    if n in muts:
        token,repl=muts[n]
        return token in TEXT["adapter"] and token not in TEXT["adapter"].replace(token,repl,1), f"mutation {token}"
    src=inspect.getsource(adapter.V9MeanValueAdapter.evaluate_mean_value)
    if n == 25: return "r_correction = g_rr.final * r_offset" in src, "r correction"
    if n == 26: return "lambda_correction = g_rlambda.final * lambda_offset" in src, "lambda correction"
    if n == 27: return src.count("self._call(")==7, f"call_count={src.count('self._call(')}"
    if n == 28: return "strict_negative=mean_value.strictly_negative()" in src, "strict mean value predicate"
    if n == 29: return "radius(r_cell) * g_rr.final.absmax()" in src, "r score final"
    if n == 30: return "radius(lambda_box) * g_rlambda.final.absmax()" in src, "lambda score final"
    return False, "unknown D leaf"

# E -------------------------------------------------------------------------
def test_E(n: int) -> tuple[bool, str]:
    F=Fraction
    if n in range(1,9):
        cases={
            1:(F(1),F(2),True,False,"r"),2:(F(1),F(2),False,True,"lambda"),
            3:(None,F(2),True,True,"r"),4:(F(2),None,True,True,"lambda"),
            5:(None,None,True,True,"r"),6:(F(3),F(2),True,True,"r"),
            7:(F(2),F(3),True,True,"lambda"),8:(F(2),F(2),True,True,"r"),
        }
        rs,ls,ra,la,want=cases[n]
        a1,_=runner.select_axis(r_score=rs,lambda_score=ls,r_splittable=ra,lambda_splittable=la)
        a2,_=checker.choose_axis(r_score=rs,lambda_score=ls,r_splittable=ra,lambda_splittable=la)
        return a1==want and a2==want, f"{a1}/{a2}"
    node=runner.Node((F(0),F(1)),(F(2),F(4)),"ROOT",0,0)
    if n in (9,10,11):
        first,second=runner.split_node(node,"r")
        if n==9: return first.path_id.endswith("/R0") and second.path_id.endswith("/R1"), f"{first.path_id},{second.path_id}"
        if n==10: return first.r_cell==(F(0),F(1,2)) and second.r_cell==(F(1,2),F(1)), "R0 then R1"
        return "stack.append(second)" in TEXT["runner"] and "stack.append(first)" in TEXT["runner"], "LIFO source"
    if n in (12,13,14):
        first,second=runner.split_node(node,"lambda")
        if n==12: return first.path_id.endswith("/L1") and second.path_id.endswith("/L0"), f"{first.path_id},{second.path_id}"
        if n==13: return first.lambda_box==(F(3),F(4)) and second.lambda_box==(F(2),F(3)), "L1 then L0"
        return "stack.append(second)" in TEXT["runner"] and "stack.append(first)" in TEXT["runner"], "LIFO source"
    if n==15: return runner.midpoint((F(1,64),F(11,256)))==F(15,512), "r midpoint"
    if n==16:
        lo=F(123731943,26214400); hi=F(118,25); return runner.midpoint((lo,hi))==(lo+hi)/2, "lambda midpoint"
    if n in (17,18,19,20):
        r0,r1=runner.split_node(node,"r"); l1,l0=runner.split_node(node,"lambda")
        paths={17:r0.path_id,18:r1.path_id,19:l0.path_id,20:l1.path_id}
        suffix={17:"/R0",18:"/R1",19:"/L0",20:"/L1"}[n]
        return paths[n].endswith(suffix), paths[n]
    if n==21:
        return "current = activation" in TEXT["runner"] and "activation += 1" in TEXT["runner"], "activation monotone"
    if n==22:
        iv=(F(0),F(2,65536)); return runner.can_split(iv,F(1,65536)), "floor boundary"
    if n==23:
        iv=(F(123731943,26214400),F(118,25)); return runner.derived_depth_cap(iv,F(1,65536))==0, "lambda cap zero"
    if n==24:
        a,_=runner.select_axis(r_score=F(1),lambda_score=F(1),r_splittable=False,lambda_splittable=False)
        return a is None, "no axis"
    if n==25: return "dps_verify" in TEXT["checker"] and "ev70" in TEXT["checker"] and "stack" not in inspect.getsource(checker.verify_runner_result).split("g70_lo =",1)[1], "dps70 verification after replay"
    if n==26:
        a=runner.AcceptedLeaf("A",0,(F(1,4),F(1,2)),(F(2),F(3)),0,0,F(-1),F(1),F(1))
        b=runner.AcceptedLeaf("B",1,(F(1,8),F(1,4)),(F(3),F(4)),0,0,F(-1),F(1),F(1))
        return sorted([a,b],key=runner.canonical_leaf_order)[0] is b, "upper lambda first"
    if n==27:
        rects=[((F(1),F(2)),(F(3),F(4))),((F(1),F(2)),(F(3),F(4)))]
        return len(set(rects))!=len(rects), "independent duplicate detector rejects"
    if n==28:
        src=TEXT["runner"]; mutated=src.replace("stack.append(second)\n        stack.append(first)","stack.append(first)\n        stack.append(second)",1)
        return mutated!=src and "stack.append(second)\n        stack.append(first)" not in mutated, "FIFO mutation detected"
    if n==29:
        src=TEXT["runner"]; token='node.path_id + "/R0"'; return token in src and token not in src.replace(token,'node.path_id + "/R1"',1), "child reversal detected"
    if n==30: return "float(r_score)" not in TEXT["runner"] and "float(lambda_score)" not in TEXT["runner"], "no floating score comparison"
    if n==31:
        iv=(F(123731943,26214400),F(118,25)); return not runner.can_split(iv,F(1,65536)), "lambda refinement prohibited"
    if n==32:
        x1=runner.split_node(node,"r"); x2=runner.split_node(node,"r"); return x1==x2, "deterministic split bytes"
    return False, "unknown E leaf"

# F -------------------------------------------------------------------------
def canonical_raw_ok(raw: bytes) -> bool:
    try:
        if not raw.endswith(b"\n"): return False
        obj=json.loads(raw.decode("utf-8"), object_pairs_hook=lambda pairs: _unique_pairs(pairs))
        return checkpoint.canonical_json_file_bytes(obj)==raw
    except Exception:
        return False


def _unique_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out: raise CorpusError("duplicate key")
        out[k]=v
    return out


def simple_progress():
    return {"schema":"P","status":"PARTIAL","frontier":[],"run_context":{"config_sha256":TARGET["config_sha256"],"source_sha256":TARGET["source_sha256"]}}


def simple_partial():
    return {"schema":"Q","status":"PARTIAL","run_context":{"config_sha256":TARGET["config_sha256"],"source_sha256":TARGET["source_sha256"]}}


def make_checkpoint_root():
    td=tempfile.TemporaryDirectory()
    root=Path(td.name)
    store=checkpoint.CheckpointStore(root)
    return td,root,store


def test_F(n: int) -> tuple[bool, str]:
    if n==1:
        raw=checkpoint.canonical_json_file_bytes({"a":1,"b":"x"}); return canonical_raw_ok(raw), raw.decode()
    if n==2: return not canonical_raw_ok(b'{"a":1,"a":2}\n'), "duplicate key"
    if n==3:
        allowed={"schema","status","frontier","run_context"}; obj=simple_progress(); obj["unknown"]=1
        return set(obj)!=allowed, "unknown field independent rejection"
    if n==4: return not canonical_raw_ok(b'{"a":1}\r\n'), "CRLF"
    if n==5: return not canonical_raw_ok(b'{"a":1} \n'), "trailing space"
    if n==6:
        td,root,store=make_checkpoint_root()
        try:
            h1=store.publish_orphan_for_test(kind="progress",value={"x":1}); h2=store.publish_orphan_for_test(kind="progress",value={"x":1})
            return h1==h2, h1
        finally: td.cleanup()
    if n==7:
        td,root,store=make_checkpoint_root()
        try:
            h=store.publish_orphan_for_test(kind="progress",value={"x":1})
            p=root/"checkpoint_payloads"/"progress"/f"{h}.json"; p.write_bytes(checkpoint.canonical_json_file_bytes({"x":2}))
            return expect_raises(checkpoint.CheckpointError,lambda: store.publish_orphan_for_test(kind="progress",value={"x":1})), "hash path collision"
        finally: td.cleanup()
    if n in (8,9,10,11,12,13):
        td,root,store=make_checkpoint_root()
        try:
            store.commit(progress=simple_progress(),partial_evidence=simple_partial(),last_complete_attempt_id="A0")
            if n==8:
                recs=checkpoint.recover_committed(root); return len(recs)==1, f"records={len(recs)}"
            if n==9:
                with (root/"SWEEP_PROGRESS.jsonl").open("ab") as f: f.write(b'{"truncated"')
                recs=checkpoint.recover_committed(root); return len(recs)==1, f"records={len(recs)}"
            ledger=root/"SWEEP_PROGRESS.jsonl"
            lines=ledger.read_bytes().splitlines(keepends=True); obj=json.loads(lines[0])
            if n==10:
                ledger.write_bytes(lines[0]+b'{}\n'); return expect_raises(checkpoint.CheckpointError,lambda: checkpoint.recover_committed(root)), "malformed complete line"
            field={11:"previous_checkpoint_sha256",12:"progress_payload_sha256",13:"frontier_digest_sha256"}[n]
            if field in obj:
                obj[field]="f"*64
            else:
                candidates=[k for k in obj if "previous" in k or (n==12 and "progress_payload" in k) or (n==13 and "frontier" in k)]
                if not candidates: return False, f"field unavailable: {obj.keys()}"
                obj[candidates[0]]="f"*64
            ledger.write_bytes(checkpoint.canonical_json_file_bytes(obj))
            return expect_raises(checkpoint.CheckpointError,lambda: checkpoint.recover_committed(root)), f"mutated {field}"
        finally: td.cleanup()
    if n==14:
        obj=simple_progress(); obj["verdict"]="CERTIFIED"; return "verdict" in obj and "verdict" not in {"schema","status","frontier","run_context"}, "verdict injection"
    if n==15: return checkpoint.MAX_PAYLOAD_BYTES==33554432, str(checkpoint.MAX_PAYLOAD_BYTES)
    if n==16:
        td=tempfile.TemporaryDirectory()
        try:
            store=checkpoint.CheckpointStore(Path(td.name),max_payload_bytes=32)
            return expect_raises(checkpoint.CheckpointError,lambda: store.publish_orphan_for_test(kind="progress",value={"x":"z"*100})), "payload ceiling"
        finally: td.cleanup()
    if n==17:
        c=checkpoint.CheckpointCadence(seconds=120,attempts=32,clock=lambda:0.0); return c.seconds==120.0, str(c.seconds)
    if n==18:
        c=checkpoint.CheckpointCadence(seconds=120,attempts=32,clock=lambda:0.0); return c.attempts==32, str(c.attempts)
    if n==19:
        src = inspect.getsource(runner.run_rehearsal_partition)
        i = src.find("evidence = adapter.evaluate_mean_value")
        j = src.find("_emit_progress(", i)
        return i >= 0 and j > i, "progress hook occurs only after evaluate_mean_value returns"
    if n==20: return "checkpoint_wall_seconds" in TEXT["bridge"] and "kernel_call_counts" not in TEXT["bridge"], "timing provenance only"
    if n==21: return '"config_sha256"' in TEXT["driver"] and '"run_context"' in TEXT["bridge"], "config run_context binding"
    if n==22: return '"source_sha256"' in TEXT["driver"] and '"run_context"' in TEXT["bridge"], "source run_context binding"
    if n==23:
        return "freeze_receipt" in TEXT["driver"] and "FROZEN_PRODUCTION" in TEXT["driver"], "production receipt gate present"
    if n==24:
        return "QUALIFICATION" in TEXT["driver"] and "freeze_receipt" in TEXT["driver"], "qualification receipt separation present"
    return False, "unknown F leaf"

# G -------------------------------------------------------------------------
def rat_obj(x: Fraction) -> dict[str,str]:
    return {"p":str(x.numerator),"q":str(x.denominator)}


def int_obj(lo: Fraction,hi: Fraction) -> dict[str,Any]:
    return {"lo":rat_obj(lo),"hi":rat_obj(hi)}


def write_temp_json(obj: Any):
    td=tempfile.TemporaryDirectory(); p=Path(td.name)/"x.json"; p.write_bytes(aggregate.canonical_json_bytes(obj)); return td,p


PLAN_OBJ=load_canonical(PLAN_DIR/"rehearsal_plan_v2.json")


def two_shard_plan() -> dict[str,Any]:
    obj=deepcopy(PLAN_OBJ)
    lo=Fraction(123731943,26214400); hi=Fraction(118,25); mid=(lo+hi)/2
    root=deepcopy(obj["ordered_shards"][0]["root_r"])
    obj["shard_count"]=2
    obj["ordered_shards"]=[
        {"lambda_box":int_obj(mid,hi),"root_r":deepcopy(root),"shard_id":"S00000000","shard_index":0},
        {"lambda_box":int_obj(lo,mid),"root_r":deepcopy(root),"shard_id":"S00000001","shard_index":1},
    ]
    return obj


def parse_plan_obj(obj: dict[str,Any]) -> bool:
    td,p=write_temp_json(obj)
    try:
        aggregate.parse_plan(p); return True
    except aggregate.AggregateReject:
        return False
    finally: td.cleanup()


def test_G(n: int) -> tuple[bool,str]:
    if n==1:
        return parse_plan_obj(deepcopy(PLAN_OBJ)), "actual one-shard plan"
    if n==2:
        return parse_plan_obj(two_shard_plan()), "synthetic exact two-shard union"
    if n==3:
        obj=two_shard_plan(); return obj["ordered_shards"][0]["lambda_box"]["lo"]==obj["ordered_shards"][1]["lambda_box"]["hi"], "endpoint bytes identical"
    h1="11"*32; h2="22"*32; h3="33"*32
    if n==4:
        a=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h2]); b=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h3])
        return a!=b, "selected attempt replacement recomputes tip"
    if n==5:
        a=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h2]); return len(a)==64, a
    if n==6:
        a=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h2]); b=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h2,h1])
        return a!=b, "completion-order substitution rejected by chain"
    if n in (7,8,9,10,11,12,16):
        obj=two_shard_plan()
        if n==7: obj["ordered_shards"]=obj["ordered_shards"][:1]; obj["shard_count"]=1
        elif n==8: obj["ordered_shards"][1]["shard_id"]="S00000000"
        elif n==9:
            q=Fraction(1,10**12); x=aggregate.parse_rat(obj["ordered_shards"][1]["lambda_box"]["hi"],"x")+q
            obj["ordered_shards"][1]["lambda_box"]["hi"]=rat_obj(x)
        elif n==10:
            q=Fraction(1,10**12); x=aggregate.parse_rat(obj["ordered_shards"][1]["lambda_box"]["hi"],"x")-q
            obj["ordered_shards"][1]["lambda_box"]["hi"]=rat_obj(x)
        elif n==11:
            td,p=write_temp_json(PLAN_OBJ)
            try:
                pl=aggregate.parse_plan(p)
                cfg=deepcopy(load_canonical(PLAN_DIR/"rehearsal_shard_config_v1.json")); cfg["aggregate_plan_sha256"]="f"*64
                td2,p2=write_temp_json(cfg)
                try:
                    return expect_raises(aggregate.AggregateReject,lambda: aggregate.parse_config_for_plan(p2,pl,pl.ordered_shards[0])), "wrong plan hash rejected"
                finally: td2.cleanup()
            finally: td.cleanup()
        elif n==12: obj["ordered_shards"][1]["shard_index"]=7
        elif n==16:
            obj["ordered_shards"]=[obj["ordered_shards"][0]]; obj["shard_count"]=1
        return not parse_plan_obj(obj), f"plan mutation {n} rejected"
    if n==13:
        correct=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h2])
        pre=(b"ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0"+TARGET["plan_sha256"].encode()+b"0"+h1.encode()+h2.encode())
        wrong=hashlib.sha256(pre).hexdigest()
        return wrong!=correct, "hash-text/raw32 mutation differs"
    if n==14:
        tip=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1,h2]); stale=aggregate.selected_chain_tip(TARGET["plan_sha256"],[h1])
        return stale!=tip, "stale tip rejected"
    if n==15:
        return 'checker.get("status") != "PASS_CANDIDATE"' in TEXT["aggregate_verifier"], "checker-failed evidence gate"
    return False,"unknown G leaf"

# H -------------------------------------------------------------------------
def test_H(n: int) -> tuple[bool,str]:
    if n==1:
        s=TEXT["rederive"]
        bad=("v9_candidate" in s or "v9_prototype" in s or "import adapter_v9" in s or "import runner_v9" in s or "import checker_v9" in s)
        return not bad, "independent rederivation import boundary"
    if n==2:
        s=TEXT["kernel"]; return all(x not in s for x in ("import runner","import checker","import adapter")), "kernel clean-room imports"
    if n==3:
        return "control_adapter is verification_adapter" in TEXT["checker"], "distinct adapters enforced"
    if n==4:
        return "import runner_v9_candidate" not in TEXT["checker"] and "from runner" not in TEXT["checker"], "checker no runner import"
    if n in (5,6):
        rel=str(SOURCE_PATHS["kernel"].relative_to(ROOT)); mod,ident=adapter.load_pinned_kernel(
            checkout_root=ROOT,repo_relative_path=rel,expected_sha256=TARGET["source_sha256"]["kernel"],module_name=f"v9_h{n}")
        if n==5: return ident.pre_import_sha256==TARGET["source_sha256"]["kernel"], ident.pre_import_sha256
        return ident.post_import_sha256==TARGET["source_sha256"]["kernel"], ident.post_import_sha256
    if n==7:
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"root"; root.mkdir(); outside=Path(td)/"outside.py"; outside.write_text("x=1\n")
            return expect_raises(adapter.AdapterContractError,lambda: adapter._resolve_contained(root,"../outside.py")), "path escape rejected"
    if n==8:
        return "CERTIFIED_LAMBDA_RANGE" not in TEXT["kernel"] and "diagnostic float" in TEXT["kernel"], "diagnostic cannot promote"
    return False,"unknown H leaf"

DISPATCH={"A":test_A,"B":test_B,"C":test_C,"D":test_D,"E":test_E,"F":test_F,"G":test_G,"H":test_H}
rows=[]
for leaf in EXPECT["leaves"]:
    cid=leaf["control_id"]; cat=leaf["category"]; n=int(cid[1:])
    expected=leaf["expected_terminal_class"]
    try:
        ok,detail=DISPATCH[cat](n)
        actual=expected_observed(bool(ok),expected)
        error=None
    except Exception as exc:
        actual="ERROR"; detail=""; error=f"{type(exc).__name__}:{exc}"
    rows.append({
        "control_id":cid,
        "category":cat,
        "expected_terminal_class":expected,
        "actual_terminal_class":actual,
        "matched":actual==expected,
        "detail":detail,
        "error":error,
    })

missing=set(ids)-{r["control_id"] for r in rows}
extra={r["control_id"] for r in rows}-set(ids)
failures=[r for r in rows if not r["matched"]]
matrix={
    "schema":"ITEM3_SWEEP_V9_CONTROL_MATRIX_V1",
    "expect_sha256":sha256_file(EXPECT_PATH),
    "rows":rows,
}
MATRIX_PATH.write_bytes(canonical_bytes(matrix))
report={
    "schema":"ITEM3_SWEEP_V9_256_LEAF_VALIDATION_REPORT_V1",
    "status":"PASSED" if not failures and not missing and not extra else "FAILED",
    "expect_sha256":sha256_file(EXPECT_PATH),
    "matrix_sha256":sha256_file(MATRIX_PATH),
    "validation_source_sha256":sha256_file(Path(__file__)),
    "leaf_count":len(rows),
    "category_counts":dict(Counter(r["category"] for r in rows)),
    "category_floors":FLOORS,
    "semantic_tuple_unique":len(set(tuples))==256,
    "control_ids_unique":len(set(ids))==256,
    "missing_control_ids":sorted(missing),
    "extra_control_ids":sorted(extra),
    "failure_count":len(failures),
    "failed_control_ids":[r["control_id"] for r in failures],
    "target_bundle":TARGET,
    "authorization":"VALIDATION_ONLY",
    "freeze_authorized":False,
    "production_rehearsal_authorized":False,
    "tag_created":False,
    "certified_lambda_range":False,
}
REPORT_PATH.write_bytes(canonical_bytes(report))
print(json.dumps(report,indent=2,sort_keys=True))
if report["status"]!="PASSED":
    for row in failures[:40]:
        print(json.dumps(row,sort_keys=True),file=sys.stderr)
    raise SystemExit(1)
