-- YMQ4-B2 fixed-beta baseline readback + Reality Gate contract.
-- Additive only. No direct table grants. No B3-B7 execution authority.

create or replace function public.ymq4_b2_read_panel(p_panel_id text)
returns table(
  panel_id text,
  decision_date date,
  factor_id text,
  value_numeric double precision,
  known_as_of date
)
language sql
security definer
set search_path = public, pit, pg_temp
as $$
  select
    v.panel_id,
    v.decision_date,
    v.factor_id,
    v.value_numeric,
    v.known_as_of
  from pit.decision_asof_values v
  where v.panel_id = p_panel_id
  order by decision_date, factor_id;
$$;

create or replace function public.ymq4_b2_record_gate(
  p_git_sha text,
  p_started_at timestamptz,
  p_completed_at timestamptz,
  p_gate_status text,
  p_receipt jsonb
)
returns uuid
language plpgsql
security definer
set search_path = public, runtime, pg_temp
as $$
declare
  v_run_id uuid;
begin
  if p_gate_status <> 'B2_BASELINE_MATERIALIZED_PASS' then
    raise exception 'invalid B2 gate status: %', p_gate_status;
  end if;
  if coalesce(p_receipt->>'battle', '') <> 'YMQ4-B2' then
    raise exception 'B2 receipt battle mismatch';
  end if;
  if coalesce((p_receipt->'constraints'->>'b3_b7_executed')::boolean, true) then
    raise exception 'B3-B7 execution is prohibited in B2';
  end if;
  if coalesce((p_receipt->'constraints'->>'trading_action')::boolean, true) then
    raise exception 'trading action is prohibited in B2';
  end if;

  insert into runtime.reality_gate_runs(
    battle_id, git_sha, started_at, completed_at, gate_status, receipt
  ) values (
    'YMQ4-B2', p_git_sha, p_started_at, p_completed_at, p_gate_status, p_receipt
  ) returning run_id into v_run_id;

  return v_run_id;
end;
$$;

revoke all on function public.ymq4_b2_read_panel(text) from public, anon, authenticated;
revoke all on function public.ymq4_b2_record_gate(text,timestamptz,timestamptz,text,jsonb) from public, anon, authenticated;

grant execute on function public.ymq4_b2_read_panel(text) to service_role;
grant execute on function public.ymq4_b2_record_gate(text,timestamptz,timestamptz,text,jsonb) to service_role;
