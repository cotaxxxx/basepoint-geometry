"""Exploratory: is the mirror-paired integrand of E_3 pointwise positive for q_3 > 0 ?
   f(xi) = xi_3 J - l_3 sqrt(B) u_3 K ;  P(xi) = f(xi) + f(xi_bar),  xi_bar = (xi_1, xi_2, -xi_3).
DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np
rng = np.random.default_rng(1)
def f3(l, q, xi, i=2):
    k = 1 - xi @ q
    d = l*(xi - q); D = np.linalg.norm(d, axis=-1); u = d/D[:, None]
    n = xi/l; sB = np.linalg.norm(n, axis=-1)
    c = np.clip(k/(D*sB), -1, 1); al = np.arccos(c); s = np.sqrt(1 - c*c) + 1e-300
    J = -al**2 + 2*al*c/s; K = 2*al*c*c/s
    return xi[:, i]*J - l[i]*sB*u[:, i]*K
worst = {}
for trial in range(4000):
    s = np.exp(rng.uniform(0, np.log(5))); t = np.exp(rng.uniform(0, np.log(9)))
    l = np.array([1, s, s*t])
    v = rng.normal(size=3); v /= np.linalg.norm(v); q = np.abs(v)*rng.random()**(1/3)
    xi = rng.normal(size=(4000, 3)); xi /= np.linalg.norm(xi, axis=1)[:, None]; xi[:, 2] = np.abs(xi[:, 2])
    xb = xi*np.array([1, 1, -1])
    P = f3(l, q, xi) + f3(l, q, xb)
    m = P.min()/q[2]
    if not worst or m < worst["m"]:
        worst = dict(m=m, s=s, t=t, q=q, frac_neg=float((P < 0).mean()))
print("mirror-paired integrand of E_3: min P/q3 =", worst)
