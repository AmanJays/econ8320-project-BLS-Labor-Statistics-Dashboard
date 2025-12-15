#!/usr/bin/env python3
"""
Fetch U.S. labor market data (2008–present) and save as CSV.
Handles series with different start dates (CPS vs CES).
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime

# --------------------------------------------------
# Config
# --------------------------------------------------
OUTPUT_FILE = "data/labor_data.csv"
START_YEAR = 2000
END_YEAR = datetime.now().year

SERIES_KEYS = {
    "LNS14000000": "Unemployment Rate",          
    "LNS11300000": "Labor Force Participation Rate",
    "CES0000000001": "Total Nonfarm Payrolls",   
    "CES3000000001": "Manufacturing Employment"
}


BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# --------------------------------------------------
# Request JSON from BLS
# --------------------------------------------------
def request_json(series_ids, start_year, end_year):
    headers = {"Content-type": "application/json"}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    })
    response = requests.post(BLS_API, data=data, headers=headers)
    response.raise_for_status()
    return response.json()

# --------------------------------------------------
# Convert JSON to DataFrame
# --------------------------------------------------
def convert_json(json_data):
    records = []
    for series in json_data["Results"]["series"]:
        series_id = series["seriesID"]
        name = SERIES_KEYS.get(series_id, series_id)
        for item in series["data"]:
            year = int(item["year"])
            period = item["period"]
            if "M" in period:
                month = int(period.replace("M", ""))
            else:
                continue
            date_str = f"{year}-{month:02d}-01"
            value = float(item["value"].replace(",", ""))
            records.append({"Date": date_str, "Series": name, "Value": value})

    df = pd.DataFrame(records).pivot(index="Date", columns="Series", values="Value").reset_index()
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# --------------------------------------------------
# Main: Fetch All Series
# --------------------------------------------------
def fetch_all_data():
    print("Fetching labor market data...")

    df_all = pd.DataFrame()
    series_ids = list(SERIES_KEYS.keys())

    start_year = START_YEAR
    while start_year <= END_YEAR:
        end_year_chunk = min(start_year + 9, END_YEAR)
        json_data = request_json(series_ids, start_year, end_year_chunk)
        df_chunk = convert_json(json_data)
        df_all = pd.concat([df_all, df_chunk], ignore_index=True)
        start_year += 10

    df_all = df_all.sort_values("Date").reset_index(drop=True)

    # Forward-fill missing CES series (e.g., Manufacturing Employment)
    for col in ["Total Nonfarm Payrolls", "Manufacturing Employment"]:
        if col in df_all.columns:
            df_all[col] = df_all[col].ffill()

    # Add Manufacturing Share (%) = Manufacturing / Total Nonfarm Payrolls * 100
    if "Manufacturing Employment" in df_all.columns and "Total Nonfarm Payrolls" in df_all.columns:
        df_all["Manufacturing Share (%)"] = df_all["Manufacturing Employment"] / df_all["Total Nonfarm Payrolls"] * 100

    # Save CSV
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df_all.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df_all)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_all_data()
