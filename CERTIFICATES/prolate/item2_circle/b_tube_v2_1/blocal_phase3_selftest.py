#!/usr/bin/env python3
"""Calculation-free Phase-3 fixtures and semantic controls."""
from __future__ import annotations
import subprocess, tempfile
from copy import deepcopy
from pathlib import Path
from numeric_schema import (CanonicalBytesError, Dyadic, SchemaError,
    parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex)
from blocal_phase3_contract import *
from blocal_phase3_controls import mapping_test

class ME:

    def __init__(self, m, e):
        self.x = (m, e)

    def man_exp(self):
        return self.x

class Ball:

    def __init__(self, mm, me, rm, re):
        self.a = ME(mm, me)
        self.b = ME(rm, re)

    def mid(self):
        return self.a

    def rad(self):
        return self.b

def add(rs, p, x):
    x = dict(x, previous_record_sha256=p)
    x['record_sha256'] = rhash(x)
    rs.append(x)
    return x['record_sha256']

def rechain(cb, rs):
    p = genesis(sha256_hex(cb))
    for x in rs:
        x.pop('previous_record_sha256', None)
        x.pop('record_sha256', None)
        x['previous_record_sha256'] = p
        x['record_sha256'] = rhash(x)
        p = x['record_sha256']
        if x.get('record_type') == 'RUN_SUMMARY':
            x['records_chain_tip_sha256'] = x['previous_record_sha256']
            x['record_sha256'] = rhash(x)
            p = x['record_sha256']
    return b'\n'.join((cbytes(x) for x in rs))

def base_config():
    cfg = {'schema': CFG, 'design_version': DV, 'lambda_plus': q(LP), 's_neg': SN.to_json(), 'lambda_candidates': [d(1, k) for k in range(24, 3, -1)], 'u_max_candidates': [d(1, k) for k in (8, 7, 6, 5, 4)], 'budgets': {'max_depth': 8, 'max_evaluations': 1000, 'max_tiles': 100}, 'canonicalizer_id': CANON, 'adapter_id': ADAPTER, 'adapter_source_sha256': 'a' * 64, 'terminal_state_before_run': INCOMPLETE}
    return cbytes(cfg)

def add_candidate(rs, p, ci, inc, um, rejected=False, budget=False, split=False):
    zero = d(0, 0)
    uh = um.to_json()
    sl = d(-1, 16)
    sh = inc.to_json()
    pos = iv((1, 4), (1, 3))
    neg = iv((-1, 3), (-1, 4))
    unk = iv((-1, 4), (1, 4))
    dep = 9 if budget else 2
    if split:
        umid = Dyadic.from_fraction(um.as_fraction() / 2).to_json()
        sm = d(0, 0)
        l1 = ((zero, umid, sl, sm), (umid, uh, sl, sm), (zero, umid, sm, sh), (umid, uh, sm, sh))
        l2 = ((sl, sm), (sm, sh))
        half = Dyadic.from_fraction(inc.as_fraction() / 2).to_json()
        l3 = ((zero, half), (half, sh))
    else:
        l1 = ((zero, uh, sl, sh),)
        l2 = ((sl, sh),)
        l3 = ((zero, sh),)
    for ua, ub, sa, sb in l1:
        p = add(rs, p, {'record_type': 'TILE', 'node': 'L1', 'candidate_index': ci, 'u_interval': {'lo': ua, 'hi': ub}, 's_interval': {'lo': sa, 'hi': sb}, 'enclosure': pos, 'certified': True, 'depth': dep, 'evaluations': 3})
    for sa, sb in l2:
        p = add(rs, p, {'record_type': 'TILE', 'node': 'L2', 'candidate_index': ci, 'u_face': uh, 's_interval': {'lo': sa, 'hi': sb}, 'enclosure': pos, 'certified': True, 'depth': dep, 'evaluations': 3})
    for n, (sa, sb) in enumerate(l3):
        p = add(rs, p, {'record_type': 'TILE', 'node': 'L3', 'candidate_index': ci, 'u_face': zero, 's_interval': {'lo': sa, 'hi': sb}, 'enclosure': unk if rejected and n == len(l3) - 1 else neg, 'certified': not (rejected and n == len(l3) - 1), 'depth': dep, 'evaluations': 3})
    signs = not rejected
    budgets = not budget
    accepted = signs and budgets
    lam = LP + inc.as_fraction()
    ji = None
    if accepted:
        ji = iv((3, 2), (7, 3))
        p = add(rs, p, {'record_type': 'J_START', 'node': 'J_START', 'selected_candidate_index': ci, 'lambda_start': q(lam), 'r_interval': ji, 'F_at_r_lo': pos, 'F_at_r_hi': neg, 'F_r_on_interval': iv((-1, 2), (-1, 3)), 'claim': 'J_START_UNIQUE_NONDEGENERATE_ROOT', 'interval_method': 'INTERVAL_NEWTON_OR_KRAWCZYK_V1', 'strict_self_containment': True, 'certified': True})
    p = add(rs, p, {'record_type': 'CANDIDATE_SUMMARY', 'candidate_index': ci, 'lambda_start': q(lam), 'u_max': uh, 'coverage_counts': {'L1': len(l1), 'L2': len(l2), 'L3': len(l3)}, 'candidate_accepted': accepted, 'first_failure_reason': None if accepted else 'BUDGET_EXCEEDED' if budget else 'L3_STRICT_SIGN_UNRESOLVED', 'budget_exceeded': not budgets, 'unresolved': not signs})
    return (p, ji, {'L1': len(l1), 'L2': len(l2), 'L3': len(l3)})

def fixture_complete():
    cb = base_config()
    p = genesis(sha256_hex(cb))
    rs = []
    p = add(rs, p, {'record_type': 'RUN_HEADER', 'blocal_run_config_sha256': sha256_hex(cb), 'chain_genesis': genesis(sha256_hex(cb)), 'canonicalizer_id': CANON, 'adapter_source_sha256': 'a' * 64})
    inc = Dyadic(1, 24)
    p, _, c0 = add_candidate(rs, p, 0, inc, Dyadic(1, 8), rejected=True, split=True)
    p, ji, c1 = add_candidate(rs, p, 1, inc, Dyadic(1, 7), split=True)
    totals = {k: c0[k] + c1[k] for k in c0}
    p = add(rs, p, {'record_type': 'RUN_SUMMARY', 'selected_candidate_index': 1, 'lambda_start': q(LP + inc.as_fraction()), 'u_max': d(1, 7), 'start_root_interval': ji, 'exact_counts': {'attempted_candidates': 2, 'tile_records': sum(totals.values()), 'j_start_records': 1, 'candidate_summaries': 2}, 'records_chain_tip_sha256': p, 'terminal_state': COMPLETE})
    rb = b'\n'.join((cbytes(x) for x in rs))
    mc = complete_mc(1, LP + inc.as_fraction(), ji, totals, len(rs), rs[-1]['previous_record_sha256'])
    cert = cbytes({'schema': CERT, 'machine_conclusion': mc, 'logical_lemmas': logical_lemmas()})
    return (cb, rb, cert)

def fixture_incomplete():
    cb = base_config()
    cfg = parse_canonical_json_bytes(cb)
    p = genesis(sha256_hex(cb))
    rs = []
    p = add(rs, p, {'record_type': 'RUN_HEADER', 'blocal_run_config_sha256': sha256_hex(cb), 'chain_genesis': genesis(sha256_hex(cb)), 'canonicalizer_id': CANON, 'adapter_source_sha256': 'a' * 64})
    totals = {'L1': 0, 'L2': 0, 'L3': 0}
    for ci, (inc, um) in enumerate(schedule(cfg)):
        p, _, c = add_candidate(rs, p, ci, inc, um, rejected=ci % 2 == 0, budget=ci % 2 == 1)
        totals = {k: totals[k] + c[k] for k in totals}
    p = add(rs, p, {'record_type': 'RUN_SUMMARY', 'selected_candidate_index': None, 'lambda_start': None, 'u_max': None, 'start_root_interval': None, 'exact_counts': {'attempted_candidates': 105, 'tile_records': sum(totals.values()), 'j_start_records': 0, 'candidate_summaries': 105}, 'records_chain_tip_sha256': p, 'terminal_state': INCOMPLETE})
    rb = b'\n'.join((cbytes(x) for x in rs))
    mc = incomplete_mc(totals, len(rs), rs[-1]['previous_record_sha256'])
    cert = cbytes({'schema': CERT, 'machine_conclusion': mc, 'logical_lemmas': logical_lemmas()})
    return (cb, rb, cert)

def rejected(fn, msg):
    try:
        fn()
    except (RuntimeError, CanonicalBytesError, SchemaError, KeyError, ValueError):
        return
    raise RuntimeError(msg)

def semantic_controls():
    cb, rb, cert = fixture_complete()
    base = [deepcopy(x) for x, _ in parse_canonical_jsonl(rb)]

    def runmut(mut, certificate=cert, re=True):
        rs = deepcopy(base)
        mut(rs)
        data = rechain(cb, rs) if re else b'\n'.join((cbytes(x) for x in rs))
        verify_run(cb, data, certificate)

    def gap(rs):
        r = next((x for x in rs if x.get('record_type') == 'TILE' and x.get('node') == 'L1'))
        r['u_interval']['hi'] = d(1, 10)

    def overlap(rs):
        xs = [x for x in rs if x.get('record_type') == 'TILE' and x.get('node') == 'L1' and (x.get('candidate_index') == 0)]
        xs[1]['u_interval']['lo'] = d(0, 0)

    def outside(rs):
        r = next((x for x in rs if x.get('record_type') == 'TILE' and x.get('node') == 'L1'))
        r['u_interval']['hi'] = d(1, 7)
    rejected(lambda: runmut(gap), 'coverage gap accepted')
    rejected(lambda: runmut(overlap), 'coverage overlap accepted')
    rejected(lambda: runmut(outside), 'domain outside accepted')
    rejected(lambda: runmut(lambda rs: rs[2].__setitem__('previous_record_sha256', 'f' * 64), re=False), 'chain tamper accepted')
    icb, irb, icert = fixture_incomplete()
    irs = [deepcopy(x) for x, _ in parse_canonical_jsonl(irb)]
    irs[-1]['terminal_state'] = COMPLETE
    rejected(lambda: verify_run(icb, rechain(icb, irs), icert), 'incomplete promotion accepted')
    badcert = parse_canonical_json_bytes(cert)
    badcert['machine_conclusion']['status'] = 'BLOCAL_CERTIFIED'
    rejected(lambda: verify_run(cb, rb, cbytes(badcert)), 'M-A1 vocabulary accepted')
    return 6

def stage1_fixture():
    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / 'i').mkdir()
        impl = b'# independent implementation\n'
        extra = b'outer-only payload\n'
        (r / 'i/x.py').write_bytes(impl)
        (r / 'extra.txt').write_bytes(extra)
        cert = {'status': 'CERTIFIED', 'certified_statement': STATEMENT, 'machine_conclusion': MC, 'scope': SCOPE, 'lambda_partial_bracket': {'lo': q(LM), 'hi': q(LP)}, 'implementation_sha256': sha256_hex(impl)}
        cr = cbytes(cert)
        (r / 'i/c.json').write_bytes(cr)
        ir = f'{sha256_hex(cr)}  i/c.json\n{sha256_hex(impl)}  i/x.py\n'.encode()
        (r / 'i/SHA256SUMS.txt').write_bytes(ir)
        oraw = f'{sha256_hex(cr)}  i/c.json\n{sha256_hex(ir)}  i/SHA256SUMS.txt\n{sha256_hex(extra)}  extra.txt\n'.encode()
        (r / 'SHA256SUMS.txt').write_bytes(oraw)
        subprocess.run(['git', 'init', '-q', str(r)], check=True)
        subprocess.run(['git', '-C', str(r), 'config', 'user.email', 'fixture@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(r), 'config', 'user.name', 'fixture'], check=True)
        subprocess.run(['git', '-C', str(r), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(r), 'commit', '-q', '-m', 'fixture'], check=True)
        head = subprocess.run(['git', '-C', str(r), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
        plan = {'repository_root': str(r), 'certificate_path': 'i/c.json', 'inner_manifest_path': 'i/SHA256SUMS.txt', 'outer_manifest_path': 'SHA256SUMS.txt', 'implementation_path': 'i/x.py', 'source_head': head, 'certificate_sha256': sha256_hex(cr), 'inner_manifest_sha256': sha256_hex(ir), 'outer_manifest_sha256': sha256_hex(oraw), 'implementation_sha256': sha256_hex(impl)}
        need(audit_stage1(plan)['count'] == 12, 'stage1 fixture')
        (r / 'extra.txt').write_bytes(extra + b'tamper')
        rejected(lambda: audit_stage1(plan), 'outer full-entry tamper accepted')

def selftest():
    canonicalizer_test()
    margin = sneg_proof()
    sp = Path(__file__).with_name('blocal_bentry_selftest.py')
    mapping_test(sp.read_bytes() if sp.exists() else None)
    cases = [(0, 0, 0, 0), (5, 0, 0, 0), (-5, 0, 0, 0), (3, -2, 0, 0), (-3, -2, 0, 0), (3, -4, 1, -6), (7, -3, 1, -3), (-7, -3, 1, -3), (0, 0, 1, -8), (2 ** 200 + 1, -17, 2 ** 120 + 1, -91)]
    for x in cases:
        adapter(Ball(*x))
    cb, rb, cert = fixture_complete()
    complete = verify_run(cb, rb, cert)
    ib, ir, ic = fixture_incomplete()
    incomplete = verify_run(ib, ir, ic)
    controls = semantic_controls()
    stage1_fixture()
    return {'adapter_cases': 10, 'control_map': 45, 'extra_control': 46, 'semantic_verify_run_controls': controls, 'margin': margin, 'complete_fixture': complete, 'incomplete_fixture': incomplete, 'stage1_checks': 12, 'status': 'CHAT_SIDE_AUDIT_WAITING'}
