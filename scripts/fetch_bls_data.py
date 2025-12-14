#!/usr/bin/env python3
import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

SERIES = {
    "CES0000000001": "Total Nonfarm Payrolls",
    "LNS14000000": "Unemployment Rate (U-3)",
    "LNS11300000": "Labor Force Participation Rate",
    "CES0500000003": "Avg Hourly Earnings",
    "CES3000000001": "Manufacturing Employment"
}

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "bls_data.csv")
API_ENV_VAR = "BLS_API_KEY"

class BLSFetcher:
    def __init__(self, api_key: str, series_ids: List[str]):
        self.api_key = api_key
        self.series_ids = series_ids
        now = datetime.utcnow()
        self.start_year = now.year - 10
        self.end_year = now.year
        self.url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def fetch(self) -> Dict:
        payload = {
            "seriesid": self.series_ids,
            "startyear": str(self.start_year),
            "endyear": str(self.end_year),
            "registrationKey": self.api_key
        }
        resp = requests.post(self.url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def parse(self, json_resp: Dict) -> pd.DataFrame:
        rows = []
        for s in json_resp["Results"]["series"]:
            sid = s["seriesID"]
            for item in s["data"]:
                if not item["period"].startswith("M"):
                    continue
                month = int(item["period"][1:])
                date = f"{item['year']}-{month:02d}"

                rows.append({
                    "series_id": sid,
                    "series_title": SERIES.get(sid, sid),
                    "date": date,
                    "value": float(item["value"])
                })

        return pd.DataFrame(rows)

def main():
    api_key = os.getenv(API_ENV_VAR)
    if not api_key:
        sys.exit("BLS_API_KEY not set")

    fetcher = BLSFetcher(api_key, list(SERIES.keys()))
    data = fetcher.fetch()
    df = fetcher.parse(data)

    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(DATA_FILE, index=False)
    print(f"Saved {len(df)} rows to {DATA_FILE}")

if __name__ == "__main__":
    main()
