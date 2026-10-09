# D-OB P2 / D-AN-1 / L1-EVIDENCE-PIN-1 — evidence pin report (Code)

Date 2026-10-09.  READ-ONLY.  No new computation of H, E, kernels, counterexamples or G2; no commit, no push, no branch change, no canonical change.
This report is stored in Code's scratchpad only (instruction §8.3: saving/commit requires separate approval).  L1 PAUSED.  D-P2 NOT_CERTIFIED.

## Required table (§12)
| ID | object | discovery state | evidence check | Full commit | Blob | SHA-256 |
|---|---|---|---|---|---|---|
| E1 | pointwise-pair counterexample | NOT FOUND (Git, Code-accessible non-Git); daybreak-works NOT ACCESSIBLE | UNVERIFIED | — | — | — |
| E2 | G1 counterexample | REPORTED only (one relayed statement, see §4); proof NOT FOUND; daybreak-works NOT ACCESSIBLE | UNVERIFIED | N/A — UNCOMMITTED (session transcript entry) | N/A | entry SHA-256 e23bb7b78f18a58e160b5c168c7d365d16f2fe7c5b4b902aea89a6f357baecec |
| E3 | G2 material original | NOT FOUND (only references to its preservation); daybreak-works NOT ACCESSIBLE | UNVERIFIED | — | — | — |
Judge-reported (separate column, not Code's own result): ChatGPT and Claude conversation histories searched by the Judge — JUDGE-REPORTED / NOT FOUND;
ledger entry "chat 検収 PASS (2026-10-06)" has no pinned calculation file.

## §1 Executive summary
- No document, script, output or log that establishes the negative sign for E1 or E2 exists in any ref or any past commit of `cotaxxxx/bg-oblate-spheroid`
  or `cotaxxxx/basepoint-geometry`, nor in Code's non-Git work area (scratchpad, working tree) or Code's session transcript.
- The only pre-2026-10-09 occurrence of the E2 coordinates in any Code-accessible material is a statement relayed into the Code session by the user on
  2026-10-05 ("L1/G1 では境界近傍 r=127/128, mu=15/17 に固定-mu の負の phi-average の厳密 witness が存在する"; "G1 は厳密 witness で false";
  "G2 は E_rho>0 ⇔ H>0 そのもの ... PAUSED").  It is a REPORT of a result, not the proof.  The E1 coordinates appear nowhere before 2026-10-09.
- Code did not perform the 2026-10-05/06 L1 work: the Code session transcript contains no Code tool call on G1/L1/pointwise/E1/E2 on those dates.  The
  L1 work recorded as "NO COMMIT" was therefore done in another environment (most likely daybreak-works), which Code cannot access.
- The G2 material is referred to only as "Existing G2 material is preserved" (predeclare v1.2); no file carrying it was found.

## §2 Search scope and method
Repositories (fresh read-only `--mirror` clones in the scratchpad, all refs and all history):
- `cotaxxxx/bg-oblate-spheroid`: 28 refs (incl. design/d-ob-p1, design/d-ob-p2, candidate/*, diagnostic/*, implementation/*, prototype/*, rejected/*, tools/*, main), 548 commits.
- `cotaxxxx/basepoint-geometry`: 127 refs (incl. claude/d-ob-p2-resumable-i8dgpn, codex/l43-independent-audit-20261009, agent/*, main), 1467 commits;
  includes `tools/d_ob_p2/diagnostics/`, `comparison_runs/`, `loss_decomposition/`.
Methods: commit-message search; pickaxe `git log --all -G` over every diff for: `15/17`, `127/128`, `15/16`, `r=15/16`, `mu=5/8`, `b=3/4`, `mu=15/17`,
`pointwise[-_ ]pair`, `pointwise`, `\bG1\b`, `\bG2\b`, `G1 ACTIVE|NO VERDICT|NO COMMIT`, `L1 PAUSED|PAUSED`, `phi.average|azimuthal average`,
`mu.integrated`, `G1.{0,60}(phi|azimuth)`; path-name search over the union of all paths ever committed for `artifact|daybreak|l1_|g1|g2|pointwise|counterex`.
Non-Git, Code-accessible: Code scratchpad (all subdirectories except the mirrors), the working tree of `/home/user/basepoint-geometry` (no untracked files),
the read-only canonical clone, and Code's session transcript (`.jsonl`, 2026-09-23 → 2026-10-09; 152 entries dated 2026-10-05/06).
NOT ACCESSIBLE: daybreak-works (no `/home/daybreak` in this container; `basepoint-geometry-artifacts/` exists only there), other agents' sessions,
ChatGPT/Claude histories (only the Judge's report).

## §3 E1 — pointwise-pair (λ, r, τ, μ, b) = (93/200, 15/16, 7/8, 5/8, 3/4)
NOT FOUND.  Every Git hit of `mu=5/8`, `b=3/4`, `r=15/16`, `pointwise[-_ ]pair` is Code's own commit cb22f40c (2026-10-09), which quotes the instruction.
`15/16` hits in bg-oblate-spheroid (37ffce8b, 0bc53da, 0c128246; 2026-10-08) are FT_q south kernel constants, unrelated.  The `pointwise` hits
(L2 9eb8ddee, NP-T 99467ed5, FT_q drafts) concern "pointwise centered kernel", "no pointwise sign of A" etc., not this counterexample.
Session transcript: first occurrence of the E1 coordinates and of "pointwise-pair" is 2026-10-09 (instructions); none from 10-05/06.
Object definition (the "pointwise-pair density"), proof method, audit state: not determinable from accessible material.

## §4 E2 — G1 (λ, r, τ, μ) = (93/200, 127/128, 7/8, 15/17)
REPORTED / EVIDENCE NOT FOUND.  Git: the only hits of `15/17` / `127/128` are cb22f40c (Code report, quoting) and unrelated `-127/128` grid rows in
`loss_decomposition/runs/LD_v1_20261006/.../partition.tsv` (29205372) and C1-C5 diagnostic runs (2026-10-01..05) — numeric grid boundaries, not G1.
`\bG1\b`/`\bG2\b` in bg-oblate-spheroid 2026-09-28..30 (1a868473, ea6214e2, d4465c3b) are gates of the SPEC V3 comparison ("G1 Lower consistency",
"G2 Upper consistency") — a NAME COLLISION, not L1's G1/G2.
Non-Git: Code session transcript, entry line 2447, timestamp 2026-10-05T20:34:27.602Z, type user, uuid 201b3075-5cd2-4d8c-84ee-ad908ba29f90,
SHA-256 of the entry e23bb7b78f18a58e160b5c168c7d365d16f2fe7c5b4b902aea89a6f357baecec.  Content: a relayed statement that a "厳密 witness" of a negative
fixed-mu phi-average exists at r = 127/128, mu = 15/17 and that "G1 は ... false"; λ and τ are not stated there; the witness itself (formula,
script, output) is not included.  Classification: COUNTEREXAMPLE (reported), UNCOMMITTED, proof NOT FOUND.  The φ-integration range and normalization
of the "φ-average" are not given.

## §5 E3 — G2 material
NOT FOUND (original).  References only:
- predeclare v1.2 `analysis/D_OB_P2_D_AN1_PREDECLARE_V1_2.md` (bg-oblate-spheroid, e9c8b1caa3ad502a3d01dafe354b61108787eed2, blob
  931c0cdb0e3f9d81430ae7e9029b3704bf099505, SHA-256 f27a568b...), line 110 ("Existing G2 material is preserved") and line 270 ("Preserved G2 material may
  be used"); introduced in d38126fc76492db0ee31ce068e11612ff1f39820 (2026-10-06).  These record that material exists; they do not identify it.
- predeclare v1.1 (6de8a178b3f9c278952ac68590f97f3f100ed9f9, 2026-10-05) contains no G1/G2/pointwise/PAUSE text.
- Code session transcript line 2447 (above): "G2 は E_rho>0 ⇔ H>0 そのものだが、現在は失敗ではなく PAUSED" — a characterization, not material.
Saved name, location, commit, time of saving, proved/unproved content: not determinable.  Classification: UNKNOWN.

## §6 Evidence classification
| item | Git / non-Git | classification | note |
|---|---|---|---|
| predeclare v1.2 lines 110, 270 | Git (e9c8b1ca) | ARCHIVED reference | asserts preservation of G2 material; not the material |
| transcript line 2447 (2026-10-05) | non-Git, UNCOMMITTED | COUNTEREXAMPLE (reported) for G1; characterization of G2 | relayed user statement; no proof |
| transcript line 2511 (2026-10-05) | non-Git | — | its "NO COMMIT" refers to the L3-MRA file, not to L1 work (SHA-256 181c4fdc...) |
| SPEC V3 G1/G2 (1a868473, ea6214e2, d4465c3b) | Git | not related | name collision |
| `-127/128`, `15/16` numeric hits | Git | not related | grid rows / FT_q constants |

## §7 Missing evidence
NOT FOUND (Code): E1 proof, E2 proof, E3 original, in all refs/history of both repositories and Code-accessible non-Git material.
NOT ACCESSIBLE: daybreak-works and `basepoint-geometry-artifacts/` (where the NO COMMIT L1 work most likely resides); other agents' sessions.
JUDGE-REPORTED / NOT FOUND: ChatGPT and Claude conversation histories.
Independence: Code's search did not use any Astra result.  Code cannot independently confirm anything held only on daybreak-works.
Not done (prohibited): no recomputation of either counterexample, no G2 work.

## §8 Final findings for CHAT AUDIT
1. No proof of E1 or E2 can be pinned from Git or Code-accessible material; per §7.1 both are REPORTED / EVIDENCE NOT FOUND and may not be used as theorems.
2. The earliest record Code holds is the relayed E2/G1/G2 statement of 2026-10-05T20:34Z (transcript line 2447); it can be cited only as a report.
3. E3: the G2 material is referenced (predeclare v1.2 l.110, l.270) but not located; the δ_L1 specification must state its structure as undetermined.
4. The most promising unsearched location is daybreak-works (`basepoint-geometry-artifacts/`, 2026-10-05/06); a search there needs the user or ChatGPT
   (the executor on that host), not Code.
5. Per §7.2, plan B can continue with the design condition that pointwise-pair and G1 uniform positivity are not assumed.
