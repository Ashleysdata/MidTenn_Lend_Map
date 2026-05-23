MODEL (
  name silver.sba_loans,
  kind FULL,
  description 'Silver layer: deduplicated and cleaned SBA loan data for Middle Tennessee'
);

SELECT
  approval_date,
  TRIM(program_type)              AS program_type,
  borrower_name,
  borrower_city,
  borrower_zip,
  project_county,
  gross_approval_amount,
  sba_guaranteed_amount,
  approval_fiscal_year,
  naics_code,
  naics_description,
  business_type,
  business_age,
  loan_status,
  jobs_supported,
  term_months
FROM bronze.sba_loans
WHERE gross_approval_amount > 0
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY borrower_name, approval_date, gross_approval_amount
  ORDER BY approval_date
) = 1
