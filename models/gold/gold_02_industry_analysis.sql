MODEL (
  name gold.industry_analysis,
  kind FULL,
  description 'Gold 02: SBA loan volume and amount by industry (NAICS) and county'
);

SELECT
  project_county                        AS county,
  naics_code,
  naics_description,
  COUNT(*)                              AS total_loans,
  SUM(gross_approval_amount)            AS total_approved_amount,
  ROUND(AVG(gross_approval_amount), 0)  AS avg_loan_amount,
  SUM(jobs_supported)                   AS total_jobs_supported
FROM silver.sba_loans
WHERE naics_code IS NOT NULL
AND naics_description IS NOT NULL
AND naics_description != ''
GROUP BY project_county, naics_code, naics_description
ORDER BY total_approved_amount DESC
