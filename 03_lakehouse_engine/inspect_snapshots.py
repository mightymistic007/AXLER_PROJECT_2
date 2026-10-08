import sys
from iceberg_manager import init_catalog, get_or_create_table, TABLE_IDENTIFIER

def inspect_table_snapshots():
    """
    Connects to the Iceberg catalog and inspects table metadata,
    snapshot history, and schema evolution state.
    """
    print(f"[INSPECT] Connecting to Iceberg catalog for table: {TABLE_IDENTIFIER}")
    try:
        catalog = init_catalog()
        table = get_or_create_table(catalog)
    except Exception as e:
        print(f"[ERROR] Could not load table from catalog: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("APACHE ICEBERG TABLE METADATA AUDIT")
    print("=" * 60)
    print(f"Table Identifier : {table.identifier}")
    print(f"Storage Location : {table.location()}")
    print(f"Schema Version   : {table.schema().schema_id}")
    print(f"Current Snapshot : {table.current_snapshot().snapshot_id if table.current_snapshot() else 'None (Empty Table)'}")
    print("=" * 60)

    snapshots = list(table.snapshots())
    if not snapshots:
        print("\n[INFO] No data snapshots committed yet. Table is ready for streaming appends.")
    else:
        print(f"\n[COMMITS] Found {len(snapshots)} snapshot(s) in table history:\n")
        for idx, snap in enumerate(snapshots, start=1):
            print(f"  [{idx}] Snapshot ID  : {snap.snapshot_id}")
            print(f"      Timestamp    : {snap.timestamp_ms}")
            print(f"      Operation    : {snap.summary.operation if snap.summary else 'N/A'}")
            print(f"      Manifest List: {snap.manifest_list}")
            print("-" * 50)

    print("\n✓ TABLE SNAPSHOT AUDIT COMPLETE.")

if __name__ == "__main__":
    inspect_table_snapshots()
    