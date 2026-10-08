# Contract 43 — North near band — PREDECLARE DRAFT v2

STATUS: DRAFT v2 / SUBMITTED FOR CHAT AUDIT (design audit) / NOT FROZEN / NOT AUTHORIZED FOR CERTIFICATE EXECUTION.
Contract 43 OPEN (countersign in progress).  D-P2 NOT_CERTIFIED.  No diagnostic value appears in this document.
Supersedes v1.1 (a6479efe).  Changelog in section 8.  Assumption stated in section 3: chat has not yet ruled on the base chain,
so v2 carries TWO routes with an explicit precedence; chat may strike either at audit.

## 0. Fixed evidence and inputs
| item | commit | SHA-256 | status |
|---|---|---|---|
| decomposition of N, pointwise |N| <= C D^2: `ftq_cert/n43_decomposition_cert.py` | a3bed35b | 04e73583... | CHAT AUDIT PASS (identity class) |
| xi-antiderivatives F1, F2: `ftq_cert/n43_xi_antiderivative_cert.py` | db8ef8da | a0aad6ae... | CHAT AUDIT PASS (identity class) |
| contracts 44 (N1-N3) / 46: `ftq_cert/n3_identities_cert.py` | 79588e2e | a5ba8a33... | PASS (46 not used here) |
| far band U_1+U_2+U_3 < 5481/10000: pieces 1-3 (99c9b62, 7ba339a8, 9cb723c0) | — | ad564945..., 8910105d..., 308e626e... | CHAT AUDIT PASS |
| S''_lb = 635530452759/817216000000: `ftq_cert/kernel_extension_cert.py` | 1ac4446 | 3c0b4d45... | CHAT AUDIT PASS |
| Astra report `D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md` | (Astra audit branch, pin table pending) | — | received; countersign in progress |
| Code collation of the Astra report: `ftq_cert/astra_l43_collation_check.py`, `CONTRACT43_ASTRA_COLLATION_NOTE.md` | 53bdb0bc / ec3282fa | c5f40600... / 07e1c86f... | Code collation, not a countersign |
Not received by Code: Astra's `l43_graph_majorant_exact.py` (SHA-256 6187c2b0... as stated by Astra), its output, `source_manifest.json`.

## 1. Region, variables, normalization (frozen sources)
s := m - mu (mu the surface coordinate, m = 2 tau/(1 + tau^2)).  Formal band (contract 24, kappa = 1): |mu - m| <= rho, i.e. s in [-rho, rho].
Physical region = formal band intersected with mu <= 1:  mu in [m - rho, 1],  s in [m - 1, rho]  (m - 1 = -rho^2/(1+m) > -rho; cap side s < 0
included).  |xi| <= rho, phi in [0, pi].  Box: L = lambda^2 in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2 <= (15/113)^2.
Diagonal singular points (D = 0): (s, phi, xi) = (0, 0, rho), (0, pi, -rho) only; they lie on the surface (base-segment endpoints).
(S0) contract 44: [-K_H]_+ <= pi * mean_xi M,  M := [2N^2 - h^2 T]_+/(w D^5) = (w/D)[Phi]_+,  pointwise wherever D > 0.
U_near := int_{m-rho}^{1} [-G(mu)]_+ dmu <= U_43^{N3} := pi int_{m-rho}^{1} int_0^pi mean_xi M dphi dmu   (P units; same outer pi and
measure dmu dphi as contract 45, so U_near,cert + U_far,cert is unit-consistent).
NOT inherited: (S1) D >= D_0 and contract 46 (need a >= rho; false on the cap and degenerate at s -> 0).

## 2. Pieces
ROUTE A (section 3): ONE integration piece, the whole physical region; the only boundaries are the band and its geometric projection.
ROUTE B (appendix B): J_1 = [m - 1, 0], J_2 = [0, rho] (structural boundary s = 0 = sign(a - rho)).  No phi split, no xi split in either route.
Piece cap (8 total): far 3 + near 1 (route A) or 2 (route B).

## 3. Route A (primary, conditional on the chat countersign of the Astra report) — chain to be certified by Code INDEPENDENTLY
Assumption: the primary route follows the Astra chain (5.5) -> (5.7) -> (6.5) -> §7 because (i) it is a complete paper proof with exact
constants, (ii) Code's collation reproduced every identity, integral, Bernstein table, constant and rational total, (iii) it needs no
rational-majorant machinery.  Code will write its OWN certificate (no import of Astra's script).  If chat does not countersign, route B applies.
 (A1) identity (5.5):  N = lambda [ xi D^2 + (t/2)( D^2 - (1-L) s^2 - delta ) ],  t := b - xi,  delta := rho^2 - xi^2 = mu_xi^2 - m^2 >= 0,
      mu_xi := sqrt(1 - xi^2), l := mu_xi - m >= 0, 2 m l <= delta <= 2 l.                                   [exact; collation PASS]
 (A2) 2h/lambda = D^2 + (1-L)s^2 + delta >= D^2, hence 0 <= gamma <= 1; |N| <= w D^2 (Gram / Cauchy-Schwarz).  [exact; collation PASS]
 (A3) plane projection u = (b, y), y = a sin phi >= 0, |u| <= R_* = sqrt(2 m rho); d mu d phi = db dy / mu, mu >= mu_0 = 97/113;
      r := |u - (xi, 0)|, D^2 = r^2 + L s^2 >= r^2.  Lipschitz of g(u) = sqrt(1 - |u|^2) on the convex disk: |grad g| <= R_*/(m - rho) < k = 3/5
      [Bernstein: (9/25)(1-z)^2 - 2z > 0 on z = rho/m in [0, 15/112]], so |s + l| <= k r.
 (A4) Young: s^2 <= (9/20) r^2 + 5 l^2;  (1-L) s^2 <= (189/500) r^2 + delta/50  [Bernstein: 1/50 - (21/20) z^2 > 0];
      D^2 >= (3/4)(r^2 + L l^2)  [Bernstein: 1/12 - (9/25) L > 0].                                             [SOS identities; collation PASS]
 (A5) zeta := 1 - ((1-L)s^2 + delta)/D^2 in [-c_g delta/D^2, 1], c_g = 51/50;  N^2/D^4 <= L[ xi^2 + |xi t| + t^2/4 + c_g delta |xi t|/D^2 + c_g^2 delta^2 t^2/(4 D^4) ];
      M <= 2N^2/(w D^5) (positive part and -h^2 T dropped, one-sided)  =>  pointwise majorant (5.7).
 (A6) one-piece closed-form integration in plane polar coordinates (t, y) = r(cos theta, sin theta), theta in [0, pi], region extended to
      r <= R_e = R_* + rho (one-sided): curvature three terms -> A(rho, R_e) = pi rho^2 R_e/3 + rho R_e^2/2 + pi R_e^3/24;
      cross term -> c_g (4/3)^{3/2} rho^3 log(1 + 10 R_e/rho^2);  depth term -> pi c_g^2 (4/3)^{5/2} rho^2/(9 lambda);
      prefactor 2 pi lambda^p/(mu w) <= 2 pi lambda_bar^p/(mu_0 W(lambda_bar)), W(lambda)^2 = mu_0^2 + lambda^2 (1 - mu_0^2), lambda_bar = 93/200, p = 2 (p = 1 for the depth term).
 (A7) rational constants: rho <= 15/113, R_e < 13/20, (4/3)^{3/2} < 77/50, (4/3)^{5/2} < 103/50, pi < 22/7, W(lambda_bar) > 89/100,
      rho^3 log(1 + 10 H_0/rho^2) <= 6 (15/113)^3 via 1 + 10 H_0/r_0^2 = 166447/450 < sum_{j<=10} 6^j/j! < e^6;  monotonicity in rho of each term.
 (A8) exact rational result (as stated by Astra and reproduced by Code's collation):  U_43^{N3} <= 3887073979116207/17284813033600000 < 9/40.
 Code certificate plan (execution after PASS of this predeclare): one script re-deriving (A1)-(A8) with sympy/Fractions, containing
 (a) the ring identities, (b) the three Bernstein tables, (c) the SOS identities of (A4), (d) the antiderivative/limit facts of (A6) by
 differentiation, (e) the rational constant checks of (A7), (f) the final rational evaluation and the comparison of (C6).  The collation
 script already performs (a)-(e) and the arithmetic of (f) as a RE-COMPUTATION OF ASTRA'S FIGURES; it is not the certificate and was run for
 collation only (disclosed in CONTRACT43_ASTRA_COLLATION_NOTE.md).

## 4. Analytic obligations
 H-43-1(i)  interchange of differentiation and the surface integral in the FT_q density derivation.  OPEN.
 H-43-1(ii) one-sided limits at the band boundary vs Lemma V boundary values; improper-integral representation.  OPEN; Astra's independent
            lemma announced by chat; Code does not pre-empt it.  Astra §3 (K_H = (1/2 rho) int F_xixi dxi a.e., Fubini, null set) overlaps:
            chat to rule whether it discharges (i)/(ii).
 L43-I (route A/B, paper): nonnegativity => Tonelli; pairing not needed in route A (full phi-range); null set {D = 0} = two points.
 L43-E (route B only): kernel-unit endpoint boundedness (appendix A).   L43-E' (route B only): majorant endpoint boundedness.

## 5. Budget clause (C6)
U_near,cert is compared by exact rational arithmetic with the budget text in force at submission.  The number is FIXED AFTER the repository
commit and pin of 22'' v1.2 (Judge adopted; commit/SHA pending).  For information only (not a budget statement): under the v1.2 design value
S''_lb, the residual after the far band is S''_lb - 5481/10000 = 187614363159/817216000000, and 9/40 is below it by 3740763159/817216000000.
Under the frozen v1.1 text (104/625) the far band alone exceeds the budget; this contract does not change that fact.

## 6. Governance
 Order: this v2 design audit (chat, 7 confirmed items + pre-review A-D) -> Astra countersign of its own report (chat) -> FREEZE of v2 (or v3) ->
 Code certificate execution -> CHAT AUDIT.  Code executes no integral-evaluation certificate before FREEZE.  Astra independence: Astra -> Code
 direction opened by the research team (report sent to Code); Code -> Astra direction remains closed until chat says otherwise.
 Method (B) is not used.  Diagnostics remain NOT_EVIDENCE and are not cited.

## 7. Compliance table (chat ruling items and pre-review A-D)
| item | where |
|---|---|
| 1 identity certs as fixed evidence | §0 |
| 2 (C5) route (i) with difference structure | appendix B (route B), unchanged from v1.1 |
| 3 route (ii) appendix-only | appendix B.2 |
| 4 H-43-1 split, L43-I/L43-E separate | §4 |
| 5 no O(rho) motivation | removed |
| 6 singular points, non-inheritance | §1, §2 |
| 7 (C6) fixed after v1.2 pin | §5 |
| 8 submission after Astra report | this v2 |
| A H-43-1 original meaning restored | §4 |
| B half-line rational majorant, strict excess at infinity | appendix B (C5.2) |
| C DeltaG_k = e^{2k} DeltaF_k; L43-E' | appendix B, §4 |
| D rationalization as separate step | appendix B (C5.3') |

## 8. Changelog
 v0 (7cebf22c) -> v1 (bd890d91) -> v1.1 (a6479efe) -> v2: route A (Astra chain, Code-independent certificate plan) added as primary with
 explicit assumption; former main chain moved to appendix B as route B; §0 inputs table; §5 budget clause with v1.2 pending.

## Appendix A (paper derivation, UNAUDITED; route B): from db8ef8da, F_1 = e^{-4} G_1(u), F_2 = e^{-2} G_2(u), G_1 = u(2u^2+3)/(3(1+u^2)^{3/2}),
 G_2 = u^3/(3(1+u^2)^{3/2}), both increasing and odd, G_1(+inf) = 2/3, G_2(+inf) = 1/3; hence DeltaG_1 <= 4/3, DeltaG_2 <= 2/3.

## Appendix B (route B = v1.1 chain, kept verbatim in substance; see a6479efe for the full text)
 (C1) N = lambda[b e^2 + p A], p = b - xi, e^2 = q^2 + L s^2, A = s(m-s) - q^2.  (C2) 2N^2 <= 4 lambda^2 [b^2 e^4 + p^2 A^2].
 (C3) finite-range xi-integration with F_1, F_2 (db8ef8da); inseparable units b^2 e^4 DeltaF_1 (<= (4/3) b^2) and A^2 DeltaF_2 (<= (2/3) A^2/e^2).
 (C4) w >= m - s, b^2 <= a^2, e^2 >= L s^2, e^2 >= q^2.
 (C5.1) scaling p = e u; (C5.2) half-line rational H_k with H_k(0) = 0, H_k' >= g_k on [0, inf), H_k(+inf) > G_k(+inf) strictly, certified by
 Bernstein via u = v/(1-v) (L43-H, drafting only); (C5.3') rationalization of e, a as a separate step ((alpha) even powers / (beta) certified
 rational bounds); (C5.4) (phi, s)-integration (L43-Q).  B.2: route (ii) only with an exact square-root elimination identity.
 Structural reasons (a)-(f) as in v1.1 §4.
