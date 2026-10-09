# South paper proof — canonical import plan (Code, 2026-10-09)

Status: PLAN / SUBMITTED FOR CHAT AUDIT.  Nothing is imported by Code (no canonical write access); the user performs byte-identical placement after
Judge approval, as for 22'' v1.2.

## 1. Files to import (source: cotaxxxx/basepoint-geometry, branch claude/d-ob-p2-resumable-i8dgpn; all CHAT AUDIT PASS)
| # | source path | commit | blob | SHA-256 | lines | proposed canonical path |
|---|---|---|---|---|---|---|
| 1 | tools/d_ob_p2/ftq_paper_proof/D_OB_P2_D_AN1_FT_Q_SOUTH_POSITIVE_MASS_DRAFT.md | 05668a47216e243450211f0cf438702dc6d1527c | a66ac60edfc75e70ae198bdea7807e6d5c14b360 | f320acb964cb278d1dd8ef6240fcc88bc9bdf77ae75edd4c77f86ce78da93d3c | 126 | analysis/D_OB_P2_D_AN1_FT_Q_SOUTH_POSITIVE_MASS.md |
| 2 | tools/d_ob_p2/ftq_cert/bernstein_G.py | f74e1221762f1b52e00bf5fbc7ba3b548526f953 | 15a773446cb43c667e377e2575e721570e2703d8 | 97057844894f699dea9a994dc7b9d2c5f46673d9f67c5b9c9535f5e7f4cc23e3 | 62 | analysis/ftq_cert/bernstein_G.py |
| 3 | tools/d_ob_p2/ftq_cert/bernstein_south_A.py | f74e1221762f1b52e00bf5fbc7ba3b548526f953 | 48a185c3f0e760c5bd3a9d0773747842779296c9 | 977f629435d84dfda5152271d8774f2f432757f8f7cc5d5615ef8df820e5a0af | 81 | analysis/ftq_cert/bernstein_south_A.py |
| 4 | tools/d_ob_p2/ftq_cert/theta_14_over_5_cert.py | 6621f3d9c234557200f1d6a884ed603306ca1b40 | 955011114ea677d583b97295859858d75482b2d0 | f0ab87b17507451197c06f2ab25cca66f1083c1f609b93f83e1c135c97ca8b88 | 58 | analysis/ftq_cert/theta_14_over_5_cert.py |
| 5 | tools/d_ob_p2/ftq_cert/kernel_extension_cert.py | 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e | 3600e0771c73456698035484eb267415111acc4d | 3c4b0d452d87072c2c7a27d432048691c4cce47da871bfad0a50630436146e85 | 111 | analysis/ftq_cert/kernel_extension_cert.py |
Astra certificate-39' originals (report 1d084881..., script 4b51bd9b..., coefficients 853d022e...) are cited by SHA-256 in file 1 §0; they are not in
this repository.  Import of those three is Astra's / the user's decision; file 1 remains valid as long as its pins are cited, not imported.

## 2. Procedure (user)
 1. For each row: `git -C <basepoint-geometry> show <commit>:<source path> > <bg-oblate-spheroid>/<proposed path>`.
 2. Before commit: `sha256sum` and `git hash-object` must equal the table (no newline / encoding conversion).
 3. One canonical commit containing only these files; then report full commit, blobs, SHA-256 to CHAT AUDIT for raw readback.
 4. Code then updates the pin rows that say "canonical import NOT DONE" (22'' closure record, predeclares) in a separate commit.

## 3. Open choices for the Judge
 (a) proposed canonical paths (the `analysis/ftq_cert/` directory does not exist yet in canonical);
 (b) whether to import the Astra 39' originals;
 (c) whether file 1 is imported verbatim with its "DRAFT" title or with a status-only header change (a change would make the SHA-256 differ and
     requires a re-audit of the changed file).
