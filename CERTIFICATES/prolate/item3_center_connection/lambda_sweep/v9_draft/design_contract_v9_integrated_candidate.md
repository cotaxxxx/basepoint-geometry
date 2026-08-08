# Item 3 lambda Sweep Design Contract v9 — Integrated Freeze Candidate

**Status:** `INTEGRATED_FREEZE_CANDIDATE / NOT FROZEN / NO RUN AUTHORIZATION`  
**Date:** 2026-08-08  
**Issue:** #20

This document consolidates the v9 mean-value design, analytic closure, deterministic
control rules, checkpoint policy, quotient association, schema/aggregate grammar,
validation-corpus requirement, performance qualification, and the exact first rehearsal
range into one self-contained normative candidate.

It does **not** authorize a production tag, workflow run, certificate, or
`CERTIFIED_LAMBDA_RANGE`.  Any source/config/dependency change after the final one-shot
freeze requires a new identity and the applicable re-audit path.

---

## 1. Purpose and predecessor evidence

The frozen v8.1 production path reached the pinned production runner in GitHub Actions run
`30609564841` but could not complete inside the hosted-job wall-clock limit.  That run is
provenance for a resource limitation only.  It is not a mathematical failure and is not a
proof node.

v9 replaces raw interval evaluation of `G_r` on an `(r,lambda)` rectangle by a rigorous
five-output derivative kernel plus a two-variable mean-value enclosure.  The initial
precision policy remains

```text
partition-control runner/checker dps = 50
accepted-cell fresh checker dps      = 70.
```

The dps-70 checker may reject an accepted dps-50 cell but may not alter the dps-50 split
tree.

---

## 2. Exact first rehearsal range

The exact first end-to-end production-rehearsal target is

```text
lambda_anchor = 118/25
lambda_target = 123731943/26214400
R_rehearsal   = [123731943/26214400, 118/25]
width          = 1/1048576 = 2^-20.
```

The range is downward oriented.  It is a production rehearsal of the final contract and
evidence structure, not the theorem-sufficient connected chain toward `a_c`.

No run may silently move an endpoint, reverse direction, widen the range, shrink the range
after a failure, or reinterpret partial evidence as a certified subrange.

The later upward/bidirectional work toward `a_c` requires its own explicitly approved
range/partition plan and does not inherit authorization from this rehearsal.

---

## 3. Coordinates and canonical arithmetic

Lambda endpoints use `CANONICAL_REDUCED_RATIONAL_V1`; r endpoints use
`CANONICAL_DYADIC_V1`; rigorous output enclosures use the frozen canonical interval
encoding selected by the final adapter contract.

For

```text
I      = [r_lo,r_hi]
Lambda = [lambda_lo,lambda_hi],
```

define exact canonical centers

```text
r0      = (r_lo+r_hi)/2
lambda0 = (lambda_lo+lambda_hi)/2.
```

Runner and checker independently rederive these centers.  Floating-point centers,
decimal-rendered centers, arbitrary interior points, or unreduced rational centers are
prohibited.

All width, midpoint, inclusion, split-score, endpoint, and coverage comparisons are exact
canonical comparisons.

---

## 4. Analytic domain and fixed integration domain

The approved analytic proof uses the fixed integration domain

```text
theta in [0,pi/2]
phi   in [0,pi].
```

Every machine rectangle is contained in

```text
0 < r < 1,
lambda >= 1.
```

On compact subrectangles of this domain the analytic proof establishes uniform positivity
of all algebraic denominators, including the exact lower bounds implied by

```text
q >= (1-r)^2 > 0,
W >= 1-r > 0,
w^2 >= 1.
```

The exact square-sum identity establishes

```text
0 < gamma <= 1.
```

For `h(c)=acos(c)^2`, the endpoint `c=1` is removable through the derivatives needed by
v9, with

```text
h'(1)   = -2
h''(1)  = 2/3
h'''(1) = -8/15.
```

The analytic proof establishes the displayed `F_r`, `F_lambda`, `F_rr`, and `F_rlambda`
integrands, differentiation under the fixed-domain integral, and commutation of the mixed
derivative.  These analytic statements are inputs to source validation; they do not by
themselves authorize machine use.

---

## 5. Clean-room kernel boundary

The production kernel must expose exactly the rigorous F-level interfaces required by the
adapter:

```text
F
F_r
F_lambda
F_rr
F_rlambda.
```

The current validated source candidate is

```text
KERNEL_ID = ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2
candidate SHA-256 = abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76.
```

The final freeze may bind this source only if the source bytes remain identical.  A changed
kernel hash requires a fresh static/runtime/source-formula validation cycle.

The kernel must:

- import no runner/checker/adapter/prototype proof source;
- propagate nested `acb.integral` analyticity by logical OR;
- forward `analytic=` to both square roots;
- reject the Gauss `2F1` principal-cut intersection fail-closed during analytic callback
  evaluation;
- enforce the full input-ball domain `0<r<1`, `lambda>=1`;
- reject non-finite validated integral output;
- expose no diagnostic float path under the rigorous interface IDs.

Finite differences, sampled agreement, or diagnostic quadrature are not proof machinery.

---

## 6. Logical dependencies

The final dependency snapshot adds canonical entries for:

### `L-SECOND-DERIV`

The rigorous analytic formula for `F_rr`, the exact quotient identity for `G_rr`, the
validity domain, differentiation-under-integral justification, and the requirement that
the approved interval source encloses that exact formula.

### `L-MIXED-DERIV`

The rigorous analytic formulas for `F_lambda` and `F_rlambda`, the exact quotient identity
for `G_rlambda`, the validity domain, mixed-differentiation justification, and the
requirement that the approved interval source encloses those exact formulas.

### `L-MEAN-VALUE-ENCL`

The two-variable mean-value inclusion, exact centers, exact split scores, total axis order,
strict sign predicate, and fail-closed refinement semantics.

A dependency entry uses schema `ITEM3_SWEEP_V9_DEPENDENCY_ENTRY_V1`, contains no self-hash,
and is externally identified by SHA-256 of its exact canonical bytes.  Final dependency
hashes are generated only after proof/source bytes are frozen.

---

## 7. Exact quotient identities

Let

```text
G = F/r.
```

For `r>0`,

```text
G_r       = F_r/r - F/r^2
G_rr      = F_rr/r - 2 F_r/r^2 + 2 F/r^3
G_rlambda = F_rlambda/r - F_lambda/r^2.
```

For a positive rigorous interval `R`, compute once

```text
R2 = R*R
R3 = R2*R.
```

Three expression IDs are frozen by the final contract:

```text
ITEM3_V9_GR_DUAL_ASSOC_V1
ITEM3_V9_GRR_DUAL_ASSOC_V1
ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1.
```

---

## 8. Dual quotient association

For each quotient quantity compute both the exact direct association and exact
common-denominator association in the frozen operation order.

### Direct

```text
GR_DIRECT  = (F_r/R) - (F/R2)
GRR_DIRECT = ((F_rr/R) - ((2*F_r)/R2)) + ((2*F)/R3)
GRL_DIRECT = (F_rlambda/R) - (F_lambda/R2).
```

### Factored

```text
GR_FACTORED  = ((F_r*R)-F)/R2
GRR_FACTORED = (((F_rr*R2)-((2*F_r)*R))+(2*F))/R3
GRL_FACTORED = ((F_rlambda*R)-F_lambda)/R2.
```

Combination is fail-closed:

```text
both finite and overlapping -> FINAL = intersection
both finite and disjoint    -> RUN_FATAL / QUOTIENT_ASSOCIATION_DISJOINT
exactly one finite          -> use the finite enclosure
neither finite              -> NONFINITE and ordinary deterministic refinement.
```

No approximate radius comparison chooses an association.  Runner values are evidence;
checker recomputes both paths from fresh F-level calls.

---

## 9. Two-variable mean-value enclosure

Set `H=G_r`.  The analytic theorem gives, for the canonical center,

```text
H(I,Lambda)
 subset
 H(r0,lambda0)
 + G_rr(I,Lambda)*(I-r0)
 + G_rlambda(I,Lambda)*(Lambda-lambda0).
```

The normative machine enclosure is therefore

```text
MV = FINAL(G_r at center)
     + FINAL(G_rr on box)*(I-r0)
     + FINAL(G_rlambda on box)*(Lambda-lambda0).
```

A cell is `NEG` if and only if every required term is finite and

```text
sup(MV) < 0.
```

`sup(MV)=0` is not negative.  A non-finite or non-NEG result enters deterministic
refinement and is not a mathematical counterexample.

Runner records every center, derivative box, offset, correction term, both quotient
associations, final quotient enclosure, and final MV.  Checker independently reconstructs
them.

---

## 10. Split scores and total axis order

At dps 50, using the FINAL derivative boxes,

```text
S_r      = radius(I)      * absmax(FINAL(G_rr(I,Lambda)))
S_lambda = radius(Lambda) * absmax(FINAL(G_rlambda(I,Lambda))).
```

Scores are exact canonical nonnegative quantities or `NONFINITE`.

Among splittable axes the total selection order is:

1. no splittable axis -> normative unsplittable/incomplete terminal reason;
2. only one splittable axis -> select it;
3. `NONFINITE` outranks finite;
4. among finite scores, larger exact score wins;
5. exact class/score tie -> `r`.

Thus double-nonfinite ties select r.  Unsplittable axes are never candidates.  dps-70,
wall clock, host load, completion order, or approximate score magnitude may not influence
the tree.

---

## 11. Refinement floor and derived depth cap

The measured v9 planning evidence supports the frozen first-v9 stop floors

```text
min_r_width      = 2^-16
min_lambda_width = 2^-16.
```

These are certification stop floors, not measured certification boundaries.

A split on an axis is permitted only when **each resulting child width is at least the
axis floor**.

No independent arbitrary numeric maximum depth is needed.  For each axis root interval
`J` with width `w` and floor `f`, define the exact derived depth cap

```text
d_cap(J,f) = max { d in Z_{>=0} : w/2^d >= f },
```

with `d_cap=0` when `w<f`.  This is computed by exact rational/dyadic comparisons, never
floating logarithms.

A child may be created only if its depth does not exceed the root-derived cap and its exact
width satisfies the floor.  The two checks are redundant by design and checker-rederived.

For the rehearsal lambda root, `width=2^-20 < 2^-16`, hence `d_cap=0`: lambda refinement
inside that exact rehearsal shard is prohibited.  Failure of the root lambda box must
therefore remain fail-closed rather than silently narrowing the approved rehearsal target.

A cell reaching a required floor without strict NEG is `INCOMPLETE`; time success cannot
promote it.

---

## 12. Deterministic child and stack order

A node is identified structurally by

```text
(lambda_box, r_cell, path_id, r_depth, lambda_depth).
```

Each shard root has `path_id="ROOT"`.

For an r split:

```text
R0 = lower-r child
R1 = upper-r child
processing order R0 then R1
LIFO pushes R1 then R0.
```

For a lambda split:

```text
L0 = lower-lambda child
L1 = upper-lambda child
processing order L1 then L0
LIFO pushes L0 then L1.
```

This preserves frozen v8.1 lower-r-first and upper-lambda-first behavior.

Path IDs append `/R0`, `/R1`, `/L0`, `/L1`.  Activation indices are exact nonnegative
integers in pop/activation order.  Retries retain the same path ID and use increasing
`attempt_index`.

The checker independently reconstructs selected axes, midpoints, stack push/pop, path IDs,
activation order, and retry structure.

---

## 13. Record ordering

Execution attempt records are serialized by increasing

```text
activation_index, attempt_index.
```

Accepted mathematical leaves are separately serialized in exact geometric order:

```text
1. lambda_hi descending
2. lambda_lo descending
3. r_lo ascending
4. r_hi ascending
5. path_id lexicographic only as an impossible-tie guard.
```

Two distinct leaves tied on the same exact rectangle are an internal duplicate error.
Workflow or thread completion order is never mathematical order.

---

## 14. Checkpoint contract

Initial v9 writes

```text
SWEEP_PROGRESS.json
SWEEP_PROGRESS.jsonl
SWEEP_PARTIAL_EVIDENCE.json.
```

Checkpoint evidence is partial execution provenance only.  Initial v9 has no resume
semantics and checkpoint data cannot authorize a mathematical verdict.

Replacement files use:

```text
serialize complete canonical bytes in memory
-> unique sibling temp
-> write/flush
-> fsync file
-> close
-> os.replace
-> fsync parent directory.
```

JSONL entries are one canonical object plus exactly one LF, followed by flush+fsync.
Only a trailing non-line suffix after the last LF may be ignored after cancellation; a
malformed complete line is corruption.

Checkpoint request occurs only after a completed attempt when any of:

```text
>=120 monotonic seconds since last durable checkpoint
>=32 completed attempts since last durable checkpoint
structural lambda/shard completion boundary
controlled shutdown/cancellation hook.
```

No checkpoint is taken mid-kernel-call.

Each replacement checkpoint object is at most

```text
32 MiB = 33554432 bytes.
```

Checkpoint overhead must satisfy

```text
checkpoint_wall_time / complete_path_wall_time <= 0.05.
```

Failure is infrastructure/performance failure, never a mathematical verdict.

Checkpoint timing/count is excluded from final mathematical-evidence hashes.

---

## 15. v9 schema IDs

The v9 top-level schemas are deliberately incompatible with v8.1 and use:

```text
ITEM3_SWEEP_V9_SHARD_PLAN_V1
ITEM3_SWEEP_V9_ATTEMPT_V1
ITEM3_SWEEP_V9_SHARD_EVIDENCE_V1
ITEM3_SWEEP_V9_CHECKER_REPORT_V1
ITEM3_SWEEP_V9_AGGREGATE_MANIFEST_V1
ITEM3_SWEEP_V9_PROGRESS_V1
ITEM3_SWEEP_V9_PROGRESS_LINE_V1
ITEM3_SWEEP_V9_PARTIAL_EVIDENCE_V1
ITEM3_SWEEP_V9_DEPENDENCY_ENTRY_V1
ITEM3_SWEEP_V9_STATIC_AUDIT_V1
ITEM3_SWEEP_V9_VALIDATION_REPORT_V1.
```

Unknown fields/IDs fail closed unless a schema explicitly provides a diagnostic extension
object.  Normative JSON is canonical UTF-8, has no duplicate keys, no CRLF/trailing
whitespace, no binary floating-point normative values, and uses exactly 64 lowercase hex
characters for SHA-256 text.

`SWEEP_PARTIAL_EVIDENCE.json` is one canonical embedded object, not a second DAG/JSONL
chain.

---

## 16. Multi-run shard plan

Before multi-run execution, one canonical `ITEM3_SWEEP_V9_SHARD_PLAN_V1` object fixes the
exact total range, ordered shards, source/config/design/dependency hashes, and dps policy.
The object contains no self-hash; define

```text
aggregate_plan_sha256 = SHA256(canonical shard-plan bytes).
```

Shard index zero is the uppermost shard.  Adjacent exact endpoints must be byte-identical,
shard interiors pairwise disjoint, and the exact union equal the approved target range.

Immutable shard evidence contains its own evidence hash but no normative predecessor-shard
hash.  A failed shard may be rerun without regenerating unrelated passing shard evidence.

The exact `2^-20` rehearsal may be represented by a single shard.  If packaging is split
into multiple shards in a future approved plan, partitioning changes execution packaging,
not the mathematical target.

---

## 17. Selected-shard aggregate chain

Freeze domain bytes

```text
ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V1\0
```

including the terminal zero byte.  Decode all SHA-256 text to raw32 bytes and encode the
shard index as uint64 big-endian.

Let

```text
D   = domain bytes
P   = raw32(aggregate_plan_sha256)
h_i = raw32(selected shard_evidence_sha256)
I_i = uint64_be(i).
```

Then

```text
C_0 = SHA256(D || P || I_0 || h_0)
C_i = SHA256(D || P || I_i || C_(i-1) || h_i), i>0.
```

The manifest records lowerhex of the final digest.  The verifier independently recomputes
the plan hash, exact union, selected list, and chain.  Workflow completion order never
enters the chain.

Changing one selected shard attempt regenerates aggregate selection/chain evidence only;
unrelated immutable shard evidence remains unchanged.

---

## 18. Runner/checker independence and source binding

Runner and checker use separate adapter instances and separate kernel-call counters.
Checker may not reuse runner interval objects, caches, scores, split decisions, or final
quotient/MV values.

Before import, every proof-relevant source path is resolved inside the approved source root
and SHA-256 checked against the frozen config/dependency snapshot.  Immediately after
import, the source is rehashed and must be unchanged.  The imported module's resolved file
path must equal the approved path.

Dynamic path escape, source replacement after hash check, or importing a different module
under the same public name is `RUN_FATAL`.

---

## 19. Failure and rehearsal semantics

The following separation is mandatory:

```text
mathematical strict-sign success
certification incompletion
source/schema/internal fatal failure
infrastructure/performance failure.
```

An inability to prove NEG is not a proof that NEG is false.

The rehearsal is promoted only if its entire preapproved target range and all final
checker/evidence gates pass.  A failure or incomplete shard leaves the aggregate
`NOT_CERTIFIED`/`INCOMPLETE` as applicable.

Prohibited recovery includes:

- dropping a failed shard;
- shrinking the approved range after execution;
- promoting a passing partial prefix;
- treating diagnostic/smoke/reference output as a proof node.

---

## 20. Independent validation corpus

Before source approval the exact final source/config bytes must pass a prepublished
`CONTROL_EXPECT` corpus with at least **256 unique leaves** and the following category
floors:

```text
A analytic/source-formula mapping       32
B domain/branch/angle controls          32
C five-output rigorous kernel behavior  80
D quotient/mean-value adapter           32
E deterministic refinement              32
F evidence/checkpoint/cancellation       24
G multi-run/aggregate                    16
H independence/source identity            8
TOTAL                                   256.
```

A leaf belongs to one primary category.  Cosmetic duplicates count once.  Expected results
are fixed before execution.  The machine report must contain exactly the expected IDs,
meet every category floor, have no duplicate leaf tuple, no unexpected positive failure,
and no unexpected negative-control pass.

Required attacks include, among others, OR->AND, removed 2F1 guard, quotient coefficient
mutation, `sup(MV)=0`, altered tie-break, FIFO substitution, malformed complete JSONL line,
missing directory fsync, stale aggregate plan/chain, checker-object reuse, and source-path
escape.

The historical 224-leaf result is provenance only and is not inherited by candidate v2.

---

## 21. Performance qualification

Production eligibility for the exact final frozen rehearsal bytes requires exactly three
successful independent GitHub-hosted full-path qualification repetitions.

Every counted run includes

```text
runner
fresh dps-50 checker partition replay
fresh dps-70 accepted-cell verification
final canonical evidence serialization
artifact preparation.
```

Every counted complete-path wall time must satisfy

```text
< 3 hours.
```

Across the three counted runs require

```text
median <= 2h30
maximum <= 2h45
checkpoint overhead <= 5% in every run
stop_floor_incomplete_count = 0 in every run.
```

Cancelled/failed/incomplete runs do not count.  Performance failure is not a mathematical
counterexample and cannot weaken the certificate target.

In addition, collect at least nine component timings per approved input class for each of

```text
F, F_r, F_lambda, F_rr, F_rlambda,
```

with min/median/max/p90 and enclosure size.

Passing this gate establishes eligibility only for the exact rehearsal plan, not the
cost of a broad theorem-sufficient connected sweep.

---

## 22. Qualification source identity reset rule

All counted validation/performance runs must use byte-identical:

```text
kernel
adapter
runner
checker
config
this final design contract
logical dependency snapshot
shard plan
Python version
python-flint version
workflow source.
```

Any change restarts the applicable corpus/qualification count.  Results from predecessor
bytes may remain provenance but cannot approve successor bytes.

---

## 23. Final one-shot freeze gate

This integrated candidate may become the final v9 contract only after all of the following
are complete on a single exact byte set:

1. candidate-v2 static/runtime validation PASS is archived;
2. independent analytic rederivation PASS is archived;
3. aggregate exact-core controls PASS is archived;
4. final runner/checker/adapter implementation is source-bound to the approved kernel and
   contract;
5. quotient, ordering/checkpoint, schema/aggregate controls pass against final source;
6. canonical dependency entries and dependency snapshot hashes are generated from final
   proof/source bytes;
7. the >=256-leaf independent corpus passes on final bytes;
8. the three-run performance qualification passes on final bytes;
9. config, source, workflow, dependency, and design hashes are mutually consistent;
10. no `SPEC_PENDING` normative decision remains.

Only then may the exact bytes receive the one-shot v9 freeze/approval state.

The first subsequent mathematical execution is the exact `2^-20` production rehearsal.
The rehearsal itself is not silently folded into the freeze qualification.

---

## 24. Current nonclaims

This candidate does not claim:

- that the final runner/checker/adapter is already implemented;
- that the >=256-leaf corpus has already passed final source bytes;
- that the three-run performance gate has already passed;
- that any production tag exists;
- that `CERTIFIED_LAMBDA_RANGE` has been obtained;
- that the theorem-sufficient connected range toward `a_c` has been selected or executed;
- that `lambda_match=118/25` has been promoted beyond its separately frozen candidate
  status in the full 16-stage theorem chain.

Until Section 23 is satisfied, status remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```
