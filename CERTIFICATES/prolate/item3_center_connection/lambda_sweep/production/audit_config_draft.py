#!/usr/bin/env python3
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def cb(o): return json.dumps(o,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')

def canonical(name):
    p=HERE/name; raw=p.read_bytes(); obj=json.loads(raw)
    if cb(obj)!=raw: raise SystemExit(f'noncanonical: {name}')
    return obj,raw

D,draw=canonical('CONFIG_DECISIONS.candidate.json')
S,sraw=canonical('dependency_snapshot.candidate.json')
R,rraw=canonical('pilot_identity_receipt.candidate.json')
ast.parse((HERE/'materialize_config.py').read_text(),filename='materialize_config.py')
required={'L-CONT','L-DERIV','L-ENCL','L-SIGN','L-IVT'}
checks={
 'decision_status_hold':D['status']=='REQUIRES_USER_APPROVAL_AND_SOURCE_BINDING',
 'target_is_anchor_minus_2^-12':D['lambda_target']=={'p':'483303','q':'102400'},
 'target_requires_approval':D['lambda_target_approval_required'] is True,
 'pilot_run_id':S['pilot_run_id']==R['run_id']==30334858060,
 'pilot_source_relation':S['pilot_source_sha256']==R['pilot_source_sha256']=='9da05b2c44119c9937c19a2184ea9722de7876442235896f1f0e0dbc076f2ecc',
 'pilot_kernel_relation':S['pilot_kernel_source_sha256']==R['pilot_kernel_source_sha256']=='77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac',
 'snapshot_relation':hashlib.sha256(sraw).hexdigest()==R['dependency_snapshot_sha256']==D['dependency_snapshot_sha256'],
 'receipt_relation':hashlib.sha256(rraw).hexdigest()==D['pilot_identity_receipt_sha256'],
 'root_endpoint_bytes':S['certified_root_interval']['lower_endpoint']=={'p':'1','q':'64'} and S['certified_root_interval']['upper_endpoint']=={'p':'11','q':'256'},
 'logical_key_set':set(S['logical_dependencies'])==required==set(D['sweep_logical_dependencies']),
 'logical_hashes':all(hashlib.sha256(cb(S['logical_dependencies'][k])).hexdigest()==D['sweep_logical_dependencies'][k]['dependency_entry_sha256'] for k in required),
 'run_withheld':D['run_authorized'] is False and D['tag_created'] is False and D['workflow_executed'] is False,
 'source_binding_hold':D['adapter_binding']=='PHASE3_PROTOCOL_ONLY_NOT_PRODUCTION_EXECUTABLE' and D['production_entrypoint_status']=='MISSING',
 'runtime_hold':D['phase4_runtime_dependency_status']=='PYTHON_FLINT_INSTALL_STEP_ABSENT',
}
fail=[k for k,v in checks.items() if not v]
report={'schema':'ITEM3_SWEEP_PRODUCTION_CONFIG_DRAFT_AUDIT_V1','checks':checks,'failure_count':len(fail),'failures':fail,'kernel_evaluations':0,'mathematical_calculations':0,'verdict':'PASS' if not fail else 'FAIL'}
raw=cb(report)
(HERE/'CONFIG_DRAFT_STATIC_AUDIT.json').write_bytes(raw)
print(raw.decode())
raise SystemExit(0 if not fail else 1)
