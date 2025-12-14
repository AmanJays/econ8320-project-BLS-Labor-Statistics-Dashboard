# scripts/fetch_bls_data.py

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict

# ---------------------------
# CONFIG: change these if desired
# ---------------------------
SERIES = {
    # series_id: friendly_name
    "CES0000000001": "Total Nonfarm Payrolls",     # Required
    "LNS14000000": "Unemployment Rate",           # Required
    "LNS11300000": "Labor Force Participation Rate", # Selected
    "CES0500000003": "Avg Hourly Earnings, Total Private", # Selected
    "CES3000000001": "Manufacturing Employment"     # Selected
}

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "bls_data.csv")
API_ENV_VAR = "BLS_API_KEY"
# ---------------------------

class BLSFetcher:
    def __init__(self, api_key: str, series_ids: List[str], start_year: int = None, end_year: int = None):
        self.api_key = api_key
        self.series_ids = series_ids
        now = datetime.utcnow()
        self.end_year = end_year or now.year
        # Default: collect 5 years back to ensure history
        self.start_year = start_year or max(1970, now.year - 5)
        self.url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def fetch(self) -> Dict:
        """Fetch data for all series in one API request."""
        headers = {"Content-type": "application/json"}
        payload = {
            "seriesid": self.series_ids,
            "startyear": str(self.start_year),
            "endyear": str(self.end_year),
            "registrationKey": self.api_key
        }
        try:
            resp = requests.post(self.url, data=json.dumps(payload), headers=headers, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            if j.get("status") != "REQUEST_SUCCEEDED":
                # Print API error message for debugging
                raise RuntimeError(f"BLS API returned non-success status: {j.get('status')} - {j.get('message')}")
            return j
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def parse_to_df(self, json_resp: Dict) -> pd.DataFrame:
        """Convert BLS JSON response to a long-format DataFrame."""
        rows = []
        series_list = json_resp.get("Results", {}).get("series", [])
        for s in series_list:
            sid = s.get("seriesID")
            # Use the friendly name from the SERIES dict
            series_title = SERIES.get(sid, sid) 
            
            for item in s.get("data", []):
                year = int(item.get("year"))
                period = item.get("period")
                value = item.get("value")
                
                date_str = None
                if period and period.startswith("M"):
                    # Monthly data: convert to YYYY-MM
                    month = int(period[1:])
                    date_str = f"{year:04d}-{month:02d}"
                else:
                    # Keep non-monthly data format for completeness
                    date_str = f"{year}-{period}"
                    
                rows.append({
                    "series_id": sid,
                    "series_title": series_title,
                    "date": date_str,
                    "value": pd.to_numeric(value, errors="coerce")
                })
                
        if not rows:
            return pd.DataFrame(columns=["series_id","series_title","date","value"])
            
        df = pd.DataFrame(rows)
        # Sort by date
        df = df.sort_values(["series_id","date"]).reset_index(drop=True)
        return df

    def load_existing(self) -> pd.DataFrame:
        """Load existing CSV if present."""
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE)
        else:
            return pd.DataFrame(columns=["series_id","series_title","date","value"])

    def update_csv(self, new_df: pd.DataFrame):
        """Append new rows to existing CSV, deduplicate, sort, and save."""
        os.makedirs(DATA_DIR, exist_ok=True)
        existing = self.load_existing()
        
        combined = pd.concat([existing, new_df], axis=0, ignore_index=True)
        # Drop duplicates by (series_id, date), keeping the last (newest API pull)
        combined = combined.drop_duplicates(subset=["series_id","date"], keep="last")
        
        # sort and save
        combined = combined.sort_values(["series_id","date"]).reset_index(drop=True)
        combined.to_csv(DATA_FILE, index=False)
        print(f"Saved {len(combined)} total rows to {DATA_FILE}")

def main():
    api_key = os.environ.get(API_ENV_VAR)
    if not api_key:
        sys.exit(f"Error: environment variable {API_ENV_VAR} not set. Set it before running.")
        
    fetcher = BLSFetcher(api_key=api_key, series_ids=list(SERIES.keys()))
    
    print(f"Fetching BLS series for years {fetcher.start_year} to {fetcher.end_year}...")
    
    try:
        resp = fetcher.fetch()
        df = fetcher.parse_to_df(resp)
        if df.empty:
            print("Warning: no data returned by BLS API.")
        else:
            fetcher.update_csv(df)
            
    except RuntimeError as e:
        sys.exit(f"Data fetching failed: {e}")
        
    print("Done.")

if __name__ == "__main__":
    main()
