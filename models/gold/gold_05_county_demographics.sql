MODEL (
  name gold.county_demographics,
  kind FULL,
  description 'Gold 05: County population, income, and poverty trends 2019-2023'
);

SELECT
  county_name                   AS county,
  year,
  total_population,
  median_household_income,
  poverty_rate_pct,
  unemployment_rate_pct,
  LAG(total_population) OVER (PARTITION BY county_name ORDER BY year) AS prev_year_population,
  ROUND((total_population - LAG(total_population) OVER (PARTITION BY county_name ORDER BY year))
    * 100.0 / LAG(total_population) OVER (PARTITION BY county_name ORDER BY year), 2) AS population_growth_pct
FROM silver.census_acs5
ORDER BY county_name, year
