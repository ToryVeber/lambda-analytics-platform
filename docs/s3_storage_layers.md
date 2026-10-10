# S3 Object Storage Topology (MinIO Data Lake)

This document specifies the bucket topology and directory partitioning strategy within our MinIO S3 object storage across the Medallion architecture layers.

---

## 1. Bronze Bucket: `ecom-platform-bronze`
The landing zone for raw, immutable data. Directory naming is strictly organized by **source system** and partitioned by ingestion date (`year/month/day`) to support efficient incremental processing by Apache Spark.

*   📂 `snowplow_web/` - Raw batch JSON payloads from the Snowplow frontend collector.
    *   📂 `year=2026/`
        *   📂 `month=10/`
            *   📂 `day=11/` ➔ 📄 *raw_snowplow_batches_*.json*
*   📂 `google_ads_api/` - Daily marketing performance metrics fetched via Google Ads API.
    *   📂 `year=2026/month=10/day=11/` ➔ 📄 *google_spend_*.json*
*   📂 `yandex_direct_api/` - Daily ad spend data fetched via Yandex Direct API.
    *   📂 `year=2026/month=10/day=11/` ➔ 📄 *yandex_spend_*.json*
*   📂 `s3://ecom-platform-bronze/telegram_campaigns/` - Manual or API expense logs for Telegram channels and bloggers.
    *   📂 `year=2026/month=10/day=11/` ➔ 📄 *telegram_spend_*.json*
*   📂 `crm_postgres_dump/` - Snapshot tables exported daily from the transactional OLTP system.
    *   📂 `year=2026/month=10/day=11/`
        *   📂 `orders/` ➔ 📄 *orders_dump.csv*
        *   📂 `users/` ➔ 📄 *users_dump.csv*

---

## 2. Silver Bucket: `ecom-platform-silver`
Stores cleaned, parsed, and deduplicated tables. Unlike the Bronze layer, this bucket utilizes the **Apache Iceberg** table format. Directory paths represent structural namespaces, while file layouts (Parquet) and partitions are managed automatically by the Iceberg catalog engine.

*   📂 `iceberg_warehouse/`
    *   📂 `web_analytics.db/`
        *   📂 `snowplow_user_events/` ➔ *Sessionized detailed log table*
    *   📂 `marketing_finance.db/`
        *   📂 `marketing_spend_unified/` ➔ *Currency-normalized marketing costs*
        *   📂 `orders_historical/` ➔ *Deduplicated transaction history with status tracking*

---

## 3. Gold Bucket (Optional Deployment/Backups)
*Note: The primary Gold layer resides in the high-performance columnar ClickHouse. S3 is utilized strictly for cold storage backups or long-term historical snapshots of analytical data marts.*
