#!/bin/sh
# reproduce.sh -- rebuild every numerical output of this directory.  DIAGNOSTIC_ONLY / NOT_EVIDENCE.
# Requirements: gcc (OpenMP), Python 3 with numpy, scipy, mpmath, matplotlib.  About 2 hours on 4 cores.
# Outputs go to a fresh directory (default: repro_out/) so the shipped out/ is never overwritten.
set -eu
cd "$(dirname "$0")"
OUT="${1:-repro_out}"; FIG="${2:-repro_fig}"
mkdir -p "$OUT" "$FIG"
OUT="$(cd "$OUT" && pwd)"; FIG="$(cd "$FIG" && pwd)"
sha256sum -c PLAN.sha256
cd code
gcc -O2 -ffp-contract=off -fopenmp -shared -fPIC -o libtriax.so triax_kernel.c -lm
gcc -O2 -ffp-contract=off -fopenmp -shared -fPIC -o libtriax_big.so triax_big.c -lm
python3 check_formulas.py   "$OUT/check_formulas.json"      # definition / gradient / Hessian / boundary trace
python3 shear.py            "$OUT/check_shear.json"         # shear identities (S2), (S3)
python3 run_A.py            "$OUT/runA_census.jsonl"        # Run A: main grid census (longest step)
python3 run_B_curves.py     "$OUT/runB_curves.json"         # Run B/E: curves Z1, Z2, D1, D2
python3 run_C_edges.py      "$OUT/runC_edges.json"          # Run C: splitting near the edges
python3 run_D_sphere.py     "$OUT/runD_sphere.json"         # Run D: neighbourhood of the sphere
python3 run_E_far.py        "$OUT/runE_far.json"            # Run E: far grid
python3 flat_limit.py       "$OUT/flat_limit.json"          # leading-log flat limit
python3 probe_monotone.py   "$OUT/probe_monotone.json"      # exploratory probes (outside the fixed plan)
python3 probe_ordering.py   "$OUT/probe_ordering.json"
python3 probe_plane12.py    "$OUT/probe_plane12.json"
python3 probe_shear_sign.py "$OUT/probe_shear_sign.json"
python3 probe_pairing.py  > "$OUT/probe_pairing.txt"
python3 analyze.py "$OUT" "$FIG"                            # tables.md, ledger CSV, figures
echo "done: outputs in $OUT, figures in $FIG"
echo "note: the shipped Run A used the one-stage Newton (algo 1) for its first 451 shapes; this script uses algo 2 throughout."
