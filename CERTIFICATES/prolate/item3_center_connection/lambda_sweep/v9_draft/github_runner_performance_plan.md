# v9 GitHub Hosted-Runner Performance Measurement Plan

**Status:** `DRAFT / SPEC_PENDING`  
**Issue:** #20  
**Measurement revision:** 2026-08-01  
**Purpose:** define measured performance parameters and qualification gates for the v9
kernel and mean-value enclosure path.

No workflow execution, production tag, approved-config change, or certification is
authorized by this plan.

## 1. Baseline evidence

GitHub Actions run `30609564841` reached the production runner after all gates passed and
was cancelled after approximately six hours. The runner had written only
`PILOT_ARTIFACT_REDERIVATION.json` before entering the long computation. This establishes
that the v8.1 raw interval path is not viable under the hosted-runner wall-clock limit for
the approved case.

Earlier diagnostic local measurements were:

| dps | approximate `evaluate_gr` time | enclosure radius |
|---:|---:|---:|
| 50 | 7.69 s | 0.005181 |
| 25 | 2.77 s | 0.005165 |
| 20 | 2.28 s | 0.005165 |

With approximately 20,000 required evaluations, dps 50 implied about 42.7 runner-hours
before fresh checker work. Even dps 20 implied about 12.7 runner-hours. Those values
motivated a structural reduction in evaluation count. They are not qualification data.

## 2. Independent prototype audit correction

The initial publication report stated eight commits and seven changed files under
`v9_prototype/`. Independent audit measured eleven commits and ten changed files:

```text
7 files under v9_prototype/
3 files under v9_draft/
```

The additional draft changes make the canonical-center rule normative and are
substantively acceptable. The report must nevertheless use the measured eleven-commit,
ten-file scope.

The v8.1 design blob, approved production config, and existing production kernel were
checked and remained unchanged.

## 3. Attribution rule

The first v9 qualification keeps:

```text
runner dps  = 50
checker dps = 70
```

No precision reduction, external long-running host, resume mechanism, or parallel
nondeterministic algorithm is mixed into the initial comparison. This isolates the effect
of:

- the new derivative kernel;
- r mean-value correction;
- λ mixed correction;
- deterministic adaptive subdivision.

A later precision study requires a separate config, SHA, approval, and report.

## 4. Qualification environment

Record at minimum:

```text
GitHub run ID and attempt
commit and tag/ref, when separately approved
runner image and image version
region if exposed
CPU model and logical count
available and peak memory
Python version
python-flint version and wheel hash
workflow source hash
kernel and adapter source hashes
config hash
all logical dependency hashes
```

The final workflow shall use pinned actions and a pinned Python setup. Variance across
hosted hardware must be measured rather than assumed away.

## 5. First rigorous derivative timings

The independent audit environment contained `python-flint`, allowing the previously
unexecuted rigorous point integrations to run. All five outputs returned finite values.
These results remain diagnostic and outside the proof path.

At dps 50, the measured point-evaluation costs were:

| output | measured time |
|---|---:|
| `F` | 2.33 s |
| `F_r` | 1.51 s |
| `F_λ` | 1.44 s |
| `F_rr` | 3.42 s |
| `F_rλ` | 3.32 s |

A seven-call mean-value cell therefore costs approximately:

```text
12.6 seconds per cell.
```

The hosted qualification must repeat these measurements and record cold, warm, median,
minimum, maximum, p90, and p95 values. The current local figures are planning inputs, not
hosted qualification results.

## 6. Mean-value component measurements

For every sampled `(I, Λ)`, the qualification shall record:

```text
radius(G_r center)
radius(r correction)
radius(λ correction)
radius(MV)
sup(MV)
raw G_r(I,Λ) radius, diagnostic only
```

Report the contribution ratios

```text
R_r = radius(r correction) / radius(MV)
R_λ = radius(λ correction) / radius(MV)
```

where defined.

### 6.1 Measured r-width behavior

At the left endpoint, identified as the difficult point:

| r width | result |
|---:|---|
| `2^-12` | not certified |
| `2^-13` | NEG, MV upper endpoint approximately `-0.00439` |
| `2^-14` | NEG with additional margin |

The earlier approximately two-cell estimate is withdrawn. Although the sampled true
`|G_rr|` is about 0.5, dependency inflation enlarges the interval enclosure of `G_rr`; at
r width `2^-12` it reaches approximately `±101`. The second-derivative enclosure
therefore also requires subdivision.

### 6.2 Measured λ-width behavior

With r width fixed at `2^-13` in the leftmost cell:

| λ width | MV upper endpoint | result |
|---:|---:|---|
| `2^-20` | `-0.00439` | NEG |
| `2^-16` | `-0.00415` | NEG |
| `2^-13` | `-0.00240` | NEG |
| `2^-10` | `+0.012` | not certified |

The λ first-order correction is not the controlling contribution. At λ width `2^-13`,
its radius is only approximately `1.7e-5`.

The controlling mechanism is the enlargement of `G_rr(I,Λ)` as the λ box widens, which
increases the r correction. The measured r-correction radii are:

```text
0.00308 -> 0.00332 -> 0.00505.
```

Thus r and λ certification limits are mathematically coupled. The config shall
nevertheless retain separate r and λ width and depth controls because refinement,
terminal reasons, and checker reproduction must be independently auditable by axis.

## 7. Measured boundary, operating range, and stop floor

The performance contract must distinguish three different quantities:

| quantity | r | λ |
|---|---:|---:|
| measured certification boundary | `2^-13` | `2^-13` |
| expected operating widths | `2^-11` through `2^-13` | `2^-11` through `2^-13` |
| recommended stop floor | `2^-16` | `2^-16` |

`2^-13` is the measured width at which the difficult sampled cell still certifies. It is
not the stop floor.

Using the measured boundary as the stop floor would leave effectively no reserve for a
slightly worse unsampled point. The stop floor is therefore:

```text
min_r_width      = 2^-16
min_lambda_width = 2^-16
```

Under adaptive refinement, lowering the floor from `2^-13` to `2^-16` does not multiply
the whole tree by eight. Only cells reaching the difficult left-end region continue to
split. The expected increase is tens of cells and a few minutes.

A cell that reaches a stop floor without a strict NEG enclosure terminates
`INCOMPLETE`. Stop-floor exhaustion is an independent failure condition and is not a
performance-gate pass even when the run finishes within three hours.

The r/λ width decision is materially resolved by these measurements and is ready for
formal adoption in the v9 contract. Overall v9 status remains `SPEC_PENDING` until the
other contract decisions are frozen.

## 8. Algorithm-level estimate

The updated measured planning estimates are:

| path | cells | approximate runner time |
|---|---:|---:|
| uniform width `2^-13` | 224 | 47.0 min |
| adaptive refinement | 150 | 31.5 min |
| adaptive with local floor reserve | approximately 150 plus tens | small additional minutes |

Compared with the approximately 9,000-cell v8.1 path, this is roughly a 40-fold reduction
in cell count.

The qualification path shall report:

```text
λ boxes created/completed
r cells created/accepted
r and λ split counts
maximum r and λ depth
attempt count
runner kernel calls by derivative
checker kernel calls by derivative
runner wall time
checker wall time
serialization/artifact wall time
checkpoint wall time
peak memory
terminal class
stop-floor exhaustion count and reason
```

The checker must perform fresh recomputation. A runner-only benchmark is informative but
cannot pass the complete-path gate.

## 9. Complete-path time gate

### 9.1 Hard gate

The complete approved qualification case must satisfy:

```text
runner
+ fresh checker
+ final serialization
+ artifact preparation
< 3 hours.
```

The measured planning estimate for the complete path is:

```text
1.5 to 2.3 hours.
```

The stop-floor change to `2^-16` is expected to leave this range substantially unchanged.
It adds reserve against unsampled difficult cells rather than materially changing the
whole-tree cost.

### 9.2 Independent mathematical completion gate

Time eligibility and mathematical completion are separate predicates:

```text
TIME_GATE_PASS
AND
NO_STOP_FLOOR_INCOMPLETE
AND
FRESH_CHECKER_PASS
```

are all required. A run that finishes quickly but cannot certify every required cell is
not eligible.

### 9.3 Margin analysis

Report at least median and upper-tail estimates across repeated runs or justified
component measurements. A single run below three hours is insufficient if variance could
plausibly approach the six-hour hosted limit.

The exact repetition count and margin criterion remain open. These are among the
remaining SPEC_PENDING decisions.

### 9.4 Early stop

Stop qualification early and report `PERFORMANCE_GATE_FAIL` if a frozen conservative
extrapolation from completed attempts exceeds three hours. The extrapolation formula must
be approved before the run and may not authorize a mathematical verdict.

## 10. Checkpoint overhead and cancellation

Test candidate checkpoint cadences based on:

```text
time
kernel-call count
box completion
combined cadence
```

Measure:

```text
bytes written
serialization time
flush/fsync time
total overhead percentage
largest checkpoint
artifact upload size and time
last recoverable attempt after injected cancellation
```

The final policy must freeze:

- whether file and directory `fsync` are required;
- checkpoint frequency;
- maximum overhead;
- checkpoint and partial-evidence schemas.

Before any production authorization, a qualification workflow shall intentionally stop
the runner at controlled times. It must demonstrate that `if: always()` uploads the last
complete atomic checkpoint and that:

- checkpoint JSON parses canonically;
- hashes match;
- no partial verdict is present;
- the last completed attempt is internally consistent;
- truncated temporary files are ignored;
- shell post-processing may be absent without corrupting runner evidence.

This test does not use or move a production tag.

## 11. Broad-range relevance

The immediate target is a single λ box of width `2^-20`. The measured performance plan
supports that target.

If practical λ boxes must be no wider than `2^-13`, covering a λ range of width `2^-4`
requires:

```text
2^(-4) / 2^(-13) = 512 λ boxes.
```

At approximately 30 to 47 runner minutes per box, a sequential broad sweep toward `a_c`
is not practical. Broad-range work therefore requires a separate parallelization policy
or a different broad-range enclosure design.

The performance report must distinguish:

```text
current single-box qualification
broad λ-sweep projection
broad λ-sweep measured diagnostic
```

No broad-range projection is a certificate or run authorization. The immediate
width-`2^-20` single-box goal is unaffected.

## 12. Comparison table

The final report shall include at least:

| path | dps | λ width | r cells | λ boxes | runner calls | checker calls | runner time | checker time | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v8.1 diagnostic estimate | 50/70 | `2^-20` | ~9000 | 1 | estimated | estimated | >6 h | not reached | incomplete |
| v9 measured uniform | 50/70 | `2^-20` | ~224 | 1 | measured/projected | fresh | ~47 min | projected | 1.5-2.3 h complete path |
| v9 measured adaptive | 50/70 | `2^-20` | ~150 plus reserve | 1 | measured/projected | fresh | ~31-47 min | projected | 1.5-2.3 h complete path |

The final qualification must replace projections with hosted measurements and disclose
all extrapolation formulas.

## 13. Qualification artifacts

A future qualification package shall contain at least:

```text
PERFORMANCE_ENVIRONMENT.json
KERNEL_MICROBENCHMARK.jsonl
MEAN_VALUE_COMPONENTS.jsonl
ALGORITHM_PERFORMANCE.json
CHECKPOINT_OVERHEAD.json
CANCELLATION_RECOVERY.json
PERFORMANCE_GATE_REPORT.json
PERFORMANCE.log
```

All normative reports use canonical bytes and source/config hashes.

## 14. Remaining performance-related SPEC_PENDING decisions

The r/λ minimum-width decision is materially resolved. The remaining performance-related
open decisions are:

1. final split-score upper-bound form;
2. normative tie-break;
3. checkpoint `fsync` policy;
4. checkpoint frequency and overhead limit;
5. checkpoint and partial-evidence schema;
6. exact three-hour margin criterion;
7. benchmark repetition count;
8. exact definition of “224-leaf-equivalent or stronger” for the five-output kernel.

The analytic contract separately retains the open integration-variable, integrand, and
differentiation-under-integral obligations.

## 15. Exclusions

This plan does not authorize:

- a workflow run;
- a production tag;
- an approved config change;
- dps reduction;
- an external unlimited-time host;
- parallel nondeterministic evaluation;
- a broad-range production sweep;
- kernel approval;
- certification.

The next phase is resolution of the remaining SPEC_PENDING decisions followed by explicit
v9 contract freeze.