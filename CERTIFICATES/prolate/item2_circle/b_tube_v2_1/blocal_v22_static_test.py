#!/usr/bin/env python3
"""Calculation-free structural audit for the B-LOCAL v2.2 implementation."""
from __future__ import annotations

import hashlib
import json
import py_compile
from pathlib import Path

import blocal_v22_model as model
import blocal_v22_symbolic_audit as symbolic

HERE=Path(__file__).resolve(strict=True).parent
ROOT=HERE.parents[3]
CONFIG=HERE/"config.blocal-v2.2-run.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(x: bool,msg: str) -> None:
    if not x: raise RuntimeError(msg)


def main() -> int:
    config=model.parse_canonical_json(CONFIG.read_bytes());model.validate_config(config)
    for rel,expected in config["implementation"]["sources_sha256"].items():
        p=ROOT/rel;need(p.is_file() and not p.is_symlink(),f"regular source {rel}")
        need(digest(p)==expected,f"source pin {rel}")
        py_compile.compile(str(p),doraise=True)
    need(digest(ROOT/config["checker"]["path"])==config["checker"]["source_sha256"],"checker pin")
    need(digest(ROOT/config["symbolic_audit"]["path"])==config["symbolic_audit"]["source_sha256"],"audit pin")
    result=symbolic.run_audit();need(result["exact_algebra"] is True,"exact symbolic audit")
    boundary=(HERE/"blocal_v22_boundary.py").read_text(encoding="utf-8")
    for forbidden in ("float(","Decimal(","1-epsilon","1 - epsilon","except Exception"):
        need(forbidden not in boundary,f"forbidden boundary token {forbidden}")
    for required in ("_z_den_lower","_bhat_lower","_integrate_duffy","_integrate_regular",
                     "gamma = _unit_interval","sin_theta_dtheta_cancelled_symbolically"):
        need(required in boundary,f"required boundary token {required}")
    runner=(HERE/"blocal_v22_runner.py").read_text(encoding="utf-8")
    need("L1_BOUNDARY_STRIP" in runner and "L1_INTERIOR" in runner,"closed split records")
    need("verify_records(records,config,config_hash)" in runner,"checker gate")
    print(json.dumps({"schema":"blocal-v22-static-audit-v1","calculation_free":True,
                      "kernel_imported":False,"kernel_evaluated":False,
                      "symbolic_audit_exact":True,"status":"CHAT_SIDE_AUDIT_WAITING"},
                     sort_keys=True,separators=(",",":")))
    return 0


if __name__=="__main__": raise SystemExit(main())
