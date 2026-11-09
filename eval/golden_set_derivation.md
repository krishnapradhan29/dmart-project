# Golden Evaluation Set: Derivation and Traceability

This document records the exact mathematical derivations, SQL queries, and expected values for custom test cases (C01–C11) added to `eval/golden_set.csv`.

---

### Case C01: Typo Store Resolution (`Bengalore`)
- **Query:** `What was Bengalore's revenue on 2026-04-10?`
- **Derivation:** Fuzzy string matching between candidate `Bengalore` and store `Bengaluru` yields `SequenceMatcher.ratio() = 0.78` ($\ge 0.70$). It resolves to `Bengaluru`.
- **Database Query:**
  ```sql
  SELECT revenue_inr FROM store_daily_clean WHERE store = 'Bengaluru' AND date = '2026-04-10';