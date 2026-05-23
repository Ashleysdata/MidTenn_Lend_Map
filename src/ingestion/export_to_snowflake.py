import ssl
import duckdb
import pandas as pd
import os
from dotenv import load_dotenv

# Force Python stdlib SSL (no cert verification) before importing snowflake connector
ssl._create_default_https_context = ssl._create_unverified_context

import snowflake.connector

# Extract pyopenssl from snowflake's vendored urllib3 so it uses stdlib ssl above
try:
    from snowflake.connector.vendored.urllib3.contrib import pyopenssl as _sf_pyopenssl
    _sf_pyopenssl.extract_from_urllib3()
except Exception:
    pass

load_dotenv()

DUCKDB_PATH = "db/midtenn.duckdb"

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


def get_create_statement(table_name: str, df) -> str:
    type_map = {
        "int64": "NUMBER",
        "float64": "FLOAT",
        "object": "VARCHAR",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP",
        "date": "DATE",
    }
    cols = []
    for col, dtype in zip(df.columns, df.dtypes):
        sf_type = type_map.get(str(dtype), "VARCHAR")
        cols.append(f'"{col.upper()}" {sf_type}')
    return f"CREATE OR REPLACE TABLE {table_name} ({', '.join(cols)})"


def run():
    duck = duckdb.connect(DUCKDB_PATH)

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        insecure_mode=True,
    )
    cur = conn.cursor()

    cur.execute("CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH WAREHOUSE_SIZE = 'X-SMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE")
    cur.execute("USE WAREHOUSE COMPUTE_WH")
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {os.environ['SNOWFLAKE_DATABASE']}")
    cur.execute(f"USE DATABASE {os.environ['SNOWFLAKE_DATABASE']}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {os.environ['SNOWFLAKE_SCHEMA']}")
    cur.execute(f"USE SCHEMA {os.environ['SNOWFLAKE_SCHEMA']}")

    for table in GOLD_TABLES:
        schema, name = table.split(".")
        print(f"Exporting {table}...")

        df = duck.execute(f"SELECT * FROM {table}").df()
        df.columns = [c.upper() for c in df.columns]

        cur.execute(get_create_statement(name.upper(), df))

        def clean(v):
            try:
                if pd.isna(v):
                    return None
            except (TypeError, ValueError):
                pass
            if hasattr(v, "item"):
                return v.item()
            return v

        rows = [tuple(clean(v) for v in row) for row in df.itertuples(index=False, name=None)]
        placeholders = ", ".join(["%s"] * len(df.columns))
        cur.executemany(
            f"INSERT INTO {name.upper()} VALUES ({placeholders})", rows
        )

        print(f"  {len(df)} rows uploaded")

    cur.close()
    conn.close()
    duck.close()
    print("\nDone. All Gold tables exported to Snowflake.")


if __name__ == "__main__":
    run()
