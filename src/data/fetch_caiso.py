"""
Fetch CAISO data via gridstatus and aggregate to monthly averages.

Features produced (matching paper Table 1 columns):
  nd  – total system load (MW avg)                 ← get_load
  x3  – renewable generation (MW avg)              ← get_fuel_mix: Solar+Wind+Geo+Biomass+Biogas+SmHydro
  x4  – gas generation (MW avg)                    ← get_fuel_mix: Natural Gas
  x9  – net imports (MW avg)                       ← get_fuel_mix: Imports

Saves to: data/raw/caiso_monthly.csv

Usage:
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 scripts/fetch_caiso.py
"""

import os
import sys
import warnings
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

warnings.filterwarnings("ignore")

try:
    from gridstatus import CAISO
except ImportError:
    sys.exit("Run: pip install gridstatus python-dateutil")

# ── Config ─────────────────────────────────────────────────────────────────────
START = date(2015, 1, 1)
END   = date(2024, 12, 31)

RENEWABLE_COLS = ["Solar", "Wind", "Geothermal", "Biomass", "Biogas", "Small Hydro"]

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT  = os.path.join(RAW_DIR, "caiso_monthly.csv")


def month_range(start: date, end: date):
    """Yield (month_start_str, month_end_str) pairs for each calendar month."""
    cur = start.replace(day=1)
    while cur <= end:
        nxt = cur + relativedelta(months=1)
        yield cur.isoformat(), nxt.isoformat(), cur.year, cur.month
        cur = nxt


def fetch_load(caiso: CAISO) -> pd.DataFrame:
    """Monthly average system load (MW)."""
    records = []
    for ms, me, yr, mo in tqdm(list(month_range(START, END)), desc="Load"):
        try:
            df = caiso.get_load(start=ms, end=me)
            records.append({"year": yr, "month": mo, "nd": df["Load"].mean()})
        except Exception as exc:
            print(f"  load {ms}: {exc}")
            records.append({"year": yr, "month": mo, "nd": float("nan")})
    return pd.DataFrame(records)


def fetch_fuel_mix(caiso: CAISO) -> pd.DataFrame:
    """Monthly averages for renewables, gas, and imports."""
    records = []
    for ms, me, yr, mo in tqdm(list(month_range(START, END)), desc="Fuel mix"):
        try:
            df = caiso.get_fuel_mix(start=ms, end=me)
            present_ren = [c for c in RENEWABLE_COLS if c in df.columns]
            row = {
                "year":  yr,
                "month": mo,
                "x3": df[present_ren].sum(axis=1).mean() if present_ren else float("nan"),
                "x4": df["Natural Gas"].mean()            if "Natural Gas" in df.columns else float("nan"),
                "x9": df["Imports"].mean()                if "Imports" in df.columns else float("nan"),
            }
            records.append(row)
        except Exception as exc:
            print(f"  fuel_mix {ms}: {exc}")
            records.append({"year": yr, "month": mo, "x3": float("nan"),
                            "x4": float("nan"), "x9": float("nan")})
    return pd.DataFrame(records)


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    caiso = CAISO()

    print("=== Fetching CAISO system load ===")
    load_df = fetch_load(caiso)

    print("\n=== Fetching CAISO fuel mix (renewables, gas, imports) ===")
    fuel_df = fetch_fuel_mix(caiso)

    merged = load_df.merge(fuel_df, on=["year", "month"])
    merged["date"] = pd.to_datetime(merged[["year", "month"]].assign(day=1))
    merged = merged.sort_values("date").reset_index(drop=True)

    print(f"\n--- Sample output ---")
    print(merged.tail(6).to_string(index=False))

    missing_pct = merged.isnull().mean() * 100
    print("\n--- Missing value % ---")
    print(missing_pct.round(1).to_string())

    merged.to_csv(OUTPUT, index=False)
    print(f"\nSaved {len(merged)} monthly rows → {OUTPUT}")


if __name__ == "__main__":
    main()
