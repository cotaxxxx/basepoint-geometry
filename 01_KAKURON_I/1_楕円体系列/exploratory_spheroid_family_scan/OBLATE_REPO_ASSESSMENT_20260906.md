# bg-oblate-spheroid 評価（2026-09-06）

**対象**　`github.com/cotaxxxx/bg-oblate-spheroid`
`main` @ `4c8fe17`（14 commits、9 files、台帳のみ）と
`implementation/gt-boundary-two-chart` @ `c0449a3`（151 files、producer/checker/contracts/receipts）
**方法**　全ブランチ取得、実装ブランチのテスト再実行、機械レシートの数値と**定義からの独立実装**
（`family_scan.py`：θ パラメータ・Gauss–Legendre、`oblate_independent_check.py`：μ パラメータ・tanh-sinh。
リポジトリのコード・級数・チャートは不使用）との照合。

---

## 1. 結論

扁平側の研究基盤は、Paper 1 の証明物件よりも**一段厳しい規律**（`RESEARCH_RULES.md`：証拠クラス、
producer/checker 分離、実装前固定の control、fail-closed、失敗履歴の保存）で運営されており、
中心軸係数（契約A）は **`CERTIFIED_WITHIN_SCOPE / JUDGE_PASS`** に達している。
本評価で、リポジトリの**全候補値が独立に再現**した（§2）。族論文の扁平側は、
「中心ピッチフォーク（A+B+C0）」を定理として書ける段階にあり、「極からの進入」は
端点補題と C1 組立てが閉じるまで条件付きである。

`main` は実装ブランチより2週間分古く、README の「計算源が一つ」・launcher の存在しない
SOURCE_SHA など、外部読者を誤導する状態にある（§4）。

---

## 2. 独立再現（DIAGNOSTIC_ONLY・値の照合であり包絡の証明ではない）

| 量 | リポジトリ（HIGH_PRECISION / EXACT） | 独立実装 | 一致 |
| --- | --- | --- | --- |
| `λ_axis_ob` | `0.4079588603009463642491058701855…` | `0.407958860300946364249106` | 24桁 |
| `λ_entry_ob` | `0.6435457703666799690435` | `0.6435457703666799690436` | 21桁 |
| `b_ob(1)` | `π²/32 = 0.30842513753404245684` (EXACT) | `0.30842513753404245684` | 20桁 |
| `b_ob(0.60)`, `b_ob(0.70)` | `−0.04917`, `+0.06016` | `−0.04916812`, `+0.06015631` | ✓ |
| `b_ob′(λ_entry)` | `+1.10246` | `+1.102463` | ✓ |
| `∂_t g(1⁻, λ_entry)` | `−1.45623019` | `−1.4562302` | ✓ |
| `entry_slope_ob` | `0.757064` | `0.75706644` | ✓ |
| `A′_ob = ∂_λ H_axis(λ_axis)` | `2.4911324812` | `λ²Qz′ = 2.491132481` | ✓ |
| `C_ob`（3次係数） | `−0.2613968852` | `Hz4·λ⁴/6 = −0.2613968852` | ✓ |
| `−A′/C` | `9.5300771445` | `9.530077144` | ✓ |
| `Q_perp_ob(center, λ_axis)` | `1.55240199118` | `1.552401991` | ✓ |
| `c3_ob(1)` | `−8/9` (EXACT) | `Hz4(1)/6 = −0.888888888889` | ✓ |
| 契約A 端点 `H_axis(2/5)`, `H_axis(83/200)` | 負, 正 | `−0.01973`, `+0.01761` | ✓ |
| 契約B `c3_ob` on `[2/5, 83/200]` | 負 | `−0.2519 … −0.2699` | ✓ |
| census 下端 `g_axis(63/64, 5/8)` | 「独立参考値 ≈ +4.37e−4」 | `+4.368080e−4` | ✓ |
| 軸上枝 `t*(λ)` の単調性（census） | 25点で単調・唯一 | `0.41→0.139, 0.50→0.780, 0.60→0.960, 0.70→なし` | ✓ |

正規化の対応：`p=(0,0,λt)` に対し `H_axis_ob = λ²·Qz`、`c3_ob = Hz4·λ⁴/6`（`Qz, Hz4` は
赤道半径1・絶対座標での中心係数）。両実装は座標系・求積法・特異点処理が異なるため、
これはチェッカー宣言 `CHECKER_KERNEL=TRANSCRIBED_COPY_NOT_INDEPENDENT_DERIVATION` が
留保する「**導出の独立性**」を、値のレベルで補うものである。

---

## 3. 実装ブランチの状態台帳（`analysis/*.md` の Status 行より）

| 義務 | 状態 | 独立照合 |
| --- | --- | --- |
| **A** 中心軸係数 `H_axis` の一意零点・単調性 on `[1/4,1]` | **CERTIFIED_WITHIN_SCOPE / JUDGE_PASS** | ✓ |
| **B** 3次係数 `c3_ob<0` on `[2/5,83/200]` | MACHINE_GATING_PASS / EXTERNAL_JUDGE_PENDING | ✓ |
| **C0** 定量ピッチフォーク箱 `t≤1/2` | MACHINE_GATING_PASS / EXTERNAL_JUDGE_PENDING | — |
| **C1a** 交差橋 `t=1/2` | MACHINE_PASS / C1A_CLOSED | — |
| **C1b** 軸上枝チューブ＋外側符号被覆 | サブゲート（bob）のみ PASS、**全体は未閉** | — |
| **C1c** | MACHINE_GATING_PASS / JUDGE_PASS / ASSEMBLY_PENDING_C1B | — |
| 端点符号包絡 `[5/8, 33/50]` | CERTIFIED_ENCLOSURE（**端点補題と census 同定を条件**） | ✓（`λ_entry` 内） |
| census 下端 v1（`t=63/64`） | **SUPERSEDED_INVALID**（密度に `q^{-1/2}` の余剰因子、Arb 余裕の印字で発覚） | v1包絡 `[0.041,0.205]` は真値 `4.4e−4` を含まず ✓ |
| 下スラブ `31/32` | MACHINE_GATING_PASS / NOT_AUDITED | — |
| 単調チューブ | 精密化は PASS、**境界帯 `t∈[511/512,1]` は UNRESOLVED** | — |
| 軸外排除（子午面走査） | DIAGNOSTIC_ONLY（6点、有限 q の軸外候補なし） | — |

### テスト再実行（Python 3.11、python-flint 0.9.0）

| 結果 | ファイル |
| --- | --- |
| OK（7ファイル、43テスト） | `controls/` 21件、`test_endpoint_*`、`test_gt_boundary_interval`、`test_lower_slab_and_edge_31_32`、`test_monotone_tube_refinement`、`test_c1b_resumable_driver_smoke` |
| **FAIL** | `test_census_lower_edge`：`GATING FAIL [+/- 0.0960]`（`g(63/64,·)` の全λ包絡が零を含む） |
| **FAIL** | `test_census_lower_edge_refinement`：`λ=5/8:32007/51200` で `[+/- 0.0107]` |
| **FAIL** | `test_monotone_tube_interval`：`t∈[511/512,1]` の全λ箱が UNRESOLVED（`total_rad` 2.7–43） |

3件とも環境要因ではなく、**台帳が「撤回」「未解決」と記す義務そのもの**である。
`63/64` 端は真値 `4.4e−4` で枝にほぼ接しており（`t*(0.625)≈0.98`）、箱の取り方として
証明不能に近い。`31/32` スラブが PASS している以上、63/64 系のテストは
`expectedFailure`／削除にして CI を意味のある緑に戻すべきである。

---

## 4. 修正が必要な点

1. **`main` の陳腐化。** README/STATUS は「`λ_entry` の計算源は一つ」だが実装ブランチは
   二源、さらに本評価で第三の独立源が加わった。`AUDIT_PIN.md` の CERTIFIED_ENCLOSURE も
   main には無い。`.github/workflows/c0a-term-chart-launcher.yml` が固定する
   `SOURCE_SHA 5716bcc…` は **main の履歴に存在しない**（`implementation/gt-boundary-two-chart`
   上にのみ存在）。main の README に正典ブランチを明記するか、実装ブランチを取り込む。
2. **境界帯の接続。** 単調チューブは `t≤31/32`（精密化で `511/512` まで）で止まり、
   端点補題は `t=1` の片側 `C¹` 拡張を与える。両者をつなぐ「`t∈[31/32,1]×λ箱` で
   `∂_t g<0`」の区間包絡、または極近傍の解析的単調性補題が、「枝が極から進入し中心へ
   吸収される」定理の**唯一の未接続リンク**である。`total_rad` が 2.7–43 と大きいのは
   `q→0` の端点特異性がチャートに吸収されていないためで、`μ=1−s²` 正則化を
   チューブ側にも入れる必要がある。
3. **軸外排除は診断のまま。** 族論文では Paper 1 と同じ節度で、中心近傍
   （`Q_perp>0` による軸への閉じ込め、補題6.1 の鏡像）と極近傍の局所定理に限定し、
   大域的な軸外不在は「観察」と分ける。
4. **用語の衝突。** リポジトリは中心ピッチフォークを "supercritical"（`A′>0, C<0`、
   非自明枝は `A>0` 側）と呼ぶ。私は前回「劣臨界」と書いた（非自明枝＝制限プロファイルの
   極大＝不安定）。数学は一致しており、**分岐方向の慣習と安定性の慣習の違い**である。
   論文では「非自明枝は中心が局所極小である側に存在し、枝上の点は軸方向極大（横方向正値の
   もとで3次元モース指数1）」と**符号で**述べ、super/sub は定義してから使う。
5. **`mpmath` 固定。** `requirements-prototype.txt` は `1.4.1`、Paper 1 の環境記録は `1.3.0`。
   族論文で両チェーンを引くなら環境表を統一する。

---

## 5. 族論文への示唆

- **定理の三層。** (A) 扁長・赤道停留円の局所分岐（Paper 1、認証済）。
  (B) 扁平・中心ピッチフォーク（契約 A+B+C0 — Judge 通過で認証内）。
  (C) 扁平・極からの進入と枝の中心吸収（端点補題 + C1 組立て — 条件付き）。
  (B) までで「同一汎関数・同一族に**次元の異なる二種の基点分岐**」は成立する。
  (C) は "conditional on Lemma E" と明記して別節に置くのが RESEARCH_RULES §13 に沿う。
- **球を組織中心に。** `Q(1)=Qz(1)=4/3`、`H4(1)=Hz4(1)=−16/3`、`b_ob(1)=π²/32`、
  `c3_ob(1)=−8/9`、`E_1(1)=3π²/32−1/2` は閉形式で証明でき、両チェーンの EXACT control になる。
- **非対称性を主張に。** `ln λ_axis = −0.8966`、`ln a_c = +1.5527`。軸方向の破れは 1:2.45、
  赤道方向は 1:4.72 まで起きない。
- **証拠の等級を統一。** Paper 1 は「12物件・SHA・再実行」、扁平側は「契約・レシート・Judge」。
  族論文の Data availability では両者の証拠クラスを同じ語彙（`RESEARCH_RULES` §1–2）で並べる。

---

*本ファイルおよび `family_scan.py`、`oblate_independent_check.py` は DIAGNOSTIC_ONLY / NOT_BINDING。*
*bg-oblate-spheroid への push 権限はないため、basepoint-geometry の査読ブランチに記録する。*
