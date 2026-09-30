#!/usr/bin/env bash
set -euo pipefail
# DIAGNOSTIC / NOT_EVIDENCE. G7 wrapper. Formal RUN_DIR is forbidden.
: "${OUT_DIR:?absolute diagnostic OUT_DIR required}"
: "${CANDIDATE:?candidate required}"
: "${SET_ID:?set id required}"
case "$OUT_DIR" in /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_candidate_comparison/*) ;; *) echo 'INVALID OUTSIDE_DIAGNOSTIC_ROOT' >&2; exit 2;; esac
if [[ -e "$OUT_DIR" ]]; then echo 'INVALID OUT_DIR_EXISTS' >&2; exit 2; fi
mkdir -p "$OUT_DIR"
LOG="$OUT_DIR/run.log"; MAN="$OUT_DIR/g7_manifest.txt"; START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
{
 echo 'label=DIAGNOSTIC / NOT_EVIDENCE'; echo "host=$(hostname)"; echo "utc_start=$START"; echo "pid=$$"; echo "candidate=$CANDIDATE"; echo "set_id=$SET_ID"; echo "workers=${WORKERS:-10}"; echo "driver=$(realpath tools/d_ob_p2/candidate_comparison_driver.py)"; sha256sum tools/d_ob_p2/candidate_comparison_driver.py tools/d_ob_p2/candidate_comparison_config.py tools/d_ob_p2/d_ob_p2_producer_c_regular_diagnostic.py tools/d_ob_p2/independent_H_sign_N7_result.tsv;
} > "$MAN"
set +e
/home/daybreak/.pyenv/versions/3.11.16/bin/python tools/d_ob_p2/candidate_comparison_driver.py "$@" --candidate "$CANDIDATE" --set-id "$SET_ID" --out "$OUT_DIR/result.tsv" --candidate "$CANDIDATE" --set-id "$SET_ID" --out "$OUT_DIR/result.tsv" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e
echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$MAN"; echo "actual_exit_code=$RC" >> "$MAN"; sha256sum "$LOG" >> "$MAN"
exit "$RC"
