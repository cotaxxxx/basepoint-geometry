# C1_STRUCTURAL_FLOOR_SPEC_V1 — Taylor2 prototype v4 用 C1 専用下界仕様

STATUS: DIAGNOSTIC PROTOTYPE SPEC — §6 method-selection 診断専用。
certificate_evidence=false。production／native 9 source／committed config／tag には一切適用しない。
本仕様は chat 診断(2026-08-12、head 5fafb162 上の非本番計測)で改善率を確認した2部品のみを正典化する。

## §1 記法と exact 量(C1 チャート)

セル＝[a0,a1]×[b0,b1] ⊂ [0,1]²(exact dyadic)。
c = ε + (1/2−ε)·a、φ = π·b、S = √(1−c²)、U = S·cosφ、W = 1−rU、
A = (λ²−1)c²、B = 1−U² = sin²φ + c²·cos²φ(設計 reset §1 で検証済み恒等式)、
q = W² + A + r²B。

exact 有理数(すべて分数演算のみ):
- c0 = ε + (1/2−ε)·a0、c1 = ε + (1/2−ε)·a1(c_hi ≡ c1)
- λ_lo = λ_plus + s0(s-区間下端)
- π_lo = 333/106、π_hi = 355/113(validated helper lemma)
- φ の外側 bracket: φ_LO = π_lo·b0(真の φ_lo=π·b0 の下界)、φ_HI = π_hi·b1
- 三角関数の certified 有理 bound は、指定引数(exact 有理 or 有理端点 ball)を
  Arb で評価し canonical dyadic 端点を外向きに取ったもののみを許す。

## §2 q 下界の3成分(add-only)

q_floor_C1 = A_lo + [W2_lo] + [RB_lo](各成分は §4 の規則で非負化してから加算)

1. **A_lo = (λ_lo²−1)·c0²** — v3 と同一(変更なし)。
2. **W2_lo = (W_lo)² if W_lo > 0 else 0** — W_lo は §3 の U_max 規則から。
3. **RB_lo = r_sq_lo · B_lo** — B_lo は §3 の恒等式形から。1−U_max² 型の導出は禁止
   (U_min が必要になり緩い。B_lo は必ず sin²φ + c²cos²φ 形から作る)。

## §3 端点規則

**U_max(W_lo 専用。U_min は本 floor では消費しない)**
- cmax = min( cos_hi_Arb( ball[π_lo·b0, π_hi·b0] ), 1 )。cos は [0,π] で減少ゆえ
  cosφ ≤ cos(φ_lo_true) ≤ cmax。
- S の cell 内範囲は [S_lo, 1]、S_lo = max(1−c1², 0)(√x ≥ x on [0,1] の exact 代数)。
- 符号別: **cmax ≥ 0 → U_max = cmax**(S≤1)。**cmax < 0 → U_max = S_lo·cmax**
  (負の値に S_lo を掛けることで最大＝絶対値最小側を取る)。

**W_lo(exact-r と interval-r の統一規則)**
r ∈ [r_lo, r_hi](exact-r 点評価は r_lo = r_hi = r_exact の特別な場合):
- **U_max ≥ 0 → W_lo = 1 − r_hi·U_max**
- **U_max < 0 → W_lo = 1 − r_lo·U_max**(r_lo 規則。r_hi を使うと過大＝
  chat 標本試験で 4/262 violation を実測した誤り。禁止)

**B_lo**
- sin 成分: s_left = lower(sin_Arb(ball[π_lo·b0, π_hi·b0]))、
  s_right = lower(sin_Arb(ball[π_lo·b1, π_hi·b1]))、
  sin_min = max( min(s_left, s_right), 0 )。(sin は [0,π] で凹＝最小は端点。
  端点自身の π 不確定は ball 評価が吸収する)
- cos² 成分(π/2 跨ぎは b で exact 判定: φ=π/2 ⟺ b=1/2):
  - **b0 < 1/2 < b1 → cos2_min = 0**(跨ぎ)
  - b1 ≤ 1/2 → m = max( lower(cos_Arb(ball[π_lo·b1, π_hi·b1])), 0 )、cos2_min = m²
  - b0 ≥ 1/2 → m = max( −upper(cos_Arb(ball[π_lo·b0, π_hi·b0])), 0 )、cos2_min = m²
- **B_lo = sin_min² + c0²·cos2_min**(≥0)
- **r_sq_lo = r_lo²**(exact-r 点評価では r_exact²)

## §4 結合・非負化・fallback

- 各成分は個別に 0 で clamp してから加算(負値の混入禁止)。
- W2_lo または RB_lo の計算中に Arb 評価が nonfinite になった場合、
  **その成分のみ 0 とし record に component_dropped を記す**(A_lo へは影響させない)。
- A_lo ≤ 0 は config/座標の異常 → **hard fail(INDETERMINATE、fail-closed)**。
- 最終 q_floor_C1 > 0 を必須検査。加算後に上限側と比較する類の「再 hull」は行わない
  (設計 reset R-6 の禁止事項に従う)。

## §5 per-cell S floor(jsqrt 用)

C1 の geometry jet における S = jsqrt(1−c², S2_floor) の floor を
**S2_floor = max(3/4, 1−c1²)** に置換する(c1 = ε+(1/2−ε)·a1、exact 有理)。
妥当性は exact 代数のみ(c ≤ c1 → 1−c² ≥ 1−c1²。c1 ≤ 1/2 → 1−c1² ≥ 3/4)。
標本検証は不要級だが、§7 の record には S2_floor 値を残す。

## §6 適用範囲・不変条件・予算

- 適用は **C1 チャートのみ**。TH／R2／T1／T2 の floor と評価形は v3 から不変。
- γ 適応 bin(v2/v3 で監査済み)・record の intern／上限化(v3)・workflow の
  gzip artifact／summary step(v3)は不変。
- **予算は不変で事前固定**: cell evaluations 24,000／max depth 14／active 16,000／
  wall 900s、J_START 40 bisections／96 evaluations。事後増額禁止。
- native 9 source・committed config(fec14e99…)・production・tag は無変更。

## §7 record 追加項目(§6.5 に加算)

セル毎: q_floor_source("C1_A_W2_B" または component_dropped 内訳)、
A_lo／W2_lo／RB_lo の exact 有理値、U_max と採用した r 端点(r_lo/r_hi/r_exact)、
π/2 跨ぎ判定(b0,b1 と結果)、S2_floor 値。
counters／elapsed は v3 契約どおり全経路で保存。

## §8 fail-closed 条件(列挙)

1. A_lo ≤ 0 → INDETERMINATE。
2. q_floor_C1 ≤ 0 → INDETERMINATE。
3. S2_floor < 3/4 → config 異常として拒否。
4. §3 で許可した以外の三角関数 bound 構成(点 float 評価・単調性の暗黙仮定・
   端点規則のみでの sin/cos 極値処理)を検出したら record を無効化。
5. U_max < 0 で r_hi を用いた W_lo → 無効(§3 違反)。
6. b0 < 1/2 < b1 で cos2_min > 0 → 無効。
7. 予算・depth の run 中／run 後変更 → run 全体を非採用。

## §9 実測根拠(provenance、診断値)

chat 診断(2026-08-12・head 5fafb162 上・非本番):
- 旧 floor(A のみ): J_START initial F plateau 1.40e14(収束停止)。
- A+W²: plateau 4.41e6／tightness median 0.76。
- A+W²+r²B̂: plateau 1.03e5／tightness median 0.96(p90 0.999)、標本 violation 0/268。
- ＋per-cell S floor: **plateau 消滅**(2,005 cells 6.67 → 6,005 cells 4.94、減少継続)、
  残差は TH/R2/C1 に通常分散(C1 depth-cap 独占の解消)。
v4 の判定は §6.2 の6条件そのもので行い、本仕様の数値は期待値であって合格基準ではない。
