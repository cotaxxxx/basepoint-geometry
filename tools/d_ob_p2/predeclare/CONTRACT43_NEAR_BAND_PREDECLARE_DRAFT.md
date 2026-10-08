# Contract 43 — North near band — PREDECLARE DRAFT v3.1 (FREEZE candidate)

STATUS: DRAFT v3 / SUBMITTED FOR CHAT DESIGN AUDIT / NOT FROZEN / NOT AUTHORIZED FOR CERTIFICATE EXECUTION.
Contract 43 OPEN (countersign in progress).  D-P2 NOT_CERTIFIED.  No diagnostic value appears in this document.
Supersedes v2 (3665f33e, CONDITIONAL PASS).  v3 (459abecf) design audit: CHAT AUDIT PASS (FREEZE condition 1 of 4); v3.1 = pin update only.  Basis: chat instruction "Predeclare v3 作成・独立証明書準備 (CHAT AUDIT 裁定統合版)".
The formal proof route of Contract 43 is the Astra L43 single-piece chain (5.5) -> (5.7) -> (6.5) -> §7.  The former route (C1)-(C5)
is SHELVED: preserved at commit a6479efe3d173a5952087f9bd3df67da02856fb5, not an alternative route of this contract, not used here.
Any change of the main chain is re-submitted to CHAT AUDIT before implementation.

## 0. Evidence and inputs (pins; PENDING = not received by Code, never guessed)

### 0.1 Code certificates (repository `cotaxxxx/basepoint-geometry`, branch `claude/d-ob-p2-resumable-i8dgpn`)
| item | commit | git blob | SHA-256 | status |
|---|---|---|---|---|
| decomposition of N, pointwise \|N\| <= C D^2: `ftq_cert/n43_decomposition_cert.py` | a3bed35b7b9912081afd7f8819fb2306840ab49e | bde5a8453d1a7beea4dcb0a6fe66385ff32fae90 | 04e7358375c81328a8cd4c628cead339477233f831e21bd8a623ac5395090c6d | CHAT AUDIT PASS (identity class) |
| xi-antiderivatives: `ftq_cert/n43_xi_antiderivative_cert.py` | db8ef8da590329d207aa8d8b18d7198bf1b7e251 | 136ff5ac21d0b27dc0ca3fcffa904472b9a84cfd | a0aad6ae55e257fb0bd2aeb73e97d62f0177401f305fc3f748dbcd687696801a | CHAT AUDIT PASS (identity class; not used by the formal route) |
| contracts 44 (N1-N3) / 46: `ftq_cert/n3_identities_cert.py` | 79588e2e9373c06aa80589a5ab7ffe1611be99d7 | 6a40bede832c462917f16ae024437c6c93f93b98 | a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c | PASS (contract 46 not used here) |
| far piece 1: `ftq_cert/north_far_piece1_cert.py` | 99c9b62aae9a6baa14e95b1892cab8c9da28d17a | 7944d8b825e1d2a4eeed8a4a79f4927497f69893 | ad564945f7a11f6d61e892116382e365d45334ab1d29981b5c65d13c7e2d9256 | CHAT AUDIT PASS |
| far piece 2: `ftq_cert/north_far_piece2_cert.py` | 7ba339a8c54278dd0165020f394fdb583ca7e0da | 85b00c4e599ee71016d9a1fe5ff8d227b822a0fa | 8910105df4e9acddb9d273710fe60503edac2cd0ee280840cf0eb1a13552f678 | CHAT AUDIT PASS |
| far piece 3: `ftq_cert/north_far_piece3_cert.py` | 9cb723c0b424297f3ce572109daf312fbe42b675 | 3beb1e7b0597f9072211a25cf7fb09fc4a323d4a | 308e626e0f864222c6e1176ac4d3a69333186c59aaa100a1d7965c727581fada | CHAT AUDIT PASS |
| far total: U_1 + U_2 + U_3 < 5481/10000 (exact sum of the three certified fractions) | — | — | — | derived from the three rows above |
| Code collation of the Astra report: `ftq_cert/astra_l43_collation_check.py` | 53bdb0bcd25027db88ea0b2e063d27a0bbe7b418 | 31d1ff80b1475063264e42b32fc26fe960457868 | c5f4060012fd59da8315860b4d1f32638ff0d55df55454213f86a65950c863ff | chat: collation run, disclosed, separate class; NOT the certificate |
| collation note: `ftq_cert/CONTRACT43_ASTRA_COLLATION_NOTE.md` | ec3282fa3850b2ab51c46321603ce80f47743d62 | fe5897035fcd9d5831ccab563b2d82011bab744c | 07e1c86f258fb6929e90c1a03a9da3ebff8b3025a1dabe8a34d29cde9c7a436e | Code note |

### 0.2 S''_lb: derivation source and input certificate (two distinct evidence rows; not the same evidence)
| row | item | commit | git blob | SHA-256 | evidence class | audit state |
|---|---|---|---|---|---|---|
| 1 | South positive mass paper proof: `ftq_paper_proof/D_OB_P2_D_AN1_FT_Q_SOUTH_POSITIVE_MASS_DRAFT.md` | 05668a47216e243450211f0cf438702dc6d1527c | a66ac60edfc75e70ae198bdea7807e6d5c14b360 | f320acb964cb278d1dd8ef6240fcc88bc9bdf77ae75edd4c77f86ce78da93d3c | DERIVATION SOURCE of S''_lb | CHAT AUDIT done (south paper-proof audit PASS); canonical import NOT done |
| 2 | Kernel extension certificate: `ftq_cert/kernel_extension_cert.py` | 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e | 3600e0771c73456698035484eb267415111acc4d | 3c4b0d452d87072c2c7a27d432048691c4cce47da871bfad0a50630436146e85 | one INPUT certificate to the derivation of S''_lb | CHAT AUDIT PASS |
S''_lb = 635530452759/817216000000.  Dependency: 22'' v1.2 budget text (row 0.4) -> cites S''_lb -> derived in row 1 -> uses row 2 (and the
certificate-39' south lemma inputs listed in row 1's pin table).  Row 1 and row 2 are never cited as one piece of evidence.

### 0.3 Astra deliverables (five items)
| # | item | commit | git blob | SHA-256 | confirmation state |
|---|---|---|---|---|---|
| 1 | `l43_graph_majorant_exact.py` | PENDING | PENDING | 6187c2b0c22d3e1b75ede72da3f470185eb6d93722b25265974ce2e01488cf18 (as stated in the Astra report; not verified by Code) | PENDING (file not received; chat audit of the script pending) |
| 2 | exact output of item 1 (46 checks, exit 0 as stated) | PENDING | PENDING | PENDING | PENDING |
| 3 | `source_manifest.json` | PENDING | PENDING | PENDING | PENDING |
| 4 | independent audit report `D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md` | PENDING | PENDING | PENDING | received by Code as text (2026-10-09); pin PENDING |
| 5 | correction notice `E43_CORRECTION_NOTICE_2026_10_09.md` | PENDING | PENDING | PENDING | received by Code as text; sending state "未送付"; Astra self-applied E-43-1 in item 4 |

### 0.4 Budget evidence
| # | item | commit | git blob | SHA-256 | state |
|---|---|---|---|---|---|
| 6 | 22'' v1.2 budget document (Judge adopted) | PENDING | PENDING | PENDING | PENDING (not committed/pinned; (C6) number stays PENDING) |
| — | 22'' v1.1 (frozen text in force): `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_1.md` in `cotaxxxx/bg-oblate-spheroid` (verified by Code in the read-only canonical clone) | b1a10ea6f0ef127aaf4a40a93070cf270d03e073 | 49e658b0487123249eb81d70bde1ef188ff640d7 | db975daba9d712246ed5e27465437f34450b356f453729a5fb78ec8ceab468cb | FROZEN; official budget 104/625 |

## 1. Region, variables, normalization (frozen sources)
s := m - mu (mu the surface coordinate, m = 2 tau/(1 + tau^2)).  Formal band (contract 24, kappa = 1): |mu - m| <= rho, i.e. s in [-rho, rho].
Physical region = formal band intersected with mu <= 1:  mu in [m - rho, 1],  s in [m - 1, rho]  (m - 1 = -rho^2/(1+m) > -rho; cap side s < 0
included).  |xi| <= rho, phi in [0, pi].  Box: L = lambda^2 in [4/25, 8649/40000] (lambda in [2/5, 93/200]), m in [112/113, 1], rho^2 = 1 - m^2
<= (15/113)^2.  Diagonal singular points (D = 0): (s, phi, xi) = (0, 0, rho) and (0, pi, -rho) only; both on the surface (base-segment endpoints).
(S0) contract 44: [-K_H]_+ <= pi * mean_xi M,  M := [2N^2 - h^2 T]_+/(w D^5) = (w/D)[Phi]_+,  pointwise wherever D > 0, with
mean_xi := (1/(2 rho)) int_{-rho}^{rho} (.) dxi.
U_near := int_{m-rho}^{1} [-G(mu)]_+ dmu <= U_43^{N3} := pi int_{m-rho}^{1} int_0^pi mean_xi M dphi dmu.
Normalization (P units): the same outer factor pi, the same xi-mean 1/(2 rho), the same measure dmu dphi and the same P units as the far band
of contract 45, so U_near,cert + U_far,cert is unit-consistent; see CONTRACT43_ASTRA_COLLATION_NOTE.md §2 (normalization paragraph).
Area change used below: dmu dphi = db dy / mu with u = (b, y) = a (cos phi, sin phi); it is kept throughout (never dropped).
NOT inherited: (S1) D >= D_0 and contract 46 (need a >= rho; false on the cap and degenerate at s -> 0).

## 2. Integration structure
ONE integration piece: the whole physical region of §1.  The only boundaries are the band |mu - m| <= rho, the surface mu <= 1 and the
geometric projection of §3 (A3); no phi split, no xi split, no interior boundary.  Piece count: far 3 + near 1 = 4 of the cap 8.
No boundary, constant or threshold is chosen from a diagnostic.

## 3. Formal chain (Astra (5.5) -> (5.7) -> (6.5) -> §7), to be certified by Code INDEPENDENTLY (`ftq_cert/north_near_l43_cert.py`)
 (A1) identity:  N = lambda [ xi D^2 + (t/2)( D^2 - (1-L) s^2 - delta ) ],  t := b - xi,  delta := rho^2 - xi^2 = mu_xi^2 - m^2 >= 0,
      mu_xi := sqrt(1 - xi^2) in [m, 1],  l := mu_xi - m >= 0,  delta = (mu_xi + m) l,  2 m l <= delta <= 2 l.
 (A2) 2h/lambda = D^2 + (1-L) s^2 + delta >= D^2  =>  0 <= gamma = h/(wD) <= 1;  with n = (lambda b, lambda y, mu)/w, e = (b - xi, y, -lambda s)/D
      (unit vectors), nu = n.e_x, kappa = e.e_x:  N/(w D^2) = nu - gamma kappa = (n - gamma e).(e_x - kappa e),  hence |N| <= w D^2 (Cauchy-Schwarz);
      Gram identity (1 - gamma^2)(1 - kappa^2) - (nu - gamma kappa)^2 = (mu + L s)^2 y^2/(w^2 D^2).
 (A3) projection: u = (b, y), y = a sin phi >= 0, |u| = a <= R_* := sqrt(2 m rho) (a^2 = 1 - mu^2 <= 1 - (m - rho)^2 = 2 m rho);
      Jacobian dmu dphi = db dy / mu (mu dmu = -a da, db dy = a da dphi), mu >= mu_0 := 97/113 on the band;  r := |u - (xi, 0)|,
      D^2 = r^2 + L s^2 >= r^2.  g(u) := sqrt(1 - |u|^2) on the convex disk |u| <= R_*:  |grad g| = |u|/g <= R_*/(m - rho) < k := 3/5,
      because with z := rho/m in [0, 15/112]:  k^2 (1 - z)^2 - 2 z > 0  [Bernstein, degree 2, coefficients 9/25, 249/1400, 681/313600];
      both u and (xi, 0) lie in the disk (|xi| <= rho <= R_*), so |mu_xi - mu| = |s + l| <= k r.
 (A4) Young:  s^2 <= (5/4)(s + l)^2 + 5 l^2 <= (9/20) r^2 + 5 l^2  [SOS: (5/4)(s+l)^2 + 5 l^2 - s^2 = (s/2 + 5 l/2)^2];
      (1 - L) s^2 <= (21/25)[(9/20) r^2 + 5 l^2] = (189/500) r^2 + (21/5) l^2 <= (189/500) r^2 + delta/50,  using (21/5) l^2/delta <= (21/5) l/(2m)
      <= (21/20) z^2 < 1/50  [Bernstein: 1/50 - (21/20) z^2 on z in [0, 15/112], coefficients 1/50, 1/50, 209/179200];
      l^2 <= 4 (s + l)^2 + (4/3) s^2  [SOS: 4(s+l)^2 + (4/3)s^2 - l^2 = (4s + 3l)^2/3],  so  r^2 + L l^2 <= (1 + 4 L k^2) r^2 + (4/3) L s^2 <= (4/3) D^2
      [Bernstein: 1/12 - (9/25) L on L in [4/25, 8649/40000], coefficients 193/7500, 16477/3000000],  i.e.  D^2 >= (3/4)(r^2 + L l^2).
 (A5) zeta := 1 - ((1-L) s^2 + delta)/D^2 in [-c_g delta/D^2, 1],  c_g := 51/50 (from (A4): (1-L)s^2 <= D^2 + delta/50);  N/D^2 = lambda (xi + t zeta/2);
      N^2/D^4 <= L [ xi^2 + |xi t| + t^2/4 + c_g delta |xi t|/D^2 + c_g^2 delta^2 t^2/(4 D^4) ]  (|zeta| <= 1 + v, zeta^2 <= 1 + v^2, v = c_g delta/D^2);
      M <= 2 N^2/(w D^5)  (positive part and -h^2 T dropped, one-sided)  =>  pointwise majorant
      M <= (2L/w) [ (xi^2 + |xi t| + t^2/4)/D + c_g delta |xi t|/D^3 + c_g^2 delta^2 t^2/(4 D^5) ].
 (A6) one-piece integration.  Plane polar coordinates (t, y) = r (cos theta, sin theta), theta in [0, pi]; the projected half-disk is contained in
      {r <= R_e := R_* + rho, y >= 0} (one-sided extension for a nonnegative majorant).  With D >= r for the first three terms and
      D^2 >= (3/4)(r^2 + d_l^2), d_l := lambda l, for the last two:
        curvature terms:  int int (xi^2 + |xi t| + t^2/4)/r  r dr dtheta <= pi xi^2 R_e + |xi| R_e^2 + pi R_e^3/24;  xi-mean (<xi^2> = rho^2/3, <|xi|> = rho/2):
                          A(rho, R_e) := pi rho^2 R_e/3 + rho R_e^2/2 + pi R_e^3/24;
        cross term:       (4/3)^{3/2} c_g delta |xi| * 2 * int_0^{R_e} r^2 (r^2 + d_l^2)^{-3/2} dr,  int = arsinh(R_e/d_l) - R_e/sqrt(R_e^2 + d_l^2) <= log(1 + 2 R_e/d_l),
                          d_l >= delta/5 (l >= delta/2, lambda >= 2/5),  x log(1 + c/x) increasing  =>  <= (4/3)^{3/2} c_g |xi| rho^2 log(1 + 10 R_e/rho^2);
                          xi-mean:  c_g (4/3)^{3/2} rho^3 log(1 + 10 R_e/rho^2);
        depth term:       (4/3)^{5/2} (c_g^2 delta^2/4) (pi/2) int_0^inf r^3 (r^2 + d_l^2)^{-5/2} dr = (4/3)^{5/2} c_g^2 pi delta^2/(12 d_l) <= (4/3)^{5/2} c_g^2 pi delta/(6 lambda)
                          (delta^2/d_l <= 2 delta/lambda);  xi-mean (<delta> = 2 rho^2/3):  pi c_g^2 (4/3)^{5/2} rho^2/(9 lambda);
        prefactor:        pi (outer) * (2L/w) * (1/mu)  with  lambda^p/(mu w) <= lambda_bar^p/(mu_0 W(lambda_bar)),  W(lambda)^2 := mu_0^2 + lambda^2 (1 - mu_0^2),
                          lambda_bar := 93/200, p = 2 (curvature, cross) and p = 1 (depth, after lambda^2/lambda), since w >= W(lambda) for mu >= mu_0 and
                          lambda^p/W(lambda) is increasing in lambda.
      Result (6.5):  U_43^{N3} <= [2 pi lambda_bar^2/(mu_0 W(lambda_bar))] { A(rho, R_e) + c_g (4/3)^{3/2} rho^3 log(1 + 10 R_e/rho^2) } + [2 pi lambda_bar/(mu_0 W(lambda_bar))] pi c_g^2 (4/3)^{5/2} rho^2/9.
 (A7) rational constants and monotonicity.  Define r_0 := 15/113 (rho <= r_0) and H_0 := 13/20 (R_e <= sqrt(2 rho) + rho <= sqrt(2 r_0) + r_0 < H_0, checked as
      2 r_0 < (H_0 - r_0)^2).  Each term is increasing in rho and in R_e, so it is evaluated at (r_0, H_0).  (4/3)^{3/2} < 77/50, (4/3)^{5/2} < 103/50,
      pi < 22/7 (applied to every pi), W(lambda_bar) > 89/100 (W(lambda_bar)^2 - (89/100)^2 = 211911/127690000 > 0).
      Logarithm:  rho^3 log(1 + 10 H_0/rho^2) is increasing in rho (3 log(1+x) >= 2x/(1+x), x = 10 H_0/rho^2), and at rho = r_0:
      1 + 10 H_0/r_0^2 = 166447/450 < sum_{j<=10} 6^j/j! = 67591/175 < e^6,  so  rho^3 log(1 + 10 H_0/rho^2) <= 6 r_0^3.
 (A8) exact rational result (Astra; reproduced by Code's collation 53bdb0bc):
      curvature 20682286967199/152962947200000 + cross 4323211299/110234777000 + depth 3014712459/59751151250 = 3887073979116207/17284813033600000 < 9/40,
      9/40 - sum = 2008953443793/17284813033600000 > 0.   The Code certificate re-derives this value independently and compares exactly.

## 4. Analytic obligations
 H-43-1(i)  interchange of differentiation and the surface integral in the FT_q density derivation: the mathematical argument of Astra §3 is
            confirmed by chat; the formal pin of the source statement and the final evidence closure are separate and remain to be recorded.
 H-43-1(ii) OPEN.  Awaiting Astra's independent lemma, which must establish (a) existence of the one-sided limits at the band boundary,
            (b) agreement with the Lemma V boundary values, (c) justification of the improper-integral representation.  Astra §3's a.e. FTC
            statement alone does not close (ii).  Lemma V source pin: PENDING until the Astra lemma names it.
 L43-I (paper): nonnegativity => Tonelli for the order xi, then (phi, mu); {D = 0} is two points (surface-measure zero).

## 5. Budget clause (C6)
U_near,cert is compared by exact rational arithmetic with the budget text in force at submission.  OFFICIAL NUMBER: PENDING until the
22'' v1.2 commit and SHA-256 are pinned (row 0.4 #6).  For information only, not a budget statement: under the v1.2 design value S''_lb (row 0.2),
S''_lb - 5481/10000 = 187614363159/817216000000 and 9/40 is below it by 3740763159/817216000000.  Under the frozen v1.1 text (104/625) the far band
alone exceeds the budget; this contract does not change that fact and does not replace the frozen text.

## 6. Governance
 FREEZE requires all four: (1) v3 design audit CHAT AUDIT PASS; (2) Astra five deliverables pinned and the exact script CHAT AUDITED;
 (3) H-43-1(ii) independent lemma confirmed; (4) 22'' v1.2 commit/SHA-256 pinned.  FREEZE only by explicit chat ruling.
 Code certificate `ftq_cert/north_near_l43_cert.py`: source committed (static review by chat done; S-1/S-2/R-S1 applied); syntax check by ast.parse
 permitted and done; EXECUTION and use of its output as evidence only after FREEZE.  Its final line distinguishes machine-checked items, paper
 steps and external obligations, and reads "C6 PENDING; NOT CERTIFIED" while 22'' v1.2 is unpinned.
 Independence: Code and Astra may share decompositions, notes and mathematical reports (both directions opened by chat); certificate CODE is
 never copied in either direction; the Code implementation and the Astra implementation remain separate evidence.
 Method (B) not used.  Diagnostics NOT_EVIDENCE, not cited.

## 7. Compliance table
| item | where |
|---|---|
| 1 identity certs as fixed evidence | §0.1 |
| 2 (C5) route (i) | see a6479efe; outside this contract |
| 3 route (ii) | see a6479efe; outside this contract |
| 4 H-43-1 split, L43-I separate | §4 |
| 5 no O(rho) motivation | none present |
| 6 singular points, non-inheritance | §1 |
| 7 (C6) fixed after v1.2 pin | §5 |
| 8 submission after Astra report | v2, v3 |
| A H-43-1 original meaning | §4 |
| B, C, D (former route) | see a6479efe; outside this contract |
| R-1 former route removed | this document |
| R-2 external evidence pins with PENDING | §0.3, §0.4 |
| R-3 audit states of former versions | §8 |
| R-4 S''_lb source vs input separated | §0.2 |

## 8. Changelog and audit states of former versions
 v0  7cebf22c  chat pre-review (no formal CHAT AUDIT PASS).
 v1  bd890d9164f5d075e5f2743ceceb79d2e71199eb  formal CHAT AUDIT PASS NOT obtained (pre-review only).
 v1.1 a6479efe3d173a5952087f9bd3df67da02856fb5  formal CHAT AUDIT PASS NOT obtained (pre-review corrections A-D applied).  The former route
      (C1)-(C5), appendices A and B are preserved at this commit and are NOT used in this contract.
 v2  3665f33e82ee1cfa5a1ea1166d8cf1d8bcb3958a  CONDITIONAL PASS; superseded by v3.
 v3  459abecf3249ace4789e4a94708218fa0128363e  design audit CHAT AUDIT PASS (FREEZE condition 1/4).
 v3.1 this document: §0.4 v1.1 row completed with full commit/blob/SHA-256 verified in the canonical clone; §6 certificate status updated.
 v3  content: R-1 former route removed (history kept); R-2 pin tables with PENDING; R-3 this list; R-4 S''_lb rows separated;
     (A7) defines (r_0, H_0) and the logarithm/monotonicity bookkeeping; §1 cites the collation note for the normalization.
