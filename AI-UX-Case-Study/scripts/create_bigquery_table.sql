-- BigQuery schema for AI UX metrics
-- 1. Create dataset in Console: BigQuery > Create dataset > ai_ux_metrics
-- 2. Run this in BigQuery Console (Standard SQL) or:
--    bq mk --dataset PROJECT_ID:ai_ux_metrics
--    bq query --use_legacy_sql=false "$(cat scripts/create_bigquery_table.sql)"

CREATE TABLE IF NOT EXISTS `ai_ux_metrics.interactions` (
  timestamp TIMESTAMP,
  prompt_length INT64,
  response_length INT64,
  latency_ms INT64,
  confidence FLOAT64,
  model_used STRING,
  template_id STRING,
  has_hedging BOOL,
  session_id STRING
)
PARTITION BY DATE(timestamp)
OPTIONS(
  description = 'AI UX Case Study - interaction metrics for latency, accuracy, cost analysis'
);
