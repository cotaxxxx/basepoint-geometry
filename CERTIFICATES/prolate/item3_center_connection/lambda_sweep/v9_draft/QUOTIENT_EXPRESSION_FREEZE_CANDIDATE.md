# Item 3 sweep v9 — quotient expression freeze candidate

**Status:** `NORMATIVE CANDIDATE / VALIDATION PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This candidate resolves the open interval-association question for

```text
G_r,
G_rr,
G_rlambda.
```

It uses two algebraically identical enclosure paths and combines them fail-closed. No
additional kernel calls are required because both paths reuse the same five F-level
interval outputs.

It authorizes no source approval, workflow, tag, or certificate until incorporated in the
one-shot v9 freeze and independently validated.

## 1. Exact identities

For `r>0`,

```text
G_r
 = F_r/r - F/r^2
 = (F_r r - F)/r^2,
```

```text
G_rr
 = F_rr/r - 2F_r/r^2 + 2F/r^3
 = (F_rr r^2 - 2F_r r + 2F)/r^3,
```

```text
G_rlambda
 = F_rlambda/r - F_lambda/r^2
 = (F_rlambda r - F_lambda)/r^2.
```

The analytic proof establishes these equalities for the exact real quantities.

## 2. Frozen intermediate powers

For a positive rigorous r interval `R`, compute once, in this order,

```text
R2 = R * R
R3 = R2 * R.
```

Do not independently evaluate `R**2` or `R**3` in one association and cached products in
the other. Runner and checker use the same frozen operation graph.

## 3. Direct association

Using already computed rigorous F-level enclosures, define exactly:

```text
GR_DIRECT
 = (F_r / R) - (F / R2)
```

```text
GRR_DIRECT
 = ((F_rr / R) - ((2 * F_r) / R2))
   + ((2 * F) / R3)
```

```text
GRL_DIRECT
 = (F_rlambda / R) - (F_lambda / R2).
```

The parentheses above are normative evaluation order.

## 4. Common-denominator association

Define exactly:

```text
GR_FACTORED
 = ((F_r * R) - F) / R2
```

```text
GRR_FACTORED
 = ((((F_rr * R2) - ((2 * F_r) * R)) + (2 * F)) / R3)
```

```text
GRL_FACTORED
 = ((F_rlambda * R) - F_lambda) / R2.
```

Again, the displayed parentheses are normative.

## 5. Dual-association combination rule

For each quotient quantity independently, let `D` be the direct enclosure and `Q` the
common-denominator enclosure.

### 5.1 both finite

If both are finite, they must overlap because both rigorously contain the same exact real
quantity. Require

```text
D.overlaps(Q) == true.
```

Then define

```text
FINAL = D.intersection(Q).
```

The exact value lies in both `D` and `Q`, hence in their set intersection, and therefore in
the outward-rounded `arb.intersection` result.

If both are finite but do not overlap, this is not an ordinary refinement failure. It is
an implementation/source inconsistency and produces

```text
RUN_FATAL / QUOTIENT_ASSOCIATION_DISJOINT.
```

### 5.2 exactly one finite

If exactly one association is finite, use that finite enclosure as `FINAL` and record

```text
association_class = DIRECT_ONLY
```

or

```text
association_class = FACTORED_ONLY.
```

This remains rigorous because either algebraic association separately encloses the exact
quantity. A non-finite alternative cannot invalidate a finite rigorous enclosure.

### 5.3 neither finite

If neither association is finite, return a non-finite quotient enclosure and enter the
ordinary deterministic refinement path.

No strict sign verdict may be extracted from a non-finite final enclosure.

## 6. Frozen expression IDs

The proposed normative IDs are

```text
ITEM3_V9_GR_DUAL_ASSOC_V1
ITEM3_V9_GRR_DUAL_ASSOC_V1
ITEM3_V9_GRLAMBDA_DUAL_ASSOC_V1.
```

Each evidence record stores:

```text
expression_id
direct_enclosure
factored_enclosure
direct_finite
factored_finite
overlap                 # both-finite case
association_class       # INTERSECTION | DIRECT_ONLY | FACTORED_ONLY | NONFINITE
final_enclosure.
```

Runner values are evidence only. Checker recomputes every field from fresh F-level calls.

## 7. Why no performance-based expression selection is required

The earlier draft asked qualification to compare algebraically equivalent associations
and choose one. The dual-association rule removes the need for a host-dependent or sampled
winner:

- both paths are analytically exact;
- both use the same already available kernel outputs;
- when both are finite, their intersection is at least as informative set-theoretically as
  retaining either uncombined enclosure;
- when only one is finite, retaining the finite one avoids an unnecessary failure;
- no timing, sampled truth, or approximate width comparison selects the proof expression.

Performance qualification should still report the algebraic adapter cost, but that cost is
expected to be negligible compared with the rigorous integrals and is not used to choose
between the two paths.

## 8. Mean-value use

The v9 mean-value enclosure uses only the **FINAL** quotient enclosures:

```text
G_r_center = FINAL(G_r at canonical center)
G_rr_box = FINAL(G_rr on I x Lambda)
G_rlambda_box = FINAL(G_rlambda on I x Lambda).
```

Then

```text
MV
 = G_r_center
   + G_rr_box (I-r0)
   + G_rlambda_box (Lambda-lambda0).
```

Split scores also use the final dual-association derivative boxes.

## 9. Required controls

Positive validation must cover for each of the three quotient quantities:

- both finite and overlapping;
- direct strictly sharper;
- factored strictly sharper;
- partial overlap;
- exactly direct finite;
- exactly factored finite;
- both non-finite.

Mutation controls must reject:

- wrong coefficient `2` in `G_rr`;
- omitted `2F/r^3` term;
- use of `F_rlambda` in place of `F_lambda`;
- altered operation order under the same expression ID;
- accepting disjoint finite associations;
- trusting runner overlap flags;
- selecting one finite association by approximate radius when both are finite;
- using a non-finite association when the other is finite;
- constructing split scores from a pre-combination rather than FINAL derivative box.

## 10. Status effect

If incorporated and validated, this candidate closes the open

```text
final interval expression order
```

item in the analytic/v9 design documents.

Until then the expression policy is a freeze candidate and v9 remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```
