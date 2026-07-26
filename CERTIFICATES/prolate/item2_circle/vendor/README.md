# vendor/ — B-KERNEL 入庫指示

1. 元成果物 ZIP から `prolate_general_r_arb_kernels.py` と
   `riemann_rescue.py` を無改変でここに置き、両ファイルの SHA-256 を
   `SHA256SUMS_VENDOR.txt` に記録する。
2. `prolate_circle_kernels.py` をここに新規作成し、次の4関数を公開する:
   - `F_arb(r: arb, lam: arb) -> arb` — F の厳密包含（vendored 核を呼ぶ）
   - `dFdr_arb(r: arb, lam: arb) -> arb` — ∂F/∂r の厳密包含。
     元成果物に無い場合は F と同一の式から記号導出し、
     symbolic audit（項目6形式）を添付する
   - `F_float(r: float, lam: float) -> float` / `dFdr_float(...)` —
     B-SEED 用の非厳密版（同じ式の float 評価）
3. 監査: ランダム有理点で F_arb と F_float の整合、および
   dFdr_arb と F_arb の差分商の包含整合を確認する smoke を付ける。
