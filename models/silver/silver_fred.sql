MODEL (
  name silver.fred_indicators,
  kind FULL,
  description 'Silver layer: cleaned FRED economic indicators'
);

SELECT
  series_id,
  series_label,
  observation_date,
  value
FROM bronze.fred_indicators
WHERE value IS NOT NULL
ORDER BY series_id, observation_date
