# Technical Architecture Decisions (TAD)

The platform is designed around the principle of Compute and Storage Separation and implements the Lambda Architecture pattern.

## 1. Data Ingestion Profile & SLA
* **Batch Sources (OLTP, APIs):** 5 TB of historical data with a daily increment of 10 GB. Available in data marts by 06:00 UTC daily.
* **Streaming Sources (Clickstream):** Peak load up to 10,000 RPS (events per second) with a daily volume of 50 GB. Latency for real-time monitoring and trigger marts must be < 30 seconds.
* **Query Performance:** Analytical BI requests to the Gold layer must run with an average Response Time < 1.5 seconds on billion-row datasets.

## 2. Infrastructure Stack Justification

### Layer 1: Bronze (Raw Storage & Streaming Buffer)
* **MinIO S3:** Acts as a cost-effective, scalable Data Lake for raw, immutable data (JSON/CSV) coming from APIs and database dumps.
* **Apache Kafka:** Serves as a distributed append-only log, safely buffering high-throughput clickstream data (up to 10k RPS) directly from the frontend.

### Layer 2: Silver (Cleaned Detailed Layer)
* **Apache Spark (Batch & Streaming):** Chosen for heavy, distributed window functions (e.g., sessionization for CJM, joining high-volume log streams with user directories). Moving heavy processing out of the data warehouse prevents analytical performance degradation.
* **Apache Iceberg:** Implemented on top of MinIO to bring ACID transactions, efficient `MERGE/UPSERT` operations (essential for handling OLTP status updates), and seamless Schema Evolution (safeguarding pipelines against unexpected ad API changes).

### Layer 3: Gold (Analytical Data Marts)
* **ClickHouse:** A columnar distributed DBMS optimized for OLAP. It stores pre-aggregated data marts. Columnar compression allows product analysts to run complex aggregation queries (like calculating exact quantiles for page load times) over billions of rows in milliseconds.
* **dbt (Data Build Tool):** Governs the Transformation layer between Silver and Gold. It manages SQL models inside ClickHouse using the ELT approach, maintains data lineage graphs (DAG), and runs automated Data Quality tests.

### Orchestration
* **Apache Airflow:** Automates and schedules the batch pipelines, handles retry logic, establishes data lineage boundaries, and triggers alerting mechanisms.
