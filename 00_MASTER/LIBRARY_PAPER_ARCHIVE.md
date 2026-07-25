# Library Paper Archive

ChatGPT File Library で確認した立体関連論文の整理台帳。体系番号と投稿順序は別管理とする。

## 各論 I　体系列

| 体系 | 対象 | 論文・資料 | 状態 | GitHub 配置先 |
|---|---|---|---|---|
| 1-1 | 球体 | `Kakuron_I_1_1_Sphere.pdf` / `.tex` / source ZIP | 完全解析分類・収録済み | `01_KAKURON_I/1_楕円体系列/1-1_球体/` |
| 1-2 | 長球 | `furuta_prolate_spheroid_bifurcation_manuscript.pdf` | 局所分岐認証済み・大域分類を加えて改稿中 | `01_KAKURON_I/1_楕円体系列/1-2_長球/` |
| 1-3 | 三軸楕円体 | `002_Furuta_Triaxial_Manuscript.pdf` | 局所 unfolding 認証済み・投稿準備 | `01_KAKURON_I/1_楕円体系列/1-3_三軸楕円体/` |
| 2-2 | 正六面体 | `Furuta005_Manuscript.pdf` | Experimental Mathematics 投稿済み | `01_KAKURON_I/2_柱体系列/2-2_正六面体/` |
| 3-3 | 正四面体 | `006_furuta_regular_tetrahedron_manuscript_v0_3.pdf` | Experimental Mathematics 投稿済み | `01_KAKURON_I/3_錐体系列/3-3_正四面体/` |
| 3-4 | 正四角錐 | `008_square_pyramid_verification_report.md` | 検証中 | `01_KAKURON_I/3_錐体系列/3-4_正四角錐/` |
| 3-5 | 双正四面体 | 正三角形6面の三角双錐に関する認証資料 | 検証完了・単独論文準備 | `01_KAKURON_I/3_錐体系列/3-5_双正四面体/` |
| 4-1 | 丸めた D3 対称双円錐 | `furuta_bicone_D3_manuscript.pdf` | Experimental Mathematics 投稿済み | `01_KAKURON_I/4_混成体系列/4-1_丸めた_D3_対称双円錐/` |

## 各論 II　複合研究

| 研究 | 論文・資料 | 状態 | GitHub 配置先 |
|---|---|---|---|
| 円柱–円錐台統一族 | `furuta_circular_frustum_cusp.pdf` / `.tex` | 投稿済み・本文差し替え依頼中 | `02_KAKURON_II/1_円柱_円錐台統一族/` |
| 球体–正六面体比較 | `Furuta005_Manuscript.pdf` | Experimental Mathematics 投稿済み | `02_KAKURON_II/2_球体_正六面体比較/` |

## 取込規則

1. 完成稿は `manuscript.pdf`、原稿は `manuscript.tex` に統一する。
2. 投稿用ファイル名は `submission/` に原名のまま保存する。
3. 認証コード・JSON・実行記録は `supplement/` に置く。
4. SHA-256 manifest がある場合は改変せず同梱する。
5. 旧版は `archive/` に隔離し、最新版と混在させない。

## 現在の制約

このコミットでは配置先、論文情報、状態、原ファイル名を確定した。File Library の PDF・ZIP バイナリは GitHub Contents API から直接転送できないため、バイナリ本体は各フォルダの `README.md` に記した原名で後続取込する。