-- YMQ4-DP1-A REST/RPC hardening for non-exposed operational schemas.
-- Keep evidence/pit/runtime internal; expose only narrowly scoped service-role RPCs in public.

create index if not exists observations_source_snapshot_id_idx
  on pit.observations(source_snapshot_id);

create or replace function public.ymq4_dp1a_ingest(
  p_source_id text,
  p_retrieved_at timestamptz,
  p_http_status integer,
  p_content_type text,
  p_sha256 text,
  p_storage_bucket text,
  p_storage_path text,
  p_request_template text,
  p_runner_commit text,
  p_series_id text,
  p_value_numeric double precision,
  p_observation_date date,
  p_release_date date,
  p_vintage_date date,
  p_known_as_of date,
  p_pit_status text,
  p_measurement_regime text
)
returns table(snapshot_id uuid, observation_id uuid)
language plpgsql
security definer
set search_path = public, evidence, pit, pg_temp
as $$
declare
  v_snapshot_id uuid;
  v_observation_id uuid;
begin
  insert into evidence.source_snapshots(
    source_id, retrieved_at, http_status, content_type, sha256,
    storage_bucket, storage_path, request_template, runner_commit
  ) values (
    p_source_id, p_retrieved_at, p_http_status, p_content_type, p_sha256,
    p_storage_bucket, p_storage_path, p_request_template, p_runner_commit
  )
  on conflict (source_id, sha256) do update set
    retrieved_at = excluded.retrieved_at
  returning evidence.source_snapshots.snapshot_id into v_snapshot_id;

  insert into pit.observations(
    series_id, value_numeric, observation_date, release_date, vintage_date,
    known_as_of, source_snapshot_id, pit_status, measurement_regime
  ) values (
    p_series_id, p_value_numeric, p_observation_date, p_release_date, p_vintage_date,
    p_known_as_of, v_snapshot_id, p_pit_status, p_measurement_regime
  )
  on conflict (series_id, observation_date, known_as_of, value_numeric) do update set
    source_snapshot_id = excluded.source_snapshot_id
  returning pit.observations.observation_id into v_observation_id;

  return query select v_snapshot_id, v_observation_id;
end;
$$;

create or replace function public.ymq4_dp1a_readback(
  p_series_id text,
  p_observation_date date,
  p_known_as_of date
)
returns table(
  observation_id uuid,
  value_numeric double precision,
  observation_date date,
  release_date date,
  vintage_date date,
  known_as_of date,
  snapshot_id uuid,
  sha256 text,
  storage_bucket text,
  storage_path text
)
language sql
security definer
set search_path = public, evidence, pit, pg_temp
as $$
  select o.observation_id, o.value_numeric, o.observation_date, o.release_date,
         o.vintage_date, o.known_as_of, s.snapshot_id, s.sha256,
         s.storage_bucket, s.storage_path
  from pit.observations o
  join evidence.source_snapshots s on s.snapshot_id = o.source_snapshot_id
  where o.series_id = p_series_id
    and o.observation_date = p_observation_date
    and o.known_as_of = p_known_as_of
  order by o.created_at desc
  limit 1;
$$;

create or replace function public.ymq4_dp1a_record_gate(
  p_battle_id text,
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
  insert into runtime.reality_gate_runs(
    battle_id, git_sha, started_at, completed_at, gate_status, receipt
  ) values (
    p_battle_id, p_git_sha, p_started_at, p_completed_at, p_gate_status, p_receipt
  ) returning run_id into v_run_id;
  return v_run_id;
end;
$$;

revoke all on function public.ymq4_dp1a_ingest(text,timestamptz,integer,text,text,text,text,text,text,text,double precision,date,date,date,date,text,text) from public, anon, authenticated;
revoke all on function public.ymq4_dp1a_readback(text,date,date) from public, anon, authenticated;
revoke all on function public.ymq4_dp1a_record_gate(text,text,timestamptz,timestamptz,text,jsonb) from public, anon, authenticated;

grant execute on function public.ymq4_dp1a_ingest(text,timestamptz,integer,text,text,text,text,text,text,text,double precision,date,date,date,date,text,text) to service_role;
grant execute on function public.ymq4_dp1a_readback(text,date,date) to service_role;
grant execute on function public.ymq4_dp1a_record_gate(text,text,timestamptz,timestamptz,text,jsonb) to service_role;
