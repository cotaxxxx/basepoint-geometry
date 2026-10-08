# Contract 43 — E-43-1 / E-43-2 訂正通知

宛先：Astra・Code（同文）
日付：2026-10-09（Asia/Tokyo）
送付状態：**未送付**。この会話から既存の送付先を特定できず、直接送信・受領を確認できていない。

訂正 E-43-1：独立監査依頼書 §3 と前回 Code 宛許可文の対象領域は誤り。
正しくは Contract 24 baseline band `|mu-m|<=rho`（`s in [-rho,rho]`、cap 側を含む）、`|xi|<=rho`。
`s in [rho,max(rho,1/10)]` は Contract 45 Piece 1 で被覆済みの far band であり、今回の監査対象外。
物理領域 `-1<=mu<=1` との共通部分を取ると、実際の区間は `mu in [m-rho,1]`、`s in [m-1,rho]`。

帯の内部に対角特異点 `xi=±rho, mu=m, phi=0 or pi`（符号の対応する一致点）を含む。
Q1 の前に「N3 の ξ 平均表式が near band で可積分な形で成立するか」を Q0 として追加する。
Code は predeclare の対象領域も同じ定義に訂正すること。

訂正 E-43-2：`blob 63bfc769...` は `SHA-256 63bfc769...` に訂正。
完全識別子は次の通り。

- commit：`2b53e1375163fef1fca56af1bd83905948673f72`
- SHA-256：`63bfc769c3db49d8d728d099e5efefec3e509fd4796f7926133c4ec7628508c2`
- Git blob：`3c22bfca6ee715f3135934f819e23775d533021d`

逸脱記録：「Contract 43 領域を far Piece 1 区間と誤記（2026-10-09）、E-43-1 で訂正」。
研究状態：D-P2 NOT_CERTIFIED。訂正は数学的成立や正式 freeze を宣言するものではない。
