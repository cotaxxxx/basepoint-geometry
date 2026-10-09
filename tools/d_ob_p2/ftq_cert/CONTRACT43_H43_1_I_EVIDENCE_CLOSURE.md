# Contract 43 — H-43-1(i) evidence closure document (Code, 2026-10-09)

Status: SUBMITTED FOR CHAT AUDIT.  H-43-1(i) source collation: PASS (chat); this document is the evidence closure requested by chat.
Contract 43: FROZEN (machine checks CLOSED by the authorized run bd512f53).  c_FT UNSET.  D-P2 NOT_CERTIFIED.  Nothing here changes those states.

## 1. Obligation (as fixed in predeclare v3.4.1 §4, commit 97d85f5914e23f593fc2a41baeb883645f5ce994)
H-43-1(i): interchange of differentiation (in the base-point coordinate xi, at fixed lambda, m, mu, phi) and the surface integral in the
FT_q density derivation, i.e. for j = 1, 2 and the fixed band B (or the whole surface),
    d^j/dxi^j  integral_B calF(x, p_xi) dsigma(x)  =  integral_B  partial_xi^j calF(x, p_xi) dsigma(x),       p_xi = (xi, 0, lambda m).
The obligation is split by the position of the base point (mandatory distinction):
  (I)  INTERIOR base points |xi| < rho:  p_xi in int K, because xi^2 + (lambda m)^2/lambda^2 = xi^2 + m^2 < rho^2 + m^2 = 1.
  (B)  BOUNDARY base points xi = +-rho:  p_(+-rho) in bd K (rho^2 + m^2 = 1); these are the two points where the integrand is singular at
       x = p_(+-rho).  No differentiation under the integral is claimed AT these points; the boundary values enter only as one-sided limits,
       which is the content of H-43-1(ii) (CLOSED by chat ruling on Astra's lemma H-43-1(ii)-E), together with Lemma V(c).

## 2. Source and collation scope (five lines)
Source: `cotaxxxx/bg-oblate-spheroid`, `analysis/D_OB_P1_DESIGN_NOTE.md`, commit 69e104602e939817b6f4d71df3f6bd63cbc729e0,
git blob f81e120e44a866d206117d4fab5fac627f26ccd1, SHA-256 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9, 164 lines,
recorded status in the source: CHAT_ANALYTIC_DERIVATION_PASS / EXTERNAL_AUDIT_PENDING / NOT_BINDING (not upgraded here).
The five source lines in scope (verbatim, by line number in that blob; read back by Code in the read-only canonical clone):
| line | text |
|---|---|
| 86 | `E_beta(p) := (1/(4 pi lambda)) integral_{bd K \ {p}} partial_p^beta F(x, p) dA(x)/w(x).` |
| 89 | `Then: (a) the integral converges absolutely for every `p` in `closure(K)`; (b) `E` is `C^2` on `int K` with `partial^beta E = E_beta` there; (c) each `E_beta` is continuous on `closure(K)`.` |
| 91 | `*Proof.* (a) By Lemma 3.4 the integrand is bounded for `\|beta\| <= 1` and bounded by `(5/2) C2/D` for `\|beta\| = 2`, integrable by Lemma 4.2.` |
| 93 | `(b) Let `p` in `int K`, `r = dist(p, bd K)/2 > 0`. For `p'` in `B(p, r)`, `D(x, p') >= r` on `bd K`, so all integrands with `\|beta\| <= 2` are bounded on `bd K x B(p, r)`. Differentiation under the integral on a finite measure space, applied twice, gives `E` in `C^2(B(p, r))` with `partial^beta E = E_beta`.` |
| 95 | `(c) Let `p_n -> p0` in `closure(K)` and fix `x != p0`. For large `n`, `D(x, p_n) >= D(x, p0)/2 > 0`; `h`, `D` and their `p`-derivatives are continuous at `p0`; `gamma(x, p_n)` in `[0, 1]` converges to `gamma(x, p0)` in `[0, 1]`; and `G`, `R`, `R_gamma` are continuous on `[0, 1]`. Hence `partial_p^beta F(x, p_n) -> partial_p^beta F(x, p0)` for almost every `x`. The integrands are uniformly bounded for `\|beta\| <= 1` and uniformly integrable for `\|beta\| = 2` (Corollary 4.3). Vitali's theorem on `(bd K, dA)` gives `E_beta(p_n) -> E_beta(p0)`. ∎` |
Supporting lemmas cited by those lines (same blob): Lemma 3.4 (line 47, density bound with C2 := 9 pi + 8), Lemma 4.2 (line 71, area growth),
Corollary 4.3 (line 79, uniform integrability of C2/(wD)).  Their internal proofs are part of the P1 note's own audit state and are not re-proved here.

## 3. Evidence closure
### (I) Interior base points — CLOSED by source line 93 (Lemma V(b)) and independently by Astra Proof A
- Line 93: for p in int K and r = dist(p, bd K)/2 > 0, D(x, p') >= r on bd K for p' in B(p, r); all integrands with |beta| <= 2 are bounded on
  bd K x B(p, r); differentiation under the integral on a finite measure space, applied twice, gives E in C^2(B(p, r)) with partial^beta E = E_beta.
  Applied with p = p_xi, |xi| < rho, and the xi-direction e_x: this is exactly the interchange for j = 1, 2 on the WHOLE surface; restriction to
  the fixed band B (a fixed measurable subset, independent of xi) is the same statement with the same bound.
- Independent re-derivation: Astra `H43_ENDPOINT_LEMMA.md` Proof A, (3.E2) (evidence commit ff1e1a5351e2c8ed4bd816e168a08f5b17310e88,
  blob 303d1d7c6aa1640590eb83434888c8c19ab44c3a, SHA-256 b1a906edeb21cef356d3d7810dbdc11d30773364620b174a425c441b826d6276): on compact
  interior xi-intervals D has a positive lower bound on the surface, so the fixed-B integral is twice xi-differentiable under the integral sign,
  with m, rho and the band boundary NOT moved together with xi.
- Code check of the interior condition: xi^2 + m^2 < 1 for |xi| < rho is the ring relation rho^2 = 1 - m^2 (contract 44, n3_identities_cert.py
  79588e2; used again in the Code run bd512f53, checks (A1), (A7)).
### (B) Boundary base points — NOT an interchange claim; handled by limits
- Line 95 (Lemma V(c)): E_beta is continuous on closure(K) (a.e. convergence of the integrands plus uniform integrability, Vitali).  Hence the
  boundary values E_beta(p_(+-rho)) are the limits of the interior values; no derivative is taken at the boundary point.
- The one-sided traces of calF_xi at xi -> +-rho, their L^1(B) convergence, the agreement of the integrated traces with the Lemma V boundary
  integrals, and the improper-integral representation are H-43-1(ii): CLOSED by chat ruling on Astra's lemma ((3.E1), (3.E3)-(3.E6)).
- Consequence used by Contract 43: K_H = (calF_xi(rho-) - calF_xi(-rho+))/(2 rho) = (1/(2 rho)) integral_{-rho}^{rho} calF_xixi dxi a.e. in (mu, phi),
  and the (xi, mu, phi) integrals may be reordered (nonnegative majorant, Tonelli).  This is where (I) and (B) are consumed by the N3 chain (S0).
### What is NOT closed by this document
- The P1 note's own status (NOT_BINDING, EXTERNAL_AUDIT_PENDING) is unchanged; this document relies on its Lemma V(b)/(c) text as pinned above
  and on Astra's independent re-derivation.  If chat requires the P1 note itself to be audited before (i) is CLOSED, that is a separate gate.
- c_FT, the Boundary Pair Lemma and D-P2 certification are untouched.

## 4. Pins of all evidence cited
| item | repository / path | commit | blob | SHA-256 |
|---|---|---|---|---|
| P1 design note (Lemma V) | bg-oblate-spheroid / analysis/D_OB_P1_DESIGN_NOTE.md | 69e104602e939817b6f4d71df3f6bd63cbc729e0 | f81e120e44a866d206117d4fab5fac627f26ccd1 | 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9 |
| Astra H-43-1(ii)-E lemma | basepoint-geometry / tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/H43_ENDPOINT_LEMMA.md | ff1e1a5351e2c8ed4bd816e168a08f5b17310e88 | 303d1d7c6aa1640590eb83434888c8c19ab44c3a | b1a906edeb21cef356d3d7810dbdc11d30773364620b174a425c441b826d6276 |
| Astra report §3 | same dir / D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md | ff1e1a5351e2c8ed4bd816e168a08f5b17310e88 | 3f95ef5b82980affcc1e453393308acd099544ad | 9fc500bd486d325451ae049806673bdef400987c06f07cc16a4c174130e1b615 |
| contract 44 identities | basepoint-geometry / tools/d_ob_p2/ftq_cert/n3_identities_cert.py | 79588e2e9373c06aa80589a5ab7ffe1611be99d7 | 6a40bede832c462917f16ae024437c6c93f93b98 | a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c |
| frozen predeclare v3.4.1 | basepoint-geometry / tools/d_ob_p2/predeclare/CONTRACT43_NEAR_BAND_PREDECLARE_DRAFT.md | 97d85f5914e23f593fc2a41baeb883645f5ce994 | 5f121c5eeff241e6a2a50ae6114a17a158ffac67 | aaaf04137219ec9bfcd4f71fe88463efabd88a76411cffe0cd5a7fb121d66efc |
| frozen certificate / run evidence | basepoint-geometry / tools/d_ob_p2/ftq_cert/north_near_l43_cert.py ; l43_code_execution/ | 7f71fb433dfabf2e99dc52d9fa775b0ae50dee30 ; bd512f535ef2d32531c0e48e5229a8ddca0d3fa1 | 3a4ce931b8fbd50ff4db7dda88ae86cea3427dc4 ; SHA256SUMS blob d21e5c8f5725c389c5e01225540ec902f81d33e7 | 4c2d6eb97c5f74bdca2cd75c22e53fdbac420235b9d69633ee27290e7fdf7fa4 ; SHA256SUMS 5fd6ce05ccd8885650fab43142d4d45c4df3ffa05da1aab398080fd475c2fa65 |
