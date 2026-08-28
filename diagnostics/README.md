# Diagnostics

Everything in this directory is `DIAGNOSTIC_ONLY` and `NOT_BINDING`.

`basepoint-geometry` is the general-framework repository. Per `DECISIONS.md`
sections 2 and 5, particular-body diagnostics normally live in the relevant
experimental repository. Files kept here are cross-repository hand-off
material: they are produced or specified at the project level and are meant to
be executed against, or ported into, an experimental repository.

Every diagnostic artifact must record:

- code revision;
- parameter domain;
- mesh or subdivision;
- arithmetic and precision;
- derivation class for every recorded number;
- stopping criteria;
- unresolved or failed cells;
- creation date.

Diagnostic files must not be consumed as certification dependencies.

## Contents

| File | Evidence class | Notes |
|---|---|---|
| `wolfram_handoff_cap_crosscheck.md` | `SYMBOLIC_CROSSCHECK / NOT_BINDING` | Hand-off request and output contract. |
| `wolfram_handoff_cap_crosscheck.wl` | `SYMBOLIC_CROSSCHECK / NOT_BINDING` | The script the hand-off asks to run. |
| `wolfram_handoff_cap_crosscheck_sympy_mirror.py` | `SYMBOLIC_CROSSCHECK / NOT_BINDING` | Same eight checks in SymPy, runnable without a Wolfram kernel. |

### `wolfram_handoff_cap_crosscheck.wl`

- Created: 2026-08-28.
- Subject: the oblate endpoint-cap algebra of
  `cotaxxxx/bg-oblate-spheroid`, branch `analytic-endpoint-limit-78c178f`,
  file `analysis/endpoint_kernel_lemma.md`.
- Parameter domain: `-1 < mu < 1`, `t < 1`, `0 < lambda < 1/sqrt(2)`.
- Arithmetic: exact rational and exact symbolic throughout; sample residuals
  at 60 working digits, reported at 50 digits, pass tolerance `10^-45`.
- Derivation class: `EXACT` for the symbolic identities, `HIGH_PRECISION`
  for the sample residuals.
- Stopping criteria: every named check reports `PASS` or `FAIL`; the script
  exits non-zero if any check fails.
- Unresolved cells: none by construction. A `FAIL` line is a failed cell and
  must be reported with the run.
- It is a second, independent computer-algebra path over the same algebra.
  It certifies no interval, replaces no interval checker, and promotes no
  numerical value.

### `wolfram_handoff_cap_crosscheck_sympy_mirror.py`

Same subject, domain, arithmetic, tolerance and derivation classes as the
Wolfram script. It runs the eight checks under the same labels through a
different computer algebra system, so that the hand-off can be checked
without a Wolfram kernel and so that a disagreement between the two systems
is visible. Requires SymPy. It does not remove the obligation to run the
Wolfram script: two independent systems agreeing is the point.

An unexecuted script is not evidence. This directory records the request and
the code; the returned standard output and the matching SHA-256 are what may
later be cited, and only at `SYMBOLIC_CROSSCHECK / NOT_BINDING`.
