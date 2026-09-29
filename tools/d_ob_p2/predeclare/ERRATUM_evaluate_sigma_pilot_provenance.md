# Erratum: provenance sentence in evaluate_sigma_pilot.py

Target: `tools/d_ob_p2/evaluate_sigma_pilot.py`, SHA-256 `8e481042d4e3b7bde30fce400cbfc15c42f905df89fbe550b7cf7ae1440ad746`
(commit `fd3db6421a2c119943d2fe98e1c782684ea57d17`). The file is left unchanged because these exact bytes
were audited and used for the A4 verdict.

Retracted sentence (docstring):

> Written and committed before any pilot output existed.

This is false. The A4 run log was created 2026-09-29 20:02:49 JST (filesystem birth, executor record);
the judge commit time is 2026-09-29T11:26:14Z = 20:26:14 JST, about 23 minutes later. The author (Claude
Code) had already been told that A4 was running when writing the sentence.

Corrected statement: the judge was written and committed while A4 was running. Its author had no access
to any A4 output, log or partial result, and implements only base predeclare Sections 4-6, frozen at
`dbef3157...` / `31a4ed34...` before A4 started. It was blind-audited by the auditing side before the
A4 output was opened.

This does not change the judge logic or the A4 verdict.
