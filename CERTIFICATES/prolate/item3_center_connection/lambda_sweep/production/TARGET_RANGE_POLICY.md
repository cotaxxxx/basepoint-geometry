# Item 3 lambda sweep — target range policy

Status: `V9_REHEARSAL_RANGE_RESOLVED / FINAL_GLOBAL_DIRECTION_UNRESOLVED`

## 1. Exact v9 rehearsal range

The current approved v8.1 production config records

```text
lambda_anchor = 118/25
lambda_target = 123731943/26214400
```

and these satisfy the exact identity

```text
118/25 - 123731943/26214400 = 1/1048576 = 2^-20.
```

Therefore the minimal connected range for the first v9 end-to-end production rehearsal is
frozen for planning as

```text
R_rehearsal = [123731943/26214400, 118/25].
```

This is a downward connected interval of exact width `2^-20`. It is the immediate
single-range rehearsal target only. It is not a claim of final mathematical coverage and
it does not authorize a workflow run, production tag, certification, or config change.

The earlier `2^-12` candidate mentioned in historical planning is superseded for the v9
rehearsal by the exact range encoded in the current production config.

## 2. No silent widening or orientation change

The rehearsal may not silently:

- move either endpoint;
- widen beyond `R_rehearsal`;
- reverse the sweep orientation;
- reinterpret the lower endpoint as an upward target;
- substitute a decimal approximation for either rational endpoint.

Any changed range requires a new explicit config identity and the corresponding audit and
approval path.

## 3. Multi-run partitioning

A multi-run rehearsal may partition `R_rehearsal` into exact canonical rational shards,
provided that the final aggregate verifier establishes all of the following:

1. every shard lies inside `R_rehearsal`;
2. adjacent shard endpoints are byte-identical canonical rationals;
3. the shard interiors are pairwise disjoint;
4. the exact union is all of `R_rehearsal` with no gap;
5. every selected shard attempt passes its own fresh checker;
6. the aggregate evidence satisfies the v9 multi-run chain contract.

Partitioning changes execution packaging, not the mathematical target interval.

## 4. Historical upward objective

The earlier ledger phrase `lambda_match -> a_c` points upward. The certified bracket

```text
a_c in [236219/50000, 472439/100000]
```

lies strictly above

```text
lambda_anchor = 118/25.
```

The frozen v8.1 downward-only contract cannot implement coverage from the anchor toward
`a_c`. The v9 rehearsal deliberately does not resolve that global direction question.

If the later mathematical objective requires upward extension from `118/25` toward
`a_c`, that work requires an explicit upward or bidirectional contract and a fresh audit
cycle. It cannot inherit authorization from the `2^-20` downward rehearsal.

## 5. Failure rule

Failure or incompletion anywhere inside `R_rehearsal` leaves the aggregate status
`NOT_CERTIFIED` or `INCOMPLETE`, as appropriate. A failed rehearsal may motivate a
contract revision, but it may not be converted into a certified range by dropping a
failed shard, shrinking the target after execution, or reclassifying partial evidence.
