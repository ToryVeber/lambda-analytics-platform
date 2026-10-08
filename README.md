# Medallion Lakehouse Analytics Platform for E-Commerce

This repository contains the architecture and implementation of an Enterprise Data Platform built for the e-commerce sector. The platform handles end-to-end marketing attribution, Customer Journey Map (CJM) sessionization, supply chain SLA tracking, and advanced A/B testing evaluation.

## 🚀 Key Features & Capabilities
* **Lambda Architecture:** Combines an Airflow + Spark batch loop with a Kafka + Spark Streaming real-time track.
* **Lakehouse Paradigm:** Built with Apache Iceberg over MinIO S3 storage, delivering full ACID compliance and Schema Evolution.
* **High-Performance Analytics:** Utilizes ClickHouse and dbt to serve interactive BI dashboards with sub-second latency.
* **Advanced A/B Testing Matrix:** Correlates product conversion rates directly with technical web performance metrics (Page Load Time percentiles, HTTP Error Rates).

## 🗺️ Documentation & Specifications
For deep-dives into our design decisions, explore the specifications below:
* [Business Requirements & Use Cases](docs/business_requirements.md)
* [Technical Architecture & Stack Justification](docs/technical_architecture.md)

---
*Developed as a data engineering portfolio project focused on high-throughput analytical systems.*
