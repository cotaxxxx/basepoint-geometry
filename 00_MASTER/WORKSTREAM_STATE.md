# Workstream state

Updated: 2026-08-08

This ledger separates current workstream control state from older historical status
paragraphs. It records no new mathematical theorem by itself.

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

## Item 3 sweep v9

Branch: `agent/item3-sweep-v9-kernel-prototype`

Pinned prototype implementation scope:

```text
base = b82c00f2f154f131e02e122efdb156592fa98070
head = bb990b552d47af8788b5622b29af9dbaad4cf2f1
compare = 10 commits / 8 changed files
```

The post-prototype control-repair sequence through
`2b7831296b8c5796ebc05d06bd23b290e84497e6` adds only workstream/specification controls:

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

Overall v9 status remains **SPEC_PENDING / FREEZE NOT AUTHORIZED**. Remaining blockers
include the production-grade analytic derivative package, differentiation-under-integral
proofs, endpoint/branch/domain proofs, frozen expression ordering, child/record ordering,
checkpoint durability/schema policy, independent validation corpus, post-import source
identity, performance margin policy, final aggregate-chain byte grammar, and integration
of the multi-run aggregate verifier.

## Promotion rule

No workstream is promoted by a successful diagnostic, smoke, prototype, or partial run.
A production rehearsal or final theorem claim requires the exact frozen dependency and
evidence gates for that workstream. Failed or incomplete rehearsal evidence remains
fail-closed and cannot be converted into a certified subrange by silently shrinking the
approved target.
