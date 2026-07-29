#!/usr/bin/env python3
"""B-LOCAL/B-ENTRY Phase-3 contract implementation.

Status: CHAT_SIDE_AUDIT_WAITING. Calculation-free only.
"""
from __future__ import annotations
import subprocess
from fractions import Fraction
from pathlib import Path
from numeric_schema import (D_ZERO, Dyadic, DyadicInterval, Rational,
    arb_ball_to_exact_interval, canonical_json_bytes,
    parse_canonical_json_bytes, parse_canonical_jsonl, sha256_hex)

ERR = RuntimeError

DV = '2.1'

CFG = 'blocal-run-config-v1'

CERT = 'blocal-certificate-v1'

MCS = 'btube-blocal-machine-conclusion-v1'

COMPLETE = 'BLOCAL_COMPLETE'

INCOMPLETE = 'BLOCAL_INCOMPLETE'

CHAIN = 'BLOCAL-COVERAGE-CHAIN-v1'

CANON = 'BTUBE_NUMERIC_SCHEMA_CANONICAL_JSON_V1'

ADAPTER = 'ARB_TO_CANONICAL_DYADIC_INTERVAL_V1'

LP = Fraction(206539, 100000)

LM = Fraction(206538, 100000)

SN = Dyadic(1, 16)

RANGE = '(lambda_partial,lambda_start]'

STATEMENT = "B(103/50)>0, B(207/100)<0, B(206538/100000)>0, B(206539/100000)<0, and B'(lambda)<0 on [206538/100000,206539/100000]. Hence lambda_partial is the unique root in (206538/100000,206539/100000)."

MC = {'lambda_partial': '(206538/100000,206539/100000)', 'strict_upper_bound': '206539/100000', 'unique_on_interval': True}

SCOPE = 'Boundary-entry parameter only. Item 2 proper, requiring the single sign change of F_r, remains open.'

L4_PREMISES = ['STAGE1_UNIQUE_BOUNDARY_ROOT_IN_OPEN_BRACKET', 'STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET', 'STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO', 'L1_EXTENDED_HU_STRICT_POSITIVITY', 'L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY', 'L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY', 'S_NEG_STRICTLY_EXCEEDS_STAGE1_BRACKET_WIDTH', 'H_CONTINUITY_FROM_FIXED_FORMULA']

CLAIM_KEYS = {'stage1_dependency_exact', 'l1_extended_exact_coverage', 'l1_Hu_strictly_positive', 'l2_extended_exact_coverage', 'l2_inner_face_strictly_positive', 'l3_nonnegative_exact_coverage', 'l3_boundary_face_strictly_negative', 'start_root_interval_certified', 'supplies_binding_lambda_start', 'real_analytic_claimed'}

def need(x, msg):
    if not x:
        raise ERR(msg)

def keys(x, k, w):
    need(isinstance(x, dict) and set(x) == k, f'{w}: exact keys')

def cbytes(x):
    return canonical_json_bytes(x)

def d(m, e):
    return Dyadic.canonical(m, e).to_json()

def q(x):
    return Rational.from_fraction(x).to_json()

def iv(a, b):
    return DyadicInterval(Dyadic.canonical(*a), Dyadic.canonical(*b)).to_json()

def df(x, w='dyadic'):
    return Dyadic.from_json(x, w).as_fraction()

def qf(x, w='rational'):
    return Rational.from_json(x, w).as_fraction()

def inf(x, w='interval'):
    z = DyadicInterval.from_json(x, w)
    return (z.lo.as_fraction(), z.hi.as_fraction())

def canonicalizer_test():
    need(cbytes({'scope': 'α'}) == b'{"scope":"\\u03b1"}', 'canonicalizer policy')

def adapter(ball):
    return arb_ball_to_exact_interval(ball)

def adapter_source_sha(path=None):
    p = Path(__file__) if path is None else Path(path)
    need(not p.is_symlink(), 'adapter symlink')
    p = p.resolve(strict=True)
    need(p.is_file(), 'adapter regular file')
    return sha256_hex(p.read_bytes())

def sneg_proof():
    need(100000 > 1 << 16, 'integer s_neg proof')
    need(SN.as_fraction() > LP - LM, 'fraction s_neg proof')
    return {'lhs': 100000, 'rhs': 65536, 'strict': True}

def pointer(x, p):
    need(p.startswith('/'), 'JSON pointer')
    for t in p[1:].split('/'):
        t = t.replace('~1', '/').replace('~0', '~')
        need(isinstance(x, dict) and t in x, 'pointer component')
        x = x[t]
    return x

def machine_conclusion(raw):
    x = parse_canonical_json_bytes(raw, allow_display=False)
    y = pointer(x, '/machine_conclusion')
    need(isinstance(y, dict), 'machine conclusion object')
    return (y, cbytes(y))

def sums(raw, where):
    need(b'\r' not in raw, f'{where}: CR')
    out = {}
    for n, line in enumerate(raw.decode().splitlines(), 1):
        if not line:
            continue
        p = line.split(maxsplit=1)
        need(len(p) == 2, f'{where}:{n}')
        h, name = (p[0], p[1].lstrip(' *'))
        need(len(h) == 64 and all((c in '0123456789abcdef' for c in h)), f'{where}: hash')
        need(name and name not in out and (not name.startswith('/')) and ('..' not in Path(name).parts), f'{where}: path')
        out[name] = h
    need(out, f'{where}: empty')
    return out

def repo_file(root, rel):
    need(isinstance(rel, str) and rel and (not rel.startswith('/')), 'repo path')
    p = Path(root) / rel
    need(not p.is_symlink(), f'symlink {rel}')
    rr = Path(root).resolve(strict=True)
    p = p.resolve(strict=True)
    try:
        p.relative_to(rr)
    except ValueError as e:
        raise ERR(f'escape {rel}') from e
    need(p.is_file(), f'file {rel}')
    return p

def audit_stage1(plan):
    req = {'repository_root', 'certificate_path', 'inner_manifest_path', 'outer_manifest_path', 'implementation_path', 'source_head', 'certificate_sha256', 'inner_manifest_sha256', 'outer_manifest_sha256', 'implementation_sha256'}
    keys(plan, req, 'plan')
    root = Path(plan['repository_root'])
    actual = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
    need(actual == plan['source_head'], '01 source head mismatch')
    cp = repo_file(root, plan['certificate_path'])
    ip = repo_file(root, plan['inner_manifest_path'])
    op = repo_file(root, plan['outer_manifest_path'])
    xp = repo_file(root, plan['implementation_path'])
    cr, ir, orr, xr = (cp.read_bytes(), ip.read_bytes(), op.read_bytes(), xp.read_bytes())
    done = []
    need(len(plan['source_head']) == 40 and all((c in '0123456789abcdef' for c in plan['source_head'])), '01 source head format')
    done.append(1)
    need(sha256_hex(cr) == plan['certificate_sha256'], '02 cert hash')
    done.append(2)
    need(sha256_hex(ir) == plan['inner_manifest_sha256'], '03 inner hash')
    done.append(3)
    need(sha256_hex(orr) == plan['outer_manifest_sha256'], '04 outer hash')
    done.append(4)
    cert = parse_canonical_json_bytes(cr, allow_display=False)
    need(cert.get('status') == 'CERTIFIED', '05 status')
    done.append(5)
    need(cert.get('certified_statement') == STATEMENT, '06 statement')
    done.append(6)
    mc, mcb = machine_conclusion(cr)
    need(mc == MC and mcb == cbytes(MC), '07 conclusion')
    done.append(7)
    need(cert.get('scope') == SCOPE, '08 scope')
    done.append(8)
    br = cert.get('lambda_partial_bracket')
    need(isinstance(br, dict) and set(br) == {'lo', 'hi'}, '09 bracket')
    need(qf(br['lo']) == LM and qf(br['hi']) == LP and (mc['unique_on_interval'] is True) and (mc['strict_upper_bound'] == '206539/100000'), '09 bracket')
    done.append(9)
    need(sha256_hex(xr) == plan['implementation_sha256'], '10 implementation hash')
    need(cert.get('implementation_sha256') in (None, plan['implementation_sha256']), '10 certificate implementation pin')
    done.append(10)
    inn, outer = (sums(ir, 'inner'), sums(orr, 'outer'))
    inner_payload = []
    for rel, h in inn.items():
        raw = repo_file(root, rel).read_bytes()
        need(sha256_hex(raw) == h, f'12 payload {rel}')
        inner_payload.append(raw)
    outer_payload = []
    for rel, h in outer.items():
        raw = repo_file(root, rel).read_bytes()
        need(sha256_hex(raw) == h, f'12 outer payload {rel}')
        outer_payload.append(raw)
    need(b'UNVERIFIED_PROVENANCE' not in b''.join([cr, ir, orr, xr, *inner_payload, *outer_payload]), '11 provenance dependency')
    done.append(11)
    need(inn.get(plan['certificate_path']) == plan['certificate_sha256'], '12 cert inner')
    need(inn.get(plan['implementation_path']) == plan['implementation_sha256'], '12 impl inner')
    need(outer.get(plan['inner_manifest_path']) == plan['inner_manifest_sha256'], '12 inner outer')
    need(outer.get(plan['certificate_path']) == plan['certificate_sha256'], '12 cert outer')
    done.append(12)
    return {'checks': done, 'count': 12, 'state': 'STAGE1_CONTENT_AUDIT_CANDIDATE'}

def interval_cover(xs, lo, hi, w):
    for a, b in xs:
        need(lo <= a < b <= hi, f'{w}: outside')
    ep = sorted({lo, hi, *[z for x in xs for z in x]})
    for a, b in zip(ep, ep[1:]):
        need(sum((x <= a and b <= y for x, y in xs)) == 1, f'{w}: gap/overlap')

def rect_cover(xs, ulo, uhi, slo, shi, w):
    for a, b, c, e in xs:
        need(ulo <= a < b <= uhi and slo <= c < e <= shi, f'{w}: outside')
    us = sorted({ulo, uhi, *[z for a, b, _, _ in xs for z in (a, b)]})
    ss = sorted({slo, shi, *[z for _, _, c, e in xs for z in (c, e)]})
    for a, b in zip(us, us[1:]):
        for c, e in zip(ss, ss[1:]):
            need(sum((x <= a and b <= y and (z <= c) and (e <= t) for x, y, z, t in xs)) == 1, f'{w}: gap/overlap')

def sign(node, x, ok):
    z = DyadicInterval.from_json(x)
    return ok and (D_ZERO < z.lo if node in ('L1', 'L2') else z.hi < D_ZERO)

def rhash(r):
    return sha256_hex(cbytes({k: v for k, v in r.items() if k != 'record_sha256'}))

def genesis(h):
    return sha256_hex(CHAIN.encode() + b'\x00' + bytes.fromhex(h))

def schedule(cfg):
    ls = [Dyadic.from_json(x) for x in cfg['lambda_candidates']]
    us = [Dyadic.from_json(x) for x in cfg['u_max_candidates']]
    need(ls == [Dyadic(1, k) for k in range(24, 3, -1)], 'lambda schedule')
    need(us == [Dyadic(1, k) for k in (8, 7, 6, 5, 4)], 'u schedule')
    return [(l, u) for l in ls for u in us]

def tiles(rs, cur, ci, node, u, s, sn, bud):
    a = []
    while cur < len(rs) and rs[cur].get('record_type') == 'TILE' and (rs[cur].get('node') == node):
        r = rs[cur]
        need(r.get('candidate_index') == ci, f'{node}: index')
        for k in ('depth', 'evaluations'):
            need(isinstance(r.get(k), int) and (not isinstance(r.get(k), bool)) and (r[k] >= 0), f'{node}: {k}')
        a.append(r)
        cur += 1
    need(a, f'{node}: count')
    sign_ok = all((sign(node, r['enclosure'], r.get('certified') is True) for r in a))
    budget_ok = len(a) <= bud['max_tiles'] and all((r['depth'] <= bud['max_depth'] and r['evaluations'] <= bud['max_evaluations'] for r in a))
    if node == 'L1':
        rect_cover([(*inf(r['u_interval']), *inf(r['s_interval'])) for r in a], Fraction(0), u, -sn, s, 'L1')
    else:
        interval_cover([inf(r['s_interval']) for r in a], -sn if node == 'L2' else Fraction(0), s, node)
        face = u if node == 'L2' else Fraction(0)
        for r in a:
            need(df(r['u_face']) == face, f'{node}: face')
    return (cur, sign_ok, budget_ok, len(a))

def jstart(r, ci, lam):
    req = {'record_type', 'node', 'selected_candidate_index', 'lambda_start', 'r_interval', 'F_at_r_lo', 'F_at_r_hi', 'F_r_on_interval', 'claim', 'interval_method', 'strict_self_containment', 'certified', 'previous_record_sha256', 'record_sha256'}
    keys(r, req, 'J_START')
    need(r['record_type'] == r['node'] == 'J_START' and r['selected_candidate_index'] == ci and (qf(r['lambda_start']) == lam), 'J_START identity')
    a, b = inf(r['r_interval'])
    x = DyadicInterval.from_json(r['F_at_r_lo'])
    y = DyadicInterval.from_json(r['F_at_r_hi'])
    z = DyadicInterval.from_json(r['F_r_on_interval'])
    need(0 < a < b < 1 and D_ZERO < x.lo and (y.hi < D_ZERO) and (z.hi < D_ZERO), 'J_START signs')
    need(r['claim'] == 'J_START_UNIQUE_NONDEGENERATE_ROOT' and r['interval_method'] == 'INTERVAL_NEWTON_OR_KRAWCZYK_V1' and (r['strict_self_containment'] is True) and (r['certified'] is True), 'J_START proof')
    return r['r_interval']

def machine_claims(value):
    keys(value, CLAIM_KEYS, 'machine_claims')
    need(value['real_analytic_claimed'] is False, 'real analytic claim')
    for k, v in value.items():
        if k != 'real_analytic_claimed':
            need(isinstance(v, bool), f'machine claim {k}')

def complete_mc(ci, lam, ji, counts, record_count, chain_tip):
    return {'schema': MCS, 'status': COMPLETE, 'selected_candidate_index': ci, 'lambda_start': q(lam), 'start_root_interval': ji, 'machine_claims': {'stage1_dependency_exact': True, 'l1_extended_exact_coverage': True, 'l1_Hu_strictly_positive': True, 'l2_extended_exact_coverage': True, 'l2_inner_face_strictly_positive': True, 'l3_nonnegative_exact_coverage': True, 'l3_boundary_face_strictly_negative': True, 'start_root_interval_certified': True, 'supplies_binding_lambda_start': True, 'real_analytic_claimed': False}, 'coverage': {'l1_leaf_count': counts['L1'], 'l2_leaf_count': counts['L2'], 'l3_leaf_count': counts['L3'], 'record_count': record_count, 'chain_tip_sha256': chain_tip}}

def incomplete_mc(counts, record_count, chain_tip):
    return {'schema': MCS, 'status': INCOMPLETE, 'selected_candidate_index': None, 'lambda_start': None, 'start_root_interval': None, 'machine_claims': {'stage1_dependency_exact': False, 'l1_extended_exact_coverage': False, 'l1_Hu_strictly_positive': False, 'l2_extended_exact_coverage': False, 'l2_inner_face_strictly_positive': False, 'l3_nonnegative_exact_coverage': False, 'l3_boundary_face_strictly_negative': False, 'start_root_interval_certified': False, 'supplies_binding_lambda_start': False, 'real_analytic_claimed': False}, 'coverage': {'l1_leaf_count': counts['L1'], 'l2_leaf_count': counts['L2'], 'l3_leaf_count': counts['L3'], 'record_count': record_count, 'chain_tip_sha256': chain_tip}}

def logical_lemmas():
    return {'BLOCAL_IVT_MONOTONE_ENTRY_V1': {'premises': L4_PREMISES, 'conclusion': {'unique_non_degenerate_root_for_every_lambda_in': RANGE}}}

def verify_certificate(certb, expected):
    cert = parse_canonical_json_bytes(certb, allow_display=False)
    need(cert.get('schema') == CERT, 'certificate schema')
    mc, mcb = machine_conclusion(certb)
    need(mc == expected and mcb == cbytes(expected), 'certificate conclusion')
    need('binding_to_final_lambda_start' not in mc and 'coverage_claim' not in mc and ('unique_non_degenerate_root_for_every_lambda_in' not in mc) and ('real_analytic' not in mc), 'machine/logical separation')
    machine_claims(mc.get('machine_claims'))
    need(cert.get('logical_lemmas') == logical_lemmas(), 'logical lemma separation')

def verify_run(cb, rb, certb=None):
    cfg = parse_canonical_json_bytes(cb, allow_display=False)
    req = {'schema', 'design_version', 'lambda_plus', 's_neg', 'lambda_candidates', 'u_max_candidates', 'budgets', 'canonicalizer_id', 'adapter_id', 'adapter_source_sha256', 'terminal_state_before_run'}
    keys(cfg, req, 'config')
    need(cfg['schema'] == CFG and cfg['design_version'] == DV and (cfg['canonicalizer_id'] == CANON) and (cfg['adapter_id'] == ADAPTER) and (cfg['terminal_state_before_run'] == INCOMPLETE), 'config identity')
    need(qf(cfg['lambda_plus']) == LP and Dyadic.from_json(cfg['s_neg']) == SN, 'config endpoints')
    sneg_proof()
    bud = cfg['budgets']
    keys(bud, {'max_depth', 'max_evaluations', 'max_tiles'}, 'budgets')
    for v in bud.values():
        need(isinstance(v, int) and (not isinstance(v, bool)) and (v > 0), 'budget')
    sch = schedule(cfg)
    parsed = parse_canonical_jsonl(rb)
    rs = [x for x, _ in parsed]
    need(rs, 'records')
    h = sha256_hex(cb)
    prev = genesis(h)
    for r in rs:
        need(r.get('previous_record_sha256') == prev and r.get('record_sha256') == rhash(r), 'chain')
        prev = r['record_sha256']
    hd = rs[0]
    need(hd.get('record_type') == 'RUN_HEADER' and hd.get('blocal_run_config_sha256') == h and (hd.get('chain_genesis') == genesis(h)) and (hd.get('canonicalizer_id') == CANON) and (hd.get('adapter_source_sha256') == cfg['adapter_source_sha256']), 'header')
    cur = 1
    totals = {'L1': 0, 'L2': 0, 'L3': 0}
    selected = None
    attempted = 0
    jcount = 0
    for ci, (inc, um) in enumerate(sch):
        s, u = (inc.as_fraction(), um.as_fraction())
        lam = LP + s
        cur, a, ba, n1 = tiles(rs, cur, ci, 'L1', u, s, SN.as_fraction(), bud)
        totals['L1'] += n1
        cur, b, bb, n2 = tiles(rs, cur, ci, 'L2', u, s, SN.as_fraction(), bud)
        totals['L2'] += n2
        cur, c, bc, n3 = tiles(rs, cur, ci, 'L3', u, s, SN.as_fraction(), bud)
        totals['L3'] += n3
        signs = a and b and c
        budgets = ba and bb and bc
        ji = None
        if cur < len(rs) and rs[cur].get('record_type') == 'J_START':
            need(signs and budgets, 'J_START failed candidate')
            ji = jstart(rs[cur], ci, lam)
            cur += 1
            jcount += 1
        need(cur < len(rs) and rs[cur].get('record_type') == 'CANDIDATE_SUMMARY', 'candidate summary')
        x = rs[cur]
        cur += 1
        attempted += 1
        need(x.get('candidate_index') == ci and qf(x.get('lambda_start')) == lam and (df(x.get('u_max')) == u), 'candidate summary identity')
        need(x.get('coverage_counts') == {'L1': n1, 'L2': n2, 'L3': n3}, 'coverage counts')
        accepted = x.get('candidate_accepted') is True
        need(accepted == (signs and budgets and (ji is not None)), 'acceptance')
        need(x.get('budget_exceeded') is (not budgets), 'budget summary')
        need(x.get('unresolved') is (not signs), 'unresolved summary')
        if accepted:
            selected = (ci, lam, u, ji)
            break
        need(x.get('first_failure_reason') not in (None, ''), 'failure reason')
    need(cur < len(rs) and rs[cur].get('record_type') == 'RUN_SUMMARY', 'run summary')
    x = rs[cur]
    cur += 1
    need(cur == len(rs), 'record after summary')
    need(x.get('records_chain_tip_sha256') == x.get('previous_record_sha256'), 'summary chain tip')
    exact = {'attempted_candidates': attempted, 'tile_records': sum(totals.values()), 'j_start_records': jcount, 'candidate_summaries': attempted}
    need(x.get('exact_counts') == exact, 'summary counts')
    if selected is not None:
        ci, lam, u, ji = selected
        need(x.get('terminal_state') == COMPLETE, 'complete state')
        need(x.get('selected_candidate_index') == ci and qf(x.get('lambda_start')) == lam and (df(x.get('u_max')) == u) and (x.get('start_root_interval') == ji), 'complete summary')
        expected = complete_mc(ci, lam, ji, totals, len(rs), x['previous_record_sha256'])
        state = COMPLETE
    else:
        need(attempted == len(sch) and jcount == 0, 'incomplete attempted/J_START')
        need(x.get('terminal_state') == INCOMPLETE and x.get('selected_candidate_index') is None and (x.get('lambda_start') is None) and (x.get('u_max') is None) and (x.get('start_root_interval') is None), 'incomplete summary')
        expected = incomplete_mc(totals, len(rs), x['previous_record_sha256'])
        state = INCOMPLETE
    if certb:
        verify_certificate(certb, expected)
    return {'attempted_candidates': attempted, 'selected_candidate_index': selected[0] if selected else None, 'tile_records': sum(totals.values()), 'terminal_state': state, 'state': 'BLOCAL_VERIFICATION_CANDIDATE'}
