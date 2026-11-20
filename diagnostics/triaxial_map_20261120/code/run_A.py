"""Run A driver: census over the main grid (PLAN.md).  Resumable JSONL.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, os, sys, time
import numpy as np
from census import census
out = sys.argv[1]
S = [4.0**(i/32) for i in range(33)]
T = [8.0**(j/40) for j in range(41)]
done = set()
if os.path.exists(out):
    for line in open(out):
        r = json.loads(line); done.add((r["i"], r["j"]))
jobs = sorted(((i, j) for i in range(33) for j in range(41) if (i, j) not in done), key=lambda ij: S[ij[0]]*T[ij[1]])
t0 = time.time()
with open(out, "a") as f:
    for c, (i, j) in enumerate(jobs):
        t1 = time.time()
        try:
            r = census(S[i], T[j])
        except Exception as e:      # recorded, never hidden
            r = dict(s=S[i], t=T[j], error=repr(e))
        r["i"] = i; r["j"] = j; r["seconds"] = time.time() - t1
        f.write(json.dumps(r) + "\n"); f.flush()
        if c % 25 == 0:
            print(c, len(jobs), i, j, round(time.time() - t0), flush=True)
