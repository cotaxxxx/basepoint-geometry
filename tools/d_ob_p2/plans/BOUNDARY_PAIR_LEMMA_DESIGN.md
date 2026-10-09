# Boundary Pair Lemma — design proposal for an independent paper lemma (Code, 2026-10-09)

Status: DESIGN / SUBMITTED FOR CHAT AUDIT.  Not a proof submission.  D-P2 NOT_CERTIFIED.

## 1. Statement to be proved (FT_q reduction draft 20c5c59b…, §8, (8.1))
There exists an explicit rational c_FT > 0 such that for lambda in [2/5, 93/200], 112/113 <= m < 1, rho = sqrt(1 - m^2):
   integral_{-1}^{1} integral_0^{2 pi} R J dphi dmu >= 2 pi lambda rho c_FT.                         (8.1)
By the exact identity (4.4)  H = (2 pi lambda rho)^{-1} integral integral R J,  (8.1) is EQUIVALENT to  H >= c_FT  for rho > 0  (8.2).

## 2. Proposed proof route (different from the "permissible route" sketched in FT_q §8; flagged for the Judge)
FT_q §8 describes one permissible route (b-pairing of R J, even/odd split, R Lipschitz).  The certified chain proves (8.2) directly via the other exact
representation of H:
 (B1) 2 pi lambda H = integral G (H-43-1(i) closure c4d49d81, chain (C1)-(C5); P1 Lemma V, Lemma 6.1; FT_q (3.2)).
 (B2) integral G >= S''_lb - U_north - U_near > Delta (22'' v1.2 closure record).
 (B3) H >= Delta/(2 pi lambda) > c_FT for rho > 0 (c_FT predeclare, rule R1-R3).
 (B4) (4.4) converts (8.2) into (8.1):  integral integral R J = 2 pi lambda rho H >= 2 pi lambda rho c_FT.
The lemma is therefore a COROLLARY of the certified chain plus the identity (4.4).  Its proof text is short; the evidence is the existing ledger.

## 3. Dependencies and their states
| dependency | where | state |
|---|---|---|
| (4.4) H = (2 pi lambda rho)^{-1} int int R J | FT_q draft §4 (lines 78-104), recorded as "closed in this reduction draft" in its §11 | FT_q draft status: PAPER-PROOF REDUCTION DRAFT; chat to confirm that §3-§4 are audited |
| (3.2) and Lemma 6.1 | FT_q draft §3; P1 note §6 | P1 note NOT_BINDING (carried, per Judge 案A) |
| Lemma V (a)(b)(c) | P1 note §5 | NOT_BINDING (carried) |
| S''_lb | south paper proof 05668a47 + kernel_extension_cert 1ac44469 | CHAT AUDIT PASS; canonical import PENDING |
| U_north | contract 45 | CHAT AUDIT PASS |
| U_near | contract 43 | CERTIFIED |
| c_FT | c_FT predeclare → certificate | UNSET |
| rho = 0 endpoint | NP-T (9.1) 13/2000 | AUDIT PASS (per FT_q draft header) |

## 4. Unclosed obligations before the lemma can be submitted
 (O1) c_FT certificate (predeclare audit, FREEZE, run).
 (O2) Judge ruling that the route (B1)-(B4) is admissible for (8.1) although it is not the route sketched in FT_q §8.
 (O3) Confirmation of the audit state of FT_q §3-§4 ((3.2), (4.2)-(4.4)) as used in (B1) and (B4).
 (O4) Decision on how the NOT_BINDING status of the P1 note propagates to the D-P2 gate (Judge 案A says it is carried to the D-P2 gate).
 (O5) South canonical import (pins in the lemma will cite canonical paths once imported).

## 5. Proposed deliverable after O1-O3
`analysis/D_OB_P2_D_AN1_FT_Q_BOUNDARY_PAIR_LEMMA.md` (paper lemma, <= 2 pages): statement (8.1)/(8.2), proof (B1)-(B4) with full pins, endpoint
m0 = min(c_FT, 13/2000), and a "not claimed" section (no D-P2 certification; P1 note status unchanged).
