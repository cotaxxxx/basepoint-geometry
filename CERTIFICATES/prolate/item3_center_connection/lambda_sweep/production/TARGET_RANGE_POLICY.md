# Item 3 lambda sweep — target range policy

Status: `DIRECTION_CONFLICT_DOCUMENTED`

## Current frozen contract

The frozen v8.1 contract implements only a downward sweep:

```text
lambda_target < lambda_anchor = 118/25
covered interval = [lambda_target, lambda_anchor]
```

The first production-pipeline validation candidate is

```text
lambda_target = 483303/102400 = 118/25 - 2^-12
```

This short interval is only an end-to-end pipeline validation target. It is not the final mathematical coverage objective and it is not yet approved.

## Historical ledger phrase

The earlier ledger phrase `lambda_match -> a_c` points upward. The certified bracket

```text
a_c in [236219/50000, 472439/100000]
```

lies strictly above `lambda_anchor = 118/25`.

Therefore the frozen downward-only contract cannot implement coverage from the anchor toward `a_c`. No reinterpretation of `lambda_target`, endpoint order, or interval orientation is permitted.

## Required decision

The final coverage objective remains unresolved. If the mathematics requires upward extension from `118/25` toward `a_c`, that work requires:

1. a revised design contract with an upward or bidirectional frontier;
2. a new Phase 1 content audit and byte freeze;
3. new Phase 2 controls;
4. a new Phase 3 implementation audit;
5. a new Phase 4 workflow audit.

This document authorizes no run, tag, certification claim, or contract revision.
