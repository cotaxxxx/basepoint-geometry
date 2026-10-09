# Contract 43 — 二件の独立提出と FREEZE 状態

日付：2026-10-09。Repository `cotaxxxx/basepoint-geometry`、branch `codex/l43-independent-audit-20261009`。
成果物 path prefix: `tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/`。
原納品 commit `0c1189f9af5eb221abfc518b110e11dda345b4b0` を履歴に保持し、追補する。
各ファイルの完全 commit/blob/SHA-256/行数は、証拠 commit 作成後に `FULL_PIN_TABLE.md` へ固定する。

## 第一提出：成果物5点

1. `l43_graph_majorant_exact.py`: 固定版・変更なし・46検査の既存実行済み。
2. `exact_checks.stdout.txt`: 同じ固定版の生 stdout・変更なし。機械出力 `exact_checks.json` と空の `exact_checks.stderr.txt` も提出。
3. `source_manifest.json`: 原典 pin、成果物のハッシュと依存関係、E-43 反映状態、未完了義務を加えた更新版。初版は原納品 commit に保存。
4. `D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md`: §3.1 端点補題、§7 の最終余裕、正式指示の状態を追補。主連鎖・有理三成分・合計は変更なし。
5. `E43_CORRECTION_NOTICE_2026_10_09.md`: 物理帯・識別子訂正を反映。ここへの提出と repo 保存を記録し、外部宛直接送信とは区別。

補助資料 `EXACT_CHECK_MAP.md` は全46検査と報告の対応、演算方式、環境、コマンド、検査対象外を列挙する。
`EXECUTION_PROVENANCE.json` は元の実行・終了観測を保存する。今回は再実行していない。
提出済みであることは CHAT AUDIT の受領・内容監査・countersign の代用にならない。

## 第二提出：H-43-1(ii) 独立補題

全文は `H43_ENDPOINT_LEMMA.md`。主報告 §3.1 と一致する。
義務A: ξ→±ρ の片側トレース、μ=m−ρ の両側と cap μ=1 の片側。
義務B: P1 design note §5 Lemma V と同一の密度・固定方向微分・測度を使い、境界積分の一致を示す。
義務C: `|F_xixi|≤(2π+2)/D`、平面 layer-cake 評価、一様可積分性による L1 収束、球切除の誤差評価、絶対可積分 Fubini を示す。
対角点での経路非依存の密度値は仮定しない。既存の境界値を新しい定義で置換しない。
**紙上証明を提出するが、H-43-1(ii) は OPEN・CHAT AUDIT 判定待ち。**

## 正式指示に対する状態

| 項目 | 状態 |
|---|---|
| 正式経路 | Astra 単一片連鎖 (5.5)→(5.7)→(6.5)→§7。旧 C1–C5 は SHELVED、並走しない |
| predeclare v3 | `459abecf3249ace4789e4a94708218fa0128363e`。設計 CHAT AUDIT PASS（正式指示に基づく） |
| predeclare v3.1 | `06f5bd2b69ce94a0dbe65dc6ff9a1c7025f0bf10`。pin 更新監査 PASS。原文 §4–6 を今回照合 |
| Code 証明書 | `213ec4bb107701d0d962738db824845721f5f299`。静的レビュー PASS・未実行・実行禁止（正式指示に基づく）。本監査で取得・複写・実行していない |
| 双方向共有 | 数学的分解・方針・note・報告は許可済み。証明書コードの相互複写は禁止を維持 |
| E-43 通知 | 本会話から外部への直接送付は未実施。監査報告で自己適用済み。本納品で訂正文実体を提出・保存 |
| 22″ v1.2 | 設計採用済み、commit/blob/SHA-256 の正式 pin は未提示。別工程・blocking |

## 数値を変えない条件付き接続

`20682286967199/152962947200000 + 4323211299/110234777000 + 3014712459/59751151250`
`=3887073979116207/17284813033600000 < 9/40`。
丸め差 `2008953443793/17284813033600000`。
設計予算での余裕 `3740763159/817216000000`（表示近似0.00458）。v1.2 未 pin の間、現行契約予算と扱わない。

## FREEZE の4条件

1. v3 設計 CHAT AUDIT PASS: 充足済み。
2. 成果物5点の pin と exact スクリプト CHAT AUDIT: 本納品で pin を提供。CHAT AUDIT は未了。
3. H-43-1(ii) 独立補題確認: 本納品で全文を提供。CHAT AUDIT は未了。
4. 22″ v1.2 commit・SHA-256 pin: 未了。

FREEZE は CHAT AUDIT の明示裁定のみ。Code の実行許可を本監査は代行しない。
**Contract 43 OPEN / H-43-1(ii) OPEN / D-P2 NOT_CERTIFIED。**
