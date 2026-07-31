# Item 3 Sweep v9 Prototype — Static and Diagnostic Audit

**Status:** `PROTOTYPE / NOT AUDITED / NOT APPROVED`  
**Issue:** #23

## Scope

This audit covers only the new files under
`lambda_sweep/v9_prototype/`. It does not approve a production kernel, config, tag,
workflow, or certificate.

## Source hashes prepared before publication

```text
prolate_F_derivatives_cleanroom_v9.py  9a237ef8f3d7f46d661ef68d1edff9f47ee22c3f25ac8b9630e5b3d64b321966
mean_value_core_v9.py                  6270059c2dfad1586a4ce86f1b3b0ceac31ef1c15278dbcdeae17923190a5188
symbolic_audit_v9_derivatives.py       1ccf104057818d32ef70cea8bb28cca9b018c942dae3f49622356c79e1028238
test_v9_derivative_kernel.py           c64926a0b0248dcd427308dc7286c38ce4187cf396963648eed68b904c2055c8
test_mean_value_core_v9.py             96ffaff10d6474322aa9976ccedbfea7e75865a265d275b6027993b02fa8757e
```

These hashes describe the locally audited candidate bytes. Git blob and post-publication
SHA checks must be performed after the files are committed.

## Checks executed

### Syntax

All five Python files passed `python3 -m py_compile`.

### Symbolic geometry diagnostic

The exact symbolic audit returned:

```json
{"checks":{"gamma_lambda":true,"gamma_r":true,"gamma_rlambda":true,"gamma_rr":true,"gamma_rrlambda":true,"gamma_rrr":true,"h3_at_one":true},"proof_status":"DIAGNOSTIC_ONLY","schema":"ITEM3_SWEEP_V9_SYMBOLIC_DIAGNOSTIC_V1","verdict":"PASS"}
```

### Exact mean-value core tests

Seven tests passed:

- exact midpoint construction;
- strict-negative mean-value example;
- exact score tie selects `r`;
- nonfinite outranks finite;
- double-nonfinite tie selects `r`;
- unsplittable axes are excluded;
- exact midpoint children.

Result:

```json
{"errors":0,"failures":0,"schema":"ITEM3_SWEEP_V9_MEAN_VALUE_CORE_TEST_V1","tests_run":7,"verdict":"PASS"}
```

### Float derivative diagnostics

Using the fixed midpoint grid in the prototype, central finite differences were compared
with the implemented analytic formulas at three representative points. Two test groups
passed:

```json
{"errors":0,"failures":0,"proof_status":"DIAGNOSTIC_ONLY","schema":"ITEM3_SWEEP_V9_FLOAT_DIAGNOSTIC_V1","tests_run":2,"verdict":"PASS"}
```

The diagnostic used a local stub only to satisfy the top-level `flint` import while
executing the independent float path. No rigorous `arb` or `acb` function was executed
locally.

## Static boundary observations

- the new kernel does not import or modify the existing production kernel;
- finite differences appear only in the diagnostic test;
- the rigorous source contains no workflow, tag, config, or certificate operation;
- the mean-value core uses exact `Fraction` arithmetic only;
- the split rule is deterministic and implements the frozen exact-arithmetic layer;
- no resume behavior is introduced;
- no production adapter is changed.

## Unresolved obligations

1. Execute rigorous `arb/acb` point and interval tests with pinned `python-flint`;
2. independently rederive all five integrands;
3. prove differentiation-under-integral conditions;
4. select and freeze quotient interval association;
5. connect the kernel to a separate prototype adapter;
6. implement fresh checker calls and counters;
7. perform the required adversarial validation corpus;
8. benchmark each rigorous derivative output;
9. freeze child ordering and stack insertion;
10. freeze checkpoint schemas and durability rules.

The prototype remains unsuitable for production until all obligations are discharged.
