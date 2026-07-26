"""Item 5: phi-split driver for the boundary energy E_lambda(1,0).

The center value E_lambda(0,0) is a fast 1D integral; the boundary value is a
2D adaptive validated integral and dominates the runtime.  Since

    E_lambda(1,0) = sum_k  (8/pi) int_{phi_k}^{phi_{k+1}} int_0^1 t^3 f dt dphi,

the phi-range can be split into independent pieces, each certified separately
and summed as balls.  This makes the cost fit inside bounded execution slots
and is exactly the decomposition used by the parallel CI jobs.

Tolerance policy: the endpoint margin of D on the bracket [3.43486, 3.43488]
is |D'| * halfwidth ~ 0.072 * 1e-5 ~ 7e-7, so per-piece tolerance 1e-7 (four
pieces) is what the proof needs; 1e-22 is 15 orders of overkill and is the
reason the serial run does not finish.

Usage:  python3 phi_split_driver.py <quantity> <piece> [tol] [dps]
  quantity: E1_lo | E1_hi | E1_mid | E1p_I   (boundary energy / derivative)
  piece:    0..3
Results accumulate in phi_split_state.json.
"""
import json
import sys
import time
from pathlib import Path

from flint import acb, arb, ctx, fmpq

import prolate_maxwell_arb_certificate as C

LAM = {
    "E1_lo": ("171743/50000", None),
    "E1_hi": ("85872/25000", None),
    "E1_mid": ("343487/100000", None),
    "E1p_I": ("171743/50000", "85872/25000"),
}
STATE = Path("phi_split_state.json")
NPIECE = 4


def lam_ball(key):
    lo, hi = LAM[key]
    if hi is None:
        q = fmpq(int(lo.split("/")[0]), int(lo.split("/")[1]))
        return arb(q)
    a = fmpq(int(lo.split("/")[0]), int(lo.split("/")[1]))
    b = fmpq(int(hi.split("/")[0]), int(hi.split("/")[1]))
    return arb((a + b) / 2, (b - a) / 2)


def piece(key, k, tol, depth, eval_limit):
    """(8/pi) * int over phi in [k, k+1]/NPIECE * (pi/2) of the inner t-integral."""
    lam = acb(lam_ball(key))
    derivative = key.endswith("_I") or key == "E1p_I"
    pi = arb.pi()
    phi_lo = pi / 2 * arb(k) / NPIECE
    phi_hi = pi / 2 * arb(k + 1) / NPIECE

    def geometry(t, phi, analytic):
        t2 = t * t
        a = 1 - 2 * t2
        s2 = phi.sin() ** 2
        c2 = 1 - s2
        L2 = c2 + lam * lam * s2
        J2 = c2 + s2 / (lam * lam)
        R2 = t2 + (1 - t2) * L2
        eta2 = a * a + 4 * t2 * (1 - t2) * J2
        c = t / (eta2.sqrt(analytic=analytic) * R2.sqrt(analytic=analytic))
        return {"t2": t2, "s2": s2, "R2": R2, "eta2": eta2, "c": c}

    def energy_kernel(t, phi, analytic):
        g = geometry(t, phi, analytic)
        f, _ = C.regular_angle_data(g["c"])
        return 8 * t**3 * f / acb(pi)

    def derivative_kernel(t, phi, analytic):
        g = geometry(t, phi, analytic)
        _, f1 = C.regular_angle_data(g["c"])
        R2_lam = 2 * lam * (1 - g["t2"]) * g["s2"]
        eta2_lam = -8 * g["t2"] * (1 - g["t2"]) * g["s2"] / lam**3
        c_lam = -g["c"] * (R2_lam / g["R2"] + eta2_lam / g["eta2"]) / 2
        return 8 * t**3 * f1 * c_lam / acb(pi)

    kernel = derivative_kernel if derivative else energy_kernel

    def outer(phi, analytic_phi):
        def inner(t, analytic_t):
            return kernel(t, phi, analytic_phi and analytic_t)

        return acb.integral(inner, 0, 1, abs_tol=tol, rel_tol=tol,
                            depth_limit=depth, eval_limit=eval_limit)

    return acb.integral(outer, acb(phi_lo), acb(phi_hi), abs_tol=tol,
                        rel_tol=tol, depth_limit=depth, eval_limit=eval_limit)


def main():
    key = sys.argv[1]
    k = int(sys.argv[2])
    tol = sys.argv[3] if len(sys.argv) > 3 else "1e-7"
    dps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    depth = int(sys.argv[5]) if len(sys.argv) > 5 else 16
    ctx.dps = dps
    t0 = time.time()
    v = piece(key, k, arb(tol), depth, 200000)
    elapsed = time.time() - t0
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    state.setdefault(key, {})[str(k)] = {
        "real_lower": str(arb(v.real.lower())),
        "real_upper": str(arb(v.real.upper())),
        "radius": float(v.real.rad()),
        "tolerance": tol, "dps": dps, "depth": depth,
        "seconds": round(elapsed, 1),
    }
    STATE.write_text(json.dumps(state, indent=1))
    print(f"{key} piece {k}: {v.real} rad={float(v.real.rad()):.2e} {elapsed:.0f}s")


if __name__ == "__main__":
    main()
