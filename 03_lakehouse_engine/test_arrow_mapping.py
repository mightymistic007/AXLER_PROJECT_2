import sys
import pyarrow as pa
from iceberg_manager import records_to_arrow_table, arrow_schema

def test_records_to_arrow_table():
    print("[TEST] Running PyArrow Schema & Type Mapping Tests...")

    # Case 1: Standard valid payload
    valid_payload = [
        {
            "transaction_id": "tx_101",
            "customer_id": "cust_501",
            "item_count": 3,
            "subtotal_usd": 120.50,
            "tax_amount": 9.64,
            "total_usd": 130.14,
            "payment_status": "SUCCESS",
            "timestamp": "2026-10-01T12:00:00Z"
        },
        {
            "transaction_id": "tx_102",
            "customer_id": "cust_502",
            "item_count": 1,
            "subtotal_usd": 15.00,
            "tax_amount": 1.20,
            "total_usd": 16.20,
            "payment_status": "PENDING",
            "timestamp": "2026-10-01T12:01:00Z"
        }
    ]

    table = records_to_arrow_table(valid_payload)
    assert isinstance(table, pa.Table), "Output must be a pyarrow.Table"
    assert table.num_rows == 2, f"Expected 2 rows, got {table.num_rows}"
    assert table.num_columns == 8, f"Expected 8 columns, got {table.num_columns}"
    print("  [PASS] Standard batch successfully converted to PyArrow Table.")

    # Case 2: Schema strictness validation
    for field in arrow_schema:
        assert table.schema.field(field.name).type == field.type, (
            f"Type mismatch on field {field.name}: "
            f"expected {field.type}, got {table.schema.field(field.name).type}"
        )
    print("  [PASS] All PyArrow column datatypes strictly match Iceberg specifications.")

    # Case 3: Empty input handling
    empty_table = records_to_arrow_table([])
    assert empty_table.num_rows == 0, "Empty list should produce 0 rows"
    assert empty_table.num_columns == 8, "Empty table must preserve table schema"
    print("  [PASS] Empty batch preserves complete schema definition.")

    # Case 4: Missing field defaulting
    partial_payload = [{
        "transaction_id": "tx_partial_01",
        "customer_id": "cust_999"
    }]
    partial_table = records_to_arrow_table(partial_payload)
    assert partial_table.num_rows == 1, "Partial batch must yield 1 row"
    assert partial_table.column("total_usd")[0].as_py() == 0.0, "Missing float should default to 0.0"
    assert partial_table.column("payment_status")[0].as_py() == "UNKNOWN", "Missing status should default to UNKNOWN"
    print("  [PASS] Missing attributes defaulted safely without raising runtime exceptions.")

    print("\n✓ ALL PYARROW BATCH MAPPING TESTS PASSED.")

if __name__ == "__main__":
    test_records_to_arrow_table()