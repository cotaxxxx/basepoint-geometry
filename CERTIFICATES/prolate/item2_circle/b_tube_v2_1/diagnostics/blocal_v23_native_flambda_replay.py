#!/usr/bin/env python3
"""Source-untouched diagnostic replay of native B-LOCAL v2.3 F_lambda.

This is DESIGN/DIAGNOSTIC evidence only. It does not authorize binding use.
"""
from __future__ import annotations
import hashlib, json, os, subprocess, sys
from fractions import Fraction
from pathlib import Path

ROOT=Path.home()/"basepoint-geometry-c6a45866"
BT=ROOT/"CERTIFICATES/prolate/item2_circle/b_tube_v2_1"
V23=BT/"dependencies/blocal_v23_source"
EXPECTED_HEAD=os.environ.get("EXPECTED_HEAD")
if not EXPECTED_HEAD: raise SystemExit("STOP: set EXPECTED_HEAD to the exact v2.3 replay commit")

def git(*a): return subprocess.check_output(["git","-C",str(ROOT),*a],text=True).strip()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if git("rev-parse","HEAD")!=EXPECTED_HEAD: raise SystemExit("STOP: HEAD mismatch")
if git("status","--porcelain"): raise SystemExit("STOP: source tree dirty")
manifest=json.loads((V23/"BLOCAL_V23_SOURCE_MANIFEST.json").read_text())
for key,name in (("boundary_sha256","blocal_v23_boundary.py"),("shared_kernel_sha256","blocal_v23_flambda_kernel.py")):
    want=manifest["native_route"][key]; got=sha(V23/name); print(f"{key.upper()}={got}")
    if got!=want: raise SystemExit("STOP: v2.3 source pin mismatch")

sys.path.insert(0,str(V23)); sys.path.insert(1,str(BT))
import blocal_v22_model as model
import blocal_arb_adapter as adapter
import blocal_v23_boundary as route
import calibration_runner
from flint import arb, acb, fmpq, ctx

cal,_=calibration_runner.load_config(); ctx.dps=cal["dps"]
raw_kernel,kernel_path=calibration_runner.load_production_kernel()
bcfg=json.loads((V23/"config.blocal-v2.2-run.json").read_text())
frag=json.loads((V23/"BLOCAL_V23_ROUTE_CONFIG.fragment.json").read_text())
bcfg["route_policies"].update(frag["route_policies"])

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
print("MIN_PRIOR_DIAGNOSTIC_MARGIN_APPROX=8.25654442933e-5")
print("PROOF_DIRECTION=LAMBDA_ADDITIVE_TRANSPORT")
print("BINDING_USE_AUTHORIZED=NO")

total=0
for side,r in endpoints.items():
    u=Fraction(1)-r
    for label,llo,lhi in cells:
        s0=llo-model.LAMBDA_PLUS; s1=lhi-model.LAMBDA_PLUS
        iv,proof=route.enclose_route("F_lambda",raw_kernel,adapter,acb,arb,fmpq,bcfg,u,u,s0,s1,
                                     required_sign="NEG",accept=None,evaluation_cap=24000)
        lo,hi=model.interval_fractions(iv,f"{side}/{label}")
        ev=proof["evaluation_count"]; total+=ev
        print(f"{side}_{label}_LAMBDA_LO={llo}")
        print(f"{side}_{label}_LAMBDA_HI={lhi}")
        print(f"{side}_{label}_LO={lo}")
        print(f"{side}_{label}_HI={hi}")
        print(f"{side}_{label}_EVAL={ev}")
        print(f"{side}_{label}_COVER={str(proof['complete_closed_cover']).upper()}")
        print(f"{side}_{label}_ROUTE_ID={proof['route_id']}")
        print(f"{side}_{label}_MONKEYPATCH_USED={str(proof['monkeypatch_used']).upper()}")
        if not (hi<0 and proof["complete_closed_cover"] and proof["route_id"]=="BLOCAL_FLAMBDA_ROUTE_V1"
                and proof["quantity"]=="F_lambda" and proof["required_sign"]=="NEG"
                and proof["monkeypatch_used"] is False and ev<=24000):
            raise SystemExit(f"FAIL_NATIVE_FLAMBDA_REPLAY:{side}:{label}")
print("TOTAL_NATIVE_FLAMBDA_CELL_EVAL="+str(total))
print("ALL_8_NATIVE_FLAMBDA_CELLS=FINITE_NEG")
print("NATIVE_FLAMBDA_REPLAY=PASS")
print("BINDING_USE_AUTHORIZED=NO")
if git("rev-parse","HEAD")!=EXPECTED_HEAD or git("status","--porcelain"):
    raise SystemExit("STOP: post-run source state changed")
print("POST_HEAD_UNCHANGED=TRUE")
print("SOURCE_TREE_POST=CLEAN")
