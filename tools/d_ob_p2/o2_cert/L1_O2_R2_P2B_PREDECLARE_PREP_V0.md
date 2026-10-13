# D-OB P2 / D-AN-1 / L1 / O2
## R2 P2-b execution-predeclare preparation V0

**Date:** 2026-10-14  
**Drafter:** ChatGPT / Dig  
**Status:** DRAFT / NOT FROZEN / EXECUTION PROHIBITED / CHAT AUDIT REQUESTED  
**Purpose:** prepare the exact freeze gates for the R2 execution predeclaration without inventing unresolved numerical parameters.

This file does **not** authorize an O2 run. D5 currently owns the research machine exclusively. No O2 producer/checker execution, numerical diagnostic, parameter sweep, or tuning is permitted while D5 is running.

---

## 0. Fixed upstream basis

Base commit:

`fbadfc4d3424b0b4d08ac401bfc9ca6c8015098a`

Fixed upstream documents at that commit:

- `L1_O2_R2_PREDECLARE_V0.md`
- `L1_O2_R2_PREDECLARE_V0_R1_DIFF.md`
- `L1_O2_P2_R1_PREDECLARE_V1_R1.md`
- O2-A3 v1.1-r1, SHA-256 `7dcbd6d660629b09c6e17ddebeb0e2210596ea2f54867d588288c8f8e16b12c5`
- O2 P2 v1-r1, SHA-256 `3f0fcdb3ec53aef7b944c9c51063d4aaf872a8e6e0cbb1aec6e18530cfaf6b5d`
- O2 P0-P1 commit `0456c1ef`, ADOPTED

Judge state inherited from 2026-10-10:

- R1: FAIL-CLOSED.
- R2 framework: adopted as the route to prepare.
- O2: NOT_CERTIFIED.
- L1 / D-P2: not discharged by this work.

No exact prior values were found for `tau_1`, outer-box count, integration-cell count, approximation degree, rational error split, or resource cap. They must therefore be derived and fixed before FREEZE; they must not be fabricated in this preparation file.

---

## 1. Claim and fixed domain

The target is the direct K-form positive mass

\[
M_+(\lambda,\tau,r_{\rm rad})
=\frac12\int_{-1}^{1/2}\int_0^\pi\int_{-1}^{1}
\Phi_{\xi\xi}(t\rho,z)\,dt\,d\phi\,d\mu,
\]

with

\[
\rho=r_{\rm rad}\frac{1-\tau^2}{1+\tau^2},\qquad
z=\lambda r_{\rm rad}\frac{2\tau}{1+\tau^2}.
\]

The closed parameter domain remains

\[
B_0=
\left[\frac25,\frac{93}{200}\right]_\lambda
\times\left[\frac78,1\right]_\tau
\times\left[\frac78,1\right]_{r_{\rm rad}}.
\]

The positive-mass interval remains

\[
I_+=\left[-1,\frac12\right].
\]

The success claim is unchanged:

\[
\boxed{M_+(\lambda,\tau,r_{\rm rad})\ge h_*>0}
\]

for one explicit rational `h_*` valid on all of `B_0`, in the frozen P normalization.

A run that proves positivity only box-by-box with no common positive rational lower bound does **not** establish the declared Form-II O2 claim.

---

## 2. Fixed analytic representation

Use the direct K-form representation only. Do not replace it by internal R-J, internal R-G, or boundary FT_q machinery.

Let

\[
A=-\lambda b,\quad v=\xi-b,\quad h=h_\xi,\quad D=D_\xi,
\quad \gamma=\gamma_\xi,
\]

\[
u=\partial_\xi\gamma
=\frac1w\left(\frac AD-\frac{hv}{D^3}\right),
\]

\[
j=\partial_{\xi\xi}\gamma
=\frac1w\left(-\frac{2Av+h}{D^3}+\frac{3hv^2}{D^5}\right),
\]

and

\[
\Phi_{\xi\xi}
=2Ag'(\gamma)u+h\left[g''(\gamma)u^2+g'(\gamma)j\right].
\]

The R1 failure prohibits the strategy of independently taking absolute bounds of the displayed terms and then integrating. R2 must preserve signed information and cancellation through the integral lower bound.

---

## 3. Fixed geometry gates

The global insurance bounds remain available:

\[
D_\xi\ge\frac{83}{565},\qquad
h_\xi\ge\frac{83}{565},\qquad
w\ge\frac25,\qquad
0<\gamma_\xi\le1.
\]

R2-L1 is mandatory:

\[
\boxed{D_\xi^2\ge(a-|\xi|)^2+(\lambda\mu-z)^2.}
\]

For every parameter box `B` and integration cell `J`, P2-b must specify how a rational lower bound

\[
\underline D(B,J)>0
\]

is proved without invalid dependency loss. If the sign of `a-|xi|` is not fixed on a cell, endpoint squaring is forbidden; use a valid interval-square lower bound or Bernstein certification.

The face `r_rad=1` remains part of the closed claim and is handled by continuous extension of the same K-form, conditional on the stated P1 continuity dependencies. It is not replaced by a boundary R-G identity.

---

## 4. The T1/T2 split that P2-b must freeze

R2 v0-r1 allows two exact routes.

### T1: away from the axis

For an exact rational

\[
\frac78\le\tau_1<1,
\]

on `tau <= tau_1`, use

\[
M_+
=\frac12\int_{-1}^{1/2}\int_0^\pi
\frac{\Phi_\xi(\rho,z)-\Phi_\xi(-\rho,z)}{\rho}
\,d\phi\,d\mu,
\]

where

\[
\rho\ge\rho_{\min}
:=\frac78\frac{1-\tau_1^2}{1+\tau_1^2}>0.
\]

### T2: near the axis

On `tau >= tau_1`, retain the symmetric FTC representation. If the quadratic even-part remainder is used,

\[
\int_{-1}^{1}f(t\rho)\,dt=2f(0)+E_{\rm axis},
\]

\[
|E_{\rm axis}|\le\frac{\rho^2}{3}
\sup_{|\xi|\le\rho}|\Phi_{\xi\xi\xi\xi}(\xi,z)|.
\]

Then P2-b must include a rigorous rational bound for the fourth xi derivative, including the required treatment of `g^(4)`, **or** must declare a different exact even-part remainder that avoids that derivative.

### Freeze gate T

Before FREEZE, the predeclaration must fix all of the following together:

1. exact rational `tau_1`;
2. exact rational `rho_min` implied by it;
3. the T2 remainder representation;
4. every derivative order of `g` needed by that representation;
5. a paper proof that the two closed tau regions cover `[7/8,1]` with no gap.

`tau_1` must be selected from an analytic inequality or a predeclared complexity theorem. It may not be selected by a diagnostic scan of margins or runtime.

---

## 5. Rational envelope gate for g

Use

\[
\sigma=1-s
\]

for the `s -> 1` expansion, reserving `u` for `partial_xi gamma`.

Before FREEZE, P2-b must state exactly:

1. the rational derivation of all expansion coefficients;
2. the truncation degree `N_g` for each of `g, g', g'', g'''` and, if T2 requires it, `g^(4)`;
3. the exact interval(s) in `sigma` on which each envelope applies;
4. rational upper and lower remainder formulas, with their direction of inequality;
5. the endpoint `s=1` treatment;
6. the independent checker proof for every coefficient identity and remainder inequality.

No degree or interval may be chosen by first running a parameter scan.

---

## 6. Outer parameter boxes and inner integration cells

The v0 framework fixes only the initial boxes

\[
B_0=[2/5,93/200]\times[7/8,1]\times[7/8,1]
\]

and

\[
J_0=[-1,1/2]_\mu\times[0,1]_\theta\times[-1,1]_t
\]

before any T1 simplification.

P2-b must additionally freeze:

- the coordinate split order for outer boxes;
- exact rational split points or a deterministic exact-rational splitting rule;
- the maximum outer-box count and maximum outer depth;
- the inner integration-cell variables actually present under T1 and T2;
- exact split rules for those cells;
- maximum cell count and maximum cell depth;
- canonical traversal order;
- the rule for carrying signed cell lower bounds into the box total.

A later implementation may subdivide only according to this frozen deterministic rule. A margin-dependent or runtime-dependent new split axis/rational point is a contract violation unless separately predeclared before execution.

---

## 7. Error-budget gate

For every certified outer box, the proof object must expose a lower-bound ledger of the form

\[
L_{\rm box}
=L_{\rm poly/int}
-E_g-E_{\sqrt{\ }}-E_{\cos}-E_{\rm rem}-E_{\rm rat},
\]

with only terms that are actually present in the selected representation.

P2-b must replace these symbolic names by exact rational budgets and state which errors are local-cell errors and which are box/global errors.

Requirements:

- every error budget is nonnegative and rational;
- no hidden floating-point rounding credit;
- no double counting of a remainder;
- the checker recomputes the total from primitive certificate fields;
- PASS requires `L_box >= h_*` for the declared common rational `h_*` after all errors are subtracted.

The exact numerical budget is **UNSET** in this preparation file and is a mandatory freeze gate.

---

## 8. Producer / checker separation

The future producer may construct:

- rational function envelopes;
- Bernstein or equivalent signed polynomial lower bounds;
- parameter-box and integration-cell subdivisions according to the frozen rule;
- per-cell exact integrals / lower bounds;
- box lower-bound ledgers;
- the candidate common `h_*`.

The independent checker must not trust producer summary fields. It must independently verify at least:

1. upstream identity hashes and contract hash;
2. exact cover of the frozen parameter domain;
3. no extra or missing outer box;
4. canonical order where order is part of the contract;
5. every rational split endpoint;
6. every polynomial/envelope coefficient identity;
7. every remainder direction and denominator-positivity claim;
8. R2-L1 lower-bound validity where used;
9. exact signed summation of integration cells;
10. every box lower bound and the final common `h_*` comparison;
11. the T1/T2 cover at `tau=tau_1`;
12. boundary handling at `r_rad=1` and `tau=1` under the frozen representation.

Producer and checker source hashes must be pinned before the evidentiary run.

---

## 9. Resource and execution gate

Before FREEZE, P2-b must state exact limits for:

- worker count;
- maximum outer boxes / depth;
- maximum inner cells / depth;
- polynomial/envelope degree;
- wall-clock or node/cell budget if used as a fail-closed limit;
- heartbeat / ledger behavior;
- interruption and resume policy;
- output artifact set;
- identity-before / identity-after records.

No value is fixed here because no prior Judge-approved exact values were found.

The O2 evidentiary run must not begin while D5 owns the research machine. Preparation and static audit may proceed in parallel; execution waits for D5 release and the normal audit/FREEZE gate.

---

## 10. PASS / FAIL-CLOSED vocabulary

`PASS` for the future certificate requires all frozen boxes to prove the declared common rational `h_*>0`, with exact complete coverage and an independent checker PASS.

The run is `FAIL-CLOSED` if, among other frozen failure conditions:

- any region remains uncovered;
- a denominator/envelope positivity condition cannot be proved;
- a rational approximation remainder is not certified in the required direction;
- the T1/T2 interface is incomplete;
- a box lower bound falls below the declared `h_*`;
- resource limits are reached with unresolved boxes/cells;
- producer/checker identity or source hashes mismatch;
- the checker cannot reconstruct the certificate solely from frozen primitives.

Failure of this certificate is **not** a mathematical counterexample to `M_+>0` unless a separate rigorous sign counterexample is produced.

No automatic route change is authorized by a failed run.

---

## 11. Remaining analytic work before the real P2-b predeclaration

The next paper-only tasks are:

1. derive an analytic criterion for choosing `tau_1` and prove the resulting `rho_min`;
2. choose T2's exact even-part remainder route and derive its derivative/envelope obligations;
3. construct the rational `g`-family envelopes, including `g^(4)` if retained;
4. define a deterministic rational outer/cell partition theorem rather than tuning from diagnostics;
5. derive a symbolic error-budget formula that can be populated by exact rational constants;
6. from those proofs, fix exact box/cell/depth/degree/resource numbers;
7. only then issue `L1_O2_R2_P2B_PREDECLARE_V1.md` for chat audit.

Until all seven items are fixed, the state remains:

**DRAFT / NOT FROZEN / EXECUTION PROHIBITED / O2 NOT_CERTIFIED.**
