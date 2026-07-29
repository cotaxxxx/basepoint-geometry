# B-TUBE v2.1 — B-LOCAL / B-ENTRY Dependency Design v2.1

Status: **DESIGN FROZEN; NO IMPLEMENTATION, COMPUTATION, WORKFLOW RUN, TAG, OR CERTIFICATE ARCHIVE AUTHORIZED**

This document supersedes the v2 design. It defines the B-LOCAL/B-ENTRY
dependency that supplies the exact left endpoint `lambda_start` to the later
B-TUBE v2.1 calibration and production stages.

## 1. Purpose and scope

B-LOCAL bridges the already certified boundary-entry parameter
`lambda_partial` to one exact rational candidate `lambda_start >
lambda_partial`. It certifies, on a local rectangle adjacent to `r = 1`, the
strict derivative and face-sign inequalities needed to prove a unique
nondegenerate interior root of

`F(r, lambda) = 0`

for every `lambda in (lambda_partial, lambda_start]`.

This stage certifies only the boundary-entry-to-local-root connection and the
exact B-TUBE handoff endpoint. It does not certify the later B-TUBE interval,
does not run calibration, does not authorize a B-LOCAL or calibration tag, and
does not create a dependency archive in Phase 1 or Phase 2.

## 2. Canonical Stage-1 dependency

### 2.1 Pinned source and bytes

The canonical Stage-1 dependency is:

- repository path:
  `CERTIFICATES/prolate/item2_branch/independent_recheck/certificate_item2_independent.json`
- source head:
  `b0582728d3f8fd3508ba8574a898017212a28caa`
- certificate SHA-256:
  `d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188`
- manifest SHA-256:
  `f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069`

The exact Stage-1 bracket is

`lambda_minus = 206538/100000`,
`lambda_plus  = 206539/100000`.

The exact certified statement is:

> B(103/50)>0, B(207/100)<0, B(206538/100000)>0,
> B(206539/100000)<0, and B'(lambda)<0 on
> [206538/100000,206539/100000]. Hence lambda_partial is the unique
> root in (206538/100000,206539/100000).

The exact machine conclusion is:

```json
{"lambda_partial":"(206538/100000,206539/100000)","strict_upper_bound":"206539/100000","unique_on_interval":true}
```

The exact scope string is:

> Boundary-entry parameter only. Item 2 proper, requiring the single sign
> change of F_r, remains open.

### 2.2 Dependency descriptor

The B-LOCAL run configuration contains a `stage1_dependency` object with
separate fields for:

- `path`
- `source_head`
- `certificate_sha256`
- `manifest_sha256`
- `config_sha256`
- `certified_statement`
- `machine_conclusion`
- `scope`
- `status`

`status` must equal `STAGE1_CONTENT_AUDITED` before any B-LOCAL execution path
may evaluate the mathematical kernel.

### 2.3 Normative exact objects and non-normative display

Displayed fractions such as `206539/100000` are explanatory only. Every
normative rational is a reduced exact rational object. A display fraction,
decimal string, or pretty-printed value may not substitute for that object.
The `display` namespace, when present, is ignored by proof logic and hashing
except as ordinary payload bytes.

## 3. Mandatory Stage-1 content audit

The verifier must fetch and hash the bytes at the pinned source head and must
confirm all of the following before setting `STAGE1_CONTENT_AUDITED`:

1. path, source head, certificate SHA-256, and manifest SHA-256 match;
2. the certificate parses as canonical dependency content and reports
   `status: "CERTIFIED"`;
3. the exact certified statement matches byte-for-byte;
4. the exact machine conclusion matches structurally and by canonical bytes;
5. the exact scope string matches byte-for-byte;
6. the bracket endpoints equal the reduced rational objects for
   `206538/100000` and `206539/100000`;
7. `unique_on_interval` is exactly `true`;
8. `strict_upper_bound` is exactly `206539/100000`;
9. no local or later B-LOCAL result is used to repair or reinterpret Stage-1.

A label, copied digest, README statement, or exported constant is not a
substitute for checking the actual pinned certificate and manifest bytes.

## 4. Deterministic Stage-1 dependency archive

A later Phase-3 implementation may build a deterministic Stage-1 dependency
archive. The archive is not created in Phase 1 or Phase 2.

The archive must:

- be built from a new empty directory;
- contain the pinned certificate, manifest, the exact audit descriptor, and
  sufficient source material to replay the content audit;
- use lexicographically sorted member paths;
- use fixed ZIP metadata and deterministic compression settings;
- include a canonical manifest over actual member bytes;
- record the actual archive ZIP SHA-256;
- reject symlinks, path traversal, duplicate paths, omitted files, extra files,
  and post-build mutation;
- preserve the distinction between Stage-1
  `stage1_dependency.config_sha256` and the B-LOCAL
  `blocal_run_config_sha256`.

## 5. Exact local coordinates

Set

`u = 1 - r`,
`s = lambda - lambda_plus`,
`H(u, s) = F(1 - u, lambda_plus + s)`.

Thus `u = 0` is the boundary face `r = 1`, positive `u` points into the
interior, and `s = 0` is the Stage-1 upper endpoint.

The candidate local rectangle for one pair `(lambda_start, u_max)` is

`0 <= u <= u_max`,
`-s_neg <= s <= s_start`,

where

`s_start = lambda_start - lambda_plus > 0`.

All transformations between `(r, lambda)` and `(u, s)` are exact rational or
dyadic transformations. No binary float, decimal approximation, or
string-parsed number enters a proof decision.

## 6. Negative-side dyadic margin

Freeze

`s_neg = 2^-16`.

Its canonical dyadic object is

```json
{"e":16,"m":"1"}
```

and `-s_neg` is

```json
{"e":16,"m":"-1"}
```

The Stage-1 bracket width is exactly

`lambda_plus - lambda_minus = 1/100000`.

The required comparison is proved by integer arithmetic:

`2^-16 > 1/100000`

because

`100000 > 65536`.

Since Stage-1 proves

`lambda_partial > lambda_minus`

and `s_neg > lambda_plus - lambda_minus`, one has

`lambda_plus - s_neg < lambda_minus < lambda_partial`.

Therefore the exact relation used by L4 is:

`lambda_partial > lambda_plus - s_neg`.

No decimal comparison or approximate root value may replace this argument.

## 7. Canonical exact-number formats

### 7.1 Reduced rational object

A normative rational is:

```json
{"p":"<signed base-10 integer>","q":"<positive base-10 integer>"}
```

with `gcd(abs(p), q) = 1`, `q > 0`, no leading plus sign, no negative zero,
and no redundant leading zeroes.

### 7.2 Canonical dyadic object

A normative dyadic is:

```json
{"m":"<signed base-10 integer>","e":<JSON integer>}
```

representing `m * 2^(-e)`.

Rules:

- `e` is a JSON integer and `e >= 0`;
- if `e > 0`, `m` is odd;
- if `e = 0`, there is no parity restriction on `m`;
- zero is represented only by `{"m":"0","e":0}`;
- no leading plus sign, negative zero, or redundant leading zeroes;
- equality, ordering, containment, and width are checked by exact integer
  alignment and comparison.

### 7.3 Prohibited numeric paths

The proof path forbids JSON floating numbers, Python `float`, `Decimal`,
locale-formatted numbers, decimal re-parsing, free-form interval strings, and
comparison through displayed values.

## 8. Candidate sequence

The exact `lambda_start` candidates are

`lambda_k = lambda_plus + 2^-k` for `k = 24, 23, ..., 4`.

The exact `u_max` candidates are, in this order:

`1/256, 1/128, 1/64, 1/32, 1/16`.

The candidate order is normative and deterministic:

1. lambda-major in the stated `k = 24` through `k = 4` order;
2. u-max-minor in the stated ascending order.

There are exactly `21 * 5 = 105` candidates. Candidate indices are zero-based
and must be reconstructed independently by the checker. A run may select only
the first candidate satisfying every required node and budget rule.

## 9. Certified domains

For each candidate define `s_start = 2^-k`.

The exact certification obligations are:

- **L1**:
  `H_u(u,s) > 0` on
  `[0,u_max] x [-s_neg,s_start]`;
- **L2**:
  `H(u_max,s) > 0` on
  `{u_max} x [-s_neg,s_start]`;
- **L3**:
  `H(0,s) < 0` on
  `[0,s_start]`.

The L1 and L2 domains include the negative-side strip. Their global validation
endpoints are exactly `-s_neg` and `s_start`. L3 remains on the nonnegative
side and must not be extended to negative `s`.

Tile records must cover the stated closed domains exactly, with no gap,
overlap, inversion, omitted boundary, or unauthorized enlargement.

## 10. Audited Arb-to-dyadic enclosure adapter

The sole allowed enclosure adapter is identified by

`ARB_TO_CANONICAL_DYADIC_INTERVAL_V1`.

It accepts one finite Arb ball and returns exactly:

```json
{"hi":{"e":0,"m":"0"},"lo":{"e":0,"m":"0"}}
```

with the two placeholders replaced by canonical outward dyadic endpoints.

The adapter must:

- use exact binary mantissa/exponent extraction;
- use exact integer shifts and exact big-integer addition/subtraction;
- produce endpoints that outwardly contain the complete Arb ball;
- canonicalize both endpoints;
- require `lo <= hi` by integer comparison;
- reject non-finite input;
- expose its actual source-file SHA-256;
- be pinned by `arb_to_dyadic_adapter_sha256` in the B-LOCAL run config;
- be checked from actual imported file bytes and resolved path.

Forbidden paths include `str(arb)`, decimal-string parsing, binary-float
conversion, approximate midpoint/radius arithmetic, locale formatting, and
any independent unpinned adapter.

The mandatory ten adapter audit cases cover:

1. exact zero;
2. positive and negative integers;
3. positive and negative nonintegral dyadics;
4. unequal midpoint and radius exponents;
5. carry at the upper endpoint;
6. borrow at the lower endpoint;
7. an interval crossing zero;
8. very large mantissas;
9. rejection or canonicalization of noncanonical candidate representations;
10. rejection of NaN/infinity and of a decimal-string input path.

## 11. Coverage-record schemas

All proof enclosures in every record are canonical dyadic `{lo,hi}` objects
created by the pinned adapter. A free-form Arb display string is permitted only
under `display` and is non-normative.

### 11.1 Run header

One `RUN_HEADER` record contains at least:

- `record_type`
- `schema`
- `design_version`
- `blocal_run_config_sha256`
- complete `stage1_dependency`
- `arb_to_dyadic_adapter_sha256`
- candidate order and exact candidate lists
- precision and fixed budgets
- chain domain and genesis
- `previous_record_sha256`
- `record_sha256`

### 11.2 L1, L2, and L3 tile records

Every tile record contains:

- `record_type`
- `node` equal to `L1`, `L2`, or `L3`
- `candidate_index`
- exact rational/dyadic domain endpoints
- the canonical dyadic enclosure of the certified quantity
- the exact strict-sign predicate
- precision, subdivision depth, and evaluation count
- `certified`
- `previous_record_sha256`
- `record_sha256`

L1 and L2 records must expose global domain endpoints
`[-s_neg,s_start]`; L3 records must expose `[0,s_start]`.

### 11.3 Candidate summary

Exactly one `CANDIDATE_SUMMARY` follows the proof records for each attempted
candidate. It records exact candidate data, complete node status, exact
coverage counts, budgets, the first failure reason if any, and
`candidate_accepted`.

### 11.4 J_START

After all L3 records for the selected candidate, exactly one terminal
`J_START` proof record is required with these fields:

- `record_type`
- `node`
- `selected_candidate_index`
- `lambda_start` as a reduced rational `p/q` object
- `r_interval` as canonical dyadic `lo/hi`
- `F_at_r_lo`
- `F_at_r_hi`
- `F_r_on_interval`
- `claim: "J_START_UNIQUE_NONDEGENERATE_ROOT"`
- `interval_method: "INTERVAL_NEWTON_OR_KRAWCZYK_V1"`
- `strict_self_containment: true`
- `certified: true`
- `previous_record_sha256`
- `record_sha256`

It must verify exactly:

- `0 < r_lo < r_hi < 1`;
- `F_at_r_lo.lo > 0`;
- `F_at_r_hi.hi < 0`;
- `F_r_on_interval.hi < 0`;
- strict interval-Newton or Krawczyk self-containment.

A missing, duplicate, or nonterminal `J_START` record is rejected.

### 11.5 Run summary

One final `RUN_SUMMARY` records the selected first accepted candidate,
`lambda_start`, `u_max`, the J_START interval, exact counts and budgets, chain
tip, dependency identities, and terminal state.

## 12. Complete-tile verification

The independent checker reconstructs all 105 candidates and all requested
tile domains locally from the canonical run config. It does not reuse the
runner's candidate or tiling helper.

For each attempted candidate it verifies:

- exact candidate index and order;
- exact L1 and L2 global endpoints `[-s_neg,s_start]`;
- exact L3 global endpoints `[0,s_start]`;
- pairwise tile disjointness except shared faces;
- exact union coverage of every required closed domain;
- no missing, duplicate, unresolved, or extra tile;
- strict signs from canonical dyadic endpoint comparisons;
- precision and fixed budget limits;
- candidate summary consistency;
- first-accepted-candidate selection.

For the accepted candidate it additionally verifies the unique terminal
J_START record and the exact equality

`lambda_start = lambda_plus + s_start`.

## 13. Canonical JSON and record order

Canonical JSON object bytes are UTF-8 bytes produced by the equivalent of:

```python
json.dumps(
    obj,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

Duplicate keys, BOM, CR, non-UTF-8, NaN, infinity, JSON floating numbers, and
noncanonical bytes are rejected.

JSONL stores one canonical object per line using LF. The hash of a record is
over the canonical object bytes and excludes the JSONL linefeed.

Normative record order is:

1. one `RUN_HEADER`;
2. for each attempted candidate before the selected candidate, in deterministic
   order: all L1 tiles, all L2 tiles, all L3 tiles, then one
   `CANDIDATE_SUMMARY` with `candidate_accepted: false`;
3. for the selected candidate: all L1 tiles, all L2 tiles, all L3 tiles, exactly
   one `J_START`, then one `CANDIDATE_SUMMARY` with
   `candidate_accepted: true`;
4. one final `RUN_SUMMARY`.

No record may occur after `RUN_SUMMARY`. Phase-2 self-test must enforce this
exact placement; it may not choose, defer, or redefine the J_START position.

## 14. Chain genesis and configuration identity

The names are distinct and non-interchangeable:

- `stage1_dependency.config_sha256` identifies the Stage-1 dependency
  configuration;
- `blocal_run_config_sha256` identifies the canonical B-LOCAL run config.

The chain genesis is only:

```text
SHA256(
  ASCII("BLOCAL-COVERAGE-CHAIN-v1")
  || 0x00
  || bytes.fromhex(blocal_run_config_sha256)
)
```

It must not use the Stage-1 descriptor hash, Stage-1 config hash, certificate
hash, manifest hash, design commit, or any display field.

Every record carries `previous_record_sha256`; every successor binds the
canonical bytes of the preceding record. The checker independently rebuilds
the genesis and the complete chain.

## 15. Mathematical certification nodes

### 15.1 L1

`L1_EXTENDED_HU_STRICT_POSITIVITY` certifies

`H_u(u,s) > 0`

on `[0,u_max] x [-s_neg,s_start]`.

Because `H_u(u,s) = -F_r(1-u,lambda_plus+s)`, L1 also supplies strict radial
nondegeneracy.

### 15.2 L2

`L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY` certifies

`H(u_max,s) > 0`

for every `s in [-s_neg,s_start]`.

### 15.3 L3

`L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY` certifies

`H(0,s) < 0`

for every `s in [0,s_start]`.

### 15.4 L4

The logical lemma is pinned as

`BLOCAL_IVT_MONOTONE_ENTRY_V1`.

Its exact premises are:

1. `STAGE1_UNIQUE_BOUNDARY_ROOT_IN_OPEN_BRACKET`;
2. `STAGE1_B_STRICTLY_DECREASING_ON_CLOSED_BRACKET`;
3. `STAGE1_B_OF_LAMBDA_PARTIAL_EQUALS_ZERO`;
4. `L1_EXTENDED_HU_STRICT_POSITIVITY`;
5. `L2_EXTENDED_INNER_FACE_STRICT_POSITIVITY`;
6. `L3_NONNEGATIVE_BOUNDARY_FACE_STRICT_NEGATIVITY`;
7. `S_NEG_STRICTLY_EXCEEDS_STAGE1_BRACKET_WIDTH`;
8. `H_CONTINUITY_FROM_FIXED_FORMULA`.

For `lambda in [lambda_plus,lambda_start]`, L3 gives the boundary-face
negative sign directly. For the sliver
`lambda in (lambda_partial,lambda_plus)`, Stage-1 supplies
`B(lambda_partial)=0` and `B'<0`, while Section 6 proves the sliver lies inside
the extended L1/L2 strip. Thus the boundary face is negative throughout
`(lambda_partial,lambda_start]`.

L1 makes `H` strictly increasing in `u`, and L2 makes the inner face positive.
The intermediate value theorem therefore supplies exactly one root in
`0<u<u_max`; L1 makes it nondegenerate.

The exact L4 conclusion is:

> For every lambda in (lambda_partial, lambda_start], F(r,lambda)=0 has
> exactly one root with 1-u_max < r < 1, and F_r(r,lambda)<0 at that root.

## 16. Machine claims and logical lemmas

The checker distinguishes machine-certified inequalities from logical
assembly.

Machine-certified nodes are exactly L1, L2, L3, and J_START. L4 is derived
only by the pinned lemma and the eight premises above.

No machine record may claim the exact unknown value of `lambda_partial`.
No sampled grid, approximate root, plot, display interval, or numerical
continuation may replace a certified node or logical premise.

The output must explicitly report `real_analytic: false` unless a separate
audited analytic dependency is later added; real analyticity is not silently
inferred by this design.

## 17. Endpoint evaluation at r = 1

The boundary value is

`B(lambda) = F(1,lambda) = H(0,lambda-lambda_plus)`.

Endpoint evaluation at `r = 1` must use the fixed regularized formula and the
same pinned F/F_r source selected for B-LOCAL. A different boundary-only
implementation may be used only as a separately pinned cross-check and never
as the normative source.

L3 evaluates the nonnegative side. The negative-side boundary sign used by L4
comes logically from Stage-1 and is not requested as a negative-s L3 machine
domain.

## 18. Evaluation budget and deterministic termination

The canonical run config fixes precision, tolerances, subdivision policy,
maximum depth, maximum evaluations, and maximum tile count for every node.

A tile is terminal only when the required strict sign is certified or a fixed
budget/depth limit is reached. Limit exhaustion is
`BLOCAL_INCOMPLETE`, never success.

Candidate processing is deterministic. The runner stops after the first fully
accepted candidate and emits exact failure summaries for every preceding
candidate. If all 105 candidates fail or remain unresolved, the terminal state
is `BLOCAL_INCOMPLETE`.

## 19. Start-root interval and B-TUBE handoff

The selected exact `lambda_start` is the first accepted `lambda_k`.

J_START independently proves a unique nondegenerate interior root at that
exact lambda. The B-LOCAL certificate hands to calibration:

- exact `lambda_start`;
- exact J_START root interval;
- B-LOCAL artifact ZIP SHA-256;
- B-LOCAL certificate SHA-256;
- B-LOCAL source head;
- `blocal_run_config_sha256`;
- exact pinned machine conclusion;
- dependency status `PINNED`.

This tuple is the only permissible replacement for the current unpinned
B-LOCAL dependency in calibration.

## 20. B-LOCAL certificate schema

The canonical B-LOCAL certificate contains at least:

- `schema`
- `design_version`
- `status`
- `source_head`
- `design_commit`
- `blocal_run_config_sha256`
- `stage1_dependency`
- `arb_to_dyadic_adapter_sha256`
- `candidate_schedule`
- `selected_candidate_index`
- `lambda_start`
- `u_max`
- `s_neg`
- `s_start`
- `nodes` with L1, L2, L3, L4, and J_START
- exact `j_start`
- exact counts and budgets
- `chain_genesis`
- `chain_tip`
- `machine_conclusion`
- `scope`
- `real_analytic`
- `certificate_sha256`
- `artifact_zip_sha256`

The certificate is canonical JSON with no trailing newline. All referenced
payload bytes are closed inside the later deterministic delivery.

## 21. Exact pinned machine conclusion

A successful B-LOCAL certificate must pin one canonical machine conclusion
object equivalent to:

```json
{"binding_to_final_lambda_start":true,"coverage_claim":true,"lambda_start":{"p":"<selected reduced numerator>","q":"<selected reduced denominator>"},"real_analytic":false,"state":"BLOCAL_CERTIFIED","unique_non_degenerate_root_for_every_lambda_in":"(lambda_partial,lambda_start]"}
```

The exact selected rational object is substituted before hashing. No
placeholder, decimal, display fraction, recommendation field, or approximate
lambda is allowed.

The scope remains:

> B-LOCAL/B-ENTRY only. Later B-TUBE calibration and production certification
> remain separate and unauthorized.

## 22. Calibration mode-state machine

The later calibration implementation retains two modes:

- `DIAGNOSTIC_ONLY`;
- `BINDING`.

`DIAGNOSTIC_ONLY` requires an explicit `--diagnostic` command, keeps
`binding_to_final_lambda_start: false`, forces `recommendation: null`,
`coverage_claim: false`, and terminal state `CALIBRATION_INCOMPLETE`.

`BINDING` requires the complete pinned B-LOCAL tuple and exact
`lambda_start` equality.

The following combinations are rejected:

- `BINDING` with `--diagnostic`;
- `DIAGNOSTIC_ONLY` with B-LOCAL status `PINNED`;
- `BINDING` with B-LOCAL status `UNPINNED`;
- `BINDING` with `binding_to_final_lambda_start: false`;
- any mode that promotes `21/10`, `2/1`, or another diagnostic endpoint to the
  final B-LOCAL endpoint.

## 23. Required calibration implementation revisions

After B-LOCAL certification and separate static audit, calibration must:

1. replace the null B-LOCAL tuple with the exact certified tuple;
2. set mode to `BINDING`;
3. set `binding_to_final_lambda_start: true`;
4. remove or retain diagnostic data only in a nonbinding, explicitly separate
   path;
5. require exact equality between calibration `lambda_start` and the B-LOCAL
   rational object;
6. verify the B-LOCAL artifact, certificate, source, config, conclusion, and
   scope bytes;
7. preserve all existing calibration/B-TUBE source and workflow security
   gates;
8. remain unrun until a later explicit authorization.

## 24. Replacement of the placeholder dependency gate

The current fail-closed `require_blocal_dependency` gate is replaced only by
a verifier that checks:

- Stage-1 content-audited tuple;
- B-LOCAL artifact ZIP SHA-256;
- B-LOCAL certificate SHA-256;
- B-LOCAL source head;
- `blocal_run_config_sha256`;
- exact `lambda_start`;
- exact machine conclusion;
- status `PINNED`;
- `binding_to_final_lambda_start: true`.

Changing only a status string or numeric endpoint does not open the gate.

## 25. Mandatory negative controls

The Phase-2 self-test freezes at least these 45 fail-closed controls:

1. Stage-1 source-head tamper;
2. Stage-1 certificate SHA tamper;
3. Stage-1 manifest SHA tamper;
4. Stage-1 path mismatch;
5. Stage-1 status not `CERTIFIED`;
6. Stage-1 certified-statement mismatch;
7. Stage-1 machine-conclusion mismatch;
8. Stage-1 scope mismatch;
9. missing `STAGE1_CONTENT_AUDITED`;
10. nondeterministic or mutated Stage-1 dependency archive;
11. a display fraction accepted without the required reduced exact object;
12. lambda-candidate order changed;
13. u-max order changed;
14. L1 domain starts at `0` instead of `-s_neg`;
15. L2 domain starts at `0` instead of `-s_neg`;
16. L1/L2 global validation endpoint remains the old nonnegative endpoint;
17. `s_neg` is not exactly `2^-16`;
18. the `s_neg` comparison uses decimal or floating arithmetic;
19. the Section-6 inequality direction is reversed or corrupted;
20. the proof that `s_neg` exceeds the Stage-1 bracket width is missing;
21. L3 is extended to a negative-s interval;
22. L4 omits `B(lambda_partial)=0`;
23. L4 omits Stage-1 strict decrease `B'<0`;
24. an enclosure is stored as a free-form or decimal string;
25. an enclosure was not produced by the pinned
    `ARB_TO_CANONICAL_DYADIC_INTERVAL_V1` adapter or its source SHA mismatches;
26. a noncanonical dyadic object is accepted;
27. the adapter accepts NaN or infinity;
28. a display enclosure is used as normative proof data;
29. chain genesis uses `stage1_dependency.config_sha256` or another dependency
    hash instead of `blocal_run_config_sha256`;
30. the two config-hash field names are conflated;
31. record order is changed;
32. `previous_record_sha256` is tampered;
33. CRLF, BOM, trailing bytes, or noncanonical JSONL is accepted;
34. duplicate keys, NaN, infinity, or JSON floating numbers are accepted;
35. a coverage gap is accepted;
36. an overlap beyond a shared face is accepted;
37. a tile uses a domain outside the exact required rectangle;
38. an unresolved leaf is promoted;
39. a depth, evaluation, or tile limit is exceeded and success is emitted;
40. J_START is missing;
41. J_START is duplicated;
42. J_START is nonterminal or misplaced;
43. J_START lacks strict signs, strict derivative negativity, or strict
    self-containment;
44. an invalid mode/status/binding combination opens calibration;
45. `BLOCAL_INCOMPLETE` is promoted to a certificate, recommendation, coverage
    claim, tag, workflow run, or dependency archive.

## 26. Development and audit sequence

### Phase 1 — design freeze

- commit this design document only;
- no implementation, computation, workflow, tag, or archive;
- commit message explicitly states `no run authorized`;
- chat-side static audit verifies byte identity with the frozen text.

### Phase 2 — calculation-free self-test

- add canonical number, adapter, schema, chain, tile, J_START, state-machine,
  and control fixtures only;
- no production kernel evaluation;
- no B-LOCAL or calibration workflow;
- no tag;
- static audit must pass before Phase 3.

### Phase 3 — implementation and dependency archive

- implement the audited source and exact Stage-1 dependency archive;
- pin actual adapter source bytes and SHA;
- run only calculation-free tests and source-level audits unless a separate
  mathematical-run authorization is issued;
- dependency archive creation is first permitted in this phase.

### Phase 4 — separately authorized B-LOCAL run

- authorize one fixed source head and one canonical run config;
- execute B-LOCAL;
- independently reconstruct all records, chain, certificate, and delivery
  bytes;
- no calibration tag or run is implied.

### Phase 5 — calibration dependency pin

- pin the accepted B-LOCAL tuple into calibration in a separate commit;
- statically audit that commit;
- only after a further explicit authorization may an approval tag or
  calibration run be considered.

## 27. Authorization boundary

This design commit authorizes only static review of design bytes.

It does not authorize:

- implementation;
- mathematical kernel evaluation;
- GitHub Actions execution;
- creation of a B-LOCAL tag;
- creation of a calibration tag;
- promotion of `21/10` or any diagnostic endpoint;
- a calibration run;
- a production B-TUBE run;
- merge of result-bearing code to `main`;
- creation of a dependency archive before Phase 3.

The existing prohibitions on B-LOCAL tags, calibration tags, `21/10`
promotion, and dependency-archive creation remain in force.

## 28. Completion criterion

B-LOCAL/B-ENTRY is complete only when all of the following are true:

1. the frozen design commit has passed byte-level static audit;
2. the Phase-2 calculation-free self-test has passed all positive and negative
   controls;
3. the implementation source and adapter bytes have passed static audit;
4. Stage-1 content is independently revalidated from pinned bytes;
5. one separately authorized run produces exact complete L1/L2/L3 coverage,
   L4 assembly, and J_START;
6. the first accepted candidate is independently reconstructed;
7. the canonical certificate and deterministic delivery are byte-closed and
   independently reproduced;
8. the accepted tuple is pinned into calibration by a separate audited commit.

Until then, the only valid terminal state is `BLOCAL_INCOMPLETE` or a more
specific fail-closed state. No run is authorized by this document.
