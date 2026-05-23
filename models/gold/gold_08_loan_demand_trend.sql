MODEL (
  name gold.loan_demand_trend,
  kind FULL,
  description 'Gold 08: Year-over-year SBA loan volume trend by county'
);

WITH yearly AS (
  SELECT
    project_county                        AS county,
    YEAR(approval_date)                   AS year,
    COUNT(*)                              AS total_loans,
    SUM(gross_approval_amount)            AS total_approved_amount,
    ROUND(AVG(gross_approval_amount), 0)  AS avg_loan_amount
  FROM silver.sba_loans
  GROUP BY project_county, YEAR(approval_date)
)

SELECT
  county,
  year,
  total_loans,
  total_approved_amount,
  avg_loan_amount,
  LAG(total_loans) OVER (PARTITION BY county ORDER BY year)   AS prev_year_loans,
  ROUND((total_loans - LAG(total_loans) OVER (PARTITION BY county ORDER BY year))
    * 100.0 / LAG(total_loans) OVER (PARTITION BY county ORDER BY year), 2) AS loan_growth_pct
FROM yearly
ORDER BY county, year
