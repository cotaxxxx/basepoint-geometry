# Item 3 sweep v9 — freeze delta

**Status:** `DRAFT CONTROL DELTA / STRUCTURAL RULES FROZEN / PRODUCTION NOT AUTHORIZED`  
**Date:** 2026-08-08  
**Scope:** corrections and additional normative controls required before the v9 contract can be frozen.

This file does not approve a production kernel, config, tag, workflow run, certificate, or
mathematical conclusion. Where this file explicitly corrects status prose in an older v9
draft or prototype audit, this file controls the workstream interpretation until those
older files are consolidated into the final frozen contract.

## 1. Prototype audit scope correction

The reproducible implementation-delta baseline is

```text
base design head = b82c00f2f154f131e02e122efdb156592fa98070
prototype head   = bb990b552d47af8788b5622b29af9dbaad4cf2f1
```

A repository compare between those exact refs reports

```text
10 commits
8 changed files
```

The older phrase `11 commits / 10 changed files` did not bind an explicit base SHA and is
therefore not a reproducible normative scope statement. It must not be used for source
identity, validation scope, or freeze accounting.

The eight-file delta consists of the prototype implementation/audit package plus the
measured performance-plan revision. Later repair commits, including this freeze delta,
are workstream-control changes and are not retroactively part of the pinned prototype
implementation delta.

## 2. Previously resolved controls

The following controls are no longer open decisions:

```text
canonical r center      = exact dyadic endpoint midpoint
canonical lambda center = exact reduced-rational endpoint midpoint
r split score           = radius(I) * absmax(G_rr(I,Lambda))
lambda split score      = radius(Lambda) * absmax(G_rlambda(I,Lambda))
nonfinite score         > every finite score
finite score comparison = exact canonical comparison
tie break               = r
partition control       = dps 50 in runner and checker
accepted-cell verify    = fresh dps 70, unable to mutate the partition
```

Any older audit paragraph that lists the split-score formula or normative tie-break as
`SPEC_PENDING` is stale status prose. The final consolidated contract shall remove those
items from its open-decision list.

## 3. Exact connected rehearsal range

The immediate v9 rehearsal target is the exact connected interval

```text
R_rehearsal = [123731943/26214400, 118/25]
width        = 1/1048576 = 2^-20.
```

This range is inherited from the current production config. The separate
`TARGET_RANGE_POLICY.md` governs direction and prevents silent widening or endpoint
reinterpretation.

The later upward objective toward `a_c` is outside this rehearsal and remains a separate
contract problem.

## 4. Multi-run shard model

A v9 execution may divide one approved connected lambda range into multiple workflow runs
only under the following exact shard model.

Let the approved range be `[L_min,L_max]`. Freeze a canonical ordered endpoint sequence

```text
L_max = e_0 > e_1 > ... > e_n = L_min
```

for the downward sweep. Shard `S_i` is

```text
S_i = [e_(i+1), e_i],    i = 0,...,n-1.
```

Every `e_i` is a canonical reduced rational. The sequence itself is normative evidence.
A decimal, float, display string, or independently rounded approximation cannot define a
shard boundary.

Required properties are:

1. every shard is nonempty and lies inside the approved range;
2. shard interiors are pairwise disjoint;
3. consecutive shards share exactly one endpoint;
4. the shared endpoint bytes are identical after canonical serialization;
5. the exact union of all shards is the approved connected range;
6. shard order is fixed by the endpoint sequence and not by workflow completion time;
7. no missing shard may be hidden by renumbering later shards.

The same rules apply mutatis mutandis to a future explicitly approved upward orientation.
No bidirectional interpretation is implicit.

## 5. Per-shard identity

Every reusable shard result shall bind at least:

```text
aggregate_plan_sha256
shard_id
shard_index
shard_count
lambda_lo
lambda_hi
previous_endpoint
next_endpoint
config_sha256
design_sha256
adapter_source_sha256
kernel_source_sha256
runner_source_sha256
checker_source_sha256
logical_dependency_hashes
partition_control_dps
accepted_cell_verification_dps
github_run_id
github_run_attempt
github_sha
```

The mathematical identities and source pins must be identical across shards unless a new
aggregate plan explicitly freezes a different per-shard source map. A workflow run ID is
provenance only and cannot alter shard ordering or mathematical identity.

## 6. Shard evidence chain

Each selected complete shard evidence object shall contain

```text
shard_evidence_sha256
previous_selected_shard_sha256
```

where shard `0` uses the canonical null predecessor. For `i>0`, the predecessor hash must
be the selected complete evidence hash of shard `i-1`.

The chain is checked in mathematical shard order, not wall-clock order. A run completing
early cannot become the predecessor of a geometrically earlier shard.

Partial evidence, progress checkpoints, diagnostic files, and runner-only output cannot
occupy a position in the selected complete shard chain.

## 7. Rerun unit and supersession

The minimum rerun unit is one shard. A failed, cancelled, or incomplete shard may be
rerun without recomputing already accepted independent shards, provided that:

1. the aggregate plan and all normative source/config/dependency identities are unchanged;
2. the rerun performs a fresh runner and fresh checker for that shard;
3. every attempt has a unique attempt identity;
4. the aggregate manifest selects exactly one complete passing attempt per shard;
5. an unselected attempt remains provenance and cannot contribute mathematical evidence;
6. the selected chain is rebuilt from the selected attempt hashes.

Changing a shard endpoint, source pin, design identity, config identity, dependency hash,
or precision policy is not a rerun of the same shard. It creates a new aggregate plan and
requires the corresponding audit path.

Initial v9 still has no cross-run resume semantics for an in-flight shard. A partial shard
cannot be continued from serialized Python/Arb state unless a later contract amendment
explicitly validates such resume behavior.

## 8. Aggregate manifest

A successful multi-run package shall contain a canonical aggregate object equivalent to

```text
schema
aggregate_plan_sha256
approved_range
orientation
canonical_endpoint_sequence
shard_count
selected_shards[]
selected_chain_tip_sha256
exact_union_verified
pairwise_interior_disjoint_verified
shared_endpoint_byte_identity_verified
all_shards_complete
all_shards_fresh_checker_pass
all_shards_strict_sign_pass
aggregate_status
```

The aggregate verifier independently rederives the exact union and endpoint identities.
It does not trust runner-supplied coverage flags.

`aggregate_status = CERTIFIED` is permitted only when every required shard has one
selected complete passing attempt and all aggregate predicates pass. A shard-level
`CERTIFIED`, `NEG`, or `VERIFY_PASS` cannot by itself certify the aggregate range.

## 9. Failure semantics

The following conditions force fail-closed aggregate status:

- a missing shard;
- a gap or overlap beyond the exact shared endpoint;
- endpoint byte mismatch;
- stale or mismatched source/config/dependency identity;
- incomplete runner evidence;
- absent fresh checker evidence;
- checker rejection at either required precision;
- broken selected-shard hash chain;
- stop-floor exhaustion;
- time-budget exhaustion;
- unapproved range shrinkage or widening after execution.

The resulting status is `INCOMPLETE`, `VERIFY_FAIL`, or `NOT_CERTIFIED` according to the
frozen terminal-reason table. None may be converted into a certified subrange by silently
dropping a failed shard from the approved target.

## 10. Rehearsal failure rule

The first complete v9 rehearsal is a gate, not a discovery mechanism that may rewrite its
own success criterion.

If the approved `2^-20` rehearsal fails for mathematical enclosure width, resource budget,
checker disagreement, evidence-chain failure, or schema failure, the result remains
`NOT_CERTIFIED`/`INCOMPLETE`. The next action is an explicit contract or implementation
revision followed by a new audit identity. The failed run is retained as evidence and is
never relabelled as a pass.

## 11. Validation additions required by the multi-run model

The independent validation corpus shall additionally reject at least:

- one missing middle shard;
- duplicated shard coverage;
- a one-unit rational endpoint gap;
- numerically equal but noncanonical endpoint encodings;
- a shared endpoint whose bytes differ;
- completion-order chain substitution;
- a stale predecessor hash;
- two selected attempts for one shard;
- a selected failed attempt when a later passing attempt exists;
- a rerun that changes source or config identity while claiming the same plan;
- an aggregate that omits a failed shard and shrinks the target;
- an aggregate `CERTIFIED` verdict with one shard only runner-verified;
- reuse of dps-70 values to alter a shard partition;
- cross-run resume from unvalidated serialized in-flight state.

Positive controls shall include a multi-shard exact partition whose union is independently
rederived and whose selected evidence chain remains identical under different workflow
completion orders.

## 12. Remaining freeze blockers

This delta does not close the analytic and validation obligations. Before a production v9
freeze, the package still requires at minimum:

1. final fixed-domain integrands and exact analytic formulas for all published derivative
   outputs;
2. rigorous differentiation-under-integral and mixed-derivative justification;
3. endpoint, branch, denominator, and removable-singularity proofs on the full machine
   domain;
4. one frozen interval association/expression ID for each quotient and mean-value term;
5. final child ordering, stack ordering, identifiers, and record ordering;
6. final checkpoint durability/cadence/schema policy;
7. a concrete independent control corpus of the required strength;
8. post-import source-identity verification;
9. final performance-margin/repetition policy;
10. integration of this multi-run model into the final canonical evidence schemas and
    verifier source.

Until those are discharged, overall v9 status remains `SPEC_PENDING` and no production
execution is authorized.
