# Item 3 sweep v9 — checkpoint hash-separation repair receipt

Status: **BLOCKER 1 FOCUSED CONTROLS PASS / FULL REQUALIFICATION REQUIRED / FREEZE NOT AUTHORIZED**

Date: 2026-08-08

This repair separates host-dependent checkpoint provenance from canonical mathematical shard evidence. `SHARD_EVIDENCE_CANDIDATE.json` now uses schema `ITEM3_SWEEP_V9_SHARD_EVIDENCE_CANDIDATE_V2` and contains no checkpoint count, tip, ledger hash or timing field. The source-bound driver writes a separate canonical `ITEM3_SWEEP_V9_SHARD_PROVENANCE_V1` object bound to the exact mathematical evidence SHA-256.

The aggregate verifier independently revalidates the provenance ledger, previous-line hash chain, immutable payload hashes, frontier digest and run-context bindings, but the provenance object/hash is never inserted into `selected_shard_evidence_sha256`, the selected chain preimage, or the aggregate mathematical verdict.

The integrated contract candidate v2 is updated to state this separation explicitly. All earlier qualification evidence remains provenance for its old byte identity only.

Blocker 2 (independent 256-leaf validation strength) and Blocker 3 (FLINT library version provenance) remain open. No freeze, rehearsal tag, production tag or `CERTIFIED_LAMBDA_RANGE` is authorized by this repair.
