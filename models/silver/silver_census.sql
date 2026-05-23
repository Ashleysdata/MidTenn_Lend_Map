MODEL (
  name silver.census_acs5,
  kind FULL,
  description 'Silver layer: Census demographic data with poverty rate calculated'
);

SELECT
  year,
  county_name,
  total_population,
  median_household_income,
  population_below_poverty,
  employed_population,
  unemployed_population,
  total_workers,
  ROUND(population_below_poverty * 100.0 / total_population, 2) AS poverty_rate_pct,
  ROUND(unemployed_population * 100.0 / (employed_population + unemployed_population), 2) AS unemployment_rate_pct
FROM bronze.census_acs5
WHERE total_population > 0
