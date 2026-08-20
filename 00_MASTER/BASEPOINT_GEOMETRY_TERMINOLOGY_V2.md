# BASEPOINT GEOMETRY TERMINOLOGY V2

- document_id: BASEPOINT_GEOMETRY_TERMINOLOGY_V2
- status: CANONICAL
- date_fixed: 2026-08-18
- supersedes: BASEPOINT_GEOMETRY_TERMINOLOGY_V1
- language: Japanese (normative) / English (normative for English usage)
- scope: 本文書は用語の正典定義のみを定める。数学的主張の認証は行わない。
- revision_policy: V1 はバイト凍結のまま履歴として保存する。本文書 V2 も確定後はバイト凍結とし、以後の改訂は V3 以降の新文書として発行する。

---

## 1. 基点幾何（Basepoint Geometry）— 確定

### 看板層

基点幾何とは、基点を幾何学的変数として扱い、基点に依存する汎関数とその停留構造・構造変化を研究対象とする枠組みである。

### 論文層

基点空間 \(P\)、パラメータ空間 \(\Lambda\)、および必要な正則性をもつ幾何学的汎関数の族

\[
E:P\times\Lambda\to\mathbb{R},\qquad E_\lambda(p)=E(p,\lambda)
\]

を基本対象とし、停留集合

\[
\operatorname{Crit}(E_\lambda)
=\{\,p\in P:d_pE_\lambda=0\,\}
\]

の幾何学的構造とそのパラメータ依存を研究する。

停留条件は計量に依存しない微分 \(d_pE_\lambda=0\) で定式化する。\(P\subset\mathbb{R}^n\) のように標準計量がある場合には

\[
d_pE_\lambda=0\iff \nabla_pE_\lambda=0
\]

である。

### English

Basepoint Geometry is the study of a basepoint space \(P\), a parameter space \(\Lambda\), and a sufficiently regular family of geometric functionals
\[
E:P\times\Lambda\to\mathbb{R},
\]
with emphasis on the geometric structure of the stationary sets
\[
\operatorname{Crit}(E_\lambda)=\{p\in P:d_pE_\lambda=0\}
\]
and their dependence on the parameter. Stationarity is formulated by the metric-independent differential \(d_pE_\lambda\); when a standard metric is available, this is equivalent to \(\nabla_pE_\lambda=0\).

---

## 2. 基点分岐（Basepoint Bifurcation）— 確定

### 定義

基点分岐とは、基点 \(p\) を変数とする幾何学的汎関数の族 \(E_\lambda\) において、パラメータ \(\lambda\) の変化に伴い、停留集合

\[
\operatorname{Crit}(E_\lambda)
=\{\,p:d_pE_\lambda=0\,\}
\]

の**ラベル付き幾何学的構造**が変化する現象をいう。

ここで構造には、必要に応じて、停留集合の連結成分数・次元・局所位相、孤立停留点の個数（有限の場合）、非退化停留点のモース指数、Morse–Bott 成分の法方向指数、退化度（nullity）、および共通の対称群 \(G\) が \(P\) に作用し各 \(E_\lambda\) が \(G\)-不変である場合の等方型（\(G\)-軌道型）を含む。

停留基点の位置は分岐の判定条件に含めない。位置は一般にパラメータとともに連続的に移動するため、それ自体は分岐を意味しない。位置は基点分岐図の記述対象とする（§3）。

### 論文層（分岐点の判定）

全停留集合

\[
\mathcal S
=\{\,(\lambda,p)\in\Lambda\times P:d_pE_\lambda=0\,\}
\]

と射影

\[
\pi:\mathcal S\to\Lambda,\qquad \pi(\lambda,p)=\lambda
\]

を考える。

\(\lambda_0\in\Lambda\) の近傍で、上記ラベルを保存する意味で \(\pi\) がパラメータ付きに局所自明化できないとき、\(\lambda_0\) を**基点分岐点（basepoint bifurcation point）**と呼ぶ。

したがって、単なる停留基点の連続移動は、ラベル付き停留集合が局所自明である限り、基点分岐ではない。

### 補足

- \(p\in\operatorname{Crit}(E_\lambda)\) では Hessian は \(T_pP\) 上の対称双線形形式として内在的に定義される。計算に接続や計量を用いても、停留点上の Hessian 自体はその選択に依存しない。
- 非退化孤立停留点では通常のモース指数を用いる。Morse–Bott 成分では法方向の指数を用いる。より一般の退化点では nullity および必要に応じて Hessian の符号型を記録する。
- 静的理論では「安定性」を独立ラベルとして定義の中心に置かず、Hessian の型・モース指数等を用いる。選択した計量に対する負勾配流を導入した後、非退化平衡点ではモース指数が不安定次元に一致する（§4）。
- 等方型を比較する場合は、原則としてパラメータ族全体に共通する群 \(G\) の作用を固定する。対称群そのものがパラメータとともに変化する場合は、共通の周囲群への埋込み等を別途指定して比較する。

### English

Let \(E_\lambda(p)\) be a family of geometric functionals of a basepoint \(p\). A **basepoint bifurcation** is a change, as \(\lambda\) varies, in the labelled geometric structure of
\[
\operatorname{Crit}(E_\lambda)=\{p:d_pE_\lambda=0\}.
\]

The relevant structure may include, as appropriate, the number of connected components, dimension and local topology of the stationary set, the number of isolated stationary points when finite, Morse indices of nondegenerate stationary points, normal Morse indices of Morse–Bott components, nullity at degenerate points, and—when a common symmetry group \(G\) acts on \(P\) and each \(E_\lambda\) is \(G\)-invariant—isotropy types.

Let
\[
\mathcal S=\{(\lambda,p)\in\Lambda\times P:d_pE_\lambda=0\},
\qquad
\pi:\mathcal S\to\Lambda,\ \pi(\lambda,p)=\lambda.
\]
A parameter value \(\lambda_0\) is a **basepoint bifurcation point** if, near \(\lambda_0\), the projection \(\pi\) admits no parameterized local trivialization preserving the prescribed labels. Continuous motion of stationary basepoints alone does not constitute a basepoint bifurcation.

---

## 3. 基点分岐図（Basepoint Bifurcation Diagram）— 確定

### 定義

基点分岐図とは、全停留集合

\[
\mathcal S
=\{\,(\lambda,p)\in\Lambda\times P:d_pE_\lambda=0\,\}
\]

を射影 \(\pi:\mathcal S\to\Lambda\) とともにパラメータ \(\lambda\) に対して表示し、その停留構造に、定義可能な範囲で次の情報を付した図である。

- 停留集合の連結成分・次元・局所構造
- 非退化孤立停留点のモース指数
- Morse–Bott 成分の法方向指数
- 退化点の nullity（および必要に応じて Hessian の符号型）
- \(G\)-同変の場合の等方型

非退化停留点 \((\lambda_0,p_0)\) では、\(p\)-方向 Hessian が非退化であることにより陰関数定理が適用でき、局所的に

\[
p=p_i(\lambda)
\]

という枝として表される。したがって枝は \(\mathcal S\) の局所切断であって、定義の本体ではない。

停留基点の位置の移動は分岐図には記録されるが、それだけでは基点分岐を意味しない。

### English

The **basepoint bifurcation diagram** is the total stationary set
\[
\mathcal S=\{(\lambda,p)\in\Lambda\times P:d_pE_\lambda=0\},
\]
displayed relative to the projection \(\pi:\mathcal S\to\Lambda\), together with labels describing, where applicable, connected components, dimensions and local structure of stationary sets, Morse indices of nondegenerate isolated stationary points, normal indices of Morse–Bott components, nullity at degenerate points, and isotropy types in the equivariant case.

At a nondegenerate stationary point, the implicit function theorem gives a local branch
\[
p=p_i(\lambda).
\]
Such branches are local sections of \(\mathcal S\), not the primary object of the definition. Motion of stationary basepoints is recorded in the diagram but does not by itself constitute a basepoint bifurcation.

---

## 4. 基点力学（Basepoint Dynamics）— 予約定義

### 予約定義（スコープ宣言）

基点力学とは、基点空間 \(P\) に計量を選択し、基点依存汎関数 \(E_\lambda\) から定まる負勾配流

\[
\dot p=-\nabla_pE_\lambda(p)
\]

およびそれに付随する力学的構造を研究する段階をいう。

静的理論とは次の対応で接続する。

- 停留基点 \(\leftrightarrow\) 平衡点
- 非退化平衡点における Hessian / モース指数 \(\leftrightarrow\) 線形化の符号構造 / 不安定次元
- 基点分岐 \(\leftrightarrow\) 平衡点構造・相図の再編成

吸引域、安定・不安定多様体、セパラトリクス、遷移などは後段で扱う。

### 正式化条件

本項は正式な理論定義ではなく予約語である。正式化は、基点力学に固有の最初の定理が成立した時点で行う。名称を実体に先行させない。

### English (reserved)

**Basepoint Dynamics** (reserved term): the study of the negative gradient flow
\[
\dot p=-\nabla_pE_\lambda(p)
\]
determined by \(E_\lambda\) and a chosen metric on the basepoint space, together with its associated dynamical structures. At a nondegenerate equilibrium, the Morse index equals the dimension of the unstable subspace of the negative gradient flow. Formalization is deferred until the first theorem specific to Basepoint Dynamics is established.

---

## 5. 分業と境界（規律）

1. 静的理論（基点幾何・基点分岐・基点分岐図）は計量フリーで定式化する。計量の導入は基点力学の開始点であり、これが静的理論と動的理論の境界である。
2. 分岐の本体はラベル付き停留集合の構造変化であり、位置は基点分岐図の記述対象である。単なる位置移動は分岐ではない。
3. 孤立停留点だけを前提としない。停留円・停留多様体・Morse–Bott 型などの非離散停留集合も、\(\mathcal S\subset\Lambda\times P\) の枠組みで扱う。
4. 等方型の比較には共通の群作用を明示する。対称群自体が変化する場合は比較のための共通枠組みを別途指定する。

---

## 6. 命名規律

1. 三層構造：対象は記述名（錐体積重み付き動径–法線角汎関数 \(E_K(p)\) 等）、現象は基点分岐、上位概念は基点幾何。
2. 論文では分野名を主張しない。基点幾何の名称は看板・連載・展望節に限定し、論文本文では *basepoint geometry* を記述的に用いる。体系が成立した時点で正式に名乗る。
3. 英語表記は代数トポロジーの慣行に合わせ **basepoint** を一語とする（Basepoint Geometry / basepoint bifurcation）。
4. 代数トポロジーとの対置（導入文の型）：
   > In algebraic topology, a basepoint is often auxiliary data used to anchor invariants. Here, by contrast, the basepoint itself is a variable whose position generates geometric structure and bifurcation.
5. 衝突回避規律：既存分野で確立した意味をもつ語と衝突する名称は採用しない。*dual phase* および *dual topology* は本体系の正式名称としては使用しない。*bifurcation diagram* は標準的な一般語であり、*basepoint bifurcation diagram* と修飾して対象を特定する。

---

## 7. V2 における修正点

V1 のバイト凍結方針を維持するため、V1 を変更せず、本 V2 を新しい正典として発行する。

主な修正は次のとおり。

1. 基点分岐の本体を「個数等の列挙」ではなく「ラベル付き停留集合の幾何学的構造変化」として定義し、停留円・停留多様体・Morse–Bott 型を明示的に包含した。
2. 分岐点の判定を、全停留集合 \(\mathcal S\) の射影 \(\pi:\mathcal S\to\Lambda\) のラベル保存局所自明性として明示した。
3. 「安定性はモース指数で定義する」という表現を撤回し、静的理論では Hessian / モース指数を用い、選択した計量による負勾配流導入後にのみ力学的安定性へ接続する形に修正した。
4. 非退化孤立点、Morse–Bott 成分、一般の退化点を区別し、モース指数・法方向指数・nullity の使い分けを明示した。
5. 等方型の比較には共通の群 \(G\) の作用を原則として固定することを明示した。
6. 基点分岐図の枝 \(p_i(\lambda)\) は、非退化部分で陰関数定理により得られる局所切断であり、\(\mathcal S\) が本体であることを明確化した。

---

## 8. 確定履歴

- 2026-08-16: 現象名「基点分岐 / basepoint bifurcation」および上位概念「基点幾何 / Basepoint Geometry」を確定。三層構造・basepoint 一語表記を確定。
- 2026-08-18: V1 を正典化。
- 2026-08-18: V1 のバイト凍結方針に従い、非離散停留集合・Morse–Bott 型・局所自明化・静的／動的安定性の境界・共通群作用を明確化した V2 を新しい正典として確定。
