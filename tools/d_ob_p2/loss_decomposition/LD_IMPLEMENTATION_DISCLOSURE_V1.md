# LD implementation package v1 — pre-ignition disclosure

Status: **DIAGNOSTIC / NOT_EVIDENCE / EXECUTION NOT AUTHORIZED**

This package implements the audited LD predeclare. It is not an ignition authorization.

## Pins and exact targets

Canonical producer SHA-256:
`dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b`.

Saved inputs:
- `results_192.tsv`: `6ad29461e42c265ce136e8df114400072e939335d72e2033b79741461e93fa90`
- `P003_lambda251.tsv`: `85d6146ac1b92d50fac85a6560b2679f7aa74fa89afd904f5d3838309ccca360`

The executable refuses a producer/input pin mismatch.

For C1, `(i_r,i_t,i_lambda)` is exactly the index convention of `results_192.tsv` and the frozen comparison-driver center map.

| target | index | r | t | lambda |
|---|---|---|---|---|
| P003 .022 | — | 11/500 | 1/64 | 251/400 |
| P003 .030 | — | 3/100 | 1/64 | 251/400 |
| cut-free N | (12,15,0) | 249/256 | 255/256 | 2573/6400 |
| true-cap B | (14,13,0) | 253/256 | 251/256 | 2573/6400 |
| excess-cut B | (9,14,10) | 243/256 | 253/256 | 2833/6400 |

Every target is reconstructed as `PBox(r,r,t,t,lambda,lambda,12)`, matching C1/C4 comparison execution.

## Identity gate and U semantics

After `refine_cells(B)`, the identity values are exactly those of the frozen comparison driver:

`L_id = str(float(lower(L)))`

`U_id = str(sum(float(upper(area_c * K_c)) for regular cells) + float(upper(B_cut)))`

Thus U is the saved `upper_sum = sum regular upper + B_cut`. It is not a cut-free regular upper endpoint.

`L_id` and `U_id` are compared byte-for-byte to the strings frozen in `ld_config_v1.py`. There is no numerical tolerance or alternate serialization. Failure gives `INVALID_IDENTITY` and stops that target before decomposition.

Partition serialization is deterministic: leaves are sorted lexicographically by exact rational `(m0,m1,p0,p1,depth)`; each rational uses Python Fraction canonical `str()`; fields are tab-separated and rows LF-terminated. SHA-256 of these bytes is the partition identity.

## Frozen regular-cell telescoping order

For every regular cell c:
- x_c is its exact (mu,phi) midpoint.
- I_s is exactly the producer segment [-rho,+rho].

Define:
- `W0(c)=0`: the high-precision non-interval s-line average at x_c is a scalar.
- `W1(c)=max_{s in I_s} F_rhorho(s;x_c) - min_{s in I_s} F_rhorho(s;x_c)`: high-precision non-interval true-range reference.
- `W2(c)`: width returned by the pinned producer `kernel_point(rs,z,mu,a,cp,sp,lam,True)` with the same I_s and mu, phi, lambda and z degenerate at exact target/cell midpoint values. No LD-side T1/T2/T3 recombination is used for W2.
- `W3(c)`: width of the exact `kval` stored in `data["regular"]` by the pinned producer for that complete frozen surface cell. No LD-side T1/T2/T3 recombination is used for W3.

At every regular cell, LD also calls the pinned producer `kernel_point` again on the complete cell arguments and requires its lower and upper endpoint strings to equal the stored `kval` endpoint strings exactly. Any mismatch is fail-closed as `KVAL_ENDPOINT_MISMATCH` before that cell is used. T1/T2/T3 remain record-only primitive intervals and their separately distributed sum is never used as W2 or W3.

Attribution is fixed as:
- `Delta_avg_to_range = W1 - W0 = W1`
- `Delta_dependency = W2 - W1`
- `Delta_surface = W3 - W2`

Therefore, by definition:
`W3 = W0 + Delta_avg_to_range + Delta_dependency + Delta_surface`.

The order is frozen before ignition and is not changed after results. A negative dependency difference is not clipped; if caused by reference instability it is reported together with the stability failure.

Area-weighted aggregate regular widths are `sum(area_c * Wj(c))`. They are descriptive diagnostics, not certified integral errors.

## Cut component

The baseline cut contribution is the producer's `B_cut`.

For each point box in the near column, the true-cap test uses the exact center c=(0,0,z), producer radius R, and

`distance_squared(mu) = 1 + z^2 - 2*lambda*z*mu - (1-lambda^2)*mu^2`.

A positive-area true cap exists iff the exact minimum on mu in [-1,1] is strictly below `4*R^2`.

When a cap exists, its boundary is obtained from

`1 + z^2 - 2*lambda*z*mu - (1-lambda^2)*mu^2 = 4*R^2`.

The north-cap parameter height is `d_star = 1-mu_star`. The geometric frozen-bound floor is

`B_cut_floor = (4*pi*C2/lambda) * sqrt(d_star)`, with `C2 = 9*pi+8`.

Report:
- baseline `B_cut`
- `B_cut_floor`
- `B_cut_resolution_excess = B_cut - B_cut_floor`

If no positive-area cap exists, `B_cut_floor=0`. This is descriptive only.

## LD-R4b normalized representation

On the same full regular cell, same I_s, same partition, and same 160-bit Arb precision, compare the current decomposition with exactly:

`F_rhorho = (w/D) * [ 4*v*R*(gamma*q-v) - 2*gamma*R_gamma*(gamma*q-v)^2 - 2*gamma*R*(3*gamma*q^2-gamma-2*v*q) ]`

where

`q=(b-s)/D`

`v=lambda*b/w`.

Two normalized widths are frozen:
- `normalized_raw_width`: q and v are not clipped.
- `normalized_clipped_width`: q and v are intersected with [-1,1].

Clipping is always sound for the exact geometry because `|q|<=1` and `|v|<=1`. Both variants are reported. Neither is preferred or adopted. Only enclosure widths and their area-weighted aggregates are compared.

## Primitive intervals and cancellation

For every regular cell, `cells.tsv` records lower/upper endpoints for:
`D, h, gamma, R, R_gamma, gamma_rho, gamma_rhorho, T1, T2, T3`.

At s=0 and the exact surface-cell midpoint, the non-interval local ratio is:

`C_local = (|T1|+|T2|+|T3|) / |T1+T2+T3|`.

A zero denominator is emitted as `ZERO_DENOMINATOR`; no epsilon is inserted.

The conceptual integrated ratio is:

`C_int = integral_{partial K} |K_H| dA / |J|`.

The implementation reports a **non-interval composite-midpoint approximation** on the complete frozen stopping partition, including regular and cut leaves. Every leaf uses its exact (mu,phi) midpoint, its high-precision s-line average, and its leaf area. Numerator and denominator use the identical leaf set. The field is explicitly `C_int_composite_midpoint_reference`; it is not a certified integral and not an enclosure-width ratio.

## Frozen non-interval reference protocol

- primary precision: 80 decimal digits
- tightening precision: 100 decimal digits
- line quadrature: mpmath tanh-sinh, `maxdegree=12`
- true-range seed grid: 4097 equally spaced s values including both endpoints
- each grid-local candidate extremum: 120 deterministic golden-section iterations on its adjacent grid bracket
- surface reference point: exact cell midpoint
- stability threshold: primary/tightened scalar line-average/extremum values differ by at most `1e-50` absolute
- reference workers: exactly 10 processes

Failure is `UNRESOLVED_REFERENCE`; it is never promoted to an interval bound. These settings cannot be changed after ignition.

### Runtime estimate and fixed mitigation

The pre-ignition audit measured one high-precision kernel evaluation at roughly 200 microseconds at 80 digits and 220 microseconds at 100 digits. With 4097 range-grid samples, golden-section refinement, and two precision passes, the audit estimates roughly 2 seconds per regular cell. With about 37,000--59,000 regular cells per target, a single process was estimated at about 150 hours for all five targets.

The frozen mitigation is option (a): **cell-reference parallelization with exactly 10 worker processes**. The 4097-point grid, 120 golden iterations, 80/100-digit precisions, quadrature degree, and stability threshold are unchanged. On ideal scaling this reduces the reference-dominated estimate to about 15 hours; actual wall time may be longer because process overhead, producer reconstruction, interval diagnostics, I/O, and cut-leaf reference work are not included in the ideal estimate.

Parallelism changes scheduling only. Each cell reference is a pure function of its frozen exact target/cell coordinates and the frozen numerical protocol, and results are returned in input order by `Pool.map`. No threshold, precision, grid, or attribution rule depends on worker timing.

## Output paths and schema

A new user-supplied output directory is mandatory and must be outside the canonical producer repository and outside `tools/d_ob_p2/comparison_runs`. Containment is tested with resolved `Path` equality / `Path.is_relative_to`, not string-prefix matching. An existing nonempty output directory is rejected.

Per target:
- `identity.json`
- `partition.tsv`
- `cells.tsv`
- `summary.json`

Run level:
- `manifest.json`

The manifest records input/code/config pins and artifact SHA-256 values. No production or canonical input path is an output path.

## Mechanical ignition guard

The executable requires the exact token `LD-V1-COUNTERSIGNED`. This is only a mechanical guard. Governance still requires explicit chat countersign first, followed by direct execution by the user.

Current status: **LD EXECUTION NOT AUTHORIZED**.
