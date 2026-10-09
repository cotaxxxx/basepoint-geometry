# Exact スクリプト — 検査対応表と証拠範囲

固定版 `l43_graph_majorant_exact.py`：SHA-256 `6187c2b0c22d3e1b75ede72da3f470185eb6d93722b25265974ce2e01488cf18`。
初回 pin：commit `0c1189f9af5eb221abfc518b110e11dda345b4b0`、Git blob `5ab1f7d2ca4343f43c9e520253ec9d904e791397`。
今回コードは変更・再実行していない。Code の独立証明書も実行していない。

## 実行の原記録

- host: `daybreak-works`; Python **3.11.16**; SymPy **1.14.0**; `-I`。
- 最終固定版の PID: `910823`。start tool の時刻文字列: `10/09/2026, 07:41:34`。
- 完了観測の時刻文字列: `10/09/2026, 07:42:10`; **exit 0 / runtime 0.65 s**。
- 元ツールの時刻文字列にオフセットは付いていないためそのまま保存した。JSON 出力の独立した file metadata は `modified=2026-10-08T22:41:34.464Z`。
- 生 stdout: **46 PASS / 0 FAIL**、総47行（末尾総括1行）。stderr: 0 bytes。
- 実行時のコマンド・終了観測の元記録は `EXECUTION_PROVENANCE.json`。stdout を編集・要約して置き換えていない。

```sh
/home/daybreak/basepoint-geometry-artifacts/ftq-c7743c7-independent-20261009-01/venv311/bin/python -I /home/daybreak/basepoint-geometry-artifacts/l43-independent-20261009-01/l43_graph_majorant_exact.py --json /home/daybreak/basepoint-geometry-artifacts/l43-independent-20261009-01/exact_checks.json > /home/daybreak/basepoint-geometry-artifacts/l43-independent-20261009-01/exact_checks.stdout.txt 2> /home/daybreak/basepoint-geometry-artifacts/l43-independent-20261009-01/exact_checks.stderr.txt
```

再現コマンド（実行先は新しい隔離ディレクトリを使う）：

```sh
python3 -I l43_graph_majorant_exact.py --json exact_checks.json
```

## 厳密演算の方式

Python 標準 `fractions.Fraction`、SymPy の `Rational`、多項式の `expand`/`cancel` による記号ゼロ検査、
有理 Bernstein 係数変換、厳密微分・原始関数・極限を用いる。float の閾値判定、数値求積、格子実験は用いない。
外部ライブラリは SymPy 1.14.0。`sp.limit` などの記号アルゴリズムを信頼する計算機支援検算であり proof assistant ではない。
失敗すれば `AssertionError` で終了し、通常の Python 実行で非零 exit になる。Python の `-O` は指定しない。

## 46検査と報告の対応

| ID | 報告箇所 | 検査内容 | 固定出力 |
|---|---|---|---|
| I01 | §1、§2 | 球面制約の多項式消去 | PASS |
| I02 | §2、(5.5) | N/λ=bD²−(h/λ)(b−ξ) | PASS |
| I03 | §2、(5.5) | 2h/λ=D²+(1−L)s²+δ | PASS |
| I04 | §2、(2.1) | 法線ベクトルの単位長 | PASS |
| I05 | §2、(2.1) | n·e=h/(wD) | PASS |
| I06 | (2.2) | Gram 恒等式を分母消去して検算 | PASS |
| I07 | (2.4) の直前 | w²−A⊥²=L[ρ²+(1−L)s²] | PASS |
| I08 | (2.4) | 正部分内部の多項式恒等式 | PASS |
| I09 | (5.5) | 曲率・深さの恒等式 | PASS |
| I10 | §3、(3.4)–(3.5) | (b,ξ) 同時反射時の N の奇性 | PASS |
| I11 | (5.3) | Young 1/4 の平方差表示 | PASS |
| I12 | (5.4) | Young 1/3 の平方差表示 | PASS |
| C01 | §1 | m₀²+ρ₀²=1 | PASS |
| C02 | (3.3) | μ₀=97/113>0 | PASS |
| C03 | (0.1) | cap の包含に用いる有理端点比較。包含自体は紙の証明 | PASS |
| C04 | (5.2)、§8 | graph gradient の全 Bernstein 係数 | PASS |
| C05 | (5.4)、§8 | Lk²<1/12 の全 Bernstein 係数 | PASS |
| C06 | (5.3)、§8 | 深さ誤差の全 Bernstein 係数 | PASS |
| C07 | (5.3) | 曲率係数189/500 | PASS |
| C08 | (5.5)–(5.7) | c_g=51/50 | PASS |
| C09 | §7 | R_e<13/20 の平方比較 | PASS |
| C10 | (6.1)、§7 | W(93/200)>89/100 の平方比較 | PASS |
| C11 | §7 | (4/3)^(3/2)<77/50 | PASS |
| C12 | §7 | (4/3)^(5/2)<103/50 | PASS |
| I13 | (6.1) | λ/W の微分式 | PASS |
| I14 | (6.1) | λ²/W の微分式 | PASS |
| A01 | (6.3) | 交差項の原始関数の微分 | PASS |
| A02 | (6.4) | 深さ項の原始関数の微分 | PASS |
| A03 | (6.4) | 深さ項の0から∞までの厳密積分 | PASS |
| A04 | (6.2)、(6.4) | 半平面の角積分 | PASS |
| A05 | (6.2)–(6.4) | ξ²、|ξ|、δ の ξ 平均 | PASS |
| A06 | (6.3)、§7 | 対数の比較関数の微分 | PASS |
| A07 | §7 | ρ³log(1+c/ρ²) の微分式 | PASS |
| C13 | §7 | exp Taylor 有理下和と対数引数の比較 | PASS |
| A08 | §7 | π<22/7 の正積分の値 | PASS |
| B01 | §7 | 三成分の合計の完全一致 | PASS |
| B02 | §7 | 9/40との差、正の有理数 | PASS |
| B03 | (7.1) | 設計予算との差。現行契約予算の認証ではない | PASS |
| B04 | §7 | 設計下界−far上界の算術 | PASS |
| B05 | §7 | 条件付き最終余裕の完全一致 | PASS |
| M01 | §9.3 | cap 同時極限 N/D²→−1/2 | PASS |
| M02 | §9.3 | cap 分子のρ⁸尺度での極限 | PASS |
| M03 | §9.3 | cap 核のρ²尺度での極限 | PASS |
| M04 | §9.4 | 外側尺度での D²/ρ の極限 | PASS |
| M05 | §9.4 | 外側尺度での分子/ρ³ の極限 | PASS |
| M06 | (9.2) | 正部分の方位角積分 | PASS |

## 紙上証明に依存する工程・単体では認証しない事項

射影の Cauchy–Schwarz、正部分の片側評価、凸円板上の Lipschitz 評価、非負核だけへの領域拡大、
面積要素 `db dy/μ`、Fubini・FTC・支配収束・一様可積分性、微分式からの単調性の推論、
全パラメータ被覆、端点と同時極限における一様性は紙上証明を監査する。
I10 は反射による全積分の正規化全体を認証する検査ではない。C03 は cap 包含の論証全体をコード化していない。
M04–M05 の点ごとの記号極限だけで (9.2) の積分極限を認証しない。三成分値は JSON の constants に記録し、B01 はその和を検査する。

新規 H-43-1(ii)-E、Lemma V との端点同定、原典の採択、far・south の証明、22″ v1.2 の採択・pin、
FREEZE、Code 証明書の実行許可、c_FT、D-P2 認証はこのスクリプトの認証対象ではない。
検算と CHAT AUDIT の countersign を区別する。
