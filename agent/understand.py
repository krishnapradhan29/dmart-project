import re
import difflib
from datetime import datetime, timedelta

AS_OF_DATE = "2026-06-30"  # yesterday is 2026-06-29

STORES = ["Mumbai", "Pune", "Hyderabad", "Bengaluru", "Ahmedabad"]

PRODUCTS_LIST = [
    ("P01", "Amul Milk 1L", "Amul Milk"),
    ("P02", "Toor Dal 1kg", "Toor Dal"),
    ("P03", "Basmati Rice 5kg", "Basmati Rice"),
    ("P04", "Sunflower Oil 1L", "Sunflower Oil"),
    ("P05", "Iodised Salt 1kg", "Iodised Salt"),
    ("P06", "Instant Noodles 70g", "Instant Noodles"),
    ("P07", "Glucose Biscuits 200g", "Glucose Biscuits"),
    ("P08", "Detergent Powder 1kg", "Detergent Powder"),
]

STOP_WORDS = {
    "hello", "thanks", "thank", "kindly", "please", "display", "compare",
    "which", "what", "whats", "how", "why", "did", "and", "show", "check",
    "report", "where", "would", "could", "can", "will", "give", "tell", "list",
    "the", "is", "of", "capital", "doing"
}

PROPER_NOUNS_DISALLOWED = {
    "dmart", "avenue", "supermarts", "kavita", "rao", "meteo", "github",
    "python", "sqlite", "postgresql", "markdown", "india"
}

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def parse_date(date_str):
    try:
        clean_d = date_str.rstrip("?,.;!")
        return datetime.strptime(clean_d, "%Y-%m-%d").date()
    except Exception:
        return None

def extract_dates_and_flags(q):
    q_lower = q.lower()
    
    # 1. Check yesterday
    if re.search(r"\byesterday\b", q_lower):
        as_of = datetime.strptime(AS_OF_DATE, "%Y-%m-%d").date()
        yest = (as_of - timedelta(days=1)).isoformat()
        iso_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", q)
        if iso_matches:
            return None, True
        return yest, False

    # 2. Check "between <date> and <date>"
    between_match = re.search(r"\bbetween\s+(\S+)\s+and\s+(\S+)", q, re.IGNORECASE)
    if between_match:
        d1_raw = between_match.group(1).rstrip("?,.;!")
        d2_raw = between_match.group(2).rstrip("?,.;!")
        d1 = parse_date(d1_raw)
        d2 = parse_date(d2_raw)
        if d1 and d2:
            if d1 <= d2:
                return f"{d1_raw} to {d2_raw}", False
            else:
                return None, True
        else:
            return None, True

    # Check "from ... to ..." -> invalid grammar
    if re.search(r"\bfrom\s+\S+\s+to\s+\S+", q_lower):
        return None, True

    # 3. Check "D Month YYYY"
    d_month_match = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\b", q)
    if d_month_match:
        day_val = int(d_month_match.group(1))
        m_name = d_month_match.group(2).lower()
        yr_val = int(d_month_match.group(3))
        if m_name in MONTH_MAP:
            m_num = MONTH_MAP[m_name]
            try:
                dt = datetime(yr_val, m_num, day_val).date()
                return dt.isoformat(), False
            except ValueError:
                return None, True
        else:
            return None, True

    # 4. Check single ISO date
    iso_matches = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", q)
    if len(iso_matches) == 1:
        dt = parse_date(iso_matches[0])
        if dt:
            return iso_matches[0], False
        return None, True
    elif len(iso_matches) > 1:
        return None, True

    # Unresolved date patterns
    unresolved_date_patterns = [
        r"\b\d{8}\b",
        r"\b\d{4}-\d{1}-\d{1,2}\b",
        r"\b\d{4}-W\d{2}-\d\b",
        r"\b(?:last|this|next)\s+(?:week|month|quarter|year)\b",
        r"\b(?:last\s+7\s+days|month\s+to\s+date|year\s+to\s+date|ytd|fy\d{2}|today|tomorrow|recently|latest|now|lately)\b",
        r"\b(?:in|during|for|until|throughout)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b",
        r"\b\d{1,2}(?:st|nd|rd|th)\s+[A-Za-z]+\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b"
    ]
    for pat in unresolved_date_patterns:
        if re.search(pat, q_lower):
            return None, True

    return None, False

def extract_store(q):
    q_clean = q.replace("?", " ").replace("!", " ").replace(",", " ")
    tokens = q_clean.split()

    resolved_store = None
    store_conf = 1.0
    unresolved_named_store = False

    # 1. Exact match / aliases
    for s in STORES:
        pattern = r"\b" + re.escape(s) + r"(?:'s)?\b"
        if re.search(pattern, q, re.IGNORECASE):
            resolved_store = s
            store_conf = 1.0
            break

    if not resolved_store:
        if re.search(r"\bBangalore(?:'s)?\b", q, re.IGNORECASE):
            resolved_store = "Bengaluru"
            store_conf = 1.0

    # 2. Check candidate words for fuzzy match
    for i, raw_word in enumerate(tokens):
        w = raw_word.rstrip(".,!?;:\"'")
        w_bare = re.sub(r"'s$", "", w, flags=re.IGNORECASE)
        has_possessive = bool(re.search(r"'s$", w, re.IGNORECASE))
        is_first = (i == 0)

        if len(w_bare) < 5:
            continue
        if not (w_bare[0].isupper() or has_possessive):
            continue
        if is_first and not has_possessive:
            continue
        if w_bare.lower() in STOP_WORDS:
            continue

        prev_word = tokens[i - 1].lower().rstrip(".,;:!?") if i > 0 else ""
        if w_bare.lower() in PROPER_NOUNS_DISALLOWED:
            if has_possessive or prev_word in {"for", "about", "in", "at"}:
                unresolved_named_store = True
            continue

        best_sim = 0.0
        best_store = None
        for s in STORES:
            sim = difflib.SequenceMatcher(None, w_bare.lower(), s.lower()).ratio()
            if sim > best_sim:
                best_sim = sim
                best_store = s

        if best_sim >= 0.70:
            if not resolved_store:
                resolved_store = best_store
                store_conf = round(best_sim, 2)
        else:
            if has_possessive or prev_word in {"and", "or", "vs", "versus", "than", "for"}:
                unresolved_named_store = True
            elif not resolved_store and (prev_word in {"about", "in", "at"} or w_bare.istitle()):
                if w_bare.lower() not in {"diwali", "revenue", "target", "stock", "amul", "toor", "dal", "milk"}:
                    unresolved_named_store = True

    if unresolved_named_store:
        return resolved_store, 0.4, True

    return resolved_store, store_conf, False

def extract_product(q):
    q_lower = q.lower()
    for pid, pfull, pshort in PRODUCTS_LIST:
        if pfull.lower() in q_lower or pshort.lower() in q_lower:
            return pfull, 1.0
    return None, 1.0

def understand(question, session_context=None):
    if session_context is None:
        session_context = {}

    q = question.strip()
    q_lower = q.lower()

    prohibited_kw = [
        "ignore", "disregard", "override", "bypass", "forget",
        "send", "email", "whatsapp", "purchase", "buy", "restock", "place an order",
        "book", "flight", "ticket", "hotel"
    ]
    is_prohibited = any(re.search(r"\b" + re.escape(w) + r"\b", q_lower) for w in prohibited_kw)
    if not is_prohibited:
        m = re.search(r"\b(reorder|order)\b", q_lower)
        if m:
            after_word = q_lower[m.end():].strip().split()
            next_w = after_word[0] if after_word else ""
            if next_w not in ["threshold", "level", "point", "thresholds", "levels", "points"]:
                is_prohibited = True

    if is_prohibited:
        return {
            "intent": "out_of_scope", "store": None, "metric": None,
            "date": None, "product": None, "has_weather": False,
            "confidence": 1.0, "missing_entities": []
        }

    # Rule 2: Unsupported metrics
    unsupported_kw = [
        "profit", "margin", "marketing", "cost", "expense", "shortfall",
        "efficiency", "weekend", "per footfall", "per visitor"
    ]
    if any(re.search(r"\b" + re.escape(w) + r"\b", q_lower) for w in unsupported_kw):
        return {
            "intent": "unsupported_metric", "store": None, "metric": None,
            "date": None, "product": None, "has_weather": False,
            "confidence": 1.0, "missing_entities": []
        }

    # Rule 3: Diagnostic
    if re.search(r"\b(why|trend|reason)\b", q_lower):
        return {
            "intent": "diagnostic", "store": None, "metric": None,
            "date": None, "product": None, "has_weather": False,
            "confidence": 1.0, "missing_entities": []
        }

    # Parse entities
    res_store, store_conf, unres_store = extract_store(q)
    res_date, unres_date = extract_dates_and_flags(q)
    res_product, prod_conf = extract_product(q)
    has_weather = bool(re.search(r"\b(weather|rain|temperature|humidity|hot|cold)\b", q_lower))

    # Metric matching
    metric = None
    if re.search(r"\b(revenue|sales|turnover|earnings)\b", q_lower):
        metric = "revenue_inr"
    elif re.search(r"\btarget\b", q_lower) and not re.search(r"\b(hit|met|meet|miss|missed|beat|exceed|achieve|reach|below|above|against|versus)\b", q_lower):
        metric = "daily_target_inr"
    elif re.search(r"\b(footfall|visitors?)\b", q_lower):
        metric = "footfall"
    elif re.search(r"\bstockout\b", q_lower):
        metric = "stockout_hours"
    elif re.search(r"\bdiscount\b", q_lower):
        metric = "discount_pct"

    # Intent selection
    # Rule 4: Inventory
    if res_product or re.search(r"\b(reorder|inventory)\b", q_lower):
        intent = "inventory"
    # Rule 5: Feedback
    elif re.search(r"\b(feedback|reviews?|ratings?|customers?\s+(?:saying|say|says))\b", q_lower):
        intent = "feedback"
    # Rule 6: Target vs Actual
    elif re.search(r"\btarget\b", q_lower) and re.search(r"\b(hit|met|meet|miss|missed|beat|exceed|achieved?|reached?|below|above|against|versus|fall short)\b", q_lower) \
            or re.search(r"\b(achievement|performance\s+band)\b", q_lower):
        intent = "target_vs_actual"
    # Rule 7: Comparison
    elif re.search(r"\b(which|highest|lowest|best|worst)\b", q_lower) and not res_store and not unres_store:
        intent = "comparison"
    # Rule 8: Lookup with metric
    elif metric:
        intent = "lookup"
    # Rule 9: Weather
    elif has_weather:
        intent = "weather"
    # Rule 10: Store / Date follow up without metric or weather
    elif res_store or unres_store or res_date or unres_date:
        if session_context.get("last_intent") == "target_vs_actual":
            intent = "target_vs_actual"
        else:
            intent = "lookup"
    # Rule 11: Out of scope
    else:
        return {
            "intent": "out_of_scope", "store": None, "metric": None,
            "date": None, "product": None, "has_weather": False,
            "confidence": 1.0, "missing_entities": []
        }

    # Session context carryover
    store = res_store
    date_val = res_date
    product = res_product

    if intent in ["lookup", "target_vs_actual", "feedback", "weather"]:
        if not store and not unres_store:
            store = session_context.get("store")

    if intent in ["lookup", "comparison"]:
        if not metric:
            metric = session_context.get("metric")

    if intent in ["lookup", "target_vs_actual", "comparison", "weather"]:
        if not date_val and not unres_date:
            date_val = session_context.get("date")

    if intent == "inventory":
        if not product:
            product = session_context.get("product")

    # Ambiguity check
    is_ambiguous = False
    found_stores = [s for s in STORES if re.search(r"\b" + s + r"\b", q, re.IGNORECASE)]
    if len(found_stores) > 1 and intent != "comparison":
        is_ambiguous = True

    # Missing entities per intent
    missing = []
    if intent == "lookup":
        if not store: missing.append("store")
        if not metric: missing.append("metric")
        if not date_val: missing.append("date")
    elif intent == "target_vs_actual":
        if not store: missing.append("store")
        if not date_val: missing.append("date")
    elif intent == "comparison":
        if not metric: missing.append("metric")
        if not date_val: missing.append("date")
    elif intent == "inventory":
        if not product: missing.append("product")
    elif intent == "feedback":
        if not store: missing.append("store")
    elif intent == "weather":
        if not store: missing.append("store")
        if not date_val: missing.append("date")

    conf = 1.0
    if unres_store or unres_date or is_ambiguous or missing:
        conf = 0.4
    else:
        conf = min(conf, store_conf)

    return {
        "intent": intent,
        "store": store,
        "metric": metric,
        "date": date_val,
        "product": product,
        "has_weather": has_weather,
        "confidence": conf,
        "missing_entities": missing,
        "unres_store": unres_store,
        "unres_date": unres_date,
        "is_ambiguous": is_ambiguous
    }