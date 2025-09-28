-- =========================================================
-- Schema for Financial Analyst Project
-- =========================================================

-- Drop tables if they already exist (useful for local dev reset)
DROP TABLE IF EXISTS sentiment_runs;
DROP TABLE IF EXISTS ohlcv_daily;

-- =========================================================
-- OHLCV Daily Stock Data
-- =========================================================
CREATE TABLE ohlcv_daily (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    adjusted_close NUMERIC,
    volume BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

CREATE INDEX idx_ohlcv_symbol_date ON ohlcv_daily (symbol, date);

-- =========================================================
-- Sentiment Runs (for financial news analysis)
-- =========================================================
CREATE TABLE sentiment_runs (
    id SERIAL PRIMARY KEY,
    query VARCHAR(255) NOT NULL,                  -- e.g. "Apple"
    run_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    overall_tag VARCHAR(50),                      -- Bullish / Bearish / Neutral
    score_0_100 NUMERIC,                          -- 0–100 sentiment score
    counts JSONB,                                 -- e.g. {"positive": 10, "neutral": 5, "negative": 3}
    weighted_share JSONB,                         -- e.g. {"positive": 0.6, "neutral": 0.2, "negative": 0.2}
    articles JSONB                                -- store list of articles + their sentiment
);

CREATE INDEX idx_sentiment_query_date ON sentiment_runs (query, run_date);

-- =========================================================
-- Done
-- =========================================================
