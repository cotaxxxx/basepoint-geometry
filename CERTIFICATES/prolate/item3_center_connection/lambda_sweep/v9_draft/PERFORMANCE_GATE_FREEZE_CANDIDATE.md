# Item 3 sweep v9 — performance gate freeze candidate

**Status:** `NORMATIVE CANDIDATE / QUALIFICATION PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This candidate resolves the open repetition-count and hosted-runner margin policy for the
first v9 production qualification.

Performance failure is never a mathematical counterexample and never authorizes a weaker
certificate claim.

## 1. Frozen qualification identity

All full-path qualification repetitions must use byte-identical:

```text
candidate kernel
adapter
runner
checker
config
design contract
logical dependency snapshot
shard plan
Python version
python-flint version
workflow source.
```

A source/config/dependency change restarts the qualification count from zero.

## 2. Full-path repetition count

Require exactly three successful, independent GitHub-hosted full-path qualification runs
for the approved `2^-20` rehearsal case.

A run counts only if it executes

```text
runner
fresh dps-50 checker partition replay
fresh dps-70 accepted-cell verification
final canonical evidence serialization
artifact preparation
```

and reaches mathematical completion without stop-floor exhaustion or other incomplete
terminal class.

Cancelled, failed, or incomplete attempts do not count toward the three.

## 3. Hard complete-path time gate

For every counted repetition,

```text
complete_path_wall_time < 3 hours.
```

The wall time is measured from the start of the approved runner computation through
completion of fresh checking and final artifact preparation. Environment setup/install
may be reported separately but must also fit within the six-hour hosted job limit.

No early extrapolation can produce PASS; it can only stop a clearly failing qualification.

## 4. Margin gate

For the three counted complete-path wall times, require both

```text
median <= 2 hours 30 minutes
maximum <= 2 hours 45 minutes.
```

Thus the observed worst complete path retains at least 15 minutes below the internal
three-hour gate and at least 3 hours 15 minutes below the six-hour hosted-job ceiling.

If either margin condition fails, status is

```text
PERFORMANCE_GATE_FAIL.
```

The mathematics remains unclassified by that failure.

## 5. Checkpoint overhead gate

Each repetition must also satisfy the independently frozen checkpoint requirement

```text
checkpoint_overhead_fraction <= 0.05.
```

Checkpoint time is included in complete-path wall time.

## 6. Stop-floor gate

For every counted repetition:

```text
stop_floor_incomplete_count = 0.
```

A run below every time threshold but with an uncertified required cell is

```text
MATHEMATICAL_COMPLETION_GATE_FAIL
```

and does not count.

## 7. Fresh-checker gate

Each counted repetition must satisfy:

```text
partition_replay_dps50 = PASS
accepted_cell_verification_dps70 = PASS
record_chain_match = PASS
final_partition_match = PASS.
```

Checker time may not be omitted from the three-hour complete-path total.

## 8. Component timing sample count

In addition to the three complete runs, the qualification report collects at least nine
measurements for each principal F-level operation on each approved representative input
class:

```text
F
F_r
F_lambda
F_rr
F_rlambda.
```

Report at minimum

```text
minimum
median
maximum
p90
result enclosure width/radius.
```

Component timings are diagnostic for attribution and future tuning. They do not replace
the three full-path repetitions.

## 9. Hardware/environment reporting

For each full run record at minimum:

```text
GitHub runner image/OS
CPU model when exposed
logical CPU count
reported memory when exposed
Python version
python-flint version
FLINT version
workflow run ID/attempt
source/config/dependency hashes.
```

Hardware variation is observed, not normalized away. The three-run margin gates are
applied to actual elapsed times on the provided hosted runners.

## 10. Early-stop rule

A qualification attempt may terminate early with

```text
PERFORMANCE_GATE_FAIL_EARLY
```

only if a pre-frozen conservative extrapolation proves that the three-hour hard gate
cannot be met.

The extrapolation formula must be part of the final workflow/config identity and cannot
be changed from observed data during the run.

Early stop never creates a mathematical verdict and never counts as a full-path repetition.

## 11. Broad-range nonclaim

Passing this qualification establishes performance eligibility only for the exact first
rehearsal plan. It does not certify that a broad connected range toward `a_c` can be
executed sequentially.

Broad-range execution remains governed by the multi-run shard design and the separately
chosen mathematical connected range.

## 12. Resolution status

If incorporated into the one-shot final v9 freeze, this candidate resolves:

```text
full-path repetition count
three-hour margin criterion
component timing repetition count
checkpoint-overhead interaction.
```

Actual performance PASS remains pending execution on final frozen bytes.
