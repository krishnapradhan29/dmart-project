# Agent Architecture & Pipeline Specification

## 1. Eight-Step Processing Pipeline

Every user question is processed sequentially through an 8-step pipeline. The `Validate` step executes strictly before data querying to enforce governance and prevent unapproved field queries or SQL injection.

| Step # | Pipeline Step | Nature | Implementation Technique | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Interpret** | Deterministic | Closed grammar parser, regex, and difflib fuzzy candidate matching | Extracts entities (store, metric, date/range, product, weather flag), computes entity confidence, and maps session context. |
| 2 | **Route** | Deterministic | Sequential intent classification order (Rules 1–11) | Routes request to Python data function, SQL generator, external weather tool, or terminal refusal handlers. |
| 3 | **Validate** | Deterministic | Whitelist schema validator | Checks requested fields against the 11 approved reportable metrics and validates date boundaries (`2026-04-01` to `2026-06-29`). |
| 4 | **Query** | Deterministic | Parameterized SQL (`?` placeholders) and Python data filtering | Fetches raw records with maximum 3 execution attempts (initial try + 2 retries). |
| 5 | **Calculate** | Deterministic | Decimal integer-cent arithmetic with `ROUND_HALF_UP` | Calculates averages, percentage ratios, feedback metrics, and ranks without floating-point inaccuracies. |
| 6 | **Synthesize** | Deterministic (Generative step handled via template engine) | Fixed deterministic response string templates | Populates verified numeric values into standardized human-readable sentences without LLM hallucinations. |
| 7 | **Ground** | Deterministic | Array tracking of fetched/computed data values | Builds `grounded_values` list directly from query outputs and calculates `ungrounded_numbers` to guarantee zero hallucinated digits. |
| 8 | **Record** | Deterministic | Atomic JSONL audit logging (`logs/runs.jsonl` or `eval/eval_runs.jsonl`) | Commits a structured log line capturing run metadata, latency, tokens, attempts, and verification state. |

---

## 2. Intent Classification Table

The agent supports 9 canonical intents resolved in fixed sequential precedence:

| Intent | Example User Query | Target Execution Route | Expected Action |
| :--- | :--- | :--- | :--- |
| `out_of_scope` | "What is the capital of India?" / "Reorder 200 units of Amul Milk" | None (`route: none`) | Immediately escalates; refuses external imperatives or non-domain questions. |
| `unsupported_metric` | "What was Pune's profit margin on 2026-05-15?" | None (`route: none`) | Returns Safe Failure explaining the metric is not approved. |
| `diagnostic` | "Why is Pune's revenue so low?" | None (`route: none`) | Escalates to human analyst; refuses to fabricate causal explanations. |
| `inventory` | "Which stores are below the reorder threshold for Amul Milk?" | SQLite parameterized query | Evaluates `stock_units < reorder_threshold` on inventory table. |
| `feedback` | "What are customers saying about Hyderabad?" | SQLite parameterized query | Computes average rating on rated rows, rated row count, and top theme. |
| `target_vs_actual` | "Did Pune hit its target on 2026-05-16?" | Python data handler | Compares revenue against target; computes `achievement_pct` and `performance_band`. |
| `comparison` | "Which store had the highest average revenue between 2026-05-01 and 2026-05-31?" | SQLite aggregate query | Averages metric per store over range, sorts highest/lowest, and breaks ties by store name. |
| `lookup` | "What was Pune's revenue on 15 May 2026?" | Python handler (single date) or SQLite (date range) | Fetches single metric value or computes range average. |
| `weather` | "What was the weather in Pune on 2026-05-16?" | Weather tool (`tools/weather.py`) | Returns temperature, humidity, wind, and precipitation. |

---

## 3. Entity & Query Handling Rules

### Store Resolution
- Exact case-insensitive matching (`MUMBAI` -> `Mumbai`) yields confidence `1.0`.
- `Bangalore` is an explicit alias for `Bengaluru` (confidence `1.0`).
- Fuzzy matching (using `difflib.SequenceMatcher`) is strictly applied to **candidate words**: words $\ge 5$ letters that are capitalized, carry possessive `'s`, are not the first word of the query (unless carrying `'s`), and are not keywords or stop words.
- Brief proper nouns (`DMart`, `Avenue`, `Kavita`, etc.) are never candidates.
- A candidate word with best similarity $\ge 0.7$ resolves to that store with confidence equal to the similarity score (`Bengalore` $\to 0.78$, `Bangalor` $\to 0.71$, `Punee` $\to 0.89$, `Hydrabad's` $\to 0.94$, `Mumbay` $\to 0.83$).
- A candidate word with similarity $< 0.7$ becomes an **unresolved named store** (confidence `0.4`, yields `Clarification Needed`, and is **never** replaced by context).

### Metric Synonyms (Closed List)
- `revenue`, `sales`, `turnover`, `earnings` $\to$ `revenue_inr`
- `target` $\to$ `daily_target_inr`
- `footfall`, `visitors` $\to$ `footfall`
- `stockout` $\to$ `stockout_hours`
- `discount` $\to$ `discount_pct`

### Date Grammar (Closed Grammar)
- Supported formats:
  - ISO: `YYYY-MM-DD` (`^\d{4}-\d{2}-\d{2}$`)
  - Full text date: `D Month YYYY` (e.g., `15 May 2026`)
  - Relative: `yesterday` (resolved via constant `AS_OF_DATE = 2026-06-30` $\to$ `2026-06-29`)
  - Inclusive Range: `between <date> and <date>`
- Any other date form (`20260515`, `15 Jun 2026`, `last week`, `month to date`) is an **unresolved named date** (confidence `0.4`, yields `Clarification Needed`, never replaced by context).

### Ambiguity Rule
- If the question contains two different stores (e.g., "Pune and Mumbai revenue") or two different metrics, the agent assigns confidence `0.4` and sets status to `Clarification Needed`.

### Confidence Score Calculation
- Confidence is the minimum confidence across all entities required by the intent:
  - Exact match / synonym / closed grammar date = `1.0`
  - Fuzzy store match = similarity score ($0.70$ to $0.99$)
  - Missing required entity / unresolved named entity / ambiguity = `0.4`
- A query with overall confidence $< 0.7$ halts execution and yields `Clarification Needed`.

---

## 4. Status Decision Precedence & Conditions

The assistant outputs one of five mutually exclusive completion statuses based on the following strict decision order:

1. **Intent-Level Triggers:**
   - `unsupported_metric` $\to$ **`Safe Failure`**
   - `out_of_scope` or `diagnostic` $\to$ **`Escalated`**
2. **Entity & Confidence Triggers:**
   - Confidence $< 0.7$, missing required entities, unresolved named store/date, or ambiguity $\to$ **`Clarification Needed`**
3. **Temporal Boundary Triggers:**
   - Date or range outside `2026-04-01` to `2026-06-29` (for date-using intents) $\to$ **`Safe Failure`**
4. **Data Execution Triggers:**
   - 3 consecutive failed query attempts $\to$ **`Escalated`**
   - Zero matching rows found for valid entity $\to$ **`Safe Failure`**
5. **Business Alerting / Normal Completion:**
   - For `target_vs_actual`, if `performance_band == 'Poor'` (`achievement_pct < 75.00%`) $\to$ **`Drafted`** (held for human review)
   - Otherwise $\to$ **`Answered`**

---

## 5. Escalation & Retry Policies

- **Maximum Attempts:** Exactly 3 attempts (initial attempt + 2 automatic retries).
- **Simulated Failures:** Controllable via `SIMULATE_DB_FAILURES=<n>`. If $n < 3$, query succeeds on attempt $n+1$. If $n \ge 3$, retries are exhausted and status transitions to `Escalated`.
- **Escalation Notification:** Escalated responses clearly state the failure reason and indicate that the inquiry has been transferred to operations leadership.

---

## 6. Grounding & Verification Criteria

- **`grounded_values`:** An array of every numeric figure incorporated into the response, populated directly from data structures.
- **`ungrounded_numbers`:** Count of digit runs appearing in the response text that cannot be verified in `grounded_values`. **Must be exactly 0 across all runs.**
- Numbers in explanatory error/clarification messages must be spelled out (e.g., "three attempts") to preserve zero ungrounded counts.