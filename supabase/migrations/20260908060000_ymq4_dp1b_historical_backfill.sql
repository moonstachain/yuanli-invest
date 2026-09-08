-- YMQ4-DP1-B historical Gold PIT/as-of backfill data surface.
-- Additive only. Does not modify A9 Canon or authorize B2-B7.

create table if not exists pit.decision_asof_values (
  panel_id text not null,
  decision_date date not null,
  factor_id text not null check (factor_id in ('gold_usd_oz','usd','inflation_yoy','real_rate')),
  value_numeric double precision not null,
  source_series_id text not null,
  pit_status text not null,
  known_as_of date not null,
  measurement_regime text not null,
  provenance jsonb not null default '{}'::jsonb,
  runner_commit text,
  created_at timestamptz not null default now(),
  primary key (panel_id, decision_date, factor_id),
  check (known_as_of <= decision_date)
);

alter table pit.decision_asof_values enable row level security;

create index if not exists decision_asof_values_factor_date_idx
  on pit.decision_asof_values(panel_id, factor_id, decision_date);

insert into evidence.sources(source_id, provider, authority_tier, source_class, canonical_locator)
values
  ('worldbank_pinksheet_gold', 'World Bank Prospects Group', 'institutional_primary_distribution', 'PIT_MARKET_RECONSTRUCTED', 'https://www.worldbank.org/en/research/commodity-markets'),
  ('fred_cpiaucsl', 'BLS via Federal Reserve Bank of St. Louis', 'official_primary_distribution', 'REVISIONABLE_STATISTIC', 'https://fred.stlouisfed.org/series/CPIAUCSL'),
  ('fred_dtb3', 'Federal Reserve H.15 via FRED', 'official_primary_distribution', 'PIT_MARKET_RECONSTRUCTED', 'https://fred.stlouisfed.org/series/DTB3'),
  ('fred_dtwexm', 'Federal Reserve H.10 via FRED', 'official_primary_distribution', 'PIT_MARKET_RECONSTRUCTED', 'https://fred.stlouisfed.org/series/DTWEXM'),
  ('fred_dtwexbgs', 'Federal Reserve H.10 via FRED', 'official_primary_distribution', 'PIT_MARKET_RECONSTRUCTED', 'https://fred.stlouisfed.org/series/DTWEXBGS'),
  ('fred_dfii10', 'Federal Reserve H.15 via FRED', 'official_primary_distribution', 'PIT_MARKET_RECONSTRUCTED', 'https://fred.stlouisfed.org/series/DFII10')
on conflict (source_id) do update set
  provider = excluded.provider,
  authority_tier = excluded.authority_tier,
  source_class = excluded.source_class,
  canonical_locator = excluded.canonical_locator;

create or replace function public.ymq4_dp1b_ingest_source(
  p_source_id text,
  p_retrieved_at timestamptz,
  p_http_status integer,
  p_content_type text,
  p_sha256 text,
  p_storage_bucket text,
  p_storage_path text,
  p_request_template text,
  p_runner_commit text,
  p_observations jsonb
)
returns table(snapshot_id uuid, inserted_count bigint)
language plpgsql
security definer
set search_path = public, evidence, pit, pg_temp
as $$
declare
  v_snapshot_id uuid;
  v_inserted bigint := 0;
begin
  if not exists (select 1 from evidence.sources where source_id = p_source_id) then
    raise exception 'unknown source_id: %', p_source_id;
  end if;

  insert into evidence.source_snapshots(
    source_id, retrieved_at, http_status, content_type, sha256,
    storage_bucket, storage_path, request_template, runner_commit
  ) values (
    p_source_id, p_retrieved_at, p_http_status, p_content_type, p_sha256,
    p_storage_bucket, p_storage_path, p_request_template, p_runner_commit
  )
  on conflict (source_id, sha256) do update set
    retrieved_at = excluded.retrieved_at,
    storage_bucket = excluded.storage_bucket,
    storage_path = excluded.storage_path,
    runner_commit = excluded.runner_commit
  returning evidence.source_snapshots.snapshot_id into v_snapshot_id;

  insert into pit.observations(
    series_id, value_numeric, observation_date, release_date, vintage_date,
    known_as_of, source_snapshot_id, pit_status, measurement_regime
  )
  select
    x.series_id, x.value_numeric, x.observation_date, x.release_date,
    x.vintage_date, x.known_as_of, v_snapshot_id, x.pit_status,
    x.measurement_regime
  from jsonb_to_recordset(coalesce(p_observations, '[]'::jsonb)) as x(
    series_id text,
    value_numeric double precision,
    observation_date date,
    release_date date,
    vintage_date date,
    known_as_of date,
    pit_status text,
    measurement_regime text
  )
  where x.series_id is not null and x.value_numeric is not null
  on conflict (series_id, observation_date, known_as_of, value_numeric) do update set
    source_snapshot_id = excluded.source_snapshot_id,
    pit_status = excluded.pit_status,
    measurement_regime = excluded.measurement_regime;

  get diagnostics v_inserted = row_count;
  return query select v_snapshot_id, v_inserted;
end;
$$;

create or replace function public.ymq4_dp1b_upsert_panel(
  p_panel_id text,
  p_rows jsonb,
  p_runner_commit text
)
returns bigint
language plpgsql
security definer
set search_path = public, pit, pg_temp
as $$
declare
  v_count bigint := 0;
begin
  if p_panel_id is null or btrim(p_panel_id) = '' then
    raise exception 'panel_id required';
  end if;

  insert into pit.decision_asof_values(
    panel_id, decision_date, factor_id, value_numeric, source_series_id,
    pit_status, known_as_of, measurement_regime, provenance, runner_commit
  )
  select
    p_panel_id, x.decision_date, x.factor_id, x.value_numeric,
    x.source_series_id, x.pit_status, x.known_as_of,
    x.measurement_regime, coalesce(x.provenance, '{}'::jsonb), p_runner_commit
  from jsonb_to_recordset(coalesce(p_rows, '[]'::jsonb)) as x(
    decision_date date,
    factor_id text,
    value_numeric double precision,
    source_series_id text,
    pit_status text,
    known_as_of date,
    measurement_regime text,
    provenance jsonb
  )
  where x.decision_date is not null
    and x.factor_id is not null
    and x.value_numeric is not null
  on conflict (panel_id, decision_date, factor_id) do update set
    value_numeric = excluded.value_numeric,
    source_series_id = excluded.source_series_id,
    pit_status = excluded.pit_status,
    known_as_of = excluded.known_as_of,
    measurement_regime = excluded.measurement_regime,
    provenance = excluded.provenance,
    runner_commit = excluded.runner_commit,
    created_at = now();

  get diagnostics v_count = row_count;
  return v_count;
end;
$$;

create or replace function public.ymq4_dp1b_readback(p_panel_id text)
returns jsonb
language sql
security definer
set search_path = public, pit, pg_temp
as $$
  select jsonb_build_object(
    'panel_id', p_panel_id,
    'total_rows', count(*),
    'min_decision_date', min(decision_date),
    'max_decision_date', max(decision_date),
    'future_leakage', count(*) filter (where known_as_of > decision_date),
    'factor_counts', coalesce((
      select jsonb_object_agg(factor_id, n)
      from (
        select factor_id, count(*) as n
        from pit.decision_asof_values
        where panel_id = p_panel_id
        group by factor_id
      ) q
    ), '{}'::jsonb)
  )
  from pit.decision_asof_values
  where panel_id = p_panel_id;
$$;

create or replace function public.ymq4_dp1b_record_gate(
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
    'YMQ4-DP1-B', p_git_sha, p_started_at, p_completed_at, p_gate_status, p_receipt
  ) returning run_id into v_run_id;
  return v_run_id;
end;
$$;

revoke all on table pit.decision_asof_values from public, anon, authenticated;
revoke all on function public.ymq4_dp1b_ingest_source(text,timestamptz,integer,text,text,text,text,text,text,jsonb) from public, anon, authenticated;
revoke all on function public.ymq4_dp1b_upsert_panel(text,jsonb,text) from public, anon, authenticated;
revoke all on function public.ymq4_dp1b_readback(text) from public, anon, authenticated;
revoke all on function public.ymq4_dp1b_record_gate(text,timestamptz,timestamptz,text,jsonb) from public, anon, authenticated;

grant execute on function public.ymq4_dp1b_ingest_source(text,timestamptz,integer,text,text,text,text,text,text,jsonb) to service_role;
grant execute on function public.ymq4_dp1b_upsert_panel(text,jsonb,text) to service_role;
grant execute on function public.ymq4_dp1b_readback(text) to service_role;
grant execute on function public.ymq4_dp1b_record_gate(text,timestamptz,timestamptz,text,jsonb) to service_role;
