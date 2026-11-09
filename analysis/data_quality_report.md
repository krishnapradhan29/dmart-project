# Data Quality Report: Store Daily Practice Dataset

## 1. Dataset Shape & Structure
- **Rows:** 453 (including duplicate and injected error records)
- **Columns:** 9
- **Column Types:**
  - `date`: string / object (ISO 8601 date format YYYY-MM-DD)
  - `store_id`: string / object (e.g., S01, S02)
  - `store`: string / object (Mumbai, Pune, Hyderabad, Bengaluru, Ahmedabad)
  - `footfall`: float64 / object (raw data contains missing strings and negative values)
  - `revenue_inr`: float64
  - `daily_target_inr`: int64
  - `marketing_spend_inr`: int64
  - `stockout_hours`: float64
  - `discount_pct`: float64

## 2. Integrity Issues & Missing Values
- **Exact Duplicate Rows:** 3 rows
  - `S01` (Mumbai) on offset day 40 (2026-05-11)
  - `S03` (Hyderabad) on offset day 60 (2026-05-31)
  - `S05` (Ahmedabad) on offset day 15 (2026-04-16)
- **Null / Missing Counts per Column:**
  - `footfall`: 4 missing values (Pune day 11, Pune day 46, Mumbai day 29, Bengaluru day 70)
  - All other 8 columns: 0 nulls
- **Value Extremes:**
  - `footfall` Minimum: -150 (Hyderabad, day 20 / 2026-04-21; impossible negative value)
  - `footfall` Maximum: 9800 (Ahmedabad, day 55 / 2026-05-26; extreme high value)

## 3. Per-Store Footfall Distribution & Outlier Bounds
*Computed after deduplicating exact matches (450 rows) and setting negative footfall (-150) to missing (using linear interpolation for percentiles).*

| Store | Non-missing Count | Q1 (25th %) | Q3 (75th %) | IQR | Lower Bound (Q1 - 1.5×IQR) | Upper Bound (Q3 + 1.5×IQR) | Outlier Values Found |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ahmedabad** | 90 | 1862.00 | 2029.75 | 167.75 | 1582.38 | 2281.38 | 9800 (2026-05-26) |
| **Bengaluru** | 89 | 1978.00 | 2226.60 | 248.60 | 1563.50 | 2599.50 | None |
| **Hyderabad** | 89 | 2083.30 | 2568.10 | 484.80 | 1598.50 | 2810.50 | None |
| **Mumbai** | 89 | 2275.60 | 2559.80 | 284.20 | 1802.00 | 2986.00 | 6100 (2026-04-09) |
| **Pune** | 88 | 1450.00 | 1603.10 | 153.10 | 1194.75 | 1832.75 | None |

*Total rows falling outside bounds:* Exactly 2 rows (Mumbai 6100 and Ahmedabad 9800).

## 4. Decisions
- **Duplicates:** Removed 3 appended duplicate rows keeping the first occurrence. Keeping duplicates would artificially bias volume metrics and violate the 1-row-per-store-per-day constraint.
- **Negative Values:** Hyderabad day 20 (`-150`) was converted to missing (`NaN`). Physical footfall cannot be negative; treating it as missing allows clean, unbiased distribution and median calculation.
- **Extreme Values:** The two outliers (Mumbai 6100 and Ahmedabad 9800) represent valid business operating days with exceptional traffic rather than logging corruption. Instead of deletion (which loses operational context and distorts the 90-day time series), values were capped at the upper IQR threshold (Mumbai 2986.00, Ahmedabad 2281.38) rounded half-up to 2 decimals.
- **Missing Values:** The 5 missing values (4 originally missing + 1 converted negative) were imputed using the respective store's median footfall (calculated after IQR capping). We avoid zero (which destroys averages) and all-store aggregates (which blur store scale differences).
- **Raw File Status:** The raw file `data/store_daily.csv` remains completely unmodified and preserved as generated.