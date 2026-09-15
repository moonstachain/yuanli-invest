-- YMQ-OS0-G1 follow-up hardening from Supabase performance advisor.
-- Add leading indexes for foreign-key lookup paths without changing semantics.

create index if not exists claim_receipts_source_snapshot_idx
  on evidence.claim_receipts (source_snapshot_id);

create index if not exists learning_deltas_source_run_idx
  on runtime.learning_deltas (source_run_id);
