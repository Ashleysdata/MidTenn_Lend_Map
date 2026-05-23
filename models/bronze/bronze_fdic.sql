MODEL (
  name bronze.fdic_institutions,
  kind FULL,
  description 'Bronze layer: FDIC bank institution data for Middle Tennessee counties'
);

SELECT
  NAME                          AS institution_name,
  CITY                          AS city,
  STNAME                        AS state_name,
  COUNTY                        AS county,
  CAST(ASSET AS DOUBLE)         AS total_assets,
  CAST(DEP AS DOUBLE)           AS total_deposits,
  CAST(NETINC AS DOUBLE)        AS net_income,
  CERT                          AS fdic_cert_number,
  ACTIVE                        AS is_active,
  REPDTE                        AS report_date,
  ESTYMD                        AS established_date,
  ENDEFYMD                      AS end_date,
  CURRENT_TIMESTAMP             AS ingested_at
FROM read_json_auto('raw_data/fdic/fdic_institutions_*.json')
