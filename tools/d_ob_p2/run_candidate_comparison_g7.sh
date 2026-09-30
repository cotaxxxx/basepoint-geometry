#!/usr/bin/env bash
set -euo pipefail
# DIAGNOSTIC / NOT_EVIDENCE. G7 wrapper. Formal RUN_DIR is forbidden.
: "${OUT_DIR:?absolute diagnostic OUT_DIR required}"
: "${CANDIDATE:?candidate required}"
: "${SET_ID:?set id required}"
: "${BASE_PRODUCER:?absolute pinned base producer required}"
case "$OUT_DIR" in /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_candidate_comparison/*) ;; *) echo 'INVALID OUTSIDE_DIAGNOSTIC_ROOT' >&2; exit 2;; esac
[[ "$BASE_PRODUCER" = /* ]] || { echo 'INVALID BASE_PRODUCER_NOT_ABSOLUTE' >&2; exit 2; }
if [[ -e "$OUT_DIR" ]]; then echo 'INVALID OUT_DIR_EXISTS' >&2; exit 2; fi
for arg in "$@"; do
 case "$arg" in --candidate|--candidate=*|--set-id|--set-id=*|--out|--out=*|--config|--config=*|--base-producer|--base-producer=*|--derived-producer|--derived-producer=*|--c1|--c1=*|--c2|--c2=*|--c3|--c3=*|--c4|--c4=*|--c4j|--c4j=*|--c5|--c5=*) echo 'INVALID RESERVED_DRIVER_ARG' >&2; exit 2;; esac
done
mkdir -p "$OUT_DIR"
LOG="$OUT_DIR/run.log"; MAN="$OUT_DIR/g7_manifest.txt"; START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
FILES=(tools/d_ob_p2/candidate_comparison_driver.py tools/d_ob_p2/candidate_comparison_config.py tools/d_ob_p2/d_ob_p2_producer_c_regular_diagnostic.py tools/d_ob_p2/independent_H_sign_N7_result.tsv tools/d_ob_p2/results_192.tsv tools/d_ob_p2/phase0_points.tsv tools/d_ob_p2/P003_lambda251.tsv tools/d_ob_p2/P003_independent_J_lambda251.tsv tools/d_ob_p2/full_terminal_map.tsv "$BASE_PRODUCER")
{
 echo 'label=DIAGNOSTIC / NOT_EVIDENCE'; echo "host=$(hostname)"; echo "utc_start=$START"; echo "pid=$$"; echo "candidate=$CANDIDATE"; echo "set_id=$SET_ID"; echo "workers=${WORKERS:-10}"; echo "driver=$(realpath tools/d_ob_p2/candidate_comparison_driver.py)"; sha256sum "${FILES[@]}";
} > "$MAN"
set +e
/home/daybreak/.pyenv/versions/3.11.16/bin/python tools/d_ob_p2/candidate_comparison_driver.py \
 --config tools/d_ob_p2/candidate_comparison_config.py --base-producer "$BASE_PRODUCER" \
 --derived-producer tools/d_ob_p2/d_ob_p2_producer_c_regular_diagnostic.py \
 --c1 tools/d_ob_p2/results_192.tsv --c2 tools/d_ob_p2/independent_H_sign_N7_result.tsv \
 --c3 tools/d_ob_p2/phase0_points.tsv --c4 tools/d_ob_p2/P003_lambda251.tsv \
 --c4j tools/d_ob_p2/P003_independent_J_lambda251.tsv --c5 tools/d_ob_p2/full_terminal_map.tsv \
 --candidate "$CANDIDATE" --set-id "$SET_ID" --out "$OUT_DIR/result.tsv" "$@" 2>&1 | tee "$LOG"
RC=${PIPESTATUS[0]}
set -e
echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$MAN"; echo "actual_exit_code=$RC" >> "$MAN"; sha256sum "$LOG" "$OUT_DIR/result.tsv" 2>/dev/null >> "$MAN" || true
exit "$RC"
