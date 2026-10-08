# Contract 43 — North near band — PREDECLARE DRAFT v1

STATUS: WORKING DRAFT v1 / NOT FROZEN / NOT YET SUBMITTED (formal submission as v1 follows receipt of Astra's independent report,
chat ruling 2026-10-09 item 8) / NOT AUTHORIZED FOR CERTIFICATE EXECUTION.  Contract 43 OPEN.  D-P2 NOT_CERTIFIED.
This document contains no diagnostic values; method choices are justified structurally (section 4).
Changelog v0 (7cebf22c, chat pre-review) -> v1: items 1-8 of the chat ruling of 2026-10-09 (see section 7).

## 0. Fixed evidence (identity class, CHAT AUDIT PASS)
| item | commit | SHA-256 |
|---|---|---|
| (43.1)-(43.3) decomposition of N, pointwise |N| <= C D^2: `ftq_cert/n43_decomposition_cert.py` | a3bed35b7b9912081afd7f8819fb2306840ab49e | 04e7358375c81328a8cd4c628cead339477233f831e21bd8a623ac5395090c6d |
| (C3.1)-(C3.3) xi-antiderivatives F1, F2 by differentiation: `ftq_cert/n43_xi_antiderivative_cert.py` | db8ef8da590329d207aa8d8b18d7198bf1b7e251 | a0aad6ae55e257fb0bd2aeb73e97d62f0177401f305fc3f748dbcd687696801a |
| contract 44 (N1-N3) and 46: `ftq_cert/n3_identities_cert.py` | 79588e2e9373c06aa80589a5ab7ffe1611be99d7 | a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c |
Contract 46 is NOT used in this contract (it needs a >= rho).

## 1. Region and chain inherited (frozen sources)
Definition of the band variable: s := m - mu, where mu is the surface coordinate (mu in [-1, 1]) and m = 2 tau/(1 + tau^2).
Formal band (contract 24, kappa = 1): |mu - m| <= rho, i.e. s in [-rho, rho].  Physical region: the formal band intersected with the
surface mu <= 1, i.e. s in [m - 1, rho] (the part s in [-rho, m - 1) corresponds to mu > 1 and is not part of the surface).
All integrals of this contract are over the physical region s in [m - 1, rho];  |xi| <= rho;  phi in [0, pi].
Box: L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2.
(S0) as in contract 45: [-K_H]_+ <= pi * mean_xi [2N^2 - h^2 T]_+/(w D^5) <= pi * mean_xi 2N^2/(w D^5)   (contract 44, N2/N3),
pointwise wherever D > 0.  U_near <= int_{m-1}^{rho} int_0^pi mean_xi pi 2N^2/(w D^5) dphi ds.
Pairing (xi, phi) -> (-xi, pi - phi) may be used as in contract 45 (never halve xi alone at fixed phi).
NOT inherited: (S1) D >= D_0 (needs a >= rho, false for s < 0, and D_0 degenerates as s -> 0); contract 46.

## 2. Pieces (<= 2, per the 8-piece cap: 3 far + 2 near)
 J_1 (cap) = [m - 1, 0]  (a <= rho),   J_2 (band) = [0, rho]  (a >= rho).   No phi split.  No xi split.
 The piece boundary s = 0 is structural: sign(s) = sign(a - rho).  No boundary, constant or kappa comes from a diagnostic.
 Singular points: D = 0 exactly at (s, phi, xi) = (0, 0, rho) and (0, pi, -rho).  They lie ON the common boundary s = 0 of J_1 and J_2
 (surface point = base-segment endpoint).  Both pieces therefore touch the singularity; neither piece inherits any far-band lower
 bound (D_0 chain, contract 46), and the cap piece J_1 has a < rho throughout its interior.

## 3. Candidate chain (to be confirmed/replaced after collation with the Astra report)
 (C1) N = lambda[ b (q^2 + L s^2) + p (s(m - s) - q^2) ],  p = b - xi, q = a sin phi  (fixed evidence a3bed35b).
 (C2) 2N^2 <= 4 lambda^2 [ b^2 e^4 + p^2 (s(m - s) - q^2)^2 ],   e^2 := q^2 + L s^2 = D^2 - p^2.
 (C3) xi-integration in closed form over the FINITE range p in [b - rho, b + rho] with e fixed (fixed evidence db8ef8da):
      int (p^2+e^2)^{-5/2} dp = F1(p) = p(2p^2 + 3e^2)/(3 e^4 (p^2+e^2)^{3/2}),   int p^2 (p^2+e^2)^{-5/2} dp = F2(p) = p^3/(3 e^2 (p^2+e^2)^{3/2}).
      The xi-mean of each term is a DIFFERENCE  F_k(b + rho) - F_k(b - rho)  (times its (s, phi)-coefficient and 1/(2 rho)).
      Extension of the p-range to R is not planned (section 4(d)); finite limits are kept.
 (C4) w >= m - s >= m - rho on J_2 and w >= m on J_1;  b^2 <= a^2;  a^2 = rho^2 + 2ms - s^2 exact;  e^2 >= L s^2 and e^2 >= q^2.
 (C5) MAIN ROUTE (i), chat ruling: "finite-range xi-integral (algebraic) -> rational majorant -> Bernstein exact evaluation",
      with the DIFFERENCE STRUCTURE PRESERVED.  Chat addendum (2026-10-09): after the finite-range xi-integration the two terms are
      treated as INSEPARABLE EVALUATION UNITS:
        unit 1:  b^2 e^4 DeltaF1,   DeltaF1 := F1(b+rho) - F1(b-rho),   with the structural fact  0 <= e^4 DeltaF1 <= 4/3;
                 e^4 and DeltaF1 are never bounded separately (no artificial e^{-4} singularity is introduced);
        unit 2:  A^2 DeltaF2,  A := s(m-s) - q^2,  DeltaF2 := F2(b+rho) - F2(b-rho),  with  0 <= DeltaF2 <= 2/(3e^2);
                 the product is the object of the estimate; the factor e^{-2} is never bounded on its own.
      The vanishing of A near the diagonal singular points may be used, but a uniform constant obtained from a LOCAL approximation
      is not admissible: any such use must be an exact inequality with its residual.  Boundedness near the singular points and
      budget compliance on the whole box are SEPARATE proof obligations (L43-E vs L43-Q below).  Design:
      (C5.1) scale p = e u.  Then  F1(b+rho) - F1(b-rho) = e^{-4} [G1(U+) - G1(U-)],  F2(...) = e^{-2} [G2(U+) - G2(U-)],
             U± := (b ± rho)/e,  G1(U) = U(2U^2+3)/(3(1+U^2)^{3/2}),  G2(U) = U^3/(3(1+U^2)^{3/2})  (G_k = int_0^U of the scaled integrands).
             Unit 1 is then b^2 * [e^4 DeltaF1] = b^2 [G1(U+) - G1(U-)], a bounded quantity.  For unit 2 the exact (approximation-free)
             bound  A^2/e^2 <= 2 s^2 (m-s)^2/e^2 + 2 q^4/e^2 <= 2 (m-s)^2/L + 2 q^2  (using e^2 >= L s^2 and e^2 >= q^2)  gives
             A^2 DeltaF2 <= (2/3)[2 (m-s)^2/L + 2 q^2] = 4 (m-s)^2/(3L) + 4 q^2/3, finite and uniform near e -> 0.  This is the content
             of the planned endpoint lemma L43-E (section 6, H-43-1(ii)); it removes the singularity but is coarse and is NOT the
             quantitative estimate used for the budget (L43-Q).
      (C5.2) rational majorant of the DIFFERENCE, not of the endpoints: choose, on each sign half-line u >= 0 / u <= 0 (splitting the
             p-range at p = 0 when it contains 0), a RATIONAL function H_k with H_k' >= g_k (g_1 = (1+u^2)^{-5/2}, g_2 = u^2 (1+u^2)^{-5/2})
             and H_k bounded, increasing.  Then  G_k(U+) - G_k(U-) = int_{U-}^{U+} g_k <= H_k(U+) - H_k(U-),  a rational difference that
             vanishes with the interval length and stays bounded as U± -> infinity (this is what "preserving the cancellation" means;
             bounding G_k(U+) and G_k(U-) separately would lose it).  Candidate family (parameters to be fixed in v1 by matching
             H_k(0) = 0, H_k'(0) = g_k(0), H_k(+infinity) = G_k(+infinity) = 2/3 resp. 1/3):  H_k(u) = c_k u (u^2 + alpha_k)/((u^2 + beta_k)(u + gamma_k)),
             u >= 0 (odd extension for u <= 0).  The inequality H_k' >= g_k is certified as a polynomial inequality after clearing
             denominators and squaring (both sides positive), on u in [0, infinity) via u = v/(1 - v), v in [0, 1) (Bernstein).
      (C5.3) substitute U± = (b ± rho)/e: the majorant becomes a rational function of (b, e, rho); with b = a cos phi, e^2 = a^2 sin^2 phi + L s^2
             it is a rational function of (cos phi, sin phi, s, rho, L, m) after the substitution a^2 = rho^2 + 2ms - s^2 and a possible
             rationalization of a (a appears linearly in b; use the piece-wise monotone bounds of (C4) or square where the sign is fixed).
      (C5.4) phi- and s-integration of the rational majorant by exact rational arithmetic where closed-form, otherwise by monotone/convex
             bounds and Bernstein on the box, with the few irrational constants (pi, sqrt) enclosed rationally as in pieces 2-3.
      ALTERNATIVE ROUTE (ii) (appendix candidate only, chat ruling item 3): algebraize the phi-integral by q = a sin phi before the
             s-integration.  Admissible only if the elimination of the square roots is shown by an exact identity; otherwise not used.
 (C6) exact rational comparison of U_near,cert with the frozen budget text in force at submission time.  The budget is FIXED AFTER
      the repository commit and pin of 22'' v1.2 (Judge adopted, commit pending); until then this line carries no number.

## 4. Structural reasons for the method choice (no diagnostic values)
 (a) Pointwise chain |N| <= C D^2, then 2C^2/(wD).  The constant C is of order 1 while N/D^2 is of order 1 only where
     |p| ~ sqrt(L)|s| and q <~ sqrt(L)|s| (second term of (C1)); off that cone N/D^2 is smaller.  The chain discards this,
     replacing N^2/D^4 by its supremum on the whole band.  Rejected.
 (b) First term with e^4 <= D^4 before the xi-integral (i.e. 4 lambda^2 b^2/(wD)).  The exact xi-integral of e^4/D^5 over p is
     concentrated on |p| <~ e and is O(1/e) in size, whereas int dp/D over |p| <= 2 rho is of size log(rho/e) when e << rho:
     the relaxation loses the factor (e/D)^4 exactly where the xi-integral lives.  Rejected.  (No claim about the order in rho of
     the retained term is made here; such statements are motivation only and are not part of the predeclare.)
 (c) Second term with p^2 <= D^2 before the xi-integral (i.e. 4 lambda^2 (s(m-s) - q^2)^2/(wD^3)).  The exact xi-integral of
     p^2/D^5 is 2/(3e^2) over R while that of 1/D^3 is 2/e^2: a factor 3 is lost pointwise in (s, phi), uniformly.  Rejected in
     favour of keeping p^2 inside the xi-integral, which costs nothing (both are elementary).
 (d) Extension of the p-range to R in (C3).  One-sided and exact-closed-form, but for e >~ rho the integrand (p^2+e^2)^{-5/2}
     has most of its mass at |p| > 2 rho, outside the true range [b - rho, b + rho] of length 2 rho.  Finite limits are kept.
 (e) Positive part [2N^2 - h^2 T]_+ : dropped in (S0).  h vanishes at the singular points together with N (h = lambda(k - xi b),
     k - xi b -> 0 there), so the subtraction does not change the order of the singularity; keeping it would require a sign
     analysis of 2N^2 - h^2 T that is not needed for integrability (Q0).  May be restored later if the budget requires.
 (f) Endpoint-separate bounds in (C5): rejected because the exact xi-mean is a difference of two large endpoint values when
     U- and U+ have the same sign and |U±| >> 1 (e << |b| - rho); separate bounds would be of size O(1) each while the difference
     is O(U+ - U-) * sup g_k.  See (C5.2).

## 5. Analytic obligations H-43-1 (chat label; Code reading of the split, to be confirmed)
 H-43-1(i) INTERNAL INTERCHANGE: the chain uses (S0) pointwise off the null set {D = 0} = two points, then integrates xi first, then
     (phi, s).  All integrands after (C2) are nonnegative, so the order of integration and the xi-mean/integral interchange are
     justified by Tonelli; the pairing (xi, phi) -> (-xi, pi - phi) is a measure-preserving involution of the (xi, phi) domain under
     which 2N^2/(wD^5) is invariant (b -> -b, xi -> -xi; p -> -p, q, e, w unchanged).  Planned as a paper lemma L43-I (no computation).
 H-43-1(ii) ENDPOINT BOUNDARY VALUES: the finite-range xi-integral equals F_k(b+rho) - F_k(b-rho) only for e > 0; e = 0 is the null set
     {sin phi = 0, s = 0}.  The (phi, s)-integrability near e -> 0 must be shown for the MAJORANT, not assumed: planned lemma L43-E,
     stating  e^4 [G1(U+) - G1(U-)] <= 4/3  and  e^2 [G2(U+) - G2(U-)] <= 2/3  (from int over R of the scaled integrands) and the
     boundedness of the (s, phi)-coefficients, so that the majorant is bounded on the band and the singular set is negligible.
     UNRESOLVED until certified; this is the open endpoint obligation named by chat.

## 6. Planned lemmas (names fixed here; none certified yet)
 L43-I  interchange / pairing (paper).     L43-E  endpoint boundedness (definite-integral statement: NOT executed before PASS of this predeclare).
 L43-H  rational majorants H_k with H_k' >= g_k (polynomial Bernstein certificate).     L43-Q  (phi, s)-integration of the majorant (exact).

## 7. Governance and changelog
 Audit path: Astra L43 structure audit (independent; Code material not shared) -> chat collation -> this predeclare frozen as v1 (or v2)
 -> Code certificate -> CHAT AUDIT.  Code will not execute any integral-evaluation certificate before the predeclare PASS.
 v1 changes (chat ruling 2026-10-09): [1] fixed evidence table; [2] (C5) main route (i) with difference structure, (C5.2) and 4(f);
 [3] route (ii) appendix-only; [4] H-43-1 split into (i)/(ii), section 5; [5] O(rho) motivation removed from 4(b); [6] singular points
 and non-inheritance in section 2; [7] (C6) budget deferred to the 22'' v1.2 pin; [8] formal submission after the Astra report; v1 addendum: (C5) inseparable units 1 and 2 (chat 2026-10-09).
