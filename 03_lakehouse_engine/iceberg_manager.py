import os
from typing import List, Dict, Any
import pyarrow as pa
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    StringType,
    LongType,
    FloatType,
    NestedField
)

# Configuration with fallback defaults
CATALOG_NAME = os.getenv("ICEBERG_CATALOG_NAME", "lakehouse_catalog")
CATALOG_URI = os.getenv("ICEBERG_CATALOG_URI", "sqlite:////tmp/iceberg_catalog.db")
S3_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
S3_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "password123")
TABLE_IDENTIFIER = os.getenv("ICEBERG_TABLE", "lakehouse.orders")
S3_TABLE_LOCATION = os.getenv("ICEBERG_LOCATION", "s3://lakehouse/orders")

# Strongly-typed Iceberg transaction schema
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

# PyArrow Schema matching Iceberg field specifications
arrow_schema = pa.schema([
    ("transaction_id", pa.string()),
    ("customer_id", pa.string()),
    ("item_count", pa.int64()),
    ("subtotal_usd", pa.float32()),
    ("tax_amount", pa.float32()),
    ("total_usd", pa.float32()),
    ("payment_status", pa.string()),
    ("timestamp", pa.string())
])

def init_catalog() -> SqlCatalog:
    """Initializes and returns an Apache Iceberg SqlCatalog connected to MinIO S3."""
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
    """Idempotently loads or creates the orders table in the lakehouse namespace."""
    namespace = TABLE_IDENTIFIER.split(".")[0]
    try:
        catalog.create_namespace(namespace)
        print(f"✓ Namespace '{namespace}' verified/created")
    except Exception:
        pass

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
        print(f"✓ Provisioned new Iceberg table '{TABLE_IDENTIFIER}' at {S3_TABLE_LOCATION}")
        return table

def records_to_arrow_table(records: List[Dict[str, Any]]) -> pa.Table:
    """
    Transforms a batch of streaming JSON transaction dictionaries into
    a strictly-typed PyArrow Table matching the Iceberg table layout.
    """
    if not records:
        return pa.Table.from_batches([], schema=arrow_schema)

    formatted_data = {
        "transaction_id": [str(r.get("transaction_id", "")) for r in records],
        "customer_id": [str(r.get("customer_id", "")) for r in records],
        "item_count": [int(r.get("item_count", 0)) for r in records],
        "subtotal_usd": [float(r.get("subtotal_usd", 0.0)) for r in records],
        "tax_amount": [float(r.get("tax_amount", 0.0)) for r in records],
        "total_usd": [float(r.get("total_usd", 0.0)) for r in records],
        "payment_status": [str(r.get("payment_status", "UNKNOWN")) for r in records],
        "timestamp": [str(r.get("timestamp", "")) for r in records]
    }
    return pa.Table.from_pydict(formatted_data, schema=arrow_schema)

if __name__ == "__main__":
    cat = init_catalog()
    table = get_or_create_table(cat)
    print("✓ Active table location:", table.location())
    
    # Test batch conversion
    test_batch = [{
        "transaction_id": "tx_test_01",
        "customer_id": "cust_100",
        "item_count": 2,
        "subtotal_usd": 50.0,
        "tax_amount": 4.0,
        "total_usd": 54.0,
        "payment_status": "SUCCESS",
        "timestamp": "2026-09-28T10:00:00Z"
    }]
    arrow_tbl = records_to_arrow_table(test_batch)
    print(f"✓ PyArrow conversion validated: {arrow_tbl.num_rows} row(s) mapped.")
    