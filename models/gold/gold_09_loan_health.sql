MODEL (
  name gold.loan_health,
  kind FULL,
  description 'Gold 09: Loan status and charge-off rates by county and industry',
  audits (
    not_null(columns := (county, loan_status)),
    accepted_values(column := loan_status, is_in := ('EXEMPT', 'PIF', 'CANCLD', 'COMMIT', 'CHGOFF', 'NOT FUNDED'))
  )
);

SELECT
  project_county                  AS county,
  naics_description,
  loan_status,
  COUNT(*)                        AS total_loans,
  SUM(gross_approval_amount)      AS total_amount,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY project_county), 2) AS pct_of_county_loans
FROM silver.sba_loans
WHERE loan_status IS NOT NULL
GROUP BY project_county, naics_description, loan_status
ORDER BY project_county, total_loans DESC
