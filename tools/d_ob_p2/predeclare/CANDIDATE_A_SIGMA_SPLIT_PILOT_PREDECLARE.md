# D-OB P2 candidate (a) sigma-split pilot: measurement predeclare

Status: DIAGNOSTIC / NOT_EVIDENCE. Pre-measurement freeze candidate.
No L, W or margin value of any real unresolved leaf has been computed or seen when this
document was written. D-P2 remains NOT_CERTIFIED; nothing in this document or its run changes that.
This document is not part of canonical `design/d-ob-p2`.

## 0. Purpose and scope

The pilot selects the sigma-split count k* for candidate (a) (v2 comparison predeclare), or
declares candidate (a) NOT READY at k <= 8. It is a parameter-selection measurement only.
It does not measure candidate (a) performance, does not accept any leaf, and does not fill
any v2 [TBD] other than the candidate (a) k value, and that only through Section 5.

## 1. Pins

| object | value |
|---|---|
| measurement script | `tools/d_ob_p2/near_sigma_split_measure.py`, SHA-256 `a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d` (commit `5132f0a15804c654f943144938ae74be8ed0da24`, repo `cotaxxxx/basepoint-geometry`) |
| producer | SHA-256 `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b` (checked by the script before any work) |
| map | `full_terminal_map.tsv`, SHA-256 `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8` (output of `extract_unresolved_map.py`) |

A file whose SHA-256 differs from its pin must not be used. `--workers` does not affect results
and is not pinned.

## 2. Preconditions (all required before the run starts)

1. Byte audit of commit `5132f0a` (script above) recorded as PASS.
2. Audit item on the sigma-split premise closed: C^1 regularity of s -> F_rho along
   s = sigma*rho for regular near cells, in particular at gamma -> 1 (series chart,
   gamma >= 7/10), checked against the producer source. Raw data: commit `48e92fb`.
3. This document frozen by its commit SHA and file SHA-256.
4. The `--check-only` command of Section 3 prints exactly the expected line.

## 3. Population, sample and commands

- Population: rows of the map with `decision=unresolved` and `column=near`, in file order: 7,662 rows.
- Sample: `stride:32:0`, i.e. population indices 0, 32, ..., 7648: 240 leaves.
- Changing the stride or the offset, searching over offsets, or replacing any sampled leaf
  after the run starts is forbidden.

Check-only command (paths resolve to files with the pinned SHA-256):

```
python3 near_sigma_split_measure.py --producer <PRODUCER> --map <MAP> --select stride:32:0 --ks 1,2,4,8 --check-only
```

Expected stdout, exact and complete:

```
population_near_unresolved=7662 selected=240 ks=[1, 2, 4, 8]
```

Any other output: stop; the run does not start.

Run command:

```
python3 near_sigma_split_measure.py --producer <PRODUCER> --map <MAP> --select stride:32:0 --ks 1,2,4,8 --out <OUT.tsv> --workers <W>
```

`<OUT.tsv>` must not exist beforehand. The executor records the host identity in the report.
The TSV header also records host, Python and python-flint versions, and the script and map SHA-256.

## 4. Run-validity gate

The run is VALID only if all of the following hold. Otherwise the result is RUN INVALID and no k*
is selected.

1. Exit code 0, and the stdout summary is `rows=240 not_still_unresolved=0 k1_not_reproduced=0`.
2. The output has exactly 240 data rows, and their keys equal the selection in selection order.
3. For all 240 rows: `L1_reproduces_producer=yes`.
4. For all 240 rows: `still_unresolved=yes`.
5. For all 240 rows: `margin_k1_lower <= 0`.

Item 5 is not checked by the script's exit code; it is checked on the TSV.

## 5. Score and selection rule

For k in {1, 2, 4, 8}:

    p_k = #{ i : margin_k{k}_lower(i) > 0 } / 240

- The denominator is always 240. Rows with `fallback_k{k} > 0` are neither excluded nor
  treated differently.
- The decision uses the point value only. No confidence interval, standard error or
  near-threshold rescue is applied.
- k* is the smallest k in {2, 4, 8} with p_k >= 0.90, that is at least 216 of 240 rows with
  margin > 0.
- If no such k exists, the outcome is: candidate (a) NOT READY at k <= 8.
- k = 1 is the baseline reproduction control and is never a candidate.
- No value k > 8 is adopted or extrapolated from this pilot.
- The threshold 0.90 and the k list are not changed after seeing any result.

Report p_k for every k (including k = 1, expected 0 by gate item 5) as a count out of 240.

## 6. Fallback reporting

For each k in {1, 2, 4, 8}, report:
- the number of leaves with `fallback_k{k} > 0`
- the sum of `fallback_k{k}` over all 240 leaves (total fallback cells).

A fallback cell uses the baseline enclosure of that cell, which is still sound; fallbacks are
reported, not corrected.

## 7. Fixed-partition gap rule

The values measured here are computed on the baseline (final) cell partition of each leaf.
They are not results of an adaptive candidate (a) run.

- `margin_k{k}_lower > 0` is classified only as "pilot rescue" (fixed-partition rescue).
- No acceptance of any real leaf by candidate (a) is claimed from this pilot.
- If k* exists, the next stage reruns the same 240 keys with candidate (a)'s actual refinement
  rule at k = k*. That implementation is a separate artifact with its own predeclare and audit;
  this document does not define it. The rerun must preserve the baseline checks.
- For each of the 240 keys, compare fixed-partition rescue (margin_{k*} > 0 here) against
  rerun rescue (the leaf is accepted in the rerun), and record the two directions separately:
  - fixed rescue and rerun not rescue: adverse disagreement. If there is at least one,
    freezing candidate (a) is stopped until the cause is audited.
  - fixed not rescue and rerun rescue: beneficial disagreement. The count is recorded; on its
    own it does not stop freezing candidate (a).
- If k* does not exist, the gap stage is not run.

## 8. Reporting

Report verbatim: the check-only stdout, the run stdout, the exit code, the output TSV SHA-256,
the host identity, the gate result (Section 4), p_k counts (Section 5), and the fallback counts
(Section 6). Any change to this document after the run starts voids this predeclare; a changed
plan needs a new version and a new run.
