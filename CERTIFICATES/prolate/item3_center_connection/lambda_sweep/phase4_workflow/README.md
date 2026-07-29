# Item 3 Lambda Sweep — Phase 4 Workflow Candidate

This directory contains the Phase 4 workflow, provenance, and observer-separation audit assets.

Normative design blob: `cafbf7b661911995008dda49bfb3ecabcecb1f12`

Audited source commit: `70af0de152fe93256dd243770181addb250ca7c2`

Reference tag↔SHA pattern: `e86c130d18f69e9d9944a2f35a5af2f37f399881`

## Separation

- Production workflow: `.github/workflows/prolate-item3-lambda-sweep.yml`
  - trigger: `item3-sweep-run-*` tags only
  - permissions: `contents: read`
  - validates tag suffix before checkout and checked-out HEAD after checkout
  - performs Phase 3 gates before requiring the separately audited production config
  - uploads output using a commit-SHA-pinned action
- Observer workflow: `.github/workflows/prolate-item3-lambda-sweep-observer.yml`
  - trigger: successful completion of the production workflow
  - permissions: `actions: read`, `contents: write`
  - atomically writes immutable run receipt plus `latest.json` to the pre-existing receipt branch
  - enforces strictly increasing workflow run IDs and `EXCLUDED_HEAD_SHA`

## Fail-closed prerequisites

Before a tag is authorized, all of the following remain required:

1. Chat-side Phase 4 byte and static audit PASS.
2. Separate production config and entrypoint audit.
3. Creation and audit of the dedicated receipt branch named in `OBSERVER_POLICY.json`.
4. Explicit user authorization for exactly one tag whose suffix is the full 40-character source commit SHA.

No tag, workflow run, production calculation, or main update is performed by this Phase 4 candidate.
