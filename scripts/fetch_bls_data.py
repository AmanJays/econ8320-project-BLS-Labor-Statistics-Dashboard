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
    "LNS14000000": "Unemployment Rate",
    "LNS11300000": "Labor Force Participation Rate",
    "CES0500000003": "Avg Hourly Earnings, Total Private",
    "CES3000000001": "Manufacturing Employment"
}

@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df



class BLSFetcher:
    def __init__(
        self,
        api_key: str,
        series_ids: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ):
        now = datetime.utcnow()
        self.api_key = api_key
        self.series_ids = series_ids
        self.start_year = start_year or now.year - 5
        self.end_year = end_year or now.year
        self.url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def fetch(self) -> Dict:
        payload = {
            "seriesid": self.series_ids,
            "startyear": str(self.start_year),
            "endyear": str(self.end_year),
            "registrationKey": self.api_key,
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(self.url, data=json.dumps(payload), headers=headers, timeout=30)
        resp.raise_for_status()
        j = resp.json()
        if j.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(j)
        return j

    def parse(self, json_resp: Dict) -> pd.DataFrame:
        rows = []
        for s in json_resp["Results"]["series"]:
            sid = s["seriesID"]
            for item in s["data"]:
                if not item["period"].startswith("M"):
                    continue
                month = int(item["period"][1:])
                date = f"{item['year']}-{month:02d}"
                rows.append(
                    {
                        "series_id": sid,
                        "series_title": SERIES.get(sid, sid),
                        "date": date,
                        "value": float(item["value"]),
                    }
                )
        return pd.DataFrame(rows)

    def save(self, df: pd.DataFrame):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(DATA_FILE):
            old = pd.read_csv(DATA_FILE)
            df = pd.concat([old, df])
            df = df.drop_duplicates(subset=["series_id", "date"], keep="last")
        df = df.sort_values(["series_id", "date"])
        df.to_csv(DATA_FILE, index=False)
        print(f"Saved {len(df)} rows to {DATA_FILE}")


def main():
    api_key = os.environ.get(API_ENV_VAR)
    if not api_key:
        sys.exit("ERROR: BLS_API_KEY not set")

    fetcher = BLSFetcher(api_key, list(SERIES.keys()))
    print(f"Fetching BLS data {fetcher.start_year}–{fetcher.end_year}")
    data = fetcher.fetch()
    df = fetcher.parse(data)
    fetcher.save(df)
    print("Done.")


if __name__ == "__main__":
    main()
