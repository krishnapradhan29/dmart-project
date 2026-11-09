# DMart Conversational Analytics Agent

A deterministic, zero-hallucination Conversational Analytics Agent for DMart retail operations across Mumbai, Pune, and Bengaluru.

## Project Structure
- data/: Cleaned and raw operational datasets.
- analysis/: Analytical derivations, cleaning logs, and executive findings.
- docs/: Specification documents and release gate.
- agent/: Modular deterministic agent implementation.
- logs/: Execution traces for all acceptance turns.
- outputs/: Full transcript of acceptance test suite.
- tools/: External weather tool integration.
- eval/: Golden set evaluation framework and summary.

## Evaluation Results
- Acceptance Tests (A01-A20): 20/20 Passed (100%)
- Expanded Golden Set (35 cases): 35/35 Passed (100%)
- Ungrounded Numbers: 0 (Strict zero-hallucination verified)
- Mean Latency: ~6.4 ms
