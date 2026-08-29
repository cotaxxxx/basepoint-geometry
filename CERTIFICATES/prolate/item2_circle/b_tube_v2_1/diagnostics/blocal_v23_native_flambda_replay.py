#!/usr/bin/env python3
"""Explicit-NEG regression replay for native B-LOCAL v2.3 F_lambda.

DESIGN/DIAGNOSTIC evidence only. It does not authorize binding use.
The replay is intentionally fail-closed and compares the post-fix route with
both the pinned prior replay log and the exact prior route source at PRIOR_HEAD.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys, types
from fractions import Fraction
from pathlib import Path

ROOT=Path.home()/"basepoint-geometry-c6a45866"
BT=ROOT/"CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
V23=BT/"dependencies/blocal_v23_source"
THIS=Path(__file__).resolve()
BOUNDARY=V23/"blocal_v23_boundary.py"
KERNEL=V23/"blocal_v23_flambda_kernel.py"
PIN_FILE=V23/"BLOCAL_V23_EXPLICIT_NEG_REPLAY_PINS.json"
PRIOR_LOG=Path(os.environ.get("PRIOR_REPLAY_LOG",str(Path.home()/"blocal-v23-native-flambda-replay.log")))
PRIOR_HEAD="956ea04ba95b8f9fadfe332d0837c11f32a2d1b2"
PRIOR_LOG_SHA256="bb930ad4bda4fa9b2c9822d35b9c3001920c30610c6af9fe931b4501d53266c2"
BOUNDARY_REPO_PATH="CERTIFICATES/prolate/item2_circle/b_tube_v2_1/dependencies/blocal_v23_source/blocal_v23_boundary.py"
EXPECTED_HEAD=os.environ.get("EXPECTED_HEAD")
if not EXPECTED_HEAD: raise SystemExit("STOP: set EXPECTED_HEAD to the exact repinned replay commit")

def git(*a): return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fail(msg): raise SystemExit("STOP: "+msg)

def parse_log(path:Path):
    rows={}
    for raw in path.read_text().splitlines():
        if "=" in raw:
            k,v=raw.split("=",1); rows[k]=v
    return rows

if git("rev-parse","HEAD")!=EXPECTED_HEAD: fail("HEAD mismatch")
if git("status","--porcelain"): fail("source tree dirty")
if not PIN_FILE.exists(): fail("missing explicit-NEG replay pin file")
pins=json.loads(PIN_FILE.read_text())

actual_boundary=sha(BOUNDARY); actual_kernel=sha(KERNEL); actual_replay=sha(THIS)
print("BOUNDARY_SHA256="+actual_boundary)
print("SHARED_KERNEL_SHA256="+actual_kernel)
print("REPLAY_SCRIPT_SHA256="+actual_replay)
print("PRIOR_REPLAY_LOG_SHA256="+sha(PRIOR_LOG))
for key,actual in (("boundary_sha256",actual_boundary),("shared_kernel_sha256",actual_kernel),("replay_script_sha256",actual_replay)):
    if pins[key]!=actual: fail(key+" pin mismatch")
if pins["expected_head"]!=EXPECTED_HEAD: fail("pin-file HEAD mismatch")
if pins["prior_head"]!=PRIOR_HEAD: fail("prior HEAD pin mismatch")
if pins["prior_replay_log_sha256"]!=PRIOR_LOG_SHA256: fail("prior log contract pin mismatch")
if sha(PRIOR_LOG)!=PRIOR_LOG_SHA256: fail("prior replay log SHA mismatch")
prior_log=parse_log(PRIOR_LOG)

sys.path.insert(0,str(V23)); sys.path.insert(1,str(BT))
import blocal_v22_model as model
import blocal_arb_adapter as adapter
import blocal_v23_boundary as route
import calibration_runner
from flint import arb, acb, fmpq, ctx

cal,_=calibration_runner.load_config(); ctx.dps=cal["dps"]
raw_kernel,_=calibration_runner.load_production_kernel()
bcfg=json.loads((V23/"config.blocal-v2.2-run.json").read_text())
frag=json.loads((V23/"BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
bcfg["route_policies"].update(frag["route_policies"])

# Load the exact prior route source without checking out or mutating the tree.
prior_source=subprocess.check_output(["git","-C",str(ROOT),"show",f"{PRIOR_HEAD}:{BOUNDARY_REPO_PATH}"],text=True)
prior_mod=types.ModuleType("blocal_v23_boundary_prior")
prior_mod.__file__=f"git:{PRIOR_HEAD}:{BOUNDARY_REPO_PATH}"
exec(compile(prior_source,prior_mod.__file__,"exec"),prior_mod.__dict__)

lam0=Fraction(3307749,1600000)
cells=[(f"C{k}",lam0+Fraction(k,16),lam0+Fraction(k+1,16)) for k in range(4)]
endpoints={
 "R_HI":Fraction(77359446546029624093969931,1<<86),
 "R_LO":Fraction(74281023883021057323306507,1<<86),
}
print("EVIDENCE_CLASS=DIAGNOSTIC_NOT_BINDING")
print("NATIVE_ROUTE_ID="+route.FLAMBDA_ROUTE_ID)
print("PRODUCER_DPS="+str(cal["dps"]))
print("CELL_CAP=24000")
print("REQUIRED_SIGN_INPUT=EXPLICIT_NEG")
print("REGRESSION_EXPECTATION=BIT_IDENTICAL_TO_PRIOR_NATIVE_REPLAY")
print("BINDING_USE_AUTHORIZED=NO")

total=0
for side,r in endpoints.items():
    u=Fraction(1)-r
    for label,llo,lhi in cells:
        s0=llo-model.LAMBDA_PLUS; s1=lhi-model.LAMBDA_PLUS
        prior_iv,prior_proof=prior_mod.enclose_route("F_lambda",raw_kernel,adapter,acb,arb,fmpq,bcfg,u,u,s0,s1,
                                                    required_sign="NEG",accept=None,evaluation_cap=24000)
        iv,proof=route.enclose_route("F_lambda",raw_kernel,adapter,acb,arb,fmpq,bcfg,u,u,s0,s1,
                                     required_sign="NEG",accept=None,evaluation_cap=24000)
        lo,hi=model.interval_fractions(iv,f"{side}/{label}")
        ev=proof["evaluation_count"]; total+=ev; prefix=f"{side}_{label}"
        print(f"{prefix}_LAMBDA_LO={llo}")
        print(f"{prefix}_LAMBDA_HI={lhi}")
        print(f"{prefix}_LO={lo}")
        print(f"{prefix}_HI={hi}")
        print(f"{prefix}_EVAL={ev}")
        print(f"{prefix}_COVER={str(proof['complete_closed_cover']).upper()}")
        print(f"{prefix}_ROUTE_ID={proof['route_id']}")
        print(f"{prefix}_MONKEYPATCH_USED={str(proof['monkeypatch_used']).upper()}")
        enclosure_match=(iv==prior_iv)
        eval_match=(proof["evaluation_count"]==prior_proof["evaluation_count"])
        tree_match=(proof["ordered_children"]==prior_proof["ordered_children"] and proof["split_reasons"]==prior_proof["split_reasons"])
        log_match=(prior_log.get(prefix+"_LO")==str(lo) and prior_log.get(prefix+"_HI")==str(hi)
                   and prior_log.get(prefix+"_EVAL")==str(ev) and prior_log.get(prefix+"_COVER")=="TRUE"
                   and prior_log.get(prefix+"_ROUTE_ID")=="BLOCAL_FLAMBDA_ROUTE_V1"
                   and prior_log.get(prefix+"_MONKEYPATCH_USED")=="FALSE")
        print(f"{prefix}_PRIOR_ENCLOSURE_BIT_MATCH={str(enclosure_match).upper()}")
        print(f"{prefix}_PRIOR_EVAL_MATCH={str(eval_match).upper()}")
        print(f"{prefix}_PRIOR_COVER_TREE_MATCH={str(tree_match).upper()}")
        print(f"{prefix}_PRIOR_LOG_MATCH={str(log_match).upper()}")
        if not (hi<0 and proof["complete_closed_cover"] and proof["route_id"]=="BLOCAL_FLAMBDA_ROUTE_V1"
                and proof["quantity"]=="F_lambda" and proof["required_sign"]=="NEG"
                and proof["monkeypatch_used"] is False and ev<=24000
                and enclosure_match and eval_match and tree_match and log_match):
            raise SystemExit(f"FAIL_EXPLICIT_NEG_REGRESSION:{side}:{label}")

# Contract negative controls: failure code strings are part of the audit surface.
u=Fraction(1)-endpoints["R_HI"]; s=lam0-model.LAMBDA_PLUS

def expect_code(name,code,**kw):
    try:
        route.enclose_route("F_lambda",raw_kernel,adapter,acb,arb,fmpq,bcfg,u,u,s,s,evaluation_cap=24000,**kw)
    except route.ContractFailure as exc:
        print(f"{name}_EXPECTED={code}")
        print(f"{name}_ACTUAL={exc.code}")
        print(f"{name}_PASS={str(exc.code==code).upper()}")
        if exc.code!=code: raise SystemExit(f"FAIL_NEGATIVE_CONTROL:{name}:{exc.code}")
        return
    raise SystemExit(f"FAIL_NEGATIVE_CONTROL_NO_FAILURE:{name}")

expect_code("NC32_REQUIRED_SIGN_MISSING","FAIL_REQUIRED_SIGN_MISSING",required_sign=None,accept=None)
expect_code("NC10_WRONG_SIGN_REQUEST","FAIL_SIGN_CONTRACT",required_sign="POS",accept=None)
expect_code("NC_CUSTOM_ACCEPT","FAIL_CUSTOM_PREDICATE_FORBIDDEN",required_sign="NEG",accept=lambda _: True)

print("TOTAL_NATIVE_FLAMBDA_CELL_EVAL="+str(total))
print("ALL_8_NATIVE_FLAMBDA_CELLS=FINITE_NEG")
print("ALL_8_PRIOR_ENCLOSURE_BIT_MATCH=TRUE")
print("ALL_8_PRIOR_EVAL_MATCH=TRUE")
print("ALL_8_PRIOR_COVER_TREE_MATCH=TRUE")
print("ALL_8_PRIOR_LOG_MATCH=TRUE")
print("NC32_REQUIRED_SIGN_MISSING=PASS")
print("NC10_WRONG_SIGN_REQUEST=PASS")
print("NC_CUSTOM_ACCEPT=PASS")
print("EXPLICIT_NEG_REGRESSION_REPLAY=PASS")
print("BINDING_USE_AUTHORIZED=NO")
if git("rev-parse","HEAD")!=EXPECTED_HEAD or git("status","--porcelain"):
    fail("post-run source state changed")
print("POST_HEAD_UNCHANGED=TRUE")
print("SOURCE_TREE_POST=CLEAN")
