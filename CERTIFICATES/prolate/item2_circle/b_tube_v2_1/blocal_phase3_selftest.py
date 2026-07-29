#!/usr/bin/env python3
"""Calculation-free Phase-3 fixtures and semantic controls."""
from __future__ import annotations

import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path

from numeric_schema import CanonicalBytesError, Dyadic, SchemaError, parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex
from blocal_phase3_contract import *
from blocal_phase3_controls import mapping_test


class ME:
    def __init__(self, m, e): self.value=(m,e)
    def man_exp(self): return self.value
class Ball:
    def __init__(self, mm, me, rm, re): self.m=ME(mm,me); self.r=ME(rm,re)
    def mid(self): return self.m
    def rad(self): return self.r


def add(records, previous, body):
    record=dict(body, previous_record_sha256=previous)
    record['record_sha256']=record_hash(record)
    records.append(record)
    return record['record_sha256']


def rechain(config_raw, records):
    previous=chain_genesis(sha256_hex(config_raw))
    for record in records:
        record.pop('previous_record_sha256',None)
        record.pop('record_sha256',None)
        record['previous_record_sha256']=previous
        if record.get('record_type')=='RUN_SUMMARY':
            record['records_chain_tip_sha256']=previous
        record['record_sha256']=record_hash(record)
        previous=record['record_sha256']
    return b'\n'.join(cbytes(record) for record in records)


def config_bytes():
    return cbytes({
        'schema':CFG,'design_version':DV,'lambda_plus':q(LP),'s_neg':SN.to_json(),
        'lambda_candidates':[d(1,k) for k in range(24,3,-1)],
        'u_max_candidates':[d(1,k) for k in (8,7,6,5,4)],
        'budgets':{'max_depth':8,'max_evaluations':1000,'max_tiles':100},
        'canonicalizer_id':CANON,'adapter_id':ADAPTER,
        'adapter_source_sha256':'a'*64,'terminal_state_before_run':INCOMPLETE,
    })


def add_candidate(records, previous, candidate_index, increment, u_value, *, rejected=False, budget=False, split=False):
    zero=d(0,0); u_hi=u_value.to_json(); s_lo=d(-1,16); s_hi=increment.to_json()
    pos=iv((1,4),(1,3)); neg=iv((-1,3),(-1,4)); undecided=iv((-1,4),(1,4))
    depth=9 if budget else 2
    if split:
        u_mid=Dyadic.from_fraction(u_value.as_fraction()/2).to_json(); s_mid=zero
        l1=((zero,u_mid,s_lo,s_mid),(u_mid,u_hi,s_lo,s_mid),(zero,u_mid,s_mid,s_hi),(u_mid,u_hi,s_mid,s_hi))
        l2=((s_lo,s_mid),(s_mid,s_hi))
        half=Dyadic.from_fraction(increment.as_fraction()/2).to_json(); l3=((zero,half),(half,s_hi))
    else:
        l1=((zero,u_hi,s_lo,s_hi),); l2=((s_lo,s_hi),); l3=((zero,s_hi),)
    for ua,ub,sa,sb in l1:
        previous=add(records,previous,{'record_type':'TILE','node':'L1','candidate_index':candidate_index,'u_interval':{'lo':ua,'hi':ub},'s_interval':{'lo':sa,'hi':sb},'enclosure':pos,'certified':True,'depth':depth,'evaluations':3})
    for sa,sb in l2:
        previous=add(records,previous,{'record_type':'TILE','node':'L2','candidate_index':candidate_index,'u_face':u_hi,'s_interval':{'lo':sa,'hi':sb},'enclosure':pos,'certified':True,'depth':depth,'evaluations':3})
    for index,(sa,sb) in enumerate(l3):
        failed=rejected and index==len(l3)-1
        previous=add(records,previous,{'record_type':'TILE','node':'L3','candidate_index':candidate_index,'u_face':zero,'s_interval':{'lo':sa,'hi':sb},'enclosure':undecided if failed else neg,'certified':not failed,'depth':depth,'evaluations':3})
    signs=not rejected; budgets=not budget; accepted=signs and budgets
    lambda_start=LP+increment.as_fraction(); root_interval=None
    if accepted:
        root_interval=iv((3,2),(7,3))
        previous=add(records,previous,{'record_type':'J_START','node':'J_START','selected_candidate_index':candidate_index,'lambda_start':q(lambda_start),'r_interval':root_interval,'F_at_r_lo':pos,'F_at_r_hi':neg,'F_r_on_interval':iv((-1,2),(-1,3)),'claim':'J_START_UNIQUE_NONDEGENERATE_ROOT','interval_method':'INTERVAL_NEWTON_OR_KRAWCZYK_V1','strict_self_containment':True,'certified':True})
    previous=add(records,previous,{'record_type':'CANDIDATE_SUMMARY','candidate_index':candidate_index,'lambda_start':q(lambda_start),'u_max':u_hi,'coverage_counts':{'L1':len(l1),'L2':len(l2),'L3':len(l3)},'candidate_accepted':accepted,'first_failure_reason':None if accepted else ('BUDGET_EXCEEDED' if budget else 'L3_STRICT_SIGN_UNRESOLVED'),'budget_exceeded':not budgets,'unresolved':not signs})
    return previous,root_interval,{'L1':len(l1),'L2':len(l2),'L3':len(l3)}


def complete_fixture():
    config_raw=config_bytes(); previous=chain_genesis(sha256_hex(config_raw)); records=[]
    previous=add(records,previous,{'record_type':'RUN_HEADER','blocal_run_config_sha256':sha256_hex(config_raw),'chain_genesis':chain_genesis(sha256_hex(config_raw)),'canonicalizer_id':CANON,'adapter_source_sha256':'a'*64})
    inc=Dyadic(1,24)
    previous,_,first=add_candidate(records,previous,0,inc,Dyadic(1,8),rejected=True,split=True)
    previous,root,second=add_candidate(records,previous,1,inc,Dyadic(1,7),split=True)
    totals={key:first[key]+second[key] for key in first}
    previous=add(records,previous,{'record_type':'RUN_SUMMARY','selected_candidate_index':1,'lambda_start':q(LP+inc.as_fraction()),'u_max':d(1,7),'start_root_interval':root,'exact_counts':{'attempted_candidates':2,'tile_records':sum(totals.values()),'j_start_records':1,'candidate_summaries':2},'records_chain_tip_sha256':previous,'terminal_state':COMPLETE})
    records_raw=b'\n'.join(cbytes(record) for record in records)
    conclusion=complete_machine_conclusion(1,LP+inc.as_fraction(),root,totals,len(records),records[-1]['previous_record_sha256'])
    certificate=cbytes({'schema':CERT,'machine_conclusion':conclusion,'logical_lemmas':logical_lemmas()})
    return config_raw,records_raw,certificate


def incomplete_fixture():
    config_raw=config_bytes(); config=parse_canonical_json_bytes(config_raw)
    previous=chain_genesis(sha256_hex(config_raw)); records=[]
    previous=add(records,previous,{'record_type':'RUN_HEADER','blocal_run_config_sha256':sha256_hex(config_raw),'chain_genesis':chain_genesis(sha256_hex(config_raw)),'canonicalizer_id':CANON,'adapter_source_sha256':'a'*64})
    totals={'L1':0,'L2':0,'L3':0}
    for candidate_index,(increment,u_value) in enumerate(candidate_schedule(config)):
        previous,_,counts=add_candidate(records,previous,candidate_index,increment,u_value,rejected=candidate_index%2==0,budget=candidate_index%2==1)
        for key in totals: totals[key]+=counts[key]
    previous=add(records,previous,{'record_type':'RUN_SUMMARY','selected_candidate_index':None,'lambda_start':None,'u_max':None,'start_root_interval':None,'exact_counts':{'attempted_candidates':105,'tile_records':sum(totals.values()),'j_start_records':0,'candidate_summaries':105},'records_chain_tip_sha256':previous,'terminal_state':INCOMPLETE})
    records_raw=b'\n'.join(cbytes(record) for record in records)
    conclusion=incomplete_machine_conclusion(totals,len(records),records[-1]['previous_record_sha256'])
    certificate=cbytes({'schema':CERT,'machine_conclusion':conclusion,'logical_lemmas':logical_lemmas()})
    return config_raw,records_raw,certificate


def rejected(action,message):
    try: action()
    except (RuntimeError,CanonicalBytesError,SchemaError,KeyError,ValueError): return
    raise RuntimeError(message)


def semantic_controls():
    config_raw,records_raw,certificate=complete_fixture()
    base=[deepcopy(record) for record,_ in parse_canonical_jsonl(records_raw)]
    def run_mutation(mutation,*,rebuild=True,certificate_raw=certificate):
        records=deepcopy(base); mutation(records)
        raw=rechain(config_raw,records) if rebuild else b'\n'.join(cbytes(record) for record in records)
        verify_run(config_raw,raw,certificate_raw)
    def gap(records):
        record=next(record for record in records if record.get('record_type')=='TILE' and record.get('node')=='L1')
        record['u_interval']['hi']=d(1,10)
    def overlap(records):
        selected=[record for record in records if record.get('record_type')=='TILE' and record.get('node')=='L1' and record.get('candidate_index')==0]
        selected[1]['u_interval']['lo']=d(0,0)
    def outside(records):
        record=next(record for record in records if record.get('record_type')=='TILE' and record.get('node')=='L1')
        record['u_interval']['hi']=d(1,7)
    rejected(lambda:run_mutation(gap),'coverage gap accepted')
    rejected(lambda:run_mutation(overlap),'coverage overlap accepted')
    rejected(lambda:run_mutation(outside),'outside accepted')
    rejected(lambda:run_mutation(lambda records:records[2].__setitem__('previous_record_sha256','f'*64),rebuild=False),'chain tamper accepted')
    incomplete_config,incomplete_records,incomplete_certificate=incomplete_fixture()
    records=[deepcopy(record) for record,_ in parse_canonical_jsonl(incomplete_records)]
    records[-1]['terminal_state']=COMPLETE
    rejected(lambda:verify_run(incomplete_config,rechain(incomplete_config,records),incomplete_certificate),'incomplete promotion accepted')
    bad=parse_canonical_json_bytes(certificate); bad['machine_conclusion']['status']='BLOCAL_CERTIFIED'
    rejected(lambda:verify_run(config_raw,records_raw,cbytes(bad)),'old vocabulary accepted')
    return 6


def stage1_fixture():
    with tempfile.TemporaryDirectory() as temporary:
        root=Path(temporary); item=root/'CERTIFICATES/prolate/item2_branch'; independent=item/'independent_recheck'; independent.mkdir(parents=True)
        sources={
            'boundary_entry_independent.py':b'"""UNVERIFIED_PROVENANCE disclaimer only."""\nimport json\n',
            'bprime_independent.py':b'import time\n',
            'run_enclosure.py':b'import boundary_entry_independent as M\n',
            'verify_change_of_variables.py':b'import sympy as sp\n',
        }
        implementation_hashes={}
        for name,raw in sources.items():
            (independent/name).write_bytes(raw); implementation_hashes[name]=sha256_hex(raw)
        evaluations={
            'B(206538/100000)':{'lower':'2.0e-7','upper':'8.0e-7','sign':'POSITIVE'},
            'B(206539/100000)':{'lower':'-2.0e-6','upper':'-1.3e-6','sign':'NEGATIVE'},
            'Bprime([206538/100000,206539/100000])':{'lower':'-0.2190','upper':'-0.2189','sign':'NEGATIVE'},
        }
        certificate={'status':'CERTIFIED','independence':{'unverified_provenance_file_read':False},'certified_statement':STATEMENT,'evaluations':evaluations,'implementation_files_sha256':implementation_hashes,'conclusion':STAGE1_CONCLUSION,'scope':SCOPE}
        certificate_raw=cbytes(certificate); (independent/'certificate_item2_independent.json').write_bytes(certificate_raw)
        note=b'UNVERIFIED_PROVENANCE disclaimer and no access statement\n'; run_log=b'run log\n'
        (independent/'INDEPENDENT_CHECK_NOTE.md').write_bytes(note); (independent/'RUN_LOG.md').write_bytes(run_log)
        inner_members={'INDEPENDENT_CHECK_NOTE.md':sha256_hex(note),'RUN_LOG.md':sha256_hex(run_log),'certificate_item2_independent.json':sha256_hex(certificate_raw),**implementation_hashes}
        inner_raw=''.join(f'{digest}  {name}\n' for name,digest in sorted(inner_members.items())).encode(); (independent/'SHA256SUMS.txt').write_bytes(inner_raw)
        extra_dir=item/'UNVERIFIED_PROVENANCE'; extra_dir.mkdir(); unverified=b'old source\n'; (extra_dir/'prolate_boundary_entry_arb.py').write_bytes(unverified)
        outer_members={
            'UNVERIFIED_PROVENANCE/prolate_boundary_entry_arb.py':sha256_hex(unverified),
            'independent_recheck/SHA256SUMS.txt':sha256_hex(inner_raw),
            **{f'independent_recheck/{name}':digest for name,digest in inner_members.items()},
        }
        outer_raw=''.join(f'{digest}  {name}\n' for name,digest in sorted(outer_members.items())).encode(); (item/'SHA256SUMS.txt').write_bytes(outer_raw)
        subprocess.run(['git','init','-q',str(root)],check=True); subprocess.run(['git','-C',str(root),'config','user.email','fixture@example.invalid'],check=True); subprocess.run(['git','-C',str(root),'config','user.name','fixture'],check=True); subprocess.run(['git','-C',str(root),'add','.'],check=True); subprocess.run(['git','-C',str(root),'commit','-q','-m','fixture'],check=True)
        head=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
        plan={'repository_root':str(root),'certificate_path':'CERTIFICATES/prolate/item2_branch/independent_recheck/certificate_item2_independent.json','inner_manifest_path':'CERTIFICATES/prolate/item2_branch/independent_recheck/SHA256SUMS.txt','outer_manifest_path':'CERTIFICATES/prolate/item2_branch/SHA256SUMS.txt','source_head':head,'certificate_sha256':sha256_hex(certificate_raw),'inner_manifest_sha256':sha256_hex(inner_raw),'outer_manifest_sha256':sha256_hex(outer_raw)}
        need(audit_stage1(plan)['count']==12,'stage1 fixture')
        malicious=b'from pathlib import Path\nPath("../UNVERIFIED_PROVENANCE/prolate_boundary_entry_arb.py").read_bytes()\n'
        rejected(lambda:audit_independent_source(malicious,'bad.py'),'forbidden path access accepted')
        bad_certificate=deepcopy(certificate); del bad_certificate['evaluations']['B(206539/100000)']; bad_raw=cbytes(bad_certificate)
        (independent/'certificate_item2_independent.json').write_bytes(bad_raw)
        rejected(lambda:audit_stage1(plan),'missing evaluation accepted')
        (independent/'certificate_item2_independent.json').write_bytes(certificate_raw)
        (extra_dir/'prolate_boundary_entry_arb.py').write_bytes(unverified+b'tamper')
        rejected(lambda:audit_stage1(plan),'outer full-entry tamper accepted')


def selftest():
    canonicalizer_test(); margin=sneg_proof()
    source=Path(__file__).with_name('blocal_bentry_selftest.py')
    mapping_test(source.read_bytes() if source.exists() else None)
    adapter_cases=[(0,0,0,0),(5,0,0,0),(-5,0,0,0),(3,-2,0,0),(-3,-2,0,0),(3,-4,1,-6),(7,-3,1,-3),(-7,-3,1,-3),(0,0,1,-8),(2**200+1,-17,2**120+1,-91)]
    for case in adapter_cases: adapter(Ball(*case))
    complete=verify_run(*complete_fixture()); incomplete=verify_run(*incomplete_fixture())
    need(logical_lemmas()[0]['machine_verified'] is False and isinstance(logical_lemmas(),list),'M-B1 fixture')
    controls=semantic_controls(); stage1_fixture()
    return {'adapter_cases':10,'control_map':45,'extra_control':46,'semantic_verify_run_controls':controls,'margin':margin,'complete_fixture':complete,'incomplete_fixture':incomplete,'stage1_checks':12,'status':'CHAT_SIDE_AUDIT_WAITING'}
