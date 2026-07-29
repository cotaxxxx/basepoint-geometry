#!/usr/bin/env python3
"""Independent fixed-fixture canonical-byte equality audit; no calculation."""
from __future__ import annotations
import json
from pathlib import Path
import phase2_selftest as core

HERE=Path(__file__).resolve().parent
packs, manifest = core.unpack_all()
expect = packs['CONTROL_EXPECT.json']
fixtures = packs['CONTROL_FIXTURES.json']
if set(expect) != set(fixtures):
    raise SystemExit('control key mismatch')
mismatches=[]
for key in sorted(expect):
    fixture=fixtures[key]
    if fixture.get('fixture_id') != key:
        mismatches.append(key+':fixture_id')
        continue
    if core.cbytes(fixture.get('expected')) != core.cbytes(expect[key]):
        mismatches.append(key+':expected_bytes')
report={
    'schema':'ITEM3_SWEEP_PHASE2_FIXED_BYTE_AUDIT_V1',
    'control_count':len(expect),
    'fixed_expected_byte_equal_count':len(expect)-len(mismatches),
    'mismatches':mismatches,
    'kernel_evaluations':0,
    'arb_imported':False,
    'mathematical_calculations':0,
    'verdict':'PASS' if not mismatches else 'FAIL',
}
(HERE/'FIXED_BYTE_AUDIT.json').write_bytes(core.cbytes(report))
print(core.cbytes(report).decode())
raise SystemExit(0 if not mismatches else 1)
