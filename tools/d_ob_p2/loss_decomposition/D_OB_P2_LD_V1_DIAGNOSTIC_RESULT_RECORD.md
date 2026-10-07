# D-OB P2 LD v1 Diagnostic Result Record

**Status:** FINAL DRAFT FOR CHAT AUDIT / DIAGNOSTIC / NOT_EVIDENCE / D-P2 NOT_CERTIFIED
**Date:** 2026-10-07
**Artifact branch:** `candidate/dob-p2-closure-erratum`
**Artifact commit:** `29205372ea4cc0333c5c567a5a25f05a528b8d83`
**Artifact parent:** `6a508b8d62e92ee788a00ab7b40f2d7bc9b65285`
**Original-SHA list SHA-256:** `a27a24a95f93d20208df627b82c7c6f0ac818693c509658cf1f3d7be258959f5`
**Original manifest SHA-256:** `db3630c7118c39737e92be7c6a50abdd00548173873a84fef28598c89a795206`

## 1. Scope and governance

This record closes the descriptive audit of the frozen LD v1 diagnostic run. It records only the five predeclared/post-selected diagnostic targets and the decomposition quantities produced by the countersigned LD implementation.

Nothing in this record is certification evidence. No representation is adopted, no producer is changed, no threshold is tuned, and no population-level frequency is inferred from these five targets.

The five targets are:

- `P003_r022`: r = 11/500, t = 1/64, lambda = 251/400.
- `P003_r030`: r = 3/100, t = 1/64, lambda = 251/400.
- `N_12_15_0`: r = 249/256, t = 255/256, lambda = 2573/6400.
- `B_14_13_0`: r = 253/256, t = 251/256, lambda = 2573/6400.
- `B_9_14_10`: r = 243/256, t = 253/256, lambda = 2833/6400.

## 2. Artifact and audit status

The archived run passed the producer-identity gate for all five targets. The original uncompressed bytes of all five `cells.tsv` files were preserved outside the repository and were also recoverably archived in the repository as deterministic `gzip -9 -n` files. Before push, decompression reproduced the original SHA-256 for all five files: 5/5 PASS.

The chat-side network path could not retrieve the pushed repository bytes directly because `codeload.github.com` returned HTTP 403 in that environment. The artifact audit therefore used terminal output transcribed from the authorized `daybreak-works` machine. The audited HEAD was `29205372ea4cc0333c5c567a5a25f05a528b8d83`.

For each target, all regular-cell rows in `cells.tsv` were independently re-aggregated with the stored surface-cell area weights. The recomputed W1, W2, W3 and the three telescoping losses agreed with `summary.json`; the largest absolute discrepancy was below `2e-13`, consistent with floating-point summation order. The telescoping identities also closed to the same scale. No regular cell had negative `loss_dependency` or negative `loss_surface`.

**Artifact audit result: PASS.**

## 3. Frozen decomposition

The frozen descriptive decomposition is:

- W1: true line-segment range reference on the surface-cell midpoint.
- W2: producer point-interval width on the same s interval.
- W3: exact stored producer `kval` width for the full surface cell.
- average-to-range loss = W1.
- dependency loss = W2 - W1.
- surface-cell loss = W3 - W2.

Thus, up to floating-point summation order,

`W3 = average-to-range + dependency + surface-cell`.

## 4. Aggregate results

| Target | W1 | W2 | W3 | Average -> range | Dependency | Surface-cell | Share: avg | Share: dependency | Share: surface |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P003 r=.022 | 0.5548851992 | 7.9330062586 | 11.5898634532 | 0.5548851992 | 7.3781210594 | 3.6568571946 | 4.8% | 63.7% | 31.6% |
| P003 r=.030 | 0.7561615323 | 10.9590840844 | 14.7438323778 | 0.7561615323 | 10.2029225522 | 3.7847482933 | 5.1% | 69.2% | 25.7% |
| B (14,13,0) | 0.2064152083 | 2.9552844474 | 5.2576404333 | 0.2064152083 | 2.7488692391 | 2.3023559859 | 3.9% | 52.3% | 43.8% |
| B (9,14,10) | 0.1395574904 | 2.1084989387 | 4.9540081750 | 0.1395574904 | 1.9689414483 | 2.8455092364 | 2.8% | 39.7% | 57.4% |
| N (12,15,0) | 0.0602361206 | 0.7490650779 | 21.2683070511 | 0.0602361206 | 0.6888289573 | 20.5192419733 | 0.3% | 3.2% | 96.5% |

The percentages are descriptive shares of W3 for the same target; they are not population frequencies.

## 5. Descriptive findings

### 5.1 Average-to-range loss is small in all five targets

The loss caused by replacing the line-segment average by the true range over the same s interval is 0.3% to 5.1% of W3 in these five targets. In this sample, the average-to-range step itself is therefore a small part of the total producer width.

This statement is restricted to the five audited targets.

### 5.2 Two different loss patterns appear in the five targets

For both P003 points and both B points, dependency loss is a major component, contributing about 40% to 69% of W3. Their surface-cell loss is comparatively dispersed: the top 10% of regular cells carry about 27% to 36% of the total surface-cell loss.

For the P003 pair, dependency loss increases from about 7.38 at r=.022 to about 10.20 at r=.030, while surface-cell loss remains near 3.7 (about 3.66 to 3.78). This is numerically consistent with the earlier diagnostic two-component picture of a rho-sensitive component that does not disappear under surface refinement and a roughly stable cell component. This is a consistency observation only, not a fitted law or a population claim.

`N_12_15_0` has a different pattern. Surface-cell loss is about 96.5% of W3 and is highly localized:

- top 1% of regular cells: 48.0% of total surface-cell loss;
- top 5%: 91.8%;
- top 10%: 93.0%;
- cells with `mu in [0.9844, 1]`: 92.4%;
- cells with `D_lo < 0.03`: 91.6%.

There are 2,778 cells with `D_lo < 0.03`, about 4.5% of the 61,373 regular cells, yet they carry about 91.6% of the surface-cell loss. The same concentration lies in the near-pole `mu >= 63/64` region.

Thus the N target does not exhibit the same decomposition as the P003 targets. The earlier diagnostic statement that correlation/dependency loss is important is not contradicted globally by this N point; rather, this point is an example where a localized near-pole/small-D surface-cell effect dominates the frozen W3 decomposition.

### 5.3 LD-R4b representation comparison -- record only

The normalized-representation widths were recorded on the same partition. No representation is preferred or adopted here.

| Target | W3 | Normalized raw | Raw / W3 | q,v-clipped | Clipped / W3 |
|---|---:|---:|---:|---:|---:|
| P003 r=.022 | 11.5898634532 | 8.9505595081 | 0.772 | 8.7958224375 | 0.759 |
| P003 r=.030 | 14.7438323778 | 11.3453811800 | 0.770 | 11.0563074264 | 0.750 |
| B (14,13,0) | 5.2576404333 | 4.5020138606 | 0.856 | 3.9961142988 | 0.760 |
| B (9,14,10) | 4.9540081750 | 4.3570198340 | 0.879 | 3.6938084971 | 0.746 |
| N (12,15,0) | 21.2683070511 | 23.5218953878 | 1.106 | 5.4094983439 | 0.254 |

The q,v-clipped normalized width is smaller than W3 for all five targets. The reduction relative to W3 is about 24-25% for the P003 and B targets and about 74.6% for the N target. For N, the unclipped normalized width is instead about 10.6% larger than W3.

Within this diagnostic, that pattern indicates that imposing the exact geometric bounds `q,v in [-1,1]` materially changes the interval width near the N pole case. It does not establish that the normalized representation should replace the current producer representation.

## 6. Limits of interpretation

Two limits are mandatory.

1. **Post-selected sample.** These five targets were chosen after earlier diagnostic results were available. Their proportions, patterns, or relative frequency cannot be extrapolated to the full D-P2 population.

2. **Surface-cell loss is not further decomposed.** `W3 - W2` contains both genuine variation of the kernel over the surface cell and overestimation introduced by interval evaluation on that cell. LD v1 does not separate these two effects. Therefore a large surface-cell loss does not by itself identify which of those two submechanisms dominates.

A third governance limit also remains in force: LD-R4b is descriptive only. Any producer redesign, including adding explicit q,v constraints or adopting another representation, requires a separate predeclare and countersign before execution.

## 7. Closure statement

LD v1 has completed its intended descriptive task. The artifact identity gates passed 5/5, all reference cells resolved, the archived bytes are recoverable against the frozen original SHA list, and the full-row recomputation audit passed for all five targets.

**LD v1 status: COMPLETE / ARTIFACT AUDIT PASS / DIAGNOSTIC / NOT_EVIDENCE.**
**D-P2 status: NOT_CERTIFIED.**
