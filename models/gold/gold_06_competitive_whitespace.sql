MODEL (
  name gold.competitive_whitespace,
  kind FULL,
  description 'Gold 06: Bank density vs population to identify underserved markets'
);

WITH banks AS (
  SELECT
    UPPER(county)   AS county,
    COUNT(*)        AS bank_count,
    SUM(total_assets) AS total_bank_assets
  FROM silver.fdic_institutions
  GROUP BY UPPER(county)
),

census AS (
  SELECT
    UPPER(county_name)        AS county,
    total_population,
    median_household_income,
    poverty_rate_pct
  FROM silver.census_acs5
  WHERE year = 2023
)

SELECT
  c.county,
  c.total_population,
  c.median_household_income,
  c.poverty_rate_pct,
  b.bank_count,
  b.total_bank_assets,
  ROUND(c.total_population * 1.0 / b.bank_count, 0)  AS residents_per_bank,
  ROUND(b.bank_count * 10000.0 / c.total_population, 2) AS banks_per_10k_residents
FROM census c
LEFT JOIN banks b ON c.county = b.county
ORDER BY residents_per_bank DESC
