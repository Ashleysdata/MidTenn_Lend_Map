MODEL (
  name silver.cfpb_complaints,
  kind FULL,
  description 'Silver layer: cleaned CFPB complaint data for Middle Tennessee'
);

SELECT
  complaint_id,
  date_received,
  product,
  sub_product,
  issue,
  company,
  state,
  zip_code,
  county,
  timely_response,
  consumer_disputed,
  company_response
FROM bronze.cfpb_complaints
WHERE complaint_id IS NOT NULL
  AND date_received IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY complaint_id
  ORDER BY date_received
) = 1
