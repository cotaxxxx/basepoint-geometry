# Contract 43 — North near band — PREDECLARE DRAFT v0

STATUS: WORKING DRAFT v0 / NOT FROZEN / NOT YET SUBMITTED (formal submission follows the CHAT AUDIT of the identity certificate
n43_decomposition_cert.py, per the chat order of 2026-10-09) / NOT AUTHORIZED FOR CERTIFICATE EXECUTION.
This document contains no diagnostic values; method choices are justified structurally (section 4).  Conditional on (i) the Astra structure audit of L43 and
(ii) the budget decision (22'' v1.2 adopted by the Judge, repository commit pending; v1.1 remains the frozen text).
No constant, threshold, piece boundary or kappa in this document comes from a diagnostic; the piece boundary s = 0 is structural
(sign of s = sign of a - rho; cap side a < rho).

## 1. Region and chain inherited (frozen sources)
Near band (contract 24 baseline band kappa = 1, contract 21'' v1.1): |mu - m| <= rho, mu <= 1  <=>  s := m - mu in [-rho, rho] cap {mu <= 1}
= [m - 1, rho]  (cap side mu > m is s < 0; m - 1 = -rho^2/(1+m) > -rho);  |xi| <= rho;  phi in [0, pi].
The diagonal singular points (s = 0, phi in {0, pi}, xi = +-rho) lie inside the band; Q0 (applicability of the N3 form) is answered
in CONTRACT43_CODE_PRELIM_NOTE.md section 0': pointwise inequalities hold off a null set and the kernels are absolutely integrable.
Box: L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2.
(S0) as in contract 45: [-K_H]_+ <= pi * mean_xi [2N^2 - h^2 T]_+/(w D^5) <= pi * mean_xi 2N^2/(w D^5)   (contract 44, N2/N3).
U_near <= int_{m-1}^{rho} int_0^pi mean_xi pi 2N^2/(w D^5) dphi ds.   Pairing (xi, phi) -> (-xi, pi - phi) may be used as in 45.
NOT inherited: (S1) D >= D_0 (needs a >= rho, false for s < 0; and D_0 degenerates as s -> 0), contract 46.

## 2. Pieces (<= 2, per the 8-piece cap: 3 far + 2 near)
 J_1 (cap) = [m - 1, 0]  (a <= rho),   J_2 (band) = [0, rho]  (a >= rho).   No phi split.  No xi split.

## 3. Candidate chain (to be confirmed/replaced by the L43 audit)
 (C1) N = lambda[ b (q^2 + L s^2) + p (s(m - s) - q^2) ],  p = b - xi, q = a sin phi  (certified: n43_decomposition_cert.py).
 (C2) 2N^2 <= 4 lambda^2 [ b^2 (q^2 + L s^2)^2 + p^2 (s(m - s) - q^2)^2 ].
 (C3) xi-integration in closed form over the finite range p in [b - rho, b + rho] with e^2 := q^2 + L s^2 fixed:
      int p^2 (p^2 + e^2)^{-5/2} dp and int (p^2 + e^2)^{-5/2} dp  (elementary antiderivatives).  Extension to p in R is one-sided
      but is not planned: for e >~ rho the tail |p| > 2 rho carries most of the extended integral (see section 4), so finite limits are kept.
 (C4) w >= m - s >= m - rho (J_2) and w >= m (J_1);  b^2 <= a^2;  a^2 = rho^2 + 2ms - s^2 exact.
 (C5) phi- and s-integration of the resulting algebraic majorants by monotone/convex bounds and exact rational enclosures of the
      few irrational constants (sqrt, ln) that appear, as in pieces 2-3.  THIS STEP IS THE OPEN PART.
 (C6) exact rational comparison of U_near,cert with the frozen budget text in force at submission time.

## 4. Structural reasons for the method choice (no diagnostic values)
 Write e^2 := q^2 + L s^2 so that D^2 = p^2 + e^2 and (43.1) reads N = lambda [ b e^2 + p (s(m-s) - q^2) ].
 (a) Pointwise chain |N| <= C D^2, then 2C^2/(wD).  The constant C is of order 1 while N/D^2 is of order 1 only where
     |p| ~ sqrt(L)|s| and q <~ sqrt(L)|s| (second term of (43.1)); off that cone N/D^2 = O(rho) or smaller.  The chain discards
     this, replacing N^2/D^4 by its supremum on the whole band, and its xi-mean int dxi/D is of logarithmic size for every
     (s, phi); the resulting bound has no decay in rho, whereas the first term of (43.1) alone contributes O(rho) by (b).  Rejected.
 (b) First term with e^4 <= D^4 before the xi-integral (i.e. 4 lambda^2 b^2/(wD)).  The exact xi-integral of e^4/D^5 over p is
     concentrated on |p| <~ e and is O(1/e) in size, whereas int dp/D over |p| <= 2 rho is of size log(rho/e) >> e * (1/e) when
     e << rho: the relaxation loses the factor (e/D)^4 exactly where the xi-integral lives.  Rejected.
 (c) Second term with p^2 <= D^2 before the xi-integral (i.e. 4 lambda^2 (s(m-s) - q^2)^2/(wD^3)).  The exact xi-integral of
     p^2/D^5 is 2/(3e^2) over R while that of 1/D^3 is 2/e^2: a factor 3 is lost pointwise in (s, phi), uniformly.  Rejected in
     favour of keeping p^2 inside the xi-integral, which costs nothing (both are elementary).
 (d) Extension of the p-range to R in (C3).  One-sided and exact-closed-form, but for e >~ rho the integrand (p^2+e^2)^{-5/2}
     has most of its mass at |p| > 2 rho, outside the true range [b - rho, b + rho] of length 2 rho.  Finite limits are kept.
 (e) Positive part [2N^2 - h^2 T]_+ : dropped in (S0).  h vanishes at the singular points together with N (h = lambda(k - xi b),
     k - xi b -> 0 there), so the subtraction does not change the order of the singularity; keeping it would require a sign
     analysis of 2N^2 - h^2 T that is not needed for integrability (Q0).  May be restored later if the budget requires.
 Hence the retained chain is (C1)-(C3): the exact two-term identity, 2(x+y)^2 <= 4x^2 + 4y^2, and finite-range closed-form
 xi-integration of each term with its own xi-structure.

## 5. Governance
 Audit path: Astra L43 structure audit -> chat ruling on chain -> this predeclare frozen (version-up) -> Code certificate -> CHAT AUDIT.
 Code will not submit a near-band certificate before this draft is frozen.
