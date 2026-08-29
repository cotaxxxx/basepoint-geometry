# B-LOCAL v2.3 source bundle

Status: `DESIGN_DRAFT_ONLY / NOT_BINDING / NOT_PROMOTED`.

This directory is a new dependency lineage for native `F_lambda` work. The copied `blocal_v22_*` support files are byte-for-byte snapshots of the frozen v2.2 dependency at base commit `52b98b6bd93382a47ed4cf5cbc7067edb0cebe45`; they are not replacements for, and do not mutate, `dependencies/blocal_v22_source/`.

The v2.3 native route must use `BLOCAL_FLAMBDA_ROUTE_V1`, require strict `NEG` for binding use, and forbid runtime monkeypatching. Until the v2.3 config, symbolic audit, transport lemma, checker, and source manifest are pinned and human-promoted, `BINDING_USE_AUTHORIZED=NO`.
