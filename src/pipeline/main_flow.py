import subprocess
import sys
from prefect import flow, task


@task(name="Ingest FRED data")
def ingest_fred():
    subprocess.run([sys.executable, "src/ingestion/fred_ingestion.py"], check=True)


@task(name="Ingest FDIC data")
def ingest_fdic():
    subprocess.run([sys.executable, "src/ingestion/fdic_ingestion.py"], check=True)


@task(name="Ingest SBA data")
def ingest_sba():
    subprocess.run([sys.executable, "src/ingestion/sba_ingestion.py"], check=True)


@task(name="Ingest Census data")
def ingest_census():
    subprocess.run([sys.executable, "src/ingestion/census_ingestion.py"], check=True)


@task(name="Ingest CFPB complaints")
def ingest_cfpb():
    subprocess.run([sys.executable, "src/ingestion/cfpb_ingestion.py"], check=True)


@task(name="Run SQLMesh pipeline")
def run_sqlmesh():
    subprocess.run(
        ["sqlmesh", "plan", "--auto-apply"],
        check=True,
    )


@task(name="Export Gold to PostgreSQL")
def export_to_postgres():
    subprocess.run([sys.executable, "src/ingestion/export_to_postgres.py"], check=True)


@task(name="Upload raw data to MinIO")
def upload_to_minio():
    subprocess.run([sys.executable, "src/ingestion/upload_to_minio.py"], check=True)


@flow(name="MidTenn Lend Map Pipeline", log_prints=True)
def main_flow():
    # Step 1: Ingest all data sources (FRED, FDIC, Census can run together)
    ingest_fred()
    ingest_fdic()
    ingest_census()

    # SBA and CFPB run separately (larger files)
    ingest_sba()
    ingest_cfpb()

    # Step 2: Upload raw data to MinIO
    upload_to_minio()

    # Step 3: Run SQLMesh Bronze -> Silver -> Gold
    run_sqlmesh()

    # Step 4: Export Gold tables to PostgreSQL for Metabase
    export_to_postgres()

    print("Pipeline complete!")


if __name__ == "__main__":
    main_flow()
