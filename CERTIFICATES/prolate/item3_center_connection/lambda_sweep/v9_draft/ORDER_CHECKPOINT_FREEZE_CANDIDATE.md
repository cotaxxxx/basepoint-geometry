# Item 3 sweep v9 — deterministic order and checkpoint freeze candidate

**Status:** `NORMATIVE CANDIDATE / FINAL FREEZE PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This candidate resolves the open child-order, stack-order, record-order, fsync, checkpoint
cadence, and cancellation-tail choices for the final v9 contract. It is designed as a
strict extension of the frozen v8.1 order rather than a new traversal convention.

It authorizes no workflow run, tag, source approval, or certificate until incorporated in
the single final v9 freeze.

## 1. Inherited order constraints

Frozen v8.1 already requires:

- lambda frontier stack is LIFO;
- a lambda split creates
  `upper_child=[mid,hi]`, `lower_child=[lo,mid]`;
- lower lambda child is pushed and upper lambda child is processed next;
- r bisection processes lower-r child before upper-r child;
- verifier independently reconstructs candidate order, stack push/pop, midpoint, and
  frontier state.

v9 preserves these orientations exactly.

## 2. Unified v9 cell node

A refinement node is identified by

```text
N = (lambda_box, r_cell, path_id, r_depth, lambda_depth).
```

The root of one exact lambda shard has

```text
path_id = "ROOT".
```

Every split uses the exact canonical midpoint of the selected coordinate.

## 3. Child labels and path IDs

### 3.1 r split

For

```text
r_cell=[r_lo,r_hi],
r_mid=(r_lo+r_hi)/2,
```

define

```text
r_lower=[r_lo,r_mid]   label R0
r_upper=[r_mid,r_hi]   label R1.
```

The canonical path IDs are

```text
parent.path_id + "/R0"
parent.path_id + "/R1".
```

### 3.2 lambda split

For

```text
lambda_box=[lambda_lo,lambda_hi],
lambda_mid=(lambda_lo+lambda_hi)/2,
```

define

```text
lambda_lower=[lambda_lo,lambda_mid]  label L0
lambda_upper=[lambda_mid,lambda_hi]  label L1.
```

The canonical path IDs are

```text
parent.path_id + "/L0"
parent.path_id + "/L1".
```

Labels describe geometric position only; processing order is specified separately.

## 4. LIFO processing rule

A single LIFO pending-node stack is used inside each shard.

### 4.1 selected axis = r

The inherited r processing order is

```text
R0 then R1.
```

Therefore push in reverse order:

```text
push R1
push R0
```

and pop the next node.

### 4.2 selected axis = lambda

The inherited downward-lambda order is

```text
L1 then L0
```

because `L1` is the upper child, closer to the anchor/frontier.

Therefore push in reverse order:

```text
push L0
push L1
```

and pop the next node.

This exactly preserves the v8.1 upper-lambda-first rule.

### 4.3 no scheduler influence

Thread completion order, wall clock, host load, checker-only values, or asynchronous task
order may not alter push order, pop order, or selected axis.

If future kernel calls are parallelized, completed values must be returned to a single
ordering owner and consumed in the already determined node order.

## 5. Attempt and node identifiers

Each activated node receives two identities:

```text
path_id          # structural, independent of execution timing
activation_index # exact nonnegative integer in pop/activation order
```

The runner records both. The checker independently reconstructs the full path tree and
activation order.

A retry of the same node retains the same `path_id` and records

```text
attempt_index = 0,1,...
```

under that node. A retry may not masquerade as a new structural node.

## 6. Canonical final record order

Two orders are distinguished.

### 6.1 execution record stream

Attempt records are serialized in increasing

```text
activation_index,
attempt_index
```

order.

This order is used for the runner/checker replay chain.

### 6.2 accepted mathematical partition

Accepted leaves are serialized separately in canonical geometric order:

```text
1. lambda_hi descending;
2. lambda_lo descending;
3. r_lo ascending;
4. r_hi ascending;
5. path_id lexicographic as an impossible-tie guard.
```

The first four keys determine all ordinary nonduplicate leaves. If two distinct leaves
remain tied on the same exact rectangle, the verifier reports an internal duplicate error
rather than accepting path ordering as mathematical multiplicity.

The geometric partition order is independent of workflow completion order and is the only
order used for exact coverage counting.

## 7. Shard-level relation

Each multi-run shard executes the above traversal independently.

The aggregate layer orders shards by the already frozen exact mathematical shard index,
not by run ID or completion time. Per-shard path IDs are namespaced by

```text
shard_id + ":" + path_id.
```

No predecessor-shard hash is embedded in immutable shard evidence; the aggregate selected
chain is constructed only after one passing attempt per shard is selected.

## 8. Checkpoint files

The initial v9 runner retains

```text
SWEEP_PROGRESS.json
SWEEP_PROGRESS.jsonl
SWEEP_PARTIAL_EVIDENCE.json.
```

These are **partial execution evidence only**. They never contain or imply a certified
mathematical verdict and are never inputs to `CERTIFIED_LAMBDA_RANGE`.

Initial v9 resume remains prohibited.

## 9. Replacement-file durability

For both replacement files

```text
SWEEP_PROGRESS.json
SWEEP_PARTIAL_EVIDENCE.json
```

the frozen write protocol is:

1. serialize complete canonical bytes in memory;
2. create a unique sibling temporary file;
3. write all bytes;
4. flush the language/runtime buffer;
5. `os.fsync` the temporary file descriptor;
6. close the temporary file;
7. `os.replace(temp,target)`;
8. open the parent directory read-only and `os.fsync` its descriptor;
9. only then update the append-only checkpoint chain.

A failure at any step leaves the checkpoint uncommitted. Checkpoint I/O failure is an
execution/infrastructure failure and cannot produce a mathematical verdict.

The final qualification platform is Linux/GitHub-hosted. Directory fsync is therefore a
required platform capability, not optional behavior.

## 10. Append-only JSONL durability

Each `SWEEP_PROGRESS.jsonl` checkpoint entry is exactly one canonical JSON object followed
by exactly one LF.

For each entry:

1. construct the complete line in memory;
2. append the line in one writer process;
3. flush;
4. `os.fsync` the JSONL file;
5. only after successful fsync may the checkpoint be called durable.

Each line contains

```text
checkpoint_sequence
previous_checkpoint_sha256
snapshot_sha256
partial_evidence_sha256
frontier_digest_sha256
last_complete_attempt_id
status = PARTIAL
```

and the hash chain is rederived independently by the checker/audit tool.

## 11. Cancellation-tail recovery

If cancellation leaves bytes after the final LF, recovery may ignore **only** that
trailing non-line byte suffix.

The recoverable JSONL prefix must satisfy all of:

```text
- every retained line ends in one LF;
- every retained line parses as canonical JSON;
- checkpoint_sequence is exact and monotone;
- every previous_checkpoint_sha256 link matches;
- referenced snapshot/partial hashes match durable replacement files when applicable.
```

A malformed complete line before the tail is not truncation; it is corruption and fails
closed.

The recovered prefix is diagnostic cancellation evidence only and cannot authorize resume
or a mathematical result.

## 12. Checkpoint cadence

A checkpoint is requested immediately after a **completed attempt** when any of the
following holds:

```text
A. at least 120 monotonic seconds since the last durable checkpoint;
B. at least 32 completed attempts since the last durable checkpoint;
C. a lambda box/shard reaches a structural completion boundary;
D. a controlled shutdown/cancellation hook requests a checkpoint.
```

No checkpoint is taken in the middle of a kernel call or incomplete attempt.

The time trigger uses a monotonic clock and affects only provenance I/O. It cannot change
partition decisions, split scores, budgets, or verdicts.

## 13. Checkpoint overhead gate

Qualification must report separately

```text
checkpoint_count
checkpoint_wall_time
checkpoint_bytes_written
maximum_checkpoint_latency
checkpoint_overhead_fraction
```

where

```text
checkpoint_overhead_fraction
 = checkpoint_wall_time / complete_path_wall_time.
```

The frozen eligibility limit is

```text
checkpoint_overhead_fraction <= 0.05.
```

Exceeding this limit produces `PERFORMANCE_GATE_FAIL`. It does not authorize weakening
fsync semantics in the same run. Any durability/cadence change requires a contract
amendment and a new qualification.

## 14. Determinism and checkpoint timing

Final mathematical evidence must be deterministic for identical frozen inputs.
Checkpoint timing artifacts are explicitly nonnormative and may differ across repeated
hosted runs because the 120-second trigger is wall-time dependent.

Therefore checkpoint files are excluded from byte-identity requirements for final proof
evidence, while their own internal canonicalization/hash-chain requirements remain
mandatory.

No mathematical field may depend on checkpoint sequence or checkpoint timestamps.

## 15. Required mutation controls

Validation must reject at least:

- r child order changed to upper-first;
- lambda child order changed to lower-first;
- FIFO substituted for LIFO;
- activation index copied from runner instead of rederived;
- duplicate path IDs;
- geometric leaf list serialized in execution order rather than canonical geometric order;
- directory fsync omitted;
- JSONL fsync omitted;
- a malformed complete JSONL line treated as a truncation tail;
- a checkpoint containing a certified verdict;
- checkpoint timing used to choose a split or stop a mathematical branch;
- checkpoint overhead above five percent treated as qualification PASS.

## 16. Resolution status

This candidate resolves the design choices formerly listed as open for:

```text
child ordering
stack insertion
identifier assignment
record ordering
directory fsync
JSONL tail recovery
checkpoint cadence
maximum checkpoint overhead.
```

They become frozen only when this candidate is incorporated into the one-shot final v9
contract freeze and passes the corresponding independent controls.
