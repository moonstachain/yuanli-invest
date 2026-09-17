-- YCI0-RP0 additive research-loop persistence.
-- Reuses evidence/pit/runtime lineage. This migration grants RESEARCH authority only.

create table if not exists runtime.capital_questions (
  question_id text primary key,
  question text not null,
  theme text not null,
  owner text not null,
  journey_stage text not null,
  gate_status text not null,
  block_reason text,
  prior_belief text not null,
  defeat_condition text not null,
  time_horizon jsonb not null default '[]'::jsonb,
  book_mapping jsonb not null default '{}'::jsonb,
  next_action text,
  next_review_at timestamptz,
  known_as_of timestamptz not null,
  source_snapshot_id uuid references evidence.source_snapshots(snapshot_id),
  claim_receipt_id uuid references evidence.claim_receipts(claim_receipt_id),
  created_by_run_id uuid references runtime.agent_runs(run_id),
  authority text not null default 'RESEARCH',
  created_at timestamptz not null default now(),
  check (authority = 'RESEARCH')
);

create table if not exists runtime.context_packs (
  context_pack_id uuid primary key default gen_random_uuid(),
  question_id text not null references runtime.capital_questions(question_id),
  run_id uuid not null references runtime.agent_runs(run_id),
  source_snapshot_id uuid references evidence.source_snapshots(snapshot_id),
  claim_receipt_id uuid references evidence.claim_receipts(claim_receipt_id),
  known_as_of timestamptz not null,
  content_hash text not null check (content_hash ~ '^[0-9a-f]{64}$'),
  payload jsonb not null,
  authority text not null default 'RESEARCH',
  created_at timestamptz not null default now(),
  check (authority = 'RESEARCH')
);

create table if not exists runtime.ai_infra_state_cards (
  state_card_id uuid primary key default gen_random_uuid(),
  question_id text not null references runtime.capital_questions(question_id),
  run_id uuid not null references runtime.agent_runs(run_id),
  observation_id uuid not null references pit.observations(observation_id),
  source_snapshot_id uuid not null references evidence.source_snapshots(snapshot_id),
  claim_receipt_id uuid references evidence.claim_receipts(claim_receipt_id),
  journey_stage text not null,
  known_as_of timestamptz not null,
  state_hash text not null check (state_hash ~ '^[0-9a-f]{64}$'),
  payload jsonb not null,
  authority text not null default 'RESEARCH',
  created_at timestamptz not null default now(),
  check (authority = 'RESEARCH')
);

create table if not exists runtime.shadow_settlements (
  settlement_id uuid primary key default gen_random_uuid(),
  question_id text not null references runtime.capital_questions(question_id),
  run_id uuid not null references runtime.agent_runs(run_id),
  projection_id uuid not null references runtime.research_projections(projection_id),
  reality_gate_run_id uuid not null references runtime.reality_gate_runs(run_id),
  learning_delta_id uuid references runtime.learning_deltas(learning_delta_id),
  t0_known_as_of timestamptz not null,
  t0_question_hash text not null check (t0_question_hash ~ '^[0-9a-f]{64}$'),
  t0_context_hash text not null check (t0_context_hash ~ '^[0-9a-f]{64}$'),
  t0_projection_hash text not null check (t0_projection_hash ~ '^[0-9a-f]{64}$'),
  settlement_status text not null,
  next_review_at timestamptz,
  payload jsonb not null default '{}'::jsonb,
  authority text not null default 'RESEARCH',
  created_at timestamptz not null default now(),
  check (authority = 'RESEARCH')
);

alter table runtime.capital_questions enable row level security;
alter table runtime.context_packs enable row level security;
alter table runtime.ai_infra_state_cards enable row level security;
alter table runtime.shadow_settlements enable row level security;

revoke all on table runtime.capital_questions from public, anon, authenticated;
revoke all on table runtime.context_packs from public, anon, authenticated;
revoke all on table runtime.ai_infra_state_cards from public, anon, authenticated;
revoke all on table runtime.shadow_settlements from public, anon, authenticated;

grant select, insert, update on table runtime.capital_questions to service_role;
grant select, insert, update on table runtime.context_packs to service_role;
grant select, insert, update on table runtime.ai_infra_state_cards to service_role;
grant select, insert, update on table runtime.shadow_settlements to service_role;

create index if not exists yci0_rp0_capital_questions_stage_idx
  on runtime.capital_questions (journey_stage, question_id);
create index if not exists yci0_rp0_capital_questions_review_idx
  on runtime.capital_questions (next_review_at, question_id);
create index if not exists yci0_rp0_capital_questions_snapshot_idx
  on runtime.capital_questions (source_snapshot_id);
create index if not exists yci0_rp0_context_packs_question_asof_idx
  on runtime.context_packs (question_id, known_as_of desc);
create index if not exists yci0_rp0_context_packs_snapshot_idx
  on runtime.context_packs (source_snapshot_id);
create index if not exists yci0_rp0_context_packs_claim_idx
  on runtime.context_packs (claim_receipt_id);
create index if not exists yci0_rp0_state_cards_question_stage_asof_idx
  on runtime.ai_infra_state_cards (question_id, journey_stage, known_as_of desc);
create index if not exists yci0_rp0_state_cards_observation_idx
  on runtime.ai_infra_state_cards (observation_id);
create index if not exists yci0_rp0_state_cards_snapshot_idx
  on runtime.ai_infra_state_cards (source_snapshot_id);
create index if not exists yci0_rp0_state_cards_claim_idx
  on runtime.ai_infra_state_cards (claim_receipt_id);
create index if not exists yci0_rp0_shadow_review_idx
  on runtime.shadow_settlements (next_review_at, question_id);
create index if not exists yci0_rp0_shadow_projection_idx
  on runtime.shadow_settlements (projection_id);

create or replace function runtime.yci0_rp0_guard_shadow_t0_immutable()
returns trigger
language plpgsql
set search_path = runtime, pg_temp
as $$
begin
  if new.question_id is distinct from old.question_id
     or new.run_id is distinct from old.run_id
     or new.t0_known_as_of is distinct from old.t0_known_as_of
     or new.t0_question_hash is distinct from old.t0_question_hash
     or new.t0_context_hash is distinct from old.t0_context_hash
     or new.t0_projection_hash is distinct from old.t0_projection_hash then
    raise exception 'YCI0_RP0_T0_IDENTITY_IMMUTABLE';
  end if;
  return new;
end;
$$;

drop trigger if exists yci0_rp0_shadow_t0_immutable on runtime.shadow_settlements;
create trigger yci0_rp0_shadow_t0_immutable
before update on runtime.shadow_settlements
for each row execute function runtime.yci0_rp0_guard_shadow_t0_immutable();

create or replace function public.yci0_rp0_bind_evidence(
  p_question_id text,
  p_run_id uuid,
  p_observation_id uuid,
  p_source_snapshot_id uuid,
  p_claim_receipt_id uuid,
  p_journey_stage text,
  p_known_as_of timestamptz,
  p_state_hash text,
  p_payload jsonb
)
returns uuid
language plpgsql
security definer
set search_path = public, runtime, evidence, pit, pg_temp
as $$
declare
  v_state_card_id uuid;
  v_observation_snapshot uuid;
  v_claim_snapshot uuid;
begin
  select source_snapshot_id into v_observation_snapshot
    from pit.observations where observation_id = p_observation_id;
  if v_observation_snapshot is null or v_observation_snapshot <> p_source_snapshot_id then
    raise exception 'YCI0_RP0_EVIDENCE_LINEAGE_MISMATCH';
  end if;

  if p_claim_receipt_id is not null then
    select source_snapshot_id into v_claim_snapshot
      from evidence.claim_receipts where claim_receipt_id = p_claim_receipt_id;
    if v_claim_snapshot is null or v_claim_snapshot <> p_source_snapshot_id then
      raise exception 'YCI0_RP0_CLAIM_LINEAGE_MISMATCH';
    end if;
  end if;

  insert into runtime.ai_infra_state_cards(
    question_id, run_id, observation_id, source_snapshot_id, claim_receipt_id,
    journey_stage, known_as_of, state_hash, payload, authority
  ) values (
    p_question_id, p_run_id, p_observation_id, p_source_snapshot_id, p_claim_receipt_id,
    p_journey_stage, p_known_as_of, p_state_hash, p_payload, 'RESEARCH'
  ) returning state_card_id into v_state_card_id;

  return v_state_card_id;
end;
$$;

create or replace function public.yci0_rp0_read_evidence_bindings(p_question_id text)
returns setof runtime.ai_infra_state_cards
language sql
security definer
set search_path = public, runtime, pg_temp
as $$
  select * from runtime.ai_infra_state_cards
  where question_id = p_question_id
  order by known_as_of desc, created_at desc;
$$;

create or replace function public.yci0_rp0_insert_shadow_settlement(
  p_question_id text,
  p_run_id uuid,
  p_projection_id uuid,
  p_reality_gate_run_id uuid,
  p_learning_delta_id uuid,
  p_t0_known_as_of timestamptz,
  p_t0_question_hash text,
  p_t0_context_hash text,
  p_t0_projection_hash text,
  p_settlement_status text,
  p_next_review_at timestamptz,
  p_payload jsonb
)
returns uuid
language plpgsql
security definer
set search_path = public, runtime, pg_temp
as $$
declare
  v_settlement_id uuid;
begin
  insert into runtime.shadow_settlements(
    question_id, run_id, projection_id, reality_gate_run_id, learning_delta_id,
    t0_known_as_of, t0_question_hash, t0_context_hash, t0_projection_hash,
    settlement_status, next_review_at, payload, authority
  ) values (
    p_question_id, p_run_id, p_projection_id, p_reality_gate_run_id, p_learning_delta_id,
    p_t0_known_as_of, p_t0_question_hash, p_t0_context_hash, p_t0_projection_hash,
    p_settlement_status, p_next_review_at, p_payload, 'RESEARCH'
  ) returning settlement_id into v_settlement_id;
  return v_settlement_id;
end;
$$;

create or replace function public.yci0_rp0_read_shadow_settlements(p_question_id text)
returns setof runtime.shadow_settlements
language sql
security definer
set search_path = public, runtime, pg_temp
as $$
  select * from runtime.shadow_settlements
  where question_id = p_question_id
  order by t0_known_as_of desc, created_at desc;
$$;

revoke all on function public.yci0_rp0_bind_evidence(text,uuid,uuid,uuid,uuid,text,timestamptz,text,jsonb) from public, anon, authenticated;
revoke all on function public.yci0_rp0_read_evidence_bindings(text) from public, anon, authenticated;
revoke all on function public.yci0_rp0_insert_shadow_settlement(text,uuid,uuid,uuid,uuid,timestamptz,text,text,text,text,timestamptz,jsonb) from public, anon, authenticated;
revoke all on function public.yci0_rp0_read_shadow_settlements(text) from public, anon, authenticated;

grant execute on function public.yci0_rp0_bind_evidence(text,uuid,uuid,uuid,uuid,text,timestamptz,text,jsonb) to service_role;
grant execute on function public.yci0_rp0_read_evidence_bindings(text) to service_role;
grant execute on function public.yci0_rp0_insert_shadow_settlement(text,uuid,uuid,uuid,uuid,timestamptz,text,text,text,text,timestamptz,jsonb) to service_role;
grant execute on function public.yci0_rp0_read_shadow_settlements(text) to service_role;
