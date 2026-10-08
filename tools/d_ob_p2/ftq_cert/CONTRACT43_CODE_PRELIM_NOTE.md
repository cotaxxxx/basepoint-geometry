# Contract 43 (north near band) — Code preliminary structure note

Status: CODE NOTE / INPUT TO THE CONTRACT 43 PREDECLARE.  NOT TO BE SHARED WITH ASTRA before Astra's independent report is received
(chat instruction 2026-10-09); chat will collate the two independent results afterwards.  Not a certificate of any integral bound.
Exact statements are certified by `n43_decomposition_cert.py` (this directory); numerical values are DIAGNOSTIC_ONLY / NOT_EVIDENCE
(`../diagnostics/near_band_majorant_forms.py`).  D-P2 overall: NOT_CERTIFIED.

## 0. Corrections to the Astra request text (to be fixed before dispatch)

1. **Region.**  The request writes the near band as `s in [rho, max(rho, 1/10)], |xi| <= rho`.  That interval is Piece 1 of the
   FAR band (contract 45, I_1).  Per contract 21'' v1.1 the near band is `|mu - m| <= rho` including the cap, i.e.
   `mu in [m - rho, 1]`, equivalently  **s = m - mu in [m - 1, rho]**, with |xi| <= rho and phi in [0, pi].
   Note m - 1 = -rho^2/(1 + m) < 0: the cap part s < 0 has a < rho, so contract 46 (a - rho >= (51/100) sqrt s) and the
   far-band D_0 chain do NOT apply there.
2. **Pin.**  `commit 2b53e137, blob 63bfc769...` is the pre-audit version of the N3 certificate (its SHA-256 is
   63bfc769c3db49d8d728d099e5efefec3e509fd4796f7926133c4ec7628508c2; git blob 3c22bfca...).  The audited active version is
   `n3_identities_cert.py` at commit 79588e2e9373c06aa80589a5ab7ffe1611be99d7, git blob 6a40bede832c462917f16ae024437c6c93f93b98,
   SHA-256 a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c.  The identities are the same; the audit
   clarifications (E1/E2/E5) are only in 79588e2.
3. **Far band pins.**  Piece 1: 99c9b62 (SHA ad564945...); Piece 2: 7ba339a8 (SHA 8910105d...); Piece 3: 9cb723c0
   (SHA 308e626e...), audit package a11def1e.

## 0'. Q0 (added after chat correction E-43-1): is the N3 xi-averaged form applicable on the near band?

Yes, in the following precise sense.  Contract 44 (N1, N2) are pointwise inequalities valid wherever D > 0, i.e. everywhere except
the two diagonal singular points (s = 0, phi in {0, pi}, xi = +-rho), a null set.  Integrability: by (43.2), 2N^2/(w D^5) <= 2C^2/(w D)
with C <= (3/2) lambda + 1/2 and w >= m - rho > 0, and  int dxi dphi ds / D < infinity  on the near band because, in the local coordinates
(p, q, r) = (b - xi, a sin phi, sqrt(L) s), D is the Euclidean norm and the Jacobian is bounded away from 0 and infinity near the singular
points (a -> rho > 0).  Hence [2N^2 - h^2 T]_+/(w D^5) and 2N^2/(w D^5) are absolutely integrable over (xi, phi, s), the xi-mean exists
for every (s, phi) outside a null set, and the one-sided inequalities pass to the integrals.  The D^5 denominator is therefore not an
obstruction; the obstruction is quantitative (section 2).  The region is s in [-rho, rho] intersected with mu <= 1, i.e. s in [m - 1, rho].

## 1. Singular point and exact decomposition

D^2 = (b - xi)^2 + a^2 sin^2 phi + L s^2 vanishes only at s = 0, sin phi = 0, b = xi, i.e. a = rho, phi in {0, pi}, xi = +-rho:
the two endpoints of the base segment, which lie on the surface.  With p := b - xi, q := a sin phi (local symbols, not the
FT_q p, q), D^2 = p^2 + q^2 + L s^2 and  **(43.1)  N = lambda [ b (q^2 + L s^2) + p ( s(m - s) - q^2 ) ]**  (certified).

Consequences (certified, paper steps in the docstring of `n43_decomposition_cert.py`):
- **Q1 (pointwise): PROVED, rho-uniform.**  |N| <= C D^2 with C = lambda|b| + |m - s|/2 + lambda|q|/2 <= (3/2) lambda a + |m - s|/2,
  for every point with D > 0 and every parameter, on the whole mu-range.  So N = O(D^2) holds EVERYWHERE in the pointwise sense;
  there is no anisotropic failure of boundedness.  Along phi = 0, N = lambda s[(a - xi)(m - s) + a L s] and N/D^2 = lambda a at xi = a.
- The anisotropy is in the SIZE, not the boundedness: N/D^2 is of order 1 only on the thin cone |p| ~ sqrt(L)|s|, |q| <~ sqrt(L)|s|
  (second term of (43.1)); elsewhere it is O(rho) or smaller.  Any chain that uses the pointwise constant C loses this.

## 2. Diagnostic sizes of candidate chains (NOT_EVIDENCE; near band, worst case L = 8649/40000, tau = 7/8, rho = 0.1327)

All quantities are  int_s int_phi mean_xi [ pi * (.) ]  over the near band, pairing not applied.

| form | definition | value | vs residual 0.2296 |
|---|---|---|---|
| N3 | pi [2N^2 - h^2 T]_+ /(w D^5), T = q^2 + L s^2 (contract 44) | 0.029 | target-level reference |
| SQ | pi 2N^2/(w D^5) (positive part dropped) | 0.045 | fits |
| M2 | pi 4 lambda^2 [ b^2 (q^2+Ls^2)^2 + p^2 (s(m-s) - q^2)^2 ]/(w D^5)  (2(x+y)^2 <= 4x^2 + 4y^2) | 0.095 | fits (2.4x slack) |
| A2 + B2x | A2 := M2 first term with (q^2+Ls^2)^2 <= D^4, i.e. pi 4 lambda^2 b^2/(w D) | 0.232 + 0.059 | FAILS |
| A2 + B2 | B2 := second term with p^2 <= D^2, i.e. pi 4 lambda^2 (s(m-s)-q^2)^2/(w D^3) | 0.404 | FAILS |
| M1 | pi 2 C^2/(w D), pointwise constant C of (43.2) | 4.29 | hopeless |

rho-scaling (diagnostic): N3 0.029 / 0.0051 / 0.00033 at rho = 0.133 / 0.051 / 0.010, i.e. roughly rho^{1.7..1.8}; M2 scales the same way.
Answer to Q5 (diagnostic only): the near-band contribution is o(rho), between O(rho^2) and O(rho^{3/2}); neither O(sqrt rho) nor O(rho).

## 3. What this implies for the proof structure (Code's reading; Astra to confirm or refute)

- The positive part [2N^2 - h^2 T]_+ is worth only a factor ~1.5 (N3 vs SQ).  A chain may drop it.
- The ESSENTIAL structure is the two-term form (43.1) with the xi-dependence kept inside each term: the first term carries
  (q^2 + L s^2)^2/D^5 and the second p^2/D^5.  Both xi-integrals are elementary (antiderivatives of (p^2+e^2)^{-5/2} and
  p^2 (p^2+e^2)^{-5/2}, e^2 := q^2 + L s^2), over the FINITE range p in [b - rho, b + rho].  Extending to p in R is one-sided but
  diagnostically too lossy for the first term when e >~ rho (it gives ~0.4).
- Relaxing either factor to a power of D before the xi-integral (A2 or B2) already breaks the budget.  Hence "N = O(D^2)" in the
  pointwise sense is true but useless; the usable statement is the exact two-term identity plus finite-range xi-integration.
- The cap part s in [m - 1, 0] needs its own treatment (a < rho); diagnostically its contribution is small (s-range of length
  rho^2/(1+m)), but no certified bound exists yet.

## 4. Proposed statement of L43 for Astra (replacing the vague candidate)

L43 (candidate, Code formulation).  For every parameter in the box and every s in [m - 1, rho], phi in [0, pi]:
   mean_{|xi|<=rho}  pi * 2N^2/(w D^5)  <=  G_1(s, phi) + G_2(s, phi),
with G_1, G_2 explicit (closed-form in e^2 = a^2 sin^2 phi + L s^2 and b) such that  int_{m-1}^{rho} int_0^pi (G_1 + G_2) dphi ds
is certifiable by exact arithmetic and is < 187614363159/817216000000 for all parameters.
Open: the (phi, s) integration of the finite-range xi-antiderivatives (algebraic functions with square roots) in certified form.
