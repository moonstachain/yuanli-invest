-- Run after both migrations as administrator. All DIAGNOSTIC fixtures roll
-- back, including temporary functions/bindings/claims. This is database
-- behavior proof only; it does not prove a broker reader or CTP connection.
begin;
create temporary table gold2_coordinator_probe_results(check_name text primary key, passed boolean not null);
grant select,insert on gold2_coordinator_probe_results to service_role;
create function pg_temp.gold2_probe_canonical(p jsonb) returns text language plpgsql immutable as $$
declare v text;
begin
 case jsonb_typeof(p)
 when 'object' then select '{'||coalesce(string_agg(to_jsonb(key)::text||':'||pg_temp.gold2_probe_canonical(value),',' order by key collate "C"),'')||'}' into v from jsonb_each(p);
 when 'array' then select '['||coalesce(string_agg(pg_temp.gold2_probe_canonical(value),',' order by ord),'')||']' into v from jsonb_array_elements(p) with ordinality e(value,ord);
 else v:=p::text; end case;
 return v;
end;
$$;
create function pg_temp.gold2_probe_hash(p jsonb) returns text language sql immutable as $$
 select 'sha256:'||encode(sha256(convert_to(pg_temp.gold2_probe_canonical(p),'UTF8')),'hex');
$$;
create function pg_temp.gold2_probe_assert(p_name text,p_condition boolean) returns void language plpgsql as $$
begin
 if p_condition is distinct from true then raise exception 'PROBE_FAILED %',p_name; end if;
 insert into gold2_coordinator_probe_results values(p_name,true);
end;
$$;
create function pg_temp.gold2_probe_expect_denied(p_name text,p_sql text,p_message text) returns void language plpgsql as $$
declare denied boolean:=false;
begin
 begin execute p_sql;
 exception when others then
  if SQLERRM<>p_message then raise exception 'UNEXPECTED_ERROR %: %',p_name,SQLERRM; end if;
  denied:=true;
 end;
 perform pg_temp.gold2_probe_assert(p_name,denied);
end;
$$;
create function pg_temp.gold2_probe_anchor(p_account text,p_kind text,p_command text,p_data jsonb)
returns jsonb language plpgsql as $$
declare v_events jsonb; v_seq integer; v_previous text; v_event jsonb; v_root text;
begin
 select coalesce(jsonb_agg(event_json order by sequence),'[]'::jsonb) into v_events from gold2_paper.ledger_events where account_id=p_account and robot_id=2147483000;
 v_seq:=jsonb_array_length(v_events)+1;
 v_previous:=case when v_seq=1 then repeat('0',64) else v_events->(v_seq-2)->>'event_hash' end;
 v_event:=jsonb_build_object('sequence',v_seq,'kind',p_kind,'command_id',p_command,'at',clock_timestamp(),'data',p_data,'previous_hash',v_previous);
 v_root:=pg_temp.gold2_probe_hash(v_event);
 v_event:=v_event||jsonb_build_object('event_hash',v_root);
 perform public.gold2_paper_append_ledger_v1(p_account,2147483000,v_events||jsonb_build_array(v_event),v_root);
 return jsonb_build_object('root',v_root,'sequence',v_seq);
end;
$$;
create function pg_temp.gold2_probe_facts(p_command text,p_claim text,p_action text,p_qty integer,p_filled integer,p_status text)
returns jsonb language plpgsql as $$
declare v_party jsonb; h text:='sha256:'||repeat('6',64);
begin
 v_party:=jsonb_build_object('cash_cents',500000000,'available_cents',490000000,'frozen_margin_cents',10000000,'position_quantity',p_qty,'filled_quantity',p_filled);
 return jsonb_build_object('command_id',p_command,'claim_id',p_claim,'instrument','au2612','action',p_action,
  'order_id',case when p_status='NONE' then null else 'DIAGNOSTIC-ORDER-'||p_command end,
  'order_status',p_status,'filled_quantity',p_filled,'position_quantity',p_qty,'pending_order_count',0,
  'reconciliation',jsonb_build_object('broker',v_party,'execution',v_party,'ledger',v_party,'expected',v_party),
  'raw_account_sha256',h,'raw_orders_sha256',h,'raw_trades_sha256',h,'raw_positions_sha256',h);
end;
$$;
create function pg_temp.gold2_probe_evidence(p_account text,p_id text,p_kind text,p_facts jsonb)
returns void language plpgsql as $$
declare v_raw jsonb;
begin
 v_raw:=jsonb_build_object('raw_account_sha256',p_facts->>'raw_account_sha256','raw_orders_sha256',p_facts->>'raw_orders_sha256',
  'raw_trades_sha256',p_facts->>'raw_trades_sha256','raw_positions_sha256',p_facts->>'raw_positions_sha256');
 perform public.gold2_paper_ingest_broker_evidence_v2('SIMNOW_FIRST_NORMAL',p_account,2147483000,'sha256:'||repeat('b',64),p_id,p_kind,clock_timestamp(),
  pg_temp.gold2_probe_hash(v_raw),pg_temp.gold2_probe_hash(p_facts),p_facts,pg_temp.gold2_probe_canonical(p_facts),pg_temp.gold2_probe_canonical(v_raw));
end;
$$;
insert into gold2_paper.runtime_bindings values
 ('SIMNOW_FIRST_NORMAL','DIAGNOSTIC-COORDINATOR-NOT-BROKER-1',2147483000,'sha256:'||repeat('a',64),'sha256:'||repeat('b',64),true),
 ('SIMNOW_FIRST_NORMAL','DIAGNOSTIC-COORDINATOR-NOT-BROKER-2',2147483000,'sha256:'||repeat('a',64),'sha256:'||repeat('b',64),true),
 ('SIMNOW_FIRST_NORMAL','DIAGNOSTIC-COORDINATOR-NOT-BROKER-3',2147483000,'sha256:'||repeat('a',64),'sha256:'||repeat('b',64),true);
set local role service_role;
do $$
declare a text:='DIAGNOSTIC-COORDINATOR-NOT-BROKER-1'; a2 text:='DIAGNOSTIC-COORDINATOR-NOT-BROKER-2';
 s text:='sha256:'||repeat('a',64); h text:='sha256:'||repeat('6',64); r jsonb; anchor jsonb; f jsonb; cid text; origin text; snap jsonb;
begin
 r:=public.gold2_paper_read_account_state_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s);
 perform pg_temp.gold2_probe_assert('read_initial_flat_not_authority',r->>'phase'='FLAT' and r->>'version'='0' and r->>'ledger_sequence'='0' and r->>'ledger_root_hash'=repeat('0',64) and r->>'claimed'='false');
 perform pg_temp.gold2_probe_expect_denied('binding_account_denied',format('select public.gold2_paper_read_account_state_v2(%L,%L,2147483000,%L)','SIMNOW_FIRST_NORMAL','OTHER-ACCOUNT',s),'GOLD2_BOUND_IDENTITY_DENIED');
 perform pg_temp.gold2_probe_expect_denied('binding_robot_denied',format('select public.gold2_paper_read_account_state_v2(%L,%L,2147483001,%L)','SIMNOW_FIRST_NORMAL',a,s),'GOLD2_BOUND_IDENTITY_DENIED');
 perform pg_temp.gold2_probe_expect_denied('binding_source_denied',format('select public.gold2_paper_read_account_state_v2(%L,%L,2147483000,%L)','SIMNOW_FIRST_NORMAL',a,h),'GOLD2_BOUND_IDENTITY_DENIED');
 perform pg_temp.gold2_probe_assert('service_cannot_change_bindings',not has_table_privilege('service_role','gold2_paper.runtime_bindings','INSERT') and not has_table_privilege('service_role','gold2_paper.runtime_bindings','UPDATE'));
 perform pg_temp.gold2_probe_assert('v1_execution_revoked',not has_function_privilege('service_role','public.gold2_paper_claim_order_v1(text,text,bigint,text)','EXECUTE'));
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-OPEN-1',null,'OPEN_LONG',0,0,'NONE');
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-PRE-1','PRE_CLAIM',f);
 perform pg_temp.gold2_probe_expect_denied('unanchored_claim_denied',format('select public.gold2_paper_claim_order_v2(%L,%L,2147483000,%L,0,%L,1,%L,%L,%L,%L,null,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,h,'DIAGNOSTIC-OPEN-1',h,'OPEN_LONG','au2612','DIAGNOSTIC-PRE-1'),'GOLD2_LEDGER_HEAD_NOT_ANCHORED');
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderClaimRequested','DIAGNOSTIC-OPEN-1',jsonb_build_object('source_sha256',s,'contract_hash',h,'action','OPEN_LONG','instrument','au2612','position_origin_claim_id',null,'broker_evidence_id','DIAGNOSTIC-PRE-1'));
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,0,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-1',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-1');
 cid:=r->>'claim_id';origin:=cid;
 perform pg_temp.gold2_probe_assert('open_fresh_claim_one_shot',r->>'status'='CLAIMED' and r->>'claimed'='true' and r->>'version'='1' and r->>'pending_claim_id'=cid);
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,0,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-1',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-1');
 perform pg_temp.gold2_probe_assert('same_command_permanently_consumed',r->>'status'='ALREADY_CLAIMED' and r->>'claimed'='false');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,0,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-2',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-1');
 perform pg_temp.gold2_probe_assert('stale_version_no_new_claim',r->>'status'='VERSION_CONFLICT' and r->>'claimed'='false');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-2',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-1');
 perform pg_temp.gold2_probe_assert('different_command_account_mutex',r->>'status'='ACCOUNT_BUSY' and r->>'claimed'='false' and r->>'pending_claim_id'=cid);
 snap:=public.gold2_paper_read_account_state_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s);
 perform pg_temp.gold2_probe_assert('read_does_not_expire_or_release',snap->>'pending_claim_id'=cid and snap->>'version'='1' and snap->>'claimed'='false');
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderSubmitAttempted','DIAGNOSTIC-OPEN-1',jsonb_build_object('source_sha256',s,'claim_id',cid));
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,cid);
 perform pg_temp.gold2_probe_assert('submit_anchor_required_and_recorded',r->>'status'='SUBMIT_RECORDED' and r->>'version'='2');
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,cid);
 perform pg_temp.gold2_probe_assert('old_submit_version_denied',r->>'status'='VERSION_CONFLICT');
 perform pg_temp.gold2_probe_expect_denied('unknown_evidence_cannot_release',format('select public.gold2_paper_record_terminal_v2(%L,%L,2147483000,%L,2,%L,2,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',cid,'NONEXISTENT-EVIDENCE'),'GOLD2_BOUND_BROKER_EVIDENCE_REQUIRED');
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-OPEN-1',cid,'OPEN_LONG',1,1,'FILLED');
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-TERM-1','TERMINAL',f);
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderTerminalReconciled','DIAGNOSTIC-OPEN-1',jsonb_build_object('source_sha256',s,'claim_id',cid,'broker_evidence_id','DIAGNOSTIC-TERM-1'));
 r:=public.gold2_paper_record_terminal_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,2,anchor->>'root',(anchor->>'sequence')::integer,cid,'DIAGNOSTIC-TERM-1');
 perform pg_temp.gold2_probe_assert('filled_open_releases_pending_preserves_held_origin',r->>'status'='TERMINAL_RECORDED' and r->>'phase'='HELD' and r->>'position_quantity'='1' and r->>'position_origin_claim_id'=origin and r->'pending_claim_id'='null'::jsonb and r->>'version'='3');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-3',h,'OPEN_LONG','au2612',null,'NONEXISTENT-EVIDENCE');
 perform pg_temp.gold2_probe_assert('held_cannot_reopen',r->>'status'='OPEN_POSITION_DENIED');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-CLOSE-1',h,'CLOSE_LONG','au2612','WRONG-ORIGIN','NONEXISTENT-EVIDENCE');
 perform pg_temp.gold2_probe_assert('close_requires_confirmed_origin',r->>'status'='CLOSE_ORIGIN_DENIED');
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-CLOSE-1',null,'CLOSE_LONG',1,0,'NONE');
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-PRE-CLOSE','PRE_CLAIM',f);
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderClaimRequested','DIAGNOSTIC-CLOSE-1',jsonb_build_object('source_sha256',s,'contract_hash',h,'action','CLOSE_LONG','instrument','au2612','position_origin_claim_id',origin,'broker_evidence_id','DIAGNOSTIC-PRE-CLOSE'));
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-CLOSE-1',h,'CLOSE_LONG','au2612',origin,'DIAGNOSTIC-PRE-CLOSE');
 cid:=r->>'claim_id';
 perform pg_temp.gold2_probe_assert('close_claim_is_distinct_one_shot',r->>'claimed'='true' and cid<>origin and r->>'version'='4');
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderSubmitAttempted','DIAGNOSTIC-CLOSE-1',jsonb_build_object('source_sha256',s,'claim_id',cid));
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,4,anchor->>'root',(anchor->>'sequence')::integer,cid);
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-CLOSE-1',cid,'CLOSE_LONG',0,1,'FILLED');
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-TERM-CLOSE','TERMINAL',f);
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderTerminalReconciled','DIAGNOSTIC-CLOSE-1',jsonb_build_object('source_sha256',s,'claim_id',cid,'broker_evidence_id','DIAGNOSTIC-TERM-CLOSE'));
 r:=public.gold2_paper_record_terminal_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,5,anchor->>'root',(anchor->>'sequence')::integer,cid,'DIAGNOSTIC-TERM-CLOSE');
 perform pg_temp.gold2_probe_assert('filled_close_returns_flat',r->>'phase'='FLAT' and r->>'position_quantity'='0' and r->'position_origin_claim_id'='null'::jsonb and r->>'version'='6');
 r:=public.gold2_paper_record_terminal_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,5,anchor->>'root',(anchor->>'sequence')::integer,cid,'DIAGNOSTIC-TERM-CLOSE');
 perform pg_temp.gold2_probe_assert('old_terminal_cannot_release_again',r->>'status'='VERSION_CONFLICT');
 anchor:=pg_temp.gold2_probe_anchor(a,'AccountFrozen','DIAGNOSTIC-FREEZE-1',jsonb_build_object('source_sha256',s,'claim_id',null,'reason_code','RESTART_BROKER_UNKNOWN'));
 r:=public.gold2_paper_freeze_account_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,6,anchor->>'root',(anchor->>'sequence')::integer,null,'RESTART_BROKER_UNKNOWN');
 perform pg_temp.gold2_probe_assert('freeze_only_conservative',r->>'phase'='FROZEN' and r->>'freeze_reason'='RESTART_BROKER_UNKNOWN' and r->>'version'='7');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,7,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-4',h,'OPEN_LONG','au2612',null,'NONEXISTENT-EVIDENCE');
 perform pg_temp.gold2_probe_assert('frozen_account_cannot_open',r->>'status'='ACCOUNT_FROZEN');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,7,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-CLOSE-2',h,'CLOSE_LONG','au2612',origin,'NONEXISTENT-EVIDENCE');
 perform pg_temp.gold2_probe_assert('frozen_cannot_bypass_mutex_with_close',r->>'status'='ACCOUNT_FROZEN');
 -- Four-way checks reject drift independently of a claimed MATCHED label.
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-BAD-1',null,'OPEN_LONG',0,0,'NONE');
 f:=jsonb_set(f,'{reconciliation,expected,available_cents}','490000002'::jsonb);
 perform pg_temp.gold2_probe_expect_denied('available_drift_denied',format('select pg_temp.gold2_probe_evidence(%L,%L,%L,%L::jsonb)',a,'DIAGNOSTIC-BAD-EVIDENCE','PRE_CLAIM',f),'GOLD2_FOUR_WAY_AMOUNT_MISMATCH');
 f:=jsonb_set(f,'{reconciliation,expected,available_cents}','490000000'::jsonb);
 f:=jsonb_set(f,'{reconciliation,expected,frozen_margin_cents}','10000002'::jsonb);
 perform pg_temp.gold2_probe_expect_denied('margin_drift_denied',format('select pg_temp.gold2_probe_evidence(%L,%L,%L,%L::jsonb)',a,'DIAGNOSTIC-BAD-EVIDENCE','PRE_CLAIM',f),'GOLD2_FOUR_WAY_AMOUNT_MISMATCH');
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-BAD-1',null,'OPEN_LONG',0,0,'NONE');
 f:=jsonb_set(f,'{reconciliation,expected,position_quantity}','1'::jsonb);
 perform pg_temp.gold2_probe_expect_denied('position_drift_denied',format('select pg_temp.gold2_probe_evidence(%L,%L,%L,%L::jsonb)',a,'DIAGNOSTIC-BAD-EVIDENCE','PRE_CLAIM',f),'GOLD2_FOUR_WAY_QUANTITY_DENIED');
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-BAD-1',null,'OPEN_LONG',0,0,'NONE');
 f:=jsonb_set(f,'{reconciliation}','{"status":"MATCHED"}'::jsonb);
 perform pg_temp.gold2_probe_expect_denied('matched_dictionary_is_not_fact',format('select pg_temp.gold2_probe_evidence(%L,%L,%L,%L::jsonb)',a,'DIAGNOSTIC-BAD-EVIDENCE','PRE_CLAIM',f),'GOLD2_FOUR_WAY_REQUIRED');
 -- Independent second account remains usable despite the first's freeze.
 f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-ACCOUNT-2-OPEN',null,'OPEN_LONG',0,0,'NONE');
 perform pg_temp.gold2_probe_evidence(a2,'DIAGNOSTIC-ACCOUNT-2-PRE','PRE_CLAIM',f);
 anchor:=pg_temp.gold2_probe_anchor(a2,'OrderClaimRequested','DIAGNOSTIC-ACCOUNT-2-OPEN',jsonb_build_object('source_sha256',s,'contract_hash',h,'action','OPEN_LONG','instrument','au2612','position_origin_claim_id',null,'broker_evidence_id','DIAGNOSTIC-ACCOUNT-2-PRE'));
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a2,2147483000,s,0,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-ACCOUNT-2-OPEN',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-ACCOUNT-2-PRE');
 cid:=r->>'claim_id';
 perform pg_temp.gold2_probe_assert('different_accounts_do_not_share_mutex',r->>'claimed'='true');
 anchor:=pg_temp.gold2_probe_anchor(a2,'AccountFrozen','DIAGNOSTIC-ACCOUNT-2-OPEN',jsonb_build_object('source_sha256',s,'claim_id',cid,'reason_code','BROKER_SUBMISSION_UNKNOWN'));
 r:=public.gold2_paper_freeze_account_v2('SIMNOW_FIRST_NORMAL',a2,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,cid,'BROKER_SUBMISSION_UNKNOWN');
 perform pg_temp.gold2_probe_assert('freeze_preserves_pending_slot',r->>'pending_claim_id'=cid and r->>'phase'='FROZEN' and r->>'position_quantity'='0');
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a2,2147483000,s,2,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-OPEN-1',h,'OPEN_LONG','au2612',null,'NONEXISTENT-EVIDENCE');
 perform pg_temp.gold2_probe_assert('permanent_command_id_global_across_accounts',r->>'status'='CONFLICT' and r->>'claimed'='false');
 perform pg_temp.gold2_probe_assert('append_only_claim_grants',not has_table_privilege('service_role','gold2_paper.command_claims_v2','UPDATE') and not has_table_privilege('service_role','gold2_paper.command_claims_v2','DELETE'));
end;
$$;
do $$
declare a text:='DIAGNOSTIC-COORDINATOR-NOT-BROKER-3'; s text:='sha256:'||repeat('a',64); h text:='sha256:'||repeat('6',64);
 ver bigint:=0; j integer; cmd text; cid text; origin text; act text; qty integer; filled integer; stat text; f jsonb; anchor jsonb; r jsonb;
begin
 for j in 1..5 loop
  act:=case when j<=3 then 'OPEN_LONG' else 'CLOSE_LONG' end;
  qty:=case when j<=3 then 0 else 1 end;
  stat:=case when j in (1,4) then 'REJECTED' when j in (2,5) then 'CANCELED' else 'FILLED' end;
  filled:=case when stat='FILLED' then 1 else 0 end;
  cmd:='DIAGNOSTIC-REJECT-CANCEL-'||j::text;
  f:=pg_temp.gold2_probe_facts(cmd,null,act,qty,0,'NONE');
  perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-RC-PRE-'||j::text,'PRE_CLAIM',f);
  anchor:=pg_temp.gold2_probe_anchor(a,'OrderClaimRequested',cmd,jsonb_build_object('source_sha256',s,'contract_hash',h,'action',act,'instrument','au2612','position_origin_claim_id',case when act='OPEN_LONG' then null else origin end,'broker_evidence_id','DIAGNOSTIC-RC-PRE-'||j::text));
  r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,ver,anchor->>'root',(anchor->>'sequence')::integer,cmd,h,act,'au2612',case when act='OPEN_LONG' then null else origin end,'DIAGNOSTIC-RC-PRE-'||j::text);
  cid:=r->>'claim_id';ver:=ver+1;
  perform pg_temp.gold2_probe_assert('reject_cancel_fresh_claim_'||j::text,r->>'claimed'='true' and (r->>'version')::bigint=ver);
  anchor:=pg_temp.gold2_probe_anchor(a,'OrderSubmitAttempted',cmd,jsonb_build_object('source_sha256',s,'claim_id',cid));
  r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,ver,anchor->>'root',(anchor->>'sequence')::integer,cid);ver:=ver+1;
  if j=1 then
   -- All four parties can agree on a false position projection. The
   -- coordinator must still validate it against the stored pre-state/action.
   f:=pg_temp.gold2_probe_facts(cmd,cid,act,0,1,'FILLED');
   perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-RC-POS-DRIFT','TERMINAL',f);
   anchor:=pg_temp.gold2_probe_anchor(a,'OrderTerminalReconciled',cmd,jsonb_build_object('source_sha256',s,'claim_id',cid,'broker_evidence_id','DIAGNOSTIC-RC-POS-DRIFT'));
   perform pg_temp.gold2_probe_expect_denied('terminal_consistent_but_wrong_qty_denied',format('select public.gold2_paper_record_terminal_v2(%L,%L,2147483000,%L,%s,%L,%s,%L,%L)',
    'SIMNOW_FIRST_NORMAL',a,s,ver,anchor->>'root',anchor->>'sequence',cid,'DIAGNOSTIC-RC-POS-DRIFT'),'GOLD2_TERMINAL_POSITION_DRIFT');
   r:=public.gold2_paper_read_account_state_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s);
   perform pg_temp.gold2_probe_assert('denied_terminal_preserves_pending',r->>'pending_claim_id'=cid and (r->>'version')::bigint=ver);
   f:=pg_temp.gold2_probe_facts('DIAGNOSTIC-WRONG-COMMAND',cid,act,0,0,'REJECTED');
   perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-RC-WRONG-COMMAND','TERMINAL',f);
   perform pg_temp.gold2_probe_expect_denied('wrong_terminal_command_denied',format('select public.gold2_paper_record_terminal_v2(%L,%L,2147483000,%L,%s,%L,%s,%L,%L)',
    'SIMNOW_FIRST_NORMAL',a,s,ver,anchor->>'root',anchor->>'sequence',cid,'DIAGNOSTIC-RC-WRONG-COMMAND'),'GOLD2_BOUND_BROKER_EVIDENCE_REQUIRED');
  end if;
  f:=pg_temp.gold2_probe_facts(cmd,cid,act,case when j=3 then 1 else qty end,filled,stat);
  perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-RC-TERM-'||j::text,'TERMINAL',f);
  anchor:=pg_temp.gold2_probe_anchor(a,'OrderTerminalReconciled',cmd,jsonb_build_object('source_sha256',s,'claim_id',cid,'broker_evidence_id','DIAGNOSTIC-RC-TERM-'||j::text));
  r:=public.gold2_paper_record_terminal_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,ver,anchor->>'root',(anchor->>'sequence')::integer,cid,'DIAGNOSTIC-RC-TERM-'||j::text);ver:=ver+1;
  if j=3 then origin:=cid; end if;
  perform pg_temp.gold2_probe_assert('zero_fill_preserves_quantity_'||j::text,r->>'status'='TERMINAL_RECORDED' and r->'pending_claim_id'='null'::jsonb
   and (r->>'position_quantity')::integer=case when j=3 then 1 else qty end and (r->>'version')::bigint=ver);
  if j>=3 then perform pg_temp.gold2_probe_assert('zero_fill_close_preserves_origin_'||j::text,r->>'position_origin_claim_id'=origin); end if;
 end loop;
end;
$$;
reset role;
select check_name,passed from gold2_coordinator_probe_results order by check_name;
select count(*) as passed_checks,bool_and(passed) as all_passed from gold2_coordinator_probe_results;
select c.relname,c.relrowsecurity,
 has_table_privilege('anon',c.oid,'SELECT') as anon_select,
 has_table_privilege('authenticated',c.oid,'SELECT') as authenticated_select
 from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='gold2_paper'
 and c.relname in ('runtime_bindings','account_execution_state','command_claims_v2','broker_evidence_v2','claim_events_v2') order by c.relname;
rollback;
