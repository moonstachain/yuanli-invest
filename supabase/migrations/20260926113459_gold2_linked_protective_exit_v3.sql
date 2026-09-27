-- Candidate protocol only. No keys, binding, enable flag or broker call.
-- An unresolved parent remains permanently reserved; a child may only reduce
-- its independently observed exact one-lot native fill. No lease/TTL release.
create table gold2_paper.native_evidence_v3 (
 evidence_id text primary key,
 environment text not null check(environment='SIMNOW_FIRST_NORMAL'),
 account_id text not null, robot_id bigint not null check(robot_id>0),
 source_sha256 text not null check(source_sha256~'^sha256:[0-9a-f]{64}$'),
 kind text not null check(kind in ('NATIVE_ORDER','PAIRED_TERMINAL')),
 observed_at timestamptz not null,
 facts_sha256 text not null check(facts_sha256~'^sha256:[0-9a-f]{64}$'),
 facts jsonb not null, received_at timestamptz not null
);
create table gold2_paper.linked_exits_v3 (
 child_claim_id text primary key references gold2_paper.command_claims_v2(claim_id),
 parent_claim_id text not null unique references gold2_paper.command_claims_v2(claim_id),
 environment text not null check(environment='SIMNOW_FIRST_NORMAL'), account_id text not null,
 parent_order_id text not null, broker_evidence_id text not null references gold2_paper.native_evidence_v3(evidence_id),
 created_at timestamptz not null
);
alter table gold2_paper.native_evidence_v3 enable row level security;
alter table gold2_paper.linked_exits_v3 enable row level security;
revoke all on gold2_paper.native_evidence_v3,gold2_paper.linked_exits_v3 from public,anon,authenticated;
grant select,insert on gold2_paper.native_evidence_v3,gold2_paper.linked_exits_v3 to service_role;
create trigger native_evidence_v3_append_only before update or delete on gold2_paper.native_evidence_v3
 for each row execute function gold2_paper.reject_history_mutation();
create trigger linked_exits_v3_append_only before update or delete on gold2_paper.linked_exits_v3
 for each row execute function gold2_paper.reject_history_mutation();

create function public.gold2_paper_ingest_native_evidence_v3(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,
 p_evidence_id text,p_kind text,p_observed_at timestamptz,p_facts_sha256 text,p_facts jsonb,p_facts_canonical text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare e gold2_paper.native_evidence_v3%rowtype; f jsonb:=p_facts; k text; party jsonb; v_min numeric; v_max numeric;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 if p_evidence_id is null or p_evidence_id!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or p_kind is null or p_kind not in ('NATIVE_ORDER','PAIRED_TERMINAL')
  or p_observed_at is null or p_observed_at>clock_timestamp() or p_observed_at<clock_timestamp()-interval '30 seconds'
  or not gold2_paper.exact_json_keys_v2(f,array['command_id','claim_id','instrument','action','order_id','order_status',
   'filled_quantity','position_quantity','pending_order_count','parent_claim_id','parent_order_id','reconciliation',
   'order_binding_sha256','raw_identity_sha256','raw_account_sha256','raw_orders_sha256','raw_trades_sha256','raw_positions_sha256'])
  or p_facts_canonical is null or octet_length(p_facts_canonical)>65536 or p_facts_canonical::jsonb is distinct from f
  or 'sha256:'||encode(sha256(convert_to(p_facts_canonical,'UTF8')),'hex') is distinct from p_facts_sha256 then
  raise exception using errcode='22023',message='GOLD2_NATIVE_SHAPE_OR_HASH_DENIED'; end if;
 foreach k in array array['command_id','claim_id','order_id'] loop
  if jsonb_typeof(f->k) is distinct from 'string' or (f->>k)!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$' then
   raise exception using errcode='22023',message='GOLD2_NATIVE_ORDER_BINDING_REQUIRED'; end if;
 end loop;
 foreach k in array array['order_binding_sha256','raw_identity_sha256','raw_account_sha256','raw_orders_sha256','raw_trades_sha256','raw_positions_sha256'] loop
  if jsonb_typeof(f->k) is distinct from 'string' or (f->>k)!~'^sha256:[0-9a-f]{64}$' then
   raise exception using errcode='22023',message='GOLD2_NATIVE_RAW_HASH_REQUIRED'; end if;
 end loop;
 if jsonb_typeof(f->'instrument') is distinct from 'string' or (f->>'instrument')!~'^au[0-9]{4}$'
  or jsonb_typeof(f->'action') is distinct from 'string' or jsonb_typeof(f->'order_status') is distinct from 'string'
  or f->>'action' not in ('OPEN_LONG','CLOSE_LONG') or f->>'order_status' not in ('PENDING','FILLED','REJECTED','CANCELED')
  or f->'filled_quantity' not in ('0'::jsonb,'1'::jsonb) or f->'position_quantity' not in ('0'::jsonb,'1'::jsonb)
  or f->'pending_order_count' not in ('0'::jsonb,'1'::jsonb)
  or (f->>'order_status'='FILLED' and f->'filled_quantity'<>'1'::jsonb)
  or (f->>'order_status'<>'FILLED' and f->'filled_quantity'<>'0'::jsonb)
  or (f->>'order_status'<>'PENDING' and f->'pending_order_count'<>'0'::jsonb) then
  raise exception using errcode='22023',message='GOLD2_NATIVE_QUANTITY_OR_STATUS_DENIED'; end if;
 if p_kind='NATIVE_ORDER' then
  if f->'parent_claim_id'<>'null'::jsonb or f->'parent_order_id'<>'null'::jsonb or f->'reconciliation'<>'null'::jsonb then
   raise exception using errcode='22023',message='GOLD2_NATIVE_IS_NOT_FOUR_WAY'; end if;
 else
  if f->>'action'<>'CLOSE_LONG' or f->>'order_status'<>'FILLED' or f->'position_quantity'<>'0'::jsonb
   or f->'pending_order_count'<>'0'::jsonb or jsonb_typeof(f->'parent_claim_id') is distinct from 'string'
   or (f->>'parent_claim_id')!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
   or jsonb_typeof(f->'parent_order_id') is distinct from 'string'
   or (f->>'parent_order_id')!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$' or f->>'parent_order_id'=f->>'order_id'
   or not gold2_paper.exact_json_keys_v2(f->'reconciliation',array['broker','execution','ledger','expected']) then
   raise exception using errcode='22023',message='GOLD2_PAIRED_FOUR_WAY_REQUIRED'; end if;
  if (select count(distinct value->>'producer_id') from jsonb_each(f->'reconciliation'))<>4 then
   raise exception using errcode='22023',message='GOLD2_PAIRED_INDEPENDENT_PRODUCERS_REQUIRED'; end if;
  for party in select value from jsonb_each(f->'reconciliation') loop
   if not gold2_paper.exact_json_keys_v2(party,array['producer_id','proof_sha256','cash_cents','available_cents','frozen_margin_cents',
    'position_quantity','open_filled_quantity','close_filled_quantity','parent_order_id','child_order_id'])
    or jsonb_typeof(party->'producer_id') is distinct from 'string'
    or (party->>'producer_id')!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
    or jsonb_typeof(party->'proof_sha256') is distinct from 'string' or (party->>'proof_sha256')!~'^sha256:[0-9a-f]{64}$'
    or party->'position_quantity'<>'0'::jsonb or party->'open_filled_quantity'<>'1'::jsonb or party->'close_filled_quantity'<>'1'::jsonb
    or party->>'parent_order_id' is distinct from f->>'parent_order_id' or party->>'child_order_id' is distinct from f->>'order_id' then
    raise exception using errcode='22023',message='GOLD2_PAIRED_PARTY_DENIED'; end if;
   foreach k in array array['cash_cents','available_cents','frozen_margin_cents'] loop
    if jsonb_typeof(party->k) is distinct from 'number' or (party->>k)!~'^[0-9]+$' or (party->>k)::numeric>9007199254740991 then
     raise exception using errcode='22023',message='GOLD2_PAIRED_AMOUNT_DENIED'; end if;
   end loop;
  end loop;
  foreach k in array array['cash_cents','available_cents','frozen_margin_cents'] loop
   select min((value->>k)::numeric),max((value->>k)::numeric) into v_min,v_max from jsonb_each(f->'reconciliation');
   if v_max-v_min>1 then raise exception using errcode='22023',message='GOLD2_PAIRED_FOUR_WAY_DRIFT'; end if;
  end loop;
 end if;
 insert into gold2_paper.native_evidence_v3 values(p_evidence_id,p_environment,p_account_id,p_robot_id,p_source_sha256,
  p_kind,p_observed_at,p_facts_sha256,f,clock_timestamp()) on conflict do nothing;
 select * into e from gold2_paper.native_evidence_v3 where evidence_id=p_evidence_id;
 if e.environment is distinct from p_environment or e.account_id is distinct from p_account_id or e.robot_id is distinct from p_robot_id
  or e.source_sha256 is distinct from p_source_sha256 or e.kind is distinct from p_kind or e.observed_at is distinct from p_observed_at
  or e.facts_sha256 is distinct from p_facts_sha256 or e.facts is distinct from f then
  raise exception using errcode='22023',message='GOLD2_NATIVE_EVIDENCE_CONFLICT'; end if;
 return to_jsonb(e);
end;
$$;
create function public.gold2_paper_read_native_evidence_v3(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_evidence_id text)
returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare e gold2_paper.native_evidence_v3%rowtype;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 select * into e from gold2_paper.native_evidence_v3 where evidence_id=p_evidence_id and environment=p_environment
  and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256;
 if not found then return null; end if;
 return to_jsonb(e);
end;
$$;
create function gold2_paper.require_native_v3(p_environment text,p_account_id text,p_robot_id bigint,p_evidence_id text,
 p_kind text,p_command_id text,p_claim_id text,p_instrument text,p_action text)
returns gold2_paper.native_evidence_v3 language plpgsql stable security invoker set search_path='' as $$
declare e gold2_paper.native_evidence_v3%rowtype;
begin
 select n.* into e from gold2_paper.native_evidence_v3 n join gold2_paper.runtime_bindings b on b.environment=n.environment
  and b.account_id=n.account_id and b.robot_id=n.robot_id and b.active and b.reader_source_sha256=n.source_sha256
  where n.evidence_id=p_evidence_id and n.environment=p_environment and n.account_id=p_account_id and n.robot_id=p_robot_id;
 if not found or e.kind is distinct from p_kind or e.observed_at>clock_timestamp() or e.observed_at<clock_timestamp()-interval '30 seconds'
  or e.facts->>'command_id' is distinct from p_command_id or e.facts->>'claim_id' is distinct from p_claim_id
  or e.facts->>'instrument' is distinct from p_instrument or e.facts->>'action' is distinct from p_action then
  raise exception using errcode='22023',message='GOLD2_BOUND_NATIVE_EVIDENCE_REQUIRED'; end if;
 return e;
end;
$$;
create function public.gold2_paper_claim_linked_exit_v3(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,
 p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_command_id text,p_contract_hash text,p_parent_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; parent gold2_paper.command_claims_v2%rowtype;
 c gold2_paper.command_claims_v2%rowtype; e gold2_paper.native_evidence_v3%rowtype; original jsonb; request jsonb; v_id text; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 if p_command_id is null or p_command_id!~'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$'
  or p_contract_hash is null or p_contract_hash!~'^sha256:[0-9a-f]{64}$' then
  raise exception using errcode='22023',message='GOLD2_LINKED_CLAIM_SHAPE_DENIED'; end if;
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 if not found then raise exception using errcode='22023',message='GOLD2_LINKED_PARENT_REQUIRED'; end if;
 select * into c from gold2_paper.command_claims_v2 where command_id=p_command_id;
 if found then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'LINKED_EXIT_CONSUMED',null,p_command_id); end if;
 if exists(select 1 from gold2_paper.linked_exits_v3 where parent_claim_id=p_parent_claim_id)
  or exists(select 1 from gold2_paper.order_claims where command_id=p_command_id) then
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'LINKED_EXIT_CONSUMED',null,p_command_id); end if;
 if v.version is distinct from p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',null,p_command_id); end if;
 select * into parent from gold2_paper.command_claims_v2 where claim_id=p_parent_claim_id and environment=p_environment
  and account_id=p_account_id and robot_id=p_robot_id and source_sha256=p_source_sha256 and action='OPEN_LONG';
 if not found or v.pending_claim_id is distinct from p_parent_claim_id or v.owner_robot_id is distinct from p_robot_id
  or v.phase not in ('SUBMIT_ATTEMPTED','FROZEN') or v.submit_attempted_at is null or v.position_quantity<>0 then
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'LINKED_EXIT_DENIED',null,p_command_id); end if;
 e:=gold2_paper.require_native_v3(p_environment,p_account_id,p_robot_id,p_broker_evidence_id,'NATIVE_ORDER',parent.command_id,parent.claim_id,parent.instrument,'OPEN_LONG');
 if e.observed_at<v.submit_attempted_at or e.facts->>'order_status'<>'FILLED' or e.facts->'filled_quantity'<>'1'::jsonb
  or e.facts->'position_quantity'<>'1'::jsonb or e.facts->'pending_order_count'<>'0'::jsonb then
  raise exception using errcode='22023',message='GOLD2_LINKED_EXACT_NATIVE_FILL_REQUIRED'; end if;
 if not exists(select 1 from gold2_paper.ledger_events where account_id=p_account_id and robot_id=p_robot_id
  and event_json->>'command_id'=parent.command_id and event_json->>'kind'='OrderSubmitted'
  and event_json->'data'->>'order_id'=e.facts->>'order_id') then
  raise exception using errcode='22023',message='GOLD2_LINKED_PARENT_ORDER_BINDING_MISMATCH'; end if;
 select event_json->'data'->'body' into original from gold2_paper.ledger_events where account_id=p_account_id and robot_id=p_robot_id
  and event_json->>'command_id'=parent.command_id and event_json->>'kind'='ActionAdmitted';
 if original is null or original->>'action' is distinct from 'OPEN_LONG' or original->>'contract' is distinct from parent.instrument
  or original->>'contract_hash' is distinct from parent.contract_hash or original->>'account_id' is distinct from p_account_id
  or original->>'environment' is distinct from p_environment or original->'quantity' is distinct from '1'::jsonb
  or jsonb_typeof(original->'stop_price') is distinct from 'string' or (original->>'stop_price')::numeric<=0
  or original->>'action_contract_id' is null then
  raise exception using errcode='22023',message='GOLD2_LINKED_ORIGINAL_AUTHORITY_REQUIRED'; end if;
 select event_json->'data' into request from gold2_paper.ledger_events where account_id=p_account_id and robot_id=p_robot_id and sequence=p_ledger_sequence;
 if request->>'reason' is null or request->>'reason' not in ('EXIT_STOP','EXIT_ROLL','EXIT_TIME','EXIT_TREND') then
  raise exception using errcode='22023',message='GOLD2_LINKED_EXIT_REASON_DENIED'; end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'LinkedExitClaimRequested',p_command_id,
  jsonb_build_object('source_sha256',p_source_sha256,'contract_hash',p_contract_hash,'parent_claim_id',parent.claim_id,
   'origin_command_id',parent.command_id,'origin_order_id',e.facts->>'order_id','origin_action_contract_id',original->>'action_contract_id',
   'instrument',parent.instrument,'action','CLOSE_LONG','broker_evidence_id',p_broker_evidence_id));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 v_id:='CLM-'||encode(sha256(convert_to(p_command_id,'UTF8')),'hex');
 insert into gold2_paper.command_claims_v2 values(p_command_id,v_id,p_environment,p_account_id,p_robot_id,p_source_sha256,
  p_contract_hash,'CLOSE_LONG',parent.instrument,parent.claim_id,p_broker_evidence_id,clock_timestamp()) on conflict do nothing returning * into c;
 if not found then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CONFLICT',null,p_command_id); end if;
 insert into gold2_paper.linked_exits_v3 values(v_id,parent.claim_id,p_environment,p_account_id,e.facts->>'order_id',p_broker_evidence_id,clock_timestamp());
 update gold2_paper.account_execution_state set version=version+1,pending_claim_id=v_id,owner_robot_id=p_robot_id,
  position_quantity=1,position_origin_claim_id=parent.claim_id,phase='CLAIMED',freeze_reason='LINKED_EXIT_PAIR_RECONCILIATION_REQUIRED',
  broker_evidence_id=p_broker_evidence_id,ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,
  submit_attempted_at=null,updated_at=clock_timestamp() where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'CLAIMED',v_id,p_command_id,true);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,v_id,'CLAIMED',p_ledger_root_hash,p_ledger_sequence,p_broker_evidence_id,v_reply,clock_timestamp());
 return v_reply;
end;
$$;
-- A linked child cannot escape its paired evidence/freeze through legacy V2.
alter function public.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) set schema gold2_paper;
alter function gold2_paper.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) rename to record_terminal_base_v2;
create or replace function gold2_paper.record_terminal_base_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; c gold2_paper.command_claims_v2%rowtype; e gold2_paper.broker_evidence_v2%rowtype; v_qty integer; v_filled integer; v_reply jsonb; v_origin text;
begin
 if exists(select 1 from gold2_paper.linked_exits_v3 where child_claim_id=p_claim_id or parent_claim_id=p_claim_id) then
  raise exception using errcode='22023',message='GOLD2_LINKED_PAIR_PROTOCOL_REQUIRED'; end if;
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
create function public.gold2_paper_record_terminal_v2(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,
 p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
begin
 if exists(select 1 from gold2_paper.linked_exits_v3 where child_claim_id=p_claim_id or parent_claim_id=p_claim_id) then
  raise exception using errcode='22023',message='GOLD2_LINKED_PAIR_PROTOCOL_REQUIRED'; end if;
 return gold2_paper.record_terminal_base_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,p_expected_version,
  p_ledger_root_hash,p_ledger_sequence,p_claim_id,p_broker_evidence_id);
end;
$$;
create function public.gold2_paper_complete_linked_pair_v3(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text,
 p_expected_version bigint,p_ledger_root_hash text,p_ledger_sequence integer,p_claim_id text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare v gold2_paper.account_execution_state%rowtype; c gold2_paper.command_claims_v2%rowtype;
 link gold2_paper.linked_exits_v3%rowtype; e gold2_paper.native_evidence_v3%rowtype; v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into v from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 select * into c from gold2_paper.command_claims_v2 where claim_id=p_claim_id and environment=p_environment and account_id=p_account_id
  and robot_id=p_robot_id and source_sha256=p_source_sha256 and action='CLOSE_LONG';
 select * into link from gold2_paper.linked_exits_v3 where child_claim_id=p_claim_id and environment=p_environment and account_id=p_account_id;
 if c.claim_id is null or link.child_claim_id is null then raise exception using errcode='22023',message='GOLD2_LINKED_PAIR_BINDING_REQUIRED'; end if;
 if v.version is distinct from p_expected_version then return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'VERSION_CONFLICT',p_claim_id,c.command_id); end if;
 if v.pending_claim_id is distinct from p_claim_id or v.owner_robot_id is distinct from p_robot_id
  or v.position_quantity<>1 or v.position_origin_claim_id is distinct from link.parent_claim_id
  or v.phase not in ('SUBMIT_ATTEMPTED','FROZEN') or v.submit_attempted_at is null then
  return gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'PAIR_STATE_DENIED',p_claim_id,c.command_id); end if;
 e:=gold2_paper.require_native_v3(p_environment,p_account_id,p_robot_id,p_broker_evidence_id,'PAIRED_TERMINAL',c.command_id,c.claim_id,c.instrument,'CLOSE_LONG');
 if e.observed_at<v.submit_attempted_at or e.facts->>'parent_claim_id' is distinct from link.parent_claim_id
  or e.facts->>'parent_order_id' is distinct from link.parent_order_id then
  raise exception using errcode='22023',message='GOLD2_LINKED_PAIR_NATIVE_BINDING_MISMATCH'; end if;
 if not exists(select 1 from gold2_paper.ledger_events where account_id=p_account_id and robot_id=p_robot_id
  and event_json->>'command_id'=c.command_id and event_json->>'kind'='OrderSubmitted'
  and event_json->'data'->>'order_id'=e.facts->>'order_id') then
  raise exception using errcode='22023',message='GOLD2_LINKED_CHILD_ORDER_BINDING_MISMATCH'; end if;
 perform gold2_paper.require_ledger_v2(p_account_id,p_robot_id,p_ledger_root_hash,p_ledger_sequence,'LinkedPairReconciled',c.command_id,
  jsonb_build_object('source_sha256',p_source_sha256,'claim_id',c.claim_id,'parent_claim_id',link.parent_claim_id,'broker_evidence_id',p_broker_evidence_id));
 if p_ledger_sequence<=v.ledger_sequence then raise exception using errcode='22023',message='GOLD2_ACCOUNT_LEDGER_STALE'; end if;
 update gold2_paper.account_execution_state set version=version+1,pending_claim_id=null,owner_robot_id=null,position_quantity=0,
  position_origin_claim_id=null,phase='FROZEN',freeze_reason='LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED',
  broker_evidence_id=p_broker_evidence_id,ledger_root_hash=p_ledger_root_hash,ledger_sequence=p_ledger_sequence,
  submit_attempted_at=null,updated_at=clock_timestamp() where environment=p_environment and account_id=p_account_id returning * into v;
 v_reply:=gold2_paper.account_reply_v2(v,p_robot_id,p_source_sha256,'PAIR_RECORDED',p_claim_id,c.command_id);
 insert into gold2_paper.claim_events_v2 values(p_environment,p_account_id,v.version,p_claim_id,'FROZEN',p_ledger_root_hash,p_ledger_sequence,p_broker_evidence_id,v_reply,clock_timestamp());
 return v_reply;
end;
$$;
revoke execute on function public.gold2_paper_ingest_native_evidence_v3(text,text,bigint,text,text,text,timestamptz,text,jsonb,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_ingest_native_evidence_v3(text,text,bigint,text,text,text,timestamptz,text,jsonb,text) to service_role;
revoke execute on function public.gold2_paper_read_native_evidence_v3(text,text,bigint,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_read_native_evidence_v3(text,text,bigint,text,text) to service_role;
revoke execute on function gold2_paper.require_native_v3(text,text,bigint,text,text,text,text,text,text) from public,anon,authenticated;
grant execute on function gold2_paper.require_native_v3(text,text,bigint,text,text,text,text,text,text) to service_role;
revoke execute on function public.gold2_paper_claim_linked_exit_v3(text,text,bigint,text,bigint,text,integer,text,text,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_claim_linked_exit_v3(text,text,bigint,text,bigint,text,integer,text,text,text,text) to service_role;
revoke execute on function public.gold2_paper_complete_linked_pair_v3(text,text,bigint,text,bigint,text,integer,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_complete_linked_pair_v3(text,text,bigint,text,bigint,text,integer,text,text) to service_role;
revoke execute on function public.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_record_terminal_v2(text,text,bigint,text,bigint,text,integer,text,text) to service_role;
