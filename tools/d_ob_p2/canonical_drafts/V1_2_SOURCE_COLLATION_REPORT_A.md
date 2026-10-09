# 提出A — 22'' v1.2 原典照合報告（Code, 2026-10-09）

照合対象原典（読み取り専用 canonical clone `cotaxxxx/bg-oblate-spheroid` で Code が直接 readback）:
- v1.1: `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_1.md`, commit b1a10ea6f0ef127aaf4a40a93070cf270d03e073,
  blob 49e658b0487123249eb81d70bde1ef188ff640d7, SHA-256 db975daba9d712246ed5e27465437f34450b356f453729a5fb78ec8ceab468cb, 55 行。指示書の pin と一致。
- 親契約: commit 00138df257cee8e5480b412157dce36ae90743d0（存在確認のみ）。
- 検査対象本文（提出B）: `tools/d_ob_p2/canonical_drafts/analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_2.md`（作業ブランチ、canonical 未 commit）。

| 検査項目 | 原典・根拠 | 判定 |
|---|---|---|
| A1 座標変換 s = m − μ | v1.1 §21'' 本文「Exterior south has s=m-mu>221/565」で s = m − μ が定義済み。μ = m − s は減少写像で s ∈ [ρ, 1/2] ↔ μ ∈ [m−1/2, m−ρ]（記号計算で確認）。v1.2 §22'' 冒頭に明記 | PASS |
| A2 重なりの存在 | m ∈ [112/113, 1] ⇒ m − 1/2 ∈ [111/226, 1/2]（112/113 − 1/2 = 111/226 を厳密計算）。m − 1/2 ≤ 1/2 なので south [−1, 1/2] と north far [m−1/2, m−ρ] は [m−1/2, 1/2] で重なる | PASS |
| A3 重なり幅 | 1/2 − (m − 1/2) = 1 − m ≤ 1 − 112/113 = 1/113（厳密計算） | PASS |
| A4 全域被覆 | m − 1/2 ≤ 1/2 で south と far に隙間なし、m − ρ は far と near の共有端、near の上端は 1。和集合 = [−1, 1] | PASS |
| A5 片側評価 | G ≥ −[−G]₊ より ∫₋₁¹ G ≥ ∫₋₁^{1/2} G − ∫_{1/2}^{1}[−G]₊。[1/2, 1] ⊂ [m−1/2, 1] と被積分関数の非負性から ∫_{1/2}^{1}[−G]₊ ≤ U_north + U_near。重なり分は右辺を下げるのみ（安全側 slack）。S''_lb の導出区間は [−1, 1/2]（paper proof 05668a47 §6）で整合 | PASS |
| A6 v1.2 本文への反映 | A1–A5 は v1.2 §22'' AMENDED の「Regions」「Coverage and overlap」段落に明記 | PASS |
| A7 20''・21''・23'' 不変 | v1.1 の §20''、§21''、§23''、「Corrections and next work unit」を文字列として逐語複写し、v1.2 本文に部分文字列として含まれることをプログラムで確認（4 節とも True） | PASS |
| A8 South 導出元と入力証明書の分離 | v1.2 §22'' に「Derivation source」（05668a47…, a66ac60e…, f320acb9…; CHAT AUDIT PASS / canonical import NOT DONE）と「Input certificate」（1ac44469…, 3600e077…, 3c4b0d45…; CHAT AUDIT PASS）を別行で記載。pin は Code が作業ブランチで readback 済み | PASS |
| A9 旧予算と新予算の区別 | **差異あり**: v1.1 §22'' の正式条件は「Require U < 207/5000」（U は 21'' の (−1/4, 1] 上の外部残差上界）。指示書 §3.E の「104/625 = 207/5000 + 1/8」は v1.1 本文に存在しない（後続の作業文書で C_core ≥ 1/8 を加えた非公式の派生値）。v1.2 では「v1.1 の U < 207/5000 を supersede」と記し、104/625 は由来付きで「同様に supersede される派生値」として注記した。far 単独（5481/10000）が 207/5000 と 104/625 の双方を超過する事実も記載 | PASS（修正案を本文に反映済み、Judge 確認要） |
| A10 P 単位と正規化 | v1.1 ヘッダ「Units: S_K, C_out and U are in double-integral P units」、§22'' の H ≥ (…)/(2πλ) は 2πλH = ∫G と整合。far 証明書（contract 45）と Astra L43 は同じ外側 π・dμ dφ・ξ 平均の P 単位。v1.2 ヘッダに「2 pi lambda H = integral G」を明記 | PASS |

差異の有無: A9 の 1 件（旧予算値の表記）。その他の pin・定義に差異なし。
HOLD 要件: A1–A6 すべて PASS。

付記（Code 証明書 (C6) への含意）: v1.2 条項は U_north + U_near < S''_lb なので、near 側の比較値は S''_lb − U_north,cert = 635530452759/817216000000 − 5481/10000
= 187614363159/817216000000 となる。この値は v1.2 の canonical pin 後にのみ `BUDGET_V12` に設定する（§7 禁止事項に従い現時点では未設定）。
