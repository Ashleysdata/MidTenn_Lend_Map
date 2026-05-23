MODEL (
  name bronze.cfpb_complaints,
  kind FULL,
  description 'Bronze layer: CFPB consumer financial complaints for Middle Tennessee zip codes'
);

SELECT
  complaint_id                          AS complaint_id,
  CAST(date_received AS TIMESTAMP)      AS date_received,
  CAST(date_sent_to_company AS TIMESTAMP) AS date_sent_to_company,
  product                               AS product,
  sub_product                           AS sub_product,
  issue                                 AS issue,
  sub_issue                             AS sub_issue,
  company                               AS company,
  state                                 AS state,
  zip_code                              AS zip_code,
  county                                AS county,
  timely                                AS timely_response,
  consumer_disputed                     AS consumer_disputed,
  company_response                      AS company_response,
  submitted_via                         AS submitted_via,
  has_narrative                         AS has_narrative,
  CURRENT_TIMESTAMP                     AS ingested_at
FROM read_json_auto('raw_data/cfpb/cfpb_complaints_*.json')
WHERE YEAR(CAST(date_received AS TIMESTAMP)) >= 2020
