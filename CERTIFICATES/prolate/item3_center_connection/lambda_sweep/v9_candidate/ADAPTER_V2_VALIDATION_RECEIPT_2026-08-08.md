# Item 3 sweep v9 — adapter candidate v2 validation receipt

**Date:** 2026-08-08  
**Status:** `VALIDATED_ADAPTER_CANDIDATE_V2 / NOT PRODUCTION APPROVED`

This receipt supersedes adapter V1 for subsequent runner/checker candidate work.  V1
remains immutable provenance.

## Identities

```text
adapter ID
  ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V2

adapter source SHA-256
  8a52b7bfa9491976df2ece4f3858a8bc4b4350222c60840c82fff92e0a05913b

kernel ID
  ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2

kernel source SHA-256
  abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76
```

Runtime environment: Python 3.13.14, python-flint 0.9.0.

## V2 delta

V2 preserves the validated source-bound seven-call mean-value path and adds the public
rigorous method

```text
evaluate_g(r_cell, lambda_box, dps)
```

for `G=F/r`.  Runner/checker source therefore need not access the pinned kernel or adapter
private methods to establish endpoint signs.

## Passed endpoint controls on the exact rehearsal lambda box

For

```text
Lambda = [123731943/26214400,118/25]
```

the audit gives strict rigorous signs

```text
G(1/64,Lambda)   > 0
G(11/256,Lambda) < 0.
```

Thus the candidate S1/S2 endpoints are already validated at dps 50 for the first
rehearsal box.

## Other passed controls

All V1 source identity, path escape, exact endpoint containment, dual association,
canonical center, global-dps restoration, seven-call mean-value, finite derivative score,
and known-left-cell strict NEG controls also pass under V2.

## Promotion effect

Adapter V2 is the only adapter candidate to be used by successor runner/checker candidate
validation unless a new explicit adapter version is created.  Its state is

```text
VALIDATED_ADAPTER_CANDIDATE_V2
```

and not production approval.  Any change to the adapter source SHA invalidates this
receipt for the successor bytes.
