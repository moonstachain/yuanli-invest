-- Run after both migrations as administrator. All DIAGNOSTIC fixtures roll
-- back, including temporary functions/bindings/claims. This is database
-- behavior proof only; it does not prove a broker reader or CTP connection.
begin;
create temporary table gold2_linked_probe_results(check_name text primary key, passed boolean not null);
grant select,insert on gold2_linked_probe_results to service_role;
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
 insert into gold2_linked_probe_results values(p_name,true);
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

create function pg_temp.gold2_native_facts(p_command text,p_claim text,p_action text,p_order text,p_qty integer)
returns jsonb language sql as $$
 select jsonb_build_object('command_id',p_command,'claim_id',p_claim,'instrument','au2612','action',p_action,
 'order_id',p_order,'order_status','FILLED','filled_quantity',1,'position_quantity',p_qty,'pending_order_count',0,
 'parent_claim_id',null,'parent_order_id',null,'reconciliation',null,
 'order_binding_sha256','sha256:'||repeat('6',64),'raw_identity_sha256','sha256:'||repeat('6',64),
 'raw_account_sha256','sha256:'||repeat('6',64),'raw_orders_sha256','sha256:'||repeat('6',64),
 'raw_trades_sha256','sha256:'||repeat('6',64),'raw_positions_sha256','sha256:'||repeat('6',64));
$$;
create function pg_temp.gold2_native_evidence(p_account text,p_id text,p_kind text,p_facts jsonb)
returns void language plpgsql as $$
begin
 perform public.gold2_paper_ingest_native_evidence_v3('SIMNOW_FIRST_NORMAL',p_account,2147483000,'sha256:'||repeat('b',64),
  p_id,p_kind,clock_timestamp(),pg_temp.gold2_probe_hash(p_facts),p_facts,pg_temp.gold2_probe_canonical(p_facts));
end;
$$;
insert into gold2_paper.runtime_bindings values
 ('SIMNOW_FIRST_NORMAL','DIAGNOSTIC-LINKED-NOT-BROKER',2147483000,'sha256:'||repeat('a',64),'sha256:'||repeat('b',64),true);
set local role service_role;
do $$
declare a text:='DIAGNOSTIC-LINKED-NOT-BROKER'; s text:='sha256:'||repeat('a',64); h text:='sha256:'||repeat('6',64);
 r jsonb; anchor jsonb; f jsonb; parent text; child text; party jsonb; pairs jsonb; snap jsonb;
begin
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-PRE-OPEN','PRE_CLAIM',pg_temp.gold2_probe_facts('DIAGNOSTIC-OPEN',null,'OPEN_LONG',0,0,'NONE'));
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderClaimRequested','DIAGNOSTIC-OPEN',jsonb_build_object('source_sha256',s,'contract_hash',h,
  'action','OPEN_LONG','instrument','au2612','position_origin_claim_id',null,'broker_evidence_id','DIAGNOSTIC-PRE-OPEN'));
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,0,anchor->>'root',(anchor->>'sequence')::integer,
  'DIAGNOSTIC-OPEN',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-OPEN'); parent:=r->>'claim_id';
 perform pg_temp.gold2_probe_assert('parent_claim_fresh',r->>'claimed'='true');
 perform pg_temp.gold2_probe_anchor(a,'ActionAdmitted','DIAGNOSTIC-OPEN',jsonb_build_object('contract_hash',h,'body',jsonb_build_object(
  'command_id','DIAGNOSTIC-OPEN','contract_hash',h,'action','OPEN_LONG','account_id',a,'environment','SIMNOW_FIRST_NORMAL',
  'contract','au2612','quantity',1,'stop_price','950','action_contract_id','DIAGNOSTIC-ACTION')));
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderSubmitAttempted','DIAGNOSTIC-OPEN',jsonb_build_object('source_sha256',s,'claim_id',parent));
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,parent);
 perform pg_temp.gold2_probe_assert('parent_submit_once',r->>'phase'='SUBMIT_ATTEMPTED');
 perform pg_temp.gold2_probe_anchor(a,'OrderSubmitted','DIAGNOSTIC-OPEN',jsonb_build_object('order_id','DIAGNOSTIC-ORDER-OPEN'));
 f:=pg_temp.gold2_native_facts('DIAGNOSTIC-OPEN',parent,'OPEN_LONG','DIAGNOSTIC-ORDER-OPEN',1);
 perform pg_temp.gold2_native_evidence(a,'DIAGNOSTIC-NATIVE-PARENT','NATIVE_ORDER',f);
 perform pg_temp.gold2_probe_assert('native_is_not_fourway',(select facts->'reconciliation'='null'::jsonb from gold2_paper.native_evidence_v3 where evidence_id='DIAGNOSTIC-NATIVE-PARENT'));
 perform pg_temp.gold2_probe_expect_denied('native_cannot_claim_reconciliation',format('select pg_temp.gold2_native_evidence(%L,%L,%L,%L::jsonb)',a,'BAD-NATIVE','NATIVE_ORDER',f||jsonb_build_object('reconciliation','{}'::jsonb)),'GOLD2_NATIVE_IS_NOT_FOUR_WAY');
 anchor:=pg_temp.gold2_probe_anchor(a,'LinkedExitClaimRequested','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'contract_hash',h,
  'parent_claim_id',parent,'origin_command_id','DIAGNOSTIC-OPEN','origin_order_id','DIAGNOSTIC-ORDER-OPEN','origin_action_contract_id','DIAGNOSTIC-ACTION',
  'instrument','au2612','action','CLOSE_LONG','broker_evidence_id','DIAGNOSTIC-NATIVE-PARENT'));
 perform pg_temp.gold2_probe_expect_denied('missing_exit_reason_denied',format('select public.gold2_paper_claim_linked_exit_v3(%L,%L,2147483000,%L,2,%L,%s,%L,%L,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence','DIAGNOSTIC-CLOSE',h,parent,'DIAGNOSTIC-NATIVE-PARENT'),'GOLD2_LINKED_EXIT_REASON_DENIED');
 anchor:=pg_temp.gold2_probe_anchor(a,'LinkedExitClaimRequested','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'contract_hash',h,
  'parent_claim_id',parent,'origin_command_id','DIAGNOSTIC-OPEN','origin_order_id','DIAGNOSTIC-ORDER-OPEN','origin_action_contract_id','DIAGNOSTIC-ACTION',
  'instrument','au2612','action','CLOSE_LONG','reason',null,'broker_evidence_id','DIAGNOSTIC-NATIVE-PARENT'));
 perform pg_temp.gold2_probe_expect_denied('null_exit_reason_denied',format('select public.gold2_paper_claim_linked_exit_v3(%L,%L,2147483000,%L,2,%L,%s,%L,%L,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence','DIAGNOSTIC-CLOSE',h,parent,'DIAGNOSTIC-NATIVE-PARENT'),'GOLD2_LINKED_EXIT_REASON_DENIED');
 anchor:=pg_temp.gold2_probe_anchor(a,'LinkedExitClaimRequested','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'contract_hash',h,
  'parent_claim_id',parent,'origin_command_id','DIAGNOSTIC-OPEN','origin_order_id','DIAGNOSTIC-ORDER-OPEN','origin_action_contract_id','DIAGNOSTIC-ACTION',
  'instrument','au2612','action','CLOSE_LONG','reason','EXIT_STOP','broker_evidence_id','DIAGNOSTIC-NATIVE-PARENT'));
 r:=public.gold2_paper_claim_linked_exit_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,1,anchor->>'root',(anchor->>'sequence')::integer,
  'DIAGNOSTIC-CLOSE',h,parent,'DIAGNOSTIC-NATIVE-PARENT');
 perform pg_temp.gold2_probe_assert('stale_version_never_closes',r->>'status'='VERSION_CONFLICT');
 r:=public.gold2_paper_claim_linked_exit_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,2,anchor->>'root',(anchor->>'sequence')::integer,
  'DIAGNOSTIC-CLOSE',h,parent,'DIAGNOSTIC-NATIVE-PARENT'); child:=r->>'claim_id';
 perform pg_temp.gold2_probe_assert('native_filled_parent_allows_only_child',r->>'claimed'='true' and r->>'position_quantity'='1' and r->>'position_origin_claim_id'=parent);
 perform pg_temp.gold2_probe_assert('child_keeps_parent_reservation',(select parent_claim_id=parent from gold2_paper.linked_exits_v3 where child_claim_id=child));
 r:=public.gold2_paper_claim_linked_exit_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,
  'DIAGNOSTIC-CLOSE',h,parent,'DIAGNOSTIC-NATIVE-PARENT');
 perform pg_temp.gold2_probe_assert('same_child_permanently_consumed',r->>'status'='LINKED_EXIT_CONSUMED' and r->>'claimed'='false');
 r:=public.gold2_paper_claim_linked_exit_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,
  'DIAGNOSTIC-CLOSE-RETRY',h,parent,'DIAGNOSTIC-NATIVE-PARENT');
 perform pg_temp.gold2_probe_assert('different_child_same_parent_consumed',r->>'status'='LINKED_EXIT_CONSUMED');
 perform pg_temp.gold2_probe_expect_denied('linked_child_v2_terminal_cannot_bypass',format('select public.gold2_paper_record_terminal_v2(%L,%L,2147483000,%L,3,%L,%s,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence',child,'NOT-EVIDENCE'),'GOLD2_LINKED_PAIR_PROTOCOL_REQUIRED');
 perform pg_temp.gold2_probe_expect_denied('private_base_cannot_bypass',format('select gold2_paper.record_terminal_base_v2(%L,%L,2147483000,%L,3,%L,%s,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence',child,'NOT-EVIDENCE'),'GOLD2_LINKED_PAIR_PROTOCOL_REQUIRED');
 perform pg_temp.gold2_probe_expect_denied('parent_v2_terminal_cannot_bypass',format('select public.gold2_paper_record_terminal_v2(%L,%L,2147483000,%L,3,%L,%s,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence',parent,'NOT-EVIDENCE'),'GOLD2_LINKED_PAIR_PROTOCOL_REQUIRED');
 perform pg_temp.gold2_probe_anchor(a,'ActionAdmitted','DIAGNOSTIC-CLOSE',jsonb_build_object('contract_hash',h,'authority','SIGNED_ENTRY_CONTINGENT_EXIT','body',jsonb_build_object(
  'action','CLOSE_LONG','contract','au2612','origin_command_id','DIAGNOSTIC-OPEN','origin_order_id','DIAGNOSTIC-ORDER-OPEN','origin_action_contract_id','DIAGNOSTIC-ACTION')));
 anchor:=pg_temp.gold2_probe_anchor(a,'OrderSubmitAttempted','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'claim_id',child));
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,3,anchor->>'root',(anchor->>'sequence')::integer,child);
 perform pg_temp.gold2_probe_assert('child_submit_once',r->>'phase'='SUBMIT_ATTEMPTED');
 r:=public.gold2_paper_record_submit_attempt_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,4,anchor->>'root',(anchor->>'sequence')::integer,child);
 perform pg_temp.gold2_probe_assert('child_submit_replay_denied',r->>'status'='SUBMIT_STATE_DENIED');
 perform pg_temp.gold2_probe_anchor(a,'OrderSubmitted','DIAGNOSTIC-CLOSE',jsonb_build_object('order_id','DIAGNOSTIC-ORDER-CLOSE'));
 f:=pg_temp.gold2_native_facts('DIAGNOSTIC-CLOSE',child,'CLOSE_LONG','DIAGNOSTIC-ORDER-CLOSE',0);
 perform pg_temp.gold2_native_evidence(a,'DIAGNOSTIC-NATIVE-FLAT','NATIVE_ORDER',f);
 anchor:=pg_temp.gold2_probe_anchor(a,'LinkedPairReconciled','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'claim_id',child,'parent_claim_id',parent,'broker_evidence_id','DIAGNOSTIC-NATIVE-FLAT'));
 perform pg_temp.gold2_probe_expect_denied('native_flat_is_not_pair_settlement',format('select public.gold2_paper_complete_linked_pair_v3(%L,%L,2147483000,%L,4,%L,%s,%L,%L)',
  'SIMNOW_FIRST_NORMAL',a,s,anchor->>'root',anchor->>'sequence',child,'DIAGNOSTIC-NATIVE-FLAT'),'GOLD2_BOUND_NATIVE_EVIDENCE_REQUIRED');
 f:=f||jsonb_build_object('parent_claim_id',parent,'parent_order_id','DIAGNOSTIC-ORDER-OPEN');
 party:=jsonb_build_object('proof_sha256',h,'cash_cents',500000000,'available_cents',500000000,'frozen_margin_cents',0,'position_quantity',0,
  'open_filled_quantity',1,'close_filled_quantity',1,'parent_order_id','DIAGNOSTIC-ORDER-OPEN','child_order_id','DIAGNOSTIC-ORDER-CLOSE');
 pairs:=jsonb_build_object('broker',party||jsonb_build_object('producer_id','DIAGNOSTIC-BROKER'),'execution',party||jsonb_build_object('producer_id','DIAGNOSTIC-EXECUTION'),
  'ledger',party||jsonb_build_object('producer_id','DIAGNOSTIC-LEDGER'),'expected',party||jsonb_build_object('producer_id','DIAGNOSTIC-EXPECTED'));
 f:=f||jsonb_build_object('reconciliation',pairs);
 perform pg_temp.gold2_probe_expect_denied('pair_cloned_producers_denied',format('select pg_temp.gold2_native_evidence(%L,%L,%L,%L::jsonb)',a,'BAD-PAIR-CLONE','PAIRED_TERMINAL',jsonb_set(f,'{reconciliation,broker,producer_id}','"DIAGNOSTIC-LEDGER"')),'GOLD2_PAIRED_INDEPENDENT_PRODUCERS_REQUIRED');
 perform pg_temp.gold2_probe_expect_denied('pair_cash_drift_denied',format('select pg_temp.gold2_native_evidence(%L,%L,%L,%L::jsonb)',a,'BAD-PAIR-CASH','PAIRED_TERMINAL',jsonb_set(f,'{reconciliation,broker,cash_cents}','100')),'GOLD2_PAIRED_FOUR_WAY_DRIFT');
 perform pg_temp.gold2_native_evidence(a,'DIAGNOSTIC-TRUE-PAIR','PAIRED_TERMINAL',f);
 anchor:=pg_temp.gold2_probe_anchor(a,'LinkedPairReconciled','DIAGNOSTIC-CLOSE',jsonb_build_object('source_sha256',s,'claim_id',child,'parent_claim_id',parent,'broker_evidence_id','DIAGNOSTIC-TRUE-PAIR'));
 r:=public.gold2_paper_complete_linked_pair_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,4,anchor->>'root',(anchor->>'sequence')::integer,child,'DIAGNOSTIC-TRUE-PAIR');
 perform pg_temp.gold2_probe_assert('true_pair_reconciles_flat_but_keeps_frozen',r->>'status'='PAIR_RECORDED' and r->>'phase'='FROZEN' and r->>'position_quantity'='0' and r->'pending_claim_id'='null'::jsonb and r->>'freeze_reason'='LINKED_EXIT_PAIR_RECONCILED_REVIEW_REQUIRED');
 r:=public.gold2_paper_complete_linked_pair_v3('SIMNOW_FIRST_NORMAL',a,2147483000,s,5,anchor->>'root',(anchor->>'sequence')::integer,child,'DIAGNOSTIC-TRUE-PAIR');
 perform pg_temp.gold2_probe_assert('pair_replay_has_no_release_authority',r->>'status'='PAIR_STATE_DENIED');
 perform pg_temp.gold2_probe_evidence(a,'DIAGNOSTIC-PRE-REOPEN','PRE_CLAIM',pg_temp.gold2_probe_facts('DIAGNOSTIC-REOPEN',null,'OPEN_LONG',0,0,'NONE'));
 r:=public.gold2_paper_claim_order_v2('SIMNOW_FIRST_NORMAL',a,2147483000,s,5,anchor->>'root',(anchor->>'sequence')::integer,'DIAGNOSTIC-REOPEN',h,'OPEN_LONG','au2612',null,'DIAGNOSTIC-PRE-REOPEN');
 perform pg_temp.gold2_probe_assert('reopen_after_pair_is_denied',r->>'status'='ACCOUNT_FROZEN');
 perform pg_temp.gold2_probe_assert('private_tables_default_deny',not has_table_privilege('anon','gold2_paper.native_evidence_v3','SELECT') and not has_table_privilege('authenticated','gold2_paper.linked_exits_v3','SELECT'));
 perform pg_temp.gold2_probe_expect_denied('native_evidence_immutable',format('update gold2_paper.native_evidence_v3 set kind=%L where evidence_id=%L','PAIRED_TERMINAL','DIAGNOSTIC-NATIVE-PARENT'),'permission denied for table native_evidence_v3');
 perform pg_temp.gold2_probe_assert('one_parent_one_child', (select count(*)=1 from gold2_paper.linked_exits_v3));
 perform pg_temp.gold2_probe_assert('only_two_permanent_claims', (select count(*)=2 from gold2_paper.command_claims_v2 where account_id=a));
end;
$$;
reset role;
select jsonb_build_object('status','GOLD2_LINKED_SQL_ROLLBACK_PASS','checks',count(*),'passed',bool_and(passed)) as result from gold2_linked_probe_results;
rollback;
