# ERRATUM — D-OB P2 Candidate Comparison Closure Report

Date: 2026-10-06 (JST)

Status: **DIAGNOSTIC / NOT_EVIDENCE**

Applies to:
- `tools/d_ob_p2/D_OB_P2_CANDIDATE_COMPARISON_CLOSURE_REPORT.md`
- closure-report SHA-256 `cd1c8e71dd5e1af8f000808f38d46d220a30e0b5f72abb6daca62e7d4f06a148`
- closure commit `ab683fc33543dcb2cd3f5e0a0eeee7ef2c7031e0`

The canonical closure report above is retained byte-for-byte. This adjacent file records corrections to interpretation and counting only. It does not reopen the candidate comparison, adopt a candidate, change D-P2 status, or create certification evidence.

## ER-1 — Meaning of saved width columns

For rows with `B_cut > 0`, the comparison driver's saved columns do not represent the full enclosure width around the full integral.

The saved quantities are

[
U_{saved}=U_{reg}+B_{cut},qquad
W_{saved}=U_{saved}-L,
]

while the producer's full enclosure is

[
[L-B_{cut},,U_{reg}+B_{cut}].
]

Therefore the full enclosure width is

[
W_{full}=W_{saved}+B_{cut}.
]

Likewise, on a row with `B_cut > 0`, a saved `J_minus_L` measured from `L` omits the lower-side cut penalty; the distance from the full lower bound to the same reference J is `J_minus_L + B_cut`.

Consequently the following CR2 width statements must be read as statements about the saved driver width, not the full enclosure width:

- `C-count`: “C5 mean 32.2302→24.9579; matched-box ledger ≈−7.6”.
- `C-box-depth`: “improves on target-child basis; ≈−3.1”.
- `C-regular`: “C5 mean 32.2302→170.7450”.
- Any comparison that interprets `enclosure_width` or `J_minus_L` on cut-positive rows as a full-integral lower/upper enclosure quantity requires the same correction.

This does **not** change the zero-adoption closure or the measured B-band immobility conclusion. Those conclusions were based on acceptance outcomes / accepted counts and the frozen candidate comparison, not on treating `W_saved` as the full width. The canonical producer's acceptance test using `L-B_cut` is not corrected by this erratum.

## ER-2 — C5 rows versus distinct boxes

C5 contains duplicate rows for some identical `c5_box_bounds`. The closure report's C5 utility counts were row counts. Recounting by exact `c5_box_bounds` gives:

| candidate | C5 rows | distinct boxes | accepted rows | accepted distinct boxes |
|---|---:|---:|---:|---:|
| C0 | 199 | 197 | 8 | 7 |
| C-count | 199 | 197 | 22 | 20 |
| C-cell-depth | 199 | 197 | 8 | 7 |
| C-box-depth | 199 | 197 | 21 | 20 |
| C-regular | 199 | 197 | 2 | 1 |
| D-rho-5-32 | 199 | 197 | 8 | 7 |
| D-rho-1-4 | 199 | 197 | 8 | 7 |
| D-rho-1-16 | NOT RUN | NOT RUN | NOT RUN | NOT RUN |
| D-rho-3-32 | NOT RUN | NOT RUN | NOT RUN | NOT RUN |

Thus the closure report's “certification utility” comparison used rows rather than distinct boxes. In particular, C0 has 8 accepted rows / 7 accepted boxes, while C-count has 22 accepted rows / 20 accepted boxes. The row-based utility numbers remain a faithful description of the stored C5 rows, but must not be relabeled as distinct-box counts.

The zero-adoption conclusion is unchanged: no frozen candidate closed D-P2, and every tested candidate left the B44 band unresolved under the frozen comparison.

## ER-3 — Scope of D-AN-1

A prior chat statement that proving `H>0` in D-AN-1 would remove the need to certify all 7,662 unresolved D-P2 terminal boxes was too broad.

The canonical unresolved map is:

- `(7,7,0)`: 4,078 unresolved boxes.
- `(0,0,3)`: 3,584 unresolved boxes.
- total: 7,662.

D-AN-1 is scoped to the `(7,7,0)` band and can address at most those 4,078 unresolved boxes through its analytic handoff. The `(0,0,3)` band is explicitly reserved for D-AN-2 and requires that separate analytic stage. D-AN-1 alone must not be described as removing all 7,662 numerical certification obligations or certifying the whole D-P2 unresolved set.

This correction is to the prior chat interpretation; it does not modify the byte-frozen closure-report body.

## ER-4 — Provenance of the corrections

ER-1 and ER-2 were first identified in the read-only local investigation supplied as **“Astraへの局所の問い”**. Chat then checked the stored comparison data and confirmed the relevant width definition and row-versus-box counts. Code subsequently re-audited the cited remote primary material and independently agreed with these corrections.

All statements in this erratum remain **DIAGNOSTIC / NOT_EVIDENCE**. No producer/checker semantics, frozen harness, canonical result file, or D-P2 certification status is changed.

## Status after erratum

- Candidate-comparison closure: **CLOSED / ZERO ADOPTION**.
- Closure-report body: **UNCHANGED BYTE-FOR-BYTE**.
- This erratum: **DIAGNOSTIC / NOT_EVIDENCE**.
- D-P2: **NOT_CERTIFIED**.
