# Paper Map

更新日：2026-09-04

## 最初に参照する管理文書

- 研究全体の進捗・投稿順序：`00_MASTER/STATUS.md`
- 認証済み結果と証拠状態：`00_MASTER/CERTIFIED_RESULTS.md`
- File Library 原稿台帳：`00_MASTER/LIBRARY_PAPER_ARCHIVE.md`
- 体系配置：本ファイル

## 原点研究：4-π研究

- 入口：`00_4_MINUS_PI_RESEARCH/README.md`
- 中心定理と厳密導出：`00_4_MINUS_PI_RESEARCH/THEOREM_NOTE_JA.md`
- 先行研究との接点：`00_4_MINUS_PI_RESEARCH/PRIOR_WORK.md`
- 一般化・論文化計画：`00_4_MINUS_PI_RESEARCH/RESEARCH_PROGRAM.md`

4-π研究は、正方形と内接円の面積差 `4-π` が動径–法線角エネルギーと一致する理由を扱う。総論・各論の上流に位置し、幾何双対位相の二次元原型を記録する。

## 双対位相欠損研究

- 入口：`00_DUAL_PHASE_DEFECT_RESEARCH/README.md`
- 原稿・証明状態：`00_DUAL_PHASE_DEFECT_RESEARCH/MANUSCRIPT_STATUS.md`
- 成果物ハッシュ：`00_DUAL_PHASE_DEFECT_RESEARCH/SHA256SUMS.txt`

双対位相欠損研究は、回転相似自己極性からの連続的なずれを平面凸体上で測り、長方形族の臨界位相分岐を解析する。4-π研究の直後、総論・各論の前に置く。

## 総論

- 概要：`01_GENERAL_THEORY/OVERVIEW_JA.md`
- 目次：`01_GENERAL_THEORY/CONTENTS_JA.md`

総論には、一般定義、正則性、境界理論、対称群、極双対、Morse／Morse–Bott 理論、外部延長、等変 Lyapunov–Schmidt 縮約、標準分類表および認証法を置く。具体的な係数符号・分岐枝・形体別分類は各論へ置く。

## 各論 I　体系列

- 全体目次：`01_KAKURON_I/CONTENTS_JA.md`

### 1　楕円体系列

- 1-1　球体 — `01_KAKURON_I/1_楕円体系列/1-1_球体/`
- 1-2　長球 — `01_KAKURON_I/1_楕円体系列/1-2_長球/`
  - 正典原稿：`01_KAKURON_I/1_楕円体系列/1-2_長球/manuscript/manuscript.tex`
  - 旧 DOCX/PDF は履歴資料として凍結し、今後の本文更新対象としない。
  - 管理名「長球」は既存ディレクトリ名として維持し、原稿正式表記は「扁長回転楕円体」とする。
- 1-3　三軸楕円体 — `01_KAKURON_I/1_楕円体系列/1-3_三軸楕円体/`

### 2　柱体系列

- 2-1　円柱 — 単体分類資料を配置予定。円柱–円錐台統一論文は各論 II に配置
- 2-2　正六面体 — `01_KAKURON_I/2_柱体系列/2-2_正六面体/`

### 3　錐体系列

- 3-1　円錐 — 単体分類資料を配置予定
- 3-2　円錐台 — 単体分類資料を配置予定。円柱–円錐台統一論文は各論 II に配置
- 3-3　正四面体 — `01_KAKURON_I/3_錐体系列/3-3_正四面体/`
- 3-4　正四角錐 — `01_KAKURON_I/3_錐体系列/3-4_正四角錐/`
- 3-5　双正四面体 — `01_KAKURON_I/3_錐体系列/3-5_双正四面体/`

### 4　混成体系列

- 4-1　丸めた `D_3` 対称双円錐 — `01_KAKURON_I/4_混成体系列/4-1_丸めた_D3_対称双円錐/`

## 各論 II　複合研究

- 全体目次：`02_KAKURON_II/CONTENTS_JA.md`

- II-1　円柱–円錐台統一族 — `02_KAKURON_II/1_円柱_円錐台統一族/`
- II-2　球体–正六面体比較 — `02_KAKURON_II/2_球体_正六面体比較/`
- II-3　立方体から球への補間 — 配置予定
- II-4　連続対称性から有限対称性への分裂 — 目次段階
- II-5　境界侵入・Maxwell 転移 — 目次段階
- II-6　極双対と横断的不変量 — 目次段階

## 配置規則

1. 4-π研究は研究体系の原点として最上流に置く。
2. 双対位相欠損研究は4-π研究の直後、総論・各論の上流に置く。
3. 単一立体または同一構造を保つ体族の分類は各論 I に置く。
4. 複数の形状系列・対称群・分岐機構を横断する研究は各論 II に置く。
5. 体系番号と投稿順序は別に管理し、投稿順序は `STATUS.md` に記録する。
6. 完成稿は `manuscript.pdf`、原稿は `manuscript.tex` に統一する。
7. 投稿時の原名ファイルは `submission/` に保存する。
8. 認証コード・JSON・実行記録・SHA-256 manifest は `supplement/` に保存する。
9. 旧版は `archive/` に隔離し、最新版と混在させない。
