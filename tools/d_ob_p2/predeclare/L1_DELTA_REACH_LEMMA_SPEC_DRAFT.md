# D-OB P2 / D-AN-1 — L1 reach lemma (delta_L1) — SPECIFICATION DRAFT v1 (Code, 2026-10-09)

STATUS: SPECIFICATION ONLY / SUBMITTED FOR CHAT AUDIT / NOT FROZEN.  No proof, no computation, no execution.  L1 PAUSED (only drafting of this
specification is released, Judge 案A).  v1 = v0 (012c4336dd889e669dc92bfab2b24e63de670f58, CHAT AUDIT CONDITIONAL PASS) + items A, B, C, D, S8, E
of L1-DELTA-REACH-SPEC-v1 only.  Connection QM–L3–L1: UNDETERMINED.  D-P2 NOT_CERTIFIED.  delta_L1 stays a symbol throughout.
Evidence state used: E1 (pointwise-pair) and E2 (G1) REPORTED / EVIDENCE NOT FOUND; E3 (G2 material) only referenced at predeclare v1.2 lines 110, 270,
original NOT FOUND (evidence report f7d8f4cc053c712536f4ff9819ce898b5619454f, SHA-256 f23a770d12dc1c9b675a9307a9549838962bf79e475573285555e57c6ab08b8f).

## S1. Statement to be proved (item 1)
Domain (predeclare v1.2 §1.1, e9c8b1caa3ad502a3d01dafe354b61108787eed2): for
    lambda in [2/5, 93/200],  tau in [7/8, 1],  r in [7/8, sqrt(1 - delta_L1)]   (equivalently delta = 1 - r^2 in [delta_L1, 15/64]),
with the symbol delta_L1 restricted to   0 < delta_L1 <= 15/64   [item A].  No value of delta_L1 is chosen by this specification.
    rho = r rho_b(tau),  z = lambda r m(tau),  rho_b = (1-tau^2)/(1+tau^2),  m = 2tau/(1+tau^2),
**Lemma L1-R(delta_L1).**  H(rho, z; lambda) > 0 at every such point.
Admissible strengthening: an explicit rational h_L1 > 0, independent of (lambda, tau, r), with H >= h_L1.  [item B] It is optional only if the axis
rho = 0 is proved independently (S3); if the axis is reached by the continuity extension of S3, h_L1 > 0 is REQUIRED.  Its dependence on delta_L1 is
governed by S8.
Connection condition (not part of the lemma; recorded for the later route decision): L1-R closes T1 together with L3 iff delta_L1 <= delta0, where with
the current m0 the frozen L3 condition omega_E(delta0) < m0 admits delta0 = 3/20000000000 and fails for delta0 >= 1/6250000000 (Astra and Code reverse
feasibility reports, 9e64fce9 §9).  The lemma is specified for a symbolic delta_L1 so that this comparison is made only after its proof.

## S2. G2 structure: the cancellation to be preserved (item 2)
Representation at an interior base point p = (rho, 0, z), r < 1 (no boundary specialization):
    2 pi lambda H(p) = int_{-1}^{1} G_p(mu) dmu,   G_p(mu) := int_0^pi K_H(p; mu, phi) dphi,
    K_H = (calF_xi(rho) - calF_xi(-rho))/(2 rho) = (1/(2 rho)) int_{-rho}^{rho} calF_xixi dxi  (rho > 0),
derived as in H-43-1(i) closure c4d49d81 §3(C) (C1)-(C5) but at interior base points (all steps there for |xi| < rho hold with D bounded below; the
boundary-trace steps are not needed for r < 1).
[item C] The boundary instance of this representation (2 pi lambda H = int G dmu at p_b, used in 22'' v1.2 and R-G) may NOT be imported for r < 1.
Its validity at interior base points is a proof obligation (O1): it must be derived independently at p = (rho, 0, z), r < 1, including the
justification of every interchange of differentiation in (rho, xi) with the (mu, phi) surface integration (dominating bounds valid uniformly on the
L1 layer, using D >= delta/5 of S4).  The citation of c4d49d81 above names the template, not a proof.
[item E] Existing FT_q resources stated at a general base point (FT_q draft 20c5c59b, analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md, SHA-256 46443f0e...):
 - FT_q (5.2): N_J := w D^3 J = A2 b^2 + A1 b + A0, with A2, A1, A0 written with z as a free symbol, i.e. BEFORE the boundary reduction
   z = lambda m, rho^2 + m^2 = 1 of FT_q §6;
 - FT_q (7.1): the b-pair finite-difference identity gamma_+ - gamma_- = 4 rho b [h0 c(mu) + lambda^2 rho^2 b^2] / [w D_+ D_- (h_+ D_- + h_- D_+)],
   h0 = lambda - z mu, with c(mu) of FT_q (7.2) written with general (rho, z).
 Both are described in the FT_q draft as coming from the "L1 route" / "L1 analysis" (its lines 140, 176).  They are distinct from the boundary-only
 factorization FT_q (6.1) N_J = -lambda^2 (m - mu) Q (see S4), and they must NOT be identified with the unlocated G2 material (E3, ORIGINAL NOT FOUND).
 Conditions for interior use: FT_q §2 states the geometry (h, D^2, w^2) for the boundary base point; before (5.2) or (7.1) is used at r < 1 the
 interior forms of h, D^2 (expected h = lambda - z mu - lambda rho b, D^2 = a^2 + rho^2 + (lambda mu - z)^2 - 2 rho b; to be derived from P1, not
 assumed) must be substituted and (5.2), (7.1), (7.2)
 re-derived at general (rho, z) (part of O1); the positivity of the denominator of (7.1) (h_+ D_- + h_- D_+ > 0) must be proved for r < 1; the
 Lipschitz step (7.3) rests on the P1 trap -1 <= R_gamma <= 0 (P1 note, NOT_BINDING, carried).
 Obligations that remain after these resources: (5.2) gives the b-structure of N_J but no sign, and in the interior there is no factor (m - mu); (7.1)
 controls the R-difference of a b-pair but gives no lower bound.  Positivity of int G_p dmu is still to be obtained through the split below (O2, O3, O6).
G2 condition (the analytic route): positivity is to be proved for the mu-INTEGRATED quantity int G_p dmu, by a split of the form
    int G_p >= int_{I_+} G_p - int_{I_-} [-G_p]_+ ,    I_+ ∪ I_- = [-1, 1],
with a certified positive-mass lower bound on I_+ and certified negative-part upper bounds on I_-, exactly as in 22'' v1.2 at the boundary
(S''_lb vs U_north + U_near).  The overlap/coverage of I_+, I_- must be proved by rational inequalities.
Prohibited inside the proof of L1-R:
 - assuming uniform pointwise-pair positivity (the property E1 reportedly refutes);
 - assuming G_p(mu) >= 0 for every mu (G1; reportedly refuted by E2);
 - using the negative sign of E1 or E2 as a known fact (both are REPORTED / EVIDENCE NOT FOUND);
 - using the content of the unlocated G2 material; if it is located later it may be cited only after its own pin and audit.

## S3. rho -> 0 extension and endpoints (item 3)
 - Representation to be used everywhere, including rho = 0: H(rho, z) = int_0^1 E_rhorho(t rho, z) dt (P1 Lemma 6.1(iii); NOT_BINDING, carried).
   At rho = 0 this gives H(0, z) = E_rhorho(0, z); no division by rho and no separate treatment of E_rho/rho is permitted.  The G2 split of S2 is stated
   for rho > 0; the rho = 0 edge (tau = 1, z = lambda r) is reached either by continuity of H (Lemma 6.1(iii)) from rho > 0 with the same uniform
   bound h_L1, or by a separate axis argument with its own bound.  Which of the two is used is fixed in the predeclare that follows this spec.
   [item B] On the continuity route a uniform bound h_L1 > 0 on rho > 0 is a necessary condition: strict positivity H > 0 at every interior point
   with rho > 0 does NOT imply H > 0 on the axis (a limit of positive values may be 0); continuity then gives only H(0, z) >= h_L1.  The independent
   axis proof remains an admissible alternative.
 - Endpoints to be covered explicitly: tau = 7/8 and tau = 1; lambda = 2/5 and 93/200; r = 7/8 (delta = 15/64) and r = sqrt(1 - delta_L1).
   Uniformity in all four parameters must be by analytic bounds or exact rational certificates on closed boxes, never by sampling.

## S4. Near-boundary structure (item 4)
 - Distance: for p = r p_b and any boundary point q in the same meridian, |p - q| >= lambda (1 - r) >= delta/5 (Astra reverse report (5.4); Code
   re-derived).  Hence on the L1 layer D >= delta_L1/5, and any bound that uses |F_rhorho| <= C2/D termwise or a 1/D majorant degrades like 1/delta_L1
   (pointwise) or log(1/delta_L1) (after surface integration, P1 Lemma 4.2), as delta_L1 -> 0.  The specification therefore requires that near the
   surface point closest to p the cancellation in the paired/xi-averaged kernel be kept (as the N3 identity and the (5.5)–(5.7) chain did at the boundary
   in Contracts 44/43), not replaced by |kernel| <= C/D.
 - Boundary factorization: FT_q (6.1) N_J = -lambda^2 (m - mu) Q uses z = lambda m and rho^2 + m^2 = 1 (boundary base point).  At an interior point
   z/lambda = r m and rho^2 + (z/lambda)^2 = r^2 < 1, so (6.1) is NOT assumed in the interior; any interior analogue must be derived and certified anew.
   The same applies to contract 44 (N3 identities): its ring relation rho^2 = 1 - m^2 is a boundary relation; interior use requires re-derivation with
   rho^2 + (z/lambda)^2 = r^2.
 - The distinguished latitude: at the boundary the factor (m - mu) vanishes on mu = m; in the interior no such exact zero is assumed.

## S5. The G-numbered interval-proof option (predeclare v1.2 line 110) (item 5)
Position of this spec: the interval option is NOT adopted here.  Reasons:
   [item D] Conventional natural-interval evaluation loses the correlation between numerator and denominator, so certification for small
   delta_L1 is EXPECTED to be difficult.  This is a stated expectation, not a claim that interval proofs are impossible in general.  Kept open as
   future options: correlation-preserving interval evaluation; evaluation that carries symbolic identities through the enclosure; methods that
   enclose the integrated quantity directly.
If the Judge later selects the interval option, the separate G-numbered predeclare must at least: enclose integrated or paired quantities (not the
pointwise density); carry exact algebraic identities (N3-type, R-G-type) inside the enclosure so cancellations are symbolic, as in the Bernstein
certificates of Contracts 43/45; fix delta_L1 and the box partition before any run; and state the failure mode (loss of correlation) as a predeclared
stop condition.

## S6. Relation to existing resources (item 6)
 - Contract 45 (north far, CHAT AUDIT PASS) and Contract 43 (north near, CERTIFIED): proved at the BOUNDARY base point p_b (rho = rho_b, z = lambda m).
   Their methods (N3 majorant, D >= D_0 or Lipschitz/projection chain, exact rational integration) are templates for the interior negative part, but
   their identities use rho^2 = 1 - m^2 and must be re-derived for r < 1 before reuse.
 - R-G (22'' closure record v1 §4): proves G_P = G_K a.e. at the boundary base point via FT_q (4.2), the reflection, and (6.1); for interior points the
   reflection argument (G1) and the integration by parts (4.2) carry over (they do not use the boundary), but the step through (6.1) does not.
 - FT_q R J representation (4.4): H = (2 pi lambda rho)^{-1} int int R J holds at the boundary base point; its derivation (3.1)-(4.3) uses only D > 0 and
   the full azimuth, and should be re-checked at interior base points; the quadratic structure of N_J (5.2) is general, (6.1) is boundary-only.
   [item E] FT_q (5.2) and (7.1) are general-point resources subject to the interior-use conditions and remaining obligations stated in S2.
 - South positive mass S''_lb (paper proof 05668a47) is a boundary statement; an interior positive-mass bound is a new obligation.
 - The certified boundary margin m0 is an input to L3 only; L1-R does not use it.

## S7. Obligations created by this specification (to be predeclared before any proof)
 O1 interior representation (S2) with its independent derivation at r < 1, including the differentiation/integration interchanges and the
 interior re-derivation of FT_q (5.2), (7.1), (7.2) before any use [items C, E];  O2 interior positive-mass lower bound on I_+;  O3 interior negative-part upper bounds on I_-
 with cancellation kept near the closest surface point (S4);  O4 rho -> 0 route (S3);  O5 endpoint and uniformity certificates;  O6 coverage of I_+ ∪ I_-.
 None is started.  delta_L1 is fixed only by the predeclare that follows the CHAT AUDIT of this specification and the Judge's route decision.

## S8. Dependence on delta_L1 [item S8]
Two forms of the lower bound are distinguished; the predeclare must state which one is targeted.
 Form I  (delta_L1-dependent):  H >= h_L1(delta_L1) > 0 on the L1 layer, with the dependence of h_L1 on delta_L1 stated explicitly.
 Form II (uniform as delta_L1 -> 0):  H >= h_* > 0 with a constant h_* independent of delta_L1.
Observation (not a change of dependencies): if Form II holds in a form that covers the target region uniformly up to the boundary, then the
connection of positivity might no longer need FT_q, QM or L3.  This is an observation about the possibility of an L1-only connection; it does not
modify the dependency structure of the frozen D-AN-1, which can change only by a separate Judge decision.
Two uniformities are separate proof requirements and neither implies the other:
    uniformity as rho -> 0 (tau -> 1, the axis; S3)   !=   uniformity as delta -> 0 (r -> 1, the surface; S4).
A bound uniform in rho -> 0 at fixed delta_L1 says nothing about delta_L1 -> 0, and conversely; each must be proved and stated on its own.
