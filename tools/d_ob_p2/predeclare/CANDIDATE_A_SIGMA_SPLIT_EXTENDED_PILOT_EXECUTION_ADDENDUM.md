# Execution addendum to the extended candidate (a) sigma-split pilot predeclare

Status: DIAGNOSTIC / NOT_EVIDENCE. Draft for freeze. Pre-ignition.
Successor predeclare: `tools/d_ob_p2/predeclare/CANDIDATE_A_SIGMA_SPLIT_EXTENDED_PILOT_PREDECLARE.md`,
SHA-256 `b80a565f7e4a0e81e8397ac7c97b261550b1a5a9738e0303f3093eba27287392` (commit `3b40a385a36b5f0b1031b938aa21d85a0d1a6fc1`).
Extended judge: `tools/d_ob_p2/evaluate_sigma_pilot_ext.py`,
SHA-256 `7ff450e69cd516a69179d59598c5ada393dd51a108a9d0085afdee4c9346b507` (commit `83dcff37a8c46d735a9278275ca72c362b3d1096`).
Neither file is changed. This addendum fixes the execution identity required by successor predeclare
Section 3 and the order of its Section 8. The freeze pin is the triple (predeclare, judge, this addendum).

## E0. Roles

| role | party |
|---|---|
| drafting of this addendum | Claude Code |
| environment values, PC execution, supporting self-audit | ChatGPT (drafting / PC execution side), through Remote Desktop |
| independent audit, FREEZE countersign, authorisation of A2 | the main audit chat |

Erratum carried here: A4 addendum 1 (`31a4ed34...`) records its executor as "ChatGPT (the auditing
assistant of that conversation)". Under the three-role system that attribution is wrong; the executor was
ChatGPT on the drafting / PC execution side. Addendum 1 is left unchanged because it is frozen and was used
for the A4 verdict.

## E1. Execution identity

Directory `D` = `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927`.

| item | value |
|---|---|
| host | `daybreak-works` |
| shell | `bash` |
| Python | `/home/daybreak/.pyenv/versions/3.11.16/bin/python` (3.11.16), python-flint `0.9.0` |
| measurement script | `D/tools/near_sigma_split_measure.py`, SHA-256 `a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d` |
| judge | `D/tools/evaluate_sigma_pilot_ext.py`, SHA-256 `7ff450e69cd516a69179d59598c5ada393dd51a108a9d0085afdee4c9346b507` |
| producer | `/home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py`, SHA-256 `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b` |
| map | `D/full_terminal_map.tsv`, SHA-256 `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8` |
| A4 bridge TSV | `D/sigma_pilot_k1248.tsv`, SHA-256 `afed07837353095344befb865c3ee94c9a7020a67b2d4e86f68973dc20635d54` (read only) |
| output | `D/sigma_pilot_ext_k1_8_16_32_64.tsv` (must not exist before the run) |
| check-only log | `D/sigma_pilot_ext_k1_8_16_32_64.checkonly.log` |
| run log | `D/sigma_pilot_ext_k1_8_16_32_64.run.log` |
| workers | `20` |

In the commands below `D` is written out in full. The script and the judge are placed at the paths above
as byte copies of the committed files; placement is not ignition, and A2 checks their SHA-256. The A4
script path `/tmp/near_sigma_split_measure.py` is not used, because `/tmp` is not persistent.

Worker sizing: one measurement process peaked at about 129 MiB resident on a point box with 58,826 cells
(Claude Code container, self-test, no real leaf data); a leaf has at most 65,536 cells. 20 workers are
therefore estimated at under 3 GiB. The host condition in A2 requires at least 8 GiB available.
Rough duration estimate from A4 (not a measurement): about 1,500 s per leaf, about 5 h with 20 workers.

## E2. A2-equivalent check (after FREEZE, before E3; again immediately before E4)

```
printf '%s  %s\n' \
  a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/near_sigma_split_measure.py \
  7ff450e69cd516a69179d59598c5ada393dd51a108a9d0085afdee4c9346b507 /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/evaluate_sigma_pilot_ext.py \
  dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py \
  0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8 /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv \
  afed07837353095344befb865c3ee94c9a7020a67b2d4e86f68973dc20635d54 /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv \
  | sha256sum -c -
test ! -e /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.tsv && echo OUTPUT_ABSENT
hostname
/home/daybreak/.pyenv/versions/3.11.16/bin/python -c "import platform, flint; print(platform.python_version(), flint.__version__)"
/home/daybreak/.pyenv/versions/3.11.16/bin/python -c "import os; n=os.cpu_count(); l=os.getloadavg()[0]; m=[int(x.split()[1]) for x in open('/proc/meminfo') if x.startswith('MemAvailable:')][0]//1048576; print('HOST_OK' if n>=20 and l<=n-20 and m>=8 else 'HOST_NOT_OK nproc=%d load1=%.2f memavail_GiB=%d' % (n, l, m))"
```

Expected output, exact:

```
/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/near_sigma_split_measure.py: OK
/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/evaluate_sigma_pilot_ext.py: OK
/home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py: OK
/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv: OK
/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv: OK
OUTPUT_ABSENT
daybreak-works
3.11.16 0.9.0
HOST_OK
```

Any difference: the next step does not start. `HOST_OK` means at least 20 CPUs, a 1-minute load average
of at most (CPUs - 20), and at least 8 GiB available. For the record only (not matched), also run
`nproc; uptime; free -g` and keep the output with the report.

## E3. Check-only command

```
/home/daybreak/.pyenv/versions/3.11.16/bin/python /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/near_sigma_split_measure.py --producer /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py --map /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv --select stride:32:0 --ks 1,8,16,32,64 --check-only 2>&1 | tee /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.checkonly.log; echo "EXIT=${PIPESTATUS[0]}"
```

Expected output, exact and complete:

```
population_near_unresolved=7662 selected=240 ks=[1, 8, 16, 32, 64]
EXIT=0
```

## E4. Measurement command (ignition)

```
/home/daybreak/.pyenv/versions/3.11.16/bin/python /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/near_sigma_split_measure.py --producer /home/daybreak/bg-oblate-spheroid-c1b/producer/d_ob_p2_producer.py --map /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv --select stride:32:0 --ks 1,8,16,32,64 --out /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.tsv --workers 20 2>&1 | tee /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.run.log; echo "EXIT=${PIPESTATUS[0]}"
```

The printed `EXIT=` line is the exit line for successor predeclare Section 4 item 1.

## E5. Judge command (after the run)

```
/home/daybreak/.pyenv/versions/3.11.16/bin/python /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/tools/evaluate_sigma_pilot_ext.py --out /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.tsv --map /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/full_terminal_map.tsv --log /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_ext_k1_8_16_32_64.run.log --bridge /home/daybreak/basepoint-geometry-artifacts/D_OB_P2_analysis_20260927/sigma_pilot_k1248.tsv --exit "<the EXIT= line printed by E4, verbatim>"; echo "JUDGE_EXIT=$?"
```

## E6. Order

1. This addendum committed alone; commit, parent, tree and file SHA-256 reported.
2. Supporting self-audit by the drafting / PC execution side.
3. Independent remote-byte audit and FREEZE countersign by the main audit chat; A2 authorised.
4. E2 (including OUTPUT_ABSENT and HOST_OK).
5. E3.
6. E2 again, immediately before E4.
7. E4 (ignition).

A step taken before the step it follows invalidates the clean preregistered execution status; that case
is adjudicated separately. OUTPUT_ABSENT in step 4 is the mechanical evidence that the predeclare, the
judge and this addendum were committed before the extended output existed.

## E7. Interruption

No resume. A run that does not finish is RUN INVALID; the partial output is kept and not used. A rerun
needs a new execution addendum with a new output path.

## E8. Registered after the run

Output TSV SHA-256, run log SHA-256, check-only log SHA-256, the `EXIT=` line, start and end times (with
their source), the record-only host output of E2, the judge stdout and `JUDGE_EXIT`.
