-- GOLD2 broker-paper candidate only. Never run this migration as part of the
-- existing research pipeline. No grants for anon/authenticated and no paper
-- authority or broker connection are created by this schema.
create schema if not exists gold2_paper;
revoke all on schema gold2_paper from public, anon, authenticated;
grant usage on schema gold2_paper to service_role;

create table gold2_paper.signal_anchors (
  registry_id text not null,
  record_id text not null,
  record_sha256 text not null check (record_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  registry_root_sha256 text not null check (registry_root_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  decision_at timestamptz not null,
  recorded_at timestamptz not null,
  record_json jsonb not null check (jsonb_typeof(record_json) = 'object'),
  accepted_at timestamptz not null,
  primary key (registry_id, record_id)
);

create table gold2_paper.ledger_heads (
  account_id text not null,
  robot_id bigint not null check (robot_id > 0),
  environment text not null default 'SIMNOW_FIRST_NORMAL'
    check (environment = 'SIMNOW_FIRST_NORMAL'),
  last_sequence integer not null default 0 check (last_sequence >= 0),
  root_hash text not null default repeat('0', 64)
    check (root_hash ~ '^([0-9a-f]{64}|sha256:[0-9a-f]{64})$'),
  updated_at timestamptz not null default clock_timestamp(),
  primary key (account_id, robot_id)
);

create table gold2_paper.ledger_events (
  account_id text not null,
  robot_id bigint not null,
  sequence integer not null check (sequence > 0),
  event_json jsonb not null check (jsonb_typeof(event_json) = 'object'),
  event_hash text not null check (event_hash ~ '^sha256:[0-9a-f]{64}$'),
  previous_hash text not null check (previous_hash ~ '^([0-9a-f]{64}|sha256:[0-9a-f]{64})$'),
  accepted_at timestamptz not null,
  primary key (account_id, robot_id, sequence),
  foreign key (account_id, robot_id)
    references gold2_paper.ledger_heads(account_id, robot_id)
);

create table gold2_paper.order_claims (
  command_id text primary key,
  account_id text not null,
  robot_id bigint not null check (robot_id > 0),
  environment text not null check (environment = 'SIMNOW_FIRST_NORMAL'),
  contract_hash text not null check (contract_hash ~ '^sha256:[0-9a-f]{64}$'),
  claimed_at timestamptz not null
);

alter table gold2_paper.signal_anchors enable row level security;
alter table gold2_paper.ledger_heads enable row level security;
alter table gold2_paper.ledger_events enable row level security;
alter table gold2_paper.order_claims enable row level security;
-- No RLS policies: even an authenticated Supabase user cannot read these.
revoke all on all tables in schema gold2_paper from public, anon, authenticated;
grant select, insert on gold2_paper.signal_anchors to service_role;
grant select, insert, update on gold2_paper.ledger_heads to service_role;
grant select, insert on gold2_paper.ledger_events to service_role;
grant select, insert on gold2_paper.order_claims to service_role;

create function gold2_paper.reject_history_mutation()
returns trigger language plpgsql security invoker set search_path = '' as $$
begin
  raise exception using errcode = '22023', message = 'GOLD2_HISTORY_APPEND_ONLY';
end;
$$;
revoke execute on function gold2_paper.reject_history_mutation() from public, anon, authenticated;
create trigger signal_anchors_append_only before update or delete on gold2_paper.signal_anchors
  for each row execute function gold2_paper.reject_history_mutation();
create trigger ledger_events_append_only before update or delete on gold2_paper.ledger_events
  for each row execute function gold2_paper.reject_history_mutation();
create trigger order_claims_append_only before update or delete on gold2_paper.order_claims
  for each row execute function gold2_paper.reject_history_mutation();

-- The Edge entry checks the exact canonical JSON SHA and authenticates a
-- narrowly scoped client before invoking this service-role-only RPC. The
-- database supplies its own receipt time; caller timestamps are never proof.
create function public.gold2_paper_anchor_signal_v1(
  p_registry_id text, p_record_id text, p_record_sha256 text,
  p_registry_root_sha256 text, p_decision_at timestamptz,
  p_recorded_at timestamptz, p_record jsonb
) returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  v_existing gold2_paper.signal_anchors%rowtype;
  v_received timestamptz;
begin
  if p_registry_id is null or length(p_registry_id) not between 8 and 128
     or p_record_id is null or length(p_record_id) not between 8 and 128
     or p_record_sha256 !~ '^sha256:[0-9a-f]{64}$'
     or p_registry_root_sha256 !~ '^sha256:[0-9a-f]{64}$'
     or p_decision_at is null or p_recorded_at is null
     or p_record is null or jsonb_typeof(p_record) <> 'object'
     or p_record->>'registry_id' is distinct from p_registry_id
     or p_record->>'record_id' is distinct from p_record_id
     or (p_record->>'decision_at')::timestamptz is distinct from p_decision_at
     or (p_record->>'recorded_at')::timestamptz is distinct from p_recorded_at
  then
    raise exception using errcode = '22023', message = 'GOLD2_SIGNAL_SHAPE_DENIED';
  end if;
  if (p_decision_at at time zone 'Asia/Shanghai')::time <> time '08:30:00'
     or p_recorded_at < p_decision_at
  then
    raise exception using errcode = '22023', message = 'GOLD2_SIGNAL_TIME_DENIED';
  end if;

  select * into v_existing from gold2_paper.signal_anchors
    where registry_id = p_registry_id and record_id = p_record_id;
  if not found then
    v_received := clock_timestamp();
    if v_received < p_recorded_at or v_received >= p_decision_at + interval '1 minute'
       or v_received < p_decision_at
    then
      raise exception using errcode = '22023', message = 'GOLD2_SIGNAL_LATE_OR_FUTURE';
    end if;
    insert into gold2_paper.signal_anchors(
      registry_id, record_id, record_sha256, registry_root_sha256,
      decision_at, recorded_at, record_json, accepted_at
    ) values (
      p_registry_id, p_record_id, p_record_sha256, p_registry_root_sha256,
      p_decision_at, p_recorded_at, p_record, v_received
    ) on conflict do nothing;
    select * into v_existing from gold2_paper.signal_anchors
      where registry_id = p_registry_id and record_id = p_record_id;
  end if;
  if v_existing.record_sha256 is distinct from p_record_sha256
     or v_existing.registry_root_sha256 is distinct from p_registry_root_sha256
     or v_existing.decision_at is distinct from p_decision_at
     or v_existing.recorded_at is distinct from p_recorded_at
     or v_existing.record_json is distinct from p_record
  then
    raise exception using errcode = '22023', message = 'GOLD2_SIGNAL_CONFLICT';
  end if;
  return jsonb_build_object(
    'status', 'ANCHORED', 'registry_id', v_existing.registry_id,
    'record_id', v_existing.record_id,
    'record_sha256', v_existing.record_sha256,
    'registry_root_sha256', v_existing.registry_root_sha256,
    'decision_at', v_existing.decision_at,
    'recorded_at', v_existing.recorded_at,
    'anchor_received_at', v_existing.accepted_at
  );
end;
$$;

create function public.gold2_paper_read_signal_v1(p_registry_id text, p_record_id text)
returns jsonb language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object(
    'registry_id', a.registry_id, 'record_id', a.record_id,
    'record_sha256', a.record_sha256,
    'registry_root_sha256', a.registry_root_sha256,
    'decision_at', a.decision_at, 'recorded_at', a.recorded_at,
    'anchor_received_at', a.accepted_at, 'record', a.record_json
  ) from gold2_paper.signal_anchors a
  where a.registry_id = p_registry_id and a.record_id = p_record_id;
$$;

-- Full-prefix append is deliberate: every new receipt proves the remote
-- stream is an extension of the exact locally persisted event history.
-- Row lock serializes competing writers for one account/robot stream.
create function public.gold2_paper_append_ledger_v1(
  p_account_id text, p_robot_id bigint, p_events jsonb, p_root_hash text
) returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  v_head gold2_paper.ledger_heads%rowtype;
  v_existing jsonb;
  v_event jsonb;
  v_count integer;
  v_i integer;
  v_previous text := repeat('0', 64);
  v_accepted timestamptz;
begin
  if p_account_id is null or length(p_account_id) not between 1 and 128
     or p_robot_id is null or p_robot_id <= 0
     or p_events is null or jsonb_typeof(p_events) <> 'array'
     or octet_length(p_events::text) > 2097152
     or p_root_hash !~ '^sha256:[0-9a-f]{64}$'
  then
    raise exception using errcode = '22023', message = 'GOLD2_LEDGER_SHAPE_DENIED';
  end if;
  v_count := jsonb_array_length(p_events);
  if v_count < 1 or v_count > 10000 then
    raise exception using errcode = '22023', message = 'GOLD2_LEDGER_SIZE_DENIED';
  end if;
  insert into gold2_paper.ledger_heads(account_id, robot_id)
    values (p_account_id, p_robot_id) on conflict do nothing;
  select * into v_head from gold2_paper.ledger_heads
    where account_id = p_account_id and robot_id = p_robot_id for update;
  if v_count < v_head.last_sequence then
    raise exception using errcode = '22023', message = 'GOLD2_LEDGER_STALE_PREFIX';
  end if;
  for v_i in 1..v_count loop
    v_event := p_events -> (v_i - 1);
    if jsonb_typeof(v_event) <> 'object'
       or (v_event->>'sequence')::integer <> v_i
       or v_event->>'previous_hash' is distinct from v_previous
       or (v_event->>'event_hash') !~ '^sha256:[0-9a-f]{64}$'
    then
      raise exception using errcode = '22023', message = 'GOLD2_LEDGER_CHAIN_DENIED';
    end if;
    if v_i <= v_head.last_sequence then
      select e.event_json into v_existing from gold2_paper.ledger_events e
        where e.account_id = p_account_id and e.robot_id = p_robot_id
          and e.sequence = v_i;
      if not found or v_existing is distinct from v_event then
        raise exception using errcode = '22023', message = 'GOLD2_LEDGER_PREFIX_DIVERGED';
      end if;
    else
      insert into gold2_paper.ledger_events(
        account_id, robot_id, sequence, event_json, event_hash,
        previous_hash, accepted_at
      ) values (
        p_account_id, p_robot_id, v_i, v_event, v_event->>'event_hash',
        v_event->>'previous_hash', clock_timestamp()
      );
    end if;
    v_previous := v_event->>'event_hash';
  end loop;
  if v_previous <> p_root_hash then
    raise exception using errcode = '22023', message = 'GOLD2_LEDGER_ROOT_MISMATCH';
  end if;
  if v_count = v_head.last_sequence and p_root_hash <> v_head.root_hash then
    raise exception using errcode = '22023', message = 'GOLD2_LEDGER_HEAD_DIVERGED';
  end if;
  v_accepted := clock_timestamp();
  if v_count > v_head.last_sequence then
    update gold2_paper.ledger_heads set last_sequence = v_count,
      root_hash = p_root_hash, updated_at = v_accepted
      where account_id = p_account_id and robot_id = p_robot_id;
  else
    v_accepted := v_head.updated_at;
  end if;
  return jsonb_build_object(
    'source', 'external_append_only_ledger', 'accepted', true,
    'account_id', p_account_id, 'robot_id', p_robot_id,
    'last_sequence', v_count, 'root_hash', p_root_hash,
    'anchor_received_at', v_accepted
  );
end;
$$;

create function public.gold2_paper_read_ledger_v1(p_account_id text, p_robot_id bigint)
returns jsonb language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object(
    'account_id', h.account_id, 'robot_id', h.robot_id,
    'environment', h.environment, 'last_sequence', h.last_sequence,
    'root_hash', h.root_hash, 'anchor_received_at', h.updated_at
  ) from gold2_paper.ledger_heads h
  where h.account_id = p_account_id and h.robot_id = p_robot_id;
$$;

-- Permanent one-shot claim. A timeout is UNKNOWN to the caller; readback may
-- resolve it, but a duplicate never becomes a second claim or order license.
create function public.gold2_paper_claim_order_v1(
  p_command_id text, p_account_id text, p_robot_id bigint,
  p_contract_hash text
) returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  v_existing gold2_paper.order_claims%rowtype;
  v_inserted boolean := false;
begin
  if p_command_id is null or length(p_command_id) not between 8 and 128
     or p_account_id is null or length(p_account_id) not between 1 and 128
     or p_robot_id is null or p_robot_id <= 0
     or p_contract_hash !~ '^sha256:[0-9a-f]{64}$'
  then
    raise exception using errcode = '22023', message = 'GOLD2_CLAIM_SHAPE_DENIED';
  end if;
  insert into gold2_paper.order_claims(
    command_id, account_id, robot_id, environment, contract_hash, claimed_at
  ) values (
    p_command_id, p_account_id, p_robot_id, 'SIMNOW_FIRST_NORMAL',
    p_contract_hash, clock_timestamp()
  ) on conflict do nothing returning * into v_existing;
  v_inserted := found;
  if not v_inserted then
    select * into v_existing from gold2_paper.order_claims
      where command_id = p_command_id;
  end if;
  if v_existing.account_id is distinct from p_account_id
     or v_existing.robot_id is distinct from p_robot_id
     or v_existing.contract_hash is distinct from p_contract_hash
  then
    return jsonb_build_object('source', 'external_atomic_command_claim',
      'status', 'CONFLICT', 'claimed', false, 'command_id', p_command_id);
  end if;
  return jsonb_build_object(
    'source', 'external_atomic_command_claim',
    'status', case when v_inserted then 'CLAIMED' else 'ALREADY_CLAIMED' end,
    'claimed', v_inserted, 'command_id', v_existing.command_id,
    'account_id', v_existing.account_id, 'robot_id', v_existing.robot_id,
    'contract_hash', v_existing.contract_hash,
    'environment', v_existing.environment, 'claimed_at', v_existing.claimed_at
  );
end;
$$;

create function public.gold2_paper_read_claim_v1(p_command_id text)
returns jsonb language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object(
    'command_id', c.command_id, 'account_id', c.account_id,
    'robot_id', c.robot_id, 'contract_hash', c.contract_hash,
    'environment', c.environment, 'claimed_at', c.claimed_at
  ) from gold2_paper.order_claims c where c.command_id = p_command_id;
$$;

revoke execute on function public.gold2_paper_anchor_signal_v1(text,text,text,text,timestamptz,timestamptz,jsonb) from public, anon, authenticated;
revoke execute on function public.gold2_paper_read_signal_v1(text,text) from public, anon, authenticated;
revoke execute on function public.gold2_paper_append_ledger_v1(text,bigint,jsonb,text) from public, anon, authenticated;
revoke execute on function public.gold2_paper_read_ledger_v1(text,bigint) from public, anon, authenticated;
revoke execute on function public.gold2_paper_claim_order_v1(text,text,bigint,text) from public, anon, authenticated;
revoke execute on function public.gold2_paper_read_claim_v1(text) from public, anon, authenticated;
grant execute on function public.gold2_paper_anchor_signal_v1(text,text,text,text,timestamptz,timestamptz,jsonb) to service_role;
grant execute on function public.gold2_paper_read_signal_v1(text,text) to service_role;
grant execute on function public.gold2_paper_append_ledger_v1(text,bigint,jsonb,text) to service_role;
grant execute on function public.gold2_paper_read_ledger_v1(text,bigint) to service_role;
grant execute on function public.gold2_paper_claim_order_v1(text,text,bigint,text) to service_role;
grant execute on function public.gold2_paper_read_claim_v1(text) to service_role;
