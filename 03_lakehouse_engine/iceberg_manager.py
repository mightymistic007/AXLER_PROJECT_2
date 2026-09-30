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
S3_TABLE_LOCATION = os.getenv("ICEBERG_LOCATION", "s3://lakehouse/orders")

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

def get_or_create_table(catalog: SqlCatalog):
    """
    Idempotently verifies or provisions the namespace and orders table in MinIO.
    """
    # 1. Ensure namespace exists
    namespace = TABLE_IDENTIFIER.split(".")[0]
    try:
        catalog.create_namespace(namespace)
        print(f"✓ Created catalog namespace '{namespace}'")
    except Exception:
        pass

    # 2. Load existing table or create new table with defined schema and S3 location
    try:
        table = catalog.load_table(TABLE_IDENTIFIER)
        print(f"✓ Connected to existing Iceberg table: {TABLE_IDENTIFIER}")
        return table
    except Exception:
        table = catalog.create_table(
            identifier=TABLE_IDENTIFIER,
            schema=iceberg_schema,
            location=S3_TABLE_LOCATION
        )
        print(f"✓ Initialized new Iceberg table '{TABLE_IDENTIFIER}' at {S3_TABLE_LOCATION}")
        return table

if __name__ == "__main__":
    cat = init_catalog()
    table = get_or_create_table(cat)
    print("✓ Active table location:", table.location())