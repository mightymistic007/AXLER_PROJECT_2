import os
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    StringType,
    LongType,
    FloatType,
    NestedField
)

# Load configurations with fallback defaults
CATALOG_NAME = os.getenv("ICEBERG_CATALOG_NAME", "lakehouse_catalog")
CATALOG_URI = os.getenv("ICEBERG_CATALOG_URI", "sqlite:////tmp/iceberg_catalog.db")
S3_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
S3_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
TABLE_IDENTIFIER = os.getenv("ICEBERG_TABLE", "lakehouse.orders")

# Define strongly-typed Apache Iceberg transaction schema
iceberg_schema = Schema(
    NestedField(field_id=1, name="transaction_id", field_type=StringType(), required=True),
    NestedField(field_id=2, name="customer_id", field_type=StringType(), required=True),
    NestedField(field_id=3, name="item_count", field_type=LongType(), required=True),
    NestedField(field_id=4, name="subtotal_usd", field_type=FloatType(), required=True),
    NestedField(field_id=5, name="tax_amount", field_type=FloatType(), required=True),
    NestedField(field_id=6, name="total_usd", field_type=FloatType(), required=True),
    NestedField(field_id=7, name="payment_status", field_type=StringType(), required=True),
    NestedField(field_id=8, name="timestamp", field_type=StringType(), required=True)
)

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
    print("✓ Configured schema fields:", [field.name for field in iceberg_schema.fields])
    