# B-LOCAL v2.2 — readiness design-reset correction

Status: **NORMATIVE DESIGN CORRECTION — IMPLEMENTATION NOT AUTHORIZED**  
Base commit: `f21704b2cbd2954acb492ec2a58dbb0765773f1f`  
Scope: B-LOCAL v2.2 finite evaluation architecture after production-shaped readiness diagnostics  
Certificate evidence: **no** — the runtime measurements cited here are design evidence only  
Production authorization: **no**  
Tag authorization: **no**

This document is a correction to the evaluator-feasibility assumptions of the three
already-audited B-LOCAL v2.2 design documents:

1. `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM.md`,
2. `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM_F4_CORRECTION.md`,
3. `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM_F5_JSTART_CORRECTION.md`.

Those three documents remain normative except where this correction explicitly
supersedes their evaluator-selection or readiness-feasibility provisions.  Exact
algebraic identities, consumer maps, record/reconstruction requirements,
fail-closed rules, provenance rules, and the prohibition on the dead pinned
integrators remain in force unless explicitly stated otherwise below.

---

## 0. Reason for this correction

The previous design cycle correctly removed the v2.1 non-finite integral route and
placed all runtime `F`/`F_r` consumers on cancellation-free finite-route formulas.
The resulting draft did become finite at points that previously failed immediately.
However, production-shaped readiness demonstrated that the **natural Arb interval
extension plus adaptive angular ball-sum is not a viable production evaluator under
the current v2.2 policy**, even after the non-finite defects were repaired.

This is not a claim that the exact F/K identities are wrong.  It is a claim about
the **enclosure architecture and its dependency growth**.

The current natural-interval evaluator family is therefore withdrawn from
production-readiness status.  No source freeze, final config materialization,
production tag, workflow promotion, or certificate run may be based on it.

---

## 1. Preserved exact mathematics

The following facts remain GREEN and normative.

### 1.1 Geometry and cancellation identities

With the notation of the prior design documents,

`A = rho^2 Ahat`,

`B = rho^2 Bhat`,

`M = U Ahat + r Bhat`,

`N = -rho^2 M`.

The exact SOS identity remains:

`w^2 q - lambda^2 W^2`

`= (c S (lambda^2-1) + r c cos(phi))^2`

`  + r^2 sin(phi)^2 w^2`.

The exact derivative relation remains

`H_u = -F_r`.

The exact transformed K identity remains

`J = rho K`.

The `1/pi` normalization remains mandatory.

### 1.2 F cancellation-free bracket

The F correction remains exact:

`K_F = -U h(gamma) - L h'(gamma) M y_h z^2`,

where

`y_h = W/sqrt(q)`,

`z = rho/sqrt(q)`,

`gamma = L y_h`.

The algebraically identical dependency-reduced form

`K_F = -U h(gamma) - h'(gamma) M gamma z^2`

is also exact because `gamma = L y_h`.

The second form was used diagnostically only.  This correction records the identity
but does **not** by itself authorize a production evaluator based on it.

### 1.3 Regular normalized identities

For regular cells the following identities are exact and may be used by a future
evaluator proposal:

`rho^2 = c^2 + phi^2`,

`B = sin(phi)^2 + c^2 cos(phi)^2`,

`What = W/rho`,

`Vhat = (r-U)/rho`,

`D = q/rho^2`,

`D = What^2 + Ahat + r^2 Bhat`,

`D = Vhat^2 + Bhat + Ahat`,

`z = 1/sqrt(D)`,

`y_h = What z`.

For R1, with `t = phi/c`,

`rho = c sqrt(1+t^2)`,

`Ahat = (lambda^2-1)/(1+t^2)`,

`Bhat = ((sin(phi)/c)^2 + cos(phi)^2)/(1+t^2)`.

Equivalently,

`Bhat = (t^2 sinc(phi)^2 + cos(phi)^2)/(1+t^2)`.

For R2, with `t = c/phi`,

`rho = phi sqrt(1+t^2)`,

`Ahat = (lambda^2-1)t^2/(1+t^2)`,

`Bhat = (sinc(phi)^2 + t^2 cos(phi)^2)/(1+t^2)`.

These are algebraic normalization identities.  They do not certify the efficiency
of any particular interval extension.

---

## 2. Consumer map remains closed

The complete runtime `F`/`F_r` consumer map remains:

1. L1 — `H_u=-F_r`,
2. L2 — `F`,
3. L3 — `F`,
4. J_START — point `F`, bracket derivative `F_r`, and interval Newton data.

Stage-1 remains a byte/provenance dependency and does not consume the runtime F/F_r
evaluators.

Any future evaluator architecture must cover all four consumers.  A method that
works only for L1, only for F, or only at exact points is incomplete.

---

## 3. Direct pinned integrators remain forbidden

The following remain forbidden as certificate evaluators:

- direct `F_arb`,
- direct `dFdr_arb`,
- silent fallback to either integrator,
- exception suppression followed by an alternate formula,
- replacing `r=1` by `1-epsilon`,
- changing the certified domain to avoid a singular endpoint.

The v2.1 incident remains historical evidence and must not be rewritten or erased.

---

## 4. Production-shaped readiness evidence

All measurements in this section are **design evidence only**.  They are not
certificate evidence and do not establish any theorem statement.

The diagnostic source branch used for these measurements was
`agent/blocal-v22-readiness-draft`.

The nine native draft sources used by the first CI readiness were the bytes whose
head before later diagnostic-only files/workflows was
`007977adb6910d97d718dc3a6a9160eed80cc878`.

No final v2.2 config was materialized.  CI created only ephemeral configs and checked
that the committed v2.2 run config was not modified.

### 4.1 Baseline CI readiness — run 31485433561

Environment:

- GitHub-hosted Ubuntu runner,
- Python 3.13,
- `python-flint==0.9.0`,
- precision and design values inherited from the v2.2 readiness draft,
- `eps = 2^-8`.

Observed:

- static exact audit: PASS,
- binding negative controls: PASS,
- symbolic exact audit: PASS,
- J_START initial F point at `r=1-2^-8`: finite in approximately `0.007677 s`,
- L2: approximately `453 s`, then angular evaluation budget exhausted,
- L1 tile `u=[2^-9,2^-8]`: approximately `463 s`, then angular evaluation budget exhausted,
- L3: reciprocal-factor Arb hull lost positivity,
- J_START: initial F enclosure was finite but crossed zero because the draft point
  call did not request sign resolution.

This run established that the R-1 through R-4 repairs removed the earlier immediate
non-finite failure but did not make the evaluator production-ready.

### 4.2 R-6 — positive reciprocal factors must not be re-hulled

A positive exact reciprocal interval can again acquire a tiny negative lower Arb
endpoint if a very wide endpoint pair is immediately stored as one midpoint-radius
ball.

Therefore, for any future design that uses exact positive endpoint reciprocal
factors, the following rule is binding:

> Positive endpoint factors used to preserve denominator sign must remain separate
> through the multiplication to which their monotonic endpoint rule applies.  A
> wide positive pair must not be re-hulled into one Arb ball before that
> multiplication unless positivity of the resulting Arb hull is independently
> certified.

This is a representation rule, not a new mathematical identity.

### 4.3 R-7 — J_START sign-resolution modes

The J_START evaluator contract remains:

- initial left F value: strict `POS` resolution required,
- bisection F values: strict `NONZERO` resolution required; the result must separate
  into POS or NEG,
- retained-right value: NEG,
- bracket derivative: `H_u>0`, then exact interval negation to `F_r<0`,
- Newton midpoint F: sign is not itself required; a rigorous enclosure is required,
- interval Newton: exact rational interval division by a derivative interval
  excluding zero and strict self-containment.

A point call that returns a finite but unresolved enclosure is not a certified sign.

### 4.4 R-5/R-8 — natural interval dependency did not converge sufficiently

Subsequent diagnostic probes made the previously non-finite computations fast, but
showed that enclosure width, rather than raw computation cost, is the dominant
failure.

At the first candidate and fixed `eps=2^-8`, a priority-queue/incremental-sum
prototype with normalized regular hat variables still exhausted its evaluation
budget with a root interval crossing zero widely.

A diagnostic budget sweep at fixed depth 12 gave approximately:

- 24,000 evaluations: `[-1.55082, 2.44635]`,
- 48,000 evaluations: `[-1.39495, 2.30042]`,
- 96,000 evaluations: `[-1.29076, 2.20506]`.

All three remained unresolved.

The corresponding diagnostic run was `31492260765`.

Increasing depth while holding the diagnostic budget at 96,000 also did not close
the sign:

- depth 14: approximately `[-1.28894, 2.17195]`,
- depth 16: approximately `[-1.28882, 2.20256]`.

The corresponding diagnostic run was `31492607462`.

These measurements show that **post-hoc budget or depth inflation is not an
acceptable repair** for the current natural interval architecture.

### 4.5 Dominant dependency example

In diagnostic run `31491596350`, a dominant smooth R1 child had approximately:

- `c in [1/256, 271/4096]`,
- `phi` in a small positive low-angle band,
- `D_floor` about `0.064748`,
- `U` enclosure roughly `[-1.1e-4, 1.0009]`,
- `M` roughly `[-1.59, 4.26]`,
- `gamma` roughly `[0,1]`,
- `z` roughly `[0.479, 2.962]`,
- `h'` roughly `[-3.60, -1.82]`.

The second exact F term

`-h'(gamma) M gamma z^2`

then dominated the interval width.

This is evidence of dependency growth in the natural interval extension, not an
algebraic failure of the cancellation identity.

### 4.6 Geometric seeding helped locally but did not solve the root enclosure

Eight exact geometric R1 c-bands reduced the largest single-cell width by roughly a
factor of 51, but the 12,000-evaluation root enclosure remained unresolved.  The
run was `31491789171`.

A 32-seed R1 partition did not materially improve the root enclosure at the same
budget.  The run was `31492064954`.

The diagnostic width aggregation showed that the dominant uncertainty had migrated
to smooth high-c R1 bands, not the Duffy corner or the c≈0 side.

### 4.7 Direct high-c hybrid was decisively worse

As a final method-family check, smooth high-c R1 cells were routed back through the
native direct regular natural-extension formula while lower-c/R2 cells retained
the hat prototype.

Exact thresholds `c*=1/8`, `1/4`, and `1/2` were tested with the same 12,000
readiness evaluation budget.

All three failed, and the direct high-c cells produced substantially wider
contributions than the hat-only diagnostic architecture.

The diagnostic run was `31492896854`.

Therefore:

> A direct-natural-extension high-c fallback is rejected as the next production
> design direction.

This is a design rejection based on the measured prototype; it does not say that no
other specialized smooth-region method can work.

---

## 5. Superseded evaluator-feasibility claims

The following previous design implications are superseded.

### 5.1 Whole-domain ball-sum readiness

It is no longer valid to infer that putting all consumers on finite F/K formulas,
per-box gamma subdivision, safe denominators, per-subbox q bounds, and adaptive
angular subdivision is sufficient for production readiness.

Those ingredients are still necessary where used, but the current natural interval
ball-sum has not demonstrated adequate dependency control.

### 5.2 Fixed route-policy readiness

The existing draft policy values such as `max_depth=12` and
`max_evaluations=12000` are **not approved production values**.

They may remain historical draft values.  They must not be silently increased and
then treated as if the original readiness contract passed.

Any future production budget must be bound only after the replacement evaluator has
passed its method-selection feasibility gate.

### 5.3 Current regular-cell natural extension

The current regular R1/R2 natural Arb evaluation, including the experimental
full-hat natural extension, is not an approved production regular-cell evaluator.

The Duffy corner exact transformations and exact algebraic identities remain
available; the rejection here concerns the regular-cell enclosure architecture.

---

## 6. New method-selection gate

No new native v2.2 evaluator implementation is authorized by this correction.

The next technical phase is **method selection**, not implementation repair.

A replacement regular smooth-region evaluator must first be demonstrated in a
DIAGNOSTIC prototype and then specified in a separate audited method-selection
addendum before it may enter the nine production sources.

### 6.1 Candidate class

The leading candidate class is a dependency-reducing smooth-cell enclosure such as:

- a centered/mean-value interval form,
- a certified first- or second-order Taylor enclosure with rigorous remainder,
- an equivalent rigorous local polynomial enclosure.

This list is a research direction, not an authorization to choose one silently.

No reusable repository-native certified Taylor/centered-form infrastructure has
been positively identified during the readiness reset.  A future proposal must
therefore specify its exact formulas, derivative/remainder bounds, interval
arithmetic rules, and checker reconstruction rather than assuming such an
infrastructure exists.

### 6.2 Mandatory feasibility domains

A candidate replacement method must, at minimum, demonstrate the following on the
first production candidate with `eps=2^-8`:

1. J_START initial F point at `r=1-2^-8`: strict POS,
2. L2 first face/domain: strict POS,
3. L3 `r=1` first face/domain: strict NEG,
4. L1 representative tile `u=[2^-9,2^-8]`: strict `H_u>0`,
5. a J_START derivative bracket with exact `H_u -> -F_r` negation and `0 notin F_r`,
6. a complete J_START bisection/Newton path through strict self-containment.

A method that only narrows an enclosure without satisfying these predicates does not
pass the gate.

### 6.3 Budget discipline

Before a feasibility run, the prototype must declare a finite evaluation/depth/time
budget.

The budget may differ from the rejected draft values, but it must be fixed before
the run.  A failed run may motivate a new diagnostic experiment, but the budget
must not be raised after failure and then described as the same passing run.

Production budget values are not selected in this correction.  They become
normative only in the later method-selection addendum after successful diagnostic
feasibility.

### 6.4 Fail-closed requirements

The feasibility prototype must fail closed on:

- non-finite Arb data,
- an unproved positive denominator,
- a lost endpoint monotonicity condition,
- an unproved Taylor/remainder bound,
- an unresolved required sign,
- budget or depth exhaustion,
- incomplete angular/domain cover,
- any silent formula fallback.

### 6.5 Required diagnostic record

Each feasibility result must report at least:

- prototype identifier and exact source bytes/hash,
- git source head,
- runtime environment and python-flint version,
- exact tested domain,
- exact lambda/u/eps values,
- declared budgets,
- final enclosure,
- strict predicate result,
- evaluation/subdivision counts,
- elapsed time,
- failure reason if not certified,
- `certificate_evidence=false`.

A successful diagnostic result remains non-certificate evidence until the method is
specified, independently audited, implemented, pinned, and rerun under the final
production config.

---

## 7. Method-selection addendum required before native implementation

If a diagnostic candidate passes Section 6, the next artifact is a separate
**B-LOCAL v2.2 method-selection addendum**.

That addendum must make the selected regular evaluator fully normative, including:

1. exact local coordinates and partition rules,
2. exact centered/Taylor/polynomial formula,
3. exact derivative or remainder enclosure,
4. all analytic helper inequalities and their runtime/static validation,
5. interval rounding and endpoint rules,
6. deterministic subdivision/priority policy,
7. explicit production budgets,
8. F and K/H_u coverage,
9. L1/L2/L3/J_START integration,
10. checker reconstruction requirements,
11. binding negative controls,
12. complete records sufficient for independent reconstruction,
13. prohibition on direct pinned-integrator fallback,
14. provenance and source/config materialization sequencing.

The addendum must itself receive chat byte/content/math audit GREEN before native
implementation resumes.

---

## 8. Preserved Duffy/corner contract

Nothing in the readiness reset withdraws the exact two-triangle Duffy substitution
or the already-audited corner identities.

A future regular smooth-region evaluator may coexist with the Duffy corner route,
provided the total angular partition remains exact, non-overlapping except on
shared boundaries, and checker-reconstructible.

No circular-patch substitution is authorized.

---

## 9. Provenance and branch discipline

The diagnostic readiness branch and all runtime probes are evidence of failed or
successful design experiments only.  Their scripts/workflows are not to be copied
silently into production source.

The nine native readiness-draft source bytes are not frozen production bytes.

Until a method-selection addendum is audited GREEN:

- no final v2.2 config materialization,
- no source freeze,
- no source pin promotion,
- no production workflow promotion,
- no tag,
- no certificate production run.

When native implementation is eventually re-authorized, the prior sequencing rule
remains:

1. complete all production source/checker/test/audit/policy bytes,
2. run the specifically authorized static/readiness tests,
3. freeze final source bytes,
4. independently calculate all final source SHA-256 values,
5. materialize the config **last** from those final hashes,
6. source plus final config in the authorized single commit,
7. STOP,
8. independent chat byte/code/math audit,
9. only after GREEN may later tag/workflow/production authorization be considered.

---

## 10. Binding interpretation of the readiness evidence

The following conclusions are binding for the next design cycle:

1. **Finite is not sufficient.**  R-1 through R-4 removed immediate NONFINITE
   failure, but strict-sign dependency remained unresolved.
2. **Positive reciprocal endpoint factors must not be prematurely re-hulled.**
3. **J_START needs explicit sign-resolution modes.**
4. **Natural interval dependency in regular smooth cells is the current blocker.**
5. **Budget inflation alone is rejected.**  24k/48k/96k remained unresolved.
6. **Depth inflation alone is rejected.**  depth 14/16 at 96k remained unresolved.
7. **More initial R1 seeds alone is rejected.**
8. **Direct natural high-c fallback is rejected.**
9. **The exact F/K/Duffy algebra remains valid and reusable.**
10. **A dependency-reducing regular smooth-cell enclosure must pass a diagnostic
    method-selection gate before any further native implementation.**

---

## 11. STOP gate

This correction does **not** authorize the next implementation.

After this file is committed, the required state is:

`DESIGN_RESET_CORRECTION_COMMITTED — STOP — CHAT BYTE/CONTENT/MATH AUDIT REQUIRED`

If the audit is RED, correct the design document only.

If the audit is GREEN, proceed only to diagnostic method-selection work under
Section 6.  Do not promote a diagnostic prototype to the nine production sources
without the separate method-selection addendum required by Section 7.
