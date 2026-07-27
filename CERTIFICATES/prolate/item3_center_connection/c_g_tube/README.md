# item3_center_connection/c_g_tube — Actions clean-room pilot（ソースのみ）

役割: 単一 λ スライス（λ=118/25, r∈[1/64,11/256]）の一意根 pilot。
項目3全体の証明書ではない。二領域型 C-G-TUBE の外側領域のみ。

このディレクトリはソース・設定・対照・checker・workflow のみを含む。
計算結果（JSON/JSONL/certificate/checkpoint/manifest 実体）は一切
同梱しない。全成果物は Actions 内で endpoint → 56 Taylor cells →
identity spots [0,18,37,55] → controls → checker/finalize → manifest
の順にゼロから再生成される。

状態遷移: UNVERIFIED_DELIVERY →（SHA照合）VERIFIED_DELIVERY →
（PR登録）SOURCE_CANDIDATE →（Actions全再生成 PASS）CERTIFIED。

依存: vendor 核2本（config.json にファイル別パスと SHA をピン留め。
F 核は CERTIFICATES/prolate/item2_circle/vendor/、
Frr 核は CERTIFICATES/prolate/item3_center_connection/vendor/。
不一致・欠落は exit 2）。
較正の根拠は PR #15 の schema-v2 較正記録（セル幅 1/2048）を参照。
