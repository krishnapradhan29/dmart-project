# Evaluation Summary Report

## 1. Test Execution Metrics
- **Total Test Cases Evaluated:** 35
- **Passed Cases:** 35 / 35 (100.00%)
- **Ungrounded Numbers:** 0 (Strict Zero-Hallucination Policy Maintained)
- **Mean Latency:** 6.41 ms
- **Mean Tokens per Turn:** 21.9

## 2. Four Dimension Scorecard

### Dimension 1: Cost
- **LLM API Calls:** 0 (100% deterministic local pipeline)
- **Compute Overhead:** Negligible; in-memory SQLite and Python data filtering.
- **Estimated Cost per 1,000 Turns:** $0.00 (Zero marginal API cost).

### Dimension 2: Latency
- **Mean Response Time:** 6.41 ms.
- **P95 Latency:** < 15.00 ms (including simulated database retry cases).
- **Target SLA:** < 500 ms (Met with >98% safety margin).

### Dimension 3: Quality
- **Category Pass Rates:**
  - Ambiguity Resolution: 3 / 3 (100%)
  - Metric Comparisons: 3 / 3 (100%)
  - Diagnostic Routing: 1 / 1 (100%)
  - Customer Feedback: 1 / 1 (100%)
  - Prompt Injection Defense: 1 / 1 (100%)
  - Inventory Stockout Checks: 1 / 1 (100%)
  - Standard Metric Lookups: 7 / 7 (100%)
  - Temporal Boundary Enforcements: 2 / 2 (100%)
  - Out of Scope Escalations: 2 / 2 (100%)
  - Retry & Resilience: 2 / 2 (100%)
  - Metric Synonyms: 1 / 1 (100%)
  - Target vs Actual Performance: 3 / 3 (100%)
  - Fuzzy Typo Resolution: 2 / 2 (100%)
  - Unresolved Entity Isolations: 2 / 2 (100%)
  - Unsupported Metric Defenses: 2 / 2 (100%)
  - Weather Tool Routing: 2 / 2 (100%)

### Dimension 4: Safety & Governance
- **Zero Hallucination:** Every reported numeric figure is traceably grounded in SQLite database fields.
- **Scope Boundary Preservation:** 100% escalation rate on prompt injection, operational ordering imperatives, and non-domain inquiries.
- **Session Context Integrity:** Unresolved entities never inherit previous turn values.