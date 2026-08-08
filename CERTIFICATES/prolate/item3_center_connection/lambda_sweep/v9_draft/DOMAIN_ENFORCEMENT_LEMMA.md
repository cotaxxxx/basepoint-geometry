# Item 3 sweep v9 — refinement domain-enforcement lemma

**Status:** `CONTRACT LEMMA PROVED / FINAL SOURCE CHECK PENDING`  
**Date:** 2026-08-08

## 1. Purpose

The analytic derivative theorem requires every real kernel call to lie in

```text
0 < r < 1,
1 <= lambda < infinity.
```

This lemma shows that the frozen midpoint-refinement architecture preserves that domain
once the root intervals satisfy it. Final source approval must still verify that the
runner creates no cell through another path.

## 2. Immediate rehearsal roots

The inherited pilot/root window is

```text
R0 = [1/64, 11/256].
```

The rehearsal lambda interval is

```text
L0 = [123731943/26214400, 118/25].
```

Exactly,

```text
0 < 1/64 < 11/256 < 1,
1 < 123731943/26214400 < 118/25.
```

Therefore

```text
R0 subset (0,1),
L0 subset (1,infinity).
```

## 3. Midpoint-child invariance

Let a closed exact interval be

```text
J=[a,b],  a<b,
```

and let

```text
m=(a+b)/2.
```

The frozen refinement operation produces only

```text
J_lower=[a,m],
J_upper=[m,b].
```

Since `a<m<b`, both children are subsets of the parent:

```text
J_lower subset J,
J_upper subset J.
```

By induction on split depth, every descendant of a root interval is a subset of that
root interval.

The argument is exact and does not use floating-point arithmetic.

## 4. Application to r refinement

If the final runner obtains every r cell solely by repeated application of the frozen
exact midpoint-child operation starting from `R0`, then every r cell satisfies

```text
1/64 <= r_lo <= r_hi <= 11/256 < 1.
```

In particular:

- no cell contains `r=0`;
- every division by `r`, `r^2`, or `r^3` in the quotient layer is well-defined;
- the analytic lower bound `q >= (1-r)^2` is uniformly positive;
- the real analytic derivative theorem applies to every descendant cell.

## 5. Application to lambda refinement

If each rehearsal shard is an exact subinterval of `L0` and every lambda refinement is an
exact midpoint child, every descendant lambda box is a subset of `L0` and therefore
satisfies

```text
1 < lambda_lo <= lambda_hi <= 118/25.
```

The multi-run aggregate verifier separately enforces exact shard union and endpoint
identity; execution packaging cannot enlarge the mathematical lambda domain.

## 6. Required final static controls

The final static audit must reject source unless all of the following are true:

1. the root r interval is read from the approved config/identity and equals the approved
   canonical interval;
2. every created r child is produced by the frozen exact midpoint operation;
3. no padding, extrapolation, heuristic window expansion, float conversion, or arbitrary
   interior interval construction can create a kernel r cell;
4. each lambda shard is first checked as a canonical exact subinterval of the approved
   rehearsal range;
5. every lambda child is produced by the frozen exact midpoint operation;
6. runner and checker independently verify the same root and child containment rules;
7. evidence records parent IDs and exact endpoints so the checker can reconstruct the
   inclusion tree.

If a future design intentionally permits window translation or expansion, this lemma no
longer suffices and the analytic domain must be rechecked for that operation.

## 7. Status effect

At the contract/mathematical level, domain preservation under the currently frozen
midpoint refinement is resolved.

At the implementation level, domain enforcement remains

```text
STATIC SOURCE CHECK PENDING.
```

No production authorization follows from this lemma alone.
