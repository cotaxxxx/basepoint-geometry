# Item 3 sweep v9 — schema and aggregate byte-grammar freeze candidate

**Status:** `NORMATIVE CANDIDATE / VALIDATION PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This candidate resolves the remaining schema-ID, initial partial-evidence form,
checkpoint-size, v8.1 compatibility, and selected-shard aggregate-chain byte grammar
choices.

It authorizes no production source, run, tag, or certificate before the one-shot v9
freeze.

## 1. Deliberate v8.1 schema incompatibility

v9 adds five F-level outputs, dual quotient associations, two-coordinate refinement,
separate dps-50/dps-70 checker roles, multi-run shards, and aggregate selection evidence.

Therefore v9 does **not** reuse a v8.1 schema identifier. A v8.1 object presented under a
v9 schema is rejected even if overlapping fields appear compatible.

Coordinate encodings may inherit their existing independently frozen IDs; top-level
record schemas do not.

## 2. Frozen proposed schema IDs

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

Unknown schema IDs fail closed.

## 3. Canonical JSON inheritance

All v9 normative JSON inherits the existing project canonical-JSON discipline:

- UTF-8;
- exact field names and closed schemas;
- duplicate keys prohibited;
- unknown fields prohibited unless a schema explicitly marks a diagnostic extension
  object;
- no binary floating-point numbers in normative fields;
- rational/dyadic values use their frozen canonical coordinate encodings;
- SHA-256 strings are exactly 64 lowercase hexadecimal characters;
- JSONL normative lines end in exactly one LF;
- CRLF and trailing whitespace are prohibited in normative records.

A schema migration uses a new schema ID. The verifier never silently broadens an old ID.

## 4. Initial partial-evidence form

Initial v9 has no resume semantics. Therefore

```text
SWEEP_PARTIAL_EVIDENCE.json
```

is frozen as **one canonical embedded object**, not a content-addressed DAG and not a
second JSONL chain.

It contains only fully completed attempts through `last_complete_attempt_id`, plus the
accepted partition prefix and pending-frontier summary required for cancellation
diagnosis.

It contains no Python pickle, interval-library object, cache, thread state, or in-flight
attempt.

This choice minimizes moving parts for the first production rehearsal. A future resumable
v10-style design requires a new schema/contract.

## 5. Checkpoint-size limit

The maximum serialized size of either replacement checkpoint object is frozen at

```text
32 MiB = 33554432 bytes.
```

If a canonical replacement object would exceed this limit, the runner reports a
checkpoint/infrastructure failure and aborts fail-closed. It may not drop completed
attempts, truncate a JSON object, or continue while claiming cancellation-safe evidence.

The 32 MiB value is an engineering ceiling only and has no mathematical significance.
Qualification reports observed maximum checkpoint size.

## 6. Final proof independence from checkpoints

Checkpoint timing is nonnormative. Therefore final shard evidence and final aggregate
proof evidence do **not** include:

- checkpoint count;
- checkpoint timestamps;
- last checkpoint chain tip;
- checkpoint cadence decisions.

Such fields may appear in a clearly separated provenance/diagnostic block excluded from
the canonical mathematical-evidence hash.

Two runs with identical frozen mathematical inputs may produce different checkpoint
histories while still producing byte-identical final mathematical evidence.

## 7. Shard-plan object

Before any multi-run execution, one canonical

```text
ITEM3_SWEEP_V9_SHARD_PLAN_V1
```

object fixes:

```text
rehearsal_range
shard_count
ordered_shards[]
  shard_index
  shard_id
  lambda_lo
  lambda_hi
config_sha256
design_sha256
kernel_source_sha256
adapter_source_sha256
runner_source_sha256
checker_source_sha256
logical_dependency_hashes
partition_control_dps
accepted_cell_verification_dps.
```

The object contains **no self-hash field**. Define

```text
aggregate_plan_sha256 = SHA256(canonical shard-plan bytes).
```

Every shard evidence object records this hash and its own exact shard index/endpoints.

## 8. Mathematical shard order

Shard index zero is the uppermost shard, closest to `lambda_anchor`. Indices increase in
the downward mathematical sweep direction.

For adjacent indices `i` and `i+1`, exact canonical endpoints must satisfy

```text
shard[i].lambda_lo == shard[i+1].lambda_hi
```

with byte identity under the canonical lambda encoding.

The exact union of all ordered shards must be the approved rehearsal range and shard
interiors must be pairwise disjoint.

## 9. Selected-shard chain domain

Freeze the ASCII domain bytes

```text
ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V1\0
```

including the final zero byte.

All SHA-256 values used by the chain are decoded from their 64-character lowercase hex
representation to exactly 32 raw bytes before concatenation.

Each shard index is encoded as an unsigned 64-bit big-endian integer. Shard counts or
indices outside `[0,2^64-1]` are rejected.

No decimal text, JSON rendering, host integer byte order, variable-length integer, or
separator-dependent encoding is allowed in the chain preimage.

## 10. Exact aggregate chain formula

Let

```text
D = ASCII("ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V1\0")
P = raw32(aggregate_plan_sha256)
h_i = raw32(selected shard_evidence_sha256 at index i)
I_i = uint64_be(i).
```

For shard zero:

```text
C_0 = SHA256(D || P || I_0 || h_0).
```

For every `i>0`:

```text
C_i = SHA256(D || P || I_i || C_(i-1) || h_i).
```

Here every `C_i` is the raw 32-byte digest returned by SHA-256.

The final manifest stores

```text
selected_chain_tip_sha256 = lowerhex(C_(n-1)).
```

For `shard_count=0`, no aggregate proof manifest is legal for a nonempty rehearsal range.

## 11. Aggregate manifest selection fields

The canonical aggregate manifest contains one selected attempt for every planned shard:

```text
selected_shards[]
  shard_index
  shard_id
  github_run_id
  github_run_attempt
  shard_evidence_sha256
  checker_report_sha256.
```

The list is serialized in strictly increasing `shard_index`. Workflow completion order is
not recorded in this normative list.

The manifest also records

```text
aggregate_plan_sha256
selected_chain_tip_sha256
exact_union_verified = true
adjacent_endpoint_bytes_verified = true
all_selected_shard_checkers_pass = true
aggregate_verdict.
```

Boolean fields are evidence to be rederived, never trusted as oracles.

## 12. One-shard rerun semantics

If one shard is rerun and a different passing attempt is selected:

- immutable evidence for all unrelated shards remains unchanged;
- the selected list changes only at that index;
- the aggregate chain is recomputed from index zero;
- the aggregate manifest receives a new canonical hash;
- exact union and every checker predicate are reverified.

No downstream shard must be rerun solely because an earlier selected hash changed.

## 13. Dependency entry envelope

A canonical v9 dependency entry uses schema

```text
ITEM3_SWEEP_V9_DEPENDENCY_ENTRY_V1
```

and contains at minimum

```text
lemma_id
statement
proof_document_path
proof_document_sha256
supports_machine_conclusion
assumptions[]
nonclaims[].
```

The canonical entry object contains no self-hash. Its external

```text
dependency_entry_sha256
```

is SHA-256 of the exact canonical entry bytes and is recorded by the dependency snapshot
and run config.

This removes any ambiguity about self-referential hashing.

Final dependency entries are created only after proof documents and approved source bytes
are frozen.

## 14. Required aggregate mutation controls

Validation must reject at least:

- domain string missing the terminal zero byte;
- hash hex text concatenated instead of raw 32-byte digests;
- little-endian shard index;
- variable-length shard index;
- completion-order list substituted for shard-index order;
- stale selected chain tip after one shard selection changes;
- stale aggregate plan hash;
- duplicate/missing shard index;
- adjacent endpoint equality by numerical approximation rather than canonical bytes;
- overlapping shard interiors;
- a gap in exact union;
- selected shard checker failure hidden by aggregate boolean fields;
- final proof hash bound to checkpoint timing data.

## 15. Resolution status

If incorporated into the one-shot final v9 freeze, this candidate resolves:

```text
final schema identifiers
partial evidence representation
maximum checkpoint size
v8.1 schema compatibility policy
final aggregate selected-chain byte grammar
dependency-entry hash envelope.
```

Runtime/source validation and actual dependency hashes remain pending.
