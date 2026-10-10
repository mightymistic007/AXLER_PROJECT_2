
# Module 03: Lakehouse Storage Engine

A transactional data lakehouse consumer and metadata management layer leveraging **Apache Iceberg**, **MinIO (S3)**, **PyIceberg**, and **PyArrow**.

---

## 1. Architecture Overview

The lakehouse engine consumes clean telemetry streams from Redpanda/Kafka and persists data into open-format Parquet files governed by an Apache Iceberg table catalog.

* **Catalog Type:** `SqlCatalog` backed by SQLite metadata storage (`sqlite:////tmp/iceberg_catalog.db`).
* **Object Store:** MinIO S3-compatible bucket (`s3://lakehouse/orders`).
* **File Format:** Apache Parquet with Snappy compression.
* **In-Memory Transformation:** PyArrow batch mapping for strict typing.

---

## 2. Table Schema Specification

The Iceberg table `lakehouse.orders` enforces the following data contract:

| Field Name         | Iceberg Type   | PyArrow Type     | Required | Description                                   |
| :----------------- | :------------- | :--------------- | :------- | :-------------------------------------------- |
| `transaction_id` | `StringType` | `pa.string()`  | Yes      | Unique UUID for checkout event                |
| `customer_id`    | `StringType` | `pa.string()`  | Yes      | Unique customer identifier                    |
| `item_count`     | `LongType`   | `pa.int64()`   | Yes      | Total items in order                          |
| `subtotal_usd`   | `FloatType`  | `pa.float32()` | Yes      | Pre-tax order subtotal                        |
| `tax_amount`     | `FloatType`  | `pa.float32()` | Yes      | Calculated transaction tax                    |
| `total_usd`      | `FloatType`  | `pa.float32()` | Yes      | Gross total charged                           |
| `payment_status` | `StringType` | `pa.string()`  | Yes      | Status (`SUCCESS`, `PENDING`, `FAILED`) |
| `timestamp`      | `StringType` | `pa.string()`  | Yes      | ISO-8601 UTC timestamp                        |

---

## 3. Directory Layout & Core Modules

```text
03_lakehouse_engine/
├── .env.example               # Environment variable configuration template
├── Dockerfile                 # Containerized runtime build definition
├── requirements.txt           # Python dependency specifications
├── iceberg_manager.py         # Catalog initialization, schema, & table management
├── validator.py               # Pre-ingestion validation & financial reconciliation
├── inspect_snapshots.py       # Metadata audit & snapshot time-travel inspection
├── test_catalog_connection.py # Automated catalog & S3 connectivity test
├── test_arrow_mapping.py      # Unit tests for PyArrow schema casting
└── README.md                  # Engine technical documentation
```
