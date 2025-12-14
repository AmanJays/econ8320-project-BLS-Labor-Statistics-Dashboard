#!/usr/bin/env python3
"""
scripts/fetch_bls_data.py

Fetches U.S. labor statistics from the BLS API and saves as CSV.
Designed to be run regularly (e.g., monthly).
"""

import os
import json
import requests
import pandas as pd
from datetime import datetime

# --- Config ---
OUTPUT_FILE = "data/data.csv"
DEFAULT_START_YEAR = 2008
DEFAULT_END_YEAR = datetime.now().year

# BLS series keys
SERIES_KEYS = {
    "LNS14000000": "Unemployment Rate",
    "CES0000000001": "Employment Level",
    "CUUR0000SA0": "CPI",
    "CES0500000003": "Hourly Earnings",
    "CES0500000002": "Hours Worked"
}

BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# --- Fetch JSON from BLS ---
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

# --- Convert JSON to DataFrame ---
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
    # Calculate Weekly Income
    df["Hourly Earnings"] = pd.to_numeric(df.get("Hourly Earnings", 0), errors="coerce")
    df["Hours Worked"] = pd.to_numeric(df.get("Hours Worked", 0), errors="coerce")
    df["Weekly Income"] = round(df["Hourly Earnings"] * df["Hours Worked"], 2)
    return df

# --- Initial Data Fetch ---
def initial_data():
    df = pd.DataFrame()
    start_year = DEFAULT_START_YEAR
    series_ids = list(SERIES_KEYS.keys())

    while start_year <= DEFAULT_END_YEAR:
        end_year = min(start_year + 9, DEFAULT_END_YEAR)
        json_data = request_json(series_ids, start_year, end_year)
        new_df = convert_json(json_data)
        df = pd.concat([df, new_df], ignore_index=True)
        start_year += 10

    df = df.sort_values("Date")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Created {OUTPUT_FILE} ({DEFAULT_START_YEAR}-{DEFAULT_END_YEAR})")

# --- Update Existing Data ---
def update_data():
    df = pd.read_csv(OUTPUT_FILE)
    df["Date"] = pd.to_datetime(df["Date"])
    last_year = df["Date"].max().year
    current_year = datetime.now().year
    if last_year >= current_year:
        print("Data is already up-to-date.")
        return

    series_ids = list(SERIES_KEYS.keys())
    json_data = request_json(series_ids, last_year, current_year)
    new_df = convert_json(json_data)
    if not new_df.empty:
        df = pd.concat([df, new_df], ignore_index=True).drop_duplicates(subset="Date")
        df = df.sort_values("Date")
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Updated {OUTPUT_FILE} ({last_year}-{current_year})")
    else:
        print("No new data available.")

# --- Main Execution ---
if __name__ == "__main__":
    if os.path.exists(OUTPUT_FILE):
        update_data()
    else:
        initial_data()
