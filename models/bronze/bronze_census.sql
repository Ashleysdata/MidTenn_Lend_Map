MODEL (
  name bronze.census_acs5,
  kind FULL,
  description 'Bronze layer: Census ACS 5-year data for Middle Tennessee counties'
);

SELECT
  CAST(year AS INTEGER)                     AS year,
  county_name,
  CAST(total_population AS INTEGER)         AS total_population,
  CAST(median_household_income AS INTEGER)  AS median_household_income,
  CAST(population_below_poverty AS INTEGER) AS population_below_poverty,
  CAST(employed_population AS INTEGER)      AS employed_population,
  CAST(unemployed_population AS INTEGER)    AS unemployed_population,
  CAST(total_workers AS INTEGER)            AS total_workers,
  CURRENT_TIMESTAMP                         AS ingested_at
FROM read_json_auto('raw_data/census/census_acs5_*.json')
WHERE year >= 2019
