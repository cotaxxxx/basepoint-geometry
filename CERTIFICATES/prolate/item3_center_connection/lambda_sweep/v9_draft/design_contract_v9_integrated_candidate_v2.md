# Item 3 lambda sweep v9 — Integrated Design Contract Candidate v2

**Status:** `INTEGRATED_FREEZE_CANDIDATE_V2 / NOT FROZEN / NO RUN AUTHORIZATION`  
**Date:** 2026-08-08

This document supersedes the normative content of the earlier integrated candidate and,
where applicable, incorporates the later no-byte-mutation freeze policy and transactional
checkpoint correction.  Earlier documents remain provenance but are non-normative wherever
they conflict with this v2 candidate.

The contract is intentionally independent of final source SHA values.  Final byte
identities are bound by the canonical shard plan, per-shard config, qualification manifest
and freeze receipt after all implementation sources are stable.  This avoids circular hash
dependencies and avoids rewriting the design contract after qualification.

Nothing in this document authorizes a workflow run, tag, production certificate or
`CERTIFIED_LAMBDA_RANGE`.

---

## 1. Scope and machine conclusion

The v9 machine proves, on one or more exact closed lambda shards, a unique zero of

```text
G(r,lambda) = F(r,lambda)/r
```

inside a certified positive r window by the following closed-box obligations:

```text
G(r_lo,Lambda) > 0
G(r_hi,Lambda) < 0
G_r(r,Lambda)  < 0 throughout the r window.
```

For multiple adjacent lambda shards, the aggregate verifier additionally proves exact
lambda coverage and run-to-run root identity at every shared lambda endpoint.

The machine conclusion does **not** itself assert:

- comparison with `a_c`;
- local normal-form matching;
- analyticity of the root branch;
- asymptotic limits;
- any lambda outside the exact aggregate plan;
- completion of the frozen 16-stage paper theorem chain.

Those remain separate paper-level dependencies.

---

## 2. First production rehearsal

The first exact rehearsal range is

```text
R_rehearsal = [123731943/26214400, 118/25]
width       = 2^-20.
```

The first rehearsal plan contains exactly one shard:

```text
shard_id    = S00000000
shard_index = 0
lambda_box  = R_rehearsal
root_r      = [1/64, 11/256].
```

This range is an end-to-end production rehearsal only.  It is not the theorem-sufficient
connected range toward `a_c`.

The rehearsal must use the same plan/config/source/checkpoint/checker/aggregate schemas and
the same source architecture as later multi-shard production.  The later plan may change
only canonical data (shard geometry/config identities) and may not require a new execution
algorithm merely to support multiple shards.

---

## 3. Fixed analytic facts

The fixed integration domain is

```text
theta in [0,pi/2],
phi   in [0,pi].
```

On compact machine rectangles satisfying

```text
0 < r < 1,
lambda >= 1,
```

the accepted analytic proof establishes uniform denominator separation, including

```text
q >= (1-r)^2 > 0,
W >= 1-r > 0,
w^2 >= 1.
```

An exact square-sum identity yields

```text
0 < gamma <= 1.
```

For `h(c)=acos(c)^2`, the endpoint `c=1` is removable through third order and

```text
h'(1)   = -2,
h''(1)  = 2/3,
h'''(1) = -8/15.
```

The accepted analytic package establishes the exact F-level first/second/mixed derivative
integrands, differentiation under the integral, mixed differentiation commutation, the G
quotient identities and the two-variable mean-value inclusion.

These facts are logical dependencies.  They do not authorize machine source unless the
source is separately validated and hash-bound.

---

## 4. Required logical dependencies

The final dependency snapshot contains canonical entries at least for

```text
L-CONT
L-DERIV
L-ENCL
L-IVT
L-SIGN
L-SECOND-DERIV
L-MIXED-DERIV
L-MEAN-VALUE-ENCL.
```

The three v9 additions mean:

### `L-SECOND-DERIV`

The exact analytic `F_rr` formula, differentiation-under-integral justification, exact
`G_rr` quotient identity and validated interval-source enclosure.

### `L-MIXED-DERIV`

The exact analytic `F_lambda` and `F_rlambda` formulas, mixed-differentiation
justification, exact `G_rlambda` identity and validated interval-source enclosure.

### `L-MEAN-VALUE-ENCL`

The exact two-variable inclusion, canonical centers, dual quotient associations, exact
split scores, total axis order, strict-sign rule and fail-closed refinement semantics.

A dependency entry has schema

```text
ITEM3_SWEEP_V9_DEPENDENCY_ENTRY_V1
```

and contains no self-hash.  Its identity is the SHA-256 of its exact canonical bytes.
The dependency snapshot is generated only after final proof/source/design bytes are known.

---

## 5. Canonical coordinate rules

Lambda coordinates are canonical reduced rationals.  r coordinates are canonical exact
rationals/dyadics under the final schema.  Every normative comparison is exact.

For a cell

```text
I      = [r_lo,r_hi]
Lambda = [lambda_lo,lambda_hi]
```

the canonical center is

```text
r0      = (r_lo+r_hi)/2
lambda0 = (lambda_lo+lambda_hi)/2
```

in exact arithmetic.  Runner and checker independently rederive both centers.
Floating/decimal/ad hoc interior centers are prohibited.

---

## 6. Validated five-output kernel interface

The execution adapter is source-bound to a clean-room kernel exposing exactly

```text
F
F_r
F_lambda
F_rr
F_rlambda
```

as rigorous interval calls.

The kernel must:

- propagate nested `acb.integral` analyticity by logical OR;
- forward `analytic=` to both relevant square roots;
- fail closed when the Gauss `2F1` principal-cut condition can be met in an analytic
  callback;
- enforce complete input balls inside `0<r<1`, `lambda>=1`;
- reject non-finite validated integral output;
- expose no diagnostic float path through the rigorous interface.

Final kernel bytes are pinned by the source map; any change invalidates dependent
qualification/freeze evidence.

---

## 7. Exact G quotient associations

For positive r,

```text
G_r       = F_r/r - F/r^2
G_rr      = F_rr/r - 2 F_r/r^2 + 2 F/r^3
G_rlambda = F_rlambda/r - F_lambda/r^2.
```

For each quantity the adapter computes both the direct association and the common-
denominator association under frozen operation order.

Expression IDs are

```text
ITEM3_V9_GR_DUAL_ASSOC_V1
ITEM3_V9_GRR_DUAL_ASSOC_V1
ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1.
```

Combination rule:

```text
both finite + overlap -> exact interval intersection
both finite + disjoint -> fatal source inconsistency
one finite             -> use that finite enclosure
neither finite         -> NONFINITE, then deterministic refinement.
```

Approximate width/radius comparison never chooses the association.

---

## 8. Two-variable mean-value enclosure

Set `H=G_r`.  For the canonical center,

```text
H(I,Lambda)
 subset
 H(r0,lambda0)
 + G_rr(I,Lambda)*(I-r0)
 + G_rlambda(I,Lambda)*(Lambda-lambda0).
```

The adapter evaluates

```text
MV = FINAL(G_r center)
   + FINAL(G_rr box)*(I-r0)
   + FINAL(G_rlambda box)*(Lambda-lambda0).
```

A leaf is strict `NEG` iff every required object is finite and

```text
sup(MV) < 0.
```

`sup(MV)=0`, a non-finite object, or an interval crossing zero is not a mathematical
counterexample.  It triggers deterministic refinement or an `INCOMPLETE` stop-floor
result.

The current frozen call decomposition per mean-value attempt is seven F-level calls:

```text
F          2
F_r        2
F_lambda   1
F_rr       1
F_rlambda  1.
```

---

## 9. Split scores and axis order

At dps 50,

```text
S_r      = radius(I)      * absmax(FINAL(G_rr(I,Lambda)))
S_lambda = radius(Lambda) * absmax(FINAL(G_rlambda(I,Lambda))).
```

Each score is an exact nonnegative rational/dyadic quantity or `NONFINITE`.

Among splittable axes:

1. no splittable axis -> `INCOMPLETE`;
2. one splittable axis -> choose it;
3. `NONFINITE` outranks finite;
4. larger exact finite score wins;
5. exact tie -> r.

Double-nonfinite tie therefore selects r.  dps70, wall clock, host load and execution
completion order cannot alter the tree.

---

## 10. Stop floors and derived depth caps

The v9 floors are

```text
r_floor      = 2^-16
lambda_floor = 2^-16.
```

A split is allowed only when both children on the selected axis have width at least the
axis floor.

For each root interval J and floor f define the exact derived cap

```text
d_cap(J,f) = max {d >= 0 : width(J)/2^d >= f},
```

with cap zero if root width is below the floor.  No floating logarithm or independent
arbitrary max-depth constant is used.

For the first rehearsal shard,

```text
lambda width = 2^-20 < 2^-16 -> lambda d_cap = 0
root_r = [1/64,11/256]       -> r d_cap = 10.
```

Thus the rehearsal cannot silently repair a failure by narrowing lambda.  Failure at the
approved lambda root remains `INCOMPLETE`/`NOT_CERTIFIED`.

---

## 11. Child, stack and record order

Each node has a structural path ID.

For an r split:

```text
R0 = lower-r child
R1 = upper-r child
processing order R0 then R1
LIFO push order R1 then R0.
```

For a lambda split:

```text
L0 = lower-lambda child
L1 = upper-lambda child
processing order L1 then L0
LIFO push order L0 then L1.
```

This preserves the established lower-r-first / upper-lambda-first contract.

Execution attempt records use increasing activation index.  Accepted mathematical leaves
are separately serialized in exact geometric order:

```text
lambda_hi descending,
lambda_lo descending,
r_lo ascending,
r_hi ascending,
path_id only as impossible-tie guard.
```

Two distinct accepted leaves with the same exact rectangle are an internal error.

---

## 12. Runner result semantics

A production runner shard first evaluates the endpoint signs on the entire preapproved
closed lambda shard:

```text
G(root_r.lo,Lambda) > 0
G(root_r.hi,Lambda) < 0.
```

If either fails, the shard is `INCOMPLETE`; the lambda range is not shrunk.

It then partitions the two-variable derivative domain until every leaf is strict NEG or a
fail-closed stop/budget condition is reached.

Only complete strict-NEG coverage may produce the internal runner word

```text
COMPLETE_CANDIDATE.
```

This word is not independently citable and is not `CERTIFIED_LAMBDA_RANGE`.

---

## 13. Independent checker semantics

The checker must not import runner decision source and must instantiate distinct fresh
adapter/kernel instances.

At dps50 it independently recomputes:

- endpoint signs and runner endpoint evidence identity;
- canonical centers;
- every mean-value enclosure;
- every exact split score;
- every axis decision;
- path IDs, depths and LIFO order;
- accepted leaf partition.

It rejects any score/axis/path/leaf mutation.

At dps70 it performs fresh endpoint evaluation and fresh mean-value evaluation on every
accepted dps50 leaf.  dps70 may reject but may not change the partition.

The checker records every verified leaf's strict negative upper endpoint.

Only a complete dps50 replay plus dps70 verification produces

```text
PASS_CANDIDATE.
```

---

## 14. Transactional checkpoint architecture

Checkpoint evidence is provenance only and has no resume or theorem semantics.

Each checkpoint publishes immutable canonical payloads to

```text
checkpoint_payloads/progress/<sha256>.json
checkpoint_payloads/partial/<sha256>.json.
```

A hash-addressed payload is never overwritten.  Same-hash preexistence is accepted only
if bytes are identical.

After both immutable payloads are durable, one canonical line is appended to

```text
SWEEP_PROGRESS.jsonl.
```

The JSONL line is flushed and fsynced; **that fsync is the sole checkpoint commit point**.
Each line contains the previous committed line hash and both payload hashes.  The line hash
is SHA-256 over the exact canonical line bytes including the final LF.

Latest named JSON files are mirrors only; they are not durability roots.

Recovery:

- ignores only an incomplete non-LF trailing suffix;
- rejects malformed complete lines;
- verifies sequence and previous-line hash chain;
- verifies both immutable payload hashes;
- verifies the frontier digest;
- never destroys an older committed payload during a later interrupted checkpoint.

Checkpoint request occurs only after a completed attempt when any of:

```text
>=120 monotonic seconds since durable checkpoint
>=32 completed attempts since durable checkpoint
shard structural-completion boundary
controlled shutdown hook.
```

No checkpoint occurs mid-kernel-call.  Each replacement payload is at most 32 MiB.
Checkpoint timing/count/hashes are excluded from final mathematical proof hashes.

---

## 15. Checkpoint run-context binding

Every progress and partial payload includes one canonical `run_context` binding at least

```text
config_sha256
aggregate_plan_sha256
design_sha256
dependency_snapshot_sha256
source_sha256
shard_id
shard_index
authorization
freeze_receipt_sha256 (production; null in qualification).
```

This prevents detached checkpoint provenance from being silently attached to another shard
plan/config/source identity.

---

## 16. Source map

Every v9 shard config and freeze receipt carries exactly one source map with keys

```text
kernel
adapter
runner
checker
checkpoint
bridge
driver
aggregate_verifier.
```

The shard driver directly verifies the first seven identities relevant to shard execution,
including its own file hash.  It requires a syntactically valid aggregate-verifier hash but
does not import that verifier.

The aggregate verifier independently checks

```text
source_sha256.aggregate_verifier == SHA256(its own exact source bytes)
```

and validates the common source map in plan, configs and freeze receipts.

Thus neither driver nor aggregate verifier needs to embed the other's source hash in its
own source code; the canonical config/plan removes the circular hash dependency.

---

## 17. Canonical shard plan v2

The aggregate plan schema is

```text
ITEM3_SWEEP_V9_SHARD_PLAN_V2.
```

It contains:

```text
total_lambda_range
shard_count
ordered_shards
source_sha256
design_sha256
dependency_snapshot_sha256
policy.
```

Each ordered shard contains exactly

```text
shard_index
shard_id
lambda_box
root_r.
```

The plan contains **no config SHA values**.  This is deliberate: configs bind the plan,
not vice versa, avoiding a plan<->config hash cycle.

Shard index zero is the uppermost lambda shard.  Adjacent shards require exact canonical
shared lambda endpoint bytes.  The exact shard union must equal the total plan range with
no gap and no positive-width lambda overlap.

Adjacent root-r windows must have positive-width overlap.

---

## 18. Canonical per-shard run config

The run config schema is

```text
ITEM3_SWEEP_V9_SHARD_RUN_CONFIG_V1.
```

A config binds:

```text
aggregate_plan_sha256
design_sha256
dependency_snapshot_sha256
source_sha256
shard_id
shard_index
root_r
lambda_box
r_floor
lambda_floor
dps_control
dps_verify
integration policy
activation budget
checkpoint policy
required freeze receipt schema.
```

The config must be canonical JSON bytes ending in exactly one LF and contains no binary
floating-point normative value.

It must match the corresponding shard geometry and common policy in the aggregate plan.

The first rehearsal uses this exact same config schema with one shard.  Later multi-shard
plans use the same source and schema with different canonical shard data.

---

## 19. Qualification and production modes

The same source and same shard config can run in two authorization modes.

### Qualification

```text
--qualification-mode
```

No freeze receipt is accepted.  Mathematical success may produce only

```text
QUALIFICATION_PASS_CANDIDATE.
```

This mode exists for independent validation/performance qualification on the exact bytes
that will later be frozen.

### Production

Qualification flag absent; an exact matching canonical freeze receipt is mandatory.
Mathematical success may produce only

```text
SHARD_PASS_CANDIDATE.
```

The runner/checker mathematical path is identical between modes.  Authorization metadata
does not alter split decisions or numerical evaluation.

---

## 20. Freeze receipt

The freeze receipt schema is

```text
ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1.
```

A successful receipt binds at least

```text
aggregate_plan_sha256
config_sha256
design_sha256
dependency_snapshot_sha256
source_sha256
qualification_manifest_sha256
validation_report_sha256
performance_gate_report_sha256
freeze_verdict = V9_FROZEN_APPROVED
nonclaims.
```

It contains no self-hash; its identity is the SHA-256 of exact canonical receipt bytes.

The qualified design/source/config files are **not edited after qualification** merely to
change textual status to `FROZEN`.  Frozen identity is

```text
immutable qualified bytes + canonical freeze receipt.
```

A multi-shard production plan may use one receipt per shard config.  Each receipt must bind
the same plan/design/dependency/source map and its own exact config hash.  This avoids a
single-receipt/config-hash ambiguity.

---

## 21. Production shard evidence

The source-bound driver writes one canonical shard evidence object with schema

```text
ITEM3_SWEEP_V9_SHARD_EVIDENCE_CANDIDATE_V2.
```

It includes:

- authorization mode;
- plan/config/design/dependency/freeze identities;
- shard geometry and identity;
- source pre/post-import binding evidence;
- runner result;
- checker report including dps70 leaf bounds;
- explicit errors if any.

Checkpoint history is deliberately excluded from this mathematical evidence object. The driver writes a separate canonical `ITEM3_SWEEP_V9_SHARD_PROVENANCE_V1` object bound to the exact shard-evidence SHA-256. That provenance object records the committed-checkpoint count/tip and ledger identity, while the aggregate verifier independently revalidates the canonical JSONL chain and immutable payload hashes. No checkpoint count, checkpoint hash, checkpoint timing value, provenance-object hash, or ledger hash enters `shard_evidence_sha256` or the selected-shard mathematical chain.

Only

```text
status = SHARD_PASS_CANDIDATE
authorization = FROZEN_PRODUCTION
runner terminal = COMPLETE_CANDIDATE
checker status  = PASS_CANDIDATE
no runner/checker error
```

is eligible for aggregate verification.

Qualification evidence is categorically ineligible for production aggregation.

---

## 22. Multi-run aggregate verifier v2

The aggregate verifier is stdlib-only and independently checks:

1. canonical plan bytes and verifier self-hash;
2. exact total lambda coverage;
3. canonical shared endpoint byte identity;
4. positive-width adjacent root-window overlap;
5. every per-shard config against plan/policy/source/design/dependency;
6. every per-shard freeze receipt against its config and common identities;
7. every selected production shard evidence object against plan/config/receipt;
8. runner V2 complete status and nonempty accepted partition;
9. checker V2 PASS, equal dps50/dps70 leaf counts, and strict-negative dps70 bounds;
10. source pre/post-import identities for adapter/runner/checker/checkpoint/bridge and all
    kernel imports;
11. a separate shard-provenance object bound to the selected shard-evidence hash, with a nonempty checkpoint ledger whose canonical line chain, immutable payload hashes, frontier digests and run-context bindings are independently reverified;
12. selected-evidence SHA chain in exact mathematical shard order.

The selected chain uses domain bytes

```text
ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V2\0
```

followed by raw32 plan hash, uint64 big-endian shard index, prior raw32 chain value for
`i>0`, and raw32 selected evidence hash.

Workflow completion order never enters this chain.

---

## 23. Run-to-run root connection theorem

Let adjacent planned shards be

```text
Lambda_i     = [lambda_*, lambda_hi]
Lambda_{i+1} = [lambda_lo, lambda_*]
```

with root windows `W_i`, `W_{i+1}` having positive-width overlap.

A successful fresh checker for shard i proves at the closed endpoint `lambda_*`:

- one zero of G exists in `W_i`;
- `G_r<0` throughout `W_i`.

The adjacent successful checker proves the analogous facts in `W_{i+1}`.

Since the windows overlap with positive width, their union is an interval.  `G_r<0` on
both windows implies strict decrease on the connected union.  Therefore G has at most one
zero on the union.  The two shard zeros at `lambda_*` must be the same zero.

No extra singleton root finder, Newton step or numerical endpoint matching is required.
The aggregate verifier records the exact shared lambda and overlap interval for every
adjacency.

This theorem is the multi-run/root-window form of the established S6 connection rule.

---

## 24. Aggregate conclusion

Only after all shard/config/receipt/evidence/adjacency/source checks pass may the aggregate
verifier emit

```text
schema = ITEM3_SWEEP_V9_AGGREGATE_VERDICT_V2
status = CERTIFIED_LAMBDA_RANGE.
```

The verdict records:

```text
covered lambda range
aggregate plan hash
design/dependency/source identities
per-shard config hashes
per-shard freeze receipt hashes
selected shard evidence hashes
selected-chain tip
exact adjacency connection records
machine conclusion and nonclaims.
```

A one-shard rehearsal uses the same aggregate schema with an empty adjacency list.

---

## 25. Fail-closed rehearsal rule

Any rehearsal/source/checker/schema/checkpoint/aggregate failure leaves status

```text
NOT_CERTIFIED
```

or `INCOMPLETE` as applicable.

Prohibited recovery includes:

- dropping a failed shard;
- shrinking the target after execution;
- promoting a passing prefix;
- changing a floor or precision after seeing the result;
- reclassifying a source/schema/infrastructure failure as mathematical success;
- citing diagnostic/smoke/reference output as a proof node.

A failed rehearsal may trigger a new contract/source candidate cycle, but does not mutate
its own verdict.

---

## 26. Independent validation corpus

Before freeze, the exact final byte set must pass at least 256 unique prepublished control
leaves with category floors

```text
A analytic/source mapping          32
B domain/branch/angle              32
C five-output kernel               80
D quotient/mean-value adapter      32
E deterministic refinement        32
F evidence/checkpoint/cancellation 24
G multi-run/aggregate              16
H independence/source identity      8
TOTAL                              256.
```

A leaf has one primary category and fixed expected result before execution.  Cosmetic
duplicates count once.

The corpus must attack, among other things:

- analytic OR->AND;
- missing `2F1` guard;
- quotient coefficient/order mutation;
- `sup(MV)=0`;
- exact tie-break mutation;
- FIFO/child-order mutation;
- floor/depth mutation;
- runner evidence score/axis/endpoint mutation;
- checker adapter reuse;
- dps70 failure;
- malformed complete checkpoint line;
- orphan/missing payloads and stale mirrors;
- missing run-context binding;
- aggregate verifier self-hash mutation;
- lambda gap/shared-endpoint mutation;
- loss of root-window overlap;
- config/plan/freeze mismatch;
- qualification evidence used as production;
- stale selected-chain tip;
- source path/hash/origin substitution.

The historical 224-leaf corpus is provenance only and is not inherited.

---

## 27. Performance qualification

Each distinct shard config to receive a freeze receipt must satisfy exactly three complete
GitHub-hosted qualification repetitions on byte-identical

```text
design
kernel
adapter
runner
checker
checkpoint
bridge
driver
aggregate verifier
plan
config
dependency snapshot
validation source/workflow
qualification workflow/environment.
```

Each repetition includes runner, fresh dps50 replay checker, fresh dps70 accepted-leaf
checker, canonical evidence serialization and artifact preparation.

Requirements:

```text
every complete-path wall time < 3h
median of three             <= 2h30
maximum of three            <= 2h45
checkpoint overhead          <= 5% each run
stop-floor incomplete count  = 0 each run.
```

Cancelled/failed/incomplete runs do not count.  Performance failure is not a mathematical
counterexample.

Collect at least nine component timings per approved input class for each F-level
operation with min/median/max/p90 and enclosure size.

For the first one-shard rehearsal, qualification establishes eligibility only for that
exact rehearsal config.  It does not estimate or authorize the later theorem-sufficient
connected sweep.

---

## 28. Qualification manifest and no-byte-mutation freeze

A canonical qualification manifest records the exact hashes of all proof-relevant files
and PASS reports used by the freeze decision.

Once the first counted final validation/performance run begins, a proof-relevant byte
change restarts every dependent gate.  Do not edit the contract after PASS merely to
change status text.

Final approval is external through the canonical freeze receipt(s).  Git tags may point to
the approved commit but do not replace the receipt.

---

## 29. One-shot final freeze gate

The v9 byte set is eligible for freeze only when all of the following are simultaneously
true:

1. this design-contract v2 candidate has completed content audit and is the selected exact
   design byte sequence;
2. final kernel/adapter/runner/checker/checkpoint/bridge/driver/aggregate sources pass their
   source and structural audits;
3. the canonical analytic dependency package and independent rederivation are archived;
4. canonical dependency entries and snapshot are generated from the final proof/design
   identities;
5. canonical plan and every shard config are generated without hash cycles;
6. the >=256-leaf corpus passes on the exact final bytes;
7. every config to be frozen passes the required three-run performance qualification;
8. qualification manifest hashes match every referenced byte sequence/report;
9. freeze receipts reference the same plan/design/dependency/source identities and their
   respective config hashes;
10. no unresolved normative `SPEC_PENDING` choice remains.

Only those immutable qualified bytes plus valid freeze receipt(s) constitute
`V9_FROZEN_APPROVED`.

---

## 30. First post-freeze action

The first post-freeze mathematical run is the exact one-shard `2^-20` production
rehearsal.

On production success, the same frozen aggregate-verifier architecture processes the
single shard and may emit `CERTIFIED_LAMBDA_RANGE` for exactly

```text
[123731943/26214400,118/25].
```

This is still a pipeline/production rehearsal and not the paper's connected theorem
closure.

After that rehearsal is accepted, the theorem-sufficient connected lambda range and
multi-shard plan are fixed under the separately frozen 16-stage paper dependency graph.
The same v9 source architecture is reused; only canonical plan/config data and the
required qualification/freeze evidence for those new configs change.

Until Section 29 is closed, the workstream remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```
