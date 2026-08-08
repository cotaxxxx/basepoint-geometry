# Item 3 sweep v9 — independent validation corpus freeze candidate

**Status:** `NORMATIVE CANDIDATE / FIXTURES PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This candidate gives an exact meaning to “224-leaf-equivalent or stronger” for the new
five-output kernel and v9 control path.

The candidate requires at least **256 distinct expected control leaves** with category
floors. Repeated or trivially duplicated fixtures do not count toward the floor.

It authorizes no source approval or certificate until the actual fixtures and reports are
independently executed and source-pinned.

## 1. Leaf definition

One validation leaf is one unique tuple

```text
control_id
category
input_domain_or_source_mutation
source_or_derivation_identity
expected_terminal_class
expected_predicate_or_failure_reason.
```

Two leaves with identical tuple content except for a cosmetic ID are duplicates and count
once.

Every leaf must have an expected result fixed before execution.

## 2. Minimum total and category floors

The complete corpus contains at least

```text
256 distinct leaves.
```

The following floors are mandatory and additive:

| Category | Minimum leaves |
|---|---:|
| A. Analytic/source-formula mapping | 32 |
| B. Domain, branch, angle regularization | 32 |
| C. Five-output rigorous kernel behavior | 80 |
| D. Quotient and mean-value adapter | 32 |
| E. Deterministic split/refinement controls | 32 |
| F. Evidence, checkpoint, cancellation | 24 |
| G. Multi-run shard/aggregate controls | 16 |
| H. Independence and source identity | 8 |
| **Total floor** | **256** |

A leaf belongs to exactly one primary category for counting, even if it exercises several
properties.

## 3. Category A — analytic/source-formula mapping, minimum 32

Must include distinct controls for:

- every displayed gamma derivative;
- each of `Phi_F`, `Phi_F_r`, `Phi_F_lambda`, `Phi_F_rr`, `Phi_F_rlambda`;
- quotient identities;
- gamma-range factorization;
- denominator/domain identities;
- angle endpoint coefficients;
- mixed derivative commutation;
- source-to-formula mapping of every kernel function;
- mutations of at least eight individual algebraic signs/coefficients/terms.

At least 16 leaves are independent positive rederivations and at least 12 are negative
mutations.

## 4. Category B — domain/branch/angle controls, minimum 32

Must include:

- lower and upper rehearsal r-domain cases;
- lambda lower-domain cases;
- invalid `r<=0`, `r>=1`, `lambda<1` source/interface attacks;
- finite/non-finite parameter balls;
- all four `(analytic_theta,analytic_phi)` combinations;
- square-root branch-cut attacks;
- Gauss `2F1` cut guard cases below, touching, crossing, and separated from the real cut;
- `gamma=1` removable endpoint;
- interior gamma values;
- non-finite gamma propagation;
- mutations OR→AND and guard removal.

At least 12 leaves must be explicit rejection/mutation controls.

## 5. Category C — five-output kernel, minimum 80

Allocate at least 16 leaves to each output:

```text
F
F_r
F_lambda
F_rr
F_rlambda.
```

For each output the 16-leaf floor includes:

- at least four rigorous point cases across the rehearsal rectangle;
- at least four narrow interval-box cases;
- at least two cases near difficult integration subdomains identified by prior diagnostics;
- at least two independent containment/reference comparisons;
- at least two non-finite/fail-closed adversarial cases where applicable;
- at least two source-identity or expression-substitution attacks.

Finite-difference agreement may be reported separately but does not count as a rigorous
containment/reference leaf.

## 6. Category D — quotient and mean-value adapter, minimum 32

Must cover:

- direct and factored quotient paths for all three quotient quantities;
- both-finite intersection;
- direct-only finite;
- factored-only finite;
- both non-finite;
- disjoint-finite fatal mutation;
- all displayed quotient coefficient/sign mutations;
- exact canonical centers;
- both mean-value correction terms;
- strict `sup(MV)<0` boundary, including `sup(MV)=0` rejection;
- raw-direct-too-wide / mean-value-NEG case;
- lambda-correction materially nonzero case;
- score construction only from FINAL dual-association derivative boxes.

At least 12 leaves are negative/mutation controls.

## 7. Category E — deterministic refinement, minimum 32

Must cover every axis-selection branch:

```text
only-r splittable
only-lambda splittable
nonfinite-r
nonfinite-lambda
double-nonfinite tie to r
larger exact r score
larger exact lambda score
finite exact tie to r.
```

Also include:

- r `R0 then R1` processing;
- lambda `L1 then L0` processing;
- LIFO attack by FIFO substitution;
- exact midpoint reproduction;
- path-ID derivation;
- activation-index replay;
- stop floors by coordinate;
- unsplittable terminal reason;
- dps-70 cannot mutate dps-50 tree;
- identical frozen input produces identical final mathematical record bytes.

At least 12 leaves are mutations.

## 8. Category F — evidence/checkpoint/cancellation, minimum 24

Must include:

- canonical JSON positive controls;
- duplicate key, unknown field, CRLF, trailing-space attacks;
- atomic snapshot replacement;
- file fsync omission mutation;
- directory fsync omission mutation;
- complete JSONL hash chain;
- truncated non-line suffix recovery;
- malformed complete-line corruption rejection;
- checkpoint verdict injection rejection;
- 32 MiB checkpoint ceiling;
- checkpoint timing excluded from final proof hash;
- cancellation after several distinct checkpoint phases;
- checkpoint-overhead gate handling.

At least 10 leaves are negative/mutation controls.

## 9. Category G — multi-run/aggregate, minimum 16

Must include:

- one-shard plan;
- multi-shard exact union;
- adjacent endpoint byte identity;
- selected attempt replacement for one shard;
- aggregate chain recomputation;
- completion-order substitution attack;
- missing shard;
- duplicate shard;
- gap;
- overlap;
- wrong plan hash;
- little-endian index mutation;
- hash-text instead of raw32 mutation;
- stale chain tip;
- checker-failed shard selected;
- fail/incomplete rehearsal cannot silently shrink target.

## 10. Category H — independence/source identity, minimum 8

Must include:

- independent rederivation imports no candidate/prototype source;
- candidate imports no runner/checker/adapter;
- runner and checker instantiate separate adapters;
- no runner cache/object reuse by checker;
- source SHA checked before import;
- source SHA checked after import;
- dynamic import/path escape mutation;
- diagnostic result promoted to proof mutation.

## 11. Coverage matrix requirement

Before execution, publish one canonical `CONTROL_EXPECT` object containing every leaf and
its expected outcome. After execution, publish a machine-generated matrix with one row per
control ID and no missing or extra IDs.

The validator must verify:

```text
observed leaf count >= 256
all category floors satisfied
all control IDs unique
no duplicate leaf tuple counted twice
all expected outcomes matched
terminal failure count = 0 for positive controls
unexpected-pass count = 0 for negative controls.
```

## 12. Promotion rule

The corpus is stronger than the historical 224-leaf benchmark only when all 256-plus
leaves are independently authored/executed against the exact final source/config bytes.

A 256-row file made by duplicating cases is not equivalent and must be rejected by the
leaf-tuple uniqueness rule.
