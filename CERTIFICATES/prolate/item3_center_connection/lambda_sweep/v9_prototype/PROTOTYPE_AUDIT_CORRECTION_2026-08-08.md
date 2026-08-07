# Item 3 sweep v9 prototype audit — correction record

**Status:** `AUDIT CORRECTION / PROTOTYPE STILL NOT APPROVED`  
**Date:** 2026-08-08

This record preserves the 2026-08-01 `PROTOTYPE_AUDIT.md` as historical audit evidence
while correcting two status/provenance statements that are not suitable for the next
freeze cycle.

## 1. Reproducible scope

The prototype implementation delta is measured between the explicit refs

```text
base = b82c00f2f154f131e02e122efdb156592fa98070
head = bb990b552d47af8788b5622b29af9dbaad4cf2f1
```

Repository compare result:

```text
10 commits
8 changed files
```

The older `11 commits / 10 changed files` phrase did not specify its base ref and is not
reproducible as a normative scope statement. It remains historical prose only.

Any later workstream-control documents or audit repairs after `bb990b...` are separate
changes and do not alter the pinned prototype implementation scope.

## 2. Stale open-decision list

The older audit's final `Remaining SPEC_PENDING work before v9 freeze` list incorrectly
reintroduced the split-score upper-bound form and normative tie-break as open decisions.
For the current workstream, the following are already frozen by the v9 design controls:

```text
S_r      = radius(I) * absmax(G_rr(I,Lambda))
S_lambda = radius(Lambda) * absmax(G_rlambda(I,Lambda))
NONFINITE outranks finite
larger exact finite score wins
exact tie selects r
dps 50 controls the partition
dps 70 independently verifies accepted cells and cannot change the partition
```

Those items must not appear in the final freeze blocker list.

## 3. What remains unchanged

This correction does not upgrade the prototype. The derivative kernel and mean-value core
remain non-production until the unresolved analytic, independent-validation, source-pinning,
evidence-schema, checkpoint, ordering, and performance gates are closed.

The measured prototype timings and width diagnostics remain planning evidence only. They
are not mathematical certificates and do not authorize a production run.

## 4. Controlling follow-up

`../v9_draft/FREEZE_DELTA_2026-08-08.md` records the current exact rehearsal range,
multi-run chain semantics, failure rules, and remaining freeze blockers.
