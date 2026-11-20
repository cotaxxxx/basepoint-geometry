"""audit_points.py -- independent point-containment audit of the Codex ledgers
(D_TRI_RECTANGLE_INTERVAL_20261120.zip, sha256 60b8384d...c10573) with this directory's own kernel.

For every ledger row whose quantity can be identified from the Codex report / plans, the quantity is
recomputed here (non-interval, different quadrature, different code) at the centre and the corners of
the row's box and tested for membership in the row's enclosure [lower, upper].
A miss beyond the quadrature tolerance would contradict the enclosure.  Hits prove nothing about the
enclosures (this is a floating consistency test, not a verification of the interval arithmetic).

Run as:  python3 -I audit_points.py <extracted Codex out/ dir> <output json>
The Codex files are read as data only; none of the Codex code is imported or executed.
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import csv, json, os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import numpy as np
import triax
from shear import shear_tensor

SRC, OUTJ = sys.argv[1], sys.argv[2]
DEN = 5242880.0
EYE = np.eye(3)


def rd(name):
    with open(os.path.join(SRC, name), newline="") as f:
        return list(csv.DictReader(f))


def nclass(a):
    return 256 if a <= 6 else 384 if a <= 12 else 576


def evb(L, Q):
    """batched kernel evaluation, node count chosen by aspect ratio"""
    L = np.asarray(L, float).reshape(-1, 3); Q = np.asarray(Q, float).reshape(-1, 3)
    out = np.empty((len(L), 10))
    a = L.max(1)/L.min(1)
    cls = np.array([nclass(x) for x in a])
    for n in np.unique(cls):
        m = cls == n
        out[m] = triax.ev(L[m], Q[m], (int(n), int(n)))
    return out


def shape(s, t):
    return np.array([1.0, s, s*t])


class Tally:
    def __init__(self, name, tol):
        self.name, self.tol = name, tol
        self.rows = 0; self.points = 0; self.miss = 0; self.worst = 0.0; self.examples = []; self.minwidth = np.inf; self.minslack = np.inf

    def add(self, vals, lo, hi, tag):
        self.rows += 1; self.minwidth = min(self.minwidth, hi - lo)
        for v in np.atleast_1d(vals):
            self.points += 1
            viol = max(lo - v, v - hi)
            self.minslack = min(self.minslack, -viol)
            if viol > self.tol:
                self.miss += 1; self.worst = max(self.worst, viol)
                if len(self.examples) < 5:
                    self.examples.append(dict(tag=tag, value=float(v), lower=lo, upper=hi))

    def summary(self):
        return dict(ledger=self.name, rows=self.rows, points=self.points, misses=self.miss, tol=self.tol,
                    worst_violation=self.worst, min_enclosure_width=float(self.minwidth),
                    min_slack_inside=float(self.minslack), examples=self.examples)


def corners(lo, hi):
    """centre + all corners of a box given as lists of (lo, hi) per coordinate (degenerate coords collapse)"""
    pts = {tuple(0.5*(a + b) for a, b in zip(lo, hi))}
    for c in itertools.product(*[(a, b) if b > a else (a,) for a, b in zip(lo, hi)]):
        pts.add(c)
    return sorted(pts)


res = []
RESUME = os.environ.get("AUDIT_RESUME") == "1" and os.path.exists(os.path.join(HERE, "audit_points.partial.json"))
if RESUME:      # reuse the ledger tallies of an interrupted run; only the single-point part is recomputed
    res = json.load(open(os.path.join(HERE, "audit_points.partial.json")))
    own = dict(resumed_from_partial=True)
HEAVY = not RESUME
# ---------------------------------------------------------------- A. nodes.csv : h_1,h_2,h_3 at 97 x 129 Lobatto nodes
if HEAVY:
    rows = rd("nodes.csv")
    S = np.array([2.1 + 1.1*np.cos(np.pi*int(r["i"])/96) for r in rows]); T = np.array([3.5 + 2.5*np.cos(np.pi*int(r["j"])/128) for r in rows])
    o = evb(np.stack([np.ones_like(S), S, S*T], 1), np.zeros((len(S), 3)))
    ty = Tally("nodes.csv (h_1,h_2,h_3 at the Lobatto nodes)", 3e-10)
    for k, r in enumerate(rows):
        for i in range(3):
            ty.add(o[k, 4 + i], float(r["h%dlo" % (i + 1)]), float(r["h%dhi" % (i + 1)]), "i=%s j=%s axis=%d" % (r["i"], r["j"], i + 1))
    res.append(ty.summary()); print(res[-1], flush=True)
    # convergence of this audit's own values on the most elongated nodes
    chk = [(3.2, 6.0), (3.2, 4.0), (2.1, 6.0), (1.0, 6.0), (3.2, 1.0)]
    d = max(float(np.abs(triax.ev(shape(s, t), [0, 0, 0], (nclass(s*t),)*2) - triax.ev(shape(s, t), [0, 0, 0], (960, 960)))[4:7].max()) for s, t in chk)
    own = dict(centre_hessian_selfconvergence=d)

    # ---------------------------------------------------------------- generic (s,t)-box ledgers of h_i or b_i
    def st_ledger(name, fn_of_row, title, tol=1e-8, deriv=False):
        rows = rd(name)
        ty = Tally(title, tol); td = Tally(title + " : d/dt at the box centre", 1e-5) if deriv else None
        L = []; Q = []; idx = []; comp = []
        for k, r in enumerate(rows):
            kind, i = fn_of_row(r)
            if kind is None:
                continue
            s0, s1, t0, t1 = (int(r[c])/DEN for c in ("s0", "s1", "t0", "t1"))
            for (s, t) in corners((s0, t0), (s1, t1)):
                L.append(shape(s, t)); Q.append(np.zeros(3) if kind == "h" else EYE[i]); idx.append(k); comp.append(4 + i if kind == "h" else 1 + i)
        o = evb(L, Q); idx = np.array(idx); comp = np.array(comp)
        for k, r in enumerate(rows):
            m = idx == k
            if m.any():
                ty.add(o[m, comp[m][0]], float(r["lower"]), float(r["upper"]), "row %d" % k)
        return ty

    # central.csv : final h_i ledger
    ty = st_ledger("central.csv", lambda r: ("h", int(r["axis"]) - 1), "central.csv (h_axis on shape boxes)")
    res.append(ty.summary()); print(res[-1], flush=True)
    # axis_cover.csv / bfinish.csv : mode 0 = centre eigenvalue, mode 1 = pole trace (interpretation tested both ways)
    for name in ("axis_cover.csv", "bfinish.csv"):
        for interp, f in (("mode0=h, mode1=b", lambda r: (("h" if r["mode"] == "0" else "b"), int(r["axis"]) - 1)),
                          ("mode0=b, mode1=h", lambda r: (("b" if r["mode"] == "0" else "h"), int(r["axis"]) - 1))):
            ty = st_ledger(name, f, "%s (%s)" % (name, interp))
            res.append(ty.summary()); print(res[-1], flush=True)
    # long_end.csv : b_3
    ty = st_ledger("long_end.csv", lambda r: ("b", 2), "long_end.csv (b_3 = E_3(e_3) on shape boxes)")
    res.append(ty.summary()); print(res[-1], flush=True)

    # ---------------------------------------------------------------- long_axis.csv : mode 0 = H_33(r e_3), mode 1 = E_3(r e_3)/r
    rows = rd("long_axis.csv")
    for interp in ("mode0=H33, mode1=E3/r",):
        ty = {"0": Tally("long_axis.csv mode 0 (H_33 on the long axis)", 1e-7), "1": Tally("long_axis.csv mode 1 (E_3(r e_3)/r)", 1e-7)}
        L = []; Q = []; idx = []
        for k, r in enumerate(rows):
            b = [int(r[c])/DEN for c in ("s0", "s1", "t0", "t1", "r0", "r1")]
            for (s, t, rr) in corners((b[0], b[2], b[4]), (b[1], b[3], b[5])):
                L.append(shape(s, t)); Q.append(rr*EYE[2]); idx.append(k)
        o = evb(L, Q); idx = np.array(idx); Q = np.array(Q)
        for k, r in enumerate(rows):
            m = idx == k
            if r["mode"] == "0":
                mm = m & (Q[:, 2] < 1 - 1e-12)
                v = o[mm, 6]
            else:
                mm = m & (Q[:, 2] > 1e-12)
                v = o[mm, 3]/Q[mm, 2]
            ty[r["mode"]].add(v, float(r["lower"]), float(r["upper"]), "row %d (%s)" % (k, r["result"]))
        for v in ty.values():
            res.append(v.summary()); print(res[-1], flush=True)

    # ---------------------------------------------------------------- cal.csv : mode 1 E_3/q_3, mode 2 T_12/(q_1 q_2), mode 3 H_33
    rows = rd("cal.csv")
    ty = {"1": Tally("cal.csv mode 1 (E_3/q_3 on 5-dim boxes)", 1e-7), "2": Tally("cal.csv mode 2 (T_12/(q_1 q_2) = C_12)", 1e-7),
          "3": Tally("cal.csv mode 3 (H_33)", 1e-7)}
    skipped = 0
    for k, r in enumerate(rows):
        sb = [int(r[c])/DEN for c in ("s0", "s1", "t0", "t1")]
        qb = [int(r[c])/DEN for c in ("q10", "q11", "q20", "q21", "q30", "q31")]
        shp = corners((sb[0], sb[2]), (sb[1], sb[3]))
        pos = corners((qb[0], qb[2], qb[4]), (qb[1], qb[3], qb[5]))
        pos = [p for p in pos if np.linalg.norm(p) <= 1.0]
        pts = [(s, t, p) for (s, t) in shp for p in pos]
        if r["mode"] == "2":
            pts = [x for x in pts if x[2][0] > 1e-9 and x[2][1] > 1e-9 and x[0] > 1 + 1e-9]
        if r["mode"] == "1":
            pts = [x for x in pts if x[2][2] > 1e-9]
        if r["mode"] == "3":
            pts = [x for x in pts if np.linalg.norm(x[2]) < 1 - 1e-9]
        if not pts:
            skipped += 1; continue
        o = evb([shape(s, t) for s, t, p in pts], [p for s, t, p in pts])
        P = np.array([p for s, t, p in pts]); Sv = np.array([s for s, t, p in pts])
        if r["mode"] == "1":
            v = o[:, 3]/P[:, 2]
        elif r["mode"] == "2":
            v = (o[:, 2]/P[:, 1] - o[:, 1]/P[:, 0])/(Sv - 1/Sv)      # C_12 through the shear identity (S3)
        else:
            v = o[:, 6]
        ty[r["mode"]].add(v, float(r["lower"]), float(r["upper"]), "row %d patch %s stage %s" % (k, r["patch"], r["stage"]))
    for v in ty.values():
        res.append(v.summary()); print(res[-1], flush=True)
    own["cal_rows_without_testable_point"] = skipped

    # ---------------------------------------------------------------- disk.csv : tau = T_11 - T_22 at r e_1, s = 1 ; tau2 = d^2 tau/dr^2
    rows = rd("disk.csv")
    ty = {"tau": Tally("disk.csv tau (T_11 - T_22 at r e_1, s = 1)", 1e-8), "tau2": Tally("disk.csv tau2 (d^2 tau / dr^2, centre of the box only)", 2e-4)}
    def tau(r, t):
        Tm = shear_tensor([1.0, 1.0, t], np.array([r, 0.0, 0.0]), (192, 192))
        return Tm[0, 0] - Tm[1, 1]
    for k, r in enumerate(rows):
        t0, t1, r0, r1 = (int(r[c])/DEN for c in ("t0", "t1", "r0", "r1"))
        if r["mode"] == "tau":
            v = [tau(rr, t) for (t, rr) in corners((t0, r0), (t1, r1))]
        else:
            rc, tc, h = 0.5*(r0 + r1), 0.5*(t0 + t1), 2e-3
            v = [(tau(rc + h, tc) - 2*tau(rc, tc) + tau(max(rc - h, 0.0), tc))/h**2] if rc - h >= 0 else []
            if not v:
                continue
        ty[r["mode"]].add(v, float(r["lower"]), float(r["upper"]), "row %d" % k)
    for v in ty.values():
        res.append(v.summary()); print(res[-1], flush=True)

    # ---------------------------------------------------------------- hb.csv / bridge.csv mode 1 : normalised slope kappa_i'(r)/r
    for name in ("hb.csv", "bridge.csv"):
        rows = rd(name)
        ty = Tally("%s mode 1 (kappa_i'/r = (r E_ii - E_i)/r^3)" % name, 1e-6)
        for k, r in enumerate(rows):
            if r["mode"] != "1":
                continue
            i = int(r["axis"]) - 1
            b = [int(r[c])/DEN for c in ("s0", "s1", "t0", "t1", "r0", "r1")]
            pts = [x for x in corners((b[0], b[2], b[4]), (b[1], b[3], b[5])) if 1e-6 < x[2] < 1 - 1e-9]
            if not pts:
                continue
            o = evb([shape(s, t) for s, t, rr in pts], [rr*EYE[i] for s, t, rr in pts])
            R = np.array([x[2] for x in pts])
            ty.add((R*o[:, 4 + i] - o[:, 1 + i])/R**3, float(r["lower"]), float(r["upper"]), "row %d" % k)
        res.append(ty.summary()); print(res[-1], flush=True)

    json.dump(res, open(os.path.join(HERE, "audit_points.partial.json"), "w"), indent=1, default=float)
# ---------------------------------------------------------------- single-point ledgers
pt = []
for name in ("endpoints.csv", "cross.csv"):
    for r in rd(name):
        if r["derivative"] != "0" or r["s0"] != r["s1"] or r["t0"] != r["t1"]:
            continue
        s, t = int(r["s0"])/1e6, int(r["t0"])/1e6; i = int(r["axis"]) - 1
        o = triax.ev_big(shape(s, t), np.zeros(3) if r["mode"] == "0" else EYE[i], (768, 768))
        v = o[4 + i] if r["mode"] == "0" else o[1 + i]
        pt.append(dict(ledger=name, mode=r["mode"], axis=i + 1, s=s, t=t, N=r["N"], value=float(v), lower=float(r["lower"]), upper=float(r["upper"]),
                       inside=bool(float(r["lower"]) <= v <= float(r["upper"]))))
for r in rd("census.csv"):
    s0, s1, t0 = int(r["s0"])/DEN, int(r["s1"])/DEN, int(r["t0"])/DEN; i = int(r["axis"]) - 1
    for s in (s0, s1):
        o = triax.ev_big(shape(s, t0), np.zeros(3), (512, 512)); p = triax.ev_big(shape(s, t0), EYE[i], (512, 512))
        vh, vb = float(o[4 + i]), float(p[1 + i]); lo, hi = float(r["lower"]), float(r["upper"])
        pt.append(dict(ledger="census.csv", mode=r["mode"], axis=i + 1, s=s, t=t0, N=r["N"], h=vh, b=vb, lower=lo, upper=hi,
                       inside_as_h=bool(lo <= vh <= hi), inside_as_b=bool(lo <= vb <= hi), expected_sign=r["expected_sign"]))
# rim.csv : one-sided Hessian at q = e_1 (limit r -> 1 from inside)
rim = []
for r in rd("rim.csv"):
    s0, s1, t0, t1 = (int(r[c])/DEN for c in ("s0", "s1", "t0", "t1"))
    for (s, t) in corners((s0, t0), (s1, t1)):
        seq = [triax.ev_big(shape(s, t), [1 - 10.0**-m, 0, 0], (1536, 1536))[4:7].tolist() for m in (4, 6, 8)]
        H = seq[-1]
        rim.append(dict(mode=r["mode"], s=s, t=t, H_at_1e4_1e6_1e8=seq,
                        inside=[bool(float(r["H%dlo" % a]) <= H[k] <= float(r["H%dhi" % a])) for k, a in enumerate((11, 22, 33))],
                        box=[[float(r["H%dlo" % a]), float(r["H%dhi" % a])] for a in (11, 22, 33)]))
json.dump(dict(source_zip_sha256="60b8384d3e8ac105f53808c01e11b66fc6ada99546d96af04b5ee6b676c10573", ledgers=res, points=pt, rim=rim, own=own),
          open(OUTJ, "w"), indent=1, default=float)
print("points:", sum(1 for p in pt if p.get("inside", True) is False), "outside of", len(pt))
print("rim:", [(x["mode"], x["inside"]) for x in rim])
print("own:", own)
