import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(val, decimals=2):
    d = Decimal(str(val))
    target = Decimal("0." + "0" * decimals) if decimals > 0 else Decimal("1")
    return float(d.quantize(target, rounding=ROUND_HALF_UP))

def main():
    clean_df = pd.read_csv("data/store_daily_clean.csv")
    raw_df = pd.read_csv("data/store_daily.csv")

    stores = ["Ahmedabad", "Bengaluru", "Hyderabad", "Mumbai", "Pune"]
    
    print("--- Per-Store Metrics ---")
    for s in stores:
        sub = clean_df[clean_df["store"] == s]
        rev_mean = round_half_up(sub["revenue_inr"].mean(), 2)
        ff_mean = round_half_up(sub["footfall"].mean(), 2)
        so_mean = round_half_up(sub["stockout_hours"].mean(), 2)
        rev_per_ff = round_half_up(sub["revenue_inr"].sum() / sub["footfall"].sum(), 2)
        ach_mean = round_half_up(sub["achievement_pct"].mean(), 2)
        poor_days = int((sub["performance_band"] == "Poor").sum())
        print(f"{s}: rev={rev_mean:.2f}, ff={ff_mean:.2f}, so={so_mean:.2f}, rev_per_ff={rev_per_ff:.2f}, ach={ach_mean:.2f}, poor={poor_days}")

    all_rev_mean = round_half_up(clean_df["revenue_inr"].mean(), 2)
    all_ff_mean = round_half_up(clean_df["footfall"].mean(), 2)
    all_so_mean = round_half_up(clean_df["stockout_hours"].mean(), 2)
    all_rev_per_ff = round_half_up(clean_df["revenue_inr"].sum() / clean_df["footfall"].sum(), 2)
    all_ach_mean = round_half_up(clean_df["achievement_pct"].mean(), 2)
    all_poor_days = int((clean_df["performance_band"] == "Poor").sum())
    print(f"All stores: rev={all_rev_mean:.2f}, ff={all_ff_mean:.2f}, so={all_so_mean:.2f}, rev_per_ff={all_rev_per_ff:.2f}, ach={all_ach_mean:.2f}, poor={all_poor_days}")

    print("\n--- Correlations ---")
    # All rows cleaned
    corr_all_so = np.corrcoef(clean_df["revenue_inr"], clean_df["stockout_hours"])[0, 1]
    corr_all_ff = np.corrcoef(clean_df["revenue_inr"], clean_df["footfall"])[0, 1]
    print(f"All cleaned rows rev-so: {corr_all_so:.3f}, rev-ff: {corr_all_ff:.3f}")

    # Pune cleaned
    pune_df = clean_df[clean_df["store"] == "Pune"]
    corr_pune_so = np.corrcoef(pune_df["revenue_inr"], pune_df["stockout_hours"])[0, 1]
    corr_pune_ff = np.corrcoef(pune_df["revenue_inr"], pune_df["footfall"])[0, 1]
    print(f"Pune cleaned rev-so: {corr_pune_so:.3f}, rev-ff: {corr_pune_ff:.3f}")

    # Raw deduplicated without missing
    raw_dedup = raw_df.drop_duplicates(keep="first").copy()
    raw_dedup["ff_num"] = pd.to_numeric(raw_dedup["footfall"], errors="coerce")
    raw_valid = raw_dedup[raw_dedup["ff_num"].notna()]
    corr_raw_ff = np.corrcoef(raw_valid["revenue_inr"], raw_valid["ff_num"])[0, 1]
    print(f"Raw dedup non-missing rev-ff (446 rows): {corr_raw_ff:.3f}")

if __name__ == "__main__":
    main()