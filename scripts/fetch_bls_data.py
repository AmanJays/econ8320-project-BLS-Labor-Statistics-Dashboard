#!/usr/bin/env python3
"""
Fetch unemployment rate, total nonfarm payrolls,
and manufacturing employment from BLS (no API key).
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime

# --- Config ---
OUTPUT_FILE = "data/labor_data.csv"
START_YEAR = 2000
END_YEAR = datetime.now().year

SERIES = {
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Total Nonfarm Payrolls",
    "CES3000000001": "Manufacturing Employment"
}

BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# --- Fetch ---
def fetch_data(series_ids, start_year, end_year):
    payload = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    })
    headers = {"Content-type": "application/json"}
    response = requests.post(BLS_API, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Parse ---
def parse_json(json_data):
    records = []

    for series in json_data["Results"]["series"]:
        name = SERIES.get(series["seriesID"], series["seriesID"])

        for item in series["data"]:
            if not item["period"].startswith("M"):
                continue

            year = int(item["year"])
            month = int(item["period"][1:])
            date = f"{year}-{month:02d}-01"

            records.append({
                "Date": date,
                "Series": name,
                "Value": float(item["value"])
            })

    df = (
        pd.DataFrame(records)
        .pivot(index="Date", columns="Series", values="Value")
        .reset_index()
    )

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df

# --- Main ---
if __name__ == "__main__":
    print("Fetching labor market data...")

    json_data = fetch_data(list(SERIES.keys()), START_YEAR, END_YEAR)
    df = parse_json(json_data)

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
