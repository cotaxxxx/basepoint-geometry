# v9 Clean-Room Independent Validation Plan

**Status:** `DRAFT / SPEC_PENDING`  
**Issue:** #20  
**Scope:** validation design for a future five-output rigorous derivative kernel and
two-variable mean-value adapter. This file does not validate an implementation.

## 1. Validation objective

The future source must establish rigorous enclosures for

```text
F, F_r, F_λ, F_rr, F_rλ
```

and support independently replayable enclosures for

```text
G_r, G_rr, G_rλ,
G_rr(I,Λ)(I-r0),
G_rλ(I,Λ)(Λ-λ0),
MV(I,Λ).
```

The validation must be at least comparable in independence and adversarial strength to
the existing 224-leaf validation. “224-leaf-equivalent” is a minimum structural target,
not permission to copy an old fixture set that does not exercise the new derivatives.

## 2. Independence model

The validation package shall separate:

1. **derivation authoring path** — produces the analytic formulas;
2. **production source authoring path** — implements rigorous integration;
3. **independent validation path** — rederives formulas and controls without importing
   production derivative expressions;
4. **runner adapter path** — constructs v9 enclosures;
5. **checker adapter path** — fresh instance and independent calls;
6. **static audit path** — verifies source boundaries, hashes, imports, and prohibited
   shortcuts.

A shared low-level interval library is allowed. Shared handwritten derivative
expressions are not independent validation.

## 3. Derivation and deterministic-control review

Before code testing, an independent derivation shall verify:

- fixed integration domain;
- formulas for `∂_λ Φ`, `∂_rr Φ`, and `∂_rλ Φ`;
- commutation of mixed derivatives where used;
- endpoint and branch treatment;
- denominator positivity;
- domination/interchange theorem;
- quotient identities for `G_rr` and `G_rλ`;
- valid parameter domain;
- exact midpoint closure: dyadic r endpoints produce canonical dyadic `r0`, and rational
  λ endpoints produce canonical reduced-rational `λ0`;
- exact score definitions
  `S_r = radius(I) absmax(G_rr(I,Λ))` and
  `S_λ = radius(Λ) absmax(G_rλ(I,Λ))`;
- the total axis order: splittable-only candidates, nonfinite over finite, larger exact
  finite score, and exact tie to `r`;
- separation of dps-50 partition control from dps-70 accepted-cell verification.

The review output shall identify each mathematical term and deterministic rule by a
stable ID and map it to source only after the derivation is frozen.

## 4. Positive controls

Positive controls shall include at least:

1. exact or semi-exact calibration cases where a derivative sign or value enclosure is
   independently known;
2. point boxes and narrow boxes;
3. boxes crossing representative internal subdivisions of the integration domain;
4. both signs and near-zero cases for each derivative output where mathematically
   available;
5. finite `G_rr` and `G_rλ` boxes producing a strict `NEG` mean-value result;
6. a case where raw `G_r(I,Λ)` is too wide but the v9 mean-value result is `NEG`;
7. a case where λ correction is materially nonzero;
8. exact canonical midpoint rederivation from differently scaled but equivalent endpoint
   construction paths;
9. each split-selection branch: only-r splittable, only-λ splittable, nonfinite-r,
   nonfinite-λ, larger-r, larger-λ, finite tie to r, and double-nonfinite tie to r;
10. runner/checker partition agreement from independent dps-50 calls;
11. dps-70 accepted-cell verification without partition mutation;
12. cancellation-safe checkpoint recovery through the last complete attempt;
13. deterministic repetition producing identical canonical evidence bytes.

## 5. Negative and mutation controls

The control corpus shall reject at least the following attacks.

### Analytic identity attacks

- omit `2F/r^3` from `G_rr`;
- use `-F_r/r^2` instead of `-2F_r/r^2`;
- omit `-F_λ/r^2` from `G_rλ`;
- substitute `F_rλ` for `F_λ`;
- reverse a derivative sign;
- evaluate a derivative on a point when the contract requires a box;
- use a derivative enclosure that does not cover the entire rectangle.

### Mean-value and center attacks

- omit the λ correction;
- omit the r correction;
- use an arbitrary interior center;
- use a floating-point or printed-decimal midpoint;
- retain an unreduced rational center;
- use a stale center or stale offsets after subdivision;
- accept an evidence center not byte-identical to the checker-rederived center;
- accept `sup(MV)=0` as negative;
- accept a nonfinite interval;
- reuse a parent enclosure for a child without a valid containment rule.

### Split-tree attacks

- calculate a split score from midpoint floats or display strings;
- compare finite scores approximately;
- rank finite over nonfinite;
- include an unsplittable axis as a candidate;
- select λ on an exact finite tie;
- select λ when both scores are nonfinite and both axes are splittable;
- use dps-70 checker values to select or alter the split tree;
- trust runner-recorded scores, candidate flags, axis, or split point;
- reorder children after the final child-order policy is frozen.

### Independence attacks

- checker imports runner evidence as its fresh value;
- checker and runner share an adapter object or memoization cache;
- production derivative expression is copied into the “independent” oracle;
- source hash is checked before import but not after import;
- dynamic import resolves outside the pinned checkout;
- a diagnostic finite difference is promoted to a proof result.

### Evidence attacks

- duplicate key, unknown field, CRLF, missing required LF;
- stale config or logical dependency hash;
- broken record or checkpoint chain;
- partial checkpoint claiming completion;
- mismatched frontier digest;
- truncated JSONL tail accepted as a complete line;
- path or symlink escape;
- counter rollback or derivative-key substitution.

## 6. Rigorous inclusion tests

For a controlled collection of boxes, independently subdivide `I × Λ` into a much finer
partition. Verify that every fine-box direct rigorous `G_r` enclosure is contained in
the v9 coarse-box `MV` enclosure. This is a validation of implementation containment,
not a substitute for the analytic theorem.

The suite shall include:

- narrow and broad λ boxes;
- small and large r cells;
- boxes near any difficult integration subdomain;
- boxes producing narrow and wide derivative intervals;
- boxes with nonfinite intermediate forms that become finite after subdivision;
- boxes that remain unsplittable and terminate fail closed.

## 7. Diagnostic derivative comparisons

High-precision centered finite differences and symbolic or automatic differentiation
may be used only as diagnostics. The plan shall compare each new derivative across a
representative grid and report absolute and relative discrepancies together with the
rigorous enclosure.

Passing diagnostics cannot produce `VALIDATED`. Failing diagnostics blocks validation
until explained.

## 8. Leaf-equivalent corpus

The future validation proposal shall define a concrete corpus with at least 224
independently identified leaves. A “leaf” is one expected control outcome bound to:

```text
control ID
input domain
source/derivation identity
expected terminal class
expected failure reason or containment predicate
```

Because five kernel outputs and mixed-coordinate logic are new, the likely adequate
corpus is larger than 224. The final count shall be based on coverage classes, not on
padding repeated cases.

## 9. Static audit

The static audit shall establish:

- only the approved adapter imports the interval kernel;
- no finite-difference module appears in production imports;
- no network, subprocess, dynamic package installation, or unpinned source load;
- every published derivative function is present and source-pinned;
- runner and checker instantiate separate adapters;
- partition-control code uses exactly dps 50 in runner and checker;
- dps-70 verification code cannot mutate the partition;
- center and score comparisons contain no float conversion;
- checkpoint code cannot set a mathematical verdict;
- expression IDs and operation order are frozen;
- all production Python parses;
- workflow actions and runtime versions are pinned under the final policy;
- no source contains an unauthorized certification declaration.

## 10. Performance-aware validation

Validation shall measure, but not weaken rigor based on:

- evaluation time for each output;
- whether outputs can be co-evaluated without sharing unverified state;
- enclosure width from alternative algebraic associations;
- subdivision reduction from r and λ corrections;
- checker cost relative to runner cost;
- checkpoint overhead.

A faster expression is acceptable only if it is analytically identical and rigorously
validated.

## 11. Required validation artifacts

A future audited package shall include at least:

```text
DERIVATION_ATTESTATION.json
INDEPENDENT_REDERIVATION_REPORT.json
CONTROL_EXPECT.json
CONTROL_FIXTURES.*
CONTROL_TO_SOURCE_MAP.json
KERNEL_VALIDATION_REPORT.json
KERNEL_VALIDATION.log
STATIC_AUDIT.json
STATIC_AUDIT.log
SOURCE_MANIFEST.json
DIAGNOSTIC_DERIVATIVE_COMPARISON.json
```

Names and schemas are provisional. Canonical hashes shall bind every normative artifact.

## 12. Acceptance gate

The kernel and adapter remain `AUDITED_SOURCE_PENDING` unless all of the following hold:

1. analytic derivation approved;
2. independent rederivation approved;
3. all positive controls pass;
4. all mutation controls fail in the expected way;
5. direct fine-box enclosures are contained in the v9 mean-value enclosure;
6. source and import static audit passes;
7. runner/checker independence is demonstrated;
8. canonical evidence and split trees are deterministic;
9. diagnostic discrepancies are explained;
10. performance measurement is complete.

Passing this gate approves audited source only. It does not approve a production config,
tag, workflow run, or certified λ range.

## 13. Open validation decisions

- final independent authoring mechanism;
- exact leaf count and coverage matrix;
- calibration cases with analytic or semi-analytic values;
- required fine-partition depth for containment tests;
- policy for interval-library version pinning;
- co-evaluation versus separate-evaluation interface;
- acceptable diagnostic discrepancy criteria;
- post-import source identity mechanism;
- checkpoint crash-injection method;
- final child-order and stack-order attack corpus.

The canonical-center rule, split-score formula, axis ordering, and dps separation are
frozen inputs to validation rather than open validation choices.
