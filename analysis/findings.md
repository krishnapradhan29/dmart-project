# Store Performance Analysis and Premise Test

## 1. Summary Metrics Table

| Store | Mean Daily Revenue (INR) | Mean Footfall | Mean Stockout Hours | Revenue per Footfall (INR) | Mean Achievement (%) | Days in Poor Band (<75%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ahmedabad** | 782647.37 | 1922.59 | 3.19 | 407.08 | 92.08 | 1 |
| **Bengaluru** | 931065.68 | 2076.86 | 2.38 | 448.31 | 98.01 | 0 |
| **Hyderabad** | 893233.01 | 2209.51 | 3.85 | 404.27 | 94.02 | 0 |
| **Mumbai** | 1064371.60 | 2391.27 | 1.93 | 445.11 | 101.37 | 0 |
| **Pune** | 636358.55 | 1517.71 | 2.32 | 419.29 | 70.71 | 70 |
| **All stores** | 861535.24 | 2023.59 | 2.74 | 425.75 | 91.24 | 71 |

## 2. Premise Test: Pune Stockout Hypothesis

Kavita Rao's working premise states: *"Pune is the lowest-revenue store because of stockouts."*

### Store Ranking by Mean Stockout Hours (Lowest to Highest)
1. Mumbai: 1.93 hours
2. Pune: 2.32 hours
3. Bengaluru: 2.38 hours
4. Ahmedabad: 3.19 hours
5. Hyderabad: 3.85 hours

**Verdict:** The data **does not support** Kavita's premise. Pune ranks 4th out of 5 stores in stockout hours (2.32 hrs/day), which is well below the all-store average of 2.74 hours and significantly lower than Hyderabad (3.85 hrs/day) and Ahmedabad (3.19 hrs/day). If stockouts were the primary driver of revenue deficits, Hyderabad and Ahmedabad would suffer worse financial drops. Instead, Pune's performance is crippled by an acute footfall deficit (1,517 daily visitors vs 2,024 regional average).

## 3. Correlation Analysis
- **All Cleaned Records (450 rows):**
  - Revenue vs Stockout Hours: `r = -0.152`
  - Revenue vs Footfall: `r = 0.918`
- **Pune Specific (90 rows):**
  - Revenue vs Stockout Hours: `r = -0.254`
  - Revenue vs Footfall: `r = 0.735`
- **Raw Deduplicated Footfall (446 non-missing rows):**
  - Revenue vs Footfall: `r = 0.548` (demonstrating how extreme uncleaned outliers masked the underlying linear relationship).

*Note: Correlation does not establish causation.*

## 4. Key Observations

### Facts
1. Pune recorded the lowest mean daily revenue across all stores at INR 636,358.55 (26.14% below the regional average of INR 861,535.24).
2. Pune's daily footfall averaged 1,517.71 visitors, which is 24.998% (~25.00%) lower than the regional mean of 2,023.59.
3. Pune's revenue per footfall is INR 419.29, only 1.52% below the regional mean of INR 425.75 and higher than both Ahmedabad (INR 407.08) and Hyderabad (INR 404.27).
4. Out of 71 regional store days landing in the Poor performance band (<75% target achievement), Pune accounts for 70 days.

### Insights
1. **Footfall, not basket conversion or stockout, is the bottleneck:** Because Pune converts footfall into revenue at INR 419.29 per customer (comparable to Ahmedabad's 407.08 and Hyderabad's 404.27), in-store operations and assortment conversion are functioning healthily; people who enter the store are buying. The shortfall is entirely due to top-of-funnel customer traffic.
2. **Capital Misallocation Risk:** Funding a stock-availability enhancement initiative for Pune targets a problem that ranks among the mildest in the network (2.32 hrs vs 3.85 hrs in Hyderabad), delivering negligible return on investment.

### Hypotheses
1. *Hypothesis 1 (Unconfirmed):* Pune's physical store location, parking accessibility, or local catchment density restricts walk-ins compared to other tier-1 metro branches.
   - *Extra data needed:* Micro-market catchment demographics, competitor store proximity within 5 km, and customer transit mode logs.
2. *Hypothesis 2 (Unconfirmed):* Pune's marketing spend (INR 41,000 base vs Mumbai's INR 52,000) or promotional channel mix is under-penetrating the local customer base.
   - *Extra data needed:* Campaign-level reach, localized leaflet/app impression data, and localized footfall lift per promotional event.