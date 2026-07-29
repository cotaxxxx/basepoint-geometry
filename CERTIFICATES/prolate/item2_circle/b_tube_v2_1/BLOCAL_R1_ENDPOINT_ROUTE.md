# B-LOCAL v2.1 — r=1 endpoint evaluation route

Status: **IMPLEMENTED; MATHEMATICAL RUN NOT AUTHORIZED**

## Selected route

The normative L3 endpoint route is **Route A**:

```text
F_arb(r=1, lambda interval)
```

The call is made through the same pinned clean-room module used for L1 and L2:

```text
CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py
SHA-256 77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac
```

No separately implemented `B_arb` is admitted. This follows the frozen design's
requirement that `B(lambda)=F(1,lambda)` use the same pinned regularized F/F_r
source selected for B-LOCAL. It also avoids introducing a second normative
boundary implementation and a second provenance edge.

## Runtime acceptance contract

Route A is accepted only when all of the following hold:

1. the kernel file is contained under the repository root, is not a symlink,
   matches the pinned SHA-256 before import, resolves as the imported module's
   exact `__file__`, and matches the same SHA-256 after import;
2. `FORMULA_STATE` is `FILLED`, and `F_arb` and `dFdr_arb` are callables defined
   by that exact imported module;
3. L3 calls `F_arb` with exact integer `r=1`, not a binary float and not an
   inward perturbation;
4. the returned object has the expected Arb type and its midpoint/radius expose
   finite exact `man_exp()` data;
5. the pinned `ARB_TO_CANONICAL_DYADIC_INTERVAL_V1` adapter produces a canonical
   finite dyadic enclosure;
6. the enclosure's upper endpoint is strictly negative for an L3 leaf.

A failure of any item is fail-closed. It produces an unresolved/incomplete
candidate or aborts on a provenance/API violation.

## Prohibited alternatives

- No `1-epsilon` evaluation is permitted.
- No boundary-only implementation is imported.
- No `B_arb` identity route is used as a silent substitute.
- No exception handler retries through another formula or module.
- No NaN/infinite display string is parsed or converted.
- No decimal string or Python `float` enters a proof decision.

## Phase-4 test boundary

The Phase-4 static test verifies source structure, route identity, exact-r API
construction, pin checks, and absence of fallback/epsilon paths. It does not
import the production kernel and performs no numerical kernel evaluation. The
tag-only workflow is present but no tag or workflow run is authorized by this
implementation commit.
