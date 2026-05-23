MODEL (
  name gold.rate_sensitivity,
  kind FULL,
  description 'Gold 11: SBA loan demand by industry across different interest rate environments'
);

WITH quarterly_rates AS (
  SELECT
    YEAR(observation_date)                                          AS year,
    QUARTER(observation_date)                                       AS quarter,
    CONCAT(YEAR(observation_date), ' Q', QUARTER(observation_date)) AS year_quarter,
    ROUND(AVG(value), 2)                                            AS avg_fed_funds_rate,
    CASE
      WHEN AVG(value) < 1.0 THEN 'Low (<1%)'
      WHEN AVG(value) < 4.0 THEN 'Medium (1-4%)'
      ELSE                       'High (>4%)'
    END                                                             AS rate_environment
  FROM silver.fred_indicators
  WHERE series_id = 'FEDFUNDS'
    AND value IS NOT NULL
  GROUP BY YEAR(observation_date), QUARTER(observation_date)
),

sba_by_quarter AS (
  SELECT
    YEAR(approval_date)                                             AS year,
    QUARTER(approval_date)                                          AS quarter,
    naics_description,
    COUNT(*)                                                        AS total_loans,
    ROUND(SUM(gross_approval_amount), 0)                            AS total_amount,
    ROUND(AVG(gross_approval_amount), 0)                            AS avg_loan_amount
  FROM silver.sba_loans
  WHERE naics_description IS NOT NULL
  GROUP BY YEAR(approval_date), QUARTER(approval_date), naics_description
)

SELECT
  r.year_quarter,
  r.year,
  r.quarter,
  r.rate_environment,
  r.avg_fed_funds_rate,
  s.naics_description,
  s.total_loans,
  s.total_amount,
  s.avg_loan_amount
FROM sba_by_quarter s
JOIN quarterly_rates r ON s.year = r.year AND s.quarter = r.quarter
ORDER BY r.year, r.quarter, s.total_loans DESC
