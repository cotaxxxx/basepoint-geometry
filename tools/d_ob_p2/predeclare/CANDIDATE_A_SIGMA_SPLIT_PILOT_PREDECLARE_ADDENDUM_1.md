# Addendum 1 to the candidate (a) sigma-split pilot predeclare: execution identity

Status: DIAGNOSTIC / NOT_EVIDENCE. Pre-measurement.
Base document: `tools/d_ob_p2/predeclare/CANDIDATE_A_SIGMA_SPLIT_PILOT_PREDECLARE.md`,
SHA-256 `dbef315750f1ccacc037d6962450319a74bdb47578323e995dfc495fbf1c0b08` (commit `fe77a702d555c55d63fe0a60cbde07d0af15da2e`).
The base document is unchanged. This addendum replaces the placeholders of base Section 3 with the
fixed values below; everything else in the base document stays in force. The freeze pin is the pair
(base document SHA-256, this addendum SHA-256).

## A1. Execution identity

| item | value |
|---|---|
| executor | ChatGPT (the auditing assistant of that conversation), operating through Remote Desktop |
| host | `daybreak-works` |
| shell | `bash` |
| Python | `/home/daybreak/.pyenv/versions/3.11.16/bin/python` (Python 3.11.16) |
| python-flint | `0.9.0` |
| script | `/tmp/near_sigma_split_measure.py`, SHA-256 `a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d` |
| producer | `/home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py`, SHA-256 `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b` |
| map | `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv`, SHA-256 `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8` |
| output | `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv` (must not exist before the run) |
| check-only log | `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.checkonly.log` |
| run log | `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.run.log` |
| workers | `4` |

`/tmp/near_sigma_split_measure.py` is not a persistent path. It is valid as the run identity only
because its SHA-256 is pinned and re-checked immediately before the check-only and before the run (A2).

## A2. Pre-run check (immediately before A3, and again immediately before A4)

```
printf '%s  %s\n' \
  a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d /tmp/near_sigma_split_measure.py \
  dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py \
  0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8 /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv \
  | sha256sum -c -
test ! -e /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv && echo OUTPUT_ABSENT
hostname
/home/daybreak/.pyenv/versions/3.11.16/bin/python -c "import platform, flint; print(platform.python_version(), flint.__version__)"
```

Expected output, exact:

```
/tmp/near_sigma_split_measure.py: OK
/home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py: OK
/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv: OK
OUTPUT_ABSENT
daybreak-works
3.11.16 0.9.0
```

Any difference: the step that follows does not start.

## A3. Check-only command (base Section 3 and Section 2 item 4)

```
/home/daybreak/.pyenv/versions/3.11.16/bin/python /tmp/near_sigma_split_measure.py --producer /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py --map /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv --select stride:32:0 --ks 1,2,4,8 --check-only 2>&1 | tee /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.checkonly.log; echo "EXIT=${PIPESTATUS[0]}"
```

Expected output, exact and complete:

```
population_near_unresolved=7662 selected=240 ks=[1, 2, 4, 8]
EXIT=0
```

## A4. Measurement command

```
/home/daybreak/.pyenv/versions/3.11.16/bin/python /tmp/near_sigma_split_measure.py --producer /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py --map /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv --select stride:32:0 --ks 1,2,4,8 --out /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv --workers 4 2>&1 | tee /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.run.log; echo "EXIT=${PIPESTATUS[0]}"
```

The `EXIT=` line is the exit code for base Section 4 item 1.

## A5. Interruption

The script has no resume. A run that does not finish (interrupted, killed, host restarted) is RUN
INVALID. The partial output is kept as is and not used. Running again requires a new addendum with a
new output path; the base document's sample, k list, threshold and rules do not change.

## A6. Registered after the run

Output TSV SHA-256, run log SHA-256, the `EXIT=` line, start and end times, and the results required
by base Section 8.
