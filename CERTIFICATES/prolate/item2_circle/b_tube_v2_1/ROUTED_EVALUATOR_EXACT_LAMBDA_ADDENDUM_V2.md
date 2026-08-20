# B-TUBE v2.1 — Exact Rational Lambda Transport Addendum V2

Status: **DESIGN DRAFT / UNPINNED**  
Authority: design addendum only  
Implementation, approval tag, calibration run, and result-bearing execution are **NOT authorized**.

This addendum modifies only the lambda-to-boundary-backend transport semantics of
`ROUTED_EVALUATOR_DESIGN_V1.md`.

All existing selector rules, route IDs, physical-tube semantics, Krawczyk semantics,
production-kernel pins, frozen B-LOCAL source pins, and certification boundaries remain unchanged
unless explicitly stated below.

---

## 1. Purpose

The routed evaluator must support exact rational lambda values that are not dyadic while preserving
the frozen B-LOCAL dyadic proof-domain invariant.

The obstruction is structural:

- `lambda_plus = 206539/100000` is non-dyadic;
- therefore lambda and `s = lambda - lambda_plus` cannot both be dyadic;
- consequently a proof design requiring exact dyadic representation of both coordinates is impossible.

This addendum resolves that incompatibility by separating:

1. an exact rational ledger layer; and
2. an outward-dyadic analytic enclosure layer.

No exact identity is replaced by an approximation.

---

## 2. Result-bearing domain

The routed result-bearing lambda domain is

`lambda_start <= lambda <= lambda_end`

with

- `lambda_start = 3307749/1600000`,
- `lambda_end = 118/25`,
- `lambda_plus = 206539/100000`.

Hence

`s = lambda - lambda_plus >= 1/512 = 2^-9 > 0`.

Negative `s` is outside the scope of this addendum.

---

## 3. Exact rational canonical encoding

Every normative rational value is encoded exactly as

`{"p":"<canonical integer>","q":"<canonical positive integer>"}`.

Required canonical rules:

1. `q > 0`.
2. `gcd(|p|,q) = 1`.
3. numerator and denominator use ASCII decimal digits only.
4. leading `+` is forbidden.
5. leading zeroes are forbidden except the single string `"0"`.
6. `"-0"` is forbidden.
7. equivalent but unreduced forms such as `2/4` are forbidden.

A rational interval is encoded as

`{"lo":<canonical rational>,"hi":<canonical rational>}`

and must satisfy exact `lo <= hi`.

A point interval is represented by identical canonical rational objects at `lo` and `hi`.

The checker must parse and re-encode every normative rational object and require canonical-byte
agreement. Numerical equality alone is insufficient.

For byte-level canonicality, this addendum adopts the existing calibration canonical JSON bytes
contract: ASCII-safe JSON encoding, deterministic key ordering, and compact separators equivalent to
`ensure_ascii=True`, `sort_keys=True`, and `separators=(",", ":")`, with nonfinite numeric constants
and floating JSON numbers forbidden. The checker must require equality with those canonical JSON
bytes, not merely object-level equivalence. Consequently the physical byte order of object keys such
as `hi/lo` and `p/q` is determined by the existing sorted-key canonicalizer.

Noncanonical rational encodings are mandatory negative controls.

---

## 4. Two-layer lambda contract

### 4.1 Ledger layer

The authoritative input domain is an exact rational interval

`L = [lambda_0, lambda_1]`.

Exact identities, including:

- the final B-LOCAL `lambda_start`,
- every normative bridge lambda,
- `lambda_end = 118/25`,
- terminal C-G/MATCH identities,

are evaluated only from this ledger representation.

An Arb ball, dyadic reconstruction of an Arb ball, decimal string, or producer-reassembled lambda
must never replace the authoritative exact rational input.

### 4.2 Analytic layer

Using the pinned exact rational constant `lambda_plus`, independently compute

`s_0 = lambda_0 - lambda_plus`  
`s_1 = lambda_1 - lambda_plus`.

These exact rationals are then mapped outward to the fixed dyadic lattice defined in Section 5.

Only the resulting outward dyadic interval is supplied to the frozen B-LOCAL analytic route.

---

## 5. Normative outward-rounding semantics

Set

`ROUNDING_BITS = 192`.

This is a fixed-point lattice with spacing exactly `2^-192`.

It is **NOT** a significant-bits or relative-precision convention.

For exact rational `q`, define

`floor_192(q) = floor(q * 2^192) / 2^192`

and

`ceil_192(q) = ceil(q * 2^192) / 2^192`.

The normative implementation semantics are exactly those of the pinned frozen B-LOCAL model
functions:

- `floor_dyadic(q, 192)`
- `ceil_dyadic(q, 192)`.

These frozen functions operate directly on exact `Fraction`/rational input by integer arithmetic at
scale `1 << bits`; they do not pass the input through `dyadic_json` and therefore do not require the
input rational itself to be dyadic. The dyadic restriction applies to the produced lattice endpoint,
not to the exact rational supplied to the floor/ceil operation.

The analytic `s` interval is

`S = [floor_192(s_0), ceil_192(s_1)]`.

Therefore

`[s_0,s_1] subseteq S`

constructively.

For each endpoint the outward enlargement is strictly less than `2^-192`; consequently total
interval-width enlargement is strictly less than `2^-191`.

The checker independently reconstructs `S` through the pinned rounding semantics and requires
bit-exact equality with the producer record.

---

## 6. Frozen s-native boundary route

The frozen B-LOCAL source remains byte-invariant.

The result-bearing routed proof path must call the existing s-native backend:

- for `F`: the frozen common `enclose_route("F", ..., u0,u1,s0,s1, ...)`;
- for `F_r`: frozen `enclose_hu(...,u0,u1,s0,s1,...)`, followed by the already-pinned exact
  `H_U -> -F_r` interval negation.

The lambda-native frozen helper `enclose_f(...)` is forbidden in the result-bearing routed proof
path.

This prohibition has two independent gates:

1. static proof-path source scan shows zero prohibited `enclose_f` references;
2. runtime negative control rejects any attempted result-bearing use of that path.

No frozen B-LOCAL source byte may be modified to implement this addendum.

---

## 7. Bridge semantics

Design V1 described the bridge as exact-point evaluation by both backends.

Under this addendum:

- the interior backend remains evaluated at the exact normative lambda point;
- the boundary backend evaluates the deterministic outward `S` enclosure that contains that exact
  lambda point after reconstruction through `lambda_plus`.

Thus the boundary enclosure is an enclosure over a small lambda neighborhood containing the
normative point.

This is a deliberate normative semantic change.

It is rigorous because the exact point lies inside the supplied analytic enclosure.

The bridge PASS condition remains unchanged:

the interior enclosure and boundary enclosure for each required quantity must have nonempty exact
intersection.

No point may be removed and no enclosure may be narrowed after evaluation.

---

## 8. Normative routed trace evidence

Every result-bearing boundary evaluation must record at least:

- `lambda_exact_interval`
- `lambda_plus`
- `s_exact_interval`
- `s_outward_dyadic_interval`
- `rounding_bits`
- `rounding_rule_id`
- exact lower rounding enlargement
- exact upper rounding enlargement
- routed quantity
- route ID
- frozen dependency pins
- boundary proof ID
- boundary evaluation count

The legacy Arb-derived `lambda_interval`, if retained for diagnostic compatibility, is
non-authoritative evidence only.

It must never substitute for `lambda_exact_interval`.

---

## 9. Independent checker reconstruction

The checker must independently:

1. parse canonical exact `lambda_exact_interval`;
2. reconstruct the pinned exact `lambda_plus`;
3. compute exact rational `s_0,s_1`;
4. reconstruct `S` using the pinned 192-bit fixed-lattice floor/ceil semantics;
5. require bit-exact equality with the recorded producer `S`;
6. verify exact containment

   `lambda_exact_interval subseteq lambda_plus + S`;

7. independently reconstruct route selection;
8. independently reconstruct the `H_U -> -F_r` transform;
9. verify frozen source/config pins;
10. verify boundary evaluation counts and budgets.

Producer-supplied reconstructed lambda, s, or S values are evidence only and never trusted decision
inputs.

---

## 10. Frozen non-contact invariant

Any implementation based on this addendum is rejected unless all frozen B-LOCAL dependencies remain
byte-identical.

The implementation audit must mechanically verify zero byte changes to:

- `dependencies/blocal_v22_source/*`
- the frozen B-LOCAL config
- all existing frozen B-LOCAL SHA-pinned members.

Existing frozen SHA pin values must remain unchanged.

The implementation may add new audited glue outside the frozen set, but that glue must have its own
source pin and independent checker reconstruction.

---

## 11. Mandatory positive controls

Three real-value positive controls are required.

### 11.1 Start point

`lambda = 3307749/1600000`

gives exactly

`s = 1/512 = 2^-9`.

Required result:

- exact ledger identity preserved;
- outward rounding enlargement exactly zero;
- real routed A0B boundary path executes without non-dyadic serialization failure.

### 11.2 Bridge representative

At minimum test

`lambda = 17/8`

with

`s = 5961/100000`.

Required result:

- exact non-dyadic `s` preserved in ledger evidence;
- deterministic outward dyadic `S` reconstructed independently;
- exact lambda lies inside `lambda_plus + S`;
- bridge boundary evaluation completes through the s-native route.

### 11.3 Terminal point

`lambda = 118/25`

with

`s = 265461/100000`.

Required result:

- exact terminal/MATCH identity remains ledger-exact;
- analytic boundary call uses only outward `S`;
- no non-dyadic serialization failure occurs.

---

## 12. Mandatory negative controls

The checker or static/runtime guard suite must reject at least:

1. noncanonical rational encoding;
2. modified exact lambda;
3. modified `lambda_plus`;
4. modified exact `s`;
5. inward-rounded `S`;
6. one-ulp modified `S` endpoint;
7. modified `rounding_bits`;
8. any record for which

   `lambda_exact_interval` is not contained in `lambda_plus + S`;

9. producer-assembled lambda used as authoritative checker input;
10. result-bearing `enclose_f` use;
11. frozen source SHA mismatch;
12. frozen config SHA mismatch;
13. a producer-supplied S not equal to independent checker reconstruction.

Existing routed-selector, straddle, fallback, bridge-intersection, budget, and negation negative
controls remain in force.

---

## 13. Rounding-margin accounting

Every result-bearing boundary call must record the exact outward enlargement introduced by the
lambda-to-S transport.

The global design bound is

`added s-interval width < 2^-191`

per transported interval.

This quantity may be numerically negligible but must not be omitted from the proof ledger.

Any later margin argument must explicitly account for it.

---

## 14. Design-audit gates

Before implementation authorization, this addendum must pass all established audit axes.

### Existing four axes

1. exactness;
2. checker-side independent reconstruction;
3. no weakening of existing dyadic invariants;
4. applicable negative-control rejection of producer-assembled coordinate data.

### Additional fixed axes

(a) rounding semantics are pinned and deterministically reconstructed;

(b) the bridge semantic change is explicit and normative;

(c) frozen B-LOCAL non-contact is machine-verifiable;

(d) positive controls cover lambda_start, one bridge point, and lambda_end.

Additionally, result-bearing `enclose_f` exclusion must pass both static and runtime controls.

---

## 15. Pinning and lifecycle

This document is initially placed as:

`DESIGN DRAFT / UNPINNED`.

The required lifecycle is:

1. place draft;
2. perform chat design audit;
3. apply all audit corrections;
4. declare DESIGN GREEN;
5. compute SHA-256 of the final immutable addendum bytes;
6. pin that SHA independently in both:
   - calibration config; and
   - calibration model constant;
7. freeze the addendum bytes;
8. begin implementation.

No addendum SHA may be treated as normative before DESIGN GREEN.

Changing the addendum after the dual pin requires a new version/addendum and a new audit cycle.

---

## 16. Authorization boundary

This addendum authorizes no implementation commit, tag, workflow run, calibration run, result claim,
or certification claim.

Until the lifecycle in Section 15 reaches implementation authorization:

- branch status remains NOT GREEN;
- approval tag is prohibited;
- result-bearing calibration execution is prohibited.
