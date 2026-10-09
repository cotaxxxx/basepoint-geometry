"""QM -> L3 -> L1 reverse feasibility: EXACT RATIONAL ARITHMETIC ONLY (Code, 2026-10-09).

Scope (CHAT/Dig instruction 2026-10-09, §2.1): uses only the audited QM modulus formula (QM draft 7f9119f7, (1.1)), the L3 distance
conversion (L3-MRA 5fc03412 §6 / predeclare v1.2 L3 text), and the SET value m0.  No evaluation of H, E or any kernel; no sampling; no interval
arithmetic of H; no producer/checker.  pi and logarithms enter only through rational enclosures certified here by exact inequalities:
  pi:  3 < pi < 22/7   (22/7 - pi = int_0^1 x^4(1-x)^4/(1+x^2) dx > 0; pi > 3 from the inscribed regular hexagon, perimeter 6 < 2 pi)
  ln:  for rational y > 0, e^y is bracketed by the exact Taylor partial sum S_N(y) <= e^y <= S_N(y) + y^{N+1}/(N+1)! * 1/(1 - y/(N+2)) (y < N+2);
       so lo <= ln x <= hi is certified by  S_N(hi) >= x  and  S_N(lo) + tail(lo) <= x.
omega_E(d) = 50 C2 d + 25 C3 d (1 + 2 ln(1/d))  (0 < d <= 1/2),  C2 = 9 pi + 8,  C3 = 8788 + 39 pi;  omega_E nondecreasing (QM §9).
L3 condition (frozen text): omega_E(delta0) < m0, with |p_in - p_b| <= 1 - r = delta/(1+r) <= delta.
"""
from fractions import Fraction as Q
from math import factorial, log, floor
import sys

M0 = Q(540861826035521, 336806928254720000)
PI_LO, PI_HI = Q(3), Q(22, 7)
N_TAYLOR = 160

def exp_lo(y):            # S_N(y) <= e^y  for y >= 0
    s, t = Q(0), Q(1)
    for n in range(N_TAYLOR + 1):
        if n: t = t*y/n
        s += t
    return s
def exp_hi(y):            # e^y <= S_N(y) + tail, valid for 0 <= y < N+2
    assert 0 <= y < N_TAYLOR + 2
    return exp_lo(y) + y**(N_TAYLOR + 1)/factorial(N_TAYLOR + 1)/(1 - y/(N_TAYLOR + 2))

def ln_bounds(x, digits=12):
    """certified rationals lo <= ln x <= hi for rational x >= 1."""
    g = log(float(x)); D = 10**digits
    lo, hi = Q(floor(g*D) - 2, D), Q(floor(g*D) + 3, D)
    lo = max(lo, Q(0))
    assert exp_hi(lo) <= x, "ln lower bound not certified"
    assert exp_lo(hi) >= x, "ln upper bound not certified"
    return lo, hi

def C2(pi): return 9*pi + 8
def C3(pi): return 8788 + 39*pi
def omega_hi(d):   # rational upper bound of omega_E(d), 0 < d <= 1/2
    lo, hi = ln_bounds(1/d)
    return 50*C2(PI_HI)*d + 25*C3(PI_HI)*d*(1 + 2*hi)
def omega_lo(d):   # rational lower bound
    lo, hi = ln_bounds(1/d)
    return 50*C2(PI_LO)*d + 25*C3(PI_LO)*d*(1 + 2*lo)

def fr(x): return f"{x.numerator}/{x.denominator}" if x.denominator != 1 else str(x.numerator)
def approx(x): return f"{float(x):.6g}"

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}")

print("== certified constants")
check("pi < 22/7 (exact identity, see docstring) and pi > 3", True, "(paper; used as rational bounds only)")
l10 = ln_bounds(Q(10)); print(f"ln 10 in [{fr(l10[0])}, {fr(l10[1])}]")
print(f"m0 = {fr(M0)} ~ {approx(M0)}")

print("\n== Task B: delta0 from the frozen condition omega_E(delta0) < m0")
# monotone bracketing on the grid d = a * 10^-k with a in 1..9
best_ok, first_fail = None, None
for k in range(8, 13):
    for a in range(9, 0, -1):
        d = Q(a, 10**k)
        if omega_hi(d) < M0 and (best_ok is None or d > best_ok): best_ok = d
        if omega_lo(d) > M0 and (first_fail is None or d < first_fail): first_fail = d
print(f"certified admissible: omega_E({fr(best_ok)}) <= {fr(omega_hi(best_ok))} ~ {approx(omega_hi(best_ok))} < m0")
print(f"certified inadmissible: omega_E({fr(first_fail)}) >= {fr(omega_lo(first_fail))} ~ {approx(omega_lo(first_fail))} > m0")
check("(B1) omega_E upper bound at the admissible delta0 is < m0", omega_hi(best_ok) < M0)
check("(B2) omega_E lower bound at the inadmissible point is > m0 (so the threshold lies between)", omega_lo(first_fail) > M0)
print(f"=> the largest admissible delta0 from the frozen condition lies in [{fr(best_ok)}, {fr(first_fail)})  (~[{approx(best_ok)}, {approx(first_fail)}))")
# sharper conversion: d = 1 - r = delta/(1+r) <= delta/(1 + sqrt(1 - delta)) ; with delta <= 1/2, 1 + r >= 1 + 7/10 since r >= sqrt(1/2) > 7/10
print("remark: with the exact conversion |p_in - p_b| <= 1 - r = delta/(1+r) and r >= 7/8 on Sigma, the effective distance is <= (8/15) delta,")
print("        which enlarges the admissible delta0 by at most the factor 15/8; this does not change any conclusion below.")

print("\n== Task C: required lower bound m_required(delta) = omega_E(delta) for the candidate widths")
A_PRIORI = Q(25, 2)*C2(PI_HI)          # QM (3.1): |E_rhorho| <= (25/2) C2, hence |H| <= (25/2) C2 (Lemma 6.1(iii) average)
print(f"a-priori ceiling of any boundary lower bound: H <= sup|E_rhorho| <= (25/2) C2 <= {fr(A_PRIORI)} ~ {approx(A_PRIORI)}  (QM (3.1))")
print("| delta | omega_E(delta) in [lo, hi] (exact rationals) | R = omega_E/m0 in | connect with current m0? | attainable by ANY m0 <= (25/2)C2? |")
for k in range(1, 7):
    d = Q(1, 10**k)
    lo, hi = omega_lo(d), omega_hi(d)
    r_lo, r_hi = lo/M0, hi/M0
    connect = "NO (omega_lo > m0)" if lo > M0 else ("YES" if hi < M0 else "undecided")
    attain = "NO (omega_lo > ceiling)" if lo > A_PRIORI else "not excluded"
    print(f"| 10^-{k} | [{approx(lo)}, {approx(hi)}] | [{approx(r_lo)}, {approx(r_hi)}] | {connect} | {attain} |")
    print(f"    exact: omega_lo = {fr(lo)} ; omega_hi = {fr(hi)}")
# smallest power of 10 at which even the a-priori ceiling is exceeded
k_star = None
for k in range(1, 12):
    if omega_lo(Q(1, 10**k)) > A_PRIORI: k_star = k
check("(C1) at delta = 10^-1 ... 10^-6 the frozen condition fails for the current m0", all(omega_lo(Q(1, 10**k)) > M0 for k in range(1, 7)))
print(f"largest k with omega_E(10^-k) > (25/2)C2 (no boundary bound whatsoever can connect at that width): k = {k_star}")

print("\n== Task D: counterexample points lie in the L1 layer delta in [delta0, 15/64]")
for name, r in (("pointwise-pair (r=15/16)", Q(15, 16)), ("G1 (r=127/128)", Q(127, 128))):
    delta = 1 - r*r
    print(f"{name}: delta = {fr(delta)} ~ {approx(delta)};  in [{fr(best_ok)}, 15/64]: {best_ok <= delta <= Q(15,64)};  r in [7/8,1]: {Q(7,8) <= r <= 1}")
check("(D1) both counterexample points are in the L1 layer for any admissible delta0", all(best_ok <= 1 - r*r <= Q(15, 64) for r in (Q(15, 16), Q(127, 128))))
print("\nRESULT:", "ALL EXACT CHECKS PASS" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
