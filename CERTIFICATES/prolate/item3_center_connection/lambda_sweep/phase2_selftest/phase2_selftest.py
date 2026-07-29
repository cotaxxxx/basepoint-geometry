#!/usr/bin/env python3
"""Calculation-free Phase 2 contract-shape self-test for item-3 lambda sweep."""
from __future__ import annotations
import argparse, base64, hashlib, json, re, zlib
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any

HERE=Path(__file__).resolve().parent
DESIGN_BLOB='cafbf7b661911995008dda49bfb3ecabcecb1f12'
DESIGN_PATH=HERE.parent/'design_contract_v8_1.md'

class Reject(ValueError):
    def __init__(self,reason,msg): super().__init__(msg); self.reason=reason

def cbytes(x):
    def walk(v):
        if isinstance(v,dict):
            for k,w in v.items():
                if not isinstance(k,str) or not k.isascii(): raise Reject('NONCANONICAL_ENCODING','non-ASCII key')
                walk(w)
        elif isinstance(v,list):
            for w in v: walk(w)
        elif isinstance(v,float): raise Reject('NONCANONICAL_ENCODING','float forbidden')
    walk(x)
    return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def pairs(items):
    d={}
    for k,v in items:
        if k in d: raise Reject('NONCANONICAL_ENCODING','duplicate key')
        d[k]=v
    return d

def parse(raw):
    if raw.startswith(b'\xef\xbb\xbf') or b'\r' in raw or b'\n' in raw: raise Reject('NONCANONICAL_ENCODING','forbidden bytes')
    try: x=json.loads(raw.decode(),object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(Reject('NONCANONICAL_ENCODING','nonfinite')))
    except Reject: raise
    except Exception as e: raise Reject('NONCANONICAL_ENCODING','invalid JSON') from e
    if cbytes(x)!=raw: raise Reject('NONCANONICAL_ENCODING','noncanonical JSON')
    return x

def parse_jsonl(raw):
    if raw.endswith(b'\n') or b'\r' in raw: raise Reject('NONCANONICAL_ENCODING','bad JSONL')
    return [parse(x) for x in raw.split(b'\n')] if raw else []

def git_blob(raw): return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
def sha(raw): return hashlib.sha256(raw).hexdigest()

def unpack_all():
    manifest=parse((HERE/'PACK_MANIFEST.json').read_bytes()); out={}
    for name,m in manifest.items():
        packed=(HERE/m['pack_file']).read_bytes()
        if sha(packed)!=m['packed_sha256'] or len(packed)!=m['packed_size']: raise RuntimeError('packed fixture mismatch '+name)
        raw=zlib.decompress(base64.b85decode(packed))
        if sha(raw)!=m['canonical_json_sha256'] or len(raw)!=m['canonical_json_size']: raise RuntimeError('fixture hash mismatch '+name)
        out[name]=parse(raw)
    return out,manifest

def istr(v,where):
    if not isinstance(v,str) or not re.fullmatch(r'0|-?[1-9][0-9]*',v): raise Reject('NONCANONICAL_ENCODING',where)
    return int(v)
def rat(v,where):
    if not isinstance(v,dict) or set(v)!={'p','q'}: raise Reject('SCHEMA_VIOLATION',where)
    p,q=istr(v['p'],where+'.p'),istr(v['q'],where+'.q')
    if q<=0 or Fraction(p,q)!=(p/q if False else Fraction(p,q)) or Fraction(p,q).numerator!=p or Fraction(p,q).denominator!=q: raise Reject('NONCANONICAL_ENCODING',where)
    return Fraction(p,q)
def dy(v,where):
    if not isinstance(v,dict) or set(v)!={'m','e'}: raise Reject('SCHEMA_VIOLATION',where)
    m,e=istr(v['m'],where+'.m'),v['e']
    if not isinstance(e,int) or isinstance(e,bool) or e<0 or (m==0 and e!=0) or (m and e and m%2==0): raise Reject('NONCANONICAL_ENCODING',where)
    return Fraction(m,1<<e)

def path(v,where,escapes):
    if not isinstance(v,str) or not v or '\\' in v or v.startswith('/') or v.endswith('/') or '//' in v: raise Reject('SCHEMA_VIOLATION',where)
    if any(x in {'','.','..'} for x in v.split('/')) or str(PurePosixPath(v))!=v: raise Reject('SCHEMA_VIOLATION',where)
    if any(v==p or v.startswith(p+'/') for p in escapes): raise Reject('SCHEMA_VIOLATION',where)

def validate_config(c,schema,escapes=()):
    if not isinstance(c,dict) or set(c)!=set(schema['required']): raise Reject('SCHEMA_VIOLATION','closed top-level')
    a,t=rat(c['lambda_anchor'],'anchor'),rat(c['lambda_target'],'target')
    if a!=Fraction(118,25) or not Fraction(1)<=t<a: raise Reject('SCHEMA_VIOLATION','lambda gate')
    for n in ['min_lambda_width_exp','window_grid_exp','window_min_width_exp','max_lambda_depth']:
        if not isinstance(c[n],int) or isinstance(c[n],bool) or c[n]<0: raise Reject('SCHEMA_VIOLATION',n)
    for n in ['global_eval_limit','per_box_eval_limit','max_r_cells_per_box','dps','checker_dps']:
        if not isinstance(c[n],int) or isinstance(c[n],bool) or c[n]<=0: raise Reject('SCHEMA_VIOLATION',n)
    if c['per_box_eval_limit']>c['global_eval_limit'] or c['checker_dps']<c['dps'] or c['cg_pilot_run_id']!=30334858060: raise Reject('SCHEMA_VIOLATION','cross integer gate')
    delta=rat(c['delta_overlap_min'],'delta'); g=Fraction(1,1<<c['window_grid_exp']); mw=Fraction(1,1<<c['window_min_width_exp']); lo,hi=dy(c['w0_lo'],'w0_lo'),dy(c['w0_hi'],'w0_hi')
    if delta<=0 or delta>mw or mw>1-2*g or not g<=lo<hi<=1-g or not lo<=Fraction(1,64)<=Fraction(11,256)<=hi or hi-lo<delta or hi-lo<mw: raise Reject('SCHEMA_VIOLATION','window gate')
    sh=re.compile(r'[0-9a-f]{64}'); ids=re.compile(r'[A-Za-z0-9._:-]+')
    for n in schema['required']:
        if n.endswith('sha256') and (not isinstance(c[n],str) or not sh.fullmatch(c[n])): raise Reject('SCHEMA_VIOLATION',n)
        if n.endswith('path'): path(c[n],n,set(escapes))
    if not isinstance(c['adapter_id'],str) or not ids.fullmatch(c['adapter_id']): raise Reject('SCHEMA_VIOLATION','adapter_id')
    for n,v in schema['constants'].items():
        if n!='lambda_anchor' and c[n]!=v: raise Reject('SCHEMA_VIOLATION',n)
    deps=c['sweep_logical_dependencies']; keys=set(schema['logical_dependency_keys']); fields=set(schema['logical_dependency_entry_fields'])
    if not isinstance(deps,dict) or set(deps)!=keys: raise Reject('LOGICAL_DEPENDENCY_GATE_VIOLATION','dependency keys')
    for k,e in deps.items():
        if not isinstance(e,dict) or set(e)!=fields or e['lemma_id']!=k: raise Reject('LOGICAL_DEPENDENCY_GATE_VIOLATION',k)
        if not isinstance(e['dependency_entry_sha256'],str) or not sh.fullmatch(e['dependency_entry_sha256']): raise Reject('LOGICAL_DEPENDENCY_GATE_VIOLATION',k)
        if not isinstance(e['expected_allowlist_id'],str) or not ids.fullmatch(e['expected_allowlist_id']): raise Reject('LOGICAL_DEPENDENCY_GATE_VIOLATION',k)

def regen(spec,c):
    r=c['reason']
    if r not in spec['transitions']: raise Reject('FAILURE_TRANSITION_VIOLATION','unknown reason')
    return spec['transitions'][r]['regeneration']=='YES_STAR' and c['stage']=='PRIMARY' and c['origin'] in {'CONFIG_SEED','PARENT_INHERITED'} and c['remaining']>0 and c['regenerated_count']==0

def grammar(spec,p):
    if p['path_name'] not in spec['paths'] or p['sequence']!=spec['paths'][p['path_name']]: raise Reject('RECORD_GRAMMAR_VIOLATION','sequence')
    if p['path_name']=='RUN_FATAL' and p['manifest_emitted']: raise Reject('RECORD_GRAMMAR_VIOLATION','fatal manifest')
    if p['path_name'] in {'NORMAL_COMPLETE','TARGET_COMPLETE'} and not p['stack_empty']: raise Reject('RECORD_GRAMMAR_VIOLATION','stack')

def execute(f,schema,trans,gram):
    v,p=f['validator'],f['payload']
    try:
        if v=='PREDICATE':
            if p['actual']!=p['expected']: raise Reject(p['failure_reason'],'predicate')
        elif v=='CONFIG': validate_config(p['config'],schema,p['symlink_escape_prefixes'])
        elif v=='CONFIG_HASH':
            validate_config(p['config'],schema,p['symlink_escape_prefixes'])
            if p['stored_sha256']!=sha(cbytes(p['config'])): raise Reject('SCHEMA_VIOLATION','config hash')
        elif v=='TRANSITION_CASE':
            if p['claimed_regeneration'] and not regen(trans,p): raise Reject('RECORD_GRAMMAR_VIOLATION','regeneration')
        elif v=='GRAMMAR': grammar(gram,p)
        elif v=='CANONICAL_JSON': parse(base64.b64decode(p['raw_base64']))
        elif v=='CANONICAL_JSONL': parse_jsonl(base64.b64decode(p['raw_base64']))
        elif v=='RATIONAL': rat(parse(base64.b64decode(p['raw_base64'])),'rational')
        else: raise Reject('CONTROL_SHAPE_VIOLATION','unknown validator')
    except Reject as e: return 'VERIFY_FAIL',e.reason
    return 'VERIFY_PASS',None

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--attestation',type=Path); ap.add_argument('--write-report',action='store_true'); a=ap.parse_args()
    packs,manifest=unpack_all(); expect=packs['CONTROL_EXPECT.json']; fixtures=packs['CONTROL_FIXTURES.json']; schema=packs['CONFIG_SCHEMA.json']; trans=packs['FAILURE_TRANSITIONS.json']; gram=packs['RECORD_GRAMMAR.json']
    if set(expect)!=set(fixtures) or len(expect)!=168: raise RuntimeError('control set/count')
    fields={'fixture_id','mutation','expected_failure_reason','expected_terminal_class','expected_checker_result'}
    if any(set(v)!=fields for v in expect.values()): raise RuntimeError('CONTROL_EXPECT fields')
    if set(trans['closed_failure_reason_enum'])!=set(trans['transitions']): raise RuntimeError('transition enum/key mismatch')
    if trans['yes_star_conditions']['allowed_window_origins']!=['CONFIG_SEED','PARENT_INHERITED'] or trans['yes_star_conditions']['forbidden_window_origins']!=['PREDICTOR_HORIZONTAL','PREDICTOR_LINEAR']: raise RuntimeError('yes-star origin gate')
    if a.attestation:
        att=parse(a.attestation.read_bytes()); start=att['start_measurement']['blob_sha']; end=att['post_artifact_measurement']['blob_sha']; mode='GITHUB_CONTENTS_API_BLOB_SHA'
    else:
        start=git_blob(DESIGN_PATH.read_bytes()); end=None; mode='LOCAL_GIT_BLOB_RECOMPUTE'
    if start!=DESIGN_BLOB: raise RuntimeError('start design blob')
    failures=[]; results={}
    for k in sorted(expect):
        obs,reason=execute(fixtures[k],schema,trans,gram); ex=expect[k]; positive=k.startswith('POS_')
        ok=(obs==ex['expected_checker_result'] and (positive or reason==ex['expected_failure_reason']))
        if k=='POS_RUN_FATAL': ok=(obs=='VERIFY_PASS' and ex['expected_checker_result']=='NOT_APPLICABLE')
        results[k]={'ok':ok,'observed_checker_result':obs,'observed_failure_reason':reason}
        if not ok: failures.append(k)
    if end is None: end=git_blob(DESIGN_PATH.read_bytes())
    if end!=DESIGN_BLOB: raise RuntimeError('end design blob')
    report={'schema':'ITEM3_SWEEP_PHASE2_SELFTEST_REPORT_V1','design_blob_start':start,'design_blob_end':end,'design_blob_unchanged':start==end==DESIGN_BLOB,'design_measurement_mode':mode,'control_count':len(expect),'control_failures':failures,'pack_manifest_sha256':sha(cbytes(manifest)),'kernel_evaluations':0,'arb_imported':False,'mathematical_calculations':0,'verdict':'PASS' if not failures else 'FAIL'}
    if a.write_report: (HERE/'PHASE2_SELFTEST.json').write_bytes(cbytes(report))
    print(cbytes(report).decode())
    raise SystemExit(0 if not failures else 1)
if __name__=='__main__': main()
