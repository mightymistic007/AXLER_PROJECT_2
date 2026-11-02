import os
import json
import time
from typing import List, Dict, Any
from kafka import KafkaConsumer
from iceberg_manager import init_catalog, get_or_create_table, records_to_arrow_table
from validator import split_clean_and_corrupt_records

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "telemetry.clean")
BATCH_SIZE = int(os.getenv("INGESTION_BATCH_SIZE", "10"))
BATCH_TIMEOUT_SEC = float(os.getenv("BATCH_TIMEOUT_SEC", "3.0"))

def run_consumer():
    print("=" * 60)
    print("STARTING LAKEHOUSE STREAMING INGESTION ENGINE")
    print(f"Target Broker : {BOOTSTRAP_SERVERS}")
    print(f"Source Topic  : {TOPIC_NAME}")
    print("=" * 60)

    # 1. Initialize Iceberg Catalog and Table
    catalog = init_catalog()
    table = get_or_create_table(catalog)
    print(f"✓ Ready to append to Iceberg Table: {table.name()}")

    # 2. Connect Kafka Consumer
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=[BOOTSTRAP_SERVERS],
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="lakehouse_engine_group"
        )
        print(f"✓ Connected to Redpanda stream on topic '{TOPIC_NAME}'")
    except Exception as e:
        print(f"[WARN] Kafka direct connection failed: {e}")
        print("[INFO] Fallback: Generating simulated streaming micro-batches for demonstration...")
        consumer = None

    # 3. Micro-Batch Processing Loop
    if consumer:
        buffer: List[Dict[str, Any]] = []
        last_flush = time.time()

        for message in consumer:
            buffer.append(message.value)
            time_since_flush = time.time() - last_flush

            if len(buffer) >= BATCH_SIZE or (buffer and time_since_flush >= BATCH_TIMEOUT_SEC):
                flush_batch(table, buffer)
                buffer.clear()
                last_flush = time.time()
    else:
        # Fallback simulation to test and demo ACID appends immediately
        run_simulated_stream(table)

def flush_batch(table, raw_records: List[Dict[str, Any]]):
    clean, rejected = split_clean_and_corrupt_records(raw_records)
    print(f"\n[BATCH] Received {len(raw_records)} events -> {len(clean)} Clean, {len(rejected)} Quarantined")

    if rejected:
        for r in rejected:
            print(f"  [REJECTED] {r.get('transaction_id')} - Reason: {r.get('_rejection_reason')}")

    if clean:
        arrow_batch = records_to_arrow_table(clean)
        # Commit write to Apache Iceberg
        table.append(arrow_batch)
        current_snap = table.current_snapshot()
        print(f"  [ACID COMMIT] Appended {arrow_batch.num_rows} records to Iceberg.")
        print(f"  [SNAPSHOT ID] {current_snap.snapshot_id if current_snap else 'N/A'}")

def run_simulated_stream(table):
    """Generates synthetic transactions to showcase end-to-end ingestion and commits."""
    print("\n--- RUNNING DEMONSTRATION STREAM ---")
    mock_batches = [
        [
            {"transaction_id": "tx_demo_01", "customer_id": "cust_101", "item_count": 2, "subtotal_usd": 100.0, "tax_amount": 8.0, "total_usd": 108.0, "payment_status": "SUCCESS", "timestamp": "2026-11-02T10:00:00Z"},
            {"transaction_id": "tx_demo_02", "customer_id": "cust_102", "item_count": 1, "subtotal_usd": 50.0, "tax_amount": 4.0, "total_usd": 54.0, "payment_status": "SUCCESS", "timestamp": "2026-11-02T10:01:00Z"},
            {"transaction_id": "tx_corrupt_01", "customer_id": "cust_103", "item_count": 1, "subtotal_usd": 20.0, "tax_amount": None, "total_usd": 20.0, "payment_status": "SUCCESS", "timestamp": "2026-11-02T10:02:00Z"}
        ],
        [
            {"transaction_id": "tx_demo_03", "customer_id": "cust_104", "item_count": 4, "subtotal_usd": 200.0, "tax_amount": 16.0, "total_usd": 216.0, "payment_status": "SUCCESS", "timestamp": "2026-11-02T10:05:00Z"},
            {"transaction_id": "tx_corrupt_02", "customer_id": "cust_105", "item_count": 1, "subtotal_usd": 30.0, "tax_amount": 2.0, "total_usd": 999.0, "payment_status": "FAILED", "timestamp": "2026-11-02T10:06:00Z"}
        ]
    ]

    for idx, batch in enumerate(mock_batches, start=1):
        print(f"\n>> Ingesting Micro-Batch #{idx}...")
        flush_batch(table, batch)
        time.sleep(1)

    print("\n✓ STREAM CONSUMER DEMO COMPLETED.")

if __name__ == "__main__":
    run_consumer()