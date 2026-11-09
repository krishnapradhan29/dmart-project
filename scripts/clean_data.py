import csv
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd

def round_half_up(val, decimals=2):
    if pd.isna(val) or val == "":
        return val
    d = Decimal(str(val))
    target = Decimal("0." + "0" * decimals) if decimals > 0 else Decimal("1")
    return float(d.quantize(target, rounding=ROUND_HALF_UP))

def main():
    raw_df = pd.read_csv("data/store_daily.csv")
    cleaning_log = []

    # 1. Remove exact duplicate rows (keeping first occurrence)
    df = raw_df.drop_duplicates(keep="first").copy()

    # 2. Treat negative footfall as missing
    df["footfall_clean"] = pd.to_numeric(df["footfall"], errors="coerce")
    for idx, r in df[df["footfall_clean"] < 0].iterrows():
        cleaning_log.append({
            "store": r["store"],
            "date": r["date"],
            "old_footfall": int(r["footfall_clean"]),
            "new_footfall": "",
            "rule": "negative_to_missing"
        })
        df.loc[idx, "footfall_clean"] = np.nan

    # 3. Per-store IQR calculation & capping
    store_order = ["Mumbai", "Pune", "Hyderabad", "Bengaluru", "Ahmedabad"]
    store_bounds = {}
    for st in store_order:
        s_vals = df[(df["store"] == st) & (df["footfall_clean"].notna())]["footfall_clean"]
        q1 = s_vals.quantile(0.25, interpolation="linear")
        q3 = s_vals.quantile(0.75, interpolation="linear")
        iqr = q3 - q1
        store_bounds[st] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    for idx, r in df[df["footfall_clean"].notna()].iterrows():
        st = r["store"]
        lower, upper = store_bounds[st]
        val = r["footfall_clean"]
        if val > upper:
            capped = round_half_up(upper, 2)
            cleaning_log.append({
                "store": st,
                "date": r["date"],
                "old_footfall": int(val),
                "new_footfall": f"{capped:.2f}",
                "rule": "iqr_cap"
            })
            df.loc[idx, "footfall_clean"] = capped
        elif val < lower:
            capped = round_half_up(lower, 2)
            cleaning_log.append({
                "store": st,
                "date": r["date"],
                "old_footfall": int(val),
                "new_footfall": f"{capped:.2f}",
                "rule": "iqr_cap"
            })
            df.loc[idx, "footfall_clean"] = capped

    # 4. Per-store median imputation
    store_medians = {}
    for st in store_order:
        s_vals = df[(df["store"] == st) & (df["footfall_clean"].notna())]["footfall_clean"]
        med = round_half_up(s_vals.median(), 2)
        store_medians[st] = med

    for idx, r in df[df["footfall_clean"].isna()].iterrows():
        st = r["store"]
        med = store_medians[st]
        cleaning_log.append({
            "store": st,
            "date": r["date"],
            "old_footfall": "",
            "new_footfall": f"{med:.2f}",
            "rule": "median_impute"
        })
        df.loc[idx, "footfall_clean"] = med

    df["footfall"] = df["footfall_clean"]
    df.drop(columns=["footfall_clean"], inplace=True)

    # 5. Add feature columns (rounded to 2 decimals)
    df["revenue_per_footfall"] = (df["revenue_inr"] / df["footfall"]).apply(lambda x: round_half_up(x, 2))
    df["marketing_efficiency"] = (df["revenue_inr"] / df["marketing_spend_inr"]).apply(lambda x: round_half_up(x, 2))
    df["achievement_pct"] = ((df["revenue_inr"] / df["daily_target_inr"]) * 100).apply(lambda x: round_half_up(x, 2))
    df["shortfall_inr"] = (df["daily_target_inr"] - df["revenue_inr"]).apply(lambda x: round_half_up(x, 2))
    
    # derive weekday
    df["date_dt"] = pd.to_datetime(df["date"])
    df["weekend_flag"] = df["date_dt"].dt.dayofweek.apply(lambda w: "Yes" if w >= 5 else "No")
    
    def get_band(pct):
        if pct >= 100.0:
            return "Excellent"
        elif pct >= 75.0:
            return "Good"
        return "Poor"

    df["performance_band"] = df["achievement_pct"].apply(get_band)
    df.drop(columns=["date_dt"], inplace=True)

    # Save clean dataset
    df.to_csv("data/store_daily_clean.csv", index=False)

    # Save cleaning log
    with open("analysis/cleaning_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["store", "date", "old_footfall", "new_footfall", "rule"])
        writer.writeheader()
        writer.writerows(cleaning_log)

    print(f"Cleaned rows: {len(df)}")
    print(f"Cleaning log rows: {len(cleaning_log)}")

if __name__ == "__main__":
    main()