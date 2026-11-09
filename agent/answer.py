import re

def compute_ungrounded_numbers(text, grounded_values):
    # Remove dates like YYYY-MM-DD
    cleaned = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", text)
    # Remove product names with sizes like "Amul Milk 1L", "70g", "1kg", "200g", "5kg"
    cleaned = re.sub(r"\b\d+(?:L|kg|g)\b", " ", cleaned)

    # Extract all remaining numbers (integers or floats)
    found_nums = re.findall(r"\b\d+(?:\.\d+)?\b", cleaned)
    
    # Strip any trailing decimal zeros for loose matching if needed, or exact string match
    grounded_set = set(grounded_values)
    
    ungrounded = 0
    for n in found_nums:
        # Check direct match or formatted float match
        matched = False
        if n in grounded_set:
            matched = True
        else:
            try:
                fn = float(n)
                for g in grounded_set:
                    try:
                        if abs(float(g) - fn) < 1e-5:
                            matched = True
                            break
                    except ValueError:
                        pass
            except ValueError:
                pass
        if not matched:
            ungrounded += 1

    return ungrounded

def build_answer(understood, fetch_result, attempts, err_reason=None):
    intent = understood["intent"]
    store = understood["store"]
    date_val = understood["date"]
    metric = understood["metric"]
    product = understood["product"]
    weather_info = understood.get("weather_info")

    status = "Answered"
    answer_text = ""
    evidence = []
    grounded_values = []

    # 1. Intent level status precedence
    if intent == "unsupported_metric":
        return {
            "status": "Safe Failure",
            "answer_text": "The requested field is not an approved metric. Please ask for approved metrics such as revenue, footfall, target, stockout hours, or discount percentage.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    if intent == "out_of_scope":
        return {
            "status": "Escalated",
            "answer_text": "This request is outside the operational scope of DMart analytics or requests an unsupported action. Escalating to human management.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    if intent == "diagnostic":
        return {
            "status": "Escalated",
            "answer_text": "Diagnostic and root-cause inquiries require qualitative review. An analyst is needed to review store performance.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    # 2. Entity / confidence checks -> Clarification Needed
    if understood["confidence"] < 0.7:
        if understood.get("unres_store"):
            return {
                "status": "Clarification Needed",
                "answer_text": "Which store are you referring to? Please specify one of the five regional stores: Mumbai, Pune, Hyderabad, Bengaluru, or Ahmedabad.",
                "evidence": [],
                "grounded_values": [],
                "ungrounded_numbers": 0
            }
        if understood.get("unres_date"):
            return {
                "status": "Clarification Needed",
                "answer_text": "Could you clarify the date? Supported formats are YYYY-MM-DD, D Month YYYY, yesterday, or between <date> and <date>.",
                "evidence": [],
                "grounded_values": [],
                "ungrounded_numbers": 0
            }
        if understood.get("is_ambiguous"):
            return {
                "status": "Clarification Needed",
                "answer_text": "Your request mentions multiple entities. Which store or metric would you like to evaluate?",
                "evidence": [],
                "grounded_values": [],
                "ungrounded_numbers": 0
            }
        if understood.get("missing_entities"):
            missing_str = " and ".join(understood["missing_entities"])
            return {
                "status": "Clarification Needed",
                "answer_text": f"Could you please specify the {missing_str}?",
                "evidence": [],
                "grounded_values": [],
                "ungrounded_numbers": 0
            }

    # 3. Date boundary check
    if err_reason == "out_of_range_date":
        return {
            "status": "Safe Failure",
            "answer_text": "The requested date is out of range. Data is only available between 2026-04-01 and 2026-06-29.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    # 4. Failed queries retry / no record found
    if attempts >= 3 and fetch_result is None:
        return {
            "status": "Escalated",
            "answer_text": "Data service unavailable after three attempts. Query escalated to technical support.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    if fetch_result is None and intent not in ["weather"]:
        return {
            "status": "Safe Failure",
            "answer_text": "No record found for the requested store, date, or product in the verified dataset.",
            "evidence": [],
            "grounded_values": [],
            "ungrounded_numbers": 0
        }

    # Format answers per intent
    if intent == "lookup":
        val = fetch_result
        if metric in ["revenue_inr", "daily_target_inr"]:
            val_str = f"{float(val):.2f}"
            answer_text = f"{store}'s {metric.replace('_', ' ')} on {date_val} was INR {val_str}."
            grounded_values.append(val_str)
        elif metric == "footfall":
            val_str = f"{float(val):.2f}"
            answer_text = f"{store}'s footfall on {date_val} was {val_str}."
            grounded_values.append(val_str)
        elif metric == "stockout_hours":
            val_str = f"{float(val):.2f}"
            answer_text = f"{store}'s stockout hours on {date_val} was {val_str}."
            grounded_values.append(val_str)
        elif metric == "discount_pct":
            val_str = f"{float(val):.2f}"
            answer_text = f"{store}'s discount on {date_val} was {val_str}%."
            grounded_values.append(val_str)
        else:
            val_str = f"{float(val):.2f}"
            answer_text = f"{store}'s metric on {date_val} was {val_str}."
            grounded_values.append(val_str)

        evidence.append({
            "source": "store_daily_clean",
            "fields": [metric],
            "store": store,
            "date": date_val
        })

        if weather_info and weather_info.get("ok"):
            w_temp = f"{weather_info['temperature_c']:.1f}"
            w_hum = f"{weather_info['humidity_pct']:.1f}"
            w_wind = f"{weather_info['wind_kmh']:.1f}"
            w_rain = f"{weather_info['rain_mm']:.1f}"
            answer_text += f" Weather in {store} on {date_val}: temperature {w_temp}°C, humidity {w_hum}%, wind {w_wind} km/h, rain {w_rain} mm."
            grounded_values.extend([w_temp, w_hum, w_wind, w_rain])
            evidence.append({
                "source": "weather_tool",
                "fields": ["temperature_c", "humidity_pct", "wind_kmh", "rain_mm"],
                "store": store,
                "date": date_val
            })

    elif intent == "target_vs_actual":
        rev = fetch_result["revenue_inr"]
        tgt = fetch_result["daily_target_inr"]
        ach = fetch_result["achievement_pct"]
        band = fetch_result["performance_band"]

        rev_str = f"{float(rev):.2f}"
        tgt_str = f"{float(tgt):.2f}"
        ach_str = f"{float(ach):.2f}"

        grounded_values.extend([rev_str, tgt_str, ach_str])

        if band == "Poor":
            status = "Drafted"
            hit_str = f"did not hit its target (achievement {ach_str}%, band {band})"
        else:
            status = "Answered"
            hit_str = f"hit its target with achievement {ach_str}% (band {band})"

        answer_text = f"{store} on {date_val} {hit_str}, posting revenue of INR {rev_str} against target INR {tgt_str}."
        evidence.append({
            "source": "store_daily_clean",
            "fields": ["revenue_inr", "daily_target_inr", "achievement_pct", "performance_band"],
            "store": store,
            "date": date_val
        })

    elif intent == "comparison":
        rows = fetch_result
        items_str = []
        for s, avg in rows:
            avg_str = f"{avg:.2f}"
            items_str.append(f"{s} INR {avg_str}")
            grounded_values.append(avg_str)

        lead_store = rows[0][0]
        lead_val = f"{rows[0][1]:.2f}"
        answer_text = "; ".join(items_str) + f"; highest {lead_store}" if "highest" in understood.get("direction", "highest") else "; ".join(items_str)
        evidence.append({
            "source": "store_daily_clean",
            "fields": [metric],
            "store": "all",
            "date": date_val
        })

    elif intent == "inventory":
        rows = fetch_result
        if not rows:
            answer_text = f"No store is below its reorder threshold for {product}."
        else:
            parts = []
            for s, stock, thresh in rows:
                stock_str = str(int(stock))
                thresh_str = str(int(thresh))
                parts.append(f"{s} {stock_str} units")
                grounded_values.append(stock_str)
            thresh_quoted = str(int(rows[0][2]))
            grounded_values.append(thresh_quoted)
            answer_text = f"Stores short of stock for {product}: " + " and ".join(parts) + f" against threshold {thresh_quoted}."

        evidence.append({
            "source": "inventory",
            "fields": ["stock_units", "reorder_threshold"],
            "store": "all",
            "date": None
        })

    elif intent == "feedback":
        fb = fetch_result
        avg_str = f"{fb['avg_rating']:.2f}"
        rated_str = str(int(fb['rated_count']))
        tot_str = str(int(fb['total_count']))
        theme_str = fb['top_theme']

        grounded_values.extend([avg_str, rated_str, tot_str])
        answer_text = f"Customer feedback for {store}: average rating {avg_str}, {rated_str} rated of {tot_str}, most frequent theme {theme_str}."
        evidence.append({
            "source": "feedback",
            "fields": ["rating", "theme"],
            "store": store,
            "date": None
        })

    elif intent == "weather":
        if weather_info and weather_info.get("ok"):
            w_temp = f"{weather_info['temperature_c']:.1f}"
            w_hum = f"{weather_info['humidity_pct']:.1f}"
            w_wind = f"{weather_info['wind_kmh']:.1f}"
            w_rain = f"{weather_info['rain_mm']:.1f}"
            grounded_values.extend([w_temp, w_hum, w_wind, w_rain])
            answer_text = f"Weather in {store} on {date_val}: temperature {w_temp}°C, humidity {w_hum}%, wind {w_wind} km/h, rain {w_rain} mm."
            evidence.append({
                "source": "weather_tool",
                "fields": ["temperature_c", "humidity_pct", "wind_kmh", "rain_mm"],
                "store": store,
                "date": date_val
            })
        else:
            status = "Safe Failure"
            answer_text = "Weather data unavailable for the requested city or date."

    ungrounded = compute_ungrounded_numbers(answer_text, grounded_values)

    return {
        "status": status,
        "answer_text": answer_text,
        "evidence": evidence,
        "grounded_values": grounded_values,
        "ungrounded_numbers": ungrounded
    }