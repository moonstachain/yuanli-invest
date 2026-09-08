-- YMQ4-B3 dynamic-beta challenge contract.
-- Research-only, service-role-only. No direct table grants and no B4-B7/trading authority.

create or replace function public.ymq4_b3_read_b2_canonical(p_run_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public, runtime, pg_temp
as $$
declare
  v_result jsonb;
begin
  if p_run_id <> '8907b60a-445c-4396-8e51-29e6f36620fb'::uuid then
    raise exception 'non-canonical B2 run id';
  end if;

  select jsonb_build_object(
    'run_id', r.run_id::text,
    'battle_id', r.battle_id,
    'git_sha', r.git_sha,
    'gate_status', r.gate_status,
    'started_at', r.started_at,
    'completed_at', r.completed_at,
    'receipt', r.receipt
  )
  into v_result
  from runtime.reality_gate_runs r
  where r.run_id = p_run_id
    and r.battle_id = 'YMQ4-B2'
    and r.gate_status = 'B2_BASELINE_MATERIALIZED_PASS';

  if v_result is null then
    raise exception 'canonical B2 Reality Gate unavailable';
  end if;
  return v_result;
end;
$$;

create or replace function public.ymq4_b3_record_gate(
  p_git_sha text,
  p_started_at timestamptz,
  p_completed_at timestamptz,
  p_gate_status text,
  p_scientific_observation text,
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
  if p_gate_status <> 'B3_DYNAMIC_BETA_MATERIALIZED_PASS' then
    raise exception 'invalid B3 physical status: %', p_gate_status;
  end if;
  if p_scientific_observation not in ('DYNAMIC_BETA_BEATS_B2', 'DYNAMIC_BETA_DOES_NOT_BEAT_B2') then
    raise exception 'invalid B3 scientific observation: %', p_scientific_observation;
  end if;
  if coalesce(p_receipt->>'battle', '') <> 'YMQ4-B3' then
    raise exception 'B3 receipt battle mismatch';
  end if;
  if coalesce(p_receipt->'canonical_b2'->>'reality_gate_run_id', '') <> '8907b60a-445c-4396-8e51-29e6f36620fb' then
    raise exception 'B3 receipt canonical B2 mismatch';
  end if;
  if coalesce((p_receipt->'constraints'->>'b4_b7_executed')::boolean, true) then
    raise exception 'B4-B7 execution is prohibited in B3';
  end if;
  if coalesce((p_receipt->'constraints'->>'trading_action')::boolean, true) then
    raise exception 'trading action is prohibited in B3';
  end if;

  insert into runtime.reality_gate_runs(
    battle_id, git_sha, started_at, completed_at, gate_status, receipt
  ) values (
    'YMQ4-B3', p_git_sha, p_started_at, p_completed_at, p_gate_status,
    p_receipt || jsonb_build_object('scientific_observation', p_scientific_observation)
  ) returning run_id into v_run_id;

  return v_run_id;
end;
$$;

revoke all on function public.ymq4_b3_read_b2_canonical(uuid) from public, anon, authenticated;
revoke all on function public.ymq4_b3_record_gate(text,timestamptz,timestamptz,text,text,jsonb) from public, anon, authenticated;

grant execute on function public.ymq4_b3_read_b2_canonical(uuid) to service_role;
grant execute on function public.ymq4_b3_record_gate(text,timestamptz,timestamptz,text,text,jsonb) to service_role;
