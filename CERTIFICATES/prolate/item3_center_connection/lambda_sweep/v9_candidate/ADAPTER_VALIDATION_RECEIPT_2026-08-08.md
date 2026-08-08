# Item 3 sweep v9 — adapter candidate validation receipt

**Date:** 2026-08-08  
**Status:** `VALIDATED_ADAPTER_CANDIDATE / NOT PRODUCTION APPROVED`

This receipt records the repository-hosted pinned-runtime audit of
`adapter_v9_candidate.py`.  It is not a production source approval, final v9 freeze, run
authorization, or `CERTIFIED_LAMBDA_RANGE`.

## Source identities

```text
adapter ID
  ITEM3_SWEEP_V9_MEAN_VALUE_ADAPTER_CANDIDATE_V1

adapter source SHA-256
  7504ad3e095291b12929506c810d03264ed3609bffd6ef1230efb5740a35ea8e

kernel ID
  ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2

kernel source SHA-256
  abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76
```

The kernel pre-import hash, post-import hash, and imported module origin all match the
pinned candidate source.

## Runtime environment

```text
Python       = 3.13.14
python-flint = 0.9.0
```

## Passed controls

The tracked runtime report records all controls as true, including:

- exact adapter ID;
- kernel pre/post hash identity and exact module origin;
- rejection of wrong kernel hash;
- rejection of checkout-root path escape;
- dual-association `INTERSECTION`;
- `DIRECT_ONLY`;
- `FACTORED_ONLY`;
- `NONFINITE`;
- fatal rejection of disjoint finite associations;
- full endpoint-ball containment for exact r/lambda input intervals;
- exact canonical r and lambda centers;
- restoration of global `ctx.dps` after evaluation;
- exactly seven F-level kernel calls for one mean-value cell;
- finite final `G_r`, `G_rr`, `G_rlambda` enclosures;
- finite exact split scores;
- strict NEG on the pinned difficult left cell.

## Pinned difficult-cell control

```text
r cell
  [1/64, 129/8192]          # width 2^-13

lambda box
  [123731943/26214400,118/25] # width 2^-20
```

The final mean-value upper endpoint is strictly negative.  All three quotient quantities
use the finite-overlap `INTERSECTION` association class on this control.

The F-level call counts are exactly

```text
F          2
F_r        2
F_lambda   1
F_rr       1
F_rlambda  1
TOTAL      7.
```

## Promotion effect

The adapter source is promoted only to

```text
VALIDATED_ADAPTER_CANDIDATE.
```

It may now serve as the source-bound mathematical adapter in runner/checker candidate
validation.  Production approval still requires the final runner/checker implementation,
source identity binding, >=256-leaf independent validation corpus, performance
qualification, canonical dependency entries, and the external v9 freeze receipt.
