# D-OB P2 / D-AN-1 FT_q — closure record v1 (Code draft, 2026-10-09)

Status: v1 DRAFT / SUBMITTED FOR CHAT AUDIT.  After CHAT AUDIT, to be put to the Judge for a conditional DISCHARGED ruling of the FT_q node.
This record does NOT certify D-P2 and does NOT discharge any other D-AN-1 node.  D-P2 NOT_CERTIFIED.

## 1. Target (frozen node statement)
D-AN-1 predeclare v1.2 (`cotaxxxx/bg-oblate-spheroid`, `analysis/D_OB_P2_D_AN1_PREDECLARE_V1_2.md`, commit e9c8b1caa3ad502a3d01dafe354b61108787eed2,
blob 931c0cdb0e3f9d81430ae7e9029b3704bf099505, SHA-256 f27a568b2996eb29e3756612dac3cb40ac2796b19dd81729742082a62abcf217), §"FT_q — quantitative
boundary-face positivity": an explicit rational m0 > 0, uniform in lambda and tau, with
    H(rho_b, z_b; lambda) >= m0   for all lambda in [2/5, 93/200], tau in [7/8, 1],  rho_b = (1-tau^2)/(1+tau^2), z_b = lambda 2tau/(1+tau^2).
Dependencies declared there: Lemma V and Lemma 6.1; "the proof route is not frozen" (L2 and the NP-T method are optional routes).
Same statement: FT_q reduction draft (`analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md`, commit 20c5c59bd74f940fe0b1e05892bd2169e09d4fde, SHA-256 46443f0e...) §1.

## 2. Result
    m0 = c_FT = 540861826035521/336806928254720000 > 0      (c_FT / m0 SET, CHAT AUDIT ledger)
    H(rho_b, z_b; lambda) >= m0 on the whole frozen face, with strict inequality for rho_b > 0 (tau < 1).

## 3. Proof routes
### 3.1 rho > 0 (tau in [7/8, 1))
Boundary Pair Lemma v1 (FIXED): `tools/d_ob_p2/ftq_paper_proof/D_OB_P2_D_AN1_FT_Q_BOUNDARY_PAIR_LEMMA_DRAFT.md` in `cotaxxxx/basepoint-geometry`,
commit 6d106cbdde12cb172b4ca137b7b03697875f1d54, blob b6aa355b69c9db2cbe764b09b0a8205635c0063a,
SHA-256 fb918c0952012ee02a8696f8c2e76e093d0c4881aaea3090ce56b44c7b143944 (PAPER AUDIT PASS / v1 FIXED).  It proves (8.1) and the equivalent
(8.2) H > c_FT for rho > 0, from the certified chain:
    2 pi lambda H = int G > Delta,   2 pi lambda < P_hi = 1023/350,   c_FT = Delta/P_hi,   Delta = 1622585478106563/345696260672000000.
### 3.2 rho = 0 (tau = 1)
Primary route (uses only Lemma 6.1, a declared FT_q dependency): H is continuous on M_lambda (P1 Lemma 6.1(iii)).  The face points (rho_b, z_b) with
tau -> 1- lie in M_lambda and converge to (0, lambda); H > c_FT along them by 3.1, hence H(0, lambda) >= c_FT = m0.
Cross-check (optional route, not required): NP-T gives H(0, lambda) = E_rhorho(0, lambda) > 13/2000 (FT_q (9.1), from NP-T (9.1) lambda(13/1000)),
and 13/2000 > c_FT, consistent with m0 = min(c_FT, 13/2000) = c_FT (22'' frozen formula; c_FT certificate branch (K4)).

## 4. Certified evidence chain (all pins previously audited)
| link | evidence | commit | state |
|---|---|---|---|
| 2 pi lambda H = int G (P units) | H-43-1(i) closure, chain (C1)-(C5) | c4d49d81884a9dfebb82839236c84cee8add1ceb | CLOSED |
| South density = North density a.e. (R-G) | 22'' closure record v1 §4 | e0f59439950e59e930f3261216422da89d81a29d | CLOSED |
| int_{-1}^{1/2} G >= S''_lb | south paper proof; kernel_extension_cert | 05668a47216e243450211f0cf438702dc6d1527c; 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e | CHAT AUDIT PASS (canonical import pending) |
| U_north < 5481/10000 | contract 45 pieces 1-3 | 99c9b62a..., 7ba339a8..., 9cb723c0... | CHAT AUDIT PASS |
| U_near <= 3887073979116207/17284813033600000 | contract 43 (frozen predeclare 97d85f59, certificate 7f71fb43, run bd512f53) | — | CERTIFIED |
| 22'' v1.2 condition U_north + U_near < S''_lb | canonical contract v1.2 | d445b302bd879b5dc5211c7ba310d5aef036f31e | CLOSED |
| Delta, c_FT, m0 | c_FT predeclare v1 (FROZEN) b3127b4e; certificate 31368987; run evidence 87b7c5af | — | SET |
| (8.1) / (8.2) | Boundary Pair Lemma v1 | 6d106cbdde12cb172b4ca137b7b03697875f1d54 | PAPER AUDIT PASS / v1 FIXED |

## 5. NOT_BINDING dependencies (carried, not upgraded)
P1 design note (`analysis/D_OB_P1_DESIGN_NOTE.md`, commit 69e104602e939817b6f4d71df3f6bd63cbc729e0, blob f81e120e44a866d206117d4fab5fac627f26ccd1,
SHA-256 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9), recorded status CHAT_ANALYTIC_DERIVATION_PASS / EXTERNAL_AUDIT_PENDING /
NOT_BINDING.  Used:
 - Lemma V (a)(b)(c) (§5, lines 83-95): convergence, interior differentiation under the integral, continuity on closure(K) (H-43-1(i), E3 of BPL).
 - Lemma 6.1 (§6, line 107): (i) evenness, (ii) FTC, (iii) H = E_rho/rho for rho > 0 and continuity of H on M_lambda (E1 of BPL; §3.2 above).
 - Lemmas 3.4, 4.2, Corollary 4.3 (cited inside Lemma V).
Consequence: FT_q is closed RELATIVE TO these P1 results.  Their external audit remains a gate of D-P2 (Judge 案A).

## 6. What this record distinguishes
FT_q mathematical target: ACHIEVED (H >= m0 > 0 on the frozen face), relative to §5.
NOT established by this record:
 - D-P2 certification.  The predeclare v1.2 §"D-P2 handoff boundary": D-AN-1 does not claim that the numerical unresolved boxes may be removed from
   D-P2; the theorem-to-D-P2 handoff is a separate audited stage.
 - T1 = L0 + L1 + L2 + FT_q + QM + L3 (predeclare v1.2 DAG): only the FT_q node is addressed here; L3 (recorded as blocked on FT_q), L1 (recorded as
   paused) and the other nodes are not assessed.
 - External audit of the P1 note (§5); canonical import of the south paper proof.

## 7. Discrepancies in source status labels (for CHAT AUDIT; no change made)
 - Predeclare v1.2 file header reads "v1.2 DRAFT / AWAITING CHAT FULL-DIFF AUDIT / NOT FROZEN", while the FT_q reduction draft cites it as the
   "Frozen parent ... FROZEN".  Which label governs the node statement of §1 is for the Judge to confirm.
 - NP-T file header (`analysis/D_OB_P2_D_AN1_NP_T_DRAFT.md`, commit 99467ed5e51a9b60c88073fda7a8f0094ebe770c, SHA-256 e929d956...) reads
   "PAPER-PROOF DRAFT / AWAITING CHAT AUDIT", while the FT_q draft cites "AUDIT PASS / CROSS-CHECK".  §3.2 does not depend on NP-T (primary route is
   Lemma 6.1(iii) continuity), so this affects only the optional cross-check.

## 8. Proposed ruling for the Judge (after CHAT AUDIT)
FT_q: DISCHARGED (conditional), m0 = 540861826035521/336806928254720000, conditional on the external audit of the P1 note results in §5.
Boundary Pair Lemma: CLOSED.  D-P2: NOT_CERTIFIED.
