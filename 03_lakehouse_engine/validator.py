import math
from typing import List, Dict, Any, Tuple

def validate_transaction(record: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates an individual telemetry record against lakehouse data quality rules.
    Returns (is_valid, failure_reason).
    """
    # 1. Required identifier checks
    if not record.get("transaction_id") or not str(record.get("transaction_id")).strip():
        return False, "Missing or empty transaction_id"
    
    if not record.get("customer_id") or not str(record.get("customer_id")).strip():
        return False, "Missing or empty customer_id"

    # 2. Field existence checks for financial attributes
    tax = record.get("tax_amount")
    subtotal = record.get("subtotal_usd")
    total = record.get("total_usd")

    if tax is None:
        return False, "Anomaly detected: null tax_amount"
    if subtotal is None:
        return False, "Missing subtotal_usd"
    if total is None:
        return False, "Missing total_usd"

    # 3. Numeric bounds checks
    try:
        subtotal = float(subtotal)
        tax = float(tax)
        total = float(total)
    except (ValueError, TypeError):
        return False, "Non-numeric values in financial fields"

    if subtotal < 0 or tax < 0 or total < 0:
        return False, "Negative values detected in transaction amounts"

    # 4. Arithmetic reconciliation check (subtotal + tax ~ total)
    expected_total = round(subtotal + tax, 2)
    actual_total = round(total, 2)
    if not math.isclose(expected_total, actual_total, abs_tol=0.05):
        return False, f"Reconciliation error: subtotal ({subtotal}) + tax ({tax}) != total ({total})"

    return True, "Valid"

def split_clean_and_corrupt_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Splits an incoming batch of streaming transactions into clean records
    and rejected/corrupted records with failure metadata.
    """
    clean_batch: List[Dict[str, Any]] = []
    rejected_batch: List[Dict[str, Any]] = []

    for r in records:
        is_valid, reason = validate_transaction(r)
        if is_valid:
            clean_batch.append(r)
        else:
            corrupt_record = dict(r)
            corrupt_record["_rejection_reason"] = reason
            rejected_batch.append(corrupt_record)

    return clean_batch, rejected_batch

if __name__ == "__main__":
    test_stream = [
        {"transaction_id": "tx_clean_1", "customer_id": "c1", "item_count": 2, "subtotal_usd": 100.0, "tax_amount": 8.0, "total_usd": 108.0, "payment_status": "SUCCESS", "timestamp": "2026-10-01T00:00:00Z"},
        {"transaction_id": "tx_bad_tax", "customer_id": "c2", "item_count": 1, "subtotal_usd": 50.0, "tax_amount": None, "total_usd": 50.0, "payment_status": "SUCCESS", "timestamp": "2026-10-01T00:01:00Z"},
        {"transaction_id": "tx_bad_math", "customer_id": "c3", "item_count": 1, "subtotal_usd": 40.0, "tax_amount": 5.0, "total_usd": 999.0, "payment_status": "SUCCESS", "timestamp": "2026-10-01T00:02:00Z"},
    ]
    clean, bad = split_clean_and_corrupt_records(test_stream)
    print(f"✓ Validation complete: {len(clean)} clean record(s), {len(bad)} rejected record(s).")
    for b in bad:
        print(f"  - Rejection: {b.get('transaction_id')} -> {b.get('_rejection_reason')}")