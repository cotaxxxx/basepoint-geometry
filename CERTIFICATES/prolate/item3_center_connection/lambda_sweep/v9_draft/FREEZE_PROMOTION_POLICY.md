# Item 3 sweep v9 — no-byte-mutation freeze promotion policy

**Status:** `NORMATIVE CORRECTION / INTEGRATED CONTRACT CANDIDATE INPUT`  
**Date:** 2026-08-08

This policy resolves a circularity in the integrated v9 freeze candidate: validation and
performance qualification must be executed against the exact final design/source/config
bytes, but changing the design-contract file merely to replace a status label with
`FROZEN` would change those bytes and invalidate the qualification identity.

The final v9 promotion therefore does **not** mutate any qualified proof-relevant byte
sequence.

## 1. Qualification byte set

Before the >=256-leaf validation corpus and the three-run performance qualification, define
one exact qualification byte set containing at minimum:

```text
design contract
kernel
adapter
runner
checker
config
logical dependency entries/snapshot
shard plan
validation source
qualification workflow source.
```

Every member has an exact SHA-256 recorded in a canonical qualification manifest.

The design contract used here may retain a textual status such as

```text
INTEGRATED_FREEZE_CANDIDATE / NOT FROZEN
```

because the status text describes authorization state, not mathematical content.

## 2. No proof-relevant mutation after qualification begins

Once the first counted validation/qualification execution begins, any change to a member
of the qualification byte set invalidates all approval evidence that depends on the old
set and restarts the applicable count.

In particular, do **not** edit the design contract after PASS merely to change

```text
NOT FROZEN -> FROZEN.
```

Such an edit would create a new design hash without qualification evidence.

## 3. External canonical freeze receipt

Final one-shot promotion is recorded in a separate canonical object with schema

```text
ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1.
```

The receipt contains at minimum:

```text
qualification_manifest_sha256
design_sha256
kernel_source_sha256
adapter_source_sha256
runner_source_sha256
checker_source_sha256
config_sha256
dependency_snapshot_sha256
shard_plan_sha256
validation_report_sha256
performance_gate_report_sha256
freeze_verdict
nonclaims.
```

The receipt contains no self-hash.  Its external receipt SHA-256 is computed from exact
canonical receipt bytes.

The only permitted successful verdict is

```text
V9_FROZEN_APPROVED
```

and it is legal only when every referenced gate is PASS and every referenced hash matches
the qualification manifest.

## 4. Meaning of promotion

The pair

```text
qualified immutable byte set
+ canonical V9 freeze receipt
```

is the frozen v9 identity.

No proof-relevant source file, config, dependency entry, design contract, or workflow
requires a status-text rewrite.  Git tag/ref metadata may point to the approved commit, but
the tag itself is not a substitute for the freeze receipt.

## 5. Rehearsal authorization

Only a valid `ITEM3_SWEEP_V9_FREEZE_RECEIPT_V1` with verdict
`V9_FROZEN_APPROVED` may authorize the exact `2^-20` production rehearsal.

The rehearsal config must reference the same qualification/design/source/dependency hashes.
A mismatch is `RUN_FATAL`, not an invitation to regenerate hashes silently.

## 6. Post-freeze change rule

Any later proof-relevant byte change creates a successor candidate identity.  The old
freeze receipt remains immutable provenance for the old byte set and does not authorize
the successor.

## 7. Effect on integrated contract candidate

Where the integrated contract candidate says that exact bytes "receive" a frozen/approved
state, interpret that promotion through the external freeze receipt defined here.  The
qualified design-contract file itself remains byte-identical before and after promotion.

This correction authorizes no run and does not itself freeze v9.
