import os
from collections.abc import Generator

from dotenv import load_dotenv
from minio import Minio
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

load_dotenv()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()


def get_minio() -> Minio:
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.getenv("MINION_USER"),
        secret_key=os.getenv("MINION_PASSWORD"),
        secure=False,
    )

    if not client.bucket_exists("contabot"):
        client.make_bucket("contabot")

    return client