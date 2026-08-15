# BLOCAL_V22_METHOD_SELECTION_ADDENDUM_V1 — §7 method-selection addendum（chat 起草・未 commit）

STATUS: DRAFT。本文書は READINESS_RESET_CORRECTION（SHA-256 88f96b21…）§7 が要求する
method-selection addendum である。**commit され chat の byte/内容監査が GREEN になるまで
native 実装は解禁されない。** 本文書自体は証明証拠ではない（certificate_evidence=false）。

## §0 位置づけと非主張

- 本文書は「どの評価方式を native 実装の対象として選ぶか」を確定するものであって、
  B-LOCAL の数学的結論を主張しない。
- 引用するすべての診断値は **diagnostic prototype による feasibility 実測**であり、
  certificate ではない。判定語 CERTIFIED_* は本文書では使用しない。
- 本文書の GREEN は native 実装の**着手**を解禁するだけで、production 実行・tag・
  昇格のいずれも認可しない。

## §1 選定する方式

**Taylor2 charted evaluator**（2次 Taylor＋remainder、4チャート C1／TH／R2 と Duffy 三角
T1／T2 の分割）を native 実装の対象として選定する。design reset で撤回された
natural Arb interval＋adaptive ball-sum には戻さない。

選定の根拠は §6 の実測であり、「enclosure が狭くなった」ことではなく
**§6.2 の6条件すべての成立**である。

## §2 effective floor（normative・適用先は列挙で固定）

一般則：**eff = max(構造 floor, 引数の自然下界)**。両者とも真値の妥当な下界なので
max も妥当な下界である。交差・事後 hull・標本推定のいずれでもない。

適用先は以下の**6箇所に限定**し、第7の site を暗黙に追加してはならない。

**通常 chart（geometry jet 経路）**
1. q の逆冪 → **q_eff**
2. w2 の逆冪 → **w2_eff**（旧実装は floor=1 が hardcode）
3. 1−c² の平方根 → **S2_eff**

**Duffy 経路**
4. w2 の平方根 → **w2_eff**（旧実装 floor=1）
5. 1+y² の平方根 → **g2_eff**（旧実装 floor=1）
6. 1−c² の平方根 → **S2_eff**（旧実装は floor なし＝S∈[0,1] を返していた）

共通規則：
- 自然下端が有限かつ正のときのみ effective floor を使用。非正・nonfinite・取得不能なら
  既存の構造 floor 版／nonnegative 版へ **fallback**。
- center と box は**それぞれの評価領域**の自然下端を使う（相互流用禁止）。
- 値因子と導関数因子は**同一の effective floor を共有**する。
- structural／natural／effective の3値、選択元、fallback 理由を record 化。

C1 の構造 floor（C1_STRUCTURAL_FLOOR_SPEC_V1、SHA-256 8492755d…）は
**q_eff の構造オペランドとして保持**し、弱体化させない。

## §3 Duffy 経路の局所再構成（normative）

`_geometry` 系のヘルパは内部で floor なしの S を再生成するため、§2-6 の差し替えだけでは
不十分である。**Duffy では S・U・W・B・q を局所で一貫して再構成**し、同一の S2_eff を
全下流因子へ伝播させる。新旧の geometry を混用した record は無効とする。

γ の [0,1] clamp は **fail-closed 安全装置として維持**する（自然 γ は代表セルで
[0,1] に収まらないことを実測で確認済み）。corner 退化と非 corner fallback は
別フィールドで記録する。

**Duffy の Z_lo**（q_lo = ρ²_lo·Z_lo の Z 側）は Ŵ² 項を含める：

```
Z_lo  = Â_lo + r_lo²·B̂_lo + u0²/ρ²_hi
ρ²_hi = ε²·a1²·(1+b1²)        （exact 有理）
```

根拠は Ŵ = W/ρ、W ≥ 1−r_hi = u0。ρ²_lo は exact で緩みがないため現行のまま。
ρ² と Z の最小点は一致しないが損失は 4倍以内で、旧 Z_DEN_LO の緩み（最大 802倍）に
対して per-cell 因子積で十分。**一体型 Duffy q_lo は採用しない。**

## §4 γ 適応 bin（normative）

γ は有限性が回復するまで決定論的に中点二分し、得られた区間の union を用いる。
cut と最終 bin 数、max bin depth、use count を record 化する。cut 1/2 固定の
最大2 bin 実装へは戻さない。

## §5 J_START（条件5・6）の評価規約（normative）

**5.1 条件5（derivative bracket）** — Newton bracket 全体 u∈[0,u_max] を一度だけ評価し、
F_r = −H_u を**端点反転**（[H_lo,H_hi] → [−H_hi,−H_lo]、label 変更ではない）で得る。
sup(F_r)<0 かつ 0∉F_r を要求し、H_u と F_r の双方、および端点反転規則を record 化。

**5.2 座標写像** — 部分 bracket [left,right] に対する derivative は
**u = [1−right, 1−left]** の exact 有理写像で取る。r↔u の対応を record に明示。

**5.3 derivative 下界ラダー** — 各 step で下界目標 θ を降順ラダー
`[6/5, 1, 1/2, 1/4, 1/10]` で試し、**per-target の評価上限**内で到達した最初の θ を採用。
全滅時のみ sign-only（lo>0）へ fallback。到達 θ・各 target の REACHED/NOT_REACHED・
評価数・失敗理由を record 化。判定は常に 0∉F_r を課し、θ 到達時のみ sup(F_r) ≤ −θ を追加する。

**5.4 quotient** — F(m)/F_r(X) は**負分母の向きを保った区間除算**で計算する。
midpoint-only 除算は禁止。分子・分母の端点と reciprocal endpoint rule
（[1/F_r_hi, 1/F_r_lo]）を record 化。

**5.5 containment-first** — 各 step の F 点評価は
**「strict sign が確定」または「現在の F_r による Newton image が strict self-containment」**
のいずれかで停止してよい。containment が先に成立した場合、**F(m) の符号確定は要求しない**。
containment しなかった場合にのみ strict sign を要求して bisection を継続する。
符号未確定のまま終わった midpoint は ordered_bisection に含めない。
各 step に strict_sign_certified / sign_required_for_continuation / F_stop_reason を記録。

**5.6 self-containment の判定** — `left < N_lo ≤ N_hi < right` の strict 判定とし、
左右の margin を exact 有理数で記録する。

**5.7 評価数の帰属** — F 点評価のみが J_START の outer evaluation 予算（96）に算入される。
derivative 評価は別カウンタ（derivative_evaluations）として記録し、outer 予算には算入しない。
この帰属を record に明記する。

## §6 選定根拠（診断実測・certificate ではない）

**6.1 provenance** — v5 診断 prototype（SHA-256 7b4f9b39…）／v5 spec（42a9b798…）／
config provenance addendum（fd715ae1…）／C1 floor spec（8492755d…）／
committed config（fec14e99…、hash 入力としてのみ使用）／
materialized ephemeral config（9ef29f99…、21 shard と条件5・6 で同一）。
診断は **probe depth 16** の override 下、ephemeral diagnostic contract の budget で実行した。

**6.2 候補 pair** — λ ラダー（21候補・canonical order 2^-24…2^-4）を1候補1 shard で全列挙し、
**index 15（s = 2^-9）が最初の ACCEPTED**（budget_faithful=true、wall 切れ 0、
index 0–14 はすべて MAX_EVALUATIONS による INDETERMINATE）。
u_max は canonical schedule の第一候補 2^-8。
**選定 pair = (λ_start, u_max) = (λ_plus + 2^-9, 2^-8)。**

**6.3 六条件の実測**

| 条件 | 結果 | 主要数値 |
|---|---|---|
| 1 J_START initial F > 0 | PASS | lo = +6.022102e-06、2,091 evals |
| 2 L2 first face F > 0 | PASS | 同上 |
| 3 L3 r=1 F < 0 | PASS | hi < 0、10,173 evals（index 15） |
| 4 L1 tile H_u > 0 | PASS | lo = +3.554156e-03、449 evals |
| 5 derivative bracket | PASS | F_r ⊂ [−3.0074005, −2.387987305e-03]、815 evals |
| 6 complete J_START path | PASS | 4 steps、f_point 5（≤96）、bisections 4（≤40） |

条件6 の step 別：θ 到達は 1/4 → 1/2 → 1 → 6/5、quotient 幅は
2.0219e-02 → 4.2086e-03 → 6.2786e-04 → 3.9333e-04、
**step 3 で NEWTON_CONTAINMENT により符号確定なしで成立**
（inf|F_r| = 1.200094639、margins 左 +6.902118e-09／右 +9.494844e-05）。

## §7 既知の脆弱性（native 実装が扱うべき事項）

**7.1 step 3 の margin が薄い** — 左 margin +6.902118e-09 は bracket 幅 4.883e-04 の
約 1.4e-05 倍にすぎない。exact 有理数で strictly positive なので判定は有効だが、
θ・budget・floor の僅かな変更で反転しうる。native 実装は
**margin 下限方針**（θ をもう一段上げる、または bisection を1 step 追加する）を持ち、
採用した方針と得られた margin を record 化すること。

**7.2 derivative ラダーのコスト** — 到達しない θ の試行が評価数の大半を占める
（診断では derivative 合計 23,731、うち到達分は約 4,900）。native 実装は
前 step の到達 θ を初期値にするなどの探索順最適化を行ってよいが、
**採用 θ の妥当性（sup(F_r) ≤ −θ）は毎回検証**すること。

**7.3 committed config と現行 model の schema 不整合（native 実装の前提条件）** —
committed config（fec14e99…）は budgets キーが L1_BOUNDARY／L1_INTERIOR を持ち、
現行 model の exact-key 要求（L1／L2／L3／J_START）を満たさないため
`validate_config` を通らない。診断はすべて ephemeral materialization で実行した。
**native production へ進む前に、committed config の更新（別承認）か、
config schema の対応関係の明文化のいずれかで解消すること。**
未解消のまま production を走らせてはならない。

## §8 native 実装への要件

1. §2 の6 call site、§3、§4、§5 を実装する。列挙外の site を暗黙に追加しない。
2. record は診断で確立した項目を維持する（floor の3値と選択元、γ の cut/bin 数、
   Duffy の corner/非 corner 別 fallback、J_START の step 別 trace、評価数の帰属）。
3. registry 等の大量記録は有界表現（unique 数・総 use count・canonical SHA-256・
   上位固定件数・truncation flag・per-site 内訳）とする。
4. 負対照を実装する（標本由来 bound の使用、floor 不一致、未列挙 site の追加、
   旧 geometry の混用、γ clamp の除去、θ 未検証での採用、outer 予算への
   derivative 算入、run 中／run 後の budget 変更）。
5. budget は committed contract に従い、probe の診断値を持ち込まない。
   CI の wall timeout は数学的 budget と別フィールドに記録する。
6. 判定は fail-closed。INDETERMINATE と REJECTED を混同しない。
7. 実装完了 → 最終バイトから全 source SHA 再計算 → config を最後に materialize →
   単一 commit → STOP → chat byte/code/math 再監査。

## §9 非主張（明示）

- 本文書は λ_start = λ_plus + 2^-9 を **B-LOCAL の結論として主張しない**。
  これは診断上の候補選定であり、native 実装と production 実行を経て初めて
  正式な lambda_start となる。
- 六条件の PASS は方式の feasibility を示すのみで、B-LOCAL の主張（一意根の存在、
  boundary entry への接続）を含まない。
- calibration・B-TUBE への binding、tag 作成、sweep、CERTIFIED_* の宣言はいずれも
  本文書の射程外である。

## §10 sequencing

1. 本 addendum を commit → STOP → chat byte/内容監査
2. GREEN 後に native 実装へ着手（§8）
3. 実装完了 → STOP → chat 再監査
4. readiness（ε=2^-8 の production-shaped）→ STOP → chat 監査
5. 最終バイト freeze → config materialize → 単一 commit → STOP → chat 監査
6. production 実行・tag は別途ユーザー承認

各段で STOP を守り、自動進行しない。
