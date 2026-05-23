import os
from pathlib import Path
from minio import Minio
from dotenv import load_dotenv

load_dotenv()

client = Minio(
    "localhost:9000",
    access_key=os.environ["MINIO_ACCESS_KEY"],
    secret_key=os.environ["MINIO_SECRET_KEY"],
    secure=False,
)

BUCKET = "midtenn-raw"
RAW_DATA_DIR = Path("raw_data")


def ensure_bucket():
    if not client.bucket_exists(BUCKET):
        client.make_bucket(BUCKET)
        print(f"Created bucket: {BUCKET}")
    else:
        print(f"Bucket already exists: {BUCKET}")


def upload_all():
    ensure_bucket()
    files = list(RAW_DATA_DIR.rglob("*"))
    uploaded = 0

    for filepath in files:
        if not filepath.is_file():
            continue
        object_name = filepath.as_posix()
        client.fput_object(BUCKET, object_name, str(filepath))
        print(f"  Uploaded: {object_name}")
        uploaded += 1

    print(f"\nDone. {uploaded} files uploaded to s3://{BUCKET}/")


if __name__ == "__main__":
    upload_all()
