# D-OB P2 / D-AN-1 — L1 obligation O1 (interior representation and algebraic identities) — PREDECLARE v1 (ChatGPT / Dig, 2026-10-09)

STATUS: PREDECLARE ONLY / SUBMITTED FOR CHAT AUDIT / NOT FROZEN.  Nothing in this document is derived, proved, computed or executed.  No SymPy run,
no script written.  O1 derivation / proof / computation / execution: NOT PERMITTED.  L1 PAUSED.  QM–L3–L1 connection UNDETERMINED.  ROUTE A/B/C and
Form I/II undecided.  D-P2 NOT_CERTIFIED.  Required order: CHAT AUDIT PASS -> Judge FREEZE ruling -> separate execution permission.  A CHAT AUDIT PASS
alone does not start O1.

Instruction: CHAT / Dig, "O1 内部表示・代数恒等式の事前宣言" (2026-10-09, resent).  Parent specification (FROZEN):
`tools/d_ob_p2/predeclare/L1_DELTA_REACH_LEMMA_SPEC_DRAFT.md`, commit ecd314467e51f89413220a2dcdd8c0d0d040cac3, git blob
1cdbc1c2a06db1a310baa58e818e16cffcaee4c4, SHA-256 88153b391f8b7b79c283610774b91333caf12e1a4f27caf891d99af0505f9a07 (S2 items C, E; S7 O1).

Restored relayed symbols (CHAT / Dig ruling; R1 and R2 only):
 §3C: retain z and r as free symbols in the L1 parameter representation; for the general interior algebraic check retain rho and z independently.
 §3D: boundary consistency is checked at r -> 1, never assumed in an interior derivation.
 §3E: boundary-only relations z = lambda m and rho^2 + m^2 = 1 apply only in section D.
 Revision scope: R1 (two-stage free-symbol collation) and R2 (independent interior derivative comparison); all other obligations retained from v0.

## 0. Sources (read-only; all in cotaxxxx/bg-oblate-spheroid unless stated)
 [P1]  analysis/D_OB_P1_DESIGN_NOTE.md, commit 69e104602e939817b6f4d71df3f6bd63cbc729e0, blob f81e120e44a866d206117d4fab5fac627f26ccd1,
       SHA-256 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9, 164 lines.  Status NOT_BINDING / EXTERNAL_AUDIT_PENDING (carried).
       Used: §1 (lines 7-18), §2 (line 22), Lemma 3.1 (line 26), Lemmas 3.2-3.4, Lemma V (line 83 ff.), Lemma 6.1 (line 107).
 [FTq] analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md, commit 20c5c59bd74f940fe0b1e05892bd2169e09d4fde, blob 1c449fb4fb791f750668c44605156454cfff42af,
       SHA-256 46443f0e981f360e57fb70d99754b0e480042d246e22d36732b00b96102a9cd1, 269 lines.  Used as TEMPLATE only: §3-§7, (3.1)-(7.3).
 [C43] (basepoint-geometry) tools/d_ob_p2/ftq_cert/CONTRACT43_H43_1_I_EVIDENCE_CLOSURE.md, commit c4d49d81884a9dfebb82839236c84cee8add1ceb,
       blob 060bd0ac1b1664b20721dd8f1f125e82eddd4997, SHA-256 c542456b4139085776c323d046d66c8db41aa086ef9ad7eebcc99640d4b149bb.  Used as TEMPLATE
       only: §3(C) steps (C1)-(C5).
 None of these is imported as a proof of an interior statement.  Every interior statement below is an obligation.

## 1. Targets (from the instruction §2; stated, not proved)
Base point p = (rho, 0, z) with rho > 0 on the L1 layer of spec S1: lambda in [2/5, 93/200], tau in [7/8, 1), r in [7/8, sqrt(1 - delta_L1)],
rho = r rho_b(tau), z = lambda r m(tau), 0 < delta_L1 <= 15/64 symbolic.  (rho = 0, tau = 1 is O4, not O1.)
 O1-1  2 pi lambda H(p) = int_{-1}^{1} G_p(mu) dmu,   G_p(mu) = int_0^pi K_H(p; mu, phi) dphi,
       K_H(p; mu, phi) = (calF_xi(rho) - calF_xi(-rho))/(2 rho),  calF(xi) := F(x(mu, phi), (xi, 0, z)).
 O1-2  interior counterparts of FTq (5.2), (7.1), (7.2), derived independently at general (rho, z).
 O1-3  h_+ D_- + h_- D_+ > 0 on the interior region (with h_+-, D_+- the values at the b-pair, FTq §7 notation).

## A. Starting point
A1  Origin: [P1] §1 only.  K = {x^2 + y^2 + z^2/lambda^2 <= 1}; x(mu, phi) = (a cos phi, a sin phi, lambda mu), a = sqrt(1 - mu^2), b = a cos phi;
    w^2 = lambda^2 (1 - mu^2) + mu^2;  D = |x - p|;  h = w (x - p).nu;  gamma = h/(w D);  F = h alpha^2 = h G(gamma);  dA/w = dmu dphi.
A2  Objects to be DERIVED for p = (rho, 0, z) (targets of the derivation, not inputs):
      h  — [P1] §1 states h = lambda (1 - rho b) - z mu for a meridional base point; to be re-derived from h = w (x - p).nu;
      D^2 = |x(mu, phi) - (rho, 0, z)|^2 as a polynomial in (mu, b, rho, z, lambda) with a^2 = 1 - mu^2;
      w^2 as in A1 (independent of p);
      h0 := h at b = 0, h_+- := h at +-b, D_+- := D at +-b (b -> -b is phi -> pi - phi, a surface point at the same mu).
A3  Prohibited as a starting point: FTq §2 (its h = lambda(1 - rho b - m mu), D^2 with lambda^2 (mu - m)^2, and (2.1) use z = lambda m, rho^2 + m^2 = 1).
A4  Interior membership to be shown (obligation I-1 below): r < 1 implies p and every p_xi = (xi, 0, z), |xi| <= rho, lie in int K.

## B. Derivation stages and dominating functions (templates [C43] (C1)-(C5), [FTq] §3-§7)
Notation: S_L1 = the L1 layer of §1;  P = [-1, 1] x [0, 2 pi] with dmu dphi (finite measure 4 pi).
I-1  Segment interiority.  For p in S_L1 and |xi| <= rho: xi^2 + z^2/lambda^2 <= rho^2 + z^2/lambda^2 = r^2 < 1.  To be proved from the definitions of
     rho, z in S1 (no boundary relation used).  Consequence sought: closed segment {p_xi} is a compact subset of int K; no endpoint is a boundary point.
I-2  Uniform distance.  To prove: there is d_* > 0 with D(x, p_xi) >= d_* for all x in bd K, |xi| <= rho.  Candidate (spec S4, D >= delta/5):
     d_* = lambda (1 - r) >= delta/5 >= delta_L1/5.  Status: UNPROVED OBLIGATION; its proof must not use rho^2 + m^2 = 1 at the base point.
I-3  Regularity of the integrand.  For x in bd K and p' in int K: h > 0, gamma in (0, 1] ([P1] Lemma 3.1); G, R real-analytic on (-1, sqrt 2)
     ([P1] Lemma 3.2); hence F(x, .) is C^2 in p' wherever D > 0, with the [P1] Lemma 3.3/3.4 derivative formulas.  To be stated for p' = p_xi.
I-4  (C1-interior)  E_rho(xi) = (1/(4 pi lambda)) int_P calF_xi dmu dphi,  E_rhorho(xi) = (1/(4 pi lambda)) int_P calF_xixi dmu dphi,  |xi| <= rho.
     Interchange: d/dxi with int_P.  Dominating functions on P x [-rho, rho]:  |calF_xi| <= pi^2/4 + 2 pi,  |calF_xixi| <= C2/D <= C2/d_*
     (C2 = 9 pi + 8, [P1] Lemma 3.4; with I-2).  Domain: closed segment of I-1.  Regularity needed: I-3.  Measure finite (4 pi).
     The [P1] Lemma V(b) / §2 statement is the template; the uniform majorant via I-2 must be shown here, not cited.
I-5  (C2-interior)  H(p) = E_rho(rho)/rho = [E_rho(rho) - E_rho(-rho)]/(2 rho)  ([P1] Lemma 6.1(i), (iii)).  At interior p both endpoints +-rho are
     interior (I-1): the values are ordinary derivatives; no continuous extension (Lemma V(c)) and no one-sided trace (H-43-1(ii)) is to be used.
I-6  (C3-interior)  E_rho(rho) - E_rho(-rho) = int_{-rho}^{rho} E_rhorho(xi) dxi.  Needs E_rhorho continuous on the closed segment (from I-4).
I-7  (C4-interior)  Insert I-4 and exchange int dxi with int_P (Fubini).  Dominating function: C2/d_* (constant) on [-rho, rho] x P.
     Then int_{-rho}^{rho} calF_xixi dxi = calF_xi(rho) - calF_xi(-rho) for EVERY (mu, phi) (D > 0 everywhere by I-2; not only a.e.), giving
     4 pi lambda H = int_P K_H dmu dphi.
I-8  (C5-interior)  The reflection y -> -y (phi -> 2 pi - phi) fixes p_xi and bd K; to show K_H(mu, 2 pi - phi) = K_H(mu, phi) and hence
     int_0^{2 pi} = 2 int_0^{pi}, i.e. O1-1.
I-9  (FTq §3 (3.1), §5 (5.1) interior)  Derive h_rho, D_rho, h_b, D_b (b-derivative at fixed mu), then gamma_rho, gamma_b, at general (rho, z).
     Only differentiation of explicit expressions at points with D > 0; no interchange with an integral.
I-10 (FTq (4.3), (5.2) interior)  With J := lambda (a^2 - b^2) gamma_b - h gamma_rho (definition (4.3) taken as a definition), derive
     N_J := w D^3 J as a polynomial in b with coefficients in (lambda, mu, rho, z): the interior counterpart of (5.2).
I-11 (FTq (7.1), (7.2) interior)  Derive gamma_+ - gamma_- at general (rho, z), via the rationalization
       h_+ D_- - h_- D_+ = (h_+^2 D_-^2 - h_-^2 D_+^2)/(h_+ D_- + h_- D_+),
     which is valid only where h_+ D_- + h_- D_+ != 0: I-11 therefore DEPENDS ON O1-3.  Then identify the numerator with 4 rho b [h0 c(mu) + lambda^2 rho^2 b^2]
     and c(mu) with both forms of (7.2).
I-12 (O1-3)  Planned route: for p in int K and both surface points x(mu, phi), x(mu, pi - phi): h_+- > 0 ([P1] Lemma 3.1) and D_+- >= d_* > 0 (I-2),
     hence h_+ D_- + h_- D_+ > 0; also w >= lambda > 0, so the full denominator w D_+ D_- (h_+ D_- + h_- D_+) of (7.1) is positive.  Only strict
     positivity is targeted; a quantitative lower bound is not part of O1.  Rests on [P1] Lemma 3.1 (NOT_BINDING, carried).
Not O1 targets (listed so that they are not claimed): the interior validity of FTq (4.2)/(4.4) (integration by parts and the R J representation),
the Lipschitz step (7.3), and any sign or lower bound for N_J or for int G_p dmu (O2, O3, O6).

## C. Checks (declared; none executed)
C-S  Symbolic collation (SymPy; exact rational arithmetic only; to be run only after FREEZE and a separate execution permission).
     R1 / Stage G (general interior coordinates): free symbols lambda, mu, rho, z, b.  No relation between rho and z is imposed;
     a^2 is replaced by 1 - mu^2; D is carried as a symbol D with D^2 replaced by its A2 polynomial.
     R1 / Stage L (L1 parameter coordinates): after Stage G, substitute rho = r rho_b(tau), z = lambda r m(tau), keeping z and r
     symbolic until the substitution and retaining r as a free symbol afterward; no r = 1 or boundary-only relation is imposed.
     Carry the identities through both stages.  Boundary reduction r -> 1 belongs only to section D.
     S-1  h from w (x - p).nu equals lambda (1 - rho b) - z mu ([P1] §1); D^2 = |x - p|^2 equals a^2 + rho^2 + (lambda mu - z)^2 - 2 rho b (spec S2 E).
          PASS iff both residuals expand to 0.
     S-2  R2: independently derive gamma_rho and gamma_b from the general-interior h and D^2 of A2 (rho,z independent).
          Use [FTq] (5.1) only as a derivation template, not as an established interior identity or by merely replacing m with z/lambda.
          S-2 compares the paper-derived gamma_rho and gamma_b from I-9 against independent SymPy derivatives of A2 h and D^2; PASS iff residuals are exactly 0
          after D^2 reduction, in both R1 stages G and L.
     S-3  N_J = w D^3 J (I-10) reduces to a polynomial in (b, lambda, mu, rho, z) with no odd power of D left, and N_J - (A2 b^2 + A1 b + A0) = 0
          with A2, A1, A0 transcribed verbatim from [FTq] lines of (5.2).                                        PASS iff both hold exactly.
     S-4  h_+^2 D_-^2 - h_-^2 D_+^2 - 4 rho b [h0 c(mu) + lambda^2 rho^2 b^2] = 0 (I-11 numerator).                 PASS iff residual is 0.
     S-5  the two forms of c(mu) in [FTq] (7.2) agree at general (rho, z).                                       PASS iff residual is 0.
     Any nonzero residual: STOP, report the residual verbatim, no repair in the same run.  No floating point, no numerical substitution, no sampling.
     The script, its file name and its expected stdout are fixed in a separate execution predeclare after FREEZE; it is not written now.
C-P  Paper analytic proof (cannot be replaced by C-S):  I-1 and I-2 (interiority, d_*);  I-3 (regularity);  I-4 and I-7 (each interchange with its
     dominating function, domain and regularity);  I-5, I-6 (endpoint handling, continuity);  I-8 (reflection);  I-11's division step;  I-12 (O1-3);
     the domain statement (rho > 0, tau < 1, r <= sqrt(1 - delta_L1)) and the exclusion of the axis.  A C-S PASS shows only polynomial identity.

## D. Boundary consistency at r -> 1 (check of the interior derivation, not a substitute for it)
Substitute rho = rho_b, z = lambda m and reduce modulo rho^2 + m^2 - 1 (m free):
 D-1  the A2 forms of h, D^2 reduce to [FTq] §2 h = lambda(1 - rho b - m mu) and D^2 = a^2 + rho^2 + lambda^2 (mu - m)^2 - 2 rho b.
 D-2  the interior N_J of I-10 reduces to -lambda^2 (m - mu) Q with Q of [FTq] (6.2)  (consistency with (6.1)).
 D-3  the interior (7.1), (7.2) reduce to [FTq] (7.1), (7.2) with z = lambda m.
 PASS iff each reduced residual is 0 (SymPy polynomial reduction, exact; executed only with C-S).  (6.1)/(6.2) enter ONLY here, as the target of
 the reduction; they are never used in I-1 ... I-12.  O1-3 has no boundary counterpart claim (at r = 1, h may vanish at the coincident point).

## E. Prohibitions
 E-1  No use of z = lambda m or rho^2 + m^2 = 1 (nor contract 44's rho^2 = 1 - m^2, nor FTq (6.1)) in the interior derivation.
 E-2  No numerical evaluation, search or sampling.
 E-3  No use of the unverified counterexamples E1, E2 (REPORTED / EVIDENCE NOT FOUND).
 E-4  No use of the G2 material (ORIGINAL NOT FOUND); FTq (5.2), (7.1) are not identified with it (spec S2 item E).
 E-5  No O1 proof and no SymPy check before CHAT AUDIT PASS, Judge FREEZE, and a separate execution permission.
 E-6  No boundary statement (22'' v1.2, R-G, Contracts 43/45, FTq (4.4) at p_b, S''_lb) is imported as an interior statement.

## F. Ledger (unchanged by this draft)
 spec v1 FROZEN (ecd3144) | O1 predeclare: this draft, NOT FROZEN | O1 proof: NOT PERMITTED | L1 PAUSED | QM–L3–L1 UNDETERMINED |
 ROUTE A/B/C undecided | Form I/II undecided | daybreak-works: user task pending | D-P2 NOT_CERTIFIED
