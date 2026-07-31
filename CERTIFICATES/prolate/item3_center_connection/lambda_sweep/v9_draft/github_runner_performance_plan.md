# v9 GitHub Hosted-Runner Performance Measurement Plan

**Status:** `DRAFT / SPEC_PENDING`  
**Issue:** #20  
**Purpose:** define measurements and gates for a future v9 kernel and enclosure path.
No workflow execution is authorized by this plan.

## 1. Baseline evidence

GitHub Actions run `30609564841` reached the production runner after all gates passed
and was cancelled after approximately six hours. The runner had written only
`PILOT_ARTIFACT_REDERIVATION.json` before entering the long computation. This establishes
that the current raw interval path is not viable under the hosted-runner wall-clock
limit for the approved case.

Diagnostic local measurements supplied for planning:

| dps | approximate `evaluate_gr` time | enclosure radius |
|---:|---:|---:|
| 50 | 7.69 s | 0.005181 |
| 25 | 2.77 s | 0.005165 |
| 20 | 2.28 s | 0.005165 |

With about 20,000 required evaluations, dps 50 implies roughly 42.7 runner-hours before
fresh checker work. dps 20 would still imply roughly 12.7 runner-hours. These estimates
motivate a structural reduction in evaluation count. They are not qualification data.

## 2. Attribution rule

The first v9 qualification keeps:

```text
runner dps  = 50
checker dps = 70
```

No precision reduction, external long-running host, resume mechanism, or parallel
nondeterministic algorithm is mixed into the initial comparison. This isolates the
effect of:

- the new derivative kernel;
- r mean-value correction;
- λ mixed correction;
- changed deterministic subdivision.

A later precision study requires a separate config, SHA, approval, and report.

## 3. Qualification environment

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

## 4. Microbenchmark matrix

Measure each published kernel output separately:

```text
F
F_r
F_λ
F_rr
F_rλ
```

Also measure any approved co-evaluation interface. For each operation record:

```text
input box ID
dps
cold-start time
warm times
median
minimum
maximum
p90
p95
result enclosure width/radius
kernel-call counter delta
peak memory delta when measurable
```

Use representative inputs covering:

- canonical center points;
- the current inherited r-window;
- narrow and broad r cells;
- λ width `2^-20`;
- broader diagnostic λ widths including `2^-16` and `2^-12`;
- difficult integration subdomains identified by validation;
- finite and subdivision-triggering boxes.

The repetition count is unresolved; it must be large enough to characterize hosted
variance without consuming the full qualification budget.

## 5. Mean-value component benchmark

For every sampled `(I, Λ)`, record:

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

where defined, and the scaling of the λ correction with `width(Λ)`.

The qualification must test whether the empirical `≈2048 * width(Λ)` raw inflation has
been replaced by a certified mixed-derivative correction narrow enough for the intended
box widths.

## 6. Algorithm-level benchmark

Run a non-production qualification path that reports:

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
```

The checker must perform fresh recomputation. A runner-only benchmark is informative but
cannot pass the production eligibility gate.

## 7. Checkpoint overhead test

Test at several candidate cadences:

```text
time based
kernel-call-count based
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

The final maximum overhead is an open decision. A provisional engineering target is
less than five percent of total wall time, but this is not yet normative.

## 8. Cancellation test

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

## 9. Time gates

### Hard eligibility gate

The complete approved qualification case must satisfy:

```text
runner
+ fresh checker
+ final serialization
+ artifact preparation
< 3 hours.
```

### Margin analysis

Report at least median and upper-tail estimates across repeated runs or justified
component measurements. A single run below three hours is insufficient if variance
could plausibly approach the six-hour host limit.

A provisional planning target is `<= 2 h 30 min` for the median complete path, leaving
room for hosted variance and upload. The exact margin criterion remains open.

### Early stop

Stop qualification early and report `PERFORMANCE_GATE_FAIL` if a conservative
extrapolation from completed attempts exceeds three hours. The extrapolation formula
must be frozen before the run and may not authorize a mathematical verdict.

## 10. Broad-sweep relevance

The current width-`2^-20` box is necessary but not sufficient. Performance reporting
shall include diagnostic scaling projections for broader λ widths and actual
non-production micro/macro cases where permitted.

The report must distinguish:

```text
current single-box qualification
broad λ-sweep projection
broad λ-sweep measured diagnostic
```

No projection is a certificate or run authorization.

## 11. Comparison table

The final report shall include a table with at least:

| path | dps | λ width | r cells | λ boxes | runner calls | checker calls | runner time | checker time | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v8.1 diagnostic estimate | 50/70 | 2^-20 | ~9000 | 1 | estimated | estimated | >6 h | not reached | incomplete |
| v9 r-only diagnostic | 50/70 | ... | ... | ... | ... | ... | ... | ... | ... |
| v9 r+λ mean-value | 50/70 | ... | ... | ... | ... | ... | ... | ... | ... |

The r-only row is diagnostic and exists to quantify the mixed-partial benefit; it is not
a candidate production design unless separately approved.

## 12. Qualification artifacts

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

## 13. Exclusions

This plan does not authorize:

- a workflow run;
- a production tag;
- an approved config change;
- dps reduction;
- an external unlimited-time host;
- parallel nondeterministic evaluation;
- kernel implementation;
- certification.

## 14. Open performance decisions

1. benchmark repetition count;
2. exact representative box corpus;
3. co-evaluation policy;
4. checkpoint cadence and overhead limit;
5. early-extrapolation formula;
6. peak-memory measurement method;
7. hosted-runner variance requirement;
8. exact three-hour margin criterion;
9. whether broad-width cases are measured in one run or separate audited runs;
10. maximum qualification artifact size.

These decisions require explicit approval before measurement execution.
