# 基点幾何の定義と計算法

論文付属資料 A / Basepoint Geometry  
日本語版 第1版 改訂1 / 2026年11月20日

基点を幾何学的変数として扱う枠組み、停留集合の読み方、角度エネルギーの定義と計算法をまとめた付属資料です。一般の枠組みと、回転楕円体・三軸楕円体で用いるモデルを順に記載しています。

## 収録ファイル

| ファイル | 内容 |
|---|---|
| [Basepoint_Geometry_Supplement_v1_20261120.pdf](Basepoint_Geometry_Supplement_v1_20261120.pdf) | 閲覧用PDF、全13ページ |
| [Basepoint_Geometry_Supplement_v1_20261120.docx](Basepoint_Geometry_Supplement_v1_20261120.docx) | 編集用Word、数式は編集可能なOffice Math |
| [SHA256SUMS.txt](SHA256SUMS.txt) | PDF・Word・本READMEのSHA-256 |

ファイル名の `v1` は第1版を表します。本文の版表示と末尾の改訂履歴は「第1版 改訂1」です。

## 改訂1の内容

- **§10**：球での厳密な動径単調性と、中心以外に内部停留点がないことへの参照を追加。各論 I 1-1「球体」の定理5.1・定理7.1を参照します。
- **§11**：本研究が採用する境界条件（A）を明記。内部から延長した全勾配のトレースの零を扱い、境界接線方向の停留とは区別します。
- **§12・手順3**：GeoEncloseReaderを用いて台帳の選んだ葉を別の核・実装から包み直す独立照合を明記。
- **§13**：球の原稿を文献 [U4] に追加し、改訂履歴を更新。

## 確認記録

- WordからPDFを再生成し、全13ページであることを確認。
- 変更ページ（1、10、11、12、13ページ）の表示を確認。
- 式(1)〜(33)のOffice Mathデータが第1版と同一であることを照合。
- 登録対象のPDF・WordのSHA-256を、作成時の確認記録と照合。

本資料は定義・計算法・利用手順の説明です。個別の形状族の大域分類は、対応する論文の定理と検証資料を参照してください。

## 球の参照原稿

Katsushi Furuta, *Geometric Dual Topology of the Sphere: A Complete Analytic Classification for a Cone-Volume-Weighted Radial-Normal Angle Functional*. 各論 I 1-1「球体」、研究原稿、2026年7月。

- §5、Theorem 5.1: Positive-integral derivative.
- §7、Theorem 7.1: Unique stationary point and unique global minimum.
- 原稿の動径変数 `a` は、本付属資料の `r` に対応します。
- [固定版の原稿](https://github.com/cotaxxxx/basepoint-geometry/blob/abf704b8701f3da8eb41d8a99408570a413b2214/01_KAKURON_I/1_%E6%A5%95%E5%86%86%E4%BD%93%E7%B3%BB%E5%88%97/1-1_%E7%90%83%E4%BD%93/Kakuron_I_1_1_Sphere.tex)

## 同一性の確認

このフォルダで次を実行します。

```sh
sha256sum -c SHA256SUMS.txt
```

SHA-256はファイルの同一性を確認する値です。数学的な妥当性の確認とは別に扱います。

