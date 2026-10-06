# D-OB P2 Loss-Decomposition Diagnostic — Predeclare v1

Date: 2026-10-06 (JST)

Status: **DRAFT / DIAGNOSTIC / NOT_EVIDENCE / EXECUTION NOT AUTHORIZED**

This document predeclares a read-only diagnostic investigation of the frozen D-P2 near-column failure. It does not alter D-P2 certification status, production producer/checker semantics, the frozen comparison harness, or D-AN-1. Execution requires a separate chat audit and explicit pre-ignition countersign.

## LD-R1 — Identity, repository, and status

The diagnostic belongs in `basepoint-geometry`, the home of the diagnostic/comparison tooling, preserving the existing separation from the D-P2 production repository.

All outputs are **DIAGNOSTIC / NOT_EVIDENCE**. D-P2 remains **NOT_CERTIFIED**. No production harness, canonical producer/checker, canonical result file, frozen comparison result, or D-AN-1 proof artifact may be modified by this diagnostic.

The canonical producer used for reconstruction must be pinned by exact SHA-256 before ignition. The wrapper may call that pinned producer only to reconstruct and record the baseline stopping partition; it must not modify the producer.

## LD-R2 — Five fixed, post-selected targets

Exactly these five targets are in scope:

1. P003, `t=1/64`, `lambda=251/400`, `r=.022`.
2. P003, `t=1/64`, `lambda=251/400`, `r=.030`.
3. cut-free N target `(12,15,0)` from the 192-point representative set.
4. B target `(14,13,0)`, with a genuine geometric cap under the read-only investigation.
5. B target `(9,14,10)`, identified as an excess-cut case: the baseline has cut while the read-only geometric-cap test does not require a true cap.

These targets were selected **after observing existing results**. They are not blind, random, representative-by-construction, or prospectively selected. No inference to the frequency of a mechanism over N80, B44, or all 7,662 unresolved boxes is permitted from this five-point diagnostic.

## LD-R3 — Frozen partition reconstruction and identity gate

The final baseline cell partitions were not saved. A read-only diagnostic wrapper shall therefore run the exact pinned canonical producer sufficiently to reconstruct and record the baseline stopping partition for each target.

Before any loss-decomposition result is valid, the reconstruction must pass an identity gate:

- target identity and baseline resource/configuration identity must match the frozen C0 source for that target;
- the reconstructed stopping result must reproduce the stored C0 `L` and `U` **byte-for-byte in their serialized result representation**;
- where the stored row contains `B_cut`, cell count, or stop/failure reason, these shall also be recorded as identity metadata, but the mandatory validity gate is the byte-identical stored `L` and `U`;
- the reconstructed partition shall be assigned a deterministic partition identity (serialized partition SHA-256) and all downstream measurements for that target must cite it.

If either `L` or `U` fails byte identity, or if target/config identity cannot be established, that target is **INVALID** and no decomposition result from it may be interpreted. There is no tolerance-based fallback.

The wrapper and partition recorder are diagnostic-side additions only. Production files remain unchanged.

## LD-R4 — Four loss components and recorded quantities

On each identity-valid fixed partition, the diagnostic shall separate and report four conceptually distinct losses:

1. **Surface finite-width loss** — loss attributable to finite `mu,phi` surface-cell width, holding the s-treatment and algebraic representation fixed.
2. **Average-to-range loss** — loss introduced by replacing the true s-line average by a range over the same s-segment, separated from natural-interval dependency.
3. **Natural-interval dependency loss** — additional loss caused by evaluating correlated quantities through the natural interval expression on the same s-range.
4. **Cut loss** — separated into:
   - finite-resolution excess cut area/classification; and
   - the geometric cut floor that remains for a genuine cap under the frozen exclusion geometry.

The implementation must state exact operational formulas for each reported loss before ignition. Components must not be defined post hoc by subtracting whatever quantities happen to make the observed totals agree.

For every analyzed surface cell, record point/reference values and interval endpoints, as applicable, for:

`D, h, gamma, R, R_gamma, gamma_rho, gamma_rhorho, T1, T2, T3`.

Two different cancellation diagnostics shall be recorded and kept distinct:

- local algebraic cancellation ratio
  [
  C_{local}=(|T1|+|T2|+|T3|)/|T1+T2+T3|,
  ]
  with zero or near-zero denominators explicitly flagged rather than silently regularized;
- integrated kernel sign-cancellation ratio
  [
  C_{int}=int |K_H|,dA/|J|,
  ]
  with its normalization and integration domain recorded.

Neither ratio is an enclosure-width ratio.

### LD-R4b — Same-range algebraic representation comparison

As an additional descriptive comparison, evaluate `F_rhorho` on the **same identity-valid partition, same s-interval, and same arithmetic precision** using both:

1. the current producer decomposition; and
2. the normalized representation identified in the read-only investigation,
   [
   F_{hoho}=rac{w}{D}left[
   4vR(gamma q-v)
   -2gamma R_gamma(gamma q-v)^2
   -2gamma R(3gamma q^2-gamma-2vq)
   ight],
   ]
   where `q=(b-s)/D` and `v=lambda*b/w`, retaining the geometric constraints `|q|<=1`, `|v|<=1` only when they are justified by the evaluated enclosure.

Record only the resulting enclosure widths and their difference/ratio under the predeclared reporting convention. Do **not** declare either representation superior, recommend adoption, modify the producer, or convert this comparison into a candidate-design decision. Any such design decision requires a later, separate predeclare.

## LD-R5 — Non-interval reference values and fixed precision

Line averages, point/reference kernel values, and approximations to true ranges used to diagnose the decomposition are **non-interval reference values**. They are not certified enclosures and must never be labeled as such.

Before ignition, the implementation appendix/config shall freeze:

- arithmetic precision in bits or decimal digits;
- quadrature rule/family;
- quadrature order or stopping rule;
- s-sampling/range-reference procedure;
- surface reference procedure where applicable;
- repeat/tightening check used to estimate numerical stability.

No precision, order, tolerance, or sampling density may be changed after seeing a target's diagnostic result. If the frozen reference procedure fails its own predeclared stability check, report that reference quantity as **UNRESOLVED**, not as an interval bound.

## LD-R6 — Interpretation firewall

Outputs are descriptive loss decompositions only.

They shall not be used in this diagnostic to:

- tune a threshold or resource limit;
- choose or adopt a new producer representation;
- claim a theorem, certified sign, or certification closure;
- modify D-P2 status;
- serve as evidence for D-AN-1, FT_q, QM, L3, or L1;
- estimate population frequencies from the five post-selected targets;
- reopen the CLOSED candidate-comparison chapter.

Their only permitted downstream role is as **DIAGNOSTIC / NOT_EVIDENCE** material that may motivate a future candidate-design predeclare or other separately governed investigation.

Prior diagnostic observations — including the Code scratchpad values “roughly 15x”, “true variation 0.3–1.0”, and “P003 average-to-range loss about 0.4” — may be recorded as provenance/context only. They are explicitly **not** expected values, acceptance criteria, thresholds, or pass/fail conditions for this diagnostic.

## LD-R7 — Procedure and ignition gate

The required order is:

1. commit this predeclare;
2. chat performs a full-text audit;
3. prepare the diagnostic implementation/config and expose all LD-R3 operational serialization rules, LD-R4 formulas, LD-R4b reporting convention, and LD-R5 numerical settings for pre-ignition review;
4. obtain explicit chat pre-ignition countersign;
5. **user directly executes** the diagnostic;
6. preserve the resulting artifacts byte-for-byte, record SHA-256 pins, and push them without reinterpretive editing.

No diagnostic execution is authorized by the commit or audit of this predeclare alone.

Any identity-gate failure is recorded fail-closed. Any need to change a frozen target, decomposition definition, reference precision/procedure, identity rule, or reporting convention after ignition requires STOP and a new predeclare/version before rerun.

## Pre-ignition artifact requirements

Before countersign, the diagnostic package must expose at minimum:

- exact canonical producer SHA-256;
- exact input/result source pins for all five targets;
- wrapper/config SHA-256;
- deterministic partition serialization specification;
- exact meaning of reconstructed `L`, `U`, and their byte-identity comparison;
- operational formulas for all four LD-R4 components;
- LD-R4b interval-evaluation and width-reporting convention;
- all LD-R5 precision/quadrature/sampling/stability settings;
- output schema and filenames;
- explicit proof that no production/canonical path is an output path.

Until these are audited and countersigned, status remains **LD EXECUTION NOT AUTHORIZED**.
