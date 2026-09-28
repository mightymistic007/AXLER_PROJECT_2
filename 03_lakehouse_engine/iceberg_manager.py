import os
from pyiceberg.catalog.sql import SqlCatalog

# Load configurations with fallback defaults
CATALOG_NAME = os.getenv("ICEBERG_CATALOG_NAME", "lakehouse_catalog")
CATALOG_URI = os.getenv("ICEBERG_CATALOG_URI", "sqlite:////tmp/iceberg_catalog.db")
S3_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
S3_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")

def init_catalog() -> SqlCatalog:
    """
    Initializes and returns an Apache Iceberg SqlCatalog backed by SQLite
    and configured for MinIO S3 object storage.
    """
    catalog = SqlCatalog(
        CATALOG_NAME,
        **{
            "uri": CATALOG_URI,
            "s3.endpoint": S3_ENDPOINT,
            "s3.access-key-id": S3_ACCESS_KEY,
            "s3.secret-access-key": S3_SECRET_KEY,
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
        },
    )
    print(f"✓ Initialized Iceberg catalog '{CATALOG_NAME}' connected to {S3_ENDPOINT}")
    return catalog

if __name__ == "__main__":
    cat = init_catalog()
