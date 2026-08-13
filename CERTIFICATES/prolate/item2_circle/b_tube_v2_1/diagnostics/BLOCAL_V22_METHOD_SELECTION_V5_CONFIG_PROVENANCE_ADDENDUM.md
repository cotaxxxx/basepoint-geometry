# B-LOCAL v2.2 §6 — v5 config provenance addendum

STATUS: DIAGNOSTIC PROTOTYPE ADDENDUM. This document corrects the provenance
description of the runtime configuration used by the §6 method-selection v5
diagnosis. `certificate_evidence=false`.

This addendum does not replace or modify
`BLOCAL_V22_METHOD_SELECTION_V5_SPEC.md` (SHA-256 `42a9b798...`). The original
specification, v5 prototype, native nine sources, committed configuration,
production path, and tags remain byte-for-byte unchanged.

## 1. Correction to the v5 specification

Section 8 of the original v5 specification calls the following values
“committed node budgets”:

| Ephemeral diagnostic node | max depth | max evaluations | max tiles/bisections |
|---|---:|---:|---:|
| L1 | 18 | 20,000 | 12,000 tiles |
| L2 | 22 | 12,000 | 8,000 tiles |
| L3 | 22 | 12,000 | 8,000 tiles |
| J_START | materialized algorithm | 96 | 40 bisections |

The numeric values are correct for the established diagnostic runtime, but
their attribution to the committed configuration bytes is incorrect. They are
the budget values produced by the deterministic ephemeral materialization
described in §3. They are therefore named the **ephemeral diagnostic
contract** in all records and workflows governed by this addendum.

The committed configuration has two L1 keys, `L1_BOUNDARY` and `L1_INTERIOR`.
The materialized ephemeral configuration instead has the single key `L1` with
depth 18, 20,000 evaluations, and 12,000 tiles. This single L1 budget is used
for the H_u/derivative work in conditions 4 and 5 and for the derivative step
inside condition 6. Conditions 5 and 6 must use the same materialized
ephemeral contract as the ladder and must not import the schema or budget-key
layout of the committed configuration.

## 2. Schema-generation separation

The committed configuration SHA-256 `fec14e99...` belongs to an earlier schema
generation. Its budget keys include `L1_BOUNDARY`, `L1_INTERIOR`, `L2`, `L3`,
and `J_START`; it also contains legacy fields including `boundary_strip` and
`endpoint_route`.

The current native model requires the current exact-key schema, including
`budgets` keys `L1`, `L2`, `L3`, and `J_START`, together with current
`design_contracts`, `geometry`, and `route_policies`. Consequently, passing the
committed configuration bytes directly to the current
`model.validate_config` is an infrastructure error, not a mathematical
candidate verdict.

The committed bytes remain immutable provenance input. They are not an
executable current-schema configuration and must not be silently edited,
normalized, or relabeled as one.

## 3. Deterministic ephemeral materialization

Every shard and every later conditions-5/6 diagnostic constructs its runtime
configuration by the already established diagnostic procedure:

1. Read and hash the committed configuration bytes without validating them as
   the current schema.
2. Call `blocal_v22_checker_test.config()` from the fixed checkout to construct
   a current-schema diagnostic configuration.
3. Copy exactly these top-level values from the parsed committed bytes into
   that object: `stage1_dependency`, `kernel`, `adapter`, `base_v21`, and
   `outputs`.
4. Recompute the SHA-256 values of the fixed native nine source files from
   their checked-out bytes.
5. Reconstruct `implementation`, `checker`, and `symbolic_audit` using those
   byte hashes and the identifiers exported by the fixed current model.
6. Run `model.validate_config` on the resulting current-schema object.
7. Serialize it only with `model.canonical_json_bytes` and hash those exact
   materialized bytes.

No timestamps, host paths, matrix indices, candidate values, environment
ordering, or runtime-generated nondeterminism may enter the materialized
object. A fixed checkout and fixed committed input must yield the same
materialized SHA-256 in all 21 shards and in conditions 5 and 6.

The materialized file is ephemeral runtime input. It is never committed and is
removed after use.

## 4. Pinning asymmetry

`blocal_v22_method_taylor2_probe_v5.py` continues to pin only the original v5
specification SHA-256 `42a9b798...`, plus its existing v4/v3 dependencies. The
prototype does **not** pin this addendum, and the prototype bytes must not be
changed merely to add such a pin.

This asymmetry is intentional. The original prototype governs mathematical
evaluation changes; this addendum governs workflow-side configuration
materialization and provenance vocabulary. The ladder workflow pins and
verifies this addendum independently before constructing the ephemeral
configuration. A missing or mismatched addendum is
`INFRASTRUCTURE_FAILURE`.

## 5. Required provenance record

Each shard records these independently verified values near the top level of
its record:

1. checkout full commit SHA;
2. v5 prototype SHA-256;
3. original v5 specification SHA-256;
4. this addendum SHA-256;
5. committed configuration SHA-256;
6. materialized ephemeral configuration SHA-256;
7. materialization inputs: `blocal_v22_checker_test.py`,
   `blocal_v22_model.py`, and all native nine source SHA-256 values.

The record field for the runtime node limit is
`ephemeral_diagnostic_budget`; `mathematical_budget` and
`committed_contract_budget` are prohibited for these materialized values.
Infrastructure wall timeout remains separately recorded as
`ci_wall_timeout_seconds` and is not part of the ephemeral diagnostic
contract.

The aggregator verifies:

- exactly 21 shard records, one for every canonical candidate index;
- all fixed provenance pins;
- identical materialized ephemeral configuration SHA-256 across all shards;
- identical materialization-input hashes across all shards; and
- the previously specified verdict and canonical selection rules.

A mismatch, missing field, materialization validation error, or direct attempt
to validate committed bytes is `INFRASTRUCTURE_FAILURE`. It is never converted
to `INDETERMINATE` or `REJECTED`.

## 6. Invariants

- The committed configuration SHA-256 `fec14e99...` is unchanged and is used
  only as immutable provenance/copy input under §3.
- The original v5 specification SHA-256 `42a9b798...` is unchanged.
- The v5 prototype SHA-256 `7b4f9b39...` and its existing pins are unchanged.
- The native nine sources, v3/v4 prototypes, C1 specification, production
  path, and tags are unchanged.
- This addendum authorizes no workflow mutation or execution by itself; those
  remain separately audited and authorized steps.
