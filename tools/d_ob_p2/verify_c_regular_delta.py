#!/usr/bin/env python3
import argparse,difflib,hashlib
from pathlib import Path
BASE='dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b'
DERIVED='b7ad3fbf7ca41539b43959fd3645a2e34d397decb175cf7511daa127cb6297d2'
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=argparse.ArgumentParser(); a.add_argument('base'); a.add_argument('derived'); x=a.parse_args()
if sh(x.base)!=BASE or sh(x.derived)!=DERIVED: raise SystemExit('PIN_MISMATCH')
b=Path(x.base).read_text().splitlines(); d=Path(x.derived).read_text().splitlines()
sm=list(difflib.SequenceMatcher(a=b,b=d).get_opcodes()); edits=[z for z in sm if z[0]!='equal']
if len(edits)!=1: raise SystemExit(f'DELTA_COUNT_{edits}')
tag,i1,i2,j1,j2=edits[0]
if tag!='replace' or b[i1:i2]!=['        take=(nreg+3)//4'] or d[j1:j2]!=['        take=(nreg+1)//2']: raise SystemExit('DELTA_NOT_FROZEN_ONE_LINE')
print('C_REGULAR_ONE_LINE_DELTA_OK'); print('-'+b[i1]); print('+'+d[j1])
