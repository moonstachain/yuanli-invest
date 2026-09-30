-- Inert admission controls: no bindings, keys, policy rows or trading enable.
-- Administrator-provisioned identity persists across PID/path/source/key changes.
create table gold2_paper.reader_deployments_v4 (
 environment text not null check(environment='SIMNOW_FIRST_NORMAL'), account_id text not null,
 robot_id bigint not null check(robot_id>0), deployment_id text not null unique,
 reader_source_sha256 text not null check(reader_source_sha256~'^sha256:[0-9a-f]{64}$'),
 reader_process_id text not null check(reader_process_id~'^PID-[0-9]+$'),
 journal_path_sha256 text not null check(journal_path_sha256~'^sha256:[0-9a-f]{64}$'),
 isolation_receipt_sha256 text not null check(isolation_receipt_sha256~'^sha256:[0-9a-f]{64}$'),
 active boolean not null default false, expires_at timestamptz not null,
 primary key(environment,account_id)
);
create table gold2_paper.reader_bootstraps_v4 (
 environment text not null, account_id text not null, deployment_id text not null,
 scope_sha256 text not null check(scope_sha256~'^sha256:[0-9a-f]{64}$'), scope jsonb not null,
 received_at timestamptz not null,
 primary key(environment,account_id),
 foreign key(environment,account_id) references gold2_paper.reader_deployments_v4(environment,account_id)
);
create table gold2_paper.engineering_policies_v4 (
 environment text not null check(environment='SIMNOW_FIRST_NORMAL'), account_id text not null,
 robot_id bigint not null check(robot_id>0), case_id text not null unique,
 command_id text not null unique, contract_hash text not null check(contract_hash~'^sha256:[0-9a-f]{64}$'),
 instrument text not null check(instrument~'^au[0-9]{4}$'),
 round_trip_fee_upper_cny numeric not null check(round_trip_fee_upper_cny>=0),
 margin_one_lot_cny numeric not null check(margin_one_lot_cny>0),
 strategy_budget_cny numeric not null check(strategy_budget_cny>0 and strategy_budget_cny<=25000),
 risk_attestation_sha256 text not null check(risk_attestation_sha256~'^sha256:[0-9a-f]{64}$'),
 human_approval_ref text not null, program_approval_ref text not null,
 session_open_at timestamptz not null, session_close_at timestamptz not null,
 active boolean not null default false, expires_at timestamptz not null,
 primary key(environment,account_id)
);
create table gold2_paper.engineering_cases_v4 (
 environment text not null, account_id text not null, case_id text not null unique,
 command_id text not null unique, contract_hash text not null,
 body jsonb not null, broker_evidence_id text not null references gold2_paper.broker_evidence_v2(evidence_id),
 preparation jsonb not null, received_at timestamptz not null,
 primary key(environment,account_id),
 foreign key(environment,account_id) references gold2_paper.engineering_policies_v4(environment,account_id)
);
alter table gold2_paper.reader_deployments_v4 enable row level security;
alter table gold2_paper.reader_bootstraps_v4 enable row level security;
alter table gold2_paper.engineering_policies_v4 enable row level security;
alter table gold2_paper.engineering_cases_v4 enable row level security;
revoke all on gold2_paper.reader_deployments_v4,gold2_paper.reader_bootstraps_v4,
 gold2_paper.engineering_policies_v4,gold2_paper.engineering_cases_v4 from public,anon,authenticated,service_role;
grant select on gold2_paper.reader_deployments_v4,gold2_paper.engineering_policies_v4 to service_role;
grant select,insert on gold2_paper.reader_bootstraps_v4,gold2_paper.engineering_cases_v4 to service_role;
create trigger reader_bootstraps_v4_immutable before update or delete on gold2_paper.reader_bootstraps_v4
 for each row execute function gold2_paper.reject_history_mutation();
create trigger engineering_cases_v4_immutable before update or delete on gold2_paper.engineering_cases_v4
 for each row execute function gold2_paper.reject_history_mutation();

create function public.gold2_paper_admit_reader_bootstrap(p_environment text,p_account_id text,p_robot_id bigint,
 p_source_sha256 text,p_scope jsonb,p_scope_canonical text,p_scope_sha256 text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare d gold2_paper.reader_deployments_v4%rowtype; b gold2_paper.reader_bootstraps_v4%rowtype;
 s gold2_paper.account_execution_state%rowtype; v_now timestamptz:=clock_timestamp();
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 perform pg_advisory_xact_lock(hashtextextended('GOLD2_BOOTSTRAP:'||p_environment||':'||p_account_id,0));
 select * into d from gold2_paper.reader_deployments_v4
  where environment=p_environment and account_id=p_account_id;
 if not found or not d.active or d.expires_at<v_now or d.robot_id<>p_robot_id
  or d.reader_source_sha256<>p_source_sha256 then
  raise exception using errcode='22023',message='GOLD2_BOOTSTRAP_DEPLOYMENT_DENIED'; end if;
 if not gold2_paper.exact_json_keys_v2(p_scope,array['environment','account_id','robot_id','reader_source_sha256',
  'reader_process_id','journal_path_sha256','bootstrap_attempt_nonce'])
  or p_scope_canonical is null or length(p_scope_canonical)>8192 or p_scope_canonical::jsonb is distinct from p_scope
  or 'sha256:'||encode(sha256(convert_to(p_scope_canonical,'UTF8')),'hex') is distinct from p_scope_sha256
  or p_scope->>'environment' is distinct from d.environment or p_scope->>'account_id' is distinct from d.account_id
  or p_scope->'robot_id' is distinct from to_jsonb(d.robot_id)
  or p_scope->>'reader_source_sha256' is distinct from d.reader_source_sha256
  or p_scope->>'reader_process_id' is distinct from d.reader_process_id
  or p_scope->>'journal_path_sha256' is distinct from d.journal_path_sha256
  or p_scope->>'bootstrap_attempt_nonce' is null or (p_scope->>'bootstrap_attempt_nonce')!~'^[0-9a-f]{64}$' then
  raise exception using errcode='22023',message='GOLD2_BOOTSTRAP_SCOPE_DENIED'; end if;
 select * into b from gold2_paper.reader_bootstraps_v4 where environment=p_environment and account_id=p_account_id;
 if found then
  if b.scope_sha256 is distinct from p_scope_sha256 or b.scope is distinct from p_scope then
   raise exception using errcode='22023',message='GOLD2_BOOTSTRAP_ALREADY_CONSUMED'; end if;
 else
  select * into s from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
  if not found or s.phase<>'FLAT' or s.position_quantity<>0 or s.pending_claim_id is not null or s.freeze_reason is not null
   or exists(select 1 from gold2_paper.broker_evidence_v2 where environment=p_environment and account_id=p_account_id)
   or exists(select 1 from gold2_paper.native_evidence_v3 where environment=p_environment and account_id=p_account_id) then
   raise exception using errcode='22023',message='GOLD2_BOOTSTRAP_HISTORY_OR_UNKNOWN_DENIED'; end if;
  insert into gold2_paper.reader_bootstraps_v4 values(p_environment,p_account_id,d.deployment_id,p_scope_sha256,p_scope,v_now) returning * into b;
 end if;
 -- Exact retry returns the original observed_at; never refresh into new authority.
 return jsonb_build_object('source','independent_reader_journal_bootstrap_admission_v3','status','FRESH_ONE_SHOT_BOOTSTRAP_ACCEPTED',
  'environment',p_environment,'account_id',p_account_id,'robot_id',p_robot_id,'source_sha256',p_source_sha256,
  'deployment_id',b.deployment_id,'scope_sha256',b.scope_sha256,'observed_at',b.received_at);
end;
$$;

create function public.gold2_paper_read_reader_bootstrap(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare b gold2_paper.reader_bootstraps_v4%rowtype;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256,true);
 select * into b from gold2_paper.reader_bootstraps_v4 where environment=p_environment and account_id=p_account_id;
 if not found then return null; end if;
 return jsonb_build_object('source','independent_reader_bootstrap_readback_v4','status','BOOTSTRAP_READ_ONLY',
  'environment',p_environment,'account_id',p_account_id,'robot_id',p_robot_id,'source_sha256',p_source_sha256,
  'deployment_id',b.deployment_id,'scope_sha256',b.scope_sha256,'observed_at',b.received_at);
end;
$$;

create function public.gold2_paper_prepare_engineering_case(p_environment text,p_account_id text,p_robot_id bigint,
 p_source_sha256 text,p_body jsonb,p_body_canonical text,p_broker_evidence_id text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare p gold2_paper.engineering_policies_v4%rowtype; c gold2_paper.engineering_cases_v4%rowtype;
 s gold2_paper.account_execution_state%rowtype; e gold2_paper.broker_evidence_v2%rowtype;
 v_now timestamptz:=clock_timestamp(); v_price numeric; v_stop numeric; v_deadline timestamptz; v_decision timestamptz;
 v_reply jsonb;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into s from gold2_paper.account_execution_state where environment=p_environment and account_id=p_account_id for update;
 if not found or s.phase<>'FLAT' or s.position_quantity<>0 or s.pending_claim_id is not null or s.freeze_reason is not null then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_ACCOUNT_NOT_READY'; end if;
 select * into p from gold2_paper.engineering_policies_v4 where environment=p_environment and account_id=p_account_id;
 if not found or not p.active or p.expires_at<v_now or p.robot_id<>p_robot_id
  or not v_now between p.session_open_at and p.session_close_at then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_POLICY_OR_SESSION_DENIED'; end if;
 if p_body_canonical is null or length(p_body_canonical)>16384 or p_body_canonical::jsonb is distinct from p_body-'contract_hash'
  or 'sha256:'||encode(sha256(convert_to(p_body_canonical,'UTF8')),'hex') is distinct from p.contract_hash
  or p_body->>'contract_hash' is distinct from p.contract_hash or p_body->>'command_id' is distinct from p.command_id
  or p_body->>'contract' is distinct from p.instrument or p_body->>'environment' is distinct from p_environment
  or p_body->>'account_id' is distinct from p_account_id or p_body->'robot_id' is distinct from to_jsonb(p_robot_id)
  or p_body->>'human_approval_ref' is distinct from p.human_approval_ref
  or p_body->>'program_approval_ref' is distinct from p.program_approval_ref
  or p_body->>'action' is distinct from 'OPEN_LONG' or p_body->>'reason' is distinct from 'ENGINEERING_TEST'
  or p_body->'quantity' is distinct from '1'::jsonb
  or p_body->'live_execution_authorized' is distinct from 'false'::jsonb
  or p_body->'real_capital_movement_authorized' is distinct from 'false'::jsonb then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_CONTRACT_DENIED'; end if;
 v_price:=(p_body->>'limit_price')::numeric; v_stop:=(p_body->>'stop_price')::numeric;
 v_decision:=(p_body->>'decision_at')::timestamptz; v_deadline:=(p_body->>'exit_not_after_at')::timestamptz;
 if v_price is null or v_stop is null or v_price::text in ('NaN','Infinity','-Infinity') or v_stop::text in ('NaN','Infinity','-Infinity')
  or v_price-v_stop<=0 or v_price-v_stop>4 or (v_price-v_stop)*1000+200+p.round_trip_fee_upper_cny>least(5000,p.strategy_budget_cny)
  or abs(v_price-(p_body->>'reference_price')::numeric)>0.10
  or v_deadline is null or v_decision is null or not v_now between v_decision and v_deadline
  or v_deadline<=v_decision or v_deadline>v_decision+interval '120 seconds' or v_deadline>p.session_close_at
  or (v_deadline at time zone 'Asia/Shanghai')::date<>(v_decision at time zone 'Asia/Shanghai')::date
  or (p_body->>'roll_not_after_at')::timestamptz>v_deadline
  or (p_body->>'expires_at')::timestamptz>v_deadline
  or p.strategy_budget_cny>25000*(p_body->>'credit_multiplier')::numeric*(p_body->>'volatility_multiplier')::numeric then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_R2_LIMIT_DENIED'; end if;
 select * into c from gold2_paper.engineering_cases_v4 where environment=p_environment and account_id=p_account_id;
 if found then
  if c.body is distinct from p_body then raise exception using errcode='22023',message='GOLD2_ENGINEERING_ALREADY_PREPARED'; end if;
  return c.preparation;
 end if;
 e:=gold2_paper.require_evidence_v2(p_environment,p_account_id,p_robot_id,p_broker_evidence_id,'PRE_CLAIM',p.command_id,null,p.instrument,'OPEN_LONG');
 if e.facts->'position_quantity'<>'0'::jsonb or e.facts->'pending_order_count'<>'0'::jsonb
  or p.margin_one_lot_cny>1500000 or p.margin_one_lot_cny>(e.facts->'reconciliation'->'broker'->>'available_cents')::numeric/100 then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_BROKER_NOT_FLAT_OR_MARGIN'; end if;
 if not exists(select 1 from gold2_paper.ledger_events where account_id=p_account_id and robot_id=p_robot_id
  and event_json->>'kind'='StrategyAllocationInitialized'
  and event_json->'data'->>'approval_ref'=p.human_approval_ref) then
  raise exception using errcode='22023',message='GOLD2_ENGINEERING_SUBLEDGER_REQUIRED'; end if;
 v_reply:=jsonb_build_object('source','independent_gold2_engineering_preparation_v4','status','ENGINEERING_PREPARED',
  'environment',p_environment,'account_id',p_account_id,'robot_id',p_robot_id,'source_sha256',p_source_sha256,
  'case_id',p.case_id,'command_id',p.command_id,'contract_hash',p.contract_hash,'instrument',p.instrument,
  'round_trip_fee_upper_cny',p.round_trip_fee_upper_cny::text,'strategy_budget_cny',p.strategy_budget_cny::text,
  'risk_attestation_sha256',p.risk_attestation_sha256,'broker_evidence_id',p_broker_evidence_id,
  'exit_on_first_verified_fill',true,'counts_as_strategy_return_sample',false,'starts_formal_30_day_clock',false,
  'observed_at',v_now);
 insert into gold2_paper.engineering_cases_v4 values(p_environment,p_account_id,p.case_id,p.command_id,p.contract_hash,p_body,
  p_broker_evidence_id,v_reply,v_now);
 return v_reply;
end;
$$;
create function public.gold2_paper_read_engineering_case(p_environment text,p_account_id text,p_robot_id bigint,p_source_sha256 text)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare c gold2_paper.engineering_cases_v4%rowtype;
begin
 perform gold2_paper.require_binding_v2(p_environment,p_account_id,p_robot_id,p_source_sha256);
 select * into c from gold2_paper.engineering_cases_v4 where environment=p_environment and account_id=p_account_id;
 if not found then return null; end if;
 return c.preparation||jsonb_build_object('source','independent_gold2_engineering_readback_v4','status','ENGINEERING_READ_ONLY');
end;
$$;
revoke execute on function public.gold2_paper_read_engineering_case(text,text,bigint,text),
 public.gold2_paper_admit_reader_bootstrap(text,text,bigint,text,jsonb,text,text),
 public.gold2_paper_read_reader_bootstrap(text,text,bigint,text),
 public.gold2_paper_prepare_engineering_case(text,text,bigint,text,jsonb,text,text) from public,anon,authenticated;
grant execute on function public.gold2_paper_read_engineering_case(text,text,bigint,text),
 public.gold2_paper_admit_reader_bootstrap(text,text,bigint,text,jsonb,text,text),
 public.gold2_paper_read_reader_bootstrap(text,text,bigint,text),
 public.gold2_paper_prepare_engineering_case(text,text,bigint,text,jsonb,text,text) to service_role;
