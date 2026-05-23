import duckdb
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DUCKDB_PATH = "db/midtenn.duckdb"
PG_URL = "postgresql://datajing:datajing@localhost:5434/metabase"

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
    "gold.county_coordinates",
    "gold.rate_sensitivity",
    "gold.quarterly_lending_pulse",
    "gold.industry_yoy_growth",
]


def run():
    duck = duckdb.connect(DUCKDB_PATH)
    engine = create_engine(PG_URL)

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold"))
        conn.commit()

    for table in GOLD_TABLES:
        schema, name = table.split(".")
        print(f"Exporting {table}...")
        df = duck.execute(f"SELECT * FROM {table}").df()
        df.to_sql(name, engine, schema=schema, if_exists="replace", index=False)
        print(f"  {len(df)} rows exported")

    duck.close()
    print("\nDone. All Gold tables exported to PostgreSQL.")


if __name__ == "__main__":
    run()
