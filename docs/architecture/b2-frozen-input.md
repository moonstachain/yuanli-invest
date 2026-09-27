# B2 input identity

The administrative B2 run now requires `YMQ4_B2_INPUT_SNAPSHOT_ID`. It reads
`gold_experiment_input(p_snapshot_id)` from the runtime repository and verifies
the SHA256 of the exact stored UTF-8 `payload_json` before running the original
2,336-row, 584-month, frozen train/OOS specification.

The payload is an object containing `schema_version: "b2-input.v1"`,
`panel_id: "gold_core_monthly_v0.1"` and `rows` in the existing panel format.
The result records input snapshot ID, hash and provenance. There is no automatic
fallback to the growing `pit.decision_asof_values` table.

Runtime owns the immutable snapshot table and operator import procedure. An
operator must identify the original accepted input archive and verify its
provenance before importing it. Capturing today's same-date rows does not prove
they equal the original accepted experiment's inputs; use a new snapshot identity
and honest provenance for that case. This change does not rewrite or claim to
reconstruct an old experiment.

Licensed observations stay in the runtime evidence store, outside Git. Local
regressions use generated synthetic rows and verify that later live-panel months
and revisions cannot alter an already serialized experiment input.
