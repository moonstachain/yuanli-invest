-- Private broker-paper coordinator candidate. No account binding is provisioned
-- and this migration does not enable the Edge entry, a PaperGrant or trading.
-- Trusted reader facts must originate from accepted native CTP adapters. SQL
-- admission verifies binding/inclusion/shape; it does not contact a broker.
create table gold2_paper.runtime_bindings (
  environment text not null check (environment = 'SIMNOW_FIRST_NORMAL'),
  account_id text not null check (account_id ~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'),
  robot_id bigint not null check (robot_id > 0),
  source_sha256 text not null check (source_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  reader_source_sha256 text not null check (reader_source_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  active boolean not null default false,
  check (source_sha256 <> reader_source_sha256),
  primary key (environment, account_id)
);
create table gold2_paper.account_execution_state (
  environment text not null check (environment = 'SIMNOW_FIRST_NORMAL'),
  account_id text not null,
  version bigint not null default 0 check (version >= 0),
  pending_claim_id text,
  owner_robot_id bigint,
  position_quantity integer not null default 0 check (position_quantity in (0,1)),
  position_origin_claim_id text,
  phase text not null default 'FLAT' check (phase in ('FLAT','CLAIMED','SUBMIT_ATTEMPTED','HELD','FROZEN')),
  broker_evidence_id text,
  ledger_root_hash text not null default repeat('0',64) check (ledger_root_hash ~ '^([0-9a-f]{64}|sha256:[0-9a-f]{64})$'),
  ledger_sequence integer not null default 0 check (ledger_sequence >= 0),
  submit_attempted_at timestamptz,
  freeze_reason text,
  updated_at timestamptz not null default clock_timestamp(),
  check ((position_quantity=0 and position_origin_claim_id is null) or (position_quantity=1 and position_origin_claim_id is not null)),
  check ((pending_claim_id is null and owner_robot_id is null) or (pending_claim_id is not null and owner_robot_id is not null)),
  primary key (environment, account_id)
);
create table gold2_paper.command_claims_v2 (
  command_id text primary key,
  claim_id text not null unique,
  environment text not null check (environment = 'SIMNOW_FIRST_NORMAL'),
  account_id text not null,
  robot_id bigint not null check (robot_id > 0),
  source_sha256 text not null check (source_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  contract_hash text not null check (contract_hash ~ '^sha256:[0-9a-f]{64}$'),
  action text not null check (action in ('OPEN_LONG','CLOSE_LONG')),
  instrument text not null check (instrument ~ '^au[0-9]{4}$'),
  position_origin_claim_id text,
  broker_evidence_id text not null,
  claimed_at timestamptz not null,
  check ((action='OPEN_LONG' and position_origin_claim_id is null) or (action='CLOSE_LONG' and position_origin_claim_id is not null))
);
create table gold2_paper.broker_evidence_v2 (
  evidence_id text primary key,
  environment text not null check (environment = 'SIMNOW_FIRST_NORMAL'),
  account_id text not null,
  robot_id bigint not null check (robot_id > 0),
  source_sha256 text not null check (source_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  kind text not null check (kind in ('PRE_CLAIM','TERMINAL')),
  observed_at timestamptz not null,
  raw_sha256 text not null check (raw_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  facts_sha256 text not null check (facts_sha256 ~ '^sha256:[0-9a-f]{64}$'),
  facts jsonb not null check (jsonb_typeof(facts)='object'),
  received_at timestamptz not null
);
create table gold2_paper.claim_events_v2 (
  environment text not null,
  account_id text not null,
  version bigint not null check (version > 0),
  claim_id text,
  kind text not null check (kind in ('CLAIMED','SUBMIT_RECORDED','TERMINAL_RECORDED','FROZEN')),
  ledger_root_hash text not null check (ledger_root_hash ~ '^sha256:[0-9a-f]{64}$'),
  ledger_sequence integer not null check (ledger_sequence > 0),
  broker_evidence_id text,
  state_json jsonb not null,
  received_at timestamptz not null,
  primary key (environment, account_id, version)
);

alter table gold2_paper.account_execution_state add constraint account_execution_pending_claim_v2_fk
 foreign key(pending_claim_id) references gold2_paper.command_claims_v2(claim_id);
alter table gold2_paper.account_execution_state add constraint account_execution_origin_claim_v2_fk
 foreign key(position_origin_claim_id) references gold2_paper.command_claims_v2(claim_id);

alter table gold2_paper.runtime_bindings enable row level security;
alter table gold2_paper.account_execution_state enable row level security;
alter table gold2_paper.command_claims_v2 enable row level security;
alter table gold2_paper.broker_evidence_v2 enable row level security;
alter table gold2_paper.claim_events_v2 enable row level security;
revoke all on gold2_paper.runtime_bindings, gold2_paper.account_execution_state,
 gold2_paper.command_claims_v2, gold2_paper.broker_evidence_v2, gold2_paper.claim_events_v2 from public, anon, authenticated;
-- Runtime/reader bindings are administrator-provisioned, never supplied by a
-- runtime HMAC principal or changed by the service_role RPC service.
grant select on gold2_paper.runtime_bindings to service_role;
grant select,insert,update on gold2_paper.account_execution_state to service_role;
grant select,insert on gold2_paper.command_claims_v2, gold2_paper.broker_evidence_v2, gold2_paper.claim_events_v2 to service_role;
create trigger command_claims_v2_append_only before update or delete on gold2_paper.command_claims_v2
 for each row execute function gold2_paper.reject_history_mutation();
create trigger broker_evidence_v2_append_only before update or delete on gold2_paper.broker_evidence_v2
 for each row execute function gold2_paper.reject_history_mutation();
create trigger claim_events_v2_append_only before update or delete on gold2_paper.claim_events_v2
 for each row execute function gold2_paper.reject_history_mutation();

create function gold2_paper.exact_json_keys_v2(p_value jsonb,p_keys text[])
returns boolean language sql immutable security invoker set search_path='' as $$
 select coalesce(jsonb_typeof(p_value)='object' and
  (select array_agg(k order by k) from jsonb_object_keys(p_value) k)=
  (select array_agg(k order by k) from unnest(p_keys) k),false);
$$;
create function gold2_paper.require_binding_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_reader boolean default false)
returns void language plpgsql stable security invoker set search_path='' as $$
begin
 if p_environment is distinct from 'SIMNOW_FIRST_NORMAL' or not exists (
  select 1 from gold2_paper.runtime_bindings b where b.environment=p_environment and b.account_id=p_account_id
   and b.robot_id=p_robot_id and b.active and
   case when p_reader then b.reader_source_sha256=p_source_sha256 else b.source_sha256=p_source_sha256 end
 ) then raise exception using errcode='22023',message='GOLD2_BOUND_IDENTITY_DENIED'; end if;
end;
$$;
create function gold2_paper.account_reply_v2(p_state gold2_paper.account_execution_state,p_robot_id bigint,p_source_sha256 text,p_status text,p_claim_id text default null,p_command_id text default null,p_claimed boolean default false)
returns jsonb language sql stable security invoker set search_path='' as $$
 select jsonb_build_object('source','external_account_coordinator_v2','status',p_status,'claimed',p_claimed,
 'environment',p_state.environment,'account_id',p_state.account_id,'robot_id',p_robot_id,'source_sha256',p_source_sha256,
 'version',p_state.version,'phase',p_state.phase,'pending_claim_id',p_state.pending_claim_id,
 'claim_id',coalesce(p_claim_id,p_state.pending_claim_id),'command_id',p_command_id,
 'position_quantity',p_state.position_quantity,'position_origin_claim_id',p_state.position_origin_claim_id,
 'ledger_root_hash',p_state.ledger_root_hash,'ledger_sequence',p_state.ledger_sequence,
 'freeze_reason',p_state.freeze_reason,'updated_at',p_state.updated_at);
$$;
create function gold2_paper.require_ledger_v2(p_account_id text,p_robot_id bigint,p_root text,p_sequence integer,p_kind text,p_command_id text,p_data jsonb)
returns void language plpgsql security invoker set search_path='' as $$
declare v_event jsonb;
begin
 if p_root is null or p_root !~ '^sha256:[0-9a-f]{64}$' or p_sequence is null or p_sequence<1 then
  raise exception using errcode='22023',message='GOLD2_LEDGER_REFERENCE_DENIED'; end if;
 perform 1 from gold2_paper.ledger_heads h where h.account_id=p_account_id and h.robot_id=p_robot_id
  and h.environment='SIMNOW_FIRST_NORMAL' and h.root_hash=p_root and h.last_sequence=p_sequence for share;
 if not found then raise exception using errcode='22023',message='GOLD2_LEDGER_HEAD_NOT_ANCHORED'; end if;
 select e.event_json into v_event from gold2_paper.ledger_events e where e.account_id=p_account_id
  and e.robot_id=p_robot_id and e.sequence=p_sequence and e.event_hash=p_root;
 if not found or v_event->>'kind' is distinct from p_kind
  or (p_command_id is not null and v_event->>'command_id' is distinct from p_command_id)
  or not coalesce((v_event->'data') @> p_data,false)
  or (v_event->>'at')::timestamptz>clock_timestamp()
  or (v_event->>'at')::timestamptz<clock_timestamp()-interval '30 seconds' then
  raise exception using errcode='22023',message='GOLD2_LEDGER_EVENT_PROOF_DENIED'; end if;
end;
$$;

create function public.gold2_paper_ingest_broker_evidence_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_evidence_id text,p_kind text,p_observed_at timestamptz,p_raw_sha256 text,p_facts_sha256 text,p_facts jsonb,p_facts_canonical text,p_raw_canonical text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v_existing gold2_paper.broker_evidence_v2%rowtype; v_party jsonb; v_key text; v_min bigint; v_max bigint;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 if p_evidence_id is null or p_evidence_id !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or p_kind is null or p_kind not in ('PRE_CLAIM','TERMINAL') or p_observed_at is null
  or p_observed_at>clock_timestamp() or p_observed_at<clock_timestamp()-interval '30 seconds'
  or p_raw_sha256 is null or p_raw_sha256 !~ '^sha256:[0-9a-f]{64}$'
  or p_facts_sha256 is null or p_facts_sha256 !~ '^sha256:[0-9a-f]{64}$'
  or not gold2_paper.exact_json_keys_v2(p_facts,array['command_id','claim_id','instrument','action','order_id','order_status','filled_quantity','position_quantity','pending_order_count','reconciliation','raw_account_sha256','raw_orders_sha256','raw_trades_sha256','raw_positions_sha256'])
  or jsonb_typeof(p_facts->'command_id') is distinct from 'string'
  or (p_facts->>'command_id') !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or jsonb_typeof(p_facts->'instrument') is distinct from 'string'
  or jsonb_typeof(p_facts->'action') is distinct from 'string'
  or jsonb_typeof(p_facts->'order_status') is distinct from 'string'
  or (p_facts->>'instrument') !~ '^au[0-9]{4}$' or p_facts->>'action' not in ('OPEN_LONG','CLOSE_LONG')
  or p_facts->'filled_quantity' not in ('0'::jsonb,'1'::jsonb) or p_facts->'position_quantity' not in ('0'::jsonb,'1'::jsonb)
  or p_facts->'pending_order_count' <> '0'::jsonb then
  raise exception using errcode='22023',message='GOLD2_BROKER_EVIDENCE_SHAPE_DENIED'; end if;
 if p_facts_canonical is null or p_raw_canonical is null
  or octet_length(p_facts_canonical)>65536 or octet_length(p_raw_canonical)>1024
  or p_facts_canonical::jsonb is distinct from p_facts
  or p_raw_canonical::jsonb is distinct from jsonb_build_object(
   'raw_account_sha256',p_facts->>'raw_account_sha256','raw_orders_sha256',p_facts->>'raw_orders_sha256',
   'raw_trades_sha256',p_facts->>'raw_trades_sha256','raw_positions_sha256',p_facts->>'raw_positions_sha256')
  or 'sha256:'||encode(sha256(convert_to(p_facts_canonical,'UTF8')),'hex') is distinct from p_facts_sha256
  or 'sha256:'||encode(sha256(convert_to(p_raw_canonical,'UTF8')),'hex') is distinct from p_raw_sha256 then
  raise exception using errcode='22023',message='GOLD2_BROKER_EVIDENCE_HASH_MISMATCH'; end if;
 foreach v_key in array array['raw_account_sha256','raw_orders_sha256','raw_trades_sha256','raw_positions_sha256'] loop
  if jsonb_typeof(p_facts->v_key) is distinct from 'string' or (p_facts->>v_key) !~ '^sha256:[0-9a-f]{64}$' then
   raise exception using errcode='22023',message='GOLD2_BROKER_RAW_HASH_DENIED'; end if;
 end loop;
 if p_kind='PRE_CLAIM' and (p_facts->'claim_id'<>'null'::jsonb or p_facts->'order_id'<>'null'::jsonb
  or p_facts->>'order_status' is distinct from 'NONE' or p_facts->'filled_quantity'<>'0'::jsonb) then
  raise exception using errcode='22023',message='GOLD2_PRE_CLAIM_TRUTH_DENIED'; end if;
 if p_kind='TERMINAL' and (jsonb_typeof(p_facts->'claim_id') is distinct from 'string'
  or (p_facts->>'claim_id') !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or jsonb_typeof(p_facts->'order_id') is distinct from 'string'
  or (p_facts->>'order_id') !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or p_facts->>'order_status' not in ('FILLED','REJECTED','CANCELED')
  or (p_facts->>'filled_quantity')::integer <> case when p_facts->>'order_status'='FILLED' then 1 else 0 end) then
  raise exception using errcode='22023',message='GOLD2_TERMINAL_ORDER_TRUTH_REQUIRED'; end if;
 if not gold2_paper.exact_json_keys_v2(p_facts->'reconciliation',array['broker','execution','ledger','expected']) then
  raise exception using errcode='22023',message='GOLD2_FOUR_WAY_REQUIRED'; end if;
 for v_party in select value from jsonb_each(p_facts->'reconciliation') loop
  if not gold2_paper.exact_json_keys_v2(v_party,array['cash_cents','available_cents','frozen_margin_cents','position_quantity','filled_quantity'])
   or v_party->'position_quantity' is distinct from p_facts->'position_quantity'
   or v_party->'filled_quantity' is distinct from p_facts->'filled_quantity' then
   raise exception using errcode='22023',message='GOLD2_FOUR_WAY_QUANTITY_DENIED'; end if;
  foreach v_key in array array['cash_cents','available_cents','frozen_margin_cents'] loop
   if jsonb_typeof(v_party->v_key) is distinct from 'number' or (v_party->>v_key) !~ '^[0-9]+$'
    or (v_party->>v_key)::numeric > 9007199254740991 then
    raise exception using errcode='22023',message='GOLD2_FOUR_WAY_AMOUNT_DENIED'; end if;
  end loop;
 end loop;
 foreach v_key in array array['cash_cents','available_cents','frozen_margin_cents'] loop
  select min((value->>v_key)::bigint),max((value->>v_key)::bigint) into v_min,v_max from jsonb_each(p_facts->'reconciliation');
  if v_max-v_min>1 then raise exception using errcode='22023',message='GOLD2_FOUR_WAY_AMOUNT_MISMATCH'; end if;
 end loop;
 insert into gold2_paper.broker_evidence_v2 values(p_evidence_id,p_environment,p_account_id,p_robot_id,p_source_sha256,p_kind,p_observed_at,p_raw_sha256,p_facts_sha256,p_facts,clock_timestamp()) on conflict do nothing;
 select * into v_existing from gold2_paper.broker_evidence_v2 where evidence_id=p_evidence_id;
 if v_existing.environment is distinct from p_environment or v_existing.account_id is distinct from p_account_id
  or v_existing.robot_id is distinct from p_robot_id or v_existing.source_sha256 is distinct from p_source_sha256
  or v_existing.kind is distinct from p_kind or v_existing.observed_at is distinct from p_observed_at
  or v_existing.raw_sha256 is distinct from p_raw_sha256 or v_existing.facts_sha256 is distinct from p_facts_sha256
  or v_existing.facts is distinct from p_facts then raise exception using errcode='22023',message='GOLD2_BROKER_EVIDENCE_CONFLICT'; end if;
 return jsonb_build_object('source','bound_broker_reader_evidence_v2','status','EVIDENCE_RECORDED','evidence_id',p_evidence_id,
  'facts_sha256',p_facts_sha256,'raw_sha256',p_raw_sha256,'received_at',v_existing.received_at);
end;
$$;
create function public.gold2_paper_read_broker_evidence_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_evidence_id text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare v gold2_paper.broker_evidence_v2%rowtype;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 select * into v from gold2_paper.broker_evidence_v2 where evidence_id=p_evidence_id and environment=p_environment and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256;
 if not found then return null; end if;
 return to_jsonb(v);
end;
$$;
create function gold2_paper.require_evidence_v2(p_environment text,p_account_id text,p_robot_id bigint,p_evidence_id text,p_kind text,p_command_id text,p_claim_id text,p_instrument text,p_action text)
returns gold2_paper.broker_evidence_v2 language plpgsql stable security invoker set search_path='' as $$
declare v gold2_paper.broker_evidence_v2%rowtype;
begin
 select e.* into v from gold2_paper.broker_evidence_v2 e join gold2_paper.runtime_bindings b
  on b.environment=e.environment and b.account_id=e.account_id and b.robot_id=e.robot_id and b.reader_source_sha256=e.source_sha256 and b.active
  where e.environment=p_environment and e.account_id=p_account_id and e.robot_id=p_robot_id and e.evidence_id=p_evidence_id;
 if not found or v.kind is distinct from p_kind or v.observed_at>clock_timestamp()
  or v.observed_at<clock_timestamp()-interval '30 seconds' or v.facts->>'command_id' is distinct from p_command_id
  or v.facts->>'claim_id' is distinct from p_claim_id or v.facts->>'instrument' is distinct from p_instrument
  or v.facts->>'action' is distinct from p_action or v.facts->'pending_order_count'<>'0'::jsonb then
  raise exception using errcode='22023',message='GOLD2_BOUND_BROKER_EVIDENCE_REQUIRED'; end if;
 return v;
end;
$$;

create function public.gold2_paper_read_account_state_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; v_command text;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id;
 if not found then
  v.environment:=p_environment;v.account_id:=p_account_id;v.version:=0;v.phase:='FLAT';v.position_quantity:=0;v.ledger_sequence:=0;v.ledger_root_hash:=repeat('0',64);v.updated_at:=clock_timestamp();
 else select command_id into v_command from gold2_paper.command_claims_v2 where claim_id=v.pending_claim_id; end if;
 return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'ACCOUNT_READ',null,v_command);
end;
$$;
create function public.gold2_paper_read_claim_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_command_id text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; v_claim gold2_paper.command_claims_v2%rowtype; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 v_reply:=public.gold2_paper_read_account_state_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into v_claim from gold2_paper.command_claims_v2 where command_id=p_command_id and environment=p_environment and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256;
 if not found then return v_reply || jsonb_build_object('status','CLAIM_NOT_FOUND','claim_id',null,'command_id',p_command_id); end if;
 return v_reply || jsonb_build_object('status','CLAIM_READ','claim_id',v_claim.claim_id,'command_id',p_command_id,
  'contract_hash',v_claim.contract_hash,'action',v_claim.action,'instrument',v_claim.instrument,'claimed_at',v_claim.claimed_at);
end;
$$;

create function public.gold2_paper_claim_order_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_command_id text,p_contract_hash text,p_action text,p_instrument text,p_position_origin_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; c gold2_paper.command_claims_v2%rowtype; e gold2_paper.broker_evidence_v2%rowtype; v_id text; v_status text; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 if p_expected_version is null or p_expected_version<0 or p_command_id is null or p_command_id !~ '^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or p_contract_hash is null or p_contract_hash !~ '^sha256:[0-9a-f]{64}$' or p_action is null or p_action not in ('OPEN_LONG','CLOSE_LONG')
  or p_instrument is null or p_instrument !~ '^au[0-9]{4}$' then raise exception using errcode='22023',message='GOLD2_CLAIM_V2_SHAPE_DENIED'; end if;
 insert into gold2_paper.account_execution_state(environment,account_id) values(p_environment,p_account_id) on conflict do nothing;
 -- All coordinator mutations acquire the account row first, regardless of
 -- robot or command. Ledger locks are acquired afterwards, in this order.
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 select * into c from gold2_paper.command_claims_v2 where command_id=p_command_id;
 if found then
  v_status:=case when c.environment=p_environment and c.account_id=p_account_id and c.robot_id=p_robot_id
   and c.source_sha256=p_source_sha256 and c.contract_hash=p_contract_hash and c.action=p_action and c.instrument=p_instrument
   and c.position_origin_claim_id is not distinct from p_position_origin_claim_id then 'ALREADY_CLAIMED' else 'CONFLICT' end;
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,v_status,case when v_status='ALREADY_CLAIMED' then c.claim_id else null end,p_command_id);
 end if;
 if exists(select 1 from gold2_paper.order_claims where command_id=p_command_id) then
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'LEGACY_COMMAND_CONSUMED',null,p_command_id); end if;
 if v.version<>p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',null,p_command_id); end if;
 if v.pending_claim_id is not null then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'ACCOUNT_BUSY',null,p_command_id); end if;
 if v.freeze_reason is not null or v.phase='FROZEN' then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'ACCOUNT_FROZEN',null,p_command_id); end if;
 if p_action='OPEN_LONG' then
  if v.freeze_reason is not null or v.phase='FROZEN' then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'ACCOUNT_FROZEN',null,p_command_id); end if;
  if v.position_quantity<>0 or p_position_origin_claim_id is not null then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'OPEN_POSITION_DENIED',null,p_command_id); end if;
 else
  if v.position_quantity<>1 or p_position_origin_claim_id is distinct from v.position_origin_claim_id then
   return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CLOSE_ORIGIN_DENIED',null,p_command_id); end if;
  if not exists(select 1 from gold2_paper.command_claims_v2 where claim_id=v.position_origin_claim_id and action='OPEN_LONG' and instrument=p_instrument and account_id=p_account_id and environment=p_environment) then
   return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CLOSE_INSTRUMENT_DENIED',null,p_command_id); end if;
 end if;
 e:=gold2_paper.require_evidence_v2(p_environment,p_account_id,p_robot_id,p_broker_evidence_id,'PRE_CLAIM',p_command_id,null,p_instrument,p_action);
 if (e.facts->>'position_quantity')::integer<>v.position_quantity then raise exception using errcode='22023',message='GOLD2_PRE_CLAIM_POSITION_DRIFT'; end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'OrderClaimRequested',p_command_id,
  jsonb_build_object('source_sha256',p_source_sha256,'contract_hash',p_contract_hash,'action',p_action,'instrument',p_instrument,'position_origin_claim_id',p_position_origin_claim_id,'broker_evidence_id',p_broker_evidence_id));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 v_id:='CLM-'||encode(sha256(convert_to(p_command_id,'UTF8')),'hex');
 insert into gold2_paper.command_claims_v2 values(p_command_id,v_id,p_environment,p_account_id,p_robot_id,p_source_sha256,p_contract_hash,p_action,p_instrument,p_position_origin_claim_id,p_broker_evidence_id,clock_timestamp())
  on conflict(command_id) do nothing returning * into c;
 if not found then
  -- Global permanent command IDs also serialize across different account
  -- rows. Losing an INSERT race never authorizes the second submission.
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CONFLICT',null,p_command_id);
 end if;
 update gold2_paper.account_execution_state set version=version+1,pending_claim_id=v_id,owner_robot_id=p_robot_id,
  phase='CLAIMED',broker_evidence_id=p_broker_evidence_id,ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,
  submit_attempted_at=null,updated_at=clock_timestamp() where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CLAIMED',v_id,p_command_id,true);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,v_id,'CLAIMED',p_ledger_root_hash,p_ledger_sequence,p_broker_evidence_id,v_reply,clock_timestamp());
 return v_reply;
end;
$$;

create function public.gold2_paper_record_submit_attempt_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; c gold2_paper.command_claims_v2%rowtype; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 if not found then raise exception using errcode='22023',message='GOLD2_ACCOUNT_NOT_CLAIMED'; end if;
 select * into c from gold2_paper.command_claims_v2 where claim_id=p_claim_id and environment=p_environment and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256;
 if not found then raise exception using errcode='22023',message='GOLD2_CLAIM_OWNER_DENIED'; end if;
 if v.version is distinct from p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',p_claim_id,c.command_id); end if;
 if v.pending_claim_id is distinct from p_claim_id or v.owner_robot_id is distinct from p_robot_id or v.phase<>'CLAIMED' or v.submit_attempted_at is not null then
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'SUBMIT_STATE_DENIED',p_claim_id,c.command_id); end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'OrderSubmitAttempted',c.command_id,jsonb_build_object('source_sha256',p_source_sha256,'claim_id',p_claim_id));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 update gold2_paper.account_execution_state set version=version+1,phase='SUBMIT_ATTEMPTED',submit_attempted_at=clock_timestamp(),
  ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,updated_at=clock_timestamp()
  where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'SUBMIT_RECORDED',p_claim_id,c.command_id);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,p_claim_id,'SUBMIT_RECORDED',p_ledger_root_hash,p_ledger_sequence,null,v_reply,clock_timestamp());
 return v_reply;
end;
$$;
create function public.gold2_paper_record_terminal_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; c gold2_paper.command_claims_v2%rowtype; e gold2_paper.broker_evidence_v2%rowtype; v_qty integer; v_filled integer; v_reply jsonb; v_origin text;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 if not found then raise exception using errcode='22023',message='GOLD2_ACCOUNT_NOT_CLAIMED'; end if;
 select * into c from gold2_paper.command_claims_v2 where claim_id=p_claim_id and environment=p_environment and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256;
 if not found then raise exception using errcode='22023',message='GOLD2_CLAIM_OWNER_DENIED'; end if;
 if v.version is distinct from p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',p_claim_id,c.command_id); end if;
 if v.pending_claim_id is distinct from p_claim_id or v.owner_robot_id is distinct from p_robot_id or v.submit_attempted_at is null
  or v.phase not in ('SUBMIT_ATTEMPTED','FROZEN') then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'TERMINAL_STATE_DENIED',p_claim_id,c.command_id); end if;
 e:=gold2_paper.require_evidence_v2(p_environment,p_account_id,p_robot_id,p_broker_evidence_id,'TERMINAL',c.command_id,p_claim_id,c.instrument,c.action);
 if e.observed_at<v.submit_attempted_at then raise exception using errcode='22023',message='GOLD2_TERMINAL_PREDATES_SUBMISSION'; end if;
 v_filled:=(e.facts->>'filled_quantity')::integer;
 v_qty:=case when v_filled=0 then v.position_quantity when c.action='OPEN_LONG' then 1 else 0 end;
 if (c.action='OPEN_LONG' and v.position_quantity<>0) or (c.action='CLOSE_LONG' and (v.position_quantity<>1 or c.position_origin_claim_id is distinct from v.position_origin_claim_id))
  or (e.facts->>'position_quantity')::integer<>v_qty then raise exception using errcode='22023',message='GOLD2_TERMINAL_POSITION_DRIFT'; end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'OrderTerminalReconciled',c.command_id,
  jsonb_build_object('source_sha256',p_source_sha256,'claim_id',p_claim_id,'broker_evidence_id',p_broker_evidence_id));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 v_origin:=case when v_qty=0 then null when c.action='OPEN_LONG' and v_filled=1 then p_claim_id else v.position_origin_claim_id end;
 update gold2_paper.account_execution_state set version=version+1,pending_claim_id=null,owner_robot_id=null,position_quantity=v_qty,
  position_origin_claim_id=v_origin,phase=case when freeze_reason is not null then 'FROZEN' when v_qty=1 then 'HELD' else 'FLAT' end,
  broker_evidence_id=p_broker_evidence_id,ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,
  submit_attempted_at=null,updated_at=clock_timestamp() where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'TERMINAL_RECORDED',p_claim_id,c.command_id);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,p_claim_id,'TERMINAL_RECORDED',p_ledger_root_hash,p_ledger_sequence,p_broker_evidence_id,v_reply,clock_timestamp());
 return v_reply;
end;
$$;
create function public.gold2_paper_freeze_account_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text,p_reason_code text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; v_command text; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 if p_reason_code is null or p_reason_code !~ '^[A-Z][A-Z0-9_]{2,95}$' then raise exception using errcode='22023',message='GOLD2_FREEZE_REASON_DENIED'; end if;
 insert into gold2_paper.account_execution_state(environment,account_id) values(p_environment,p_account_id) on conflict do nothing;
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 select command_id into v_command from gold2_paper.command_claims_v2 where claim_id=v.pending_claim_id;
 if v.version is distinct from p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',p_claim_id,v_command); end if;
 if v.pending_claim_id is distinct from p_claim_id then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'FREEZE_CLAIM_DENIED',p_claim_id,v_command); end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'AccountFrozen',v_command,
  jsonb_build_object('source_sha256',p_source_sha256,'claim_id',p_claim_id,'reason_code',p_reason_code));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 update gold2_paper.account_execution_state set version=version+1,phase='FROZEN',freeze_reason=p_reason_code,
  ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,updated_at=clock_timestamp()
  where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'FROZEN',p_claim_id,v_command);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,p_claim_id,'FROZEN',p_ledger_root_hash,p_ledger_sequence,null,v_reply,clock_timestamp());
 return v_reply;
end;
$$;

-- Retire the vulnerable command-only SQL entry as well as the Edge op.
create or replace function public.gold2_paper_claim_order_v1(p_command_id text,p_account_id text,p_robot_id bigint,p_contract_hash text)
returns jsonb language plpgsql security invoker set search_path='' as $$
begin
 raise exception using errcode='22023',message='GOLD2_V1_CLAIM_PERMANENTLY_DISABLED';
end;
$$;

revoke execute on function gold2_paper.exact_json_keys_v2(jsonb,text[]) from public,anon,authenticated;
grant execute on function gold2_paper.exact_json_keys_v2(jsonb,text[]) to service_role;

revoke execute on function gold2_paper.require_binding_v2(text,text,bigint,text,boolean) from public,anon,authenticated;
grant execute on function gold2_paper.require_binding_v2(text,text,bigint,text,boolean) to service_role;

revoke execute on function gold2_paper.account_reply_v2(gold2_paper.account_execution_state,bigint,text,text,text,text,boolean) from public,anon,authenticated;
grant execute on function gold2_paper.account_reply_v2(gold2_paper.account_execution_state,bigint,text,text,text,text,boolean) to service_role;

revoke execute on function gold2_paper.require_ledger_v2(text,bigint,text,integer,text,text,jsonb) from public,anon,authenticated;
grant execute on function gold2_paper.require_ledger_v2(text,bigint,text,integer,text,text,jsonb) to service_role;

revoke execute on function gold2_paper.require_evidence_v2(text,text,bigint,text,text,text,text,text,text) from public,anon,authenticated;
grant execute on function gold2_paper.require_evidence_v2(text,text,bigint,text,text,text,text,text,text) to service_role;

revoke execute on function public.gold2_paper_ingest_broker_evidence_v2(text,text,bigint,text,text,text,timestamptz,text,text,jsonb,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_ingest_broker_evidence_v2(text,text,bigint,text,text,text,timestamptz,text,text,jsonb,text,text) to service_role;

revoke execute on function public.gold2_paper_read_broker_evidence_v2(text,text,bigint,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_read_broker_evidence_v2(text,text,bigint,text,text) to service_role;

revoke execute on function public.gold2_paper_read_account_state_v2(text,text,bigint,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_read_account_state_v2(text,text,bigint,text) to service_role;

revoke execute on function public.gold2_paper_read_claim_v2(text,text,bigint,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_read_claim_v2(text,text,bigint,text,text) to service_role;

revoke execute on function public.gold2_paper_claim_order_v2(text,text,bigint,text,bigint,text,integer,text,text,text,text,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_claim_order_v2(text,text,bigint,text,bigint,text,integer,text,text,text,text,text,text) to service_role;

revoke execute on function public.gold2_paper_record_submit_attempt_v2(text,text,bigint,text,bigint,text,integer,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_record_submit_attempt_v2(text,text,bigint,text,bigint,text,integer,text) to service_role;

revoke execute on function public.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) to service_role;

revoke execute on function public.gold2_paper_freeze_account_v2(text,text,bigint,text,bigint,text,integer,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_freeze_account_v2(text,text,bigint,text,bigint,text,integer,text,text) to service_role;

revoke execute on function public.gold2_paper_claim_order_v1(text,text,bigint,text) from public,anon,authenticated,service_role;

revoke insert on gold2_paper.order_claims from service_role;
