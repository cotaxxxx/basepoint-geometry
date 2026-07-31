# Item 3 Sweep v9 Prototype — Independent Static, Mathematical, and Performance Audit

**Status:** `PROTOTYPE / INDEPENDENT AUDIT PASS / NOT APPROVED`  
**Issue:** #23  
**Audit date:** 2026-08-01

## Scope and reported-scope correction

The prior report described the publication as eight commits changing only seven files
under `lambda_sweep/v9_prototype/`. The independently measured publication scope is:

```text
11 commits
7 files under lambda_sweep/v9_prototype/
3 files under lambda_sweep/v9_draft/
10 changed files in total
```

The three changed draft files are:

```text
v9_draft/design_contract_v9_draft.md
v9_draft/evidence_schema_proposal.md
v9_draft/cleanroom_independent_validation_plan.md
```

The additional draft changes are substantively acceptable. They make the canonical-center
rule normative:

- `r0` is the canonical dyadic midpoint derived from the parent endpoints;
- `λ0` is the canonical reduced-rational midpoint derived from the parent endpoints;
- runner and checker independently rederive both centers;
- evidence-supplied center bytes must match the independently rederived bytes;
- floating-point, printed-decimal, approximate, or arbitrary interior midpoints are
  prohibited.

The report must nevertheless be corrected from eight commits / seven files to eleven
commits / ten files.

The following frozen assets were checked and remained unchanged:

- the v8.1 design blob;
- the approved production config;
- the existing production kernel.

This audit does not approve a production kernel, config, tag, workflow, certificate, or
mathematical conclusion.

## Source hashes prepared before publication

```text
prolate_F_derivatives_cleanroom_v9.py  9a237ef8f3d7f46d661ef68d1edff9f47ee22c3f25ac8b9630e5b3d64b321966
mean_value_core_v9.py                  6270059c2dfad1586a4ce86f1b3b0ceac31ef1c15278dbcdeae17923190a5188
symbolic_audit_v9_derivatives.py       1ccf104057818d32ef70cea8bb28cca9b018c942dae3f49622356c79e1028238
test_v9_derivative_kernel.py           c64926a0b0248dcd427308dc7286c38ce4187cf396963648eed68b904c2055c8
test_mean_value_core_v9.py             96ffaff10d6474322aa9976ccedbfea7e75865a265d275b6027993b02fa8757e
```

## Post-publication byte identity

The Git blob SHA-1 values fetched from the implementation branch match locally computed
Git blob identities for every Python candidate:

```text
prolate_F_derivatives_cleanroom_v9.py  57a7725c6ff0c4135723536b313e63d609eac4f6
mean_value_core_v9.py                  aef91706635713ece16cfb15392e3583c6b5b411
symbolic_audit_v9_derivatives.py       5cd9294b3402e95d72ae44b21af1968c9866710d
test_v9_derivative_kernel.py           e2ac57371486856a974d4fe8a941009b03753be6
test_mean_value_core_v9.py             6c1722bf3400b03ac42ba77dba7b828686e09346
```

The published candidate bytes are identical to the independently syntax-checked and
diagnostically tested bytes.

## Independent checks

### Syntax and exact core

The following checks passed:

- declared blob identity;
- `python3 -m py_compile`;
- mean-value core tests: 7/7;
- symbolic audit checks: 7/7.

The exact mean-value core tests cover:

- exact midpoint construction;
- strict-negative mean-value acceptance;
- exact score tie behavior;
- nonfinite-score handling;
- double-nonfinite handling;
- exclusion of unsplittable axes;
- exact midpoint children.

### Independent symbolic check at the endpoint

For

```text
h(c) = arccos(c)^2
```

the endpoint derivative was independently checked by series expansion:

```text
h'''(1) = -8/15.
```

This agrees with the symbolic prototype.

### Float derivative diagnostics

Using the fixed midpoint grid in the prototype, central finite differences were compared
with the implemented analytic formulas at three representative points. Two diagnostic
test groups passed. These finite-difference checks are diagnostic only and are not proof
machinery.

## First rigorous python-flint execution

The independent audit environment contained `python-flint`, allowing the previously
unexecuted rigorous point integrations to be run. All five outputs returned finite values.
These measurements remain diagnostic and outside the proof path.

At dps 50, the measured point-evaluation costs were:

| output | time |
|---|---:|
| `F` | 2.33 s |
| `F_r` | 1.51 s |
| `F_λ` | 1.44 s |
| `F_rr` | 3.42 s |
| `F_rλ` | 3.32 s |

A seven-call mean-value cell therefore costs approximately 12.6 seconds in the measured
environment.

## Measured r-width behavior

At the left endpoint, identified as the difficult point, the measured r-cell behavior was:

```text
r width 2^-12: not certified
r width 2^-13: NEG certified, MV upper endpoint approximately -0.00439
r width 2^-14: NEG certified with additional margin
```

The previously suggested approximately two-cell estimate is withdrawn. Although the true
`|G_rr|` is about 0.5 at the sampled point, the interval enclosure of `G_rr` suffers strong
dependency inflation; at width `2^-12` it expands to approximately `±101`. The second-
derivative enclosure therefore also requires subdivision.

## Measured λ-width behavior and coupling mechanism

With r width fixed at `2^-13` in the leftmost cell, the λ-width measurements were:

| λ width | MV upper endpoint | result |
|---:|---:|---|
| `2^-20` | `-0.00439` | NEG |
| `2^-16` | `-0.00415` | NEG |
| `2^-13` | `-0.00240` | NEG |
| `2^-10` | `+0.012` | not certified |

The λ first-order correction is not the controlling contribution. Even at λ width
`2^-13`, its radius is only approximately `1.7e-5`.

The controlling mechanism is indirect: widening the λ box enlarges the interval enclosure
`G_rr(I,Λ)`, which enlarges the r correction. The measured r-correction radii increase as

```text
0.00308 -> 0.00332 -> 0.00505.
```

Thus the r-width and λ-width certification limits are coupled, even though the config
must retain separate r and λ controls for deterministic refinement and auditing.

## Performance conclusion

The measured planning values are:

```text
measured certification boundary: r width 2^-13, λ width 2^-13
recommended r stop floor:       2^-16
recommended λ stop floor:       2^-16
expected operating widths:      2^-11 through 2^-13
uniform 2^-13 estimate:         approximately 224 cells
adaptive estimate:              approximately 150 cells
runner estimate:                approximately 31 to 47 minutes
runner + fresh checker:         approximately 1.5 to 2.3 hours
hard complete-path gate:        3 hours
```

`2^-13` is a measured certification boundary, not the stop floor. Placing the floor at the
measured boundary would leave no reserve for a slightly worse unsampled cell. Under
adaptive subdivision, lowering the floor to `2^-16` affects only the small number of cells
that reach the difficult left-end region; the expected increase is tens of cells and a few
minutes, not an eightfold increase of the complete tree.

A run that completes within the three-hour time gate but reaches a stop floor without a
certificate terminates `INCOMPLETE`. Stop-floor exhaustion is an independent failure
condition and cannot be treated as a performance-gate pass.

Compared with the approximately 9,000-cell v8.1 path, the measured v9 plan reduces the
cell count by roughly a factor of 40 and makes the three-hour complete-path gate
plausible.

## Broad-range implication

If λ boxes must be no wider than `2^-13`, covering a λ range of width `2^-4` requires

```text
2^(-4) / 2^(-13) = 512 boxes.
```

At approximately 30 to 47 runner minutes per box, broad extension toward `a_c` requires a
separate parallelization or broad-range enclosure design. This does not affect the
immediate single-box target of width `2^-20`.

## Remaining SPEC_PENDING work before v9 freeze

The measured r/λ width decision is materially resolved by the three-layer distinction:

```text
stop floor              2^-16
expected operating      2^-11 through 2^-13
measured boundary       2^-13
```

The remaining work is:

1. exact integration variables and analytically derived integrands;
2. proof conditions for differentiation under the integral sign;
3. the final upper-bound form used by the split score;
4. the normative tie-break;
5. checkpoint `fsync` policy;
6. checkpoint frequency and overhead policy;
7. checkpoint schema and canonical partial-evidence form;
8. the three-hour gate margin and repetition count;
9. the exact definition of “224-leaf-equivalent or stronger” for the five-output kernel.

The prototype remains unsuitable for production until the v9 contract is frozen and the
remaining obligations are discharged.