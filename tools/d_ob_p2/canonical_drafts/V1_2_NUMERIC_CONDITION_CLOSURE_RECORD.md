# 22'' v1.2 numeric condition — closure record v1 (Code draft for CHAT AUDIT, 2026-10-09)

Status: DRAFT CLOSURE RECORD v1 / SUBMITTED FOR CHAT AUDIT (v0 06580669: CONDITIONAL PASS; v1 adds §5 R-G).  This record does not modify the canonical contract text
(`cotaxxxx/bg-oblate-spheroid`, `design/d-ob-p2`, `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_2.md`,
commit d445b302bd879b5dc5211c7ba310d5aef036f31e, blob 6340cb3e1dcb7387e4044013fb9f77a9cd21788a,
SHA-256 3ef26f903d15c11449e583a917723ffcbaff7217b76f3fc65284e02b820b4640).  If the Judge wants it in canonical, the user places this file
byte-identically as a separate new file (proposed path `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_22_DOUBLE_PRIME_V1_2_CLOSURE_RECORD.md`).

## 1. Condition (22'' v1.2, canonical text)
U_north + U_near < S''_lb,  S''_lb = 635530452759/817216000000,  on the box lambda in [2/5, 93/200], m in [112/113, 1], rho^2 = 1 - m^2 (P units,
2 pi lambda H = integral_{-1}^{1} G(mu) dmu).

## 2. Evidence (all CHAT AUDIT PASS)
| term | bound | evidence | state |
|---|---|---|---|
| S''_lb (south, [-1, 1/2]) | integral_{-1}^{1/2} G >= 635530452759/817216000000 | derivation source: south paper proof 05668a47216e243450211f0cf438702dc6d1527c (SHA-256 f320acb9...); input certificate kernel_extension_cert.py 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e (SHA-256 3c4b0d45...) | CHAT AUDIT PASS; canonical import PENDING |
| U_north (far, s in [rho, 1/2]) | < 5481/10000 (exact sum of three certified fractions) | contract 45 pieces 99c9b62a..., 7ba339a8..., 9cb723c0... | CHAT AUDIT PASS |
| U_near (band, mu in [m - rho, 1]) | <= 3887073979116207/17284813033600000 | contract 43: frozen predeclare 97d85f5914e23f593fc2a41baeb883645f5ce994, frozen certificate 7f71fb433dfabf2e99dc52d9fa775b0ae50dee30, authorized run bd512f535ef2d32531c0e48e5229a8ddca0d3fa1 (38 PASS / exit 0); Astra independent report and exact script (ff1e1a53..., script SHA-256 6187c2b0...); H-43-1(i) closure c4d49d81884a9dfebb82839236c84cee8add1ceb, H-43-1(ii) CLOSED | Contract 43 CERTIFIED (chat ruling 2026-10-09) |
| coverage / overlap | [-1,1/2] U [m-1/2, m-rho] U [m-rho, 1] = [-1,1]; overlap width 1 - m <= 1/113 is safe-side slack | v1.2 §22'' text; collation report A (77c3c77f, items A1-A6) | CHAT AUDIT PASS |

## 3. Exact closure
S''_lb - 5481/10000 - 3887073979116207/17284813033600000 = 1622585478106563/345696260672000000 =: Delta > 0  (computed by the frozen certificate,
check (C6), and printed in stdout.txt of run bd512f53, SHA-256 b377ee8f...).  Hence U_north + U_near < S''_lb and, for every parameter in the box
with rho > 0,  2 pi lambda H >= S''_lb - U_north - U_near > Delta.

## 4. R-G — the South density G_P and the North density G_K coincide for a.e. mu (rho > 0)
### 4.1 Sources (pins; all read back by Code)
| source | repository / path | commit | blob | SHA-256 | places used |
|---|---|---|---|---|---|
| FT_q reduction draft | bg-oblate-spheroid / analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md | 20c5c59bd74f940fe0b1e05892bd2169e09d4fde | 1c449fb4fb791f750668c44605156454cfff42af | 46443f0e981f360e57fb70d99754b0e480042d246e22d36732b00b96102a9cd1 | §2 lines 40-46 (h, D, w at p = (rho, 0, lambda m)); §3 (3.1)-(3.2) lines 68, 74; §4 (4.2) line 92, (4.3) line 96, (4.4) lines 98-100; §5 N_J := w D^3 J line 116; §6 (6.1) line 146, (6.2) lines 150-158 |
| P-decomposition draft | bg-oblate-spheroid / analysis/D_OB_P2_D_AN1_FT_Q_P_DECOMPOSITION_DRAFT.md | 641e2a2d4b0720e47c73f257cbf8de1b89eac9c5 | f0d7c01a45fe71b40785021abccd810eceb4ccfd | 67d821d4612015648758de57887fce699db1143952b658e6733cba1ebd61b518 | (1.1), (2.1)-(2.2), (3.2) Delta3 = 4 rho b L_D |
| South paper proof (definition of G_P) | basepoint-geometry / tools/d_ob_p2/ftq_paper_proof/D_OB_P2_D_AN1_FT_Q_SOUTH_POSITIVE_MASS_DRAFT.md | 05668a47216e243450211f0cf438702dc6d1527c | a66ac60edfc75e70ae198bdea7807e6d5c14b360 | f320acb964cb278d1dd8ef6240fcc88bc9bdf77ae75edd4c77f86ce78da93d3c | §1 lines 31-36 (F, A, K_R, I = -lambda^2 s F W, W = 1/(w v^3), G = int_0^pi I dphi) |
| contract 21'' (I, G) | bg-oblate-spheroid / analysis/..._CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_2.md | d445b302bd879b5dc5211c7ba310d5aef036f31e | 6340cb3e1dcb7387e4044013fb9f77a9cd21788a | 3ef26f903d15c11449e583a917723ffcbaff7217b76f3fc65284e02b820b4640 | §21'' (verbatim from v1.1): I = -lambda^2 (m - mu) F W, G = int_0^pi I dphi |
| Astra H-43-1(ii)-E lemma | basepoint-geometry / tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/H43_ENDPOINT_LEMMA.md | ff1e1a5351e2c8ed4bd816e168a08f5b17310e88 | 303d1d7c6aa1640590eb83434888c8c19ab44c3a | b1a906edeb21cef356d3d7810dbdc11d30773364620b174a425c441b826d6276 | claim 1 (one-sided traces equal the ordinary boundary formula off the diagonal), (3.E1), (3.E3) |
| H-43-1(i) closure | basepoint-geometry / tools/d_ob_p2/ftq_cert/CONTRACT43_H43_1_I_EVIDENCE_CLOSURE.md | c4d49d81884a9dfebb82839236c84cee8add1ceb | 060bd0ac1b1664b20721dd8f1f125e82eddd4997 | c542456b4139085776c323d046d66c8db41aa086ef9ad7eebcc99640d4b149bb | §3(C) (C4)-(C5): K_H, G_K, 2 pi lambda H = int G_K |
Audit state of the FT_q draft: "REDUCTION AUDIT PASS" (as recorded in the P-decomposition header).  The P-decomposition file's own header reads
"AWAITING CHAT AUDIT"; the identities used here ((2.2), (3.2)) are taken as audited in the south paper proof (input I1, CHAT AUDIT PASS).  Chat to confirm.

### 4.2 The two densities
 South (contract 21'', south paper proof §1):  G_P(mu) := int_0^pi I dphi,  I = -lambda^2 s F W,  W = 1/(w v^3),  v = D_+ D_-,  F = Rbar A + b (DeltaR/rho) K_R.
 North (contracts 43/45, closure c4d49d81 (C4)-(C5)):  G_K(mu) := int_0^pi K_H dphi,  K_H = (calF_xi(rho-) - calF_xi(-rho+))/(2 rho).
 Both are used with the same outer normalization 2 pi lambda H = int_{-1}^{1} G dmu (P units).

### 4.3 Claim R-G
For rho > 0, every parameter in the box, and every mu in [-1, 1] with mu != m (hence for a.e. mu):  G_P(mu) = G_K(mu) = (1/rho) int_0^{2 pi} R J dphi.

### 4.4 Proof
 (G1) Reflection (xi, phi) -> (-xi, pi - phi).  It maps b -> -b and keeps y = a sin phi, mu, w; the surface point and the base point are both mirrored by
      x -> -x, which preserves K, h and D.  Hence calF(mu, pi - phi; -xi) = calF(mu, phi; xi), and differentiating in xi:
      calF_xi(mu, pi - phi; -xi) = -calF_xi(mu, phi; xi).  For mu != m the surface point is never the base point p_(+-rho), D > 0 near xi = +-rho, so the
      one-sided traces are the ordinary derivatives at the boundary base point (H-43-1(ii)-E, claim 1) and the identity passes to the traces:
      int_0^pi calF_xi(mu, phi; -rho+) dphi = -int_0^pi calF_xi(mu, phi; rho-) dphi.  Therefore
      G_K(mu) = (1/rho) int_0^pi calF_xi(mu, phi; rho) dphi = (1/(2 rho)) int_0^{2 pi} calF_xi(mu, phi; rho) dphi,
      the last step by the reflection y -> -y (phi -> 2 pi - phi), which fixes b and the base point.
 (G2) At xi = rho the base point is the FT_q boundary base point p = (rho, 0, lambda m) and calF_xi = F_rho of FT_q (3.1) (FT_q §2-§3; same density
      h (arccos gamma)^2 and same derivative direction e_x, contract 44 conventions).  For mu != m the integrand is smooth in phi on the full circle, and
      FT_q (4.2) (azimuthal integration by parts at fixed mu) gives  int_0^{2 pi} F_rho dphi = 2 int_0^{2 pi} R J dphi.  Hence G_K(mu) = (1/rho) int_0^{2 pi} R J dphi.
 (G3) Pairing for the South form.  int_0^{2 pi} R J dphi = 2 int_0^pi R J dphi (phi -> 2 pi - phi), and phi -> pi - phi maps b -> -b on [0, pi], so
      int_0^{2 pi} R J dphi = int_0^pi [R_+ J_+ + R_- J_-] dphi,  J_+- = J(+-b).
      With N_J := w D^3 J (FT_q line 116) and the boundary factorization N_J = -lambda^2 (m - mu) Q (FT_q (6.1)),
      R_+ J_+ + R_- J_- = (-lambda^2 s/w) [R_+ Q(b) D_-^3 + R_- Q(-b) D_+^3]/(D_+^3 D_-^3) = -lambda^2 s W [R_+ Q(b) D_-^3 + R_- Q(-b) D_+^3].
 (G4) Identification with F.  The coefficients of Q in FT_q (6.2) are exactly  Q = m rho b^2 + B_1 b + rho C_0  (B_1, C_0 as in the south paper proof §1;
      coefficient-by-coefficient polynomial identity).  Hence Q_e := m rho b^2 + rho C_0 = rho E (E = m q + C_0, q = b^2) and Q_o := B_1 b.  The exact
      four-term identity (P-decomposition (2.2)) with N_e = rho E, N_o = B_1 b, S3 = D_+^3 + D_-^3 and Delta3 = 4 rho b L_D ((3.2)) gives
      [R_+ Q(b) D_-^3 + R_- Q(-b) D_+^3]/rho = Rbar (E S3 + 4 B_1 q L_D) + b (DeltaR/rho)(4 rho^2 E L_D + B_1 S3) = Rbar A + b (DeltaR/rho) K_R = F.
      Therefore (1/rho) int_0^{2 pi} R J dphi = int_0^pi (-lambda^2 s F W) dphi = int_0^pi I dphi = G_P(mu).
 (G5) Combining (G2) and (G4): G_K(mu) = G_P(mu) for every mu != m, rho > 0.  The exceptional latitude mu = m is a single point, of measure zero.
 Code-internal consistency check (not evidence; not committed): the polynomial identity of (G4) for Q and the four-term identity of (G4) modulo
 D_-^2 = D_+^2 + 4 rho b were re-verified symbolically by Code; both hold.  The audited sources above are the evidence.

### 4.5 Why the South and North sub-interval estimates may be combined
 - Integrability: for fixed rho > 0, |calF_xi| <= C_tr = pi^2/4 + pi (H-43-1(ii)-E (3.E3)), so |G_K(mu)| <= pi C_tr/rho on [-1, 1]; G_K is in L^1([-1, 1]),
   and so is G_P (equal a.e.).
 - Since G_P = G_K a.e., they are the same element of L^1([-1, 1]); call it G.  The South bound (stated for G_P on [-1, 1/2]) and the North bounds (stated
   for [-G_K]_+ on [m - 1/2, m - rho] and [m - rho, 1]) are statements about this one function G, and the one-sided inequality of 22'' v1.2,
   integral_{-1}^{1} G >= integral_{-1}^{1/2} G - integral_{1/2}^{1} [-G]_+ >= S''_lb - U_north - U_near, uses only additivity of the integral of G over
   [-1, 1/2] U [1/2, 1] and the overlap slack (§2 above, A1-A6).
 - The total normalization is consistent: integral G_P = (1/rho) int int R J = 2 pi lambda H by FT_q (4.4), and integral G_K = 2 pi lambda H by closure (C5).
 - rho = 0 (m = 1) is not covered by R-G; that endpoint is handled separately (NP-T (9.1) and continuity of H, P1 Lemma 6.1(iii)).

## 5. Status after this record
22'' v1.2 numeric condition: CLOSED on CHAT AUDIT of this record including R-G (§4).  c_FT: UNSET (separate predeclare).  Boundary Pair Lemma: OPEN.
D-P2: NOT_CERTIFIED.
