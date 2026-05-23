MODEL (
  name gold.macro_trends,
  kind FULL,
  description 'Gold 04: Annual average of FRED interest rates and TN economic indicators'
);

SELECT
  YEAR(observation_date)        AS year,
  series_id,
  series_label,
  ROUND(AVG(value), 4)          AS annual_avg,
  ROUND(MIN(value), 4)          AS annual_min,
  ROUND(MAX(value), 4)          AS annual_max
FROM silver.fred_indicators
GROUP BY YEAR(observation_date), series_id, series_label
ORDER BY series_id, year
