# Item 3 lambda sweep — Phase 3 implementation candidate

Status: `AUDITED_SOURCE_CANDIDATE`

Normative design: Git blob `cafbf7b661911995008dda49bfb3ecabcecb1f12` (`design_contract_v8_1.md`, FROZEN).

This directory implements the frozen contract's runner/checker/verifier control plane. It does not contain a production run config, tag, workflow, receipt mutation, or numerical conclusion.

## Module boundaries

- `canonical.py`: canonical JSON/JSONL, rational/dyadic codecs, path/hash gates.
- `schema.py`: complete closed run-config schema and dependency object shape.
- `enums.py`: disjoint runner and checker closed enums.
- `transitions.py`: closed failure-transition table and `yes*` regeneration gate.
- `records.py`: record types, three counters, exact terminal-path grammar.
- `frontier.py`: exact-rational LIFO lambda frontier.
- `windows.py`: activation-time predictor context and deterministic window generation.
- `budget.py`: global-before-per-box pre-call accounting.
- `r_tile.py`: `ADAPTIVE_R_BISECTION_V1`, lower-r first, accepted leaves only.
- `adapter.py`: canonical dyadic interval and pinned-kernel adapter protocol.
- `attempts.py`: A1–A7 sign/tile/overlap/S7/S8 orchestration through the adapter boundary.
- `runner.py`: box-attempt state machine and terminal records.
- `checker.py`: structural record/partition/fresh-evaluation verification.
- `verifier.py`: canonical config plus checker top-level verification.
- `provenance.py`, `identity.py`, `preflight.py`, `chain.py`: source, pilot, dependency and chain gates.
- `control_registry.py`: 168 control IDs mapped 1:1 to source assertions/tests.
- `CONTROL_TO_SOURCE_MAP.json.zlib.b85` + `CONTROL_MAP_MANIFEST.json`: canonical 168-entry source map with packed/canonical SHA-256 and sizes.
- `phase2_bridge.py`: executes the frozen Phase 2 fixtures through Phase 3 validators.

## Checker-only closed enum

Checker rejection reasons are deliberately outside the runner failure enum:

- `NONCANONICAL_ARTIFACT`
- `CONFIG_SCHEMA_VIOLATION`
- `LOGICAL_DEPENDENCY_VIOLATION`
- `FAILURE_TRANSITION_VIOLATION`
- `RECORD_GRAMMAR_VIOLATION`
- `FRONTIER_REDERIVATION_MISMATCH`
- `WINDOW_REDERIVATION_MISMATCH`
- `PREDICTOR_CONTEXT_MISMATCH`
- `COVERAGE_MANIFEST_VIOLATION`
- `FRESH_EVALUATION_FAIL`
- `SOURCE_IDENTITY_FAIL`
- `PILOT_IDENTITY_FAIL`
- `CHAIN_VIOLATION`
- `CERTIFICATION_WORD_VIOLATION`
- `CONTROL_MAPPING_VIOLATION`

These describe artifact rejection only and must never be serialized as §8.2 runner failure reasons.

## Tests

```bash
python run_phase3_tests.py --write-report
python static_audit.py
python run_phase3_fixture_bridge.py --write-report
```

The fixture bridge must be run from the repository checkout so it can read the Phase 2 packed fixtures. No test command imports Arb/flint or performs a kernel evaluation.

## Explicit exclusions

- No production adapter implementation is selected or pinned here.
- No production numeric config is fixed.
- No GitHub workflow is added or modified.
- No tag, PR, production run, Arb evaluation, or mathematical calculation is authorized.
- GitHub-side PASS output is a candidate report until chat-side independent audit.
