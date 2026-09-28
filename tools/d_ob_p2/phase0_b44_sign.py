#!/usr/bin/env python3
"""D-OB P2 SPEC V3 comparison predeclare v1 (ea6214e2, 9cae171b...) -- Phase 0 harness.
DIAGNOSTIC / NOT_EVIDENCE. Floating-point, non-interval.

Math functions geom / F / Frho are imported unmodified from the pinned
independent_H_sign.py (SHA-256 2dcd1667..., cotaxxxx/basepoint-geometry
commit dabc2a3b); the harness refuses to run if that file does not match.
Only the quadrature driver, step sizes, input, decision and output are new.

Usage:
  python3 phase0_b44_sign.py --pinned independent_H_sign.py \
      --results results_192.tsv --out OUT_DIR [--workers 4]
Exit codes: 0 completed (gate label in summary), 2 INVALID (pin / input /
G4 failure), anything else = crash.
"""
import argparse, csv, hashlib, importlib.util, json, math, os, re, signal, sys, time, warnings
from fractions import Fraction as Q
from multiprocessing import Pool

sys.dont_write_bytecode = True
PREDECLARE = {"commit": "ea6214e2ff3cc491ccbef2a849a67a0f0597aa74",
              "sha256": "9cae171b46e66f1d5ab3fd61eee2da06c1656816c2121f0b5a49b19caaf6e11f"}
PINNED_SHA = "2dcd16673c214369ba0555e653dae51fca7d3f3cf13c83aeac4fd000d5bfccd7"
RESULTS_SHA = "6ad29461e42c265ce136e8df114400072e939335d72e2033b79741461e93fa90"
N_EXPECTED = 44
BOX = {"initial": (7, 7, 0), "r": (Q(7, 8), Q(1)), "t": (Q(7, 8), Q(1)), "lam": (Q(2, 5), Q(93, 200))}
R0, T0, L0 = Q(7, 8), Q(7, 8), Q(2, 5)
WR, WT, WL = Q(1, 128), Q(1, 128), Q(13, 3200)
POINTS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
TOL = {"standard": {"inner": (1e-11, 1e-10, 200), "outer": (1e-10, 1e-9, 400)},
       "tightened": {"inner": (1e-12, 1e-11, 200), "outer": (1e-11, 1e-10, 400)}}
STEPS = [("1e-2", 1e-2), ("1e-3", 1e-3), ("1e-4", 1e-4)]   # d = factor * rho
D0 = "1e-4"
REL = 1e-4
LABEL = "DIAGNOSTIC / NOT_EVIDENCE"

M = None  # pinned module (geom / F / Frho), loaded per process


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_pinned(path):
    if sha256_file(path) != PINNED_SHA:
        raise SystemExit(2)
    spec = importlib.util.spec_from_file_location("independent_H_sign_pinned", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def init_worker(path):
    global M
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    M = load_pinned(path)


def mu_int(f, args, tol):
    """Same partition as the pinned driver (mu in [-1,0] plain; [0,1] via mu = 1 - s^2),
    with tolerances and breakpoints taken from predeclare v1 section 6."""
    from scipy.integrate import quad
    ia, ir, il = tol["inner"]; oa, orr, ol = tol["outer"]
    inner = lambda mu: quad(lambda ph: f(mu, ph, *args), 0, math.pi, epsabs=ia, epsrel=ir, limit=il)[0]
    lo = quad(inner, -1, 0, epsabs=oa, epsrel=orr, limit=ol)[0]
    hi = quad(lambda s: inner(1 - s * s) * 2 * s, 0, 1, epsabs=oa, epsrel=orr, limit=ol, points=POINTS)[0]
    return lo + hi


def H_B(rho, z, lam, tol):
    KH = lambda mu, ph, rho, z, lam: (M.Frho(mu, ph, rho, z, lam) - M.Frho(mu, ph, -rho, z, lam)) / (2 * rho)
    return mu_int(KH, (rho, z, lam), tol) / (2 * math.pi * lam)


def H_A(rho, z, lam, d, tol):
    E = lambda r: mu_int(M.F, (r, z, lam), tol) / (2 * math.pi * lam)
    return (E(rho + d) - E(rho - d)) / (2 * d) / rho


def compute(pt):
    rho, z, lam = pt["rho"], pt["z"], pt["lam"]
    out = {"key": pt["key"], "values": {}, "warnings": [], "errors": []}
    for tname, tol in TOL.items():
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                out["values"][f"B_{tname}"] = H_B(rho, z, lam, tol)
            except Exception as e:
                out["errors"].append(f"B_{tname}: {type(e).__name__}: {e}")
            for sname, fac in STEPS:
                try:
                    out["values"][f"A{sname}_{tname}"] = H_A(rho, z, lam, fac * rho, tol)
                except Exception as e:
                    out["errors"].append(f"A{sname}_{tname}: {type(e).__name__}: {e}")
            out["warnings"] += [f"{tname}: {x.category.__name__}: {str(x.message).splitlines()[0]}" for x in w]
    return out


def rel_ok(a, b):
    return abs(a - b) <= REL * min(abs(a), abs(b))


def decide(v, errors):
    """Predeclare v1 section 7. Criterion 4 is applied to Route B and baseline Route A (d0)."""
    need = [f"B_{t}" for t in TOL] + [f"A{s}_{t}" for s, _ in STEPS for t in TOL]
    reasons = []
    if errors or any(k not in v or not math.isfinite(v[k]) for k in need):
        return "INCONCLUSIVE", ["nonfinite_or_failure"]
    hb, ha = v["B_standard"], v[f"A{D0}_standard"]
    signs = {math.copysign(1, v[f"A{s}_standard"]) for s, _ in STEPS if v[f"A{s}_standard"] != 0}
    if hb == 0 or ha == 0 or math.copysign(1, hb) != math.copysign(1, ha):
        reasons.append("c1_route_sign_mismatch")
    if len(signs) != 1 or any(v[f"A{s}_standard"] == 0 for s, _ in STEPS):
        reasons.append("c2_step_sign_mismatch")
    if not rel_ok(hb, ha):
        reasons.append("c3_route_gap")
    for k in ("B", f"A{D0}"):
        if not rel_ok(v[f"{k}_standard"], v[f"{k}_tightened"]):
            reasons.append(f"c4_tolerance_{k}")
    if reasons:
        return "INCONCLUSIVE", reasons
    return ("POSITIVE" if hb > 0 else "NEGATIVE"), []


SYN = {"r": ["r"], "t": ["t"], "lam": ["lambda", "lam"], "stop": ["stopreason", "stop", "reason"],
       "L": ["llower", "lower"]}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def num(s):
    s = s.strip().strip("[]").split("+/-")[0].strip()
    return Q(s)


def build_b44(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8"), delimiter="\t"))
    normed = {norm(h): h for h in rows[0].keys()}
    col = {}
    for k, syns in SYN.items():
        hit = [normed[s] for s in syns if s in normed]
        if not hit:
            raise ValueError(f"column {k} not found in {list(rows[0].keys())}")
        col[k] = hit[0]
    pts = []
    for row in rows:
        stop, L = row[col["stop"]].strip(), num(row[col["L"]])
        if not (stop == "max_cell_count" and L > 0):      # class B := max_cell_count and L.lower > 0
            continue
        r, t, lam = num(row[col["r"]]), num(row[col["t"]]), num(row[col["lam"]])
        ir, it, il = (int(math.floor((r - R0) / WR)), int(math.floor((t - T0) / WT)), int(math.floor((lam - L0) / WL)))
        rc, tc, lc = R0 + WR * Q(2 * ir + 1, 2), T0 + WT * Q(2 * it + 1, 2), L0 + WL * Q(2 * il + 1, 2)
        for a, b in ((r, rc), (t, tc), (lam, lc)):
            if abs(float(a) - float(b)) > 1e-12:
                raise ValueError(f"row is not a cell centre: {(ir, it, il)}")
        rho = rc * (1 - tc * tc) / (1 + tc * tc); z = lc * rc * 2 * tc / (1 + tc * tc)
        pts.append({"key": f"{ir},{it},{il}", "cell": [ir, it, il], "r": rc, "t": tc, "lam_q": lc,
                    "rho": float(rho), "z": float(z), "lam": float(lc)})
    return pts


def g4(pt):
    return all(BOX[k][0] <= v <= BOX[k][1] for k, v in (("r", pt["r"]), ("t", pt["t"]), ("lam", pt["lam_q"])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pinned", required=True); ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    start = time.time()
    os.makedirs(a.out, exist_ok=False)
    log = lambda m: print(m, flush=True)
    header = {"label": LABEL, "predeclare": PREDECLARE, "harness_sha256": sha256_file(__file__),
              "pinned_path": os.path.abspath(a.pinned), "pinned_sha256": sha256_file(a.pinned),
              "results_sha256": sha256_file(a.results), "tolerances": TOL, "points": POINTS,
              "steps_rho_factor": [s for s, _ in STEPS], "d0": D0, "rel": REL,
              "criterion4_routes": ["B", f"A{D0}"], "J_from_H": "J = 2*pi*lambda*H",
              "class_B_rule": "stop_reason == max_cell_count and L.lower > 0",
              "c5": "not used in Phase 0", "utc_start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    json.dump(header, open(os.path.join(a.out, "header.json"), "w"), indent=2, sort_keys=True)
    if header["pinned_sha256"] != PINNED_SHA or header["results_sha256"] != RESULTS_SHA:
        log("INVALID pin mismatch"); return 2
    pts = build_b44(a.results)
    if len(pts) != N_EXPECTED:
        log(f"INVALID B44 count {len(pts)}"); return 2
    bad = [p["key"] for p in pts if not g4(p)]
    if bad:
        log(f"INVALID G4 {bad}"); return 2
    log(f"B44 built: {len(pts)} points, G4 all pass")
    with Pool(a.workers, initializer=init_worker, initargs=(a.pinned,)) as pool:
        results = list(pool.imap(compute, pts))
    rows, counts = [], {"POSITIVE": 0, "NEGATIVE": 0, "INCONCLUSIVE": 0}
    for p, res in zip(pts, results):
        label, reasons = decide(res["values"], res["errors"])
        counts[label] += 1
        v = res["values"]
        rows.append({"key": p["key"], "r": str(p["r"]), "t": str(p["t"]), "lambda": str(p["lam_q"]),
                     "rho": p["rho"], "z": p["z"], "lambda_minus_z": p["lam"] - p["z"],
                     **{k: v.get(k) for k in sorted(v)},
                     "J_B_standard": 2 * math.pi * p["lam"] * v["B_standard"] if "B_standard" in v else None,
                     "label": label, "reasons": ";".join(reasons), "n_warnings": len(res["warnings"]),
                     "errors": ";".join(res["errors"])})
        log(f"{p['key']}\t{label}\tH_B={v.get('B_standard')}\t{';'.join(reasons)}")
    with open(os.path.join(a.out, "phase0_points.tsv"), "w", newline="") as f:
        f.write(f"# {LABEL}\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t"); w.writeheader(); w.writerows(rows)
    json.dump({p["key"]: r["warnings"] for p, r in zip(pts, results)}, open(os.path.join(a.out, "warnings.json"), "w"), indent=1)
    gate = "P0-B" if counts["NEGATIVE"] else ("P0-A" if counts["POSITIVE"] == N_EXPECTED else "P0-C")
    summary = {"label": LABEL, "counts": counts, "gate": gate, "utc_end": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "elapsed_seconds": round(time.time() - start, 1)}
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w"), indent=2, sort_keys=True)
    log(f"SUMMARY {json.dumps(summary, sort_keys=True)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
