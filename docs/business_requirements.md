# Business Requirements Document (BRD) - "E-Com Trend" Data Platform

## 1. Context and Problem Statement
"E-Com Trend" is a fast-growing online retailer. Currently, marketing and product analytics are isolated from each other. Clickstream data (user behavior on the website) is partially lost, and marketing ad spend cannot be accurately tied to actual orders inside the ERP/CRM system. This fragmentation prevents marketing budget optimization and limits the product team's ability to react swiftly to customer behavior.

## 2. Key Business Use Cases

### A. Customer Journey Map (CJM) Recovery & Visualization
* **Goal:** Reconstruct a continuous graph of user actions from the first ad click to the final purchase.
* **Business Value:** Identify bottlenecks on the website (drop-off points where users abandon the funnel) and optimize UX/UI.
* **Technical Criterion:** Implement clickstream sessionization (30-minute inactivity window) and calculate the transition matrix (`source_step` -> `target_step`) with deep analytical breakdowns by UTM tags.

### B. Product Analytics & Real-Time Triggers (Abandoned Carts)
* **Goal:** Identify users who added items to their shopping cart but did not complete the checkout process within 10–15 minutes.
* **Business Value:** Automatically export these user segments into the CRM system to trigger instant push notifications/emails, recovering up to 15% of potentially lost revenue.
* **Technical Criterion:** Ensure near real-time data ingestion and processing. The end-to-end latency from a website event to its availability in the "Abandoned Carts" Gold data mart must not exceed 30 seconds.

### C. End-to-End Marketing Analytics & Cohort LTV
* **Goal:** Calculate financial performance metrics (CAC, ROAS, ROI, LTV) broken down by marketing channels.
* **Business Value:** Reallocate ad budgets dynamically toward channels that bring loyal customers with high Customer Lifetime Value (LTV), rather than channels that just generate cheap initial clicks.
* **Technical Criterion:** Combine historical daily batch data from ad platform APIs with transactional data from the OLTP database, ensuring strict data deduplication.

### D. Supply Chain & Logistics Analytics (Status Change SLA)
* **Goal:** Monitor the exact duration of an order passing through internal fulfillment statuses (Created -> Packing -> Handed to Courier -> Delivered).
* **Business Value:** Reveal operational bottlenecks at warehouses and courier services to prevent marketplace fines and improve customer satisfaction.
* **Technical Criterion:** Implement historical status tracking on the Silver layer using the SCD Type 2 pattern or historical delta mapping.

### E. Advanced A/B Testing Evaluation (Product & Technical Health)
* **Goal:** Provide a comprehensive dashboard for evaluation of A/B experiments, combining product metrics with website performance characteristics.
* **Business Value:** Eliminate scenarios where a positive product change accidentally degrades website performance (Core Web Vitals). Allows analysts to immediately notice technical anomalies in the test group (e.g., error spikes or slow load times on mobile devices).
* **Technical Criterion:** Combine user behavioral actions, experiment group assignment (`variant_A` / `variant_B`), and browser performance logs (Page Load Time, HTTP statuses) within a unified session.
