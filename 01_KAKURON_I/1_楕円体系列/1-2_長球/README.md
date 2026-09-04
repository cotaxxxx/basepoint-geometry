# 1-2　長球

## 論文1 — 存在

**基点分岐：長回転楕円体上で停留円が中心へ収縮する臨界軸比**  
— 錐体積重み付き動径–法線角に対する区間認証 —

- 著者：古田 勝士（Katsushi Furuta）
- 投稿予定先：Experimental Mathematics
- 状態：日本語正典稿（LaTeX ソースと完成 PDF）を登録済み。英訳・archival DOI・投稿版整備が残る
- [完成稿 PDF](manuscript/manuscript.pdf)
- [正典 LaTeX ソース](manuscript/manuscript.tex)
- 図版：`manuscript/figures/fig1_local_bifurcation.pdf`、`manuscript/figures/fig2_shrinking_circle.png`
- 旧 DOCX/PDF（2026-08-23 改稿版）は `manuscript/archive/` に履歴資料として隔離する

## 認証済み内容

- 臨界軸比 `a_c ∈ (4.72438, 4.72439)`
- `Q'(a_c)<0`
- `H_4(a_c)<0`
- 停留円の局所的な収縮と中心 Hessian の nullity 増加
- Arb/python-flint による fail-closed 区間認証
- 証明成果物：[`CERTIFICATES/prolate/local_bifurcation/`](../../../CERTIFICATES/prolate/local_bifurcation/)

## 論文2 — 完全性

軸比全域の停留成分・接続・ラベル構造の完全列挙は論文2の課題である。全域検証機構はリポジトリ内で B-TUBE と呼ぶ。論文1の存在定理は B-TUBE に依存しない。
