# D-OB P2 / D-AN-1 — L1 reach lemma (delta_L1) — SPECIFICATION DRAFT v0 (Code, 2026-10-09)

STATUS: SPECIFICATION ONLY / SUBMITTED FOR CHAT AUDIT / NOT FROZEN.  No proof, no computation, no execution.  L1 PAUSED (only drafting of this
specification is released, Judge 案A).  Connection QM–L3–L1: UNDETERMINED.  D-P2 NOT_CERTIFIED.  delta_L1 stays a symbol throughout.
Evidence state used: E1 (pointwise-pair) and E2 (G1) REPORTED / EVIDENCE NOT FOUND; E3 (G2 material) only referenced at predeclare v1.2 lines 110, 270,
original NOT FOUND (evidence report f7d8f4cc053c712536f4ff9819ce898b5619454f, SHA-256 f23a770d12dc1c9b675a9307a9549838962bf79e475573285555e57c6ab08b8f).

## S1. Statement to be proved (item 1)
Domain (predeclare v1.2 §1.1, e9c8b1caa3ad502a3d01dafe354b61108787eed2): for
    lambda in [2/5, 93/200],  tau in [7/8, 1],  r in [7/8, sqrt(1 - delta_L1)]   (equivalently delta = 1 - r^2 in [delta_L1, 15/64]),
    rho = r rho_b(tau),  z = lambda r m(tau),  rho_b = (1-tau^2)/(1+tau^2),  m = 2tau/(1+tau^2),
**Lemma L1-R(delta_L1).**  H(rho, z; lambda) > 0 at every such point.
Admissible strengthening (recommended, not required by T1): an explicit rational h_L1 > 0, independent of (lambda, tau, r), with H >= h_L1.
Connection condition (not part of the lemma; recorded for the later route decision): L1-R closes T1 together with L3 iff delta_L1 <= delta0, where with
the current m0 the frozen L3 condition omega_E(delta0) < m0 admits delta0 = 3/20000000000 and fails for delta0 >= 1/6250000000 (Astra and Code reverse
feasibility reports, 9e64fce9 §9).  The lemma is specified for a symbolic delta_L1 so that this comparison is made only after its proof.

## S2. G2 structure: the cancellation to be preserved (item 2)
Representation at an interior base point p = (rho, 0, z), r < 1 (no boundary specialization):
    2 pi lambda H(p) = int_{-1}^{1} G_p(mu) dmu,   G_p(mu) := int_0^pi K_H(p; mu, phi) dphi,
    K_H = (calF_xi(rho) - calF_xi(-rho))/(2 rho) = (1/(2 rho)) int_{-rho}^{rho} calF_xixi dxi  (rho > 0),
derived as in H-43-1(i) closure c4d49d81 §3(C) (C1)-(C5) but at interior base points (all steps there for |xi| < rho hold with D bounded below; the
boundary-trace steps are not needed for r < 1).
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
 (a) the old D-P2 failure was traced to natural-interval enclosure of the near-column kernel losing the correlation between numerator and 1/D
     (overestimation by about 15x, pole-cut penalty), and L1-R contains exactly such a near-boundary layer when delta_L1 is small;
 (b) S4 shows the termwise bound degrades as delta_L1 -> 0, so an interval proof would have to choose delta_L1 large, which is a decision that may not be
     made from diagnostics (predeclare v1.2 line 110: "no diagnostic value may choose the split").
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
 - South positive mass S''_lb (paper proof 05668a47) is a boundary statement; an interior positive-mass bound is a new obligation.
 - The certified boundary margin m0 is an input to L3 only; L1-R does not use it.

## S7. Obligations created by this specification (to be predeclared before any proof)
 O1 interior representation (S2) with its derivation at r < 1;  O2 interior positive-mass lower bound on I_+;  O3 interior negative-part upper bounds on I_-
 with cancellation kept near the closest surface point (S4);  O4 rho -> 0 route (S3);  O5 endpoint and uniformity certificates;  O6 coverage of I_+ ∪ I_-.
 None is started.  delta_L1 is fixed only by the predeclare that follows the CHAT AUDIT of this specification and the Judge's route decision.
