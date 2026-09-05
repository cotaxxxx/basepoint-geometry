# Prolate local bifurcation certificate

Status: **CERTIFIED — archived reference bytes**

This directory contains the local-coefficient certificate used by Paper 1 for
the prolate-spheroid basepoint bifurcation.  The rigorous Arb/Acb computation
certifies

```text
Q(4.7) > 0,
Q(4.75) < 0,
Q'(a) < 0 on [4.7, 4.75],
H4(a) < 0 on [4.7, 4.75],
Q(4.72438) > 0,
Q(4.72439) < 0.
```

Consequently, `Q` has a unique simple zero

```text
a_c in (4.72438, 4.72439),
```

with `Q'(a_c) < 0` and `H4(a_c) < 0`.

## Evidence classes

- `prolate_cap_arb_certificate.py` and
  `prolate_cap_arb_certificate.json`: rigorous interval certificate.
- `prolate_B2_symbolic_audit.py` and
  `prolate_H4_symbolic_audit.py`: exact symbolic audits of the quadratic and
  quartic reductions.
- `prolate_cap_stage1.py` and `prolate_cap_stage1_report.json`: exploratory
  high-precision cross-check; not an interval-certified proof object.

## Reference execution

```bash
python prolate_cap_arb_certificate.py \
  --dps 50 \
  --tolerance 1e-20 \
  --subdivisions 5 \
  --json prolate_cap_arb_certificate.json
```

Reference environment recorded by the manuscript: Python 3.13.5,
python-flint 0.9.0, FLINT 3.6.0, mpmath 1.3.0, and SymPy 1.14.0.

The six archived bytes are pinned by `SHA256SUMS.txt`.  They match the hashes
recorded in Appendix A.5 of the 2026-08-18 manuscript snapshot.  The executable
certificate report records `status = CERTIFIED` and all six required
conditions as true.


## 2026-09 evidence-completion chain

Paper 1's public local evidence was completed on 2026-09-05 by adding five SHA-pinned objects:

- `prolate_ac_arb_certificate.py` / `.json`: 20-digit endpoint sign certificate for `a_c`.
- `prolate_Qz_symbolic_audit.py`: exact symbolic audit of the axial second-order jet.
- `prolate_Qz_arb_certificate.py` / `.json`: rigorous axial coefficient certificate on `[4.70,4.75]`.

The JSON files record `status=CERTIFIED`, execution timestamp, environment, precision, integration tolerance, parameter subdivisions, and a `certificate_id` identifying the `2026-09` new certification chain. The ac run uses 100 decimal digits and tolerance `1e-40`; the Qz run uses 70 decimal digits, tolerance `1e-28`, and five parameter subdivisions.

The Qz certificate has positive lower endpoints on all five subintervals; its worst rigorous lower endpoint is greater than `0.0885587746621582`. The complete eleven-object manifest is `SHA256SUMS.txt`.

Evidence-completion commit: `68bc9828c3476e9db2d73d338e731c48c0931f54`.
