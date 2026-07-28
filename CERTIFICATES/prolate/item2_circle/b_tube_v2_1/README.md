# B-TUBE v2.1 — schema/checker self-test only

This directory is the **calculation-free first commit** for the frozen B-TUBE
v2.1 contract. It contains no production prolate evaluation, no GitHub Actions
workflow, no observer write, and no GitHub API write code. The kernel in
`mock_kernel.py` is mathematically meaningless and is accepted only when
`mode == SELFTEST_ONLY`.

## Intended theorem interface

The later production B-TUBE node covers the exact parameter interval
`[lambda_start, 118/25]`. For each parameter cell it will certify:

1. existence from a parametric Krawczyk strict inclusion;
2. at-most-one root from `sup F_r < 0` on the physical tube;
3. exact JOIN identification by computing the positive-width intersection
   `J_i` at the common rational endpoint and requiring
   `K(J_i; lambda_i) strict-subset int(J_i)`;
4. continuity of the unique joined roots.

Real analyticity is deliberately absent from the machine conclusion. It remains
a paper-level implicit-function lemma recorded in `logical_dependencies.json`.

## Canonical numeric representation

Normative dyadics are integer pairs `(m,e)` representing `m * 2^(-e)`.
They are unique: zero is `(0,0)`, and a nonzero mantissa is odd whenever
`e > 0`. Enclosure containment is reduced to arbitrary-precision integer
comparison after exponent alignment. Decimal text is allowed only below a
`display` key and is ignored by the mathematical checker.

The Arb adapter uses only `mid().man_exp()` and `rad().man_exp()`. It forms
`mid - rad` and `mid + rad` by exact big-integer dyadic addition. It does not
format, parse, round, or call lower/upper endpoint functions. A coarse stored
radius is therefore preserved exactly as the radius Arb actually holds.

## Canonical record bytes

A record is hashed as the exact UTF-8 output of:

```python
json.dumps(
    record,
    ensure_ascii=True,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
).encode("utf-8")
```

Keys must be ASCII; duplicate keys, floating JSON numbers, BOM, CR, and record
newlines are forbidden. JSONL joins canonical record bytes with one LF and has
no final LF. `previous_record_sha256` hashes the prior canonical object bytes,
**not** its JSONL linefeed. The checker compares stored bytes against a fresh
canonical serialization before validating the chain.

## Affine evaluation rule

The only permitted rule is `exact_endpoint_convex_hull_v1`. An affine
predictor is stored by its two exact dyadic endpoint values. Its range on a
parameter cell is the exact convex hull of those endpoints. Evaluating an
interval expression `a*L+b` is prohibited.

The residual evaluation `F(q(lambda)+m, lambda)` can lose the correlation
between `q(lambda)` and `lambda`. This only widens the enclosure. If efficiency
becomes limiting, the prescribed remedies are parameter bisection, predictor
refresh, and tube-radius adjustment. A non-rigorous midpoint substitution is
never an allowed fallback.

## JOIN and boundary semantics

JOIN is performed on the exact operand

`J_i = (q_i^R + Y_i) intersection (q_(i+1)^L + Y_(i+1))`.

The checker first proves that `J_i` has positive width and then runs the
point-parameter Krawczyk calculation **on J_i itself**. Empty intersection and
Krawczyk-enclosure shrink are separate negative controls.

`CERTIFIED_CORE_INTERVAL` is permitted with `boundary_connection: DEFERRED`.
`CERTIFIED_B_TUBE_FULL` requires the pinned boundary dependency and an exact
Krawczyk interface with the first cell. The two verdicts cannot be mixed.
The first cell starts exactly at `lambda_start`; the final cell ends exactly at
`118/25`.

## Cross-item MATCH dependency

B-TUBE is an item-2 branch certificate with an intentional terminal dependency
on the canonical **item-3 C-G-TUBE** single-slice artifact. Directory or item
number similarity must not be used to substitute another artifact.

The self-test pins:

- C-G artifact ZIP SHA256
  `c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381`;
- C-G source head `1e0f671c91798b9c044c04c7a4224a21e1e67830`;
- C-G config SHA256
  `bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17`;
- exact match parameter `118/25` and root bracket `(1/64,11/256)`;
- equality of the B and C-G kernel SHA values;
- paper/interface lemma `F_G_FIXED_SLICE_IDENTITY_V1`.

Only after these identity pins pass does strict containment of the reconstructed
B-side match Krawczyk image in the C-G bracket identify the two roots.

## Precision invariant

`checker_dps >= dps` is mandatory. Equality is a positive boundary control;
`checker_dps < dps` is rejected. Dyadic parsing and containment remain precision
independent, while the invariant governs later rigorous kernel reconstruction.

## Run locally

From this directory:

```text
python -m unittest discover -s tests -v
python run_controls.py
python b_tube_selftest_runner.py --out /tmp/btube-selftest
python b_tube_checker.py /tmp/btube-selftest
```

## Frozen static-audit checklist

1. No decimal/float conversion path in the normative adapter.
2. Canonical dyadic unit tests and integer containment.
3. Exact `man_exp` midpoint/radius endpoint construction.
4. Canonical JSON bytes and JSONL LF discipline.
5. Chain hashes over canonical object bytes only.
6. JOIN computed and checked on exact `J_i`.
7. Empty JOIN and JOIN shrink are distinct controls.
8. Exact left and right parameter endpoints.
9. CORE/DEFERRED and FULL separation.
10. Both precision-boundary controls.
11. C-G artifact, kernel identity, and F/G lemma pins.
12. Every negative control rejected; no workflow or GitHub-write implementation.
