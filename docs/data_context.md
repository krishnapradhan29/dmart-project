# Data Context & Operational Schemas

## 1. Datasets Overview

The analytics agent operates over three curated operational tables.

### A. Store Daily Operations (`data/store_daily_clean.csv`)
- **Row Count:** Exactly 450 rows (90 days across 5 store locations).
- **Date Range:** 2026-04-01 to 2026-06-29 inclusive (90 calendar days).
- **Schema & Data Types:**
  - `date`: string (ISO 8601: YYYY-MM-DD) [Key / Filter]
  - `store_id`: string (S01 to S05) [Key / Filter]
  - `store`: string (Mumbai, Pune, Hyderabad, Bengaluru, Ahmedabad) [Key / Filter]
  - `footfall`: float64 (Store visitor count) [Metric]
  - `revenue_inr`: float64 (Daily gross store revenue) [Metric]
  - `daily_target_inr`: int64 (Store daily revenue target) [Metric]
  - `marketing_spend_inr`: int64 (Daily localized marketing expense) [Unapproved Metric]
  - `stockout_hours`: float64 (Store-wide hours items were out of stock) [Metric]
  - `discount_pct`: float64 (Average promotional discount percentage) [Metric]
  - `revenue_per_footfall`: float64 (Engineered: revenue / footfall) [Unapproved Metric]
  - `marketing_efficiency`: float64 (Engineered: revenue / marketing) [Unapproved Metric]
  - `achievement_pct`: float64 (Engineered: revenue / daily_target * 100) [Metric]
  - `shortfall_inr`: float64 (Engineered: daily_target - revenue) [Unapproved Metric]
  - `weekend_flag`: string (Engineered: "Yes" if Saturday/Sunday, else "No") [Unapproved Filter]
  - `performance_band`: string (Engineered: "Excellent" >= 100%, "Good" 75-99.99%, "Poor" < 75%) [Metric]
- **Data Quality Guarantees Established in Part A:**
  - 3 exact duplicate rows purged (Mumbai day 40, Hyderabad day 60, Ahmedabad day 15).
  - 1 impossible negative footfall value (-150 in Hyderabad on 2026-04-21) converted to missing.
  - 2 extreme outlier footfall values capped at the upper IQR bound (Ahmedabad day 55 capped to 2281.38; Mumbai day 8 capped to 2986.00).
  - 5 total missing footfall values imputed using store-specific median footfalls (Mumbai 2386.00, Pune 1509.50, Bengaluru 2065.00, Hyderabad 2216.00).
  - The dataset guarantees zero null values across all columns and 100% non-negative numeric quantities.

### B. Store Inventory (`data/inventory.csv`)
- **Row Count:** Exactly 40 rows (5 stores × 8 standard FMCG products).
- **Date Range:** None (Snapshot table representing current operational stock levels).
- **Schema & Data Types:**
  - `store_id`: string (S01 to S05) [Key / Filter]
  - `store`: string (Store name) [Key / Filter]
  - `product_id`: string (P01 to P08) [Key / Filter]
  - `product`: string (Product title and size) [Key / Filter]
  - `stock_units`: int64 (Current in-stock inventory count) [Metric]
  - `reorder_threshold`: int64 (Replenishment trigger level) [Metric]
- **Catalog Products:**
  - `P01`: Amul Milk 1L (Deliberate check case: threshold 100 across all stores; stock: Mumbai 240, Pune 85, Hyderabad 40, Bengaluru 130, Ahmedabad 100)
  - `P02`: Toor Dal 1kg
  - `P03`: Basmati Rice 5kg
  - `P04`: Sunflower Oil 1L
  - `P05`: Iodised Salt 1kg
  - `P06`: Instant Noodles 70g
  - `P07`: Glucose Biscuits 200g
  - `P08`: Detergent Powder 1kg

### C. Customer Feedback (`data/feedback.csv`)
- **Row Count:** Exactly 200 rows (40 feedback responses per store).
- **Date Range:** 2026-04-01 to 2026-06-29 inclusive.
- **Schema & Data Types:**
  - `feedback_id`: string (F001 to F200) [Key]
  - `store_id`: string (S01 to S05) [Key / Filter]
  - `store`: string (Store name) [Key / Filter]
  - `date`: string (ISO 8601: YYYY-MM-DD) [Filter - Dropped by feedback intent rules]
  - `rating`: string / float64 (Customer satisfaction rating 1 to 5; contains missing strings) [Metric]
  - `theme`: string (Operational category) [Metric]
- **Themes Captured:** Stock availability, Queue time, Pricing, Freshness, Staff behaviour.
- **Data Quality Note:** Contains 12 unrated feedback entries (blank ratings). The agent strictly calculates feedback averages across rated rows only, never imputing missing ratings with an average or default value.

---

## 2. Table Relationships & Joins

All three tables share the unified relational key:
- `store` (text: Mumbai, Pune, Hyderabad, Bengaluru, Ahmedabad)
- `store_id` (foreign key: S01 through S05)

The inventory catalog additionally joins via `product_id` and `product`. There is no cross-date joining between inventory and daily records because inventory is an instantaneous snapshot.

---

## 3. Supported Question Mapping

| Dataset | Supported Question Types | Sample Questions |
| :--- | :--- | :--- |
| `store_daily_clean.csv` | Single-date store lookups, target vs actual evaluations, cross-store metric comparisons, historical range averages. | "What was Pune's revenue on 15 May 2026?", "Did Mumbai hit its target on 2026-05-21?", "Which store had the highest revenue on 2026-06-10?" |
| `inventory.csv` | Product threshold stockout checks, store-level inventory availability checks. | "Which stores are below the reorder threshold for Amul Milk?", "What is the stock of Toor Dal in Pune?" |
| `feedback.csv` | Customer sentiment summaries, mean store ratings (rated rows only), dominant customer themes. | "What are customers saying about Hyderabad?", "What is the customer rating for Pune?" |