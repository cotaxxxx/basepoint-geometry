# Contract 43 — North near band — PREDECLARE DRAFT v0

STATUS: DRAFT / NOT FROZEN / NOT AUTHORIZED FOR CERTIFICATE SUBMISSION.  Conditional on (i) the Astra structure audit of L43 and
(ii) the budget decision (22'' v1.2 adopted by the Judge, repository commit pending; v1.1 remains the frozen text).
Nothing here selects a constant or threshold from diagnostics; the piece boundaries below are structural (sign of s).

## 1. Region and chain inherited (frozen sources)
Near band (contract 21'' v1.1): mu in [m - rho, 1]  <=>  s := m - mu in [m - 1, rho];  |xi| <= rho;  phi in [0, pi].
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
      but NOT planned for the first term (diagnostically fatal); finite limits are kept.
 (C4) w >= m - s >= m - rho (J_2) and w >= m (J_1);  b^2 <= a^2;  a^2 = rho^2 + 2ms - s^2 exact.
 (C5) phi- and s-integration of the resulting algebraic majorants by monotone/convex bounds and exact rational enclosures of the
      few irrational constants (sqrt, ln) that appear, as in pieces 2-3.  THIS STEP IS THE OPEN PART.
 (C6) exact rational comparison of U_near,cert with the frozen budget text in force at submission time.

## 4. What is already known to fail (do not resubmit)
 - pointwise |N| <= C D^2 followed by 2C^2/(wD): diagnostic ~4.3 (NOT_EVIDENCE) — structurally cannot work.
 - relaxing (q^2 + Ls^2)^2 <= D^4 or p^2 <= D^2 before the xi-integral: diagnostic 0.23-0.40 vs residual 0.2296.

## 5. Governance
 Audit path: Astra L43 structure audit -> chat ruling on chain -> this predeclare frozen (version-up) -> Code certificate -> CHAT AUDIT.
 Code will not submit a near-band certificate before this draft is frozen.
