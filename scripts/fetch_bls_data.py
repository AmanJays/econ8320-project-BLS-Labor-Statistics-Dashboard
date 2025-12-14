#!/usr/bin/env python3
"""
Fetch U.S. Unemployment Rate from BLS (no API key required)
and save to data/unemployment.csv
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime

# --- Config ---
OUTPUT_FILE = "data/unemployment.csv"
START_YEAR = 2000
END_YEAR = datetime.now().year

SERIES_ID = "LNS14000000"  # Unemployment Rate
BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# --- Fetch data ---
def fetch_data(start_year, end_year):
    payload = json.dumps({
        "seriesid": [SERIES_ID],
        "startyear": str(start_year),
        "endyear": str(end_year)
    })

    headers = {"Content-type": "application/json"}
    response = requests.post(BLS_API, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Convert JSON to DataFrame ---
def parse_json(json_data):
    records = []

    series = json_data["Results"]["series"][0]
    for item in series["data"]:
        if not item["period"].startswith("M"):
            continue

        year = int(item["year"])
        month = int(item["period"][1:])
        date = f"{year}-{month:02d}-01"

        records.append({
            "Date": date,
            "Unemployment Rate": float(item["value"])
        })

    df = pd.DataFrame(records)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    return df

# --- Main ---
if __name__ == "__main__":
    print("Fetching unemployment data...")
    json_data = fetch_data(START_YEAR, END_YEAR)
    df = parse_json(json_data)

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_FILE}")
