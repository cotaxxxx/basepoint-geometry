# 三軸楕円体の族：停留点の地図（診断用）

2026-11-20 ／ **DIAGNOSTIC_ONLY / NOT_EVIDENCE** ／ 数値はすべて非区間（倍精度浮動小数点）

指示書「体積を保つ三軸楕円体の族：停留点の構造の定式化と、最初の地図」への回答である。
公式の台帳、証拠の原本、STATE.md、main には関係しない。この作業専用の branch の、新しいディレクトリだけに置いている。

| ファイル | 内容 |
|---|---|
| `REPORT.md` | 報告書（結論、定式化、地図、分岐集合の分類、証明、証明の設計、Judge への判断点） |
| `PLAN.md`、`PLAN.sha256` | 実行前に固定した数値計画と、その SHA-256 |
| `code/` | 核（C）、census、各 Run、検査、図のコード |
| `out/` | 出力（JSON、JSONL、CSV、ログ、`tables.md`） |
| `fig/` | 図 1〜4 |
| `reproduce.sh` | 再現の手順（4 コアで約 2 時間） |
| `SHA256SUMS.txt` | 全ファイルの SHA-256 |

読む順番は `REPORT.md` の §0 → 図 1（`fig/fig1_map_st.png`）→ 図 2（`fig/fig2_master_plane.png`）を勧める。
