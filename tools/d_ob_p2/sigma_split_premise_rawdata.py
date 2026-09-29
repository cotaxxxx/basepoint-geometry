#!/usr/bin/env python3
"""Raw data for auditing the sigma-split claim behind near_sigma_split_measure.py.
DIAGNOSTIC / NOT_EVIDENCE.  Prints numbers only; no thresholds, no verdict.
Computes no L, W or margin value and does not import near_sigma_split_measure.py.

The claim to audit: for a regular near cell,
    K_H(rho) = [F_rho(rho) - F_rho(-rho)]/(2 rho) = (1/2) int_{-1}^{1} F_rhorho(sigma*rho) dsigma   (FTC)
and the producer's kernel_point(..., second=True) evaluates F_rhorho.  The identity holds when
s -> F_rho(s) is C^1 on [-rho, rho]; the premise data below is what that needs.

Tables (one row per (point, mu, phi)):
  T1 FTC residual   : K_H from the independent F_rho (independent_H_sign.py, pinned) versus
                      (1/2) int F_rhorho(sigma rho) dsigma, with F_rhorho by central difference
                      of the same independent F_rho and the integral by scipy quad.
  T2 implementation : the pinned producer's kernel_point(second=True) at point balls
                      (s = sigma*rho, sigma in {-1,-1/2,0,1/2,1}) versus the independent
                      central-difference F_rhorho(s); rel_diff and whether the float lies
                      inside the ball.
  T3 premise        : along s = sigma*rho, sigma on a 201-point grid: min/max of
                      gamma = h/(w D) before clipping, min h, min D; counts of grid points where
                      gamma would be clipped to [0,1].
Summary lines give max/min of each column.

Point set: (i_r, i_t, i_l) in {0,5,10,15} x {13,14,15} x {0,15} with the probe convention
r = 7/8 + (2 i_r + 1)/256, t = 7/8 + (2 i_t + 1)/256, lambda = 2/5 + 13/3200 (2 i_l + 1)/2;
(mu, phi) on a 16 x 8 midpoint grid of [-1,1] x [0,pi].
Usage: sigma_split_premise_rawdata.py --producer PINNED_PRODUCER.py [--out OUT.tsv]
"""
import argparse
import hashlib
import importlib.util
import math
import sys
from fractions import Fraction as Q
from pathlib import Path

from scipy.integrate import quad

PRODUCER_SHA = "dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b"
HSIGN_SHA = "2dcd16673c214369ba0555e653dae51fca7d3f3cf13c83aeac4fd000d5bfccd7"
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(path, name, want):
    got = sha(path)
    if got != want:
        sys.exit(f"ABORT {name} SHA mismatch: {got}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--producer", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    P = load(a.producer, "pinned_producer", PRODUCER_SHA)
    h = load(HERE / "independent_H_sign.py", "independent_H_sign", HSIGN_SHA)
    P.ctx.prec = P.BITS
    arb = P.arb

    def frr(mu, ph, s, z, lam):
        d = 1e-6 * max(1.0, abs(s))
        return (h.Frho(mu, ph, s + d, z, lam) - h.Frho(mu, ph, s - d, z, lam)) / (2 * d)

    def raw_gamma(mu, ph, s, z, lam):
        aa = math.sqrt(max(0.0, 1 - mu * mu)); b = aa * math.cos(ph)
        hh = lam * (1 - s * b) - z * mu
        w = math.sqrt(lam * lam * aa * aa + mu * mu)
        D = math.sqrt((b - s) ** 2 + (aa * math.sin(ph)) ** 2 + (lam * mu - z) ** 2)
        return hh / (w * D), hh, D

    out = open(a.out, "x") if a.out else sys.stdout
    w = lambda *x: print("\t".join(map(str, x)), file=out, flush=True)
    w("# DIAGNOSTIC / NOT_EVIDENCE", f"producer={PRODUCER_SHA}", f"independent_H_sign={HSIGN_SHA}",
      f"script={sha(__file__)}")
    w("point", "mu", "phi", "rho", "z", "lam",
      "T1_KH_diff", "T1_KH_ftc", "T1_rel_resid",
      "T2_max_rel_diff", "T2_outside_ball",
      "T3_gamma_min", "T3_gamma_max", "T3_h_min", "T3_D_min", "T3_clip_count")
    sig5 = [-1.0, -0.5, 0.0, 0.5, 1.0]
    grid = [-1 + 2 * i / 200 for i in range(201)]
    agg = {"T1": 0.0, "T2": 0.0, "T2out": 0, "gmin": 9.0, "gmax": -9.0, "hmin": 9e9, "Dmin": 9e9, "clip": 0, "rows": 0}
    for ir in (0, 5, 10, 15):
        for it in (13, 14, 15):
            for il in (0, 15):
                r = Q(7, 8) + Q(2 * ir + 1, 256); t = Q(7, 8) + Q(2 * it + 1, 256)
                lq = Q(2, 5) + Q(13, 3200) * Q(2 * il + 1, 2)
                rho = float(r * (1 - t * t) / (1 + t * t)); z = float(lq * r * 2 * t / (1 + t * t)); lam = float(lq)
                for i in range(16):
                    mu = -1 + (2 * i + 1) / 16
                    for j in range(8):
                        ph = math.pi * (2 * j + 1) / 16
                        kd = (h.Frho(mu, ph, rho, z, lam) - h.Frho(mu, ph, -rho, z, lam)) / (2 * rho)
                        kf = 0.5 * quad(lambda sg: frr(mu, ph, sg * rho, z, lam), -1, 1,
                                        epsabs=1e-12, epsrel=1e-10, limit=200)[0]
                        t1 = abs(kd - kf) / max(1e-300, abs(kd))
                        am = math.sqrt(1 - mu * mu)
                        ma, aa_, cp, sp, la = arb(mu), arb(am), arb(math.cos(ph)), arb(math.sin(ph)), arb(lam)
                        t2 = 0.0; out2 = 0
                        for sg in sig5:
                            s = sg * rho
                            try:
                                kb = P.kernel_point(arb(s), arb(z), ma, aa_, cp, sp, la, True)
                            except Exception:
                                out2 += 1; continue
                            fv = frr(mu, ph, s, z, lam)
                            t2 = max(t2, abs(float(kb.mid()) - fv) / max(1e-300, abs(fv)))
                            if not (float(kb.lower()) - 1e-7 * max(1, abs(fv)) <= fv <= float(kb.upper()) + 1e-7 * max(1, abs(fv))):
                                out2 += 1
                        gs = [raw_gamma(mu, ph, sg * rho, z, lam) for sg in grid]
                        gmin = min(g[0] for g in gs); gmax = max(g[0] for g in gs)
                        hmin = min(g[1] for g in gs); Dmin = min(g[2] for g in gs)
                        clip = sum(1 for g in gs if not (0.0 <= g[0] <= 1.0))
                        w(f"({ir},{it},{il})", f"{mu:.6f}", f"{ph:.6f}", f"{rho:.6e}", f"{z:.6f}", f"{lam:.6f}",
                          f"{kd:+.12e}", f"{kf:+.12e}", f"{t1:.3e}", f"{t2:.3e}", out2,
                          f"{gmin:.9f}", f"{gmax:.9f}", f"{hmin:.6e}", f"{Dmin:.6e}", clip)
                        agg["T1"] = max(agg["T1"], t1); agg["T2"] = max(agg["T2"], t2); agg["T2out"] += out2
                        agg["gmin"] = min(agg["gmin"], gmin); agg["gmax"] = max(agg["gmax"], gmax)
                        agg["hmin"] = min(agg["hmin"], hmin); agg["Dmin"] = min(agg["Dmin"], Dmin)
                        agg["clip"] += clip; agg["rows"] += 1
    w("# SUMMARY", f"rows={agg['rows']}", f"T1_max_rel_resid={agg['T1']:.3e}", f"T2_max_rel_diff={agg['T2']:.3e}",
      f"T2_outside_ball_total={agg['T2out']}", f"T3_gamma_min={agg['gmin']:.9f}", f"T3_gamma_max={agg['gmax']:.9f}",
      f"T3_h_min={agg['hmin']:.6e}", f"T3_D_min={agg['Dmin']:.6e}", f"T3_clip_total={agg['clip']}")
    if a.out:
        out.close(); print(f"OUT_SHA256={sha(a.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
