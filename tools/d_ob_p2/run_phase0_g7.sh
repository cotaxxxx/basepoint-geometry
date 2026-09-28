#!/usr/bin/env bash
# G7 wrapper for the D-OB P2 Phase 0 harness. DIAGNOSTIC / NOT_EVIDENCE.
# Usage (launch detached):
#   setsid nohup bash run_phase0_g7.sh HARNESS PINNED RESULTS OUT HARNESS_COMMIT [WORKERS] >/dev/null 2>&1 &
# Writes OUT.log (harness stdout/stderr) and OUT.manifest (identity, PIDs, UTC times,
# actual exit code, SHA-256 of inputs and of the four generated artifacts).
set -u
HARNESS=$1; PINNED=$2; RESULTS=$3; OUT=$4; COMMIT=$5; WORKERS=${6:-10}
MAN="${OUT}.manifest"; LOG="${OUT}.log"
if [ -e "$OUT" ] || [ -e "$MAN" ]; then echo "ABORT: $OUT or $MAN exists" >&2; exit 3; fi
sha() { sha256sum "$1" 2>/dev/null | cut -d' ' -f1; }
{
  echo "label=DIAGNOSTIC / NOT_EVIDENCE"
  echo "utc_start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "wrapper_pid=$$"
  echo "wrapper_sha256=$(sha "$0")"
  echo "harness_path=$(readlink -f "$HARNESS")"
  echo "harness_commit=$COMMIT"
  echo "harness_sha256=$(sha "$HARNESS")"
  echo "pinned_sha256=$(sha "$PINNED")"
  echo "results_path=$(readlink -f "$RESULTS")"
  echo "results_sha256=$(sha "$RESULTS")"
  echo "out=$(readlink -f "$(dirname "$OUT")")/$(basename "$OUT")"
  echo "workers=$WORKERS"
  echo "host=$(hostname)"
  echo "python=$(python3 --version 2>&1)"
  echo "scipy=$(python3 -c 'import scipy; print(scipy.__version__)' 2>&1)"
} > "$MAN"
PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 "$HARNESS" --pinned "$PINNED" --results "$RESULTS" \
  --out "$OUT" --workers "$WORKERS" > "$LOG" 2>&1 &
CHILD=$!
echo "harness_pid=$CHILD" >> "$MAN"
wait "$CHILD"; EXIT=$?
{
  echo "utc_end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "exit=$EXIT"
  for f in header.json phase0_points.tsv warnings.json summary.json; do
    if [ -f "$OUT/$f" ]; then echo "sha256_$f=$(sha "$OUT/$f")"; else echo "sha256_$f=MISSING"; fi
  done
  echo "log_sha256=$(sha "$LOG")"
} >> "$MAN"
exit "$EXIT"
