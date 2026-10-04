# D-OB P2 Candidate Comparison Closure Report

**Status:** FINAL / CHAT COUNTERSIGNED / CLOSED
**Evidence:** DIAGNOSTIC / NOT_EVIDENCE
**D-P2:** NOT_CERTIFIED

This closes only the frozen candidate-comparison experiment. It does not certify D-P2 or touch the formal producer/checker lineage.

## CR1 — Human adjudication

**Decision: adopt no candidate. Candidate comparison CLOSED. SPEC V3 drafting remains HOLD.**

Under frozen §18 there is no evaluator-declared winner; under §22 adoption is human adjudication. Every tested candidate leaves the B44 band unresolved. The strongest useful lever, `C-count` (cell budget ×2), improves finite-width behavior but still leaves **177/191 C5 boxes unresolved** (22 accepted). Therefore no measured candidate closes D-P2. The negative result — **none of the frozen candidates closes D-P2** — is the principal outcome.

## CR2 — 9 configurations × §11 six gates

Canonical evaluator pins: evaluator `303bbf9b9d5845e4e5bd314d3fba77734c273e80b6a51ae7e7918db91e42908e`; report `968cec1b34fc01bffec3eaad1ac5c32a7175cdfa8c4ccda0a83b1b5770ab7f0a`; stdout `298c11d04a789a6eda25a3f6f55cd3d47bc1067e01e659457b9c681a0363e451`; 41-spec ledger `1aacd619a0a6786b37120ab0e0e79e46849540ad3424c46581e041a4f6b82626`.

Frozen gate order: **Soundness → Identity/reproducibility → Width → Certification utility → Cost → Independent checking**. Evaluator `winner_rule = None`; this is an adjudication ledger, not a scalar ranking.

| configuration | Soundness | Identity / reproducibility | Width | Certification utility | Cost | Independent checking | disposition |
|---|---|---|---|---|---|---|---|
| C0 | PASS in diagnostic domain | replication reference | reference | C5 8 accepted / 191 unresolved | reference | frozen controls | reference only |
| C-count | PASS | one-change checked | improves; C5 mean 32.2302→24.9579; matched-box ledger ≈−7.6 | best utility; C1 +20 accepted; C3 +1 B; C5 22/177 (+14) | materially higher | frozen fields retained | **REJECT; useful lever only** |
| C-cell-depth | PASS | one-change; substantive no-op | no change | C5 8/191 | essentially baseline | retained | **REJECT / no-op** |
| C-box-depth | PASS | one-change | improves on target-child basis; ≈−3.1 | C5 21/178 (+13); B44 unchanged | ≈+25% prior ledger | retained | **REJECT**; sibling caveat |
| C-regular | PASS | one-change | strict degradation; C5 mean 32.2302→170.7450 | C1 accepted 68→0; C5 8→2 | lower runtime but unusable | retained | **REJECT / degradation** |
| D-rho-1-16 | PASS through existing sets | C1–C3 bitwise baseline replication | unchanged where evaluable | C4 **NOT EVALUABLE** (`R2 must be positive`); C5 **NOT RUN** | no full-chain comparison | retained | **REJECT / no-op where evaluable** |
| D-rho-3-32 | PASS through existing sets | C1–C3 bitwise replication; C4 failure log byte-identical to 1/16 | unchanged where evaluable | C4 **NOT EVALUABLE**; C5 **NOT RUN** | no full-chain comparison | retained | **REJECT / no-op where evaluable** |
| D-rho-5-32 | PASS | **451-row full bitwise replication** | no change | C5 8/191; C4 7/7 including r=1/10 near return | baseline-like | retained | **REJECT / full no-op** |
| D-rho-1-4 | PASS | **451-row full bitwise replication** | no change | C5 8/191 | baseline-like; C5 wall time matched C0 to second (auxiliary only) | retained | **REJECT / full no-op** |

C-box-depth attribution is target-containing-child only; sibling was not computed, so this is not full parent certification. D-rho-1-16 and 3/32 have only C1–C3 result TSVs; C4 stopped fail-closed and C5 was not run. D-family point-limit/far behavior is a protocol-domain limitation, not evidence of improved near computation.

## CR3 — Cross-candidate findings

1. **B-band immobility:** B44 does not close under tested resource/depth/RHO0 axes. Budget ×2 rescues only 1/44 B point in C3 and gives no B-band C5 flips; cell depth is non-binding; box depth gives no B-band C5 flips; regular expansion degrades; RHO0 is a deep-near structural no-op.
2. **N-band:** cell budget is the only useful frozen lever for the N/enclosure-width failure mode. It improves width/acceptance but does not close D-P2.
3. **Replication:** four RHO0 controls reproduce baseline substantively at bit level in their common evaluable domains; 5/32 and 1/4 are full 451-row replication controls. Runtime similarity is auxiliary only.
4. **Protocol domain:** for small RHO0 the r=1/10 C4 target enters the far/point-limit path and triggers `ValueError: R2 must be positive`; C4 is **NOT EVALUABLE** and C5 **NOT RUN**. At 5/32 and 1/4 it returns to near, C4 is 7/7, and full results are baseline-bitwise.

## CR4 — Next-design boundary

No next route is selected here.

1. **Plan C: `(a)+(c)` composite characterization** may be proposed in a **new predeclare/version** under the frozen v2 §6.2 post-(c) revival allowance. Purpose: measure the boundary between numerically closable and analytic-handoff domains, not claim certification. Frozen v2 ledger: commit `d4465c3b7377528845af51549f54050a58c6b8e3`, file SHA `06fe184c565982cf295d03f7dd421662ec7672a48686229d5a44d69b5badbb7d`. That object is absent from this clean clone, so §6.2 text is not reproduced verbatim here.
2. **B-band routes for separate adjudication:** `(b)` geometric/coupled redesign; `(e)` analytic handoff; **D-problem (cross-sectional monotonicity) track**.
3. Priority is explicitly undecided. Plan C first vs D-problem mainline vs B-band geometry is a new post-closure Judge.

## CR5 — Evidence boundary

Everything here is **DIAGNOSTIC / NOT_EVIDENCE**. **D-P2 remains NOT_CERTIFIED.** No comparison artifact is promoted into formal evidence; formal producer/checker lineage is untouched. Any future formal SPEC V3 requires a fresh SPEC, independent formal producer/checker treatment, required F-list controls, fresh pins and fresh authorized run. Old diagnostics never become formal evidence by adoption, rejection or citation.

## CR6 — Pin / checkpoint ledger

- `ff8fc50cf4f286a375cbca8bfed8452757eac78a` — C0 C1
- `18e6b5b6dc76a334dda13c73e17c783bad81e6ec` — C0 C2–C4
- `d4fa18f3760aa53954e07680f5b77e56d304c738` — C0 C5
- `fdbb5977e6454a9e8145072fddd3a036e3b0f73e` — C-count C1–C4
- `c63b3814fb2b69543300dfe4cf81b2a78d0c3149` — C-count C5
- `ed639f0e00ed7ffb92c39d1c4acdfea0a1d0cf04` — C-cell-depth C1–C4
- `1fedceb63c8eada5dcc95b5257687da6d942e127` — C-cell-depth C5
- `501caf5e642fcf1997c55a02a079735f8aefefbc` — C-box-depth C1–C4
- `f2d23b0a051cd6a5b1c81bca7f7c233fe414e003` — C-box-depth C5
- `574dadf5d569dfb8e95b5304d6ae4af0be594fb9` — C-regular C1–C4
- `be0e8092ef0bf694dc15c066525d8e8e0f133392` — C-regular C5
- `5e5ba65c6775f9051dcc01f0050ae1c1971c81ef` — D-rho-1-16 C1–C4 checkpoint; C4 fail-closed/no result
- `68612372beb0c7fa1da6b7f94cf1b51521f01e55` — D-rho-3-32 C1–C4 checkpoint; C4 fail-closed/no result
- `25a692f6ce1acdda092e3c810c37497f455fb5ff` — D-rho-5-32 C1–C5
- `c4baf3a6bd32d557ed113fd6dfe4ec8c26e9fce6` — D-rho-1-4 C1–C5
- `78b0f197518306baa37729338a8e42b42e21e129` — frozen evaluator output/invocation ledger

Failure/non-adopted artifacts: D-rho-1-16 C4 log SHA `0c36ade480e3b9f0f8366696d8dd6adb1df9964a000d640fb07d6b32ef5f53aa`; D-rho-3-32 C4 log has the same SHA and byte-identical `R2 must be positive` failure. Evaluator malformed-invocation stderr SHA `491c9a3116187da81f62d3026ba3eedda798746022474e87521309e78fddf688` (`CANDIDATE_ID_MISMATCH`, **NOT ADOPTED**); malformed stdout empty SHA `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. Successful evaluator pins are in CR2.

## Closure statement

The candidate-comparison chapter is **CLOSED with zero adoption**. This establishes no theorem/certification; it establishes the diagnostic decision boundary for the next separately governed design Judge.
