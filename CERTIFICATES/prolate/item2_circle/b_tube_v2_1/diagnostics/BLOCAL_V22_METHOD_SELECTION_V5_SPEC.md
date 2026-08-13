# B-LOCAL v2.2 §6 — Taylor2 method-selection diagnostic prototype v5 specification

STATUS: DIAGNOSTIC PROTOTYPE SPEC. This document applies only to the §6
method-selection diagnosis. `certificate_evidence=false`.

The native nine sources, committed configuration, production path, tags, the
v3/v4 prototypes, and `C1_STRUCTURAL_FLOOR_SPEC_V1.md` are outside this
specification and remain byte-for-byte unchanged.

## 1. Purpose and provenance

Prototype v4 removed the C1 structural-floor plateau. Subsequent chat-side
diagnostics found the same fixed-floor dependency at six explicitly enumerated
call sites and in the Duffy denominator bound. Prototype v5 incorporates only
the changes specified below.

The measured improvements quoted in this document are provenance, not pass
criteria. Acceptance is determined only by the six §6.2 conditions and the
committed candidate ordering and budgets.

## 2. Effective-floor rule

For each call site listed in §3, define

```text
effective_floor = max(structural_floor, natural_argument_lower)
```

only when `natural_argument_lower` is available, finite, and strictly
positive. The natural lower endpoint must come from the rigorous interval/ball
enclosure of the argument on the exact evaluation region and must be converted
to a canonical outward dyadic lower endpoint. Point-float sampling is not an
admissible bound.

If the natural lower endpoint is unavailable, nonfinite, or nonpositive, use
the existing structural-floor helper. For the Duffy nonnegative square-root
site, use its existing nonnegative helper. Every fallback is fail-closed and is
recorded with its reason.

Center and box evaluations compute separate natural lower endpoints from their
respective evaluation regions. A box lower endpoint must not be reused for a
center evaluation, or conversely.

For a single factor evaluation, its value factor `f0` and derivative factors
`f1` and `f2` use the same effective floor. Recomputing different floors for
the derivative factors is prohibited.

The effective-floor rule is not an intersection, post-hoc hull, or sampled
estimate. Both operands of the maximum are independently valid lower bounds,
so their maximum is a valid lower bound.

## 3. Exhaustive call-site list

The effective-floor rule applies to exactly these six sites. The phrase “all
monotone factors” is not an implementation substitute for this list.

### 3.1 Ordinary charts through `geometry_jet`

1. The `q` argument of `qpow`: `q_eff`.
2. The `w2` argument of `qpow`, replacing the hard-coded floor `1`:
   `w2_eff`.
3. The `1-c^2` argument of `jsqrt`: `S2_eff`.

The C1 structural `q` floor from `C1_STRUCTURAL_FLOOR_SPEC_V1.md` remains the
structural operand of `q_eff`; it is not replaced or weakened. TH, R2, T1, and
T2 retain their existing structural operands.

### 3.2 Duffy charts through `_duffy_eval`

4. The `w2` argument of `_safe_positive_sqrt`, replacing floor `1`:
   `w2_eff`.
5. The `1+y^2` argument of `_safe_positive_sqrt`, replacing floor `1`:
   `g2_eff`.
6. The `1-c^2` argument of `_safe_nonnegative_sqrt`, which previously had no
   positive floor: `S2_eff`.

No seventh effective-floor call site is implied by this specification.

## 4. Duffy local geometry reconstruction

Calling `rt._geometry` after selecting Duffy `S2_eff` is prohibited because
that routine reconstructs `S` with the old floor-free square-root path. The
Duffy evaluator must locally and consistently reconstruct

```text
S, U, W, B, q
```

and propagate the same `S2_eff` through every downstream factor. Mixing a new
`S` with old `U`, `W`, `B`, or `q` values invalidates the diagnostic record.

The existing gamma clamp to `[0,1]` remains a fail-closed safety device. It is
not removed or replaced by an unproved intersection. Records distinguish
corner degeneration (`a0 == 0`) from non-corner fallback.

## 5. Duffy `Z_lo` strengthening

The old Duffy denominator lower bound omitted the nonnegative `W-hat` squared
term. V5 uses

```text
rho2_hi = epsilon^2 * a1^2 * (1 + b1^2)
Z_lo    = Ahat_lo + r_lo^2 * Bhat_lo + u0^2 / rho2_hi
q_lo    = rho2_lo * Z_lo
u0      = 1 - r_hi
```

All displayed quantities are exact rationals. `rho2_lo` is retained without
change. The new term follows from `W-hat = W/rho`, `W >= 1-r_hi = u0`, and
`rho^2 <= rho2_hi`.

Each component is clamped nonnegative before addition. A nonfinite or invalid
new component is dropped to zero and recorded; the pre-v5 components remain
available and are not weakened. A nonpositive final `q_lo` is fail-closed.

The one-piece Duffy `q_lo` alternative is not part of v5.

Chat-side adversarial sampling found zero violations in 130 tested cells and
measured `q_lo/inf(q)` median 0.983 and p90 0.998. These values are provenance,
not acceptance thresholds.

## 6. Record additions

In addition to the bounded/interned v3/v4 §6.5 record, v5 records for every
relevant evaluation:

- call-site identifier and chart;
- structural, natural, and effective floor as exact rational JSON;
- selected source (`structural` or `natural`);
- fallback occurrence and reason;
- center or box region identifier;
- the shared-floor identity for `f0`, `f1`, and `f2`;
- Duffy corner/non-corner classification and gamma fallback;
- Duffy `S2_eff` and the locally reconstructed `S/U/W/B/q` provenance;
- `Ahat_lo`, `r_lo^2*Bhat_lo`, `u0^2/rho2_hi`, `rho2_lo`, `rho2_hi`,
  `Z_lo`, and `q_lo`;
- counters and elapsed time on every success and fail-closed path.

Record growth remains bounded by the v3 intern/capping mechanism. The v3 gzip
artifact and short summary mechanism remain unchanged.

## 7. Fail-closed conditions

The diagnostic is invalid or INDETERMINATE, as appropriate, if any of the
following occurs:

1. A natural lower endpoint is derived from sampling, point float arithmetic,
   or a non-outward endpoint.
2. A nonfinite or nonpositive natural lower endpoint is selected instead of
   falling back.
3. Center and box reuse a lower endpoint from different regions.
4. `f0`, `f1`, and `f2` for one factor use different floors.
5. An unlisted effective-floor site is silently added.
6. Duffy evaluation calls the old geometry result downstream of `S2_eff`, or
   mixes reconstructed and old geometry quantities.
7. The gamma `[0,1]` clamp is removed.
8. The Duffy `W-hat` component uses an inexact endpoint or a denominator other
   than exact `rho2_hi` above.
9. A mathematical budget is changed during or after a run.
10. A required source, specification, or configuration hash differs from its
    pinned value.

## 8. Budget domains

Committed node budgets reset for each candidate and each node because
`_certify_outer` initializes its evaluation counter on every call. They are
not shared across the lambda ladder.

| Domain | max depth | max evaluations | max tiles/bisections |
|---|---:|---:|---:|
| L1_BOUNDARY / L1_INTERIOR | 18 | 20,000 | 12,000 tiles |
| L2 / L3 | 22 | 12,000 | 8,000 tiles |
| J_START | committed algorithm | 96 | 40 bisections |

The committed configuration has no wall-clock mathematical budget.

Earlier probe values (24,000 evaluations, depth 14 or 16, 16,000 active cells,
and wall 900 seconds) are diagnostic-probe limits and must not be copied into a
committed-contract shard. A CI wall timeout is infrastructure protection only,
is recorded separately as `ci_wall_timeout_seconds`, and is never entered in a
mathematical-budget field.

## 9. Lambda ladder semantics

The committed lambda increment order is

```text
2^-24, 2^-23, ..., 2^-4
```

and the committed schedule is lambda-major and `u_max`-minor. L3 at `r=1` is
independent of `u_max`, so a diagnostic ladder enumeration uses one shard per
lambda increment and does not expand a `u_max` dimension.

The selected `lambda_start` is the first `ACCEPTED` candidate in canonical
index order. An earlier `INDETERMINATE` candidate does not prevent selection of
a later certified candidate. This implements “first certified candidate”; it
does not reinterpret INDETERMINATE as mathematical rejection.

Shard verdicts are exactly:

- `ACCEPTED`: strict NEG certified;
- `INDETERMINATE`: the committed budget/depth did not certify a sign;
- `REJECTED`: failure of the condition was positively certified;
- `INFRASTRUCTURE_FAILURE`: provenance, environment, or artifact failure.

The aggregate view may derive `ACCEPTED_SELECTED` and
`ACCEPTED_NOT_SELECTED` from `ACCEPTED`; these are selection annotations, not
new mathematical verdicts.

If no candidate is ACCEPTED and provenance is complete, the aggregate result
is `NO_CANDIDATE_CERTIFIED`: fail-closed, with no `lambda_start`, and without a
claim of mathematical method failure. Missing, duplicate, mismatched, or
unreadable shard evidence instead produces `INFRASTRUCTURE_FAILURE`. Neither
case may proceed to conditions 5 and 6.

## 10. Six-condition sequencing

The required order is:

1. commit and audit this v5 specification;
2. add and audit a byte-pinned v5 prototype while preserving v4;
3. run all 21 L3 shards with that audited prototype commit and committed L3
   budgets;
4. aggregate in canonical order and select the formal `lambda_start`;
5. run conditions 5 and 6 with the same prototype and selected value;
6. set `all_six_conditions_pass=true` only after all six records are complete.

Running the ladder with v4 and transferring its selected value to v5 is
prohibited.

## 11. Invariants

- Application is diagnostic only; `certificate_evidence=false`.
- Native nine sources and committed configuration SHA-256 `fec14e99...` remain
  byte-for-byte unchanged.
- V3, v4, and canonical C1 specification SHA-256 `8492755d...` remain
  byte-for-byte unchanged.
- Gamma adaptive bins, bounded record representation, gzip artifact, and short
  summary remain unchanged except for the explicitly added v5 record fields.
- No production path or tag is created or modified.
- Workflow creation or modification requires separate explicit approval after
  the specification and prototype audits are GREEN.
