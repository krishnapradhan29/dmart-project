# Product Requirements Document: Grounded Conversational Analytics Agent

## 1. Goal

### Outcome
A grounded, deterministic conversational analytics assistant that interprets natural language operational queries from leadership, executes strictly approved, parameterized data queries against cleaned store operations records, and generates verified, auditable responses where every numeric figure is directly traceable to backend data fields.

### Stakeholder
- **Primary Stakeholder:** Kavita Rao, Regional Operations Director (Avenue Supermarts / DMart).
- **Core Need:** Rapid, trustworthy, on-demand answers to routine regional operational inquiries (daily revenue, target achievement, store-level inventory stockouts, and aggregated customer sentiment) without manual spreadsheet extraction or hallucinated numbers.

### Scope
- **Geographic Scope:** Exactly five DMart store locations: Mumbai (`S01`), Pune (`S02`), Hyderabad (`S03`), Bengaluru (`S04`), and Ahmedabad (`S05`).
- **Temporal Scope:** Exactly 90 calendar days from 2026-04-01 to 2026-06-29 inclusive.
- **Datasets:** Three clean operational datasets: `store_daily_clean.csv`, `inventory.csv`, and `feedback.csv`.

### Decision Boundary
- The assistant operates strictly in analytical and reporting capacities.
- It provides historical and diagnostic metrics within verified boundaries.
- It possesses zero autonomous operational authority (no inventory replenishment, order routing, threshold adjustments, or staff messaging).
- Any request requiring subjective business strategy, predictive modeling, or unapproved metrics must be escalated or safely rejected.

---

## 2. Approved Field List

The assistant is strictly constrained to the following **11 reportable metric fields** across the three operational datasets. Only these 11 fields may appear in data selection queries or be surfaced as measured values in responses:

### From `store_daily_clean.csv`:
1. `revenue_inr`
2. `daily_target_inr`
3. `footfall`
4. `stockout_hours`
5. `discount_pct`
6. `achievement_pct`
7. `performance_band`

*(Note: `marketing_spend_inr`, `revenue_per_footfall`, `marketing_efficiency`, `shortfall_inr`, and `weekend_flag` are intentionally NOT approved reportable metric fields).*

### From `inventory.csv`:
8. `stock_units`
9. `reorder_threshold`

### From `feedback.csv`:
10. `rating`
11. `theme`

### Key and Filter Columns (Non-Metric Fields):
The fields `store`, `store_id`, `date`, `product`, and `product_id` are designated strictly as primary keys, joining keys, categorical filters (`WHERE`), and grouping keys (`GROUP BY`). They may appear in response text as categorical row labels (e.g., store names), but are never measured metrics and do not count toward the 11 reportable metric fields.

---

## 3. Prohibited Actions

The assistant is strictly barred from the following actions:
1. **Autonomous Reordering / Supply Chain Actions:** Placing orders, initiating purchase orders, modifying reorder thresholds, or contacting vendors (e.g., executing "Reorder 200 units of Amul Milk").
2. **External Messaging and Alerting:** Dispatching emails, SMS, WhatsApp messages, or team notifications to store managers or external personnel.
3. **Imputing / Extrapolating Missing Data:** Inventing, interpolating, or guessing missing operational numbers or out-of-range dates.
4. **Asserting Correlation as Causation:** Declaring that statistical correlations establish direct operational cause-and-effect (e.g., claiming stockouts directly caused revenue shortfalls).
5. **Reporting Unapproved Financial Metrics:** Calculating or reporting unapproved metrics such as profit margin, EBITDA, overhead expenses, or marketing ROI.

---

## 4. Query Scope Boundaries

### Questions the Assistant Should Answer
1. **Single-Store Metric Lookup:**
   - *Example:* "What was Pune's revenue on 15 May 2026?"
   - *Behavior:* Returns the exact revenue (INR 623845.00) with complete data source lineage.
2. **Target vs Actual Performance Check:**
   - *Example:* "Did Pune hit its target on 2026-05-20?"
   - *Behavior:* Evaluates revenue against daily target, reporting achievement percentage and band.
3. **Cross-Store Metric Comparison:**
   - *Example:* "Which store had the highest average revenue between 2026-05-01 and 2026-05-31?"
   - *Behavior:* Calculates SQL-aggregated averages for all 5 stores and ranks them accordingly.
4. **Stockout & Inventory Deficit Monitoring:**
   - *Example:* "Which stores are below the reorder threshold for Amul Milk?"
   - *Behavior:* Filters inventory records where `stock_units < reorder_threshold`.
5. **Customer Feedback Aggregation:**
   - *Example:* "What are customers saying about Hyderabad?"
   - *Behavior:* Returns mean rating across rated reviews, response volume, and dominant feedback theme.

### Questions the Assistant Should Refuse / Escalate
1. **Unapproved Metrics:**
   - *Example:* "What was Pune's profit margin on 2026-05-15?"
   - *Behavior:* Refuses with Safe Failure explaining that profit margin is not an approved metric.
2. **Out of Scope / General Knowledge:**
   - *Example:* "What is the capital of India?"
   - *Behavior:* Escalates to human operator as an out-of-scope query.
3. **Prohibited Operational Imperatives:**
   - *Example:* "Please reorder 100 units of Amul Milk for Pune."
   - *Behavior:* Categorized as out-of-scope and escalated; takes no operational action.
4. **Root-Cause Diagnostic Questions:**
   - *Example:* "Why is Pune's revenue so low?"
   - *Behavior:* Escalates to human analyst; refuses to fabricate causal narratives.
5. **Temporal Out-of-Range Requests:**
   - *Example:* "What was Mumbai's revenue on 2026-07-15?"
   - *Behavior:* Refuses with Safe Failure stating that data is only available between 2026-04-01 and 2026-06-29.