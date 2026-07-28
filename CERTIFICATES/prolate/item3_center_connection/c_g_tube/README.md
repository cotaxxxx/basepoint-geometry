# item3_center_connection/c_g_tube — Actions clean-room hybrid pilot（ソースのみ）

役割: 単一 λ スライス（λ=118/25, r∈[1/64,11/256]）の一意根 pilot。
項目3全体の証明書ではない。左端8セルを中心恒等式、残り48セルを
Taylor 包含で処理する二領域 hybrid C-G-TUBE である。

このディレクトリはソース・設定・対照・checker・workflow のみを含む。
計算結果（JSON/JSONL/certificate/checkpoint/manifest 実体）は同梱しない。
全成果物は Actions 内で endpoint → 56 hybrid cells
（8 center-identity + 48 outer-Taylor）→ spot crosschecks
[0: refined identity pieces, 18: adaptive Taylor, 37/55: Taylor]
→ controls → checker/finalize → manifest の順にゼロから再生成される。

checker の trust boundary は原始 Arb 評価ボールである。Taylor 不等式、
中心恒等式の区間 Riemann 和、被覆、鎖 SHA、型・phase・件数、spot 交差は
保存された原始ボールから独立再構成する。Taylor 記録は G_prime_m と
C_bound を先に文字列化し、checker と同じ再読込値から再構成した後、
往復検証済みの外向き serialization guard を付けて保存する。この経路は
cells と spot Taylor の双方で共通である。spot 0 の base identity は
cells 鎖の同一セル再構成値に結合し、refined identity は256分割の
Frr_ball ピースから再構成する。identity_pieces 内の weighted_ball は
診断表示専用であり、checker は t_a, t_b, Frr_ball から再計算する。
`neg_reconstructed_ball_shrink` は cell Taylor と spot Taylor を別々に
内向き縮小し、双方を checker が exit 1 で拒否することを確認する。

状態遷移: UNVERIFIED_DELIVERY →（SHA照合）VERIFIED_DELIVERY →
SOURCE_CANDIDATE →（独立静的監査 PASS）AUDITED_SOURCE →
（固定SHAの Actions全再生成 PASS と成果物照合）CERTIFIED_SINGLE_SLICE。

依存: vendor 核2本を config.json にファイル別パスと SHA でピン留めする。
F 核は CERTIFICATES/prolate/item2_circle/vendor/、Frr 核は
CERTIFICATES/prolate/item3_center_connection/vendor/。不一致・欠落は exit 2。
較正の根拠は PR #15 の schema-v2 較正記録（セル幅 1/2048）を参照する。
