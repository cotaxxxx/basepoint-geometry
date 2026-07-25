# Independent audit of item 0d

Audit date: 2026-07-25

## Hashes

- delivery ZIP SHA-256:
  `db1c68e4bbf43fcb49bd5f27de5d45a36b44f1f8e77141477832ce16ae68df2`
- combined certificate SHA-256:
  `9961090dffca4c78eeca51d5aa97e1d72a71e62b67709396cdd6eb6b856d31a8`

Both equal the values reported at delivery.

## Leaf audit

The archive contains:

- `checkpoint_0d.json`: 118 certified driver leaves
- `mixed_queue_0d.json`: 80 certified mixed-runner records; queue empty
- `riemann_0d.json` and `riemann_patch_0d.json`: 26 certified Riemann records

Total: `118 + 80 + 26 = 224` leaves.

For every leaf, the stored result has `positive_certified = true`. The driver pending list, terminal-failure list, and mixed queue are empty.

## Exact coverage audit

All rational endpoints from the 224 leaves generate:

- 25 atomic `r` intervals
- 38 atomic `lambda` intervals
- 950 atomic cells

Using exact rational midpoint membership:

- uncovered cells: 0
- cells covered by more than one leaf: 0
- sum of leaf areas:
  `319617/1000000`
- exact domain area:
  `(3/4-9/20)(206539/100000-1) = 319617/1000000`

Thus the leaves form an exact disjoint cover of the claimed rectangle.

## Run-signature analysis

`checkpoint_0d.json` stores the run signature

```json
{"format_version":2,"stage":"0d","quantity":"F","domain":{"r":["9/20","3/4"],"lambda":["1","206539/100000"]},"initial_grid":[7,11]}
```

This object is exactly equal to the corresponding subset of `metadata` when compared as parsed JSON objects.

A canonical JSON serialization using sorted keys and separators `(',', ':')` has SHA-256

`671c9579802c065f23eaaabdcd74542b8af373671c5686a3aeef1f06508205a7`.

Therefore no internal argument disagreement was found. A signature mismatch produced by an external resume/driver layer is most likely caused by one of the following:

1. signing different field sets, such as including `requested_sign`, `theorem`, or `settings` on only one side;
2. relying on dictionary insertion order rather than sorted-key canonical JSON;
3. normalizing exact rationals differently, for example `3/4` versus `0.75`;
4. using tuple/list or integer/string representations inconsistently.

Recommended rule: construct a fixed signature schema, normalize every rational to a reduced `p/q` string, and hash canonical sorted-key JSON. The signature warning does not affect the completed leaf signs or exact coverage proof recorded in this archive.
