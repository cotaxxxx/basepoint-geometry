# BASEPOINT GEOMETRY TERMINOLOGY V3

- document_id: BASEPOINT_GEOMETRY_TERMINOLOGY_V3
- status: CANONICAL
- date_fixed: 2026-08-19
- supersedes: BASEPOINT_GEOMETRY_TERMINOLOGY_V2
- language: Japanese (normative) / English (normative for English usage)
- scope: 本文書は、基点幾何プロジェクトの研究対象・用語階層・ミッション・発展方針の正典を定める。個別の数学的主張の真偽や認証結果は、各論文・証明・certificate に委ねる。
- revision_policy: V1 および V2 はバイト凍結のまま履歴として保存する。本文書 V3 も確定後はバイト凍結とし、以後の改訂は V4 以降の新文書として発行する。

---

## 1. 公式ミッション文 — 確定

### 一般理論版

> **基点幾何は、対象上の基点に関する変分から停留点構造を抽出し、その構造と形状変形による変化を研究する。**

### 立体プロジェクト版

> **基点幾何は、立体内部の基点変動から停留点構造を抽出し、その構造と形状変動による変化を研究する。**

一般理論では「基点に関する変分」と「形状変形」を用い、立体を対象とする説明・連載・プロジェクト文脈では「基点変動」と「形状変動」を用いてよい。

---

## 2. 研究の主役 — 停留点構造

V3 では、研究の主役を **基点そのものではなく、基点を変数として抽出される停留点構造** と定める。

基点は探索変数・観測位置であり、成果物は停留点構造である。

対象を \(K\)、基点空間を \(P_K\)、基点依存汎関数を \(E_K:P_K\to\mathbb R\) とすると、基本成果物は

\[
\mathcal S_E(K)
:=\operatorname{Crit}(E_K)
=\{p\in P_K:d_pE_K=0\}
\]

である。

標準計量がある場合には

\[
d_pE_K=0\iff \nabla_pE_K=0.
\]

### 停留点構造に含め得る情報

必要に応じて、次を停留点構造の記述に含める。

- 停留集合の連結成分数
- 孤立停留点の個数
- 停留円・停留軌道・停留多様体など非離散成分の有無
- 各成分の次元・局所位相
- 基点空間内での配置
- 対称群がある場合の軌道型・等方型
- 非退化停留点の Morse index
- Morse–Bott 成分の法方向 index
- Hessian の符号型・nullity
- 形状変形に伴う生成・消滅・合流・分裂などの構造変化

位置は停留点構造の記述・比較には含め得るが、単なる連続的な位置移動だけを分岐とは呼ばない。

---

## 3. 方法・操作・成果物・変化の階層 — 確定

本プロジェクトの用語階層を次のように固定する。

1. **基点幾何（Basepoint Geometry）** = 研究の枠組み・方法
2. **基点変動 / 基点に関する変分（basepoint variation）** = 停留点構造を抽出する機構
3. **停留点構造（stationary-point structure / stationary structure）** = 主要成果物・主要研究対象
4. **形状変動 / 形状変形（shape variation / shape deformation）** = 停留点構造の変化を駆動する外部パラメータ
5. **基点分岐（basepoint bifurcation）** = 形状変形等により停留点構造が質的に変わる現象
6. **基点分岐図（basepoint bifurcation diagram）** = その構造変化をパラメータとともに記述する図

したがって、**基点分岐は研究全体の主役ではなく、停留点構造の変化として現れる重要現象の一つ**である。

---

## 4. 二つの変動の分離 — 確定

基点変動と形状変動を混同しない。

### 4.1 基点変動

対象 \(K\) と汎関数の型を固定し、基点 \(p\) を動かす。

\[
p\mapsto E_K(p)
\]

その一次変化が全方向で消える位置

\[
d_pE_K=0
\]

を抽出する。この操作は **停留点構造を見つけるための探査** である。

### 4.2 形状変動

形状族 \(K_\lambda\) を動かす。

\[
\lambda\mapsto K_\lambda
\]

各形状に対して

\[
\mathcal S_E(K_\lambda)=\operatorname{Crit}(E_{K_\lambda})
\]

を比較し、停留点構造の変化を調べる。

### 4.3 全停留集合

二つの変数を同時に扱うときは

\[
\mathcal S
=\{(\lambda,p)\in\Lambda\times P:d_pE_\lambda=0\}
\]

を基本対象とする。

ここで、

- \(p\)-方向 = 基点変動による構造抽出
- \(\lambda\)-方向 = 形状変動による構造変化

である。

---

## 5. レンズ原理 — 　停留点構造は \((K,E)\) に依存する

停留点構造は一般に形状 \(K\) 単独の関数ではない。どの基点依存汎関数 \(E\) を選ぶかによって、抽出される構造が変わる。

したがって、本研究の最短表現を

\[
\boxed{(K,E)\longmapsto \operatorname{Crit}(E_K)}
\]

とする。

汎関数 \(E\) は、対象 \(K\) のどの幾何学的側面を見るかを決める **レンズ** とみなす。

同一の対象 \(K\) に対して異なる汎関数を用いれば、

\[
(K,E_1)\mapsto \mathcal S_{E_1}(K),
\qquad
(K,E_2)\mapsto \mathcal S_{E_2}(K)
\]

という複数の停留点構造を比較できる。

この「レンズ違いの停留点構造比較」は将来の発展方向として登録するが、一般的な識別能力や完全性は現時点では定理として主張しない。

---

## 6. 停留点構造を形状の指紋として扱う方向 — 発展方針

停留点構造

\[
\mathcal S_E(K)=\operatorname{Crit}(E_K)
\]

およびそのラベル情報を、形状比較のための **stationary-structure fingerprint（停留構造指紋）** として利用する方向を正式な発展候補とする。

候補となる特徴には、停留点数、成分次元、軌道型、配置、Morse index、nullity、Hessian 型、分岐情報等を含む。

### 状態区分

- **確定**: 停留点構造は基点幾何の主要成果物である。
- **確定**: 形状変形による停留点構造の変化を研究対象とする。
- **発展仮説**: 停留点構造を形状の指紋として比較・分類に利用できる可能性がある。
- **発展仮説**: 3D shape analysis、AI、CAD、ゲーム等への応用可能性を検証する。
- **未主張**: 停留点構造だけで任意の立体を一意に識別できるとは現時点では主張しない。

---

## 7. 中心理論との位置づけ — 研究方針

従来の「良い中心を一つ選ぶ」問題と、本プロジェクトの「停留集合全体を調べる」問題を区別する。

本プロジェクトでは、単一の代表点の選択に限定せず、

\[
\operatorname{Crit}(E_K)
\]

全体の幾何学的構造を対象とする。

研究説明の基本対比として、次を採用する。

> **中心の理論は点を選ぶ。基点幾何は停留構造を調べる。**

ただし、これは研究上の位置づけを示す簡潔な表現であり、先行研究全体に停留軌道が存在しないことや「数学全体で世界初」であることを意味しない。

---

## 8. 第1論文の位置づけ — プロジェクト上の役割

prolate spheroid を扱う第1論文は、基点幾何における停留点構造の最初の代表例として位置づける。

特に、非中心の停留円 / \(O(2)\) 停留軌道と、その形状パラメータ変化に伴う局所分岐は、

- 孤立した「中心」だけでなく非離散の停留集合を扱うこと
- 基点空間側の停留構造と、形状パラメータ側の分岐を分離して扱うこと

を具体的に示す例として扱う。

個別定理の成立範囲・認証値・一意性等は、第1論文本文と対応する certificate を正本とし、本用語正典では再認証しない。

---

## 9. 命名規律 — V3

1. 上位概念は **基点幾何 / Basepoint Geometry** とする。
2. 主成果物は **停留点構造 / stationary-point structure** とする。
3. **基点分岐 / basepoint bifurcation** は停留点構造変化の現象名として残すが、研究全体の主役とはしない。
4. **幾何双対位相 / Geometric Dual Topology** は、本プロジェクトの現行名称・上位概念として使用しない。過去資料中の表記は履歴としてのみ扱う。
5. 論文本文では、必要に応じて記述的な用語を優先し、分野名の確立を個別論文の数学的主張に先行させない。
6. 新規性の主張と発展性の主張を分離する。特に「世界初」等の優先権主張は、独立した先行研究監査なしには正典化しない。

---

## 10. 英語の基本表現 — 確定

### Basepoint Geometry

> **Basepoint Geometry studies stationary-point structures extracted by variation of a basepoint, together with their changes under deformation of the underlying geometric object.**

### Core map

\[
(K,E)\longmapsto \operatorname{Crit}(E_K).
\]

### Roles

- **Basepoint Geometry**: framework
- **basepoint variation**: extraction mechanism
- **stationary-point structure / stationary structure**: primary object and output
- **shape deformation**: driver of structural change
- **basepoint bifurcation**: qualitative change of stationary-point structure

### Short contrast

> **Center theories select a point; Basepoint Geometry studies the stationary structure.**

---

## 11. 確定履歴

### 2026-08-18 — V2

- 基点幾何、基点分岐、基点分岐図、基点力学（予約）の用語階層を確定。
- 全停留集合 \(\mathcal S\subset\Lambda\times P\) と射影による分岐の定式化を登録。
- 単なる停留基点の位置移動と分岐を分離。

### 2026-08-19 — V3

- 研究の主役を **停留点構造** と明示。
- **基点幾何 = 方法・枠組み、基点変動 = 抽出機構、停留点構造 = 成果物、形状変動 = 構造変化の駆動、分岐 = 構造変化の現象** という階層を確定。
- 公式ミッション文を確定。
- 停留点構造が一般に \(K\) 単独ではなく **\((K,E)\)** に依存する「レンズ原理」を登録。
- 最短表現 **\((K,E)\mapsto\operatorname{Crit}(E_K)\)** を登録。
- 停留点構造を形状の指紋として比較する方向を発展仮説として登録。
- 基点分岐を主役から、停留点構造変化の一現象へ位置づけ直した。
- **幾何双対位相 / Geometric Dual Topology** を現行プロジェクト名・上位概念として使用しないことを確定。

---

## 12. 一行要約

> **方法は基点幾何、操作は基点変動、成果物は停留点構造、形状変動がその構造を変え、分岐はその変化として現れる。**
