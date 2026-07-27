# item2_circle — 大域停留円枝の一意性（管認証＋外部排除）

ブランチ: `agent/prolate-item2-circle`（main 3888936 起点、項目6と独立）

## DAG

- **B-KERNEL**: 項目0の `F(r,λ)` Arb 核と `∂F/∂r` 核の入庫（下記「前提債務」）
- **B-LOCAL**: 局所分岐証明書の参照（新規計算なし）
- **B-SEED**: 浮動小数 Newton による `r_c(λ)` 予測グリッド（非厳密・証明不使用）
- **B-TUBE**: 各 λ 箱で Krawczyk 縮約 → 管内に零点がちょうど1個（非退化）
- **B-EXT-LOW / B-EXT-HIGH**: 管の内外での F の符号一定性（項目0判定基準を踏襲）
- **B-JOIN**: 隣接 λ 箱の管の重なり（枝の連結性）
- **B-DAG**: 依存監査と SHA-256 manifest

λ 範囲: 局所正規形接続点（界面のみ固定、接続自体は項目3）から λ=100。

## 前提債務（B-KERNEL）

item0d 認証ランナーが import する `prolate_general_r_arb_kernels.py` と
`riemann_rescue.py` はリポジトリ未収録。元成果物 ZIP から無改変で
`item2_circle/vendor/` に入庫し、SHA-256 を manifest に記録すること。
`∂F/∂r` の Arb 核が元成果物に無い場合は、F と同一の式から記号導出して
新規核を作り、symbolic audit（項目6と同形式）を付ける。

## 実行規律

workflow_dispatch 専用。パイロット（λ∈[5,6]、max-boxes 256）先行。
raw JSON は末尾改行なしで保存し sha256 は保存バイト列に対して計算。
本番 run は項目6の待機中 run 完了後に投入。

## 判定基準

B-TUBE: Krawczyk 像が箱の内部に真に含まれること（存在＋一意＋非退化）。
B-EXT: terminal 0、exact rational coverage、全葉で符号一定。
