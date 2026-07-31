# Item 3 λ Sweep Design Contract v9 — Draft

**Status:** `SPEC_PENDING`  
**Issue:** #20  
**Base commit:** `269b71d5b08eb2c6e4c1a81fb1525581b8427786`  
**Scope:** design, evidence, validation, and performance specification only  
**Non-approval:** this draft does not approve a kernel, config, tag, workflow run, certificate, or mathematical conclusion.

## 1. Purpose and frozen predecessor evidence

The v8.1 production path reached the pinned production runner in GitHub Actions run
`30609564841`. All identity, source, pilot-artifact, configuration, Phase 3, and
production-source gates passed. The hosted job was cancelled after approximately six
hours while `runner.run()` was active. The only recovered mathematical artifact was the
already-written pilot-artifact rederivation report. Therefore run #4 is frozen as primary
evidence of a wall-clock limit, not as a mathematical failure and not as a contract
failure.

The motivating diagnostic measurements are not certificates:

| quantity | diagnostic value |
|---|---:|
| `evaluate_gr`, dps 50 | about 7.69 s per call |
| `evaluate_gr`, dps 25 | about 2.77 s per call |
| `evaluate_gr`, dps 20 | about 2.28 s per call |
| estimated raw evaluations | about 20,000 |
| raw enclosure radius / r-width | about 3,300 |
| sampled true `|G_rr|` | about 0.5 |
| observed λ-width coefficient | about 2,048 |

These values justify a new design cycle. They are not inputs to any proof.

## 2. Design objective

Replace raw interval evaluation of `G_r` on an `(r, λ)` box by a rigorous,
deterministic, two-variable mean-value enclosure. The design shall reduce dependency
inflation in both coordinates while preserving fail-closed behavior and independent
checker rederivation.

The initial v9 attribution experiment keeps

```text
runner dps  = 50
checker dps = 70
```

so that any performance change is attributable to the enclosure form and new derivative
kernel rather than to a simultaneous precision change.

## 3. Domain and notation

Let `I = [r_-, r_+]` be a closed canonical r-cell with `0 < r_- <= r_+`, and let
`Λ = [λ_-, λ_+]` be a closed canonical λ-box. Let

```text
r0 = (r_- + r_+) / 2,
λ0 = (λ_- + λ_+) / 2.
```

The centers are computed exactly in the contract's rational/dyadic encoding. No
floating-point midpoint may affect subdivision, evidence identity, or checker replay.

Let

```text
G(r, λ) = F(r, λ) / r.
```

All intervals in this contract are outward-rounded rigorous enclosures. For an interval
`X`, `sup(X)` denotes its rigorous upper endpoint and

```text
absmax(X) = max(|inf(X)|, |sup(X)|).
```

## 4. Required clean-room kernel interface

The new pinned clean-room kernel shall rigorously expose at least

```text
F(r, λ)
F_r(r, λ)
F_λ(r, λ)
F_rr(r, λ)
F_rλ(r, λ)
```

on point and interval inputs required by the adapter contract.

Finite differences, complex-step differentiation, automatic differentiation of an
unreviewed expression graph, and numerical regression are prohibited as proof
machinery. They may appear only in explicitly labelled diagnostic tests.

The source shall contain or bind to analytically derived integrands for every published
derivative. Differentiation under the integral sign, singular-endpoint treatment, branch
choices, and domain restrictions must be justified in the analytic appendix and then
independently rederived during validation.

## 5. Quotient identities

The adapter shall derive the following quantities from the pinned kernel outputs:

```text
G_r  = F_r/r - F/r^2

G_rr = F_rr/r - 2 F_r/r^2 + 2 F/r^3

G_rλ = F_rλ/r - F_λ/r^2
```

The checker shall recompute these expressions from fresh kernel calls. A runner-supplied
final `G_rr`, `G_rλ`, correction interval, or mean-value enclosure is evidence to be
checked, never an oracle.

## 6. Two-variable mean-value enclosure

Define `H = G_r`. For every `(r, λ) in I × Λ`, the target inclusion is

```text
H(r, λ) ∈ H(r0, λ0)
          + H_r(I, Λ) (I - r0)
          + H_λ(I, Λ) (Λ - λ0).
```

Using `H_r = G_rr` and `H_λ = G_rλ`, the normative enclosure is

```text
MV(I, Λ) =
    G_r(r0, λ0)
  + G_rr(I, Λ)  (I - r0)
  + G_rλ(I, Λ)  (Λ - λ0).
```

The enclosure is accepted as `NEG` if and only if all terms are finite and

```text
sup(MV(I, Λ)) < 0.
```

A strict-positive classification is outside the initial v9 r-tile purpose unless a later
contract amendment explicitly introduces it.

### 6.1 Required recorded terms

For every attempted cell, runner evidence shall record:

```text
G_r(r0, λ0)
G_rr(I, Λ)
G_rλ(I, Λ)
I - r0
Λ - λ0
G_rr(I, Λ) (I - r0)
G_rλ(I, Λ) (Λ - λ0)
MV(I, Λ)
```

The checker independently reconstructs every item.

### 6.2 Inclusion proof obligation

The analytic appendix shall prove the inclusion by an axis path or an equivalent
multivariate mean-value theorem, using derivative enclosures valid on the entire
rectangle `I × Λ`. Pointwise or sampled derivative bounds are insufficient.

## 7. Deterministic refinement

A nonfinite or non-NEG result does not by itself produce a mathematical failure. It
enters deterministic refinement subject to hard budgets.

### 7.1 Proposed finite-term split score

When both derivative enclosures are finite, define

```text
C_r = absmax(G_rr(I, Λ))  * radius(I)
C_λ = absmax(G_rλ(I, Λ)) * radius(Λ).
```

The draft proposes splitting the coordinate with the larger contribution. Exact equality
uses the fixed tie-break `λ before r`, because λ-width inflation cannot be removed by
continued r subdivision.

### 7.2 Proposed nonfinite fallback

If one contribution is nonfinite, split its coordinate. If both are nonfinite, compare
the exact normalized widths

```text
width(I) / minimum_r_width
width(Λ) / minimum_λ_width
```

and split the larger value, with the same `λ before r` tie-break. If the selected
coordinate is unsplittable, try the other coordinate. If neither is splittable, terminate
with a normative unsplittable-enclosure reason.

### 7.3 Canonical children

Every split is an exact midpoint split. Child ordering, stack insertion, box identifiers,
and record ordering must be specified so runner and checker reproduce identical bytes.
No adaptive heuristic may depend on elapsed time, thread scheduling, host load, or
noncanonical floating-point comparisons.

### 7.4 Budgets and terminal reasons

v9 shall separately count, at minimum:

```text
F evaluations
F_r evaluations
F_λ evaluations
F_rr evaluations
F_rλ evaluations
runner total kernel calls
checker total kernel calls
r-cell creations
λ-box creations
r-depth
λ-depth
wall-clock checkpoints
```

Budget exhaustion produces `INCOMPLETE` with a normative reason. It must never be
converted into `NEG`, `VERIFY_PASS`, or a certified λ-range declaration.

## 8. Logical dependencies

The v9 logical dependency set shall add:

### `L-SECOND-DERIV`

Covers the analytic formula for `F_rr`, the quotient identity for `G_rr`, validity
domains, differentiation-under-integral justification, and rigorous enclosure semantics.

### `L-MIXED-DERIV`

Covers the analytic formulas for `F_λ` and `F_rλ`, the quotient identity for `G_rλ`,
validity domains, and rigorous enclosure semantics.

### `L-MEAN-VALUE-ENCL`

Covers the two-variable mean-value inclusion, canonical centers, interval operations,
strict sign predicate, and fail-closed refinement transition.

Each dependency entry shall be a canonical object with a 64-lowercase-hex
`dependency_entry_sha256`, an exact lemma identifier, and an explicit statement that it
supports machine use. No dependency may self-authorize a run.

## 9. Runner/checker separation

Runner and checker shall use separate adapter instances and separate kernel-call
counters. The checker shall:

1. rederive canonical centers and offsets;
2. call the pinned kernel afresh;
3. reconstruct `G_r`, `G_rr`, and `G_rλ`;
4. reconstruct both correction terms and `MV`;
5. verify finiteness and the strict sign predicate;
6. rederive the accepted partition and deterministic refinement history;
7. reject any evidence whose canonical bytes, source pins, context, or record chain do
   not match.

Reuse of runner interval objects, memoized runner values, or runner final enclosures by
the checker is prohibited.

## 10. Checkpoint and cancellation contract

The runner shall maintain:

```text
SWEEP_PROGRESS.json
SWEEP_PROGRESS.jsonl
SWEEP_PARTIAL_EVIDENCE.json
```

`SWEEP_PROGRESS.json` and `SWEEP_PARTIAL_EVIDENCE.json` are replaced atomically by
writing a sibling temporary file, flushing it, optionally applying `fsync` under the
final platform policy, and calling `os.replace`. `SWEEP_PROGRESS.jsonl` is append-only;
complete-line durability rules must be specified before implementation.

A checkpoint is partial execution evidence only. It cannot contain a certified verdict,
cannot be treated as a complete record chain, and cannot authorize resume in initial
v9. The initial design deliberately omits resume semantics.

The artifact upload step remains `if: always()`. Run #4 establishes that a hosted-job
cancellation can still permit artifact upload of files already present in the output
directory.

## 11. Evidence and canonicalization

All normative JSON uses the existing canonical JSON discipline unless v9 explicitly
amends it. Duplicate keys, CRLF, trailing whitespace, noncanonical numbers, unknown
fields, path escape, and missing required source hashes fail closed.

The proposed schemas are defined in `evidence_schema_proposal.md`. The final contract
must bind schema identifiers, required fields, record ordering, and hash-chain rules
before source implementation begins.

## 12. Performance qualification

The qualification environment is a GitHub hosted runner pinned as tightly as the
workflow permits. The measurement plan is defined in
`github_runner_performance_plan.md`.

Production eligibility requires

```text
runner + fresh checker + final artifact generation < 3 hours
```

on the approved qualification case, with reported peak memory and a documented margin
against the six-hour hosted limit. A result near three hours is a gate failure if
variance data does not support adequate margin.

The qualification must separately report the r and λ mean-value radius contributions
and demonstrate λ-width scaling relevant to later broad sweeps, not only the current
single box of width `2^-20`.

## 13. Validation gate

No production source may be approved until the independent plan in
`cleanroom_independent_validation_plan.md` passes. The validation strength must be at
least comparable to the existing 224-leaf independent validation and must include
adversarial controls for derivative identity substitution, omitted λ terms, stale source
pins, nonfinite enclosures, checker reuse, and false strict-sign acceptance.

## 14. Nonclaims and exclusions

This draft does not:

- implement or approve a kernel;
- alter the existing pinned kernel;
- alter an approved config;
- create, move, or approve a production tag;
- run or rerun a workflow;
- declare `CERTIFIED_LAMBDA_RANGE`;
- certify that the proposed split policy is optimal;
- treat diagnostic timing or sampled derivatives as proofs.

## 15. Open decisions before v9 freeze

The following remain `SPEC_PENDING`:

1. exact fixed integration variables and analytically derived integrands for
   `F_λ`, `F_rr`, and `F_rλ`;
2. proof conditions for differentiation under the integral sign at every endpoint and
   branch boundary;
3. whether the finite-term split score uses interval `absmax`, a sharper certified
   Lipschitz bound, or another exact upper contribution;
4. final tie-break and child ordering after adversarial testing;
5. separate minimum widths and maximum depths for r and λ;
6. whether checkpoint atomic replacement requires directory `fsync` on the hosted
   platform;
7. checkpoint cadence and maximum permitted checkpoint overhead;
8. exact schema IDs and whether partial evidence is one canonical object or a chained
   JSONL stream;
9. required performance margin and repetition count for the three-hour gate;
10. the exact definition of “224-leaf-equivalent or stronger” for the new five-output
    kernel.

Resolution of these decisions requires a later explicit approval. Until then the status
remains `SPEC_PENDING`.
