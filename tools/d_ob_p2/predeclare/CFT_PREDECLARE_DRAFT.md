# c_FT and m0 — PREDECLARE DRAFT v0 (Code, 2026-10-09)

STATUS: DRAFT / SUBMITTED FOR CHAT AUDIT / NOT FROZEN / certificate NOT written, NOT executed.  No numerical value of c_FT or m0 is stated in this
document; the rule that produces them is declared here and the value is produced only by the certificate after FREEZE.  D-P2 NOT_CERTIFIED.

## 1. Target (frozen sources)
FT_q frozen target (FT_q reduction draft 20c5c59bd74f940fe0b1e05892bd2169e09d4fde, §1): an explicit rational m0 > 0, independent of (lambda, tau), with
H(rho, lambda m; lambda) >= m0 for lambda in [2/5, 93/200], tau in [7/8, 1] (m in [112/113, 1], 0 <= rho <= 15/113).
22'' v1.2 (canonical d445b302…): after U_north + U_near < S''_lb is proved, a uniform rational c_FT > 0 may be declared "by bounding pi and lambda
rationally; then m0 = min(c_FT, 13/2000)".  13/2000 is the NP-T endpoint margin H(0, lambda) > 13/2000 (FT_q draft §9, (9.1)).

## 2. Inputs (all CHAT AUDIT PASS; pins in the 22'' closure record V1_2_NUMERIC_CONDITION_CLOSURE_RECORD.md)
 (I1) 2 pi lambda H = integral_{-1}^{1} G(mu) dmu for rho > 0 (H-43-1(i) closure c4d49d81, chain (C1)-(C5)).
 (I2) integral G >= S''_lb - U_north - U_near (22'' v1.2 one-sided inequality; coverage/overlap A1-A6).
 (I3) S''_lb = 635530452759/817216000000; U_north < 5481/10000; U_near <= U43 := 3887073979116207/17284813033600000.
 (I4) Delta := S''_lb - 5481/10000 - U43 > 0 (exact; frozen certificate run bd512f53).

## 3. Derivation rule (declared before any computation)
 (R1) For rho > 0 and every parameter in the box:  H >= Delta/(2 pi lambda).
 (R2) Rational upper bound of the denominator:  pi < 22/7 (exact identity int_0^1 x^4(1-x)^4/(1+x^2) dx = 22/7 - pi > 0) and lambda <= 93/200 give
      2 pi lambda < 2 (22/7)(93/200) =: P_hi  (an exact rational).  Hence H > Delta/P_hi.
 (R3) c_FT := Delta / P_hi  (the exact rational, no rounding).  Positivity of c_FT follows from Delta > 0 and P_hi > 0.
 (R4) rho = 0 endpoint: H(0, lambda) = E_rhorho(0, lambda) > 13/2000 (NP-T, FT_q (9.1)); also H is continuous on M_lambda (P1 Lemma 6.1(iii)), so
      H >= c_FT extends to rho = 0 by continuity; the declared m0 uses the frozen formula of 22'':  m0 := min(c_FT, 13/2000).
 (R5) No alternative constant, no rounding to a "nicer" rational, no use of the lower bound lambda >= 2/5 to sharpen c_FT, and no diagnostic value is
      permitted.  If chat wants a rounded-down display rational in addition, it must be declared in a version-up of this predeclare before FREEZE.

## 4. Certificate plan (tools/d_ob_p2/ftq_cert/cft_cert.py; written after this predeclare's PASS, executed after FREEZE)
 (K1) recompute Delta from the three pinned fractions and assert equality with 1622585478106563/345696260672000000 (the value printed by run bd512f53);
 (K2) assert pi < 22/7 by the exact integral identity (sympy) and P_hi = 2*(22/7)*(93/200) as an exact Fraction;
 (K3) c_FT = Delta/P_hi as an exact Fraction; assert c_FT > 0;
 (K4) m0 = min(c_FT, 13/2000) by exact comparison; print which branch is taken;
 (K5) print c_FT and m0 exactly; scope block as in the contract 43 certificate (machine-checked vs paper vs external).
 Execution: one run, isolated directory, python3 -I, provenance as for contract 43.

## 5. Not claimed
This predeclare does not prove the Boundary Pair Lemma (8.1) in the R J form of FT_q §8 (see the Boundary Pair Lemma design note), does not discharge
FT_q, and does not certify D-P2.
