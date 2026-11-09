import os
import sys
import csv
import json

# Ensure repo root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.run_agent import handle, SESSIONS

def main():
    eval_log_path = "eval/eval_runs.jsonl"
    os.environ["AGENT_LOG_PATH"] = eval_log_path
    os.environ["WEATHER_MODE"] = "stub"

    # Reset eval log file
    os.makedirs("eval", exist_ok=True)
    with open(eval_log_path, "w", encoding="utf-8") as f:
        pass

    SESSIONS.clear()

    golden_cases = []
    with open("eval/golden_set.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            golden_cases.append(row)

    print(f"Loaded {len(golden_cases)} test cases from eval/golden_set.csv")

    results = []
    category_stats = {}

    for c in golden_cases:
        cid = c["case_id"]
        cat = c["category"]
        sess = c["session_id"]
        q = c["question"]
        sim_fail = int(c.get("simulate_failures", 0))
        exp_status = c["expected_status"]
        exp_intent = c["expected_intent"]
        exp_contains = c["expected_contains"]

        os.environ["SIMULATE_DB_FAILURES"] = str(sim_fail)
        res = handle(q, session_id=sess)

        # Check status match
        status_pass = (res["status"] == exp_status)

        # Check intent match
        intent_pass = (res["intent"] == exp_intent)

        # Check expected content
        expected_items = exp_contains.split("|") if exp_contains else []
        contains_pass = True
        for item in expected_items:
            if item.strip() and item.strip() not in res["answer_text"]:
                contains_pass = False
                break

        # Zero ungrounded check
        zero_ungrounded = (res["ungrounded_numbers"] == 0)

        case_passed = status_pass and intent_pass and contains_pass and zero_ungrounded

        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1
        if case_passed:
            category_stats[cat]["passed"] += 1

        results.append({
            "case_id": cid,
            "category": cat,
            "status": res["status"],
            "expected_status": exp_status,
            "intent": res["intent"],
            "expected_intent": exp_intent,
            "case_passed": case_passed,
            "ungrounded_numbers": res["ungrounded_numbers"],
            "latency_ms": res["latency_ms"],
            "tokens_est": res["tokens_est"],
            "answer_text": res["answer_text"]
        })

        tag = "PASS" if case_passed else "FAIL"
        print(f"[{cid}] {tag} | Status: {res['status']} | Intent: {res['intent']} | Ungrounded: {res['ungrounded_numbers']}")

    total_cases = len(results)
    total_passed = sum(1 for r in results) if total_cases > 0 else 0
    passed_count = sum(1 for r in results if r["case_passed"])
    overall_accuracy = (passed_count / total_cases) * 100 if total_cases > 0 else 0

    total_ungrounded = sum(r["ungrounded_numbers"] for r in results)
    avg_latency = sum(r["latency_ms"] for r in results) / total_cases if total_cases > 0 else 0
    avg_tokens = sum(r["tokens_est"] for r in results) / total_cases if total_cases > 0 else 0

    print("\n--- Summary ---")
    print(f"Total Cases: {total_cases}")
    print(f"Passed: {passed_count}/{total_cases} ({overall_accuracy:.2f}%)")
    print(f"Total Ungrounded Numbers: {total_ungrounded}")
    print(f"Avg Latency: {avg_latency:.2f} ms")
    print(f"Avg Tokens: {avg_tokens:.1f}")

    print("\n--- Category Breakdown ---")
    for cat, s in sorted(category_stats.items()):
        acc = (s["passed"] / s["total"]) * 100
        print(f"{cat:20s}: {s['passed']}/{s['total']} ({acc:.1f}%)")

if __name__ == "__main__":
    main()