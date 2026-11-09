import os
import json
import time
import uuid
from datetime import datetime

from agent.understand import understand
from agent.fetch import (
    fetch_single_lookup, fetch_target_vs_actual, fetch_range_lookup_sql,
    fetch_comparison_sql, fetch_inventory_sql, fetch_feedback_sql,
    check_date_range
)
from agent.answer import build_answer
from tools.weather import get_weather

# In-memory session store
SESSIONS = {}

def handle(question, session_id, user_id="u1"):
    start_time = time.perf_counter()
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    ts = datetime.utcnow().isoformat() + "Z"

    session_ctx = SESSIONS.get(session_id, {})
    understood = understand(question, session_ctx)

    intent = understood["intent"]
    store = understood["store"]
    metric = understood["metric"]
    date_val = understood["date"]
    product = understood["product"]
    has_weather = understood["has_weather"]
    confidence = understood["confidence"]

    # Direction for comparison
    q_lower = question.lower()
    direction = "lowest" if "lowest" in q_lower or ("worst" in q_lower and metric != "stockout_hours") or ("best" in q_lower and metric == "stockout_hours") else "highest"
    understood["direction"] = direction

    route = "none"
    executed = None
    tool_calls = 0
    tools_called = []
    fetch_result = None
    attempts = 0
    err_reason = None

    # Check temporal boundary for date-using intents
    if intent in ["lookup", "target_vs_actual", "comparison", "weather"]:
        if date_val and not check_date_range(date_val):
            err_reason = "out_of_range_date"

    # Execution routing
    if confidence >= 0.7 and not err_reason:
        if intent == "lookup":
            if date_val and " to " in date_val:
                route = "sql"
                d1, d2 = date_val.split(" to ")
                res, attempts, err = fetch_range_lookup_sql(store, metric, d1, d2)
                if res is not None:
                    fetch_result, executed = res
                tool_calls += 1
            else:
                route = "python"
                fetch_result, attempts, err = fetch_single_lookup(store, metric, date_val)
                executed = f"fetch_single_lookup('{store}', '{metric}', '{date_val}')"
                tool_calls += 1

                if has_weather and store and date_val:
                    route = "python+weather"
                    w_res = get_weather(store, date_val)
                    understood["weather_info"] = w_res
                    tools_called.append("weather_tool")
                    tool_calls += 1

        elif intent == "target_vs_actual":
            route = "python"
            fetch_result, attempts, err = fetch_target_vs_actual(store, date_val)
            executed = f"fetch_target_vs_actual('{store}', '{date_val}')"
            tool_calls += 1

            if has_weather and store and date_val:
                route = "python+weather"
                w_res = get_weather(store, date_val)
                understood["weather_info"] = w_res
                tools_called.append("weather_tool")
                tool_calls += 1

        elif intent == "comparison":
            route = "sql"
            res, attempts, err = fetch_comparison_sql(metric, date_val, direction)
            if res is not None:
                fetch_result, executed = res
            tool_calls += 1

        elif intent == "inventory":
            route = "sql"
            res, attempts, err = fetch_inventory_sql(product)
            if res is not None:
                fetch_result, executed = res
            tool_calls += 1

        elif intent == "feedback":
            route = "sql"
            res, attempts, err = fetch_feedback_sql(store)
            if res is not None:
                fetch_result, executed = res
            tool_calls += 1

        elif intent == "weather":
            route = "weather"
            w_res = get_weather(store, date_val)
            understood["weather_info"] = w_res
            tools_called.append("weather_tool")
            tool_calls += 1
            attempts = 0

    # Build final response
    ans_pkg = build_answer(understood, fetch_result, attempts, err_reason)
    status = ans_pkg["status"]
    answer_text = ans_pkg["answer_text"]
    evidence = ans_pkg["evidence"]
    grounded_values = ans_pkg["grounded_values"]
    ungrounded_numbers = ans_pkg["ungrounded_numbers"]

    # Calculate tokens & budget
    tokens_est = len(question.split()) + len(answer_text.split())
    budget_exceeded = bool(tokens_est > 150)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Update session context
    if intent not in ["unsupported_metric", "diagnostic", "out_of_scope"]:
        if understood.get("store") and not understood.get("unres_store"):
            session_ctx["store"] = understood["store"]
        if understood.get("metric"):
            session_ctx["metric"] = understood["metric"]
        if understood.get("date") and not understood.get("unres_date"):
            session_ctx["date"] = understood["date"]
        if understood.get("product"):
            session_ctx["product"] = understood["product"]
        if intent == "target_vs_actual":
            session_ctx["last_intent"] = "target_vs_actual"
        else:
            session_ctx.pop("last_intent", None)
        SESSIONS[session_id] = session_ctx

    record = {
        "run_id": run_id,
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": ts,
        "question": question,
        "intent": intent,
        "confidence": confidence,
        "route": route,
        "executed": executed,
        "attempts": attempts,
        "tools_called": tools_called,
        "status": status,
        "answer_text": answer_text,
        "evidence": evidence,
        "grounded_values": grounded_values,
        "latency_ms": elapsed_ms,
        "tokens_est": tokens_est,
        "tool_calls": tool_calls,
        "ungrounded_numbers": ungrounded_numbers,
        "budget_exceeded": budget_exceeded
    }

    # Atomic append to log file
    log_path = os.environ.get("AGENT_LOG_PATH", "logs/runs.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    return record