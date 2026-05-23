MODEL (
  name gold.quarterly_lending_pulse,
  kind FULL,
  description 'Gold 12: Quarterly lending volume vs interest rate — executive trend view'
);

WITH quarterly_rates AS (
  SELECT
    YEAR(observation_date)                              AS year,
    QUARTER(observation_date)                           AS quarter,
    CONCAT(YEAR(observation_date), ' Q', QUARTER(observation_date)) AS year_quarter,
    ROUND(AVG(value), 2)                                AS avg_fed_funds_rate,
    ROUND(MAX(value) - MIN(value), 2)                   AS rate_volatility
  FROM silver.fred_indicators
  WHERE series_id = 'FEDFUNDS'
    AND value IS NOT NULL
  GROUP BY YEAR(observation_date), QUARTER(observation_date)
),

quarterly_loans AS (
  SELECT
    YEAR(approval_date)                                 AS year,
    QUARTER(approval_date)                              AS quarter,
    COUNT(*)                                            AS total_loans,
    ROUND(SUM(gross_approval_amount), 0)                AS total_amount,
    ROUND(AVG(gross_approval_amount), 0)                AS avg_loan_amount,
    COUNT(DISTINCT project_county)                      AS active_counties
  FROM silver.sba_loans
  GROUP BY YEAR(approval_date), QUARTER(approval_date)
)

SELECT
  r.year_quarter,
  r.year,
  r.quarter,
  r.avg_fed_funds_rate,
  r.rate_volatility,
  COALESCE(l.total_loans, 0)        AS total_loans,
  COALESCE(l.total_amount, 0)       AS total_amount,
  COALESCE(l.avg_loan_amount, 0)    AS avg_loan_amount,
  COALESCE(l.active_counties, 0)    AS active_counties,
  CASE
    WHEN r.avg_fed_funds_rate < 1.0 THEN 'Low'
    WHEN r.avg_fed_funds_rate < 4.0 THEN 'Medium'
    ELSE 'High'
  END                               AS rate_environment
FROM quarterly_rates r
LEFT JOIN quarterly_loans l
  ON r.year = l.year AND r.quarter = l.quarter
ORDER BY r.year, r.quarter
