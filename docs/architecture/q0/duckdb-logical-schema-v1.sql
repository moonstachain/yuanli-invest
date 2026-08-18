-- Yuanli Quant AI Equity Research System
-- Q0 logical schema candidate. Physical implementation belongs in quant-workspace.
-- Point-in-time rule: every mutable fact must carry as_of / effective_at / captured_at.

CREATE TABLE IF NOT EXISTS asset_master (
  asset_id VARCHAR PRIMARY KEY,
  market VARCHAR NOT NULL,
  exchange VARCHAR NOT NULL,
  ticker VARCHAR NOT NULL,
  company_name VARCHAR NOT NULL,
  currency VARCHAR NOT NULL,
  listing_state VARCHAR NOT NULL,
  valid_from TIMESTAMP,
  valid_to TIMESTAMP,
  source_snapshot_id VARCHAR,
  UNIQUE(exchange, ticker, valid_from)
);

CREATE TABLE IF NOT EXISTS ai_value_chain_mapping (
  mapping_id VARCHAR PRIMARY KEY,
  asset_id VARCHAR NOT NULL,
  value_chain_node VARCHAR NOT NULL,
  exposure_type VARCHAR NOT NULL,
  evidence_state VARCHAR NOT NULL,
  as_of TIMESTAMP NOT NULL,
  source_snapshot_ids JSON NOT NULL,
  FOREIGN KEY(asset_id) REFERENCES asset_master(asset_id)
);

CREATE TABLE IF NOT EXISTS market_daily (
  asset_id VARCHAR NOT NULL,
  trade_date DATE NOT NULL,
  open DOUBLE,
  high DOUBLE,
  low DOUBLE,
  close DOUBLE,
  adj_close DOUBLE,
  volume DOUBLE,
  turnover DOUBLE,
  market_cap DOUBLE,
  source VARCHAR NOT NULL,
  captured_at TIMESTAMP NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  PRIMARY KEY(asset_id, trade_date, source)
);

CREATE TABLE IF NOT EXISTS fundamental_fact (
  fact_id VARCHAR PRIMARY KEY,
  asset_id VARCHAR NOT NULL,
  metric_id VARCHAR NOT NULL,
  period_end DATE,
  published_at TIMESTAMP,
  as_of TIMESTAMP NOT NULL,
  value DOUBLE,
  unit VARCHAR,
  currency VARCHAR,
  source VARCHAR NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  quality_state VARCHAR NOT NULL,
  FOREIGN KEY(asset_id) REFERENCES asset_master(asset_id)
);

CREATE TABLE IF NOT EXISTS estimate_fact (
  estimate_id VARCHAR PRIMARY KEY,
  asset_id VARCHAR NOT NULL,
  metric_id VARCHAR NOT NULL,
  forecast_period DATE NOT NULL,
  consensus_as_of TIMESTAMP NOT NULL,
  value DOUBLE,
  analyst_count INTEGER,
  source VARCHAR NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  FOREIGN KEY(asset_id) REFERENCES asset_master(asset_id)
);

CREATE TABLE IF NOT EXISTS industry_fact (
  fact_id VARCHAR PRIMARY KEY,
  node_id VARCHAR NOT NULL,
  metric_id VARCHAR NOT NULL,
  as_of TIMESTAMP NOT NULL,
  published_at TIMESTAMP,
  value DOUBLE,
  unit VARCHAR,
  source VARCHAR NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  quality_state VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS narrative_event (
  event_id VARCHAR PRIMARY KEY,
  narrative_id VARCHAR NOT NULL,
  asset_id VARCHAR,
  cohort VARCHAR NOT NULL,
  event_type VARCHAR NOT NULL,
  published_at TIMESTAMP NOT NULL,
  captured_at TIMESTAMP NOT NULL,
  publisher VARCHAR NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  t0_eligibility VARCHAR NOT NULL,
  source_quality VARCHAR NOT NULL,
  FOREIGN KEY(asset_id) REFERENCES asset_master(asset_id)
);

CREATE TABLE IF NOT EXISTS macro_snapshot_feature (
  feature_id VARCHAR PRIMARY KEY,
  regime_snapshot_id VARCHAR NOT NULL,
  as_of TIMESTAMP NOT NULL,
  metric_id VARCHAR NOT NULL,
  value DOUBLE,
  unit VARCHAR,
  source_repo_revision VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS quant_feature (
  feature_row_id VARCHAR PRIMARY KEY,
  feature_id VARCHAR NOT NULL,
  subject_id VARCHAR NOT NULL,
  as_of TIMESTAMP NOT NULL,
  formula_version VARCHAR NOT NULL,
  value_json JSON NOT NULL,
  source_snapshot_ids JSON NOT NULL,
  quality_state VARCHAR NOT NULL,
  computed_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_claim_index (
  claim_id VARCHAR PRIMARY KEY,
  subject_id VARCHAR NOT NULL,
  dimension VARCHAR NOT NULL,
  claim_text VARCHAR NOT NULL,
  source_snapshot_id VARCHAR NOT NULL,
  locator_json JSON NOT NULL,
  published_at TIMESTAMP,
  t0_eligibility VARCHAR NOT NULL,
  support_direction VARCHAR NOT NULL,
  machine_state VARCHAR NOT NULL,
  reviewer_state VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_run (
  run_id VARCHAR PRIMARY KEY,
  run_type VARCHAR NOT NULL,
  subject_id VARCHAR,
  as_of TIMESTAMP NOT NULL,
  input_manifest_hash VARCHAR NOT NULL,
  runtime_profile VARCHAR NOT NULL,
  trace_id VARCHAR,
  status VARCHAR NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  output_artifact_id VARCHAR
);

CREATE TABLE IF NOT EXISTS force_state_candidate (
  candidate_id VARCHAR PRIMARY KEY,
  asset_id VARCHAR NOT NULL,
  as_of TIMESTAMP NOT NULL,
  paradigm_snapshot_id VARCHAR NOT NULL,
  stage_snapshot_id VARCHAR NOT NULL,
  convexity_profile_id VARCHAR NOT NULL,
  fundamental_gate VARCHAR NOT NULL,
  survival_gate VARCHAR NOT NULL,
  classification VARCHAR NOT NULL,
  research_priority VARCHAR NOT NULL,
  evidence_ids JSON NOT NULL,
  counter_evidence_ids JSON NOT NULL,
  falsifiers JSON NOT NULL,
  unknowns JSON NOT NULL,
  lookahead_check VARCHAR NOT NULL,
  generated_by_run_id VARCHAR NOT NULL,
  admission_state VARCHAR NOT NULL DEFAULT 'candidate',
  FOREIGN KEY(asset_id) REFERENCES asset_master(asset_id)
);

CREATE TABLE IF NOT EXISTS replay_case (
  replay_id VARCHAR PRIMARY KEY,
  subject_id VARCHAR NOT NULL,
  t0 TIMESTAMP NOT NULL,
  pre_registration_revision VARCHAR NOT NULL,
  input_manifest_hash VARCHAR NOT NULL,
  outcome_locked BOOLEAN NOT NULL,
  replay_state VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_result (
  eval_result_id VARCHAR PRIMARY KEY,
  replay_id VARCHAR NOT NULL,
  evaluator_version VARCHAR NOT NULL,
  runtime_profile VARCHAR NOT NULL,
  metric_id VARCHAR NOT NULL,
  value DOUBLE,
  details_json JSON,
  evaluated_at TIMESTAMP NOT NULL,
  FOREIGN KEY(replay_id) REFERENCES replay_case(replay_id)
);

-- Logical ownership:
-- quant-workspace: physical tables, ingestion, deterministic features, paper/backtest.
-- yuanli-invest: schemas/contracts + versioned accepted snapshots/receipts.
-- local/NAS vault: raw immutable source bytes.
-- yiru-macro-cockpit: only publishes versioned macro snapshot inputs.
