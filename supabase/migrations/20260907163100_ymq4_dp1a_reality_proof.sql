-- YMQ4-DP1-A minimal operational proof schema.
-- This is a candidate migration. It does not change GitHub Canon authority.

create schema if not exists evidence;
create schema if not exists pit;
create schema if not exists runtime;

create table if not exists evidence.sources (
  source_id text primary key,
  provider text not null,
  authority_tier text not null,
  source_class text not null,
  canonical_locator text not null,
  created_at timestamptz not null default now()
);

create table if not exists evidence.source_snapshots (
  snapshot_id uuid primary key default gen_random_uuid(),
  source_id text not null references evidence.sources(source_id),
  retrieved_at timestamptz not null,
  http_status integer not null,
  content_type text,
  sha256 text not null check (sha256 ~ '^[0-9a-f]{64}$'),
  storage_bucket text not null,
  storage_path text not null,
  request_template text not null,
  runner_commit text,
  created_at timestamptz not null default now(),
  unique (source_id, sha256)
);

create table if not exists pit.observations (
  observation_id uuid primary key default gen_random_uuid(),
  series_id text not null,
  value_numeric double precision not null,
  observation_date date not null,
  release_date date not null,
  vintage_date date not null,
  known_as_of date not null,
  source_snapshot_id uuid not null references evidence.source_snapshots(snapshot_id),
  pit_status text not null,
  measurement_regime text,
  created_at timestamptz not null default now(),
  check (known_as_of >= release_date),
  check (known_as_of >= vintage_date),
  check (release_date >= observation_date or pit_status like 'PIT_MARKET%'),
  unique (series_id, observation_date, known_as_of, value_numeric)
);

create table if not exists runtime.reality_gate_runs (
  run_id uuid primary key default gen_random_uuid(),
  battle_id text not null,
  git_sha text not null,
  started_at timestamptz not null,
  completed_at timestamptz,
  gate_status text not null,
  receipt jsonb not null,
  created_at timestamptz not null default now()
);

alter table evidence.sources enable row level security;
alter table evidence.source_snapshots enable row level security;
alter table pit.observations enable row level security;
alter table runtime.reality_gate_runs enable row level security;

-- No anon/authenticated policies are created intentionally.
-- DP1-A GitHub Action writes only with a service-role secret.

insert into evidence.sources(source_id, provider, authority_tier, source_class, canonical_locator)
values (
  'fred_cpiaucsl',
  'Federal Reserve Bank of St. Louis / BLS',
  'official_primary_distribution',
  'REVISIONABLE_STATISTIC',
  'https://fred.stlouisfed.org/series/CPIAUCSL'
)
on conflict (source_id) do update set
  provider = excluded.provider,
  authority_tier = excluded.authority_tier,
  source_class = excluded.source_class,
  canonical_locator = excluded.canonical_locator;
