MODEL (
  name bronze.fred_indicators,
  kind FULL,
  description 'Bronze layer: FRED macroeconomic indicators (interest rates, TN economy)'
);

WITH raw AS (
  SELECT * FROM read_json_auto('raw_data/fred/fred_data_*.json')
),

unpivoted AS (
  SELECT 'FEDFUNDS'     AS series_id, 'federal_funds_rate'         AS series_label, unnest(FEDFUNDS.observations)     AS obs FROM raw UNION ALL
  SELECT 'MORTGAGE30US' AS series_id, 'mortgage_rate_30yr'          AS series_label, unnest(MORTGAGE30US.observations) AS obs FROM raw UNION ALL
  SELECT 'TNUR'         AS series_id, 'tennessee_unemployment_rate' AS series_label, unnest(TNUR.observations)         AS obs FROM raw UNION ALL
  SELECT 'TNRGSP'       AS series_id, 'tennessee_real_gdp'          AS series_label, unnest(TNRGSP.observations)       AS obs FROM raw UNION ALL
  SELECT 'TNPCPI'       AS series_id, 'tennessee_per_capita_income' AS series_label, unnest(TNPCPI.observations)       AS obs FROM raw UNION ALL
  SELECT 'TNSLGRTAX'    AS series_id, 'tennessee_tax_revenue'       AS series_label, unnest(TNSLGRTAX.observations)    AS obs FROM raw
)

SELECT
  series_id,
  series_label,
  CAST(obs.date AS DATE)        AS observation_date,
  TRY_CAST(obs.value AS DOUBLE) AS value,
  CURRENT_TIMESTAMP             AS ingested_at
FROM unpivoted
WHERE obs.date >= '2020-01-01'
