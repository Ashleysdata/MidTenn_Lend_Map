MODEL (
  name gold.risk_signals,
  kind FULL,
  description 'Gold 03: CFPB complaint volume by county and product type - v2'
);

SELECT
  county,
  product,
  COUNT(*)                                          AS total_complaints,
  SUM(CASE WHEN timely_response = 'Yes' THEN 1 ELSE 0 END) AS timely_responses,
  SUM(CASE WHEN consumer_disputed NOT IN ('N/A', 'No') THEN 1 ELSE 0 END) AS disputed_complaints,
  ROUND(SUM(CASE WHEN consumer_disputed NOT IN ('N/A', 'No') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dispute_rate_pct,
  ROUND(SUM(CASE WHEN timely_response = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS timely_response_rate_pct
FROM silver.cfpb_complaints
GROUP BY county, product
ORDER BY total_complaints DESC