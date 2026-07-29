# Item 3 adaptive λ sweep — Phase 2 calculation-free self-test

This directory implements only Phase 2 of frozen design blob
`cafbf7b661911995008dda49bfb3ecabcecb1f12`.

It contains no production runner, no Arb import, no kernel evaluation, no
workflow, no tag logic, no PR automation, and no mathematical calculation.

The five `.zlib.b85` files are compressed storage for fixed canonical JSON
bytes. `PACK_MANIFEST.json` pins both compressed bytes and reconstructed
canonical JSON bytes. `phase2_selftest.py` validates:

- all 168 `CONTROL_EXPECT` entries and their exact five-field shape;
- fixed control fixtures and expected outcomes;
- the closed §13 config schema;
- the §8.2–8.3 failure-transition table, including the v8.1 predictor-origin
  regeneration prohibition;
- the §9 record grammar paths;
- design blob identity before and after the run.

Run after checkout:

```text
python phase2_selftest.py --attestation DESIGN_BLOB_ATTESTATION.json --write-report
```

The GitHub-side PASS remains a candidate report until chat-side byte checking
and independent re-execution.
