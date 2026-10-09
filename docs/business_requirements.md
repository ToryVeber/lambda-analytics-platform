# Business Requirements Document (BRD) - "E-Com PL" Data Platform

## 1. Context and Problem Statement

"E-Com PL" drives user growth through three main channels:
- Paid Advertising (Google Ads, Yandex Direct, Telegram campaigns)
- Organic Search Engine Traffic (SEO)
- Email Marketing (CRM newsletters)

The company also runs parallel product experiments (A/B testing) and tracks frontend performance metrics.

**Problem:** Marketing spend, email metrics, product analytics, and technical logs exist in isolated silos. Because they are not correlated, it is impossible to calculate true channel efficiency, evaluate segmented A/B tests, or see how technical bugs impact sales.

**Solution:** Build a unified Medallion Lakehouse platform that merges traffic streams, behavioral logs, performance metrics, and transactions. This enables full customer segmentation, precise ROI tracking, and advanced A/B test validation with technical health guardrails.

## 2. Key Business Use Cases

### Use Case A: Omnichannel Marketing Attribution & Segmented LTV
* **Goal:** Calculate the exact financial performance (CAC, ROAS, ROI) and Lifetime Value (LTV) across paid, organic, and email traffic.
* **Business Value:** Stop wasting budget on channels that bring cheap clicks but zero repeat purchases. Understand the true value of "free" organic traffic and email retention.
* **Technical Requirement:** Daily batch ingestion of marketing costs (APIs) and orders (OLTP). Spark must deduplicate data and join transactions with user traffic sources on the Silver layer.

### Use Case B: Segmented A/B Testing & Technical Health Guardrails
* **Goal:** Evaluate product experiments with a simultaneous check on website performance metrics (Page Load Time, Error Rates) for each traffic segment.
* **Business Value:** Prevent situations where a new feature improves conversion for one group but breaks the site or slows it down for mobile users coming from ad campaigns.
* **Technical Requirement:** Near Real-Time (NRT) ingestion of clickstream and performance logs via Kafka. ClickHouse and dbt must compute exact percentiles (p95, p99) of page load speed and track HTTP error rates split by `variant_id` and `traffic_source`.

### Use Case C: Customer Segmentation & Retention (RFM & Cohorts)
* **Goal:** Group customers using RFM analysis (Recency, Frequency, Monetary) and track retention dynamics via monthly cohorts.
* **Business Value:** Identify and nurture VIP customers, reactivate churning users with targeted email campaigns, and measure long-term customer loyalty across different traffic sources.
* **Technical Requirement:** Historical analysis of OLTP order data. Spark must aggregate user transaction history on the Silver layer to compute RFM scores and cohort retention metrics for dbt to serve on the Gold layer.

## 3. Non-Functional Requirements & SLA

- **Data Volumes:** 
  - **Batch Sources (OLTP, APIs):** 1 TB of historical data with a 5 GB daily increment.
  - **Streaming Sources (Clickstream):** High-throughput web logs up to 1,000 RPS, averaging 10 GB of raw events per day.
- **Data Freshness (Latency):**
  - **Marketing & Retention Marts (Batch):** Updated once a day, ready by 06:00 UTC.
  - **A/B Testing & Technical Performance (Streaming):** Near Real-Time (NRT) updates with end-to-end latency under 30 seconds.
- **Query Performance:** 
  - Analytical queries from BI tools to Gold data marts must execute within `< 1.5 seconds` on billion-row datasets.

