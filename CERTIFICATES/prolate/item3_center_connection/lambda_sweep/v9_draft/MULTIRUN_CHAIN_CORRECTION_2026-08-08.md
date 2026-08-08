# v9 multi-run chain correction

**Status:** `NORMATIVE CORRECTION TO FREEZE_DELTA_2026-08-08`  
**Date:** 2026-08-08

This file corrects the shard-chain design in `FREEZE_DELTA_2026-08-08.md`. It supersedes
that file wherever the older text requires a selected shard evidence object to embed the
hash of the previously selected shard.

## 1. Reason for correction

Embedding

```text
previous_selected_shard_sha256
```

inside each independently reusable shard result conflicts with the frozen rule that the
minimum rerun unit is one shard. If shard `i` is rerun and its evidence hash changes, an
embedded predecessor chain would force shard `i+1` and every later shard to be regenerated
merely to update predecessor hashes, even when their mathematical evidence is unchanged.

The chain therefore belongs to the aggregate selection layer, not to immutable per-shard
evidence.

## 2. Corrected per-shard rule

A complete shard evidence object is independent of workflow completion order and of the
selected attempt for every other shard. It binds its own plan identity, exact endpoints,
source/config/dependency identities, runner evidence, and fresh checker evidence.

It shall contain

```text
shard_evidence_sha256
```

but shall **not** contain a normative predecessor-shard hash.

A diagnostic field describing observed workflow order is permitted only if explicitly
nonnormative.

## 3. Aggregate selected chain

After the aggregate manifest selects exactly one complete passing attempt for each shard,
the aggregate verifier orders the selected shard hashes by canonical mathematical shard
index and derives a separate selection chain.

Let

```text
h_i = selected shard_evidence_sha256 for shard i.
```

Freeze an aggregate chain-domain identifier, for example

```text
ITEM3_SWEEP_V9_SELECTED_SHARD_CHAIN_V1.
```

Then derive

```text
C_0 = SHA256(domain || aggregate_plan_sha256 || index(0) || h_0)
C_i = SHA256(domain || aggregate_plan_sha256 || index(i) || C_(i-1) || h_i)
```

using final canonical byte encodings for every field. The exact byte grammar and index
encoding remain part of the final schema freeze.

The aggregate manifest records the ordered selected shard hashes and the final
`selected_chain_tip_sha256`. The verifier independently recomputes the chain.

Workflow completion order never enters this calculation.

## 4. Corrected rerun semantics

A failed shard may be rerun without regenerating already accepted independent shard
evidence. After a new passing attempt is selected for that shard:

1. unchanged shard evidence bytes remain unchanged;
2. the aggregate selected-attempt list is rebuilt;
3. the aggregate selected chain is recomputed;
4. the aggregate manifest receives a new identity/hash;
5. every aggregate predicate is reverified.

Thus the mathematical rerun unit remains one shard while aggregate selection evidence is
necessarily regenerated.

Changing the aggregate plan, shard endpoints, source pins, config identity, dependency
hashes, or precision policy is still not a rerun of the same shard plan.

## 5. Validation correction

Replace any mutation test phrased as a stale **per-shard predecessor hash** with tests for:

- stale aggregate selected-shard ordering;
- stale aggregate chain intermediate value;
- stale aggregate chain tip;
- completion-order substitution for mathematical shard order;
- an aggregate manifest that selects a new shard attempt but retains the old chain tip;
- an aggregate manifest whose ordered selected hashes do not match its selected attempts.

Positive validation must demonstrate that rerunning one shard changes only that shard's
selected evidence hash and the aggregate selection/chain artifacts, not the immutable
passing evidence of unrelated shards.

## 6. Status

This correction changes evidence architecture only. It authorizes no workflow run,
production tag, config change, certificate, or mathematical conclusion. Overall v9
remains `SPEC_PENDING / FREEZE NOT AUTHORIZED`.
