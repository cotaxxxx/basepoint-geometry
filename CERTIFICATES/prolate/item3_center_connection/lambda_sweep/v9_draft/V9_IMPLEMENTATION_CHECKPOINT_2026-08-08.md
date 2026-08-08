# Item 3 sweep v9 — implementation checkpoint

**Date:** 2026-08-08  
**State:** `IMPLEMENTATION/STRUCTURAL AUDIT IN PROGRESS / FREEZE NOT AUTHORIZED`

This checkpoint records the current v9 architecture after the analytic closure and before
final validation/performance qualification.  It is a workstream record, not a machine
certificate.

## Resolved architecture changes

1. The real-analysis content of `L-SECOND-DERIV`, `L-MIXED-DERIV`, and the analytic theorem
   in `L-MEAN-VALUE-ENCL` has been separated from implementation validation.
2. The old five-output prototype is not promoted; a guarded rigorous-only clean-room kernel
   candidate is used instead.
3. Mean-value adapter V2 exposes public rigorous endpoint `G` evaluation and the frozen
   seven-call mean-value path.
4. Runner V2 and checker V2 are independent source candidates.  The checker replays dps50
   decisions from fresh calls and verifies accepted leaves at fresh dps70.
5. Checkpoint durability no longer relies on overwriting latest JSON files.  Immutable
   hash-addressed payloads are published first and the append-only JSONL fsync is the sole
   checkpoint commit point.
6. Checkpoint bridge V2 binds canonical run context to each committed payload.
7. The first hard-coded rehearsal driver is superseded by a canonical shard-config driver
   architecture so the same source structure can support the one-shard `2^-20` rehearsal
   and later multi-shard connected sweeps.
8. The aggregate-verifier architecture now includes the multi-run analogue of S6:
   exact shared lambda endpoints plus positive-width adjacent root-window overlap.
9. The plan/config hash direction is one-way:

   ```text
   design/source/dependency -> plan -> config.
   ```

   The plan contains no config hash, eliminating the plan/config hash cycle.
10. The aggregate verifier is included in the common source map, avoiding an unpinned
    post-freeze verifier replacement.

## Current new artifacts

### Integrated mathematical/machine contract

- `v9_draft/design_contract_v9_integrated_candidate_v2.md`
- `v9_draft/MACHINE_LEMMAS_V9.md`

The v2 contract integrates analytic dependencies, canonical centers, exact split scores,
stop floors, child/record order, independent checking, transactional checkpointing,
config-driven shard execution, per-config freeze receipts, aggregate connection semantics,
validation corpus requirements, performance gates, and the no-byte-mutation freeze rule.

### Execution candidates

- `v9_candidate/prolate_F_derivatives_cleanroom_v9_candidate.py`
- `v9_candidate/adapter_v9_candidate_v2.py`
- `v9_candidate/runner_v9_candidate_v2.py`
- `v9_candidate/checker_v9_candidate_v2.py`
- `v9_candidate/checkpoint_v9_candidate.py`
- `v9_candidate/checkpoint_bridge_v9_candidate_v2.py`
- `v9_candidate/rehearsal_driver_v9_candidate_v3.py`
- `v9_candidate/aggregate_verifier_v9_candidate_v2.py`

Earlier driver/bridge/runner/checker candidates remain provenance only where superseded.

### Deterministic builders

- `v9_candidate/build_dependency_snapshot_v9.py`
- `v9_candidate/build_rehearsal_plan_config_v9.py`

The dependency builder packages all eight machine lemmas from exact proof/design/source
bytes.  The rehearsal builder consumes the resulting dependency snapshot and creates the
one-shard v2 plan first, then the v1 shard config referencing that plan hash.

### New structural controls/workflows

Controls have been added for:

- driver-v3 canonical config and freeze-receipt parsing;
- aggregate-v2 exact lambda coverage and positive root-window overlap;
- config/plan/freeze/evidence/source mutation rejection;
- deterministic dependency snapshot generation;
- deterministic dependency->plan->config generation;
- aggregate selected-evidence chain binding.

These controls do not promote the sources merely by existing.  Their final audit reports
must be inspected and bound into the qualification manifest.

## First rehearsal geometry remains unchanged

```text
lambda = [123731943/26214400, 118/25]
width  = 2^-20
root_r = [1/64, 11/256]
r_floor = lambda_floor = 2^-16.
```

For this shard, lambda refinement remains prohibited by the exact derived depth-cap rule;
`lambda d_cap=0`.  The rehearsal cannot silently shrink lambda after a failure.

## Multi-run connection rule

For adjacent closed lambda shards meeting at `lambda_*`, each successful fresh checker
proves one zero and strict decrease in its own root window at the shared endpoint.  The
aggregate plan requires positive-width overlap of those two windows.  Their union is then
connected and strictly decreasing, so the two unique zeros at `lambda_*` are the same
zero.  This is the run-to-run version of the established S6 connection rule and requires
no separate numerical root-equality test.

## Still not authorized

The following are **not** authorized by this checkpoint:

- a production tag;
- a freeze receipt;
- a full `2^-20` rehearsal;
- `CERTIFIED_LAMBDA_RANGE`;
- any theorem-sufficient global connected sweep;
- any paper-level completion claim.

Overall v9 remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```

## Remaining final gates

1. inspect and close all new driver-v3 / aggregate-v2 / builder audit reports against the
   exact current bytes;
2. resolve any source-map or schema mismatch exposed by those controls;
3. generate the candidate dependency snapshot and one-shard rehearsal plan/config from the
   final structural bytes;
4. complete the >=256-leaf independent validation corpus on those exact bytes;
5. run the three identical hosted qualification repetitions and performance gate;
6. build the canonical qualification manifest;
7. issue the canonical freeze receipt only if every referenced hash/report matches;
8. only then run the exact production `2^-20` rehearsal.

A failure at any gate remains fail-closed and returns to a successor candidate cycle rather
than being reclassified or silently narrowed.
