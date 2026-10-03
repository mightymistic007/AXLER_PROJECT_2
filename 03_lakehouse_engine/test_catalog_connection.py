import sys
from iceberg_manager import init_catalog, get_or_create_table, TABLE_IDENTIFIER

def test_catalog_and_table_provisioning():
    """
    Validates end-to-end connectivity between PyIceberg, SQLite metadata catalog,
    and MinIO S3 storage.
    """
    print("[TEST] Initializing Apache Iceberg Catalog...")
    try:
        catalog = init_catalog()
        assert catalog is not None, "Catalog initialization returned None"
        print("  [PASS] Catalog initialized successfully.")
    except Exception as e:
        print(f"  [FAIL] Failed to initialize catalog: {e}")
        sys.exit(1)

    print(f"[TEST] Verifying table provisioning for '{TABLE_IDENTIFIER}'...")
    try:
        table = get_or_create_table(catalog)
        assert table is not None, "Table reference returned None"
        print(f"  [PASS] Table '{table.identifier}' loaded/provisioned successfully.")
        print(f"  [INFO] Table Location: {table.location()}")
        print(f"  [INFO] Schema field count: {len(table.schema().fields)}")
    except Exception as e:
        print(f"  [FAIL] Failed table provisioning test: {e}")
        sys.exit(1)

    print("\n✓ ALL CATALOG & S3 CONNECTIVITY TESTS PASSED.")

if __name__ == "__main__":
    test_catalog_and_table_provisioning()
