import os
import sqlite3
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

APPROVED_FIELDS = {
    "revenue_inr", "daily_target_inr", "footfall", "stockout_hours",
    "discount_pct", "achievement_pct", "performance_band",
    "stock_units", "reorder_threshold", "rating", "theme"
}

ALLOWED_TABLES = {"store_daily_clean", "inventory", "feedback"}

MIN_DATE = "2026-04-01"
MAX_DATE = "2026-06-29"

def round_half_up(val, decimals=2):
    d = Decimal(str(val))
    target = Decimal("0." + "0" * decimals) if decimals > 0 else Decimal("1")
    return float(d.quantize(target, rounding=ROUND_HALF_UP))

def get_db_connection():
    conn = sqlite3.connect(":memory:")
    # Load clean data
    daily_df = pd.read_csv("data/store_daily_clean.csv")
    inv_df = pd.read_csv("data/inventory.csv")
    fb_df = pd.read_csv("data/feedback.csv")

    daily_df.to_sql("store_daily_clean", conn, index=False, if_exists="replace")
    inv_df.to_sql("inventory", conn, index=False, if_exists="replace")
    fb_df.to_sql("feedback", conn, index=False, if_exists="replace")
    return conn

def execute_with_retry(query_fn):
    simulate_failures = int(os.environ.get("SIMULATE_DB_FAILURES", 0))
    attempts = 0
    max_attempts = 3
    last_err = None

    while attempts < max_attempts:
        attempts += 1
        if attempts <= simulate_failures:
            last_err = Exception("Simulated DB connection failure")
            continue
        try:
            res = query_fn()
            return res, attempts, None
        except Exception as e:
            last_err = e

    return None, attempts, last_err

def check_date_range(date_val):
    if not date_val:
        return True
    if " to " in date_val:
        d1, d2 = date_val.split(" to ")
        return (MIN_DATE <= d1 <= MAX_DATE) and (MIN_DATE <= d2 <= MAX_DATE)
    return MIN_DATE <= date_val <= MAX_DATE

def fetch_single_lookup(store, metric, date_str):
    def run():
        df = pd.read_csv("data/store_daily_clean.csv")
        match = df[(df["store"] == store) & (df["date"] == date_str)]
        if len(match) == 0:
            return None
        val = match.iloc[0][metric]
        return val
    return execute_with_retry(run)

def fetch_target_vs_actual(store, date_str):
    def run():
        df = pd.read_csv("data/store_daily_clean.csv")
        match = df[(df["store"] == store) & (df["date"] == date_str)]
        if len(match) == 0:
            return None
        r = match.iloc[0]
        return {
            "store": store,
            "date": date_str,
            "revenue_inr": r["revenue_inr"],
            "daily_target_inr": r["daily_target_inr"],
            "achievement_pct": r["achievement_pct"],
            "performance_band": r["performance_band"]
        }
    return execute_with_retry(run)

def fetch_range_lookup_sql(store, metric, start_date, end_date):
    def run():
        conn = get_db_connection()
        cur = conn.cursor()
        query = f"SELECT {metric} FROM store_daily_clean WHERE store = ? AND date >= ? AND date <= ?"
        cur.execute(query, (store, start_date, end_date))
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return None
        total = sum(Decimal(str(r[0])) for r in rows)
        count = Decimal(str(len(rows)))
        avg = float((total / count).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        return avg, query
    return execute_with_retry(run)

def fetch_comparison_sql(metric, date_or_range, direction="highest"):
    if " to " in date_or_range:
        d1, d2 = date_or_range.split(" to ")
    else:
        d1 = d2 = date_or_range

    def run():
        conn = get_db_connection()
        cur = conn.cursor()
        query = f"""
            SELECT store, COUNT({metric}) as cnt, SUM(CAST(ROUND({metric} * 100) AS INTEGER)) as sum_cents
            FROM store_daily_clean
            WHERE date >= ? AND date <= ?
            GROUP BY store
        """
        cur.execute(query, (d1, d2))
        rows = cur.fetchall()
        conn.close()

        res = []
        for store, cnt, sum_cents in rows:
            if cnt > 0:
                avg = float((Decimal(sum_cents) / (Decimal(cnt) * Decimal(100))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                res.append((store, avg))

        # Sorting logic
        reverse = (direction == "highest")
        res.sort(key=lambda x: (-x[1] if reverse else x[1], x[0]))
        return res, query
    return execute_with_retry(run)

def fetch_inventory_sql(product):
    def run():
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT store, stock_units, reorder_threshold FROM inventory WHERE product = ? AND stock_units < reorder_threshold ORDER BY store"
        cur.execute(query, (product,))
        rows = cur.fetchall()
        conn.close()
        return rows, query
    return execute_with_retry(run)

def fetch_feedback_sql(store):
    def run():
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Rating query (rated rows only)
        q1 = "SELECT rating FROM feedback WHERE store = ? AND rating != '' AND rating IS NOT NULL"
        cur.execute(q1, (store,))
        ratings = [Decimal(str(r[0])) for r in cur.fetchall()]
        
        # All rows count
        q2 = "SELECT COUNT(*) FROM feedback WHERE store = ?"
        cur.execute(q2, (store,))
        total_rows = cur.fetchone()[0]

        # Top theme
        q3 = "SELECT theme, COUNT(*) as c FROM feedback WHERE store = ? GROUP BY theme ORDER BY c DESC, theme ASC"
        cur.execute(q3, (store,))
        top_theme = cur.fetchone()[0]
        
        conn.close()
        avg_rating = float((sum(ratings) / Decimal(str(len(ratings)))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) if ratings else 0.0
        return {
            "avg_rating": avg_rating,
            "rated_count": len(ratings),
            "total_count": total_rows,
            "top_theme": top_theme
        }, q1
    return execute_with_retry(run)