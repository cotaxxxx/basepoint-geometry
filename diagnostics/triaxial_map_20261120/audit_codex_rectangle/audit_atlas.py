"""audit_atlas.py -- compare the curve sections of the Codex first atlas
(TRIAXIAL_FIRST_ATLAS_20261120.zip, sha256 259f7212...85b89f, out/sections.csv and out/special.csv)
with roots recomputed by this directory's independent kernel.  Non-interval.
Run as:  python3 -I audit_atlas.py <extracted Codex atlas out/ dir> <output json>
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import numpy as np
from scipy.optimize import brentq, fsolve
import triax
SRC, OUTJ = sys.argv[1], sys.argv[2]
EYE = np.eye(3)


def nn(a):
    n = 256 if a <= 8 else 512 if a <= 30 else 1024 if a <= 80 else 2048 if a <= 180 else 4096
    return (n, n)


def val(mode, i, s, t):
    l = np.array([1.0, s, s*t])
    return triax.ev_big(l, np.zeros(3), nn(s*t))[4 + i] if mode == "h" else triax.ev_big(l, EYE[i], nn(s*t))[1 + i]


rows = []
with open(os.path.join(SRC, "sections.csv"), newline="") as f:
    rd = list(csv.DictReader(f))
nmax = max(int(r["n"]) for r in rd)
for r in rd:
    if int(r["n"]) != nmax:
        continue
    s, t0, i, mode = float(r["s"]), float(r["t"]), int(r["axis"]) - 1, r["mode"]
    f = lambda t: val(mode, i, s, t)
    lo, hi = t0*(1 - 2e-3), t0*(1 + 2e-3)
    if lo < 1.0 and f(1.0)*f(hi) < 0:
        lo = 1.0
    if f(lo)*f(hi) > 0:
        rows.append(dict(s=s, mode=mode, axis=i + 1, t_codex=t0, note="no sign change of this kernel in a 0.2% bracket")); continue
    t = brentq(f, lo, hi, xtol=1e-13, rtol=1e-14)
    rows.append(dict(s=s, mode=mode, axis=i + 1, t_codex=t0, t_here=t, diff=t - t0))
    print("s=%-8g %s%d  codex %.12f  here %.12f  diff %+.2e" % (s, mode, i + 1, t0, t, t - t0), flush=True)
sp = []
with open(os.path.join(SRC, "special.csv"), newline="") as f:
    for r in csv.DictReader(f):
        if int(r["n"]) != nmax:
            continue
        s, t = float(r["s"]), float(r["t"])
        if r["event"] == "h1_b2":
            x = fsolve(lambda x: [val("h", 0, x[0], x[1]), val("b", 1, x[0], x[1])], [s, t], xtol=1e-14)
            sp.append(dict(event="h1_b2", codex=[s, t], here=[float(x[0]), float(x[1])], diff=[float(x[0] - s), float(x[1] - t)]))
        elif r["event"] in ("ob_h1", "ob_b1"):
            m = "h" if r["event"] == "ob_h1" else "b"
            x = brentq(lambda ss: val(m, 0, ss, 1.0), s*0.99, s*1.01, xtol=1e-14)
            sp.append(dict(event=r["event"], codex=[s, t], here=[float(x), 1.0], diff=[float(x - s), 0.0]))
        else:
            sp.append(dict(event=r["event"], codex=[s, t], here=None, note="extremum of a curve; value on the curve compared through sections"))
        print(sp[-1], flush=True)
d = [abs(r["diff"]) for r in rows if "diff" in r]
json.dump(dict(source_zip_sha256="259f721216b2c0b4348f1ccd3351f06b4500ff98903767875798ff778d85b89f", n_sections=len(rows),
               n_compared=len(d), max_abs_diff=max(d), sections=rows, special=sp), open(OUTJ, "w"), indent=1)
print("compared", len(d), "of", len(rows), "max |diff| =", max(d))
