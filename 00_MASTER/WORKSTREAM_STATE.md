# Workstream state

Updated: 2026-08-08

This ledger separates current workstream control state from older historical status
paragraphs. It records no new machine certificate by itself.

## Item 6 — axial profile

Branch: `agent/prolate-item6-axis`

Audited repair sequence currently includes source head
`6905a795066f7d475d9caf0013d87b9c97192eb0`.

The interval-constructor audit was strengthened from endpoint overlap to full
endpoint-ball containment. GitHub Actions run `31228823621` passed the strengthened audit
at the current repair head. The earlier passing run `31228715053` produced artifact
`9012994554`, whose generated JSON was archived into the branch with a provenance receipt.

The interval-constructor blocker is therefore **CLOSED**.

This does not close item 6. The full axial theorem remains **NOT CERTIFIED** because the
finite-grid and unbounded-tail dependency-DAG obligations remain open. Historical
`STATUS.md` workflow-state text pinned to `c2534aec...` is not the current execution
ledger.

Automatically triggered diagnostic/smoke workflows are not promoted to proof nodes merely
because they succeed.

## Item 3 sweep v9 — control branch

Branch: `agent/item3-sweep-v9-kernel-prototype`

Pinned prototype implementation scope:

```text
base = b82c00f2f154f131e02e122efdb156592fa98070
head = bb990b552d47af8788b5622b29af9dbaad4cf2f1
compare = 10 commits / 8 changed files
```

The post-prototype control-repair sequence adds only workstream/specification controls:

- exact rehearsal range correction;
- multi-run shard/failure semantics;
- aggregate-side selected-shard chain semantics compatible with one-shard reruns;
- reproducible prototype-audit scope correction.

The exact immediate rehearsal range is

```text
[123731943/26214400, 118/25]
width = 2^-20.
```

The later upward objective toward `a_c` remains outside this rehearsal.

The following deterministic controls are treated as resolved inputs to the final freeze:
canonical exact centers, exact split scores, `NONFINITE` ordering, exact tie to `r`, dps-50
partition replay, and fresh dps-70 accepted-cell verification without partition mutation.

For multi-run packaging, immutable shard evidence no longer embeds predecessor-shard
hashes. The aggregate manifest selects one passing attempt per shard, orders selected
hashes by exact mathematical shard index, and independently recomputes the aggregate chain.
This preserves the rule that the minimum mathematical rerun unit is one shard.

## Item 3 sweep v9 — analytic proof branch

Branch: `agent/item3-v9-analytic-proof`

This branch is based on the control branch and isolates the analytic dependency/source
closure.

### Real-analysis state

The real-analysis core is **RESOLVED** for the following statements:

- on every compact machine rectangle with `0<=r<1` and `lambda>=1`,
  `q>0`, `w>0`, `W>0` and all algebraic denominators are uniformly separated from zero;
- the exact square-sum identity proves `0<gamma<=1`;
- `h=acos^2` has a removable endpoint through the required third derivative;
- the explicit `F_r`, `F_lambda`, `F_rr`, `F_rlambda` integrands are obtained by ordinary
  differentiation of the fixed-domain integrand;
- compactness supplies an integrable uniform majorant, so the required parameter
  derivatives pass through the integral;
- mixed differentiation commutes;
- the exact quotient identities for `G_r`, `G_rr`, `G_rlambda` hold;
- the two-variable axis-path mean-value inclusion holds;
- exact midpoint descendants of the inherited r window and rehearsal lambda range remain
  inside the analytic domain.

Accordingly, the **analytic content** of `L-SECOND-DERIV` and `L-MIXED-DERIV`, and the
analytic theorem inside `L-MEAN-VALUE-ENCL`, is no longer `SPEC_PENDING`.

### Old prototype callback audit

Audit against the pinned `python-flint==0.9.0` `acb.integral` callback contract found two
source-level defects in the old prototype blob
`57a7725c6ff0c4135723536b313e63d609eac4f6`:

1. nested integration used `analytic_theta and analytic_phi` instead of the combined OR
   requirement;
2. the Gauss `2F1` angle representation had no explicit analytic cut guard although
   `hypgeom_2f1` exposes no `analytic=` callback flag.

These are implementation defects, not failures of the real analytic formulas. The old
prototype remains **NOT APPROVED** and is retained for provenance/comparison only.

### Guarded clean-room candidate v2

A new standalone rigorous-only candidate now exists at

```text
CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_candidate/
prolate_F_derivatives_cleanroom_v9_candidate.py
```

with candidate ID

```text
ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2.
```

It is derived directly from the analytic proof rather than patching the old prototype. It
includes:

- OR propagation of nested analytic requests;
- `analytic=` forwarding to both square roots;
- explicit fail-closed `2F1` cut rejection;
- common `0<r<1`, `lambda>=1` input validation;
- explicit rejection of non-finite validated integrals;
- only the five rigorous F-level interfaces, with no float diagnostic path.

`STATIC_SOURCE_BOUNDARY_V2.md` defines the source boundary and
`static_audit_candidate_v2.py` is present to compute the exact candidate SHA-256 and check
that boundary without importing python-flint.

Candidate v2 is **AUDIT CANDIDATE / NOT APPROVED** until the static auditor and pinned
`python-flint==0.9.0` runtime controls are executed and archived.

### Deterministic contract candidates added

Two additional previously open design areas now have explicit freeze candidates:

1. `ORDER_CHECKPOINT_FREEZE_CANDIDATE.md` inherits v8.1 ordering: r lower-first,
   lambda upper-first, LIFO replay; it also fixes atomic replacement, file+directory
   fsync, JSONL tail recovery, checkpoint cadence, and a five-percent overhead gate.
2. `QUOTIENT_EXPRESSION_FREEZE_CANDIDATE.md` defines direct and common-denominator
   interval associations for `G_r`, `G_rr`, `G_rlambda`; when both are finite their
   rigorous intersection is used, when only one is finite that finite enclosure is used,
   and disjoint finite results are fatal source inconsistency.

These are freeze candidates, not yet normative final contract bytes.

### Independent rederivation

The independent formal rederivation source does not import the prototype kernel, candidate
v2, adapter, runner, or checker. Its pinned GitHub execution artifact is still pending.

## Remaining v9 freeze blockers

Overall v9 status remains **SPEC_PENDING / FREEZE NOT AUTHORIZED**. Remaining blockers are
now:

1. execute/archive candidate-v2 static audit and pinned `python-flint==0.9.0` runtime
   analytic-flag/integration controls;
2. execute/archive the independent analytic rederivation under a pinned environment;
3. incorporate and independently validate the quotient-expression and ordering/checkpoint
   freeze candidates;
4. complete the final source-level runner/checker domain-enforcement audit;
5. freeze the remaining evidence schema IDs/byte grammars, including aggregate-chain byte
   grammar;
6. build canonical dependency-entry objects and hashes from the final proof/source bytes;
7. complete the independent validation corpus and post-import source-identity checks;
8. freeze performance margin/repetition policy and run qualification;
9. implement/validate the multi-run aggregate verifier;
10. perform the one-shot v9 contract freeze and only then run the `2^-20` production
    rehearsal.

## Promotion rule

No workstream is promoted by a successful diagnostic, smoke, prototype, partial run, or
formal symbolic check alone. A production rehearsal or final theorem claim requires the
exact frozen dependency and evidence gates for that workstream. Failed or incomplete
rehearsal evidence remains fail-closed and cannot be converted into a certified subrange
by silently shrinking the approved target.
