# D-OB P2 / D-AN-1 / L1 / O2 — Interior Positive-Mass Predeclare DRAFT v0

**Date:** 2026-10-10
**STATUS:** PREDECLARE ONLY / NOT FROZEN / SUBMITTED FOR CHAT AUDIT / NO DERIVATION / NO COMPUTATION / NO EXECUTION.
**Judge decision (2026-10-10):** Target Form II; if not established, report the proven delta-dependence as Form I. ROUTE A/B/C remains UNDETERMINED pending the achieved delta_L1.
**Parent:** L1 reach lemma SPEC v1 FROZEN, commit `ecd314467e51f89413220a2dcdd8c0d0d040cac3`, `tools/d_ob_p2/predeclare/L1_DELTA_REACH_LEMMA_SPEC_DRAFT.md`, SHA-256 prefix `88153b39`. Sections S2 (G2), S3, S4, S6, S7 (O2), S8 control.
**Prerequisite:** O1 CLOSED (conditional on P1 note); P1 note is NOT_BINDING and awaits external audit. The Judge's O1 closure wording refers to P1 Lemma 3.4; the dependency inventory also includes Lemmas 3.1–3.4 and 6.1. This document does not change that ruling.
**Scope:** O2 predeclaration only. O3 negative-part bounds and O6 coverage proof are NOT authorized.

## 0. Notation, domain, and target

Use `r_rad` exclusively for the interior radial parameter; never use bare `r` for both radius and a boundary polynomial variable. Set
`rho_b(tau)=(1-tau^2)/(1+tau^2)`, `m(tau)=2tau/(1+tau^2)`,
`p=(rho,0,z)=(r_rad rho_b(tau),0,lambda r_rad m(tau))`,
`delta=1-r_rad^2`.
The closed parameter ranges for certificate design are
`lambda in [2/5,93/200]`, `tau in [7/8,1]`, `r_rad in [7/8,1)`; `mu in [-1,1]`.
Thus `rho^2+(z/lambda)^2=r_rad^2<1`. The tau identity `rho_b^2+m^2=1` locates the boundary direction; it is NOT the interior relation `rho^2+m^2=1`.

Conditional on the audited O1 resources, write
`2 pi lambda H(p)=int_{-1}^1 G_p(mu) dmu`.
The O2 goal is an explicit **positive rational** `S_lb_int` such that
`int_{I_+} G_p(mu) dmu >= S_lb_int > 0`
uniformly on the stated domain, including the tau=1 axis as an appropriate continuous/independently justified endpoint. This is a proposed proof target, NOT a claimed inequality.

## 1. Form II: two separate uniformity obligations

**O2-U-delta (surface):** Establish the same rational `S_lb_int` independently of `delta` as `delta -> 0` (`r_rad -> 1`). A bound involving `1/delta`, `log(1/delta)`, or a constant vanishing with delta does NOT satisfy Form II.

**O2-U-axis (axis):** Establish the same `S_lb_int` uniformly as `rho -> 0` (`tau -> 1`), without relying on a division by rho. Prove continuity of the relevant integrated expression or give an independent axis calculation justified by P1 Lemma 6.1(iii), subject to its NOT_BINDING/external-audit condition.

These are distinct obligations. Neither follows from the other. A joint closed-box certificate must account for both simultaneously; separate one-limit arguments without a joint uniform constant are insufficient.

## 2. Predeclared positive interval and geometric separation

**Fixed candidate:** `I_+ := [-1,1/2]`, matching the south positive interval in the boundary construction. This is a candidate, not a pre-proved positive interval. Its use is conditional on proving the sign/integrated positive mass of the **interior** `G_p`; if it fails, report FAIL and submit a revised predeclare before changing intervals.

For any surface point with latitude mu, the Euclidean distance `D` to p obeys the geometric inequality `D >= lambda |mu-r_rad m|` (vertical-coordinate separation). On the declared box, `m>=112/113`, hence `r_rad m >= (7/8)(112/113)=98/113`. For `mu<=1/2`,
`D >= (2/5)(98/113-1/2)=83/565>0`.
This is a **predeclared rational geometric bound**, independent of delta, tau, and rho, to be verified in the paper proof and checked against the exact geometry before use. It establishes separation, not positivity.

For bookkeeping only, designate the complementary candidate `I_- := [1/2,1]`; the endpoint overlap and union `I_+ union I_-=[-1,1]` follow from rational endpoint ordering. O6 must independently certify the final coverage/overlap requirements under the chosen split. No O6 proof is undertaken here. No boundary density is substituted for interior `G_p`.

## 3. Boundary resources are templates, not interior evidence

The south Lemmas A/B/C fixed at canonical commit `bbcfe6628a074d1f7b48e1f818542ee205e88f50`, and the boundary `S''_lb=635530452759/817216000000`, are boundary-only. Their coefficients, positivity certificates, kernel extensions, and numerical margins do NOT prove O2.

In the 39-prime / kernel-extension boundary calculations, the symbol `r := 1-m^2` denotes the boundary polynomial variable, not `r_rad`. Those calculations use `rho_b^2=1-m^2`, `z=lambda m`, and the boundary factorization FT_q (6.1) `N_J=-lambda^2(m-mu)Q`. None may be applied at the interior point, where `rho^2+(z/lambda)^2=r_rad^2<1`.

Mandatory fresh interior obligations before importing any template:
(a) derive the interior geometric forms of `h,D^2,w^2` from the P1 definitions;
(b) use the O1-certified general-point forms of FT_q (5.2), (7.1), (7.2), with all O1/P1 conditions retained, and verify their applicability to this exact domain;
(c) re-derive any interior analogue of the 39-prime sign polynomials, south-kernel extension, and Bernstein coefficients, without the boundary ring relation;
(d) justify the pair/reflection and xi-average steps, especially at rho=0, before division or limit interchange;
(e) prove any positive sign or integrated lower bound anew, including all endpoints.
The present document asserts none of (a)–(e) has been discharged for O2.

## 4. Planned proof stages and verification contracts (not execution)

**Stage P0 — exact interior setup (paper):** Fix the domain and `I_+`, check geometric distance bound `D>=83/565`, and identify exact denominators and their strictly positive lower bounds. No boundary substitution.

**Stage P1 — symbolic interior density (paper + exact checker after authorization):** Starting from the conditional O1 representation and general-point FT_q identities, derive an interior expression for `G_p` or a certified lower majorant/minorant suitable for integration. Preserve paired/xi-averaged cancellation and track the rho=0 limit. Do not assume pointwise `G_p>=0` globally. If a pointwise sign lemma is sought, restrict its claim explicitly to `I_+`; otherwise prove an **integrated** positive-mass inequality directly.

**Stage P2 — positivity on I_+ (paper + exact checker):** Seek a rational integrated lower bound `S_lb_int>0`. Specify whether the argument uses (i) a pointwise nonnegative lower polynomial followed by exact integration or (ii) an integrated inequality allowing local sign changes. The final certificate must state which route was actually proved; a failed pointwise route does not imply failure of the integrated route.

**Stage P3 — joint uniformity (paper + exact checker):** Prove the bound independent of delta and tau up to the two limiting faces, with a joint positive rational constant. Check lambda endpoints, tau endpoints, `r_rad=7/8`, and the limit `r_rad->1` without treating an interior point as a boundary point. Axis endpoint via a certified continuous extension or independent proof.

**Stage P4 — handoff only (paper):** Record the O2 lower bound and assumptions for later O3/O6. No negative-part estimates, no total H positivity claim, and no L1 closure claim.

**Certificate-box predeclaration:** Primary box `[2/5,93/200]_lambda x [7/8,1]_tau x [7/8,1]_{r_rad} x [-1,1/2]_mu` with `r_rad=1` used only as an algebraic limit face where justified, not as an interior point. If `m` is used as an independent polynomial coordinate, certify the exact `tau<->m` substitution and preserve dependencies; do not silently treat `m,tau` as independent. Rational subboxes and coordinate transformations require a separate audited amendment before any run. The proof may use exact rational arithmetic, symbolic polynomial identities, rational Bernstein coefficient positivity, and exact rational integration. Any transcendental constants require predeclared rational enclosures and direction checks. Floating-point probes are not evidence and cannot select constants or partitions.

**Machine checks after separate execution authorization:** Exact polynomial identity residuals; denominator positivity; certificate-box coverage; Bernstein coefficient signs or equivalent exact nonnegativity; rational integral inequalities; rational lower-bound positivity; both limiting-face checks; hashes and reproducible deterministic checker output. **Paper obligations:** derivation from general interior geometry; correctness of the density representation; justification of integration and limiting interchanges; the logical implication from certificates to the O2 integral; axis/surface uniformity and endpoint coverage. Machine PASS alone cannot replace paper proofs.

## 5. Fallback reporting: Form I, not silent weakening

If Form II cannot be established, the report must explicitly state `FORM II NOT PROVED` (or `REFUTED` only with a rigorous counterexample), the precise failing obligation (O2-U-delta and/or O2-U-axis), and the exact valid parameter range. Where a rigorous bound exists only for `delta>=delta_L1>0`, report it as
`int_{I_+} G_p dmu >= S_lb_int(delta_L1)>0`
with the explicit dependence, all conditions, and the status `FORM I CANDIDATE / O2 NOT CLOSED AS FORM II`. Do not relabel an O2 positive-mass bound as the full L1 lower bound `h_L1(delta_L1)`: the latter requires O3–O6 and the factor `2 pi lambda`. If a later complete L1 proof yields `H>=h_L1(delta_L1)>0`, its dependence must be recorded separately. No numerical delta_L1 is selected in this predeclare; ROUTE remains UNDETERMINED.

## 6. Prohibitions and governance

- Do NOT use E1, E2, or unlocated E3/G2 material as evidence, positive or negative.
- Do NOT import boundary-only (6.1), `rho^2=1-m^2`, `z=lambda m`, 39-prime coefficients, or boundary certificates as interior identities.
- Do NOT choose constants, intervals, partitions, or cutoff values by sampling or numerical exploration.
- Do NOT begin O3 negative-part bounds or O6 coverage proof. Stating their future interface is not executing them.
- Do NOT run derivations, SymPy, proof checkers, numerical experiments, or any O2 computation before separate Judge authorization.
- Preserve all existing evidence and prior run artifacts unchanged. Do not claim O2 CLOSED, L1 CLOSED, or D-P2 CERTIFIED.

**Ledger:** south 39-prime CLOSED; north far Contract 45 CLOSED; near Contract 43 CERTIFIED; FT_q DISCHARGED conditional on external P1 Lemma V audit; O1 CLOSED conditional on P1 note; Form II TARGET by Judge 2026-10-10; ROUTE UNDETERMINED; O2 PREDECLARE ONLY / NOT FROZEN; L1 PAUSED; D-P2 NOT_CERTIFIED.

**Gate:** submit this one-file DRAFT v0 for CHAT AUDIT; Judge alone decides FREEZE; only a further explicit Judge instruction permits derivation/computation/execution.
