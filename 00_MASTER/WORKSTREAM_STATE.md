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

This branch is based on the control branch and isolates the analytic dependency closure.
It now contains:

```text
ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md
SOURCE_FORMULA_MAP_V9.md
independent_analytic_rederivation_v9.py
analytic_second_mixed_derivative_appendix.md   (revised)
```

The real-analysis core is now **RESOLVED** for the following statements:

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
- the two-variable axis-path mean-value inclusion holds.

Accordingly, the **analytic content** of `L-SECOND-DERIV` and `L-MIXED-DERIV`, and the
analytic theorem inside `L-MEAN-VALUE-ENCL`, is no longer `SPEC_PENDING`.

This is not yet machine authorization. The independent formal rederivation source does not
import the prototype kernel, adapter, runner, or checker, but its pinned execution artifact
is still pending. The current prototype has been statically mapped to the proved formulas;
final source-byte validation remains required.

## Remaining v9 freeze blockers

Overall v9 status remains **SPEC_PENDING / FREEZE NOT AUTHORIZED**. The remaining blockers
are now primarily implementation/validation rather than real analysis:

1. execute and archive the independent analytic rederivation under a pinned environment;
2. validate concrete `acb.integral` enclosure semantics and analytic-flag behavior;
3. freeze the interval association and `expression_id` for `G_r`, `G_rr`, `G_rlambda`;
4. statically prove final runner/checker domain enforcement (`0<r<1`, approved lambda range);
5. freeze child/record ordering and checkpoint durability/schema policy;
6. build canonical dependency-entry objects and hashes;
7. complete the independent validation corpus and post-import source identity checks;
8. freeze performance margin/repetition policy;
9. freeze the final aggregate-chain byte grammar and implement the multi-run aggregate
   verifier.

## Promotion rule

No workstream is promoted by a successful diagnostic, smoke, prototype, partial run, or
formal symbolic check alone. A production rehearsal or final theorem claim requires the
exact frozen dependency and evidence gates for that workstream. Failed or incomplete
rehearsal evidence remains fail-closed and cannot be converted into a certified subrange
by silently shrinking the approved target.
