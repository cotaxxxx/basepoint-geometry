"""Item 5 Stage 5a: certify D>0 / D<0 at the wide-bracket endpoints and D'<0 on it.

Bracket I_5 = [1717/500, 1718/500] = [3.434, 3.436], chosen so the endpoint
margins |D'|*dist ~ 6e-5 exceed the achievable enclosure radius (~5e-6) by an
order of magnitude.  The previous bracket [3.43486, 3.43488] had margins 6e-7,
below the achievable radius, and could not be certified at any runtime.

Energy and derivative are integrated separately so a run computes only what is
needed.  Results accumulate in stage5a_state.json.

usage: python3 stage5a.py {D_lo|D_hi|Dp_I|D_mid} [tol] [dps] [depth]
"""
import json, sys, time
from pathlib import Path
from flint import acb, arb, ctx, fmpq
import prolate_maxwell_arb_certificate as C

STATE = Path("stage5a_state.json")
LAM = {"D_lo": (fmpq(1717,500), None), "D_hi": (fmpq(1718,500), None),
       "D_mid": (fmpq(687,200), None), "Dp_I": (fmpq(1717,500), fmpq(1718,500))}

def lam_ball(key):
    lo, hi = LAM[key]
    return arb(lo) if hi is None else arb((lo+hi)/2, (hi-lo)/2)

def boundary(lam_value, tol, depth, eval_limit, derivative):
    lam = acb(lam_value)
    def geometry(t, phi, analytic):
        t2 = t*t; a = 1-2*t2; s2 = phi.sin()**2; c2 = 1-s2
        L2 = c2 + lam*lam*s2; J2 = c2 + s2/(lam*lam)
        R2 = t2 + (1-t2)*L2; eta2 = a*a + 4*t2*(1-t2)*J2
        c = t/(eta2.sqrt(analytic=analytic)*R2.sqrt(analytic=analytic))
        return {"t2": t2, "s2": s2, "R2": R2, "eta2": eta2, "c": c}
    pi = acb(arb.pi())
    def energy(t, phi, analytic):
        g = geometry(t, phi, analytic); f, _ = C.regular_angle_data(g["c"])
        return 8*t**3*f/pi
    def deriv(t, phi, analytic):
        g = geometry(t, phi, analytic); _, f1 = C.regular_angle_data(g["c"])
        R2l = 2*lam*(1-g["t2"])*g["s2"]
        e2l = -8*g["t2"]*(1-g["t2"])*g["s2"]/lam**3
        cl = -g["c"]*(R2l/g["R2"] + e2l/g["eta2"])/2
        return 8*t**3*f1*cl/pi
    return C.rigorous_integral_2d(deriv if derivative else energy, tol, depth, eval_limit)

def main():
    key = sys.argv[1]
    tol = arb(sys.argv[2] if len(sys.argv) > 2 else "1e-6")
    ctx.dps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    depth = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    deriv = key == "Dp_I"
    lam = lam_ball(key)
    t0 = time.time()
    E0, E0p = C.center_values(lam, tol, depth, 200000)
    t1 = time.time()
    B = boundary(lam, tol, depth, 200000, deriv)
    t2 = time.time()
    val = (B - E0p) if deriv else (B - E0)
    rec = {"key": key, "lambda": str(lam), "derivative": deriv,
           "value_lower": str(arb(val.real.lower())), "value_upper": str(arb(val.real.upper())),
           "radius": float(val.real.rad()),
           "positive_certified": bool(val.real > 0), "negative_certified": bool(val.real < 0),
           "center_seconds": round(t1-t0,1), "boundary_seconds": round(t2-t1,1),
           "settings": {"tolerance": str(tol), "dps": ctx.dps, "depth": depth}}
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    state[key] = rec
    STATE.write_text(json.dumps(state, indent=1))
    print(f"{key}: [{rec['value_lower'][:14]}, {rec['value_upper'][:14]}] rad={rec['radius']:.2e} "
          f"pos={rec['positive_certified']} neg={rec['negative_certified']} {t2-t0:.0f}s")

if __name__ == "__main__":
    main()
