# Item 6 interval-constructor re-audit gate

Status: **RE-AUDIT REQUIRED / FINAL ASSEMBLY BLOCKED**

Date: 2026-08-08

## Baseline

The item-6 branch was independently reviewed through source head
`8eff42b26c8644de9e6047715e2bef19075e7605` before this repair sequence.

The historical runtime audit accepted endpoint **overlap** as evidence for the exact-rational
Arb interval constructor. That predicate is weaker than the stated conclusion that the
constructed ball encloses the full rational interval.

## Corrected acceptance rule

The production constructor

```text
arb(str((lo + hi) / 2), str((hi - lo) / 2))
```

is now audited by the strict requirement that the resulting ball contain the complete
`arb(str(lo))` and `arb(str(hi))` endpoint balls. Overlap is retained only as diagnostic
information and cannot produce `PASSED`.

The strengthened audit source is
`prolate_axis_interval_constructor_audit.py`.

The tracked JSON result has intentionally been changed to `REAUDIT_REQUIRED`; the former
`PASSED` record is not a current result under the strengthened predicate.

## Certification effect

This correction does **not** by itself revoke `C-HESSIAN`, `C-1`, `P-BOUNDARY`, or
`P-MODULUS`. Their existing records remain archived evidence.

However, no new item-6 freeze, dependency-DAG completion, or full theorem assembly may use
the interval-constructor audit as a satisfied gate until all of the following hold:

1. the strengthened audit is executed with `python-flint==0.9.0`;
2. every audit case reports `contains_lo=true` and `contains_hi=true`;
3. every strictly positive audit interval excludes zero;
4. no historical direct-fmpq midpoint/radius constructor remains in production item-6
   sources;
5. the generated JSON reports `status=PASSED`.

If any containment check fails, the affected constructor and every dependent certificate
path must be traced before further certification claims are made.

## State-document rule

The `Current workflow state` paragraph in the older `STATUS.md` is historical because it
is pinned to `c2534aec269263a0a585c374ad5f25d71fae9651`. This re-audit gate and later
explicit audit records take precedence for workstream state after that baseline. The
mathematical theorem remains **NOT CERTIFIED** until the existing dependency-DAG open nodes
are closed.
