import os
import sys

# Ensure repository root is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.run_agent import handle, SESSIONS

ACCEPTANCE_CASES = [
    {"id": "A01", "session": "s1", "q": "What was Pune's revenue on 15 May 2026?", "sim_fail": 0},
    {"id": "A02", "session": "s1", "q": "And the target?", "sim_fail": 0},
    {"id": "A03", "session": "s1", "q": "How about Mumbai?", "sim_fail": 0},
    {"id": "A04", "session": "s2", "q": "How is Hyderabad doing?", "sim_fail": 0},
    {"id": "A05", "session": "s2", "q": "revenue on 2026-05-15", "sim_fail": 0},
    {"id": "A06", "session": "s3", "q": "What was Hydrabad's turnover yesterday?", "sim_fail": 0},
    {"id": "A07", "session": "s4", "q": "Did Pune hit its target on 2026-05-16?", "sim_fail": 0},
    {"id": "A08", "session": "s4", "q": "Did Pune hit its target on 2026-05-20?", "sim_fail": 0},
    {"id": "A09", "session": "s4", "q": "Did Mumbai hit its target on 2026-05-21?", "sim_fail": 0},
    {"id": "A10", "session": "s5", "q": "Which store had the highest average revenue between 2026-05-01 and 2026-05-31?", "sim_fail": 0},
    {"id": "A11", "session": "s5", "q": "Which store had the lowest revenue on 2026-06-10?", "sim_fail": 0},
    {"id": "A12", "session": "s6", "q": "Which stores are below the reorder threshold for Amul Milk?", "sim_fail": 0},
    {"id": "A13", "session": "s6", "q": "What are customers saying about Hyderabad?", "sim_fail": 0},
    {"id": "A14", "session": "s7", "q": "What was Pune's profit margin on 2026-05-15?", "sim_fail": 0},
    {"id": "A15", "session": "s8", "q": "What is the capital of India?", "sim_fail": 0},
    {"id": "A16", "session": "s9", "q": "What was Mumbai's revenue on 2026-07-15?", "sim_fail": 0},
    {"id": "A17", "session": "s10", "q": "Why is Pune's revenue so low?", "sim_fail": 0},
    {"id": "A18", "session": "s11", "q": "What was Kolkata's revenue on 2026-05-15?", "sim_fail": 0},
    {"id": "A19", "session": "s12", "q": "What was Pune's revenue on 15 May 2026?", "sim_fail": 2},
    {"id": "A20", "session": "s13", "q": "What was Pune's revenue on 15 May 2026?", "sim_fail": 3},
]

def main():
    log_file = "logs/runs.jsonl"
    os.environ["AGENT_LOG_PATH"] = log_file
    os.environ["WEATHER_MODE"] = "stub"

    # Reset log file
    os.makedirs("logs", exist_ok=True)
    with open(log_file, "w", encoding="utf-8") as f:
        pass

    SESSIONS.clear()

    transcript_rows = []
    print("Running 20 Acceptance Test Cases...")

    for case in ACCEPTANCE_CASES:
        os.environ["SIMULATE_DB_FAILURES"] = str(case["sim_fail"])
        res = handle(case["q"], session_id=case["session"])

        transcript_rows.append({
            "id": case["id"],
            "session": case["session"],
            "question": case["q"],
            "status": res["status"],
            "intent": res["intent"],
            "confidence": f"{res['confidence']:.2f}",
            "route": res["route"],
            "attempts": res["attempts"],
            "answer_text": res["answer_text"]
        })
        print(f"[{case['id']}] {res['status']} | Intent: {res['intent']} | Answer: {res['answer_text'][:50]}...")

    # Write outputs/acceptance_transcript.md
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/acceptance_transcript.md", "w", encoding="utf-8") as f:
        f.write("# Acceptance Test Run Transcript (Cases A01 - A20)\n\n")
        f.write("| ID | Session | Question | Status | Intent | Conf | Route | Attempts | Answer Text |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for r in transcript_rows:
            f.write(f"| {r['id']} | {r['session']} | {r['question']} | {r['status']} | {r['intent']} | {r['confidence']} | {r['route']} | {r['attempts']} | {r['answer_text']} |\n")

    print("\nAcceptance run complete! Logged exactly 20 lines to logs/runs.jsonl and created outputs/acceptance_transcript.md")

if __name__ == "__main__":
    main()