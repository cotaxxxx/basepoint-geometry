# Wolfram hand-off: oblate endpoint-cap symbolic cross-check

## Scope

- Evidence class: `SYMBOLIC_CROSSCHECK / NOT_BINDING`.
- This checks the cap algebra through an independent computer-algebra path.
- It does not certify an interval, replace the Arb checker, or change any
  existing receipt or evidence classification.

## Input

Run from the repository root:

```text
wolframscript -file diagnostics/wolfram_handoff_cap_crosscheck.wl
```

The script uses exact rational input for all symbolic and numerical sample
checks. It does not use `PowerExpand`.

## Required returned material

Return the complete standard output, including:

- `wolfram_version`;
- every `PASS` or `FAIL` line;
- `direct_second_derivative_residuals`;
- `phi_series`;
- `majorant_maximum`;
- `failure_count`;
- the SHA-256 of the exact `.wl` file that was run.

The expected process exit status is zero and the expected final line is:

```text
failure_count=0
```

## Load-bearing checks

1. `N=-(1-mu^2) C`.
2. `w^2 q-lambda^2 A^2=(1-mu^2) C^2`.
3. Both `C>0` and `C<0` branches of `alpha_t` and `alpha_tt`.
4. The coefficient `-4 mu alpha alpha_t` in the second product derivative.
5. The compact formula

   ```text
   partial_t^2(A alpha^2)
     = 2 A lambda^2 R^2/q^2 (1-2 alpha tan(alpha)).
   ```

6. Direct 50-digit samples against the unsimplified second derivative.
7. Analyticity of `Phi(u)=arcsin(sqrt(u))^2` at `u=0`.
8. `max[z/(1+z^2)^2]=9/(16 sqrt(3))` at `z=1/sqrt(3)`.

The sign branches are deliberately separate. Combining them before handling
`Abs[C]` can hide an incorrect square-root simplification.

## Implemented output tokens

The committed script prints the required material under these exact tokens:

| Token | Meaning |
|---|---|
| `wolfram_version` | `$Version` of the kernel that ran the script. |
| `wolfram_release_number` | `$ReleaseNumber` of the same kernel. |
| `script_path` | `$InputFileName`, to confirm which file was executed. |
| `PASS` / `FAIL` | One line per named check, in the order listed above. |
| `second_product_derivative` | Expanded `partial_t^2(A alpha^2)` in symbolic form. |
| `direct_second_derivative_residuals` | Header, then one line per sample point, then `max_second_derivative_residual`. |
| `phi_series` | `Normal` of the order-8 series of `Phi(u)` at `u=0`. |
| `phi_series_coefficients` | The same coefficients as a list. |
| `majorant_maximum` | The exact value `9/(16 Sqrt[3])`. |
| `majorant_argmax` | The exact argument `1/Sqrt[3]`. |
| `failure_count` | Final line; zero when every check passed. |

Sample residuals are computed at 60 working digits and reported at 50 digits.
The pass tolerance is `10^-45`.

## Symbol naming inside the script

Mathematica reserves the single-letter names `C`, `D`, `E` and `N`. The
script therefore uses `symA`, `symQ`, `symW2`, `symR`, `symC` and `symN` for
the quantities written `A`, `q`, `w^2`, `R`, `C` and `N` in this document.
Printed labels use the mathematical names.

The square root `R = Sqrt[1-mu^2]` and the branch sign `Sign[C]` are carried
as free symbols `symR` and `symSign` constrained by `symR^2 = 1-mu^2` and
`symSign^2 = 1`. Radicals are cleared by multiplying the defining relation
`-sin(alpha) alpha_t = gamma_t` by `w q^(3/2)` and then reducing modulo those
two relations with `PolynomialReduce`. This is the mechanism that keeps the
`C>0` and `C<0` branches separate without `PowerExpand`.

## Definitions used by the checks

```text
A     = 1 - t mu
q     = 1 - mu^2 + lambda^2 (mu - t)^2
w^2   = lambda^2 (1 - mu^2) + mu^2
R     = sqrt(1 - mu^2)
C     = (1 - lambda^2) mu + lambda^2 t
N     = -mu q - A lambda^2 (t - mu)
gamma = lambda A / (w sqrt(q))
alpha = arccos(gamma)
```

The branch formulas under test are

```text
alpha_t  =  lambda R sgn(C) / q
alpha_tt = -2 lambda^3 R sgn(C) (t - mu) / q^2
```

and, with `z = lambda (t - mu)/R`,

```text
alpha_tt = -2 lambda^2 sgn(C) z / (R^2 (1 + z^2)^2),
```

so check 8 gives the cap `|alpha_tt| <= 9 lambda^2 / (8 sqrt(3) R^2)`.

## Repository placement

The oblate endpoint material itself lives in `cotaxxxx/bg-oblate-spheroid`.
This copy is held in `basepoint-geometry` only because it was produced here.
If the script is moved, the SHA-256 recorded below must be recomputed and the
hand-off reissued.

## Reference hash

The committed script has

```text
sha256(diagnostics/wolfram_handoff_cap_crosscheck.wl)
  = e5ceb1866980baf97e0b9ccdf36533a9f4a5f7d4478fbc3f49107eed58f57da0
```

The SHA-256 returned with the run must equal this value. If it does not, the
returned output describes a different file and is not evidence about this
script.

The SymPy mirror committed alongside it has

```text
sha256(diagnostics/wolfram_handoff_cap_crosscheck_sympy_mirror.py)
  = 77e6c73c58901f9677b5839eb3a132fe6005fb9eeb70b6dc052e57c25a84ffdd
```

The mirror runs the same eight checks under the same labels in a different
computer algebra system, and its recorded run is in
`wolfram_handoff_cap_crosscheck_sympy_mirror_result.txt`. It does not replace
the Wolfram run: the value of the hand-off is two independent systems
agreeing.
