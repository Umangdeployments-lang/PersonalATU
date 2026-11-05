-- AEGIS-9 Schema: TimescaleDB Hypertables & Audit Tables
-- Generated from Master AI Engineering Blueprint

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- market_ticks Hypertable (1-day chunks)
CREATE TABLE IF NOT EXISTS market_ticks (
    ts TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(24) NOT NULL,
    trade_id BIGINT,
    price NUMERIC(18,8) NOT NULL,
    qty NUMERIC(18,8) NOT NULL,
    side SMALLINT NOT NULL, -- 1=Ask lifted, -1=Bid hit
    is_block_sweep BOOLEAN DEFAULT FALSE,
    is_iceberg_fill BOOLEAN DEFAULT FALSE,
    parent_order_cluster_id UUID NULL
);

SELECT create_hypertable('market_ticks', 'ts', chunk_time_interval => INTERVAL '1 day');

-- footprint_bars Hypertable (7-day chunks)
CREATE TABLE IF NOT EXISTS footprint_bars (
    bar_open_ts TIMESTAMPTZ NOT NULL,
    bar_close_ts TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(24) NOT NULL,
    bar_type VARCHAR(16) NOT NULL, -- VOLUME_500, RANGE_10T, TIME_1M
    open_px NUMERIC(18,8) NOT NULL,
    high_px NUMERIC(18,8) NOT NULL,
    low_px NUMERIC(18,8) NOT NULL,
    close_px NUMERIC(18,8) NOT NULL,
    total_volume NUMERIC(18,8) NOT NULL,
    bar_delta NUMERIC(18,8) NOT NULL,
    cumulative_delta NUMERIC(18,8) NOT NULL,
    poc_px NUMERIC(18,8),
    vah_px NUMERIC(18,8),
    val_px NUMERIC(18,8),
    vwap_px NUMERIC(18,8),
    vwap_std_1 NUMERIC(18,8),
    vwap_std_2 NUMERIC(18,8),
    vwap_std_3 NUMERIC(18,8),
    amt_regime VARCHAR(24),
    vpin_score NUMERIC(5,4),
    price_ladder_json JSONB NOT NULL DEFAULT '{}'
);

SELECT create_hypertable('footprint_bars', 'bar_open_ts', chunk_time_interval => INTERVAL '7 days');

-- gex_snapshots Hypertable (7-day chunks)
CREATE TABLE IF NOT EXISTS gex_snapshots (
    ts TIMESTAMPTZ NOT NULL,
    underlying_symbol VARCHAR(24) NOT NULL,
    spot_px NUMERIC(18,8) NOT NULL,
    total_net_gex NUMERIC(20,4) NOT NULL,
    zero_gamma_flip_px NUMERIC(18,8),
    call_wall_px NUMERIC(18,8),
    put_wall_px NUMERIC(18,8),
    net_vanna_flow NUMERIC(20,4),
    net_charm_flow NUMERIC(20,4),
    strike_profile_json JSONB NOT NULL DEFAULT '[]'
);

SELECT create_hypertable('gex_snapshots', 'ts', chunk_time_interval => INTERVAL '7 days');

-- trade_executions (Standard Relational)
CREATE TABLE IF NOT EXISTS trade_executions (
    trade_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_ts TIMESTAMPTZ NOT NULL,
    entry_ts TIMESTAMPTZ NOT NULL,
    exit_ts TIMESTAMPTZ,
    symbol VARCHAR(24) NOT NULL,
    direction VARCHAR(8) NOT NULL, -- LONG or SHORT
    allocation_mode VARCHAR(12) NOT NULL, -- FULL_100, HALF_50, KELLY_25
    account_equity_before NUMERIC(14,4) NOT NULL,
    margin_allocated NUMERIC(14,4) NOT NULL,
    position_notional NUMERIC(14,4) NOT NULL,
    entry_px NUMERIC(18,8) NOT NULL,
    exit_px NUMERIC(18,8),
    stop_loss_px NUMERIC(18,8) NOT NULL,
    target_1_px NUMERIC(18,8) NOT NULL,
    exit_reason VARCHAR(32), -- TARGET_HIT, SCRATCH_ABSORPTION_FAIL, TRAIL_STOP, STRUCTURAL_STOP
    gross_pnl NUMERIC(14,6) DEFAULT 0,
    fees_paid NUMERIC(14,6) DEFAULT 0,
    slippage_cost NUMERIC(14,6) DEFAULT 0,
    net_pnl NUMERIC(14,6) DEFAULT 0,
    is_win BOOLEAN,
    confluence_score NUMERIC(5,2) NOT NULL,
    ml_win_probability NUMERIC(5,4) NOT NULL,
    nine_pillar_snapshot_json JSONB NOT NULL DEFAULT '{}'
);

-- critic_evaluations (Production Gate Table)
CREATE TABLE IF NOT EXISTS critic_evaluations (
    eval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    git_commit_hash VARCHAR(64),
    module_name VARCHAR(64) NOT NULL,
    math_fidelity_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    latency_perf_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    anti_leakage_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    backtest_realism_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    fault_tolerance_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    weighted_total_score NUMERIC(4,2) NOT NULL DEFAULT 0,
    passed_9_gate BOOLEAN GENERATED ALWAYS AS (weighted_total_score >= 9.00) STORED,
    blocking_defects_json JSONB NOT NULL DEFAULT '[]',
    remediation_plan TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_market_ticks_ts_symbol ON market_ticks (ts DESC, symbol);
CREATE INDEX IF NOT EXISTS idx_footprint_bars_open_ts_symbol ON footprint_bars (bar_open_ts DESC, symbol);
CREATE INDEX IF NOT EXISTS idx_gex_snapshots_ts_symbol ON gex_snapshots (ts DESC, underlying_symbol);
CREATE INDEX IF NOT EXISTS idx_trade_executions_signal_ts ON trade_executions (signal_ts DESC);
CREATE INDEX IF NOT EXISTS idx_critic_evaluations_module ON critic_evaluations (module_name, evaluated_at DESC);

-- Grant privileges
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC TO aegis9;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA PUBLIC TO aegis9;