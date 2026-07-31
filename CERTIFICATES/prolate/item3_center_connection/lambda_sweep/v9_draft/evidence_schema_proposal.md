# v9 Runner/Checker Evidence Schema Proposal

**Status:** `DRAFT / SPEC_PENDING`  
**Issue:** #20  
**Purpose:** specify evidence content and cancellation-safe persistence before source
implementation.

## 1. Principles

1. Evidence records facts used by the mathematical decision.
2. Runner evidence is never self-verifying.
3. Checker values are recomputed through a separate adapter instance.
4. Checkpoints are partial execution evidence, not verdicts.
5. All normative objects use canonical JSON and exact rational/dyadic encodings.
6. Source identity, config identity, and logical dependency identity accompany every
   independently reusable evidence unit.
7. A hosted cancellation may truncate the computation but must not convert a partial
   file into a complete certificate.

## 2. Proposed files

### Periodic checkpoint files

```text
SWEEP_PROGRESS.json
SWEEP_PROGRESS.jsonl
SWEEP_PARTIAL_EVIDENCE.json
```

### Final files

```text
SWEEP_RUN_MANIFEST.json
SWEEP_RECORDS.jsonl
SWEEP_EVIDENCE.json
SWEEP_CHECKER_REPORT.json
PILOT_ARTIFACT_REDERIVATION.json
RUNNER_EXIT_CODE.txt
MISSING_EXPECTED_FILES.txt
```

The final names remain provisional until the v9 contract freezes compatibility with
v8.1.

## 3. Common identity block

Every top-level v9 JSON object that can survive independently shall include:

```json
{
  "schema": "PROVISIONAL_SCHEMA_ID",
  "config_sha256": "<64 lowercase hex>",
  "design_sha256": "<64 lowercase hex>",
  "adapter_source_sha256": "<64 lowercase hex>",
  "kernel_source_sha256": "<64 lowercase hex>",
  "runner_source_sha256": "<64 lowercase hex or null>",
  "checker_source_sha256": "<64 lowercase hex or null>",
  "logical_dependency_hashes": {
    "L-SECOND-DERIV": "<64 lowercase hex>",
    "L-MIXED-DERIV": "<64 lowercase hex>",
    "L-MEAN-VALUE-ENCL": "<64 lowercase hex>"
  },
  "github_run_id": "<decimal string or null>",
  "github_run_attempt": "<decimal string or null>",
  "github_sha": "<40 lowercase hex or null>",
  "github_ref": "<string or null>"
}
```

Unknown keys fail closed in final schemas. During draft development, schema migrations
must use new schema identifiers rather than silently broadening an existing one.

## 4. Canonical interval and coordinate objects

The proposal reuses canonical exact coordinate objects and a frozen interval enclosure
object:

```json
{
  "lo": {"m": "-123", "e": 17},
  "hi": {"m": "-121", "e": 17}
}
```

The actual field names must match the existing canonical interval contract or be
explicitly versioned. Decimal strings are not permitted as substitutes for exact
coordinates. Arb display strings may be recorded only as diagnostics beside the
normative endpoints.

## 5. Mean-value attempt evidence

Each attempted `(λ-box, r-cell)` shall have a deterministic evidence object similar to:

```json
{
  "attempt_id": "MV-A0000000123",
  "box_id": "L0000042",
  "cell_id": "R0000917",
  "lambda_box": {"lo": {}, "hi": {}},
  "r_cell": {"lo": {}, "hi": {}},
  "canonical_center": {
    "lambda0": {},
    "r0": {}
  },
  "offsets": {
    "lambda_minus_lambda0": {"lo": {}, "hi": {}},
    "r_minus_r0": {"lo": {}, "hi": {}}
  },
  "fresh_kernel_enclosures": {
    "F_center": {"lo": {}, "hi": {}},
    "F_r_center": {"lo": {}, "hi": {}},
    "F_lambda_box": {"lo": {}, "hi": {}},
    "F_rr_box": {"lo": {}, "hi": {}},
    "F_rlambda_box": {"lo": {}, "hi": {}}
  },
  "derived_enclosures": {
    "G_r_center": {"lo": {}, "hi": {}},
    "G_rr_box": {"lo": {}, "hi": {}},
    "G_rlambda_box": {"lo": {}, "hi": {}},
    "r_correction": {"lo": {}, "hi": {}},
    "lambda_correction": {"lo": {}, "hi": {}},
    "mean_value_sum": {"lo": {}, "hi": {}}
  },
  "decision": {
    "finite": true,
    "strict_negative": true,
    "terminal_class": "NEG",
    "failure_reason": null
  },
  "counters_after_attempt": {
    "F": 0,
    "F_r": 0,
    "F_lambda": 0,
    "F_rr": 0,
    "F_rlambda": 0,
    "runner_kernel_calls": 0
  }
}
```

The example is structural only; `{}` placeholders are not legal final values.

### 5.1 Point versus box evaluations

If a derivative is evaluated on a point box, the evidence must still identify the exact
input box. The schema must not infer pointness from equal printed decimals.

### 5.2 Operation order

The evidence shall record a frozen `expression_id` for each quotient and correction
expression. The checker rejects an unknown expression ID even if the final interval
happens to contain the runner value.

## 6. Refinement evidence

Every non-NEG attempt shall record the refinement inputs:

```json
{
  "r_contribution_upper": {},
  "lambda_contribution_upper": {},
  "selected_axis": "r or lambda",
  "selection_reason": "LARGER_CONTRIBUTION | NONFINITE_R | NONFINITE_LAMBDA | NORMALIZED_WIDTH | FALLBACK_OTHER_AXIS",
  "tie_break_applied": false,
  "parent_id": "...",
  "lower_child_id": "...",
  "upper_child_id": "...",
  "depth_before": {"r": 0, "lambda": 0},
  "budget_snapshot": {}
}
```

Runner and checker must independently derive the selected axis and child intervals.

## 7. `SWEEP_PROGRESS.json`

This file is the latest complete checkpoint snapshot. Proposed fields:

```json
{
  "schema": "ITEM3_SWEEP_V9_PROGRESS_V1_DRAFT",
  "identity": {},
  "checkpoint_sequence": 17,
  "checkpoint_reason": "TIME | EVALUATION_COUNT | BOX_COMPLETE | SHUTDOWN_REQUEST",
  "elapsed_monotonic_ns": "123456789",
  "wall_clock_utc": "2026-07-31T00:00:00Z",
  "current_box_id": "L0000042",
  "current_cell_id": "R0000917",
  "last_complete_attempt_id": "MV-A0000000122",
  "accepted_leaf_count": 3,
  "r_split_count": 2,
  "lambda_split_count": 1,
  "kernel_call_counts": {
    "F": 0,
    "F_r": 0,
    "F_lambda": 0,
    "F_rr": 0,
    "F_rlambda": 0,
    "total": 0
  },
  "frontier_digest_sha256": "<64 lowercase hex>",
  "partial_evidence_sha256": "<64 lowercase hex>",
  "mathematical_verdict": null,
  "checkpoint_status": "PARTIAL_EXECUTION_EVIDENCE_ONLY"
}
```

Use monotonic elapsed time for duration. Wall-clock UTC is provenance only and must not
control machine decisions.

## 8. `SWEEP_PROGRESS.jsonl`

This append-only stream records checkpoint summaries. Each line is canonical JSON and
ends with exactly one LF. Proposed chain fields:

```json
{
  "checkpoint_sequence": 17,
  "previous_checkpoint_sha256": "<64 lowercase hex>",
  "snapshot_sha256": "<64 lowercase hex>",
  "partial_evidence_sha256": "<64 lowercase hex>",
  "frontier_digest_sha256": "<64 lowercase hex>",
  "elapsed_monotonic_ns": "123456789",
  "status": "PARTIAL"
}
```

A trailing partial line after cancellation is ignored only under an explicitly frozen
recovery rule. Initial implementation may instead write complete one-line segments to
separate files and atomically rename them before concatenation. This is an open design
decision.

## 9. `SWEEP_PARTIAL_EVIDENCE.json`

This object contains only fully completed attempts up to
`last_complete_attempt_id`. It shall not serialize an adapter object, in-flight Arb
state, Python pickle, or noncanonical cache.

Proposed contents:

```json
{
  "schema": "ITEM3_SWEEP_V9_PARTIAL_EVIDENCE_V1_DRAFT",
  "identity": {},
  "last_complete_attempt_id": "MV-A0000000122",
  "completed_attempts": [],
  "accepted_partition_prefix": [],
  "pending_frontier_summary": [],
  "record_prefix_final_sha256": "<64 lowercase hex>",
  "complete_run": false,
  "mathematical_verdict": null,
  "status": "PARTIAL_EXECUTION_EVIDENCE_ONLY"
}
```

Initial v9 does not resume from this file. It exists for diagnosis, timing attribution,
and cancellation evidence.

## 10. Atomic-write protocol

For replacement snapshots:

1. serialize canonical bytes completely in memory;
2. write to a sibling temporary path whose name cannot collide with another writer;
3. flush the language buffer;
4. apply file `fsync` if required by the final platform policy;
5. close the file;
6. call `os.replace(temp, target)`;
7. optionally `fsync` the directory if required by the final policy;
8. update the JSONL checkpoint chain only after the replacement files are complete.

Only one process may own checkpoint writes. Parallel kernel evaluation, if ever allowed,
must send completed evidence to that owner in deterministic sequence order.

## 11. Checker report additions

The final checker report shall separately state:

```text
runner_attempt_count
checker_attempt_count
runner kernel counts by derivative
checker kernel counts by derivative
runner accepted cell IDs
checker rederived cell IDs
runner mean-value expression ID
checker mean-value expression ID
partition match
record-chain match
strict-sign match
```

A checker may report diagnostic width comparisons, but `VERIFY_PASS` depends only on
fresh rigorous rederivation and frozen predicates.

## 12. Cancellation semantics

Hosted cancellation can terminate Python without allowing shell post-processing. Thus:

- runner-written checkpoints are the primary cancellation evidence;
- shell-written exit and missing-file reports are secondary when control returns;
- `if: always()` artifact upload preserves files already written;
- absence of final files does not imply mathematical failure;
- presence of partial files does not imply mathematical progress beyond their last
  complete attempt;
- no partial object may contain the word `CERTIFIED` in a verdict field.

## 13. Schema attacks required in validation

At minimum, controls shall reject:

- omitted λ correction;
- swapped `F_λ` and `F_rλ`;
- stale center with current cell;
- reassociated expression under the wrong expression ID;
- runner values copied into checker fields;
- unknown derivative count keys;
- nonmonotone checkpoint sequence;
- broken checkpoint hash chain;
- partial evidence claiming `complete_run=true`;
- partial evidence carrying a verdict;
- mismatched frontier digest;
- path escape or symlink replacement;
- duplicate JSON keys, CRLF, missing final LF where required, and unknown fields.

## 14. Open schema decisions

1. final schema identifiers;
2. exact interval endpoint encoding;
3. JSONL cancellation-tail rule;
4. directory `fsync` requirement;
5. checkpoint cadence;
6. whether completed attempts are embedded or content-addressed;
7. maximum checkpoint size and compaction policy;
8. whether final evidence references the last checkpoint chain tip;
9. compatibility or deliberate incompatibility with v8.1 record types.

No implementation is authorized until these decisions are frozen.
