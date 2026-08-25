# Project Decisions and Working Memory

Updated: 2026-08-25

This file records project-level decisions whose rationale would otherwise be
lost across repositories and later stages of the research. It is a working
memory, not a certification artifact. Unless explicitly promoted through the
project rules, statements recorded here are `NOT_BINDING`.

## 1. Long-term research hierarchy

The final objective is **Basepoint Dynamics**.

**Basepoint Geometry** (formerly referred to as geometric dual topology) is the
static, geometric, and topological foundation for that objective. The research
order is:

1. complete the particular papers P1--P4;
2. write the general theory after P1--P4;
3. use the resulting stationary-point, bifurcation, Hessian, and stability
   structure as the foundation for Basepoint Dynamics.

The general theory must not be allowed to expand the scope of the current
particular papers. In particular, P2 will not be enlarged merely to anticipate
the later dynamics theory.

## 2. Repository architecture

The intended four-repository structure is:

- `basepoint-geometry` -- general framework, terminology, research rules,
  general-theory seeds, project index, and reusable workflow orchestration;
- `bg-prolate-spheroid` -- prolate-spheroid particular work;
- `bg-oblate-spheroid` -- oblate-spheroid particular work;
- `bg-triaxial-ellipsoid` -- triaxial-ellipsoid particular work.

The experimental repositories are evidence and reproduction layers for the
particular papers. They are not substitutes for the general theory.

### Rename rule

`basepoint-geometry` must not be renamed again. It was renamed from
`geometric-dual-topology`, and reusing or moving its current name could break
repository redirects. GitHub Actions also does not follow redirects for actions
or reusable workflows.

The prolate material will therefore be moved by creating a new
`bg-prolate-spheroid` repository, not by renaming
`basepoint-geometry`.

`Oblate-Spheroid-Research` may be renamed to `bg-oblate-spheroid` before it
has external workflow or publication dependencies.

## 3. Migration order

The agreed order is:

1. finish the pre-rename oblate repository correction unit;
2. obtain an archival DOI for the fixed prolate material;
3. rename `Oblate-Spheroid-Research` to `bg-oblate-spheroid`;
4. create `bg-prolate-spheroid` and move the prolate material into it;
5. create `bg-triaxial-ellipsoid` only when needed.

The prolate move is last because P1 and its reference links must remain stable
through submission.

## 4. DOI policy

Repository moves must not be the sole basis of archival identity.

- Cite the specific Zenodo version DOI used by a paper.
- A Zenodo concept DOI identifies the versions of one record; it is not by
  itself a collection DOI for several repositories.
- If a single project-level index is needed, create a separate project-manifest
  record listing the repository version DOIs and fixed commit SHAs.
- Obtain the prolate archival DOI before moving its repository contents.

## 5. Checker and workflow architecture

The mathematical checker is **vendored into each experimental repository**.
A central-checkout design is not used.

The division of responsibility is:

- mathematical verification code: vendored in each experimental repository;
- expectations, configuration, certificates, receipts, and failure records:
  stored in the experimental repository;
- execution orchestration: a reusable workflow maintained in
  `basepoint-geometry`;
- caller workflow: a thin file in each experimental repository, pinned to the
  full commit SHA of the reusable workflow.

A typical experimental repository should contain:

```text
checker/
UPSTREAM.json
controls/
certificates/
diagnostics/
.github/workflows/
RESEARCH_RULES.md
```

`UPSTREAM.json` records the upstream `basepoint-geometry` commit, Git blob
hash, and byte-level SHA-256 for every vendored checker file. CI must verify
that the vendored bytes agree with this manifest.

Central audit of an upstream checker may be reused as evidence only after the
vendored copy is shown to be byte-identical. Vendoring does not automatically
promote a reconstructed copy to an audited or certified object.

## 6. Certificate provenance

In addition to the existing audited-source consistency checks, certificates
must record at least:

- caller repository;
- caller source commit SHA;
- reusable workflow ref;
- resolved reusable workflow commit SHA;
- path and SHA-256 of the applicable `RESEARCH_RULES.md`;
- upstream rules commit;
- path and SHA-256 of `UPSTREAM.json`;
- vendored checker file hashes.

Inside a reusable workflow, the resolved workflow identity should be obtained
from the documented `job.workflow_ref` and `job.workflow_sha` contexts and
confirmed by a smoke run. The certificate must directly assert that the
resolved workflow SHA equals the full SHA pinned by the caller.

## 7. Evidence discipline

All repositories follow the evidence and derivation classes in
`RESEARCH_RULES.md`.

In particular:

- local or chat-assisted calculations are candidate evidence;
- `HIGH_PRECISION` is not `CERTIFIED_ENCLOSURE`;
- extrapolated values are replaced when direct values become available;
- diagnostic searches are not nonexistence proofs;
- expectation becomes control only when a test actually calls the
  implementation and the expectation was not generated by that implementation;
- producer and auditor remain different actors;
- failures and unresolved incidents remain in the record.

Each experimental repository must pin both the applicable research-rules
version and the reusable-workflow version.

## 8. Oblate P2 scope

The oblate tail lemma for the singular limit `lambda -> 0` is outside P2.
It remains a separate analytic obligation and must not enlarge P2.

During the finite-window determination, the following quantities should still
be retained because they are expected to arise during computation and may be
needed later for Basepoint Dynamics:

- stationary basepoint locations;
- Hessian eigenvalues;
- Morse indices;
- critical values of the functional.

Values not used in the certified P2 claim remain
`DIAGNOSTIC_ONLY / NOT_BINDING` and must carry their parameter values,
precision, derivation class, and source commit SHA.

## 9. General-theory seeds

Although the general theory will be written after P1--P4, reusable structure
must be recorded while the particular papers are being developed.

A project-level file in `basepoint-geometry`, provisionally
`GENERAL_THEORY_SEEDS.md`, should record for each of P1--P4:

- which arguments did not depend on the particular body `K`;
- the assumptions actually used;
- propositions that may be promoted into the general framework;
- references to the relevant paper section, theorem, and fixed commit.

The future general-theory section on the common framework should be assembled
from these records rather than reconstructed from memory.

## 10. Stability-theorem feasibility check

After P1 enters submission, perform a limited feasibility study of the proposed
label-preserving local-triviality theorem for the projection
`pi: S -> Lambda`.

Separate the analysis into:

1. isolated nondegenerate stationary points;
2. compact Morse--Bott components with normal nondegeneracy;
3. degenerate stationary points.

The purpose is to determine the exact reach of the future general theorem, not
to expand P1--P4.

## 11. Current priority and restart point

The immediate priority is **P1 submission**.

The repository work resumes in this order:

```text
confirm remaining oblate pre-rename items
-> obtain the prolate DOI
-> rename the oblate repository
-> create and populate the new prolate repository
```

The highest-level destination remains Basepoint Dynamics, but near-term work
must be judged by whether it advances P1--P4 and preserves reliable evidence
for the later general theory.


## 12. Execution status

Checked: 2026-08-25

The pre-rename oblate repository was inspected at
`cotaxxxx/Oblate-Spheroid-Research@2cb9e11e7eb07c1662457bac14881da7c159f968`.

| Item | Status | Record |
|---|---|---|
| Evidence/expectation demotion wording | DONE | Expectations are explicitly not controls until an implementation-calling, implementation-independent test exists. |
| Candidate numerical replacements and derivation classes | DONE | Direct high-precision values are present; obsolete values `0.64430` and `0.6965` are absent. |
| One-source/two-source provenance distinction | DONE | `lambda_entry_ob` is recorded as one-source; `lambda_axis_ob` records independent agreement near `0.40796`. |
| `RESEARCH_RULES.md` | DONE | Present in the oblate repository. |
| Diagnostic derivation-class requirement | DONE | Present in `diagnostics/README.md`. |
| README introductory sentence | DONE | Replaced with the agreed non-certification wording. |
| GitHub repository description field | DONE | Verified through the GitHub repository metadata on 2026-08-25; it exactly matches the agreed non-certification description. |
| Vendored `checker/` | NOT DONE | No production checker exists yet. Rule 11 forbids an ambiguous placeholder. |
| `UPSTREAM.json` | NOT DONE | Must be created together with an actual vendored checker; no placeholder is committed. |
| Rename to `bg-oblate-spheroid` | NOT DONE | Must wait until the pre-rename correction unit is closed. |
| Prolate archival DOI | NOT DONE | This is the next major operation after the oblate pre-rename unit. |
| New `bg-prolate-spheroid` repository | NOT DONE | Must follow the DOI and oblate rename steps. |

The oblate pre-rename documentation-and-metadata correction unit is **closed**.
The GitHub repository description was verified after manual update on
2026-08-25. Checker vendoring remains a separate implementation-stage
obligation and is intentionally deferred until a real checker exists.


### Independent audit record

On 2026-08-25, the project owner independently compared the execution-status
table with the repository contents and reported all twelve entries accurate.

The audited repository state was:

- `cotaxxxx/Oblate-Spheroid-Research@2cb9e11e7eb07c1662457bac14881da7c159f968`;
- project ledger before this audit note:
  `cotaxxxx/basepoint-geometry@8ec89573f996e73efd2e98e09132b0112db5a497`.

The audit specifically confirmed that obsolete values `0.64430`, `0.6965`,
and `0.6443` were absent; derivation classes and methods were present;
the expectation-test rename was complete; `CONTROL_EXPECT.json` separated
evidence class, derivation class, and artifact role and recorded the promotion
condition; and `RESEARCH_RULES.md` was present in the oblate repository.

This audit does not promote any numerical value or artifact to `CERTIFIED`.
The GitHub repository description field was subsequently replaced and
verified. The pre-rename documentation-and-metadata correction unit is closed.


## 13. Oblate prototype checkpoint

Recorded: 2026-08-25

A reviewable endpoint-regular axial evaluator now exists on the unmerged draft
branch:

- repository and branch:
  `cotaxxxx/Oblate-Spheroid-Research@implementation/endpoint-regular-axis-v1`;
- draft review: pull request #1;
- prototype checkpoint:
  `cotaxxxx/Oblate-Spheroid-Research@92e3ad5d2ab8a8b7b9a7cfee7ef5f84890af3e89`;
- evidence status: `PROTOTYPE / NOT_AUDITED`.

The implementation directly evaluates the pole endpoint after
`mu = 1 - s^2`, connects the fixed sphere expectations to tests that call the
implementation, reproduces the recorded boundary root and signs, and agrees
with the earlier axial-branch diagnostic table at its stated rounding scale.

The project owner reported an independent code read, algebra check, separate
numerical implementation, and execution. Because the reviewer also
participated in the earlier derivation, this is recorded as strong cross-check
evidence but not as the independent producer/auditor separation required for
interval certification.

Deferred obligations are:

- split-interval convergence comparison at increased precision;
- a derivation-independent variable transformation or quadrature path;
- fail-closed interval implementation;
- certification-only workflow discipline.

Decision: do not begin interval certification now. Leave pull request #1 as an
unmerged draft prototype and return to the P1 submission priority.
