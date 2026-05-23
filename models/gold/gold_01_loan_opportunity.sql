MODEL (
  name gold.loan_opportunity,
  kind FULL,
  description 'Gold 01: SBA loan volume and FDIC bank supply by county'
);

WITH sba AS (
  SELECT
    project_county                        AS county,
    COUNT(*)                              AS total_loans,
    SUM(gross_approval_amount)            AS total_approved_amount,
    ROUND(AVG(gross_approval_amount), 0)  AS avg_loan_amount,
    SUM(jobs_supported)                   AS total_jobs_supported
  FROM silver.sba_loans
  GROUP BY project_county
),

fdic AS (
  SELECT
    UPPER(county)   AS county,
    COUNT(*)        AS bank_count,
    SUM(total_assets)  AS total_bank_assets
  FROM silver.fdic_institutions
  GROUP BY UPPER(county)
),

census AS (
  SELECT
    UPPER(county_name)          AS county,
    total_population,
    median_household_income
  FROM silver.census_acs5
  WHERE year = 2023
)

SELECT
  s.county,
  s.total_loans,
  s.total_approved_amount,
  s.avg_loan_amount,
  s.total_jobs_supported,
  f.bank_count,
  f.total_bank_assets,
  c.total_population,
  c.median_household_income,
  ROUND(s.total_loans * 1.0 / c.total_population * 10000, 2) AS loans_per_10k_residents
FROM sba s
LEFT JOIN fdic f ON s.county = f.county
LEFT JOIN census c ON s.county = c.county
ORDER BY s.total_approved_amount DESC
