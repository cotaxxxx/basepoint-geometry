# D-OB P2 / D-AN-1 FT_q — Boundary Pair Lemma (8.1) as a corollary of the certified chain — PAPER PROOF DRAFT

Status: DRAFT / SUBMITTED FOR CHAT AUDIT.  Route approved by CHAT AUDIT (O2: corollary of the certified chain; no pointwise R J sign required).
O3: the FT_q §3-§4 identities are used with their derivation and conditions stated in §2.  c_FT: formal value on HOLD (independent re-run pending);
this draft uses the symbol c_FT := Delta/P_hi of the frozen rule (R3) and quotes the run value only as pending.  D-P2 NOT_CERTIFIED.

## 0. Notation warning (symbol collision)
FT_q uses G for the ANGLE function G(gamma) = (arccos gamma)^2 (density F = h G(gamma), G' = -2R).  Contracts 21''/43/45 and 22'' use G(mu) for the
mu-DENSITY.  Below the angle function is written G_ang and the mu-density G(mu).

## 1. Statement (FT_q reduction draft §8, (8.1))
For every lambda in [2/5, 93/200], 112/113 <= m < 1, rho = sqrt(1 - m^2) > 0, z = lambda m:
   int_{-1}^{1} ( int_0^{2 pi} R J dphi ) dmu  >  2 pi lambda rho c_FT,      c_FT := Delta/P_hi,               (8.1)
with Delta = 1622585478106563/345696260672000000, P_hi = 1023/350 (predeclare v1 rules (R1)-(R3)).  The double integral is the ITERATED integral
(phi inner), which is the form in which (4.4) is stated and used.  Equivalently (8.2): H(rho, z; lambda) > c_FT for rho > 0.

## 2. Identities used (O3): statement, derivation, conditions
Source pins: FT_q reduction draft `analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md` commit 20c5c59bd74f940fe0b1e05892bd2169e09d4fde, blob
1c449fb4fb791f750668c44605156454cfff42af, SHA-256 46443f0e981f360e57fb70d99754b0e480042d246e22d36732b00b96102a9cd1 (REDUCTION AUDIT PASS);
P1 design note `analysis/D_OB_P1_DESIGN_NOTE.md` commit 69e104602e939817b6f4d71df3f6bd63cbc729e0, blob f81e120e44a866d206117d4fab5fac627f26ccd1,
SHA-256 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9 (status NOT_BINDING, carried to the D-P2 gate per Judge 案A).
 (E1) H = E_rho(rho, z)/rho for rho > 0.  [FT_q line 60; P1 Lemma 6.1(iii), P1 line 107]  Condition: rho > 0.
 (E2) F_rho = h_rho G_ang - 2 h R gamma_rho, h_rho = -lambda b.  [FT_q (3.1), lines 68-70]  Derivation: product rule on F = h G_ang(gamma) with
      G_ang' = -2R.  Condition: D > 0 (x != p), i.e. every surface point except the coincident point (mu, phi) = (m, 0).
 (E3) E_rho = (1/(4 pi lambda)) int int F_rho dphi dmu.  [FT_q (3.2), line 74]  Derivation: dA/w = dmu dphi and Lemma V at the boundary base point:
      absolute convergence (Lemma V(a), P1 line 89/91), value as continuous extension (Lemma V(c), line 95), identification with the one-sided xi-trace
      (H-43-1(ii) CLOSED, Astra H43_ENDPOINT_LEMMA.md (3.E1), (3.E3), commit ff1e1a53, SHA-256 b1a906ed...).  Condition: rho > 0.
 (E4) For fixed mu != m:  int_0^{2 pi} F_rho dphi = 2 int_0^{2 pi} R J dphi,  J := lambda(a^2 - b^2) gamma_b - h gamma_rho.  [FT_q (4.1)-(4.3), lines 82-96]
      Derivation: b = a cos phi = d/dphi (a sin phi); integrating by parts over the full period, the boundary term vanishes and
      int b G_ang dphi = a^2 int sin^2 phi G_ang'(gamma) gamma_b dphi; with G_ang' = -2R and a^2 sin^2 phi = a^2 - b^2, (E2) integrates to 2 int R J.
      Conditions: mu != m (then D > 0 for all phi, so gamma, G_ang(gamma) and R are smooth in phi on the circle and the integration by parts is valid);
      mu = +-1 (a = 0) trivially.  The excluded latitude mu = m has measure zero.
 (E5) Iterated form of (4.4):  H = (1/(2 pi lambda rho)) int_{-1}^{1} ( int_0^{2 pi} R J dphi ) dmu.  [FT_q (4.4), line 102]  Derivation: (E1), (E3), (E4)
      with Fubini for the absolutely integrable F_rho (|F_rho| <= C_tr = pi^2/4 + pi, Astra (3.E3)), then (E4) for a.e. mu.  The inner phi-integral is
      a bounded measurable function of mu (it equals (1/2) int F_rho dphi), so the outer integral exists.  Condition: rho > 0.
 (E6) 2 pi lambda H = int_{-1}^{1} G(mu) dmu, and G(mu) = (1/rho) int_0^{2 pi} R J dphi for a.e. mu (R-G).  [H-43-1(i) closure c4d49d81 §3(C) (C1)-(C5);
      22'' closure record v1 e0f59439 §4 (G1)-(G5); both CHAT AUDIT PASS / CLOSED]

## 3. Inputs (certified)
 (C-a) int_{-1}^{1} G >= int_{-1}^{1/2} G - int_{1/2}^{1} [-G]_+ >= S''_lb - U_north - U_near   (22'' v1.2, canonical d445b302; closure record v1).
 (C-b) S''_lb = 635530452759/817216000000; U_north < 5481/10000 (contract 45); U_near <= 3887073979116207/17284813033600000 (contract 43 CERTIFIED).
 (C-c) Delta = S''_lb - 5481/10000 - 3887073979116207/17284813033600000 > 0 (exact; contract 43 run bd512f53; c_FT certificate (K1)).
 (C-d) 2 pi lambda < P_hi = 1023/350 for lambda <= 93/200, using pi < 22/7 (int_0^1 x^4(1-x)^4/(1+x^2) dx = 22/7 - pi > 0; c_FT predeclare v1 (K2)).

## 4. Proof
Fix lambda in [2/5, 93/200] and m in [112/113, 1), so rho > 0.  By (C-a), (C-b) (strict for U_north) and (C-c):
   2 pi lambda H = int G  >=  S''_lb - U_north - U_near  >  S''_lb - 5481/10000 - U43  =  Delta.
By (E5) and (E6):  int_{-1}^{1} ( int_0^{2 pi} R J dphi ) dmu  =  2 pi lambda rho H  >  rho Delta.
By (C-d):  rho Delta = 2 pi lambda rho (Delta/(2 pi lambda)) > 2 pi lambda rho (Delta/P_hi) = 2 pi lambda rho c_FT, since 0 < 2 pi lambda < P_hi and Delta > 0.
Hence (8.1) holds with strict inequality, and (8.2) H > c_FT for rho > 0.  The constant c_FT does not depend on lambda or m.  ∎

## 5. Endpoint and m0 (not part of (8.1))
rho = 0 (m = 1): H(0, lambda) = E_rhorho(0, lambda) > 13/2000 (NP-T, FT_q (9.1)); also H is continuous on M_lambda (P1 Lemma 6.1(iii)), so H >= c_FT at
rho = 0 by continuity.  m0 := min(c_FT, 13/2000) (22'' frozen formula); the c_FT certificate run reports the branch c_FT <= 13/2000.

## 6. Values (pending)
c_FT = m0 = 540861826035521/336806928254720000 as printed by the authorized run 87b7c5af (stdout SHA-256 12968e4a...).  Formal fixing of this value is
on HOLD until the CHAT AUDIT independent re-run; this draft does not fix it.

## 7. Not claimed
No pointwise sign of R J; no claim about FT_q discharge beyond (8.1)/(8.2); P1 note status unchanged (NOT_BINDING, carried to the D-P2 gate);
no D-P2 certification.
