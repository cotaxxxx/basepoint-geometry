# Contract 43 — paper-step correspondence table (Code, 2026-10-09)

Status: SUBMITTED FOR CHAT AUDIT.  Maps every step that the frozen certificate (7f71fb43, run bd512f53) declares as "paper" (not machine-verified)
to the document and location where it is proved, and to its audit state.  Machine-checked items are listed for completeness.  No new mathematics.
Legend: AR = Astra report D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md (ff1e1a53, SHA 9fc500bd…); AL = Astra H43_ENDPOINT_LEMMA.md (SHA b1a906ed…);
CN = Code collation note CONTRACT43_ASTRA_COLLATION_NOTE.md (ec3282fa, SHA 07e1c86f…); PD = frozen predeclare v3.4.1 (97d85f59); P1 = P1 design note (69e10460);
C44 = n3_identities_cert.py (79588e2); RUN = Code certificate run output stdout.txt (bd512f53).

## A. Paper steps declared in the certificate SCOPE block
| # | step (certificate wording) | where it is proved | machine support | audit state |
|---|---|---|---|---|
| P1 | Cauchy–Schwarz consequence of the Gram identity (A2): \|N\| <= w D^2 | AR §2 (2.1): (nu - gamma kappa) = (n - gamma e)·(e_x - kappa e), both factors of norm <= 1; CN §2 | Gram identity and unit-vector identities machine-checked (RUN (A2) ×4; AR I04–I06) | AR: chat PASS (script/report); CN: Code collation |
| P2 | mean-value / Lipschitz bound on the convex disk and triangle inequality for R_e (A3): \|s + l\| <= k r, \|u - (xi,0)\| <= R_* + rho | AR §5 (5.2) and §3 (3.3); CN §2 | gradient bound polynomial (9/25)(1-z)^2 - 2z > 0 machine-checked (RUN (A3); AR C04) | AR: chat PASS; CN: Code collation |
| P3 | assembly of (A4): (1-L)s^2 <= (189/500) r^2 + delta/50 and D^2 >= (3/4)(r^2 + L l^2) | AR §5 (5.3), (5.4); CN §1 | SOS identities, coefficient arithmetic and the two Bernstein tables machine-checked (RUN (A4) ×6; AR I11, I12, C05–C07) | AR: chat PASS |
| P4 | zeta-interval and the one-sided majorant (A5): -c_g delta/D^2 <= zeta <= 1, \|zeta\| <= 1+v, zeta^2 <= 1+v^2, M <= 2N^2/(wD^5) | AR §5 (5.5)–(5.7); PD §3 (A5) | identity N = lambda D^2(xi + t zeta/2) and c_g arithmetic machine-checked (RUN (A5); AR I09, C08) | AR: chat PASS |
| P5 | region extension to r <= R_e, Tonelli / order of integration (A6) | AR §6 (first paragraph) and §3 (3.6); AL Proof D (3.E6) for the xi-order; PD §4 L43-I | angular integrals, xi-means, antiderivatives, improper integral machine-checked (RUN (A6) ×8; AR A01–A05) | AR: chat PASS; AL: H-43-1(ii) CLOSED |
| P6 | rho / R_e / lambda monotonicity used to evaluate at (r_0, H_0, 93/200) (A6)–(A7) | AR §6 (6.1) and §7 (log monotonicity 3 log(1+x) >= 2x/(1+x)); PD §3 (A7) | derivative identities d(lambda^p/W)/dlambda and rational constants machine-checked (RUN (A6)/(A7); AR I13, I14, A06, A07, C09–C13) | AR: chat PASS |
| P7 | normalization (S0) of contract 44: [-K_H]_+ <= pi mean_xi M, P units, outer pi, dmu dphi = db dy/mu | C44 (44.2)–(44.4) machine-checked; AR §3 (3.3)–(3.6); CN §2 (normalization paragraph); PD §1 | Jacobian identity machine-checked (RUN (A3)); contract 44 identities (C44) | C44: PASS; AR: chat PASS |

## B. Analytic obligations outside the certificate
| # | obligation | where | state |
|---|---|---|---|
| H1 | H-43-1(i) interchange of differentiation and surface integral, interior points | P1 Lemma V(b) (line 93); AL Proof A (3.E2); evidence closure document CONTRACT43_H43_1_I_EVIDENCE_CLOSURE.md | source collation PASS (chat); closure document submitted |
| H2 | H-43-1(ii) one-sided limits, Lemma V boundary values, improper integral | AL Proofs B–E, (3.E1), (3.E3)–(3.E7); P1 Lemma V(c) (line 95) | CLOSED (chat ruling) |
| H3 | Lemma V source itself | P1 note §5 | CHAT_ANALYTIC_DERIVATION_PASS / EXTERNAL_AUDIT_PENDING / NOT_BINDING (not upgraded by Contract 43) |
| H4 | contract 44 (N1–N3) pointwise inequalities | C44 (44.2), paper step R in [1, pi/2], R_gamma in [-1, 0] from P1 §3.2 | PASS (earlier CHAT AUDIT) |

## C. Machine-checked items of the run (for completeness)
RUN bd512f53: 38 PASS / 0 FAIL, exit 0; (A1) ×2, (A2) ×4, (A3) ×5, (A4) ×6, (A5) ×2, (A6) ×8, (A7) ×7, (A8) ×2, (C6.0), (C6).
Final values: U_43^{N3} <= 3887073979116207/17284813033600000 < 9/40 < BUDGET_V12 = 187614363159/817216000000;
final margin S''_lb - 5481/10000 - U_43^{N3} = 1622585478106563/345696260672000000.

## D. What this table does not do
It does not certify any paper step; it locates each one.  It does not change Contract 43 (FROZEN, machine checks CLOSED), c_FT (UNSET) or D-P2 (NOT_CERTIFIED).
