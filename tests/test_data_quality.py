"""Data quality tests against the DuckDB database.

Requires the full pipeline to have been run first.
Skipped automatically if db/midtenn.duckdb does not exist.
"""
import pytest


BRONZE_TABLES = [
    "bronze.census_acs5",
    "bronze.cfpb_complaints",
    "bronze.fdic_institutions",
    "bronze.fred_indicators",
    "bronze.sba_loans",
]

SILVER_TABLES = [
    "silver.census_acs5",
    "silver.cfpb_complaints",
    "silver.fdic_institutions",
    "silver.fred_indicators",
    "silver.sba_loans",
]

GOLD_TABLES = [
    "gold.loan_opportunity",
    "gold.industry_analysis",
    "gold.risk_signals",
    "gold.macro_trends",
    "gold.county_demographics",
    "gold.competitive_whitespace",
    "gold.customer_profile",
    "gold.loan_demand_trend",
    "gold.loan_health",
]


# ── Row count checks ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("table", BRONZE_TABLES)
def test_bronze_table_has_rows(db, table):
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert count > 0, f"{table} is empty"


@pytest.mark.parametrize("table", SILVER_TABLES)
def test_silver_table_has_rows(db, table):
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert count > 0, f"{table} is empty"


@pytest.mark.parametrize("table", GOLD_TABLES)
def test_gold_table_has_rows(db, table):
    count = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    assert count > 0, f"{table} is empty"


# ── SBA data quality ───────────────────────────────────────────────────────────

def test_silver_sba_no_null_approval_dates(db):
    nulls = db.execute(
        "SELECT COUNT(*) FROM silver.sba_loans WHERE approval_date IS NULL"
    ).fetchone()[0]
    assert nulls == 0, f"{nulls} rows have NULL approval_date"


def test_silver_sba_dates_from_2019(db):
    bad = db.execute(
        "SELECT COUNT(*) FROM silver.sba_loans WHERE approval_date < '2019-01-01'"
    ).fetchone()[0]
    assert bad == 0, f"{bad} rows predate 2019"


def test_silver_sba_no_zero_loan_amounts(db):
    bad = db.execute(
        "SELECT COUNT(*) FROM silver.sba_loans WHERE gross_approval_amount <= 0"
    ).fetchone()[0]
    assert bad == 0, f"{bad} rows with zero or negative loan amount"


# ── CFPB data quality ──────────────────────────────────────────────────────────

def test_silver_cfpb_no_duplicate_complaint_ids(db):
    total = db.execute("SELECT COUNT(*) FROM silver.cfpb_complaints").fetchone()[0]
    distinct = db.execute(
        "SELECT COUNT(DISTINCT complaint_id) FROM silver.cfpb_complaints"
    ).fetchone()[0]
    assert total == distinct, f"Found {total - distinct} duplicate complaint_ids"


def test_silver_cfpb_no_null_dates(db):
    nulls = db.execute(
        "SELECT COUNT(*) FROM silver.cfpb_complaints WHERE date_received IS NULL"
    ).fetchone()[0]
    assert nulls == 0, f"{nulls} rows have NULL date_received"


# ── FRED data quality ──────────────────────────────────────────────────────────

def test_silver_fred_no_null_values(db):
    nulls = db.execute(
        "SELECT COUNT(*) FROM silver.fred_indicators WHERE value IS NULL"
    ).fetchone()[0]
    assert nulls == 0, f"{nulls} NULL values in fred_indicators"


def test_silver_fred_expected_series(db):
    series = {
        r[0]
        for r in db.execute(
            "SELECT DISTINCT series_id FROM silver.fred_indicators"
        ).fetchall()
    }
    expected = {"FEDFUNDS", "MORTGAGE30US", "TNUR", "TNRGSP", "TNPCPI", "TNSLGRTAX"}
    missing = expected - series
    assert not missing, f"Missing FRED series: {missing}"


# ── Gold layer checks ──────────────────────────────────────────────────────────

def test_gold_loan_opportunity_covers_all_counties(db):
    counties = {
        r[0].upper()
        for r in db.execute(
            "SELECT DISTINCT county FROM gold.loan_opportunity"
        ).fetchall()
    }
    expected = {"DAVIDSON", "WILLIAMSON", "RUTHERFORD", "MONTGOMERY"}
    missing = expected - counties
    assert not missing, f"Missing counties in loan_opportunity: {missing}"


def test_gold_macro_trends_multiple_series(db):
    count = db.execute(
        "SELECT COUNT(DISTINCT series_id) FROM gold.macro_trends"
    ).fetchone()[0]
    assert count >= 5, f"Only {count} FRED series in macro_trends, expected at least 5"
