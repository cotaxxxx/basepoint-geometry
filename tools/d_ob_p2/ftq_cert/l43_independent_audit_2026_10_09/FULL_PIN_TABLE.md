# Contract 43 — 完全 pin 表（第一・第二提出）

Repository: `cotaxxxx/basepoint-geometry`  
Branch: `codex/l43-independent-audit-20261009`  
証拠 commit: `ff1e1a5351e2c8ed4bd816e168a08f5b17310e88`  
Parent: `0c1189f9af5eb221abfc518b110e11dda345b4b0`  
共通 path prefix: `tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/`

以下の全ファイルは同じ証拠 commit の実体であり、GitHub から再取得して blob と全文の一致を確認した。
表のファイル名を共通 prefix に連結したものが正確な repository path。`delivery_pins.json` には各行ごとに
repository / branch / full path / full commit / blob / SHA-256 / 行数 / 更新状態 / 実行 / 依存関係を展開して記録した。
この pin 表を固定する次の commit は表だけの追記であり、証拠 commit のファイルを書き換えない。

## 第一提出：要求5点

| ファイル | Git blob SHA | SHA-256 | 行数 | 更新・実行状態 |
|---|---|---|---:|---|
| [l43_graph_majorant_exact.py](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/l43_graph_majorant_exact.py) | `5ab1f7d2ca4343f43c9e520253ec9d904e791397` | `6187c2b0c22d3e1b75ede72da3f470185eb6d93722b25265974ce2e01488cf18` | 216 | 不変。既存46検査 PASS / exit 0。今回再実行なし |
| [exact_checks.stdout.txt](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/exact_checks.stdout.txt) | `2dcfc808918f5310b051b6cc8afd8adff334ec4e` | `8790c7912043b4c68f5a75fb2b51aa8895b41407d299e1b1db2d964556f9d2d8` | 47 | 不変。固定コードの未編集生ログ |
| [source_manifest.json](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/source_manifest.json) | `279332bc6801702004395109d0f70d8d7b18bce7` | `bb4caa9a0795b4f40242aa136f6f9fd5f746a848b70185b3283948f7b812b58d` | 370 | 更新。原典・成果物・未完了義務を追記 |
| [D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md) | `3f95ef5b82980affcc1e453393308acd099544ad` | `9fc500bd486d325451ae049806673bdef400987c06f07cc16a4c174130e1b615` | 660 | 更新。§3.1 と最終余裕などを追補。主上界は不変 |
| [E43_CORRECTION_NOTICE_2026_10_09.md](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/E43_CORRECTION_NOTICE_2026_10_09.md) | `75068f4ba0a903ba811138592a78f1f182389dd6` | `eadeda81783078826f51e7dd9baf8499997ed57c573e2aad4cfd23c2bbffd2d6` | 27 | 更新。自己適用・保存・直接未送付を区別 |

## 第二提出：H-43-1(ii) 独立補題

- File: [H43_ENDPOINT_LEMMA.md](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/H43_ENDPOINT_LEMMA.md)
- Full path: `tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/H43_ENDPOINT_LEMMA.md`
- Full commit: `ff1e1a5351e2c8ed4bd816e168a08f5b17310e88`
- Git blob: `303d1d7c6aa1640590eb83434888c8c19ab44c3a`
- SHA-256: `b1a906edeb21cef356d3d7810dbdc11d30773364620b174a425c441b826d6276`
- 行数: 198。新規、紙上証明。主報告 §3.1 と同文。
- 依存: P1 design note の既存定義・角関数評価、および独立に示した射影・局所可積分評価。
- **H-43-1(ii) OPEN / CHAT AUDIT 確認待ち。** Code 証明書は使用・複写・実行していない。

## 補助成果物

| ファイル | Git blob SHA | SHA-256 | 行数 |
|---|---|---|---:|
| [exact_checks.json](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/exact_checks.json) | `5dd85c2c2041fb065ad5554cc66d6aed59477120` | `2c3a1e4230ed98bf82df8dab800b4835894daa27ba538706362506b8966c546a` | 288 |
| [exact_checks.stderr.txt](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/exact_checks.stderr.txt) | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| [reproduction_manifest.json](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/reproduction_manifest.json) | `e126fda7aae6e1674e106b107d8acaa9ffdc6479` | `05ccc26e54868a964a94b13f3ffa665971ac5cf86507e097926d6ec353fbd316` | 12 |
| [EXECUTION_PROVENANCE.json](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/EXECUTION_PROVENANCE.json) | `6a13cf4d745a51d110b37d138aef559a90864379` | `27764700d3353197f222844c94e3664d082a1b824107a9d67e86f3fc601b620e` | 56 |
| [EXACT_CHECK_MAP.md](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/EXACT_CHECK_MAP.md) | `a3215e0cdf19ed925b3c4fd7024b34bf1282ff1f` | `cdbe0097a9b583b70a086ee89283f66f6a4c9f2dbf5b6edbc4870493118dcc0d` | 94 |
| [HANDOFF_NOTES.md](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/HANDOFF_NOTES.md) | `22601a5c3e587e172b65c0c9c6e66a868e02b20f` | `ebe36df980edd6435de370e222b4d2537507a89ca92f45431578105ca15d18a4` | 56 |
| [SHA256SUMS](https://github.com/cotaxxxx/basepoint-geometry/blob/ff1e1a5351e2c8ed4bd816e168a08f5b17310e88/tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/SHA256SUMS) | `76f5a724f1d65f7ed854abe856fdeedc104dd7f6` | `500bb3ba0f56428f63fb05e5f22fbf698cbdb03cd066c841691adfc514af6f89` | 12 |

## 索引の固定

`delivery_pins.json` の SHA-256: `c0059a562e3215a9ddcf4b476ffde2831401ef3497c95a538fd599d2c52774a0`、Git blob: `c918fbcbec54d78c4aa9ee148ea6a87f3565649d`、261行。
この表自身の hash は自己参照を避け、納品メッセージで示す。
`SHA256SUMS` は証拠 commit の13ファイルのうち自分自身を除く12ファイルを検査する。
後置の索引2点は `SHA256SUMS` に含めない。索引の追加は証拠の内容を変更しない。

## 状態と残存義務

Predeclare v3 設計 PASS / v3.1 pin 更新監査 PASS（正式指示による）。
本納品で実体と完全 pin を提出した。exact スクリプトの CHAT AUDIT と H-43-1(ii) の判定は未了。
22″ v1.2 commit・blob・SHA-256 は別工程の PENDING。現行 v1.1 予算を設計予算で置換しない。
Code 証明書の実行禁止を維持する。FREEZE は CHAT AUDIT の明示裁定のみ。
**Contract 43 OPEN / D-P2 NOT_CERTIFIED。**
