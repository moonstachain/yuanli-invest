-- YMQ-OS0-G1 Sovereign Intelligence Stack additive runtime migration.
-- Extends the existing evidence / pit / runtime lineage; creates no competing truth schema.

create table if not exists evidence.claim_receipts (
  claim_receipt_id uuid primary key default gen_random_uuid(),
  claim_id text not null,
  source_snapshot_id uuid not null references evidence.source_snapshots(snapshot_id),
  as_of timestamptz not null,
  evidence_status text not null check (evidence_status in ('PASS','LIMITED','BLOCKED','UNKNOWN')),
  evidence_authority text not null,
  claim_authority text not null,
  rights_status jsonb not null default '{}'::jsonb,
  receipt jsonb not null default '{}'::jsonb,
  git_sha text not null,
  created_at timestamptz not null default now()
);

create table if not exists runtime.agent_runs (
  run_id uuid primary key default gen_random_uuid(),
  agent_id text not null,
  provider text not null,
  provider_run_id text,
  git_sha text not null,
  as_of timestamptz not null,
  evidence_refs uuid[] not null default '{}'::uuid[],
  requested_authority text not null default 'RESEARCH',
  granted_authority text not null default 'RESEARCH',
  intent text not null,
  request_payload jsonb not null,
  response_payload jsonb,
  run_status text not null check (run_status in ('STARTED','SUCCEEDED','DENIED','FAILED')),
  deny_reason text,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  check (granted_authority = 'RESEARCH')
);

create table if not exists runtime.research_projections (
  projection_id uuid primary key default gen_random_uuid(),
  run_id uuid not null references runtime.agent_runs(run_id),
  surface text not null,
  projection_type text not null,
  content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'),
  canonical_truth boolean not null default false,
  can_grant_authority boolean not null default false,
  payload jsonb not null,
  created_at timestamptz not null default now(),
  check (not canonical_truth),
  check (not can_grant_authority)
);

create table if not exists runtime.learning_deltas (
  learning_delta_id uuid primary key default gen_random_uuid(),
  source_run_id uuid not null references runtime.agent_runs(run_id),
  delta jsonb not null,
  effective_after timestamptz not null,
  created_at timestamptz not null default now(),
  check (effective_after >= created_at)
);

alter table evidence.claim_receipts enable row level security;
alter table runtime.agent_runs enable row level security;
alter table runtime.research_projections enable row level security;
alter table runtime.learning_deltas enable row level security;

-- No anon/authenticated policies are intentionally created.
-- Service-role access remains server-side only; GitHub Canon is not modified by database state.

create index if not exists claim_receipts_claim_asof_idx
  on evidence.claim_receipts (claim_id, as_of desc);
create index if not exists agent_runs_asof_idx
  on runtime.agent_runs (as_of desc, agent_id);
create index if not exists research_projections_run_idx
  on runtime.research_projections (run_id, created_at desc);
create index if not exists learning_deltas_effective_idx
  on runtime.learning_deltas (effective_after, source_run_id);
