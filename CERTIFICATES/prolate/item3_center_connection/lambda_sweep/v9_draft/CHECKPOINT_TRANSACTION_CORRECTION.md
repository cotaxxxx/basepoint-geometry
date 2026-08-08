# Item 3 sweep v9 — checkpoint transaction correction

**Status:** `NORMATIVE CORRECTION / FINAL FREEZE INPUT`  
**Date:** 2026-08-08

This correction supersedes the replacement-file durability sequence in
`ORDER_CHECKPOINT_FREEZE_CANDIDATE.md` and the corresponding checkpoint paragraphs in the
integrated contract candidate wherever those texts imply that overwriting
`SWEEP_PROGRESS.json` / `SWEEP_PARTIAL_EVIDENCE.json` before appending the JSONL commit
record is sufficient for cancellation-safe recovery.

## 1. Defect in the earlier candidate

The earlier ordering was conceptually

```text
replace latest progress object
replace latest partial-evidence object
append+fsync JSONL chain line.
```

If cancellation occurs after one or both replacement files are durably replaced but before
the JSONL line is durably appended, the last committed JSONL line still references the
previous payload hashes while those previous payload bytes may already have been
overwritten.

No ordering of two independent replacement files plus one append-only ledger can make all
three updates atomic.  Therefore the previous files cannot be the sole durable payload
store.

This is an evidence-transaction defect, not a mathematical defect.

## 2. Corrected durability architecture

Each checkpoint has two **immutable canonical payload objects**:

```text
progress payload
partial-evidence payload.
```

Their canonical bytes are hashed before publication.  They are stored under hash-derived
immutable paths:

```text
checkpoint_payloads/progress/<sha256>.json
checkpoint_payloads/partial/<sha256>.json.
```

A payload file is never modified after successful publication.  Existing same-hash files
must be byte-identical or the run fails closed.

The append-only file

```text
SWEEP_PROGRESS.jsonl
```

is the **only checkpoint commit ledger**.

The historical names

```text
SWEEP_PROGRESS.json
SWEEP_PARTIAL_EVIDENCE.json
```

remain optional/latest convenience mirrors.  They are not durability roots and are not
needed to reconstruct a committed checkpoint.  They may be regenerated from the most
recent committed immutable payloads.

## 3. Immutable payload publication

For each payload:

1. construct complete canonical JSON bytes in memory, ending in exactly one LF;
2. require serialized size <= 33554432 bytes;
3. compute SHA-256 over the exact file bytes including the final LF;
4. derive the final hash path from that digest;
5. if the final path already exists, require exact byte identity and perform no rewrite;
6. otherwise write a unique sibling temporary file;
7. flush and `fsync` the temporary file;
8. close it;
9. atomically rename it to the hash-derived final path;
10. `fsync` the payload directory.

No payload garbage collection is permitted during the run or before artifact archival.

## 4. JSONL commit record

After **both** immutable payloads are durable, construct one canonical commit object with
at least

```text
schema = ITEM3_SWEEP_V9_PROGRESS_LINE_V1
checkpoint_sequence
previous_checkpoint_sha256
progress_payload_sha256
partial_evidence_sha256
frontier_digest_sha256
last_complete_attempt_id
status = PARTIAL.
```

The object contains no self-hash field.

Encode the canonical object without whitespace, then append exactly one LF.  Define

```text
checkpoint_sha256 = SHA256(exact JSONL line bytes including final LF).
```

For sequence zero,

```text
previous_checkpoint_sha256 = 64 zero hex characters.
```

For every later line, `previous_checkpoint_sha256` equals the SHA-256 of the exact previous
committed JSONL line bytes.

Append the complete line using the single checkpoint writer, flush, and `fsync` the JSONL
file.  **Successful JSONL fsync is the checkpoint commit point.**

A payload published but not referenced by a committed line is an orphan diagnostic object
and has no checkpoint status.

## 5. Latest mirrors

After the JSONL commit point, the runner may atomically refresh

```text
SWEEP_PROGRESS.json
SWEEP_PARTIAL_EVIDENCE.json
```

from the just-committed immutable payload bytes.

Mirror refresh uses file fsync + `os.replace` + parent-directory fsync, but mirror failure
does not erase or invalidate the already committed JSONL checkpoint.  It is recorded as an
infrastructure warning/failure according to the final workflow policy.

No checker or recovery procedure may prefer a mirror over the committed hash-addressed
payload.

## 6. Cancellation recovery

Recovery:

1. reads `SWEEP_PROGRESS.jsonl` through the final complete LF-terminated line;
2. ignores only a trailing non-line suffix after the final LF;
3. rejects any malformed complete line;
4. verifies exact sequence and previous-line SHA chain;
5. for every retained line, locates the two immutable payloads by the recorded hashes;
6. verifies each payload file SHA-256 against its hash-derived name/reference;
7. for the final line, independently verifies the frontier digest and last-complete-attempt
   relationship against the payload content.

The last line passing all checks is the latest committed checkpoint.

Because historical payloads are immutable, an interrupted later checkpoint cannot destroy
the payload bytes referenced by an earlier committed line.

## 7. Resume nonclaim

Initial v9 still has **no resume semantics**.  The committed checkpoint is cancellation
provenance and audit evidence only.  It cannot authorize continuation of the mathematical
state machine and cannot be promoted to `CERTIFIED_LAMBDA_RANGE`.

## 8. Hash independence of final mathematical proof

Checkpoint sequence, checkpoint hashes, payload-store contents, checkpoint count, and
checkpoint timing remain excluded from the final mathematical-evidence hash.  They are
execution provenance.

The final proof partition must be reconstructed from completed final runner/checker
evidence, not from checkpoint history.

## 9. Required controls

Validation must include at least:

- cancellation after first payload publication but before second;
- cancellation after both payloads but before JSONL append;
- cancellation during an incomplete JSONL trailing suffix;
- cancellation after JSONL fsync but before mirror refresh;
- stale/corrupt mirror with valid committed immutable payloads;
- missing immutable payload referenced by a complete line;
- payload hash/path mismatch;
- prior committed payload preservation across a later interrupted checkpoint;
- malformed complete JSONL line rejection;
- wrong previous-line hash rejection;
- payload >32 MiB rejection;
- attempted overwrite of an existing hash path with different bytes.

## 10. Effect on final freeze

The final integrated contract must incorporate this correction before qualification.
`ORDER_CHECKPOINT_FREEZE_CANDIDATE.md` remains provenance for the earlier proposal but is
not normative for transaction ordering where it conflicts with this document.

This correction authorizes no run, tag, freeze, or mathematical conclusion.
