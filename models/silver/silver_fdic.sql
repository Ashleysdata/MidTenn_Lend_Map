MODEL (
  name silver.fdic_institutions,
  kind FULL,
  description 'Silver layer: cleaned FDIC bank data for Middle Tennessee'
);

SELECT
  institution_name,
  city,
  county,
  total_assets,
  total_deposits,
  net_income,
  fdic_cert_number,
  is_active,
  report_date,
  established_date
FROM bronze.fdic_institutions
WHERE institution_name IS NOT NULL
  AND county IS NOT NULL
