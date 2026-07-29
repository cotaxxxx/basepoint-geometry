# 項目3 λ 適応 2D sweep — 設計契約 v8.1
## 凍結版・完全自己完結版

status: `FROZEN`

本書は、項目3 λ 適応 2D sweep の Phase 1 設計契約である。v8 に対する chat 側内容監査の MUST 1件および軽微修正2件を統合済みであり、単体のバイト列から規範内容全体を再構成できる。

旧版 v1–v8 および差分文書は変更履歴を除いて規範性を持たない。

本書の凍結は設計だけを対象とする。以下は一切承認しない。

- production run
- tag作成
- pull request
- 数学計算
- 数値的十分性
- `CERTIFIED_LAMBDA_RANGE` 宣言

---

## 0. 目的と機械結論の上限

λ=`118/25` の C-G 正本 pilot で得た `CERTIFIED_SINGLE_SLICE` を λ 区間へ拡張する。

正本 pilot の同定は、§13で定義する次の完全値と、その相互整合性検査による。

- `cg_pilot_run_id`
- `cg_pilot_receipt_sha256`
- `cg_pilot_source_sha256`
- `cg_pilot_kernel_source_sha256`
- `dependency_snapshot_sha256`

本文中の省略hashや説明用文字列は規範的 identity ではない。

機械結論の上限は、被覆された各 λ-box `B_j` と box 固定の r 窓 `W_j` について、次を示すことに限る。

> 全ての λ ∈ B_j に対し、G(·, λ) の根が W_j 内にちょうど1個存在する。

次は機械結論に含めない。

- `a_c` との比較
- 極限
- 局所正規形との接続
- 根枝の解析性
- 根枝の連続性
- 被覆外区間についての主張

これらは必要に応じて `logical_lemmas` へ paper 記録する。

---

## 1. 座標 encoding

### 1.1 encoding ID

```text
lambda_coordinate_encoding_id = CANONICAL_REDUCED_RATIONAL_V1
r_coordinate_encoding_id      = CANONICAL_DYADIC_V1
enclosure_encoding_id         = CANONICAL_DYADIC_INTERVAL_V1
```

### 1.2 λ座標

λ端点は次を満たす正準有理 object とする。

- 分子・分母は整数
- 分母は正
- 分子と分母は互いに素
- 符号は分子だけに置く
- ゼロは正準な唯一の表現を持つ

λ分割中点は、

```text
(lambda_lo + lambda_hi) / 2
```

を exact rational で計算し、既約正準化する。

### 1.3 r座標と enclosure

r端点、rセル、r窓および全 enclosure は canonical dyadic とする。

### 1.4 比較

次は全て exact rational comparison で行う。

- λ幅
- r幅
- overlap幅
- minimum width
- midpoint
- domain境界
- inclusion

浮動小数比較は禁止する。

### 1.5 byte equality

共有端点の byte equality は、それぞれの座標型の canonical bytes に対して適用する。

異なる encoding 型同士の byte 比較は禁止する。

---

## 2. 型定義

```text
C_anchor_seed
  = 最初に処理する anchor 側の depth-0 初期 box

W_anchor_seed
  = run config の [w0_lo, w0_hi]

B_j
  = 確定した連続 SLICE_BOX_PASS leaf 列を上から再添字した box

W_j
  = B_j が SLICE_BOX_PASS となった最終 attempt の有効窓

B_0 / W_0
  = 最終的に確定した最上位 PASS leaf とその窓

is_anchor_leaf(box)
  iff box.lambda_hi == lambda_anchor

W_prev_for_generation
  = 直上 PASS leaf の最終窓
  = 直上 PASS leaf が存在しなければ W_anchor_seed
```

`C_anchor_seed` の子孫であっても、`lambda_hi != lambda_anchor` である lower child には S7 を適用しない。

---

## 3. verdict、λ添字、box verdict

### 3.1 runner terminal class

```text
runner_terminal_class =
  NORMAL_COMPLETE
  | NORMAL_INCOMPLETE
  | RUN_FATAL
```

#### NORMAL_COMPLETE

次の全てを満たす場合に限る。

- `RUN_FATAL` が発生していない
- `lambda_reached == lambda_target`
- §6の pending-child stack が空
- §9.8の正常完了経路を通った

#### NORMAL_INCOMPLETE

次の全てを満たす場合に限る。

- `RUN_FATAL` が発生していない
- `lambda_reached > lambda_target`
- §9.3、§9.4または§9.7の正常停止経路を通った

#### RUN_FATAL

証明系、schema、source identity、chainまたは内部状態の破損を表す。

`RUN_FATAL` では次を禁止する。

- `SWEEP_COMPLETE`
- `SWEEP_INCOMPLETE`
- proof manifest
- `lambda_reached` からの COMPLETE／INCOMPLETE 推論

`lambda_reached` は診断値としてのみ記録してよい。

### 3.2 sweep verdict

```text
SWEEP_COMPLETE
  iff runner_terminal_class == NORMAL_COMPLETE

SWEEP_INCOMPLETE
  iff runner_terminal_class == NORMAL_INCOMPLETE
```

### 3.3 λ添字

PASS box count を `K` とする。

#### K > 0

```text
lambda_0 = lambda_anchor
lambda_0 > lambda_1 > ... > lambda_K = lambda_reached

B_j = [lambda_{j+1}, lambda_j]
      for 0 <= j < K
```

#### K = 0

次を生成しない。

- `B_0`
- `W_0`
- PASS endpoint列

次を記録する。

```text
lambda_pass_partition     = []
covered_nonempty_interval = false
lambda_reached             = lambda_anchor
```

この `lambda_reached` は状態値にすぎず、`[lambda_anchor, lambda_anchor]` を被覆済み区間として引用してはならない。

K=0では outer endpoint incidence 規則を適用しない。

### 3.4 S5の対象

#### K > 0

最終 PASS partition が、

```text
[lambda_reached, lambda_anchor]
```

を§5の規則で完全被覆しなければならない。

#### NORMAL_COMPLETE

さらに、

```text
lambda_reached == lambda_target
```

を要求する。

#### K = 0

empty-cover 規則を適用する。

### 3.5 box verdict の二層化

```text
SLICE_BOX_PASS
  = runner-local proof candidate
  = checker 未確認の内部候補語
  = 単独引用禁止

VERIFIED_BOX_PASS
  = checker が S1–S8 を全確認した box
  = singleton fresh 検査を含む
```

`CERTIFIED_LAMBDA_RANGE` への入力にできるのは、`VERIFIED_BOX_PASS` だけである。

`SLICE_BOX_FAIL` および `BOX_ATTEMPT_FAIL` は数学的否定ではなく、認証不能を意味する。

### 3.6 飛び越し禁止

未解決 frontier の下側にある box を、連続被覆から独立して認証してはならない。

`NORMAL_INCOMPLETE` で得られた部分区間は、それ単独では `CERTIFIED_*` 判定ではない。

---

## 4. box 判定条件 S1–S8

runner が S1–S3 の証明に singleton λ評価を代用することを禁止する。

例外は次だけである。

- S6 checker singleton fresh evaluations
- pinned S7 dependency snapshot

### S1

```text
G(w_lo, B) > 0
```

λは box 全区間として評価し、Arb の厳密包含で正符号を示す。

### S2

```text
G(w_hi, B) < 0
```

λは box 全区間として評価し、Arb の厳密包含で負符号を示す。

### S3

Wの全 r タイルセルについて、

```text
G_r(cell, B) < 0
```

を示す。

rタイルは§7のアルゴリズムだけで生成する。

### S4

rタイルが§5の被覆規則に適合する。

### S5

λ-box連鎖が§3.4および§5に適合する。

S5は全 PASS 列確定後の global manifest 検査とする。

### S6

隣接 box `B_j` と `B_{j+1}` について、

```text
J_j = W_j ∩ W_{j+1}
```

が正幅でなければならない。

checker は共有端 `lambda_{j+1}` において、次を確認する。

1. 両boxのS1–S3
2. `J_j` の正幅
3. 同一 pinned kernel
4. 同一 canonical λ bytes
5. 両窓上の `G_r < 0`

正幅重なりを持つ連結和集合、

```text
W_j ∪ W_{j+1}
```

上でGが狭義減少するため、両窓内の根は同一であり、`J_j` の内部に存在する。

S6で規定する singleton fresh evaluations を除き、`J_j` の論理再構成のために次を行ってはならない。

- 追加 kernel evaluation
- 数値的区間縮小
- root finder
- Newton step
- bisectionによる根縮小

checker record は次を別 field に記録する。

- box全区間検証
- 共有λ singleton検証

### S7

正本根との接続は包含方式だけを許す。

C-G正本pilotが証明する根の所在は、開区間、

```text
(1/64, 11/256)
```

である。

S7で使用する、

```text
I_CG = [1/64, 11/256]
```

は、その開区間の閉包 hull である。

最終 PASS leaf の `W_0` について、次の全てを要求する。

1. `B_0.lambda_hi == lambda_anchor`
2. pinned dependency snapshot が、`lambda_anchor` において根が開区間 `(1/64, 11/256)` にちょうど1個存在することを証明している
3. `KERNEL_IDENTITY` が成立する
4. 閉包 hull `I_CG = [1/64, 11/256]` について `I_CG ⊆ W_0`

S7が閉包 hull の包含を要求することは、pilotの開区間結論より強い窓条件であり、安全側の接続条件である。

交差だけによる接続は禁止する。

### S8

全 enclosure が、pinned adapter を経由した、

```text
CANONICAL_DYADIC_INTERVAL_V1
```

でなければならない。

### PASS条件

`SLICE_BOX_PASS` には、§8.1の PREP および A0–A7 の全通過を要する。

---

## 5. 被覆規則

λ方向とr方向に同じ規則を適用する。

### 5.1 open atomic cells

各 open atomic cell の coverage count は exactly 1。

### 5.2 global outer endpoints

各 global outer endpoint は exactly 1回現れる。

### 5.3 internal shared endpoints

各 internal shared endpoint は、

- incident cell数が exactly 2
- endpoint canonical bytes が完全一致

を満たす。

### 5.4 検査対象

coverage count の対象は最終 PASS proof partition だけとする。

次は対象外である。

- 失敗した親box
- 失敗attempt
- discarded enclosure
- split前の非leaf partition
- RUN_FATAL途中成果物

K=0では§3.3の empty-cover 規則を適用する。

---

## 6. λ frontier — LIFO状態機械

### 6.1 基本値

```text
minimum_width = 2^-min_lambda_width_exp
```

比較は exact rational とする。

pending-child stack を `S` とする。`S` は LIFO である。

各 stack entry は次を持つ。

```text
box
depth
parent_box_id
primary_window_mode
inherited_window_bytes   # 存在する場合のみ
```

`primary_window_mode` は次の closed enum とする。

```text
PARENT_INHERITED
PREDICTOR_AT_ACTIVATION
```

### 6.2 INIT

```text
current_upper = lambda_anchor
lambda_reached = lambda_anchor
S = empty
```

最初の candidate は、

```text
[
  max(lambda_target, current_upper - 2^-4),
  current_upper
]
```

とする。

これは `C_anchor_seed` であり、depth=0。

### 6.3 candidate activation

candidate を処理対象にした瞬間を activation と呼ぶ。

activation 時に次を固定する。

- box canonical bytes
- depth
- parent_box_id
- primary_window_mode
- §10.1の `predictor_context`
- `W_prev_for_generation`
- activation 時点の global evaluation count

同一幾何boxの PRIMARY attempt と REGENERATED attempt は、同じ activation 時に固定した `predictor_context` を使用する。

同一boxのattempt中に predictor context を再取得してはならない。

### 6.4 candidate幅判定

```text
width(candidate) >= minimum_width
```

ならattemptへ進む。

```text
width(candidate) < minimum_width
```

なら§9.7の `FRONTIER_STOP` へ進む。

幅不足 candidate は、次の全てを満たさなければならない。

- depth=0
- `S` が空
- `candidate.lambda_lo == lambda_target`
- `candidate.lambda_hi == current_upper`

これ以外の幅不足 candidate は `INTERNAL_INCONSISTENCY` による `RUN_FATAL` とする。

### 6.5 SPLIT

親boxを、

```text
parent = [lo, hi]
```

とする。

split可能条件は次の両方。

```text
parent.depth < max_lambda_depth
width(parent)/2 >= minimum_width
```

中点は、

```text
mid = canonical_reduce((lo + hi)/2)
```

とする。

子boxは、

```text
upper_child = [mid, hi]
lower_child = [lo, mid]
```

であり、

```text
upper_child.depth = parent.depth + 1
lower_child.depth = parent.depth + 1
```

とする。

lower child を stack へ push し、upper child を次 candidate とする。

```text
push S:
  box = lower_child
  depth = lower_child.depth
  parent_box_id = parent.box_id
  primary_window_mode = §8.4で決定した値
  inherited_window_bytes = §8.4で存在する場合のみ
```

SPLIT record は次を含む。

- parent box
- parent depth
- midpoint
- upper child
- lower child
- 両child depth
- 両childの primary_window_mode
- inherited window hashまたはbytesの有無

### 6.6 SLICE_BOX_PASS後の優先遷移

PASS record を発行した後、次の順序で処理する。

```text
current_upper  = passed_box.lambda_lo
lambda_reached = current_upper
```

#### target到達

```text
current_upper == lambda_target
```

なら、次を要求する。

```text
S == empty
```

`S != empty` なら、

```text
RUN_FATAL(
  reason   = INTERNAL_INCONSISTENCY,
  location = FRONTIER_STACK_AT_TARGET
)
```

とする。

`S == empty` なら§9.8の `NORMAL_COMPLETE` へ進む。

この場合、次 candidate を生成してはならない。

#### target未到達かつ stack 非empty

```text
current_upper > lambda_target
and S != empty
```

の場合、

```text
S.top.box.lambda_hi == current_upper
```

を要求する。

不一致なら、

```text
RUN_FATAL(
  reason   = INTERNAL_INCONSISTENCY,
  location = FRONTIER_STACK_TOP
)
```

とする。

一致する場合は `S.top` を pop し、次 candidate とする。

#### target未到達かつ stack empty

```text
current_upper > lambda_target
and S == empty
```

の場合だけ、新しい depth-0 初期boxを生成する。

```text
next_candidate = [
  max(lambda_target, current_upper - 2^-4),
  current_upper
]

next_candidate.depth = 0
```

pending child が存在する状態で新しい初期boxを生成してはならない。

### 6.7 SLICE_BOX_FAIL後

split可能なら§6.5へ進む。

split不能なら§9.3へ進む。

### 6.8 処理順の検証

verifier は次を独立再構成する。

- candidate順序
- depth
- stack push/pop
- stack entry
- midpoint
- current_upper
- lambda_reached
- 新規 depth-0 box生成時点

runner record との完全一致を要求する。

---

## 7. rタイル生成

```text
r_tile_algorithm_id = ADAPTIVE_R_BISECTION_V1
```

### 7.1 root

root cell は閉区間 W。

### 7.2 PASS判定

```text
upper(G_r(cell, B)) < 0
```

なら leaf PASS。

### 7.3 split

PASSしない場合、dyadic midpointで二分する。

処理順は、

```text
lower-r child
upper-r child
```

とする。

### 7.4 proof chain

proof chain へ収録できるのは accepted leaf だけである。

failed internal node は attempt 記録側に failure reason だけを残し、enclosure は保存しない。

### 7.5 leaf budget

```text
partition_leaf_count = 1 + split_count
```

各splitの直前に、

```text
partition_leaf_count + 1 > max_r_cells_per_box
```

なら、

```text
R_CELL_BUDGET_EXCEEDED
```

とする。

そのattemptで得た全 enclosure を破棄する。

### 7.6 failure reason

少なくとも次を区別する。

- `NONFINITE_ENCLOSURE`
- `R_CELL_BUDGET_EXCEEDED`
- `PER_BOX_EVAL_LIMIT_REACHED`
- `GLOBAL_EVAL_LIMIT_REACHED`

### 7.7 source pin

次をrun configにピンする。

- algorithm ID
- source path
- source SHA-256

---

## 8. attempt準備、検査順、failure-transition

## 8.1 attempt準備と検査順

### PREP

attempt開始前に窓を確定する。

#### CONFIG_SEED

`C_anchor_seed` の primary attempt は `W_anchor_seed` を使う。

#### PARENT_INHERITED

stack entry に有効な inherited window がある child は、それを primary window とする。

#### PREDICTOR_AT_ACTIVATION

それ以外は、activation時に固定した predictor context から§10の窓を生成する。

PREP失敗は次のいずれかとする。

- `WINDOW_GENERATION_FAIL`
- `WINDOW_OVERLAP_IMPOSSIBLE`

PREP失敗でも `BOX_ATTEMPT_FAIL` を1件生成する。

この場合は規範的に、

```text
attempt_evaluations_used = 0
```

とする。

PREP失敗前に kernel evaluation を実行してはならない。

### A0

source、adapter、encoding、config integrity。

### A1

S1。

### A2

S2。

### A3

S3。

### A4

S4。

### A5a

`W_prev_for_generation` との必要 overlap。

### A5b

直上 PASS leaf が存在する場合だけ、S6構造条件を検査する。

- shared λ bytes
- `J` の正幅
- kernel identity
- required stored sign records
- required derivative records

直上 PASS leaf がなければ `NOT_APPLICABLE`。

checker singleton fresh 検査は A5b とは別の後段検査とする。

### A6

`is_anchor_leaf` の場合だけ S7。

### A7

S8。

### S5

全 PASS 列確定後の global manifest 検査。

## 8.2 failure reason closed enum

failure reason は次の closed enum に限る。

```text
NONCANONICAL_ENCODING
HASH_ORIGIN_MISMATCH
LOGICAL_DEPENDENCY_GATE_VIOLATION
SCHEMA_VIOLATION
COVERAGE_STRUCTURE_VIOLATION
SHARED_ENDPOINT_BYTES_MISMATCH
KERNEL_IDENTITY_MISMATCH
REQUIRED_STORED_RECORD_MISSING
INTERNAL_INCONSISTENCY
ANCHOR_PREDICATE_VIOLATION
SNAPSHOT_MISMATCH
PILOT_IDENTITY_MISMATCH
DESIGN_IDENTITY_MISMATCH

STRICT_SIGN_FAIL
NONFINITE_ENCLOSURE
WINDOW_GENERATION_FAIL
WINDOW_OVERLAP_IMPOSSIBLE
INHERITED_OVERLAP_INSUFFICIENT
ICG_NOT_CONTAINED
R_CELL_BUDGET_EXCEEDED
PER_BOX_EVAL_LIMIT_REACHED

GLOBAL_EVAL_LIMIT_REACHED
```

enum外の failure reason を verifier は拒否する。

## 8.3 failure-transition表

| failure reason | class | regeneration | next state |
|---|---|---:|---|
| NONCANONICAL_ENCODING | RUN_FATAL | no | §9.5 |
| HASH_ORIGIN_MISMATCH | RUN_FATAL | no | §9.5 |
| LOGICAL_DEPENDENCY_GATE_VIOLATION | RUN_FATAL | no | §9.5 |
| SCHEMA_VIOLATION | RUN_FATAL | no | §9.5 |
| COVERAGE_STRUCTURE_VIOLATION | RUN_FATAL | no | §9.5 |
| SHARED_ENDPOINT_BYTES_MISMATCH | RUN_FATAL | no | §9.5 |
| KERNEL_IDENTITY_MISMATCH | RUN_FATAL | no | §9.5 |
| REQUIRED_STORED_RECORD_MISSING | RUN_FATAL | no | §9.5 |
| INTERNAL_INCONSISTENCY | RUN_FATAL | no | §9.5 |
| ANCHOR_PREDICATE_VIOLATION | RUN_FATAL | no | §9.5 |
| SNAPSHOT_MISMATCH | RUN_FATAL | no | §9.5 |
| PILOT_IDENTITY_MISMATCH | RUN_FATAL | no | §9.5 |
| DESIGN_IDENTITY_MISMATCH | RUN_FATAL | no | §9.5 |
| STRICT_SIGN_FAIL | BOX_RETRYABLE | yes* | §8.5 |
| NONFINITE_ENCLOSURE | BOX_RETRYABLE | yes* | §8.5 |
| INHERITED_OVERLAP_INSUFFICIENT | BOX_RETRYABLE | yes* | §8.5 |
| ICG_NOT_CONTAINED | BOX_RETRYABLE | yes* | §8.5 |
| WINDOW_GENERATION_FAIL | BOX_RETRYABLE | no | SLICE_BOX_FAIL→split判定 |
| WINDOW_OVERLAP_IMPOSSIBLE | BOX_RETRYABLE | no | SLICE_BOX_FAIL→split判定 |
| R_CELL_BUDGET_EXCEEDED | BOX_RETRYABLE | no | SLICE_BOX_FAIL→split判定 |
| PER_BOX_EVAL_LIMIT_REACHED | BOX_RETRYABLE | no | SLICE_BOX_FAIL→split判定 |
| GLOBAL_EVAL_LIMIT_REACHED | GLOBAL_STOP | no | §9.4 |

`yes*` は、次の全てを満たす場合に限り、ちょうど1回の regenerated attempt を許す。

- 現在が PRIMARY attempt
- per-box evaluation 残量が正
- failure class が `BOX_RETRYABLE`
- failure reason が表で `yes*`
- PRIMARY attempt の `window_origin` が次のいずれか
  - `CONFIG_SEED`
  - `PARENT_INHERITED`

PRIMARY attempt の `window_origin` が次のいずれかである場合、`yes*` failure reason であっても regeneration を行ってはならない。

- `PREDICTOR_HORIZONTAL`
- `PREDICTOR_LINEAR`

predictor由来 PRIMARY では、同一 predictor context と同一決定論的窓生成規則から同一 bytes の窓が再生成されるため、regenerated attempt は新しい認証試行を構成しない。

predictor由来 PRIMARY が失敗した場合は、

```text
BOX_ATTEMPT_FAIL(PRIMARY)
SLICE_BOX_FAIL
```

を発行し、split可否判定へ進む。

REGENERATED attempt の失敗後に、さらに再生成してはならない。

## 8.4 split時の窓継承

### 親primary windowが有効に構築済み

§10.2の全段階を通過した有効 primary window が存在する場合、

```text
upper_child.primary_window_mode = PARENT_INHERITED
lower_child.primary_window_mode = PARENT_INHERITED
```

とする。

両childは親の primary window を継承する。

regenerated window は継承してはならない。

### 親primary windowが未構築または無効

次のいずれかの場合、継承窓なしとする。

- PREP途中で失敗
- clamp後に無効
- minimum width喪失
- overlap喪失
- noncanonical window
- window object未完成

この場合、

```text
upper_child.primary_window_mode = PREDICTOR_AT_ACTIVATION
lower_child.primary_window_mode = PREDICTOR_AT_ACTIVATION
```

とする。

各childは、自身が candidate として activation された時点の確定 PASS 列から predictor context を取得する。

したがって、upper child と pending lower child が同じ predictor context を使うことは要求しない。

upper child が PASS した後に lower child が activation された場合、lower child はその新しい PASS 点を含む最新の確定 PASS 列を使用する。

split時点の predictor 点列を両child用に凍結してはならない。

## 8.5 1幾何boxのattempt状態機械

1. candidate activation で predictor context を固定する
2. PRIMARY PREP を行う
3. A0→A7を順に検査する
4. PRIMARY PASSなら `SLICE_BOX_PASS`
5. PRIMARYが `yes*` reason で失敗し、かつ `window_origin` が `CONFIG_SEED` または `PARENT_INHERITED` である場合に限り、同じ activation 時に固定した predictor context を使用して、ちょうど1回の REGENERATED attempt を行う
6. PRIMARYの `window_origin` が `PREDICTOR_HORIZONTAL` または `PREDICTOR_LINEAR` である場合、regeneration を行わず `SLICE_BOX_FAIL`
7. REGENERATED PASSなら `SLICE_BOX_PASS`
8. REGENERATED失敗、または regeneration 不可なら `SLICE_BOX_FAIL`
9. split可能なら SPLIT
10. split不能なら§9.3へ進む

次の failure 後に regeneration してはならない。

- `WINDOW_GENERATION_FAIL`
- `WINDOW_OVERLAP_IMPOSSIBLE`
- `R_CELL_BUDGET_EXCEEDED`
- `PER_BOX_EVAL_LIMIT_REACHED`
- predictor由来 PRIMARY の任意の failure

---

## 9. record grammar

## 9.1 evaluation counter

attempt record は次を分離して持つ。

```text
attempt_evaluations_used
box_evaluations_used_cumulative
global_evaluations_used_cumulative
```

`BOX_ATTEMPT_FAIL` の必須 field は次。

- box
- box_id
- attempt_stage
- window_origin
- depth
- 3 evaluation counter
- fixed budget
- failure_reason
- failure location
- predictor_context_sha256
- primary window の構築完了有無

`attempt_stage` は、

```text
PRIMARY
REGENERATED
```

だけを許す。

`window_origin` は、

```text
CONFIG_SEED
PARENT_INHERITED
PREDICTOR_HORIZONTAL
PREDICTOR_LINEAR
```

だけを許す。

## 9.2 通常box

### PRIMARY PASS

```text
SLICE_BOX_PASS
```

### PRIMARY FAIL、REGENERATED PASS

```text
BOX_ATTEMPT_FAIL(PRIMARY)
SLICE_BOX_PASS
```

PRIMARYの failure record を省略してはならない。

### FAIL後にsplit可能

```text
BOX_ATTEMPT_FAIL(PRIMARY)
BOX_ATTEMPT_FAIL(REGENERATED)   # 実施時のみ
SLICE_BOX_FAIL
SPLIT
```

PREP失敗などで PRIMARY だけを実施した場合は、PRIMARY record だけとする。

## 9.3 最終frontier

split不能の `BOX_RETRYABLE` は、

```text
BOX_ATTEMPT_FAIL(PRIMARY)
BOX_ATTEMPT_FAIL(REGENERATED)   # 実施時のみ
SLICE_BOX_FAIL
SWEEP_INCOMPLETE
```

の順で連続配置する。

terminal class は `NORMAL_INCOMPLETE`。

## 9.4 GLOBAL_STOP

```text
BOX_ATTEMPT_FAIL(
  current attempt,
  reason = GLOBAL_EVAL_LIMIT_REACHED
)
SLICE_BOX_FAIL
SWEEP_INCOMPLETE
```

次を要求する。

- 阻止対象 kernel call を実行しない
- current attempt の一時 enclosure を全破棄
- regeneration しない
- split しない
- terminal class=`NORMAL_INCOMPLETE`

PRIMARY以前に発行済みの record がある場合、それらは保持する。

## 9.5 RUN_FATAL

```text
RUN_FATAL(
  reason,
  detection_location,
  diagnostic_state
)
```

その後、

```text
nonzero exit
```

とする。

次を発行してはならない。

- `SWEEP_COMPLETE`
- `SWEEP_INCOMPLETE`
- proof manifest
- verified manifest

RUN_FATAL以前に既に書き込まれた append-only diagnostic record は残してよいが、proof artifact として引用してはならない。

## 9.6 checker

checker terminal class は、

```text
VERIFY_PASS
VERIFY_FAIL
```

とする。

次は `VERIFY_FAIL`。

- S5失敗
- singleton fresh失敗
- record grammar違反
- window再導出不一致
- predictor context再導出不一致
- stack履歴不一致
- candidate順序不一致
- source hash不一致
- pilot identity不一致
- config hash不一致
- enclosure round-trip不一致

`VERIFY_FAIL` run は `CERTIFIED_LAMBDA_RANGE` へ昇格不可。

各boxについて、checkerがS1–S8を全確認した場合だけ `VERIFIED_BOX_PASS` を発行する。

## 9.7 FRONTIER_STOP

未試行の depth-0 remainder が minimum width 未満の場合、

```text
FRONTIER_STOP(
  reason = LAMBDA_WIDTH_BELOW_MINIMUM,
  box,
  depth = 0
)
SWEEP_INCOMPLETE
```

とする。

この経路で次を生成してはならない。

- `BOX_ATTEMPT_FAIL`
- `SLICE_BOX_FAIL`
- `attempt_stage`
- `window_origin`
- attempt evaluation counter

terminal class は `NORMAL_INCOMPLETE`。

## 9.8 NORMAL_COMPLETE

最終boxのPASSにより、

```text
current_upper == lambda_target
and S == empty
```

となった場合、

```text
SLICE_BOX_PASS(final box)
SWEEP_COMPLETE
```

で正常終了する。

terminal class は `NORMAL_COMPLETE`。

`SWEEP_COMPLETE` 後に次を生成してはならない。

- 新しい candidate
- zero-width candidate
- `FRONTIER_STOP`
- `SLICE_BOX_FAIL`
- `SPLIT`
- `SWEEP_INCOMPLETE`

---

## 10. r窓生成

## 10.1 predictor context

### runner-local PASS点

```text
P_0 = (
  lambda_anchor,
  midpoint(I_CG)
)
```

以後、確定した runner-local PASS 列について、

```text
P_j = (
  lambda_j,
  midpoint(J_{j-1})
)
```

とする。

`J_{j-1}` は、直上の連続 PASS 窓から得た canonical overlap である。

### predictor context capture

candidate activation 時に、次を immutable に固定する。

```text
predictor_context = {
  latest_point,
  previous_point_if_present,
  source_pass_box_ids,
  source_lambda_bytes,
  source_overlap_bytes
}
```

canonical bytes 全体の SHA-256 を、

```text
predictor_context_sha256
```

とする。

### predictor

点が1個の場合は水平 predictor。

点が2個以上の場合は、直近2点を通る有理直線 `L`。

候補box、

```text
C = [lambda_lo, lambda_hi]
```

に対する評価値は、

```text
q = L(lambda_hi)
```

とする。

midpointおよび直線計算は exact rational。

PRIMARY と REGENERATED は同一box activation時の同じ predictor context を使用する。

異なるboxのactivationでは predictor context を再取得する。

## 10.2 点から窓への変換

```text
q = rational predictor value
g = 2^-window_grid_exp
minimum_window_width = 2^-window_min_width_exp
```

### Step 1 — center cell

```text
c_lo = floor(q/g) * g
c_hi = ceil(q/g) * g
```

### Step 2 — minimum width

```text
initial_width = c_hi - c_lo

needed_steps =
  max(
    0,
    ceil(
      (minimum_window_width - initial_width) / g
    )
  )

lower_steps = ceil(needed_steps / 2)
upper_steps = floor(needed_steps / 2)
```

```text
w_lo = c_lo - lower_steps*g
w_hi = c_hi + upper_steps*g
```

tieでは lower 側へ1step多く配分する。

### Step 3 — overlap可能性

```text
maximum_possible_overlap =
  width(W_prev_for_generation ∩ [g, 1-g])
```

```text
maximum_possible_overlap < delta_overlap_min
```

なら、

```text
WINDOW_OVERLAP_IMPOSSIBLE
```

として直ちにFAIL。

### Step 4 — overlap拡張

次を満たすまで、1stepずつ拡張する。

```text
width(
  W_prev_for_generation ∩ W_new
) >= delta_overlap_min
```

各stepで、

```text
lower_expandable iff w_lo > g
upper_expandable iff w_hi < 1-g
```

とする。

```text
w_lo <= g
```

ならlower側は saturated。

```text
w_hi >= 1-g
```

ならupper側は saturated。

方向選択は、現在の unclamped rational endpoints の midpoint で行う。

```text
midpoint(W_prev) > midpoint(W_new)
  → upper側を選択

midpoint(W_prev) < midpoint(W_new)
  → lower側を選択

midpoint同値
  → lower側を選択
```

選択側が saturated なら反対側を選択する。

両側 saturated かつ overlap 不足なら、

```text
WINDOW_OVERLAP_IMPOSSIBLE
```

とする。

いかなるstepも、端点を `[g, 1-g]` のさらに外側へ移動してはならない。

全step履歴を canonical record として保存する。

### Step 5 — domain clamp

```text
w_lo = max(w_lo, g)
w_hi = min(w_hi, 1-g)
```

### Step 6 — final gate

clamp後に次の全てを要求する。

```text
w_lo < w_hi
width(W_new) >= minimum_window_width
width(W_prev_for_generation ∩ W_new)
  >= delta_overlap_min
```

1つでも失敗すれば、

```text
WINDOW_GENERATION_FAIL
```

とする。

暗黙の再調整、再拡張、center変更は禁止する。

### verifier

verifierは次を独立再導出する。

- predictor context
- q
- center cell
- needed steps
- lower／upper steps
- saturation
- 各overlap step
- clamp
- final window

runner出力との完全一致を要求する。

## 10.3 seedおよびwindow config gate

次をschema検証で必須とする。

```text
delta_overlap_min > 0

delta_overlap_min
  <= 2^-window_min_width_exp

2^-window_min_width_exp
  <= 1 - 2g

w0_lo, w0_hi
  are canonical dyadic

g <= w0_lo < w0_hi <= 1-g

I_CG ⊆ W_anchor_seed

width(W_anchor_seed)
  >= delta_overlap_min

width(W_anchor_seed)
  >= minimum_window_width
```

seedへの minimum width 免除は認めない。

---

## 11. 論理依存ゲート

required set は exactly 次の5件。

```text
L-CONT
L-DERIV
L-ENCL
L-SIGN
L-IVT
```

意味は次。

```text
L-CONT
  Gは対象領域でrに関して連続

L-DERIV
  G_r = ∂G/∂r
  同一pinned kernel内の恒等

L-ENCL
  adapter enclosureは真値を包含

L-SIGN
  strict sign enclosureは実関数のstrict signを含意

L-IVT
  IVTとstrict monotonicityによる
  existence / uniqueness
```

各dependencyについて、

```text
dependency_entry_sha256 =
  SHA256(
    pinned snapshot内の
    当該lemma dependency recordの
    canonical bytes全体
  )
```

とする。

chain genesisとは名前空間を分離する。

checkerはsnapshot entry内の次を検証する。

- `lemma_id`
- full-record hash
- `allowlist_id`
- `supports_machine_conclusion == true`

`supports_machine_conclusion` をrun configの自己申告値から採用してはならない。

次のいずれかなら、

```text
LOGICAL_DEPENDENCY_GATE_VIOLATION
```

による RUN_FATAL。

- required key不存在
- unknown required key
- lemma ID不一致
- hash不一致
- allowlist外
- allowlist ID不一致
- `supports_machine_conclusion != true`
- snapshot record欠落

`machine_verified:false` のpaper lemmaをrequired setの代用にしてはならない。

required set外の補助lemmaだけを `logical_lemmas` へpaper記録できる。

---

## 12. 機構

### 12.1 kernel identity

pilot正本と同一のpinned `G/G_r` を使う。

検査順は次。

1. path containment
2. import前hash
3. module origin一致
4. import
5. import後再hash
6. snapshot内pilot kernel hashとの一致
7. receipt内pilot kernel hashとの一致

不一致は `KERNEL_IDENTITY_MISMATCH` または `HASH_ORIGIN_MISMATCH`。

### 12.2 pilot identity

`cg_pilot_run_id` は exactly、

```text
30334858060
```

とする。

pinned pilot receiptおよびdependency snapshotについて、checkerは次を要求する。

```text
receipt.run_id
  == cg_pilot_run_id
  == 30334858060

receipt.pilot_source_sha256
  == cg_pilot_source_sha256

receipt.pilot_kernel_source_sha256
  == cg_pilot_kernel_source_sha256

snapshot.pilot_run_id
  == cg_pilot_run_id

snapshot.pilot_source_sha256
  == cg_pilot_source_sha256

snapshot.pilot_kernel_source_sha256
  == cg_pilot_kernel_source_sha256

snapshot.certified_lambda
  == 118/25

kernel_source_sha256
  == cg_pilot_kernel_source_sha256
```

C-G正本pilotの root-location conclusion は、

```text
root ∈ (1/64, 11/256)
```

である。

S7 window-containment condition は、

```text
[1/64, 11/256] ⊆ W_0
```

である。

snapshotとのidentity検査は、interval objectの開閉属性そのものの等値ではなく、端点対の canonical bytes 等値とする。

```text
snapshot.certified_root_interval.lower_endpoint_bytes
  == canonical_bytes(1/64)

snapshot.certified_root_interval.upper_endpoint_bytes
  == canonical_bytes(11/256)
```

receiptに根区間端点が保存される場合も、同じ端点対の canonical bytes 等値を要求する。

receiptがdependency snapshot hashを持つ場合、

```text
receipt.dependency_snapshot_sha256
  == dependency_snapshot_sha256
```

も要求する。

不一致は `PILOT_IDENTITY_MISMATCH` または `SNAPSHOT_MISMATCH`。

完全hash値は production run config 監査で固定し、その完全config SHAを別途承認する。

### 12.3 design identity

run configは次を含む。

- `sweep_design_path`
- `sweep_design_sha256`

checkerは実際にcheckoutされた本設計契約の canonical bytes をhashし、run config値と一致させる。

不一致は `DESIGN_IDENTITY_MISMATCH`。

### 12.4 canonical JSON

canonical JSON object bytes は次。

```text
ensure_ascii = True
sort_keys = True
separators = (",", ":")
```

次を禁止する。

- 重複key
- CRLF
- 末尾LF
- NaN
- Infinity
- 浮動小数によるexact値表現

recordsはJSONLとする。

- record間にLF
- ファイル末尾に最終LFを付けない

### 12.5 enclosure serialization

保存前に round-trip serialization を行う。

guard retryは許すが、各retryをkernel evaluation countに含める。

round-trip後のobjectが正準bytesと一致しなければ保存してはならない。

### 12.6 checker fresh evaluation

checkerは保存enclosureの正準性確認に加え、同一cellを `checker_dps` でfresh評価する。

fresh enclosureでも同じstrict signを要求する。

### 12.7 chain

```text
sweep_run_config_sha256 =
  SHA256(
    canonical JSON bytes
    of the complete run config
  )
```

chain genesisは `SWEEP_RUN_CONFIG_V1` 名前空間における `sweep_run_config_sha256` だけとする。

`dependency_entry_sha256` との混用は禁止する。

成果物階層は次。

```text
lambda-box chain
  → box内r-chain
  → checker records
  → full lambda coverage manifest
```

### 12.8 budget

kernel call直前に次の順で検査する。

1. global limit
2. per-box limit
3. kernel call

超過が見込まれるcallは実行しない。

実行したcallは次を問わず全て加算する。

- 成功
- failure
- nonfinite
- guard retry

checker再評価はrunner budgetに含めない。

`per_box_eval_limit` は同一幾何boxの全attempt合計。

split後のchildは、

```text
per_box_evaluations_used = 0
```

から開始する。

global counterだけを継承する。

### 12.9 workflow

無フィルタ branch-push triggerは禁止する。

唯一の許可triggerは、

```yaml
on:
  push:
    tags:
      - "item3-sweep-run-*"
```

tag規約は、

```text
item3-sweep-run-<40桁小文字hex>
```

とする。

checkout前に、

```text
tag suffix == GITHUB_SHA
```

を要求する。

checkout後に、

```text
HEAD == GITHUB_SHA
```

を要求する。

workflow権限は、

```text
permissions:
  contents: read
```

とする。

```text
persist-credentials: false
```

を要求する。

全GitHub Actionsはcommit SHAで固定する。

受領証を書き込むobserverは別workflow・別権限とする。

observer側で次を管理する。

- run_id単調更新則
- `EXCLUDED_HEAD_SHA`

---

## 13. run config closed schema

unknown top-level fieldは禁止する。

canonical run configの必須fieldは次。

### 13.1 design

```text
sweep_design_path
sweep_design_sha256
```

### 13.2 λとwindow

```text
lambda_anchor
lambda_target
min_lambda_width_exp
delta_overlap_min
window_grid_exp
window_min_width_exp
w0_lo
w0_hi
```

### 13.3 budgetと精度

```text
global_eval_limit
per_box_eval_limit
max_lambda_depth
max_r_cells_per_box
dps
checker_dps
```

### 13.4 implementation source

```text
runner_source_path
runner_source_sha256
checker_source_path
checker_source_sha256
r_tile_algorithm_id
r_tile_source_path
r_tile_source_sha256
kernel_source_path
kernel_source_sha256
adapter_id
adapter_source_path
adapter_sha256
```

### 13.5 pilot assets

```text
cg_pilot_run_id
cg_pilot_receipt_path
cg_pilot_receipt_sha256
cg_pilot_source_sha256
cg_pilot_kernel_source_sha256
dependency_snapshot_path
dependency_snapshot_sha256
```

### 13.6 logical dependencies

```text
sweep_logical_dependencies
```

### 13.7 encoding IDs

```text
lambda_coordinate_encoding_id
r_coordinate_encoding_id
enclosure_encoding_id
```

### 13.8 型gate

```text
lambda_anchor
  exact rational == 118/25

lambda_target
  canonical reduced rational
  1 <= target < anchor

min_lambda_width_exp
  nonnegative integer

delta_overlap_min
  exact rational > 0

window_grid_exp
  nonnegative integer

window_min_width_exp
  nonnegative integer

w0_lo, w0_hi
  canonical dyadic

global_eval_limit
  positive integer

per_box_eval_limit
  positive integer
  <= global_eval_limit

max_lambda_depth
  nonnegative integer

max_r_cells_per_box
  integer >= 1

dps
  positive integer

checker_dps
  integer >= dps

cg_pilot_run_id
  integer == 30334858060
```

全SHA-256 fieldは、

```text
exactly 64 lowercase hexadecimal characters
```

とする。

### 13.9 path gate

全path fieldは次を満たす。

- nonempty
- normalized repo-relative path
- `/`区切り
- absolute path禁止
- `..`禁止
- empty component禁止
- NUL禁止
- symlink escape禁止
- checkout root外へのresolve禁止

### 13.10 ID string gate

ID fieldはnonempty ASCIIで、次の正規表現に適合する。

```text
[A-Za-z0-9._:-]+
```

### 13.11 encoding定数

```text
lambda_coordinate_encoding_id
  == "CANONICAL_REDUCED_RATIONAL_V1"

r_coordinate_encoding_id
  == "CANONICAL_DYADIC_V1"

enclosure_encoding_id
  == "CANONICAL_DYADIC_INTERVAL_V1"

r_tile_algorithm_id
  == "ADAPTIVE_R_BISECTION_V1"
```

### 13.12 logical dependency object

`sweep_logical_dependencies` は、lemma IDをkeyとするJSON object。

key setはexactly、

```text
{
  "L-CONT",
  "L-DERIV",
  "L-ENCL",
  "L-SIGN",
  "L-IVT"
}
```

各entryのfieldはexactly次。

```text
{
  "lemma_id":
    canonical nonempty ID string,

  "dependency_entry_sha256":
    64 lowercase hex,

  "expected_allowlist_id":
    canonical nonempty ID string
}
```

各entryで、

```text
entry.lemma_id == object key
```

を要求する。

unknown key、unknown entry field、required key欠落は禁止する。

allowlist membershipはpinned snapshotから検証する。

config内のboolean自己申告を採用してはならない。

`sort_keys=True` によって同一集合の canonical bytes を一意化する。

### 13.13 alias

外部入力aliasとして、

```text
lambda_match
```

を許してよいが、canonical run configへ変換する前に、

```text
lambda_match == lambda_anchor == 118/25
```

を検査する。

canonical run configには `lambda_match` を残してはならない。

### 13.14 candidate values

```text
min_lambda_width_exp = 20
delta_overlap_min    = 2^-12
window_grid_exp      = 16
window_min_width_exp = 12
```

これらはschema上の候補であり、Phase 1では数値的十分性を認定しない。

次はproduction run config監査で完全値を固定する。

- `lambda_target`
- `w0_lo`
- `w0_hi`
- budgets
- dps
- 全source SHA-256
- pilot receipt SHA-256
- pilot source SHA-256
- dependency snapshot SHA-256

固定後、complete run configのSHA-256を別途承認する。

---

## 14. 判定語

runner語彙：

```text
SLICE_BOX_PASS
SLICE_BOX_FAIL
BOX_ATTEMPT_FAIL
FRONTIER_STOP
RUN_FATAL
SWEEP_COMPLETE
SWEEP_INCOMPLETE
```

checker語彙：

```text
VERIFIED_BOX_PASS
VERIFY_PASS
VERIFY_FAIL
```

failure reasonは§8.2のclosed enumだけを許す。

`CERTIFIED_LAMBDA_RANGE` は、Actions正本runに対するchat側全数照合PASS後だけ宣言できる。

`CERTIFIED_*` 禁止はsweep生成物の次に適用する。

- verdict fields
- records
- summaries
- filenames

pinned dependency snapshot内の既存語彙だけはallowlistで許可する。

---

## 15. controls — CONTROL_EXPECT単一辞書

`CONTROL_EXPECT` の全keyは本節に列挙したものに限る。

旧版のcontrol集合は継承しない。

各controlは次を1:1で持つ。

```text
fixture_id
mutation
expected_failure_reason
expected_terminal_class
expected_checker_result
```

## 15.1 positive controls

```text
POS_COMPLETE_2BOX
POS_PRIMARY_FAIL_REGENERATED_PASS
POS_GLOBAL_STOP
POS_WINDOW_FAIL_SPLIT
POS_RUN_FATAL
POS_FRONTIER_STOP
POS_LIFO_PENDING_CHILD
POS_TARGET_COMPLETE
POS_PRIMARY_UNBUILT_CHILD_CONTEXT
POS_CHECKER_VERIFY_PASS
```

意味論：

```text
POS_COMPLETE_2BOX
  正常2-box連鎖
  runner=NORMAL_COMPLETE
  checker=VERIFY_PASS

POS_PRIMARY_FAIL_REGENERATED_PASS
  CONFIG_SEEDまたはPARENT_INHERITED由来PRIMARY strict sign FAIL
  REGENERATED PASS
  primary BOX_ATTEMPT_FAILを保持
  checker=VERIFY_PASS

POS_GLOBAL_STOP
  GLOBAL_EVAL_LIMIT_REACHED
  runner=NORMAL_INCOMPLETE
  grammar=§9.4

POS_WINDOW_FAIL_SPLIT
  WINDOW_GENERATION_FAIL
  regenerationなし
  split実行

POS_RUN_FATAL
  RUN_FATAL後にverdict・manifest不発行
  nonzero exit

POS_FRONTIER_STOP
  minimum-width未満depth-0 remainder
  grammar=§9.7

POS_LIFO_PENDING_CHILD
  upper child PASS後にpending lower childをpop
  新規初期boxを生成しない

POS_TARGET_COMPLETE
  最終box PASS後にtarget到達
  zero-width candidateを作らずSWEEP_COMPLETE

POS_PRIMARY_UNBUILT_CHILD_CONTEXT
  親primary未構築
  upper/lower childが各activation時のpredictor contextを使用

POS_CHECKER_VERIFY_PASS
  全box VERIFIED_BOX_PASS
  global VERIFY_PASS
```

## 15.2 sign、tile、coverage controls

```text
NEG_S1_SIGN
NEG_S2_SIGN
NEG_S3_NONNEGATIVE_CELL
NEG_OPEN_CELL_COVERAGE_NOT_ONE
NEG_OUTER_ENDPOINT_DUPLICATE
NEG_SHARED_ENDPOINT_INCIDENT_NOT_TWO
NEG_SHARED_ENDPOINT_BYTES_LAMBDA
NEG_SHARED_ENDPOINT_BYTES_R
NEG_R_TILE_ORDER
NEG_PARTITION_LEAF_COUNT
NEG_COVERAGE_FAILED_PARENT_INCLUDED
NEG_COVERAGE_FAILED_ATTEMPT_INCLUDED
```

## 15.3 coordinate、λ-chain controls

```text
NEG_LAMBDA_NONREDUCED
NEG_LAMBDA_DENOMINATOR_NONPOSITIVE
NEG_LAMBDA_DYADIC_FORCED_MUTATION
NEG_LAMBDA_CHAIN_GAP
NEG_LAMBDA_CHAIN_OVERLAP
NEG_LAMBDA_REACHED_JUMP
NEG_INCOMPLETE_INDEX_TERMINATES_AT_TARGET
NEG_ZERO_PASS_B0_CREATED
NEG_ZERO_PASS_DEGENERATE_INTERVAL_QUOTED
NEG_TARGET_CLIP_VIOLATION
```

## 15.4 S6、S7、identity controls

```text
NEG_J_NONPOSITIVE
NEG_S7_INTERSECTION_ONLY
NEG_S7_APPLIED_TO_SEED_NOT_FINAL_W0
NEG_S7_APPLIED_TO_NONANCHOR_CHILD
NEG_ANCHOR_PREDICATE
NEG_A5A_A5B_MIXED
NEG_SEED_USED_AS_S6_ADJACENT_BOX
NEG_SHARED_ENDPOINT_MISMATCH_RETRYABLE
NEG_KERNEL_IDENTITY_MISMATCH_RETRYABLE
NEG_REQUIRED_RECORD_MISSING_RETRYABLE
NEG_INTERNAL_J_INCONSISTENCY_RETRYABLE
NEG_ICG_NOT_CONTAINED_FATAL
NEG_PILOT_RUN_ID_MISMATCH
NEG_PILOT_RECEIPT_HASH_MISMATCH
NEG_PILOT_SOURCE_HASH_MISMATCH
NEG_PILOT_KERNEL_HASH_MISMATCH
NEG_SNAPSHOT_PILOT_RELATION_MISMATCH
NEG_DESIGN_HASH_MISMATCH
```

## 15.5 predictor、window controls

```text
NEG_PREDICTOR_BOOTSTRAP
NEG_PREDICTOR_Q_NOT_LAMBDA_HI
NEG_PREDICTOR_CONTEXT_RECAPTURE_SAME_BOX
NEG_PREDICTOR_CONTEXT_SPLIT_TIME_FROZEN
NEG_PENDING_LOWER_IGNORES_NEW_UPPER_PASS
NEG_REGENERATION_SECOND_TIME
NEG_RUN_FATAL_REGENERATION
NEG_WINDOW_FAIL_REGENERATION
NEG_R_CELL_BUDGET_REGENERATION
NEG_PER_BOX_BUDGET_REGENERATION
NEG_ZERO_REMAINING_REGENERATION
NEG_INHERITED_OVERLAP_WRONG_CLASS
NEG_REGENERATED_WINDOW_INHERITED
NEG_UNFINISHED_WINDOW_INHERITED
NEG_INVALID_CLAMPED_WINDOW_INHERITED
NEG_PRIMARY_BUILD_FAIL_CHILD_INHERITED
NEG_NEEDED_STEPS_NEGATIVE
NEG_OVERLAP_DIRECTION
NEG_OVERLAP_TIE
NEG_SATURATED_SIDE_EXPANSION
NEG_OVERLAP_OUTSIDE_DOMAIN_STEP
NEG_OVERLAP_MIDPOINT_USES_CLAMPED_VALUE
NEG_OVERLAP_IMPOSSIBLE_INFINITE_LOOP
NEG_CLAMP_LOSES_OVERLAP_ACCEPTED
NEG_CLAMP_LOSES_MIN_WIDTH_ACCEPTED
NEG_WINDOW_STEP_HISTORY_MISMATCH
NEG_WINDOW_REDERIVATION_MISMATCH
NEG_SEED_ICG_GATE
NEG_SEED_DOMAIN_GATE
NEG_SEED_MIN_WIDTH_GATE
NEG_SEED_OVERLAP_WIDTH_GATE
NEG_PREDICTOR_PRIMARY_REGENERATION
```

`NEG_PREDICTOR_PRIMARY_REGENERATION` のfixture mutationは次。

```text
window_originが
PREDICTOR_HORIZONTAL
または
PREDICTOR_LINEAR
であるPRIMARY attemptが失敗した後、
REGENERATED attemptを開始する
```

正しい遷移は次だけである。

```text
BOX_ATTEMPT_FAIL(PRIMARY)
SLICE_BOX_FAIL
split判定
```

Phase 2で `CONTROL_EXPECT` 辞書を実体化する際は、非阻害注記を解消して単一値へ固定する。

```text
expected_checker_result = VERIFY_FAIL
failure_category = RECORD_GRAMMAR_VIOLATION
```

## 15.6 frontier、stack、depth controls

```text
NEG_LOWER_CHILD_FIRST
NEG_PENDING_CHILD_NEW_INITIAL_BOX
NEG_STACK_TOP_MISMATCH_NOT_FATAL
NEG_CHILD_DEPTH_NOT_INCREMENTED
NEG_SPLIT_DEPTH_CONDITION
NEG_SPLIT_HALF_WIDTH_CONDITION
NEG_MIN_WIDTH_BOX_ATTEMPT
NEG_FRONTIER_STOP_WITH_ATTEMPT_FAIL
NEG_FRONTIER_STOP_WITH_SLICE_FAIL
NEG_FRONTIER_STOP_WITH_ATTEMPT_FIELDS
NEG_FRONTIER_STOP_NONDEPTH_ZERO
NEG_TARGET_ZERO_WIDTH_CANDIDATE
NEG_COMPLETE_WITH_NONEMPTY_STACK
NEG_COMPLETE_GRAMMAR
NEG_COMPLETE_FOLLOWED_BY_FRONTIER_STOP
NEG_CHILD_PER_BOX_COUNTER_NOT_RESET
NEG_SPLIT_RECORD_CHILD_MISMATCH
```

## 15.7 budget、counter controls

```text
NEG_BUDGET_POSTCHECK
NEG_GLOBAL_LIMIT_AFTER_PER_BOX_CHECK
NEG_FAILED_CALL_NOT_COUNTED
NEG_GUARD_RETRY_NOT_COUNTED
NEG_EVALUATION_COUNTERS_NOT_SEPARATED
NEG_PER_BOX_LIMIT_PER_ATTEMPT
NEG_PER_BOX_LIMIT_GREATER_THAN_GLOBAL
NEG_GLOBAL_STOP_REGENERATION
NEG_GLOBAL_STOP_SPLIT
NEG_GLOBAL_STOP_ENCLOSURE_RETAINED
NEG_R_CELL_OVERBUDGET_ENCLOSURE_RETAINED
```

## 15.8 grammar、terminal controls

```text
NEG_PRIMARY_FAIL_RECORD_MISSING
NEG_REGENERATED_FAIL_RECORD_MISSING
NEG_RECORD_ORDER_PRIMARY_REGEN
NEG_RECORD_ORDER_SPLIT
NEG_RECORD_ORDER_FINAL_FRONTIER
NEG_RECORD_ORDER_GLOBAL_STOP
NEG_RUN_FATAL_EMITS_COMPLETE
NEG_RUN_FATAL_EMITS_INCOMPLETE
NEG_RUN_FATAL_EMITS_MANIFEST
NEG_RUN_FATAL_USES_REACHED_FOR_VERDICT
NEG_SLICE_BOX_FAIL_PROMOTED_COMPLETE
NEG_SLICE_BOX_PASS_USED_AS_VERIFIED
NEG_CHECKER_FAIL_CERTIFIED
NEG_BOX_ATTEMPT_FAIL_MISSING
NEG_ENUM_UNKNOWN_FAILURE_REASON
```

## 15.9 serialization、chain、precision controls

```text
NEG_NONCANONICAL_JSON
NEG_JSON_DUPLICATE_KEY
NEG_JSON_CRLF
NEG_JSON_TRAILING_LF
NEG_JSONL_FINAL_LF
NEG_ENCLOSURE_ROUNDTRIP
NEG_CHAIN_GENESIS_WRONG_DOMAIN
NEG_CHAIN_USES_DEPENDENCY_HASH
NEG_CHECKER_DPS_LT_DPS
NEG_CHECKER_FRESH_SIGN_FAIL
NEG_CHECKER_WINDOW_ORDER_MISMATCH
NEG_CHECKER_STACK_MISMATCH
NEG_CHECKER_PREDICTOR_CONTEXT_MISMATCH
NEG_CERTIFIED_WORD_OUTSIDE_ALLOWLIST
```

## 15.10 logical dependency controls

```text
NEG_LOGICAL_REQUIRED_KEY_MISSING
NEG_LOGICAL_UNKNOWN_KEY
NEG_LOGICAL_UNKNOWN_ENTRY_FIELD
NEG_LOGICAL_LEMMA_ID_MISMATCH
NEG_LOGICAL_HASH_MISMATCH
NEG_LOGICAL_ALLOWLIST_ID_MISMATCH
NEG_LOGICAL_ALLOWLIST_CONFIG_BOOLEAN
NEG_LOGICAL_SUPPORTS_CONFIG_SELF_REPORT
NEG_LOGICAL_SUPPORTS_FALSE
NEG_LOGICAL_PAPER_LEMMA_SUBSTITUTION
NEG_LOGICAL_NONCANONICAL_OBJECT
```

## 15.11 config schema controls

```text
NEG_CONFIG_REQUIRED_FIELD_MISSING
NEG_CONFIG_UNKNOWN_TOP_LEVEL_FIELD
NEG_CONFIG_SHA_LENGTH
NEG_CONFIG_SHA_UPPERCASE
NEG_CONFIG_PATH_ABSOLUTE
NEG_CONFIG_PATH_DOTDOT
NEG_CONFIG_PATH_EMPTY_COMPONENT
NEG_CONFIG_PATH_SYMLINK_ESCAPE
NEG_CONFIG_ID_EMPTY
NEG_CONFIG_ID_INVALID_CHARACTER
NEG_CONFIG_ALIAS_RETAINED
NEG_CONFIG_ALIAS_VALUE_MISMATCH
NEG_CONFIG_ENCODING_ID
NEG_CONFIG_R_TILE_ALGORITHM_ID
NEG_CONFIG_LAMBDA_TARGET_DOMAIN
NEG_CONFIG_DELTA_OVERLAP_NONPOSITIVE
NEG_CONFIG_CHECKER_DPS
NEG_CONFIG_COMPLETE_HASH_MISMATCH
```

全controlsはPhase 2またはPhase 3で実走し、期待結果との1:1対応表を成果物に含める。

---

## 16. Phase順序

```text
Phase 1
  design commit
  本書凍結

Phase 2
  計算なしself-test
  controls grammar
  schema
  failure transition

Phase 3
  runner/checker/verifier実装
  chat側静的監査
  AUDITED_SOURCE

Phase 4
  workflow監査
  provenance監査
  observer分離監査

Production run config監査
  lambda_target
  w0
  budgets
  dps
  source SHA
  pilot receipt
  dependency snapshot
  complete config SHA承認

ユーザー承認tag

Actions正本run

chat側全数照合

CERTIFIED_LAMBDA_RANGE宣言
```

GitHub側の自己監査宣言はcandidate報告として扱う。

監査済みheadから無報告差替えがあった場合は、即凍結し、clean環境から再構築する。

---

## 17. 変更記録

### v7からv8

- controlsの自己完結化
- target到達の優先遷移
- stack不変条件とdepthの固定
- predictor contextのactivation時固定
- pilot identityの相互整合gate
- logical dependency schemaのclosed化

### v8からv8.1 — MUST 1

`yes*`によるregenerationを、PRIMARYの`window_origin`が`CONFIG_SEED`または`PARENT_INHERITED`の場合だけに限定した。

`PREDICTOR_HORIZONTAL`および`PREDICTOR_LINEAR`由来のPRIMARYは、同一predictor contextから同一窓を再構築するため、失敗後はregenerationを行わず`SLICE_BOX_FAIL`からsplit判定へ進む。

`NEG_PREDICTOR_PRIMARY_REGENERATION`をcontrolsへ追加した。

### v8からv8.1 — 軽微1

C-G正本pilotの根所在を開区間、

```text
(1/64, 11/256)
```

と明記した。

S7ではその閉包hull、

```text
[1/64, 11/256]
```

を窓包含条件として用いる。

snapshotとのidentity検査はinterval objectの開閉属性等値ではなく、端点対のcanonical bytes等値とした。

### v8からv8.1 — 軽微2

PREP失敗時の、

```text
attempt_evaluations_used
```

をexactly `0`に固定した。

PREP失敗前のkernel evaluationを禁止した。
