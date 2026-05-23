MODEL (
  name gold.customer_profile,
  kind FULL,
  description 'Gold 07: Business size and type profile from SBA loan data'
);

SELECT
  project_county                        AS county,
  business_type,
  business_age,
  COUNT(*)                              AS total_loans,
  ROUND(AVG(gross_approval_amount), 0)  AS avg_loan_amount,
  ROUND(AVG(jobs_supported), 1)         AS avg_jobs_supported,
  SUM(gross_approval_amount)            AS total_approved_amount
FROM silver.sba_loans
WHERE business_type IS NOT NULL
GROUP BY project_county, business_type, business_age
ORDER BY project_county, total_loans DESC
