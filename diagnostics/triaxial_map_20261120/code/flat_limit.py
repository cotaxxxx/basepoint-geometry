"""Flat limit s -> infinity (a_1 -> 0), leading logarithmic order (heuristic outlook, non-interval).

   gamma ~ k / (s |xi_1| |L'(xi'-q')|) away from the rim xi_1 = 0, and the measure dxi_1/|xi_1| is
   log-divergent at the rim (cut off at |xi_1| ~ 1/s).  Hence
       E(q) = pi^2/4 - (log s / s) * Lambda(q') + O(1/s),
       Lambda(q') = (1/2) Int_0^{2pi} (1 - q'.e(psi))^2 / |L'(e(psi) - q')| dpsi,
   q' = (q_2, q_3) in the unit disc, e(psi) = (cos psi, sin psi), L' = diag(1, t).
   Lambda is a boundary-integral functional of the limiting ellipse (semi-axes 1, t).
   The O(1/s) term contains -(pi/s) q_1^2 Psi(q') with Psi > 0 (so h_1 < 0 in the limit).
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np
from scipy.optimize import brentq

N = 20000
PS = 2*np.pi*(np.arange(N) + 0.5)/N
C, S = np.cos(PS), np.sin(PS)


def Lam(x, y, t):
    return 0.5*2*np.pi*np.mean((1 - x*C - y*S)**2/np.sqrt((C - x)**2 + t*t*(S - y)**2))


def Lam_x(x, y, t):
    k = 1 - x*C - y*S; d2 = (C - x)**2 + t*t*(S - y)**2
    return 0.5*2*np.pi*np.mean(-2*k*C/np.sqrt(d2) + k*k*(C - x)/d2**1.5)


def Lam_xx0(t):
    m2 = C*C + t*t*S*S
    return 2*np.pi*np.mean((C*C - (2*C*C + 0.5)/m2 + 1.5*C*C/m2**2)/np.sqrt(m2))


def Lam_yy0(t):
    m2 = C*C + t*t*S*S
    # by the same expansion with q' = (0, y): numerator (1 - y S)^2, |L'(e - q')|^2 = m2 - 2 t^2 y S + t^2 y^2
    return 2*np.pi*np.mean((S*S - (2*t*t*S*S + 0.5*t*t)/m2 + 1.5*t**4*S*S/m2**2)/np.sqrt(m2))


if __name__ == "__main__":
    import json, sys
    out = {}
    h = 1e-4
    chk = (Lam(h, 0, 2.0) - 2*Lam(0, 0, 2.0) + Lam(-h, 0, 2.0))/h**2
    print("check Lam_xx0 closed vs FD (t=2):", Lam_xx0(2.0), chk)
    chk = (Lam(0, h, 2.0) - 2*Lam(0, 0, 2.0) + Lam(0, -h, 2.0))/h**2
    print("check Lam_yy0 closed vs FD (t=2):", Lam_yy0(2.0), chk)
    print("t=1: Lam_xx0 = %.6f  (-pi/2 = %.6f)" % (Lam_xx0(1.0), -np.pi/2))
    tt = np.array([1, 1.5, 2, 3, 4, 5, 6, 8, 12, 20, 50])
    print("t         :", tt)
    print("Lam_xx(0) :", np.array([Lam_xx0(t) for t in tt]).round(4))
    print("Lam_yy(0) :", np.array([Lam_yy0(t) for t in tt]).round(4))
    print("Lam_x(rim):", np.array([Lam_x(1 - 1e-7, 0, t) for t in tt]).round(4))
    sg = np.sign([Lam_xx0(t) for t in np.linspace(1, 60, 600)])
    out["Lam_xx0_sign_changes_t_1_60"] = [float(np.linspace(1, 60, 600)[i]) for i in np.where(np.diff(sg) != 0)[0]]
    sg = np.sign([Lam_x(1 - 1e-7, 0, t) for t in np.linspace(1, 60, 600)])
    out["Lam_x_rim_sign_changes_t_1_60"] = [float(np.linspace(1, 60, 600)[i]) for i in np.where(np.diff(sg) != 0)[0]]
    print(out)
    for key, f in (("t_c_inf", Lam_xx0), ("t_b_inf", lambda t: Lam_x(1 - 1e-7, 0, t))):
        br = out["Lam_xx0_sign_changes_t_1_60" if key == "t_c_inf" else "Lam_x_rim_sign_changes_t_1_60"]
        out[key] = [float(brentq(f, b, b + 0.1)) for b in br]
    print(out)
    if len(sys.argv) > 1:
        json.dump(out, open(sys.argv[1], "w"), indent=1)
