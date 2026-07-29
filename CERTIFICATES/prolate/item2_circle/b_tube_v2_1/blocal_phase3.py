#!/usr/bin/env python3
"""B-LOCAL/B-ENTRY Phase-3 entry point.

Status: CHAT_SIDE_AUDIT_WAITING. No production kernel, archive creation, tag,
workflow, or mathematical run is authorized.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from numeric_schema import CanonicalBytesError, SchemaError, parse_canonical_json_bytes
from blocal_phase3_contract import cbytes, audit_stage1, verify_run
from blocal_phase3_controls import CONTROL_MAP, EXTRA
from blocal_phase3_selftest import selftest

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
    s.add_parser("selftest")
    v=s.add_parser("verify-run"); v.add_argument("--config",type=Path,required=True); v.add_argument("--records",type=Path,required=True); v.add_argument("--certificate",type=Path)
    a=s.add_parser("audit-stage1"); a.add_argument("--plan",type=Path,required=True)
    s.add_parser("control-map"); z=p.parse_args()
    if z.cmd=="selftest": out=selftest()
    elif z.cmd=="verify-run":
        out=verify_run(z.config.read_bytes(),z.records.read_bytes(),z.certificate.read_bytes() if z.certificate else None); out["status"]="CHAT_SIDE_AUDIT_WAITING"
    elif z.cmd=="audit-stage1":
        out=audit_stage1(parse_canonical_json_bytes(z.plan.read_bytes(),allow_display=False)); out["status"]="CHAT_SIDE_AUDIT_WAITING"
    else: out={"mapping":CONTROL_MAP,"extension":EXTRA,"status":"CHAT_SIDE_AUDIT_WAITING"}
    print(cbytes(out).decode("ascii"))

if __name__=="__main__":
    try: main()
    except (RuntimeError,CanonicalBytesError,SchemaError,OSError,KeyError,ValueError,json.JSONDecodeError) as e:
        print(f"BLOCAL ERROR: {e}"); raise SystemExit(2)
