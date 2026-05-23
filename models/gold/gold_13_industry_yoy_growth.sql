MODEL (
  name gold.industry_yoy_growth,
  kind FULL,
  description 'Gold 13: Year-over-year SBA loan growth by county and industry — drill-through detail for loan_demand_trend'
);

WITH yearly AS (
  SELECT
    project_county                        AS county,
    YEAR(approval_date)                   AS year,
    naics_description                     AS industry,
    COUNT(*)                              AS total_loans,
    ROUND(SUM(gross_approval_amount), 0)  AS total_amount
  FROM silver.sba_loans
  WHERE naics_description IS NOT NULL
  GROUP BY project_county, YEAR(approval_date), naics_description
),

with_yoy AS (
  SELECT
    county,
    year,
    industry,
    total_loans,
    total_amount,
    LAG(total_loans) OVER (PARTITION BY county, industry ORDER BY year) AS prev_year_loans,
    ROUND(
      (total_loans - LAG(total_loans) OVER (PARTITION BY county, industry ORDER BY year))
        * 100.0
        / NULLIF(LAG(total_loans) OVER (PARTITION BY county, industry ORDER BY year), 0),
      2
    ) AS loan_growth_pct
  FROM yearly
),

ranked AS (
  SELECT
    *,
    RANK() OVER (PARTITION BY county, year ORDER BY loan_growth_pct DESC NULLS LAST) AS growth_rank
  FROM with_yoy
  WHERE prev_year_loans IS NOT NULL
)

SELECT
  county,
  year,
  industry,
  total_loans,
  total_amount,
  prev_year_loans,
  loan_growth_pct,
  growth_rank
FROM ranked
ORDER BY county, year, growth_rank
