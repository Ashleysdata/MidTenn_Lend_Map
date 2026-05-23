import pytest
import duckdb
from pathlib import Path

DB_PATH = Path("db/midtenn.duckdb")


@pytest.fixture(scope="session")
def db():
    if not DB_PATH.exists():
        pytest.skip("DuckDB not found — run the pipeline first")
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    yield conn
    conn.close()
