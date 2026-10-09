"""c_FT and m0 -- exact certificate (Code).  Implements predeclare v1 (tools/d_ob_p2/predeclare/CFT_PREDECLARE_DRAFT.md,
commit b3127b4e987f2869392daa3ee0d7b1841380272d, blob e2ed7391ca5d65ccecacfd531605ecf1bac48bf0,
SHA-256 d63430c6768ada4f0fd397066c8281755a2ac014624706149fba036181bc458a; FROZEN by CHAT AUDIT).

STATUS AT COMMIT: SOURCE ONLY.  NOT EXECUTED.  Syntax checked with ast.parse only.  Execution requires CHAT AUDIT static PASS and an explicit
run permission; then one run, isolated directory, python3 -I, provenance as for contract 43.

Rules implemented (predeclare v1 §3; no other rule, no rounding, no diagnostic value):
 (R1) for rho > 0 and every parameter in the box, H >= Delta/(2 pi lambda)          [inputs I1-I4; paper, not re-proved here]
 (R2) 2 pi lambda < P_hi := 2 * (22/7) * (93/200)   using pi < 22/7 and lambda <= 93/200
 (R3) c_FT := Delta / P_hi   (exact rational; no rounding)
 (R4) m0 := min(c_FT, 13/2000)   (22'' frozen formula; 13/2000 = NP-T endpoint margin, FT_q (9.1))
 (R5) no alternative constant, no rounding, no use of lambda >= 2/5, no diagnostic value
Checks (predeclare v1 §4):
 (K1) Delta recomputed from the three pinned fractions; equality with the value printed by the contract 43 run bd512f53
 (K2) pi < 22/7: exact integral identity int_0^1 x^4(1-x)^4/(1+x^2) dx = 22/7 - pi (machine), positivity of the integrand (paper, predeclare §4 (K2));
      P_hi as an exact Fraction
 (K3) c_FT = Delta/P_hi exact; c_FT > 0
 (K4) m0 = min(c_FT, 13/2000) by exact comparison; branch printed
 (K5) exact printing of c_FT and m0; scope block (machine-checked / paper / external)
All arithmetic is fractions.Fraction or sympy Rational; no floating point enters any assertion (floats appear only in printed approximations).
"""
from fractions import Fraction as Q
import sympy as sp

ok = True
def check(name, cond, detail=""):
    global ok; ok &= bool(cond); print(f"{name}: {'PASS' if cond else 'FAIL'} {detail}", flush=True)

# ---------------------------------------------------------------- (K1) Delta from the pinned fractions
S_LB = Q(635530452759, 817216000000)                      # S''_lb: south paper proof 05668a47 / kernel_extension_cert 1ac44469 (CHAT AUDIT PASS)
U_FAR = Q(5481, 10000)                                    # U_north,cert: contract 45 pieces 1-3 (CHAT AUDIT PASS)
U_NEAR = Q(3887073979116207, 17284813033600000)           # U_43^N3: contract 43 frozen certificate 7f71fb43, run bd512f53 (CERTIFIED)
DELTA_RUN = Q(1622585478106563, 345696260672000000)       # final margin printed by run bd512f53 (stdout.txt SHA-256 b377ee8f...)
DELTA = S_LB - U_FAR - U_NEAR
check("(K1) Delta = S''_lb - U_far - U_near equals the contract 43 run value", DELTA == DELTA_RUN, f"Delta = {DELTA}")
check("(K1) Delta > 0", DELTA > 0)

# ---------------------------------------------------------------- (K2) pi < 22/7 and P_hi
x = sp.symbols('x', real=True)
integrand = x**4*(1 - x)**4/(1 + x**2)
quot, rem = sp.div(sp.expand(x**4*(1 - x)**4), 1 + x**2, x)
check("(K2) polynomial division: x^4(1-x)^4 = (x^6-4x^5+5x^4-4x^2+4)(1+x^2) - 4",
      sp.expand(quot - (x**6 - 4*x**5 + 5*x**4 - 4*x**2 + 4)) == 0 and rem == -4)
check("(K2) int_0^1 x^4(1-x)^4/(1+x^2) dx == 22/7 - pi  (exact symbolic)",
      sp.simplify(sp.integrate(integrand, (x, 0, 1)) - (sp.Rational(22, 7) - sp.pi)) == 0)
# paper (predeclare v1 §4 (K2)): the integrand is continuous, >= 0 on [0,1] and not identically 0, hence the integral is > 0, i.e. pi < 22/7.
PI_HI = Q(22, 7)
LAMBDA_HI = Q(93, 200)
P_HI = 2*PI_HI*LAMBDA_HI
check("(K2) P_hi == 2*(22/7)*(93/200) as an exact Fraction", P_HI == Q(2)*Q(22, 7)*Q(93, 200), f"P_hi = {P_HI}")
check("(K2) P_hi > 0", P_HI > 0)

# ---------------------------------------------------------------- (K3) c_FT
C_FT = DELTA/P_HI
check("(K3) c_FT = Delta/P_hi is an exact Fraction and c_FT > 0", isinstance(C_FT, Q) and C_FT > 0)

# ---------------------------------------------------------------- (K4) m0
NPT_MARGIN = Q(13, 2000)
if C_FT <= NPT_MARGIN:
    M0, branch = C_FT, "c_FT <= 13/2000, m0 = c_FT"
else:
    M0, branch = NPT_MARGIN, "c_FT > 13/2000, m0 = 13/2000"
check("(K4) m0 == min(c_FT, 13/2000) (exact comparison)", M0 == min(C_FT, NPT_MARGIN) and M0 > 0, branch)

# ---------------------------------------------------------------- (K5) exact output and scope
print(f"(K5) Delta = {DELTA}  (~{float(DELTA):.9f})")
print(f"(K5) P_hi  = {P_HI}  (~{float(P_HI):.9f})")
print(f"(K5) c_FT  = {C_FT}  (~{float(C_FT):.9f})   [exact rational, no rounding]")
print(f"(K5) m0    = {M0}  (~{float(M0):.9f})   [{branch}]")
print("SCOPE OF THIS CERTIFICATE RUN")
print("  machine-checked here: (K1) exact recomputation of Delta and equality with the contract 43 run value; (K2) polynomial division and the")
print("    exact integral identity for 22/7 - pi, and P_hi as an exact Fraction; (K3) c_FT exact and positive; (K4) m0 by exact comparison.")
print("  paper steps relied on (NOT machine-verified here): positivity of x^4(1-x)^4/(1+x^2) on (0,1) (so 22/7 - pi > 0); (R1) H >= Delta/(2 pi lambda)")
print("    from 2 pi lambda H = int G (H-43-1(i) closure c4d49d81) and int G >= S''_lb - U_north - U_near (22'' v1.2; closure record v1 incl. R-G);")
print("    lambda <= 93/200 from the frozen box; the rho = 0 endpoint via NP-T (9.1) and continuity of H (P1 Lemma 6.1(iii)).")
print("  external items NOT re-verified by this run: the CHAT AUDIT states of S''_lb, U_north, U_near, R-G and the 22'' closure record; the")
print("    Boundary Pair Lemma (8.1) in the R J form; FT_q discharge; D-P2.  This run does not certify D-P2.")
if not ok:
    print("RESULT: SOME CHECK FAILED -- c_FT NOT SET"); raise SystemExit(1)
print("RESULT: ALL IMPLEMENTED CHECKS PASS; c_FT and m0 as printed are subject to CHAT AUDIT of this run; NOT a D-P2 certification")
raise SystemExit(0)
