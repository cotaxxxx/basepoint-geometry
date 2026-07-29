# Item 3 lambda sweep — Phase 4 workflow candidate v2

Status: `PHASE4_REAUDIT_REQUIRED`.

The workflow previously certified at head `21756fbba0aa974df4ebddfd7d40a7816250dcdc` remains valid historical evidence for those exact bytes. It does not certify the current workflow candidate because the runtime and pilot-artifact gates have changed.

## Differential changes

The production workflow now adds:

- `actions: read` permission for fixed artifact download;
- pinned `actions/setup-python` and Python 3.12;
- `python-flint==0.9.0` installed from the Linux x86-64 stable-ABI wheel with `--require-hashes`, `--no-deps`, and `--only-binary=:all:`;
- canonical pilot artifact ID and ZIP SHA-256 binding;
- extraction and independent verification of every artifact-internal manifest entry;
- direct rederivation of `c_g_tube_pilot.py` SHA-256;
- production source static audit and no-math tests;
- approved config SHA-256 sidecar requirement;
- production entrypoint arguments binding the verified pilot artifact.

## Audit status

`PHASE4_STATIC_AUDIT.json` and `STATIC_AUDIT_LOG.txt` in this directory are retained as the prior-byte audit output. They are not a PASS for workflow v2.

`PHASE4_REAUDIT_REQUEST.json` defines the required differential audit. A new chat-side Phase 4 PASS must be issued before any tag or run authorization.

## Candidate static self-test

`PHASE4_STATIC_AUDIT_V2.json` and `STATIC_AUDIT_V2_LOG.txt` record a no-computation candidate self-test with all 29 checks passing. This is implementation evidence only; `chat_differential_audit_status` remains `PENDING`.

## Non-authorization

```text
run_authorized = false
tag_created = false
workflow_executed = false
```
