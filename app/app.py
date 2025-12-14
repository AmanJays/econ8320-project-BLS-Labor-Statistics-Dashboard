# app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
#!/usr/bin/env python3
import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

# ---------------------------
# CONFIG: change these if desired
# ---------------------------
SERIES = {
    # series_id: friendly_name
    "CES0000000001": "Total Nonfarm Payrolls",    
    "LNS14000000": "Unemployment Rate",           # Unemployment rate (U-3)
    "LNS11300000": "Labor Force Participation Rate",
    "CES0500000003": "Avg Hourly Earnings, Total Private",
    "CES3000000001": "Manufacturing Employment"
}

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "bls_data.csv")
API_ENV_VAR = "BLS_API_KEY"

# ---------------------------
# Helper functions / class
# ---------------------------

class BLSFetcher:
    def __init__(self, api_key: str, series_ids: List[str], start_year: Optional[int] = None, end_year: Optional[int] = None):
        self.api_key = api_key
        self.series_ids = series_ids
        now = datetime.utcnow()
        self.end_year = end_year or now.year
        # default: collect 5 years back (ensures > 1 year history). Change if you want more.
        self.start_year = start_year or max(1970, now.year - 5)
        self.url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    def fetch(self) -> Dict:
        """
        Fetch data for all series in one API request.
        Returns the parsed JSON response.
        """
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
                raise RuntimeError(f"BLS API returned non-success status: {j.get('status')} - {j.get('message')}")
            return j
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def parse_to_df(self, json_resp: Dict) -> pd.DataFrame:
        """
        Convert BLS JSON response to a long-format DataFrame:
        columns = ['series_id','series_title','year','period','date','value']
        period is like 'M01' for January; date will be 'YYYY-MM'
        """
        rows = []
        series_list = json_resp.get("Results", {}).get("series", [])
        for s in series_list:
            sid = s.get("seriesID")
            # If the API includes 'series' -> 'catalog' structure not always present; use provided mapping if available.
            # The data array contains year & period & value
            for item in s.get("data", []):
                year = int(item.get("year"))
                period = item.get("period")           # e.g., 'M01'
                # skip annual or other non-monthly if needed; we'll keep anything.
                value = item.get("value")
                # convert period to YYYY-MM when possible
                date_str = None
                if period and period.startswith("M"):
                    month = int(period[1:])
                    date_str = f"{year:04d}-{month:02d}"
                else:
                    # For annual/quarterly, just use year with suffix
                    date_str = f"{year}-{period}"
                rows.append({
                    "series_id": sid,
                    "series_title": SERIES.get(sid, s.get("seriesID", sid)),
                    "year": year,
                    "period": period,
                    "date": date_str,
                    "value": pd.to_numeric(value, errors="coerce")
                })
        if not rows:
            return pd.DataFrame(columns=["series_id","series_title","year","period","date","value"])
        df = pd.DataFrame(rows)
        # Keep newest rows first (helpful for append logic)
        df = df.sort_values(["series_id","date"]).reset_index(drop=True)
        return df

    def load_existing(self) -> pd.DataFrame:
        """Load existing CSV if present, otherwise return empty df with proper columns."""
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE, dtype={"series_id": str, "series_title": str, "year": int, "period": str, "date": str, "value": float})
        else:
            return pd.DataFrame(columns=["series_id","series_title","year","period","date","value"])

    def update_csv(self, new_df: pd.DataFrame):
        """Append new rows to existing CSV, deduplicate, sort, and save."""
        os.makedirs(DATA_DIR, exist_ok=True)
        existing = self.load_existing()
        combined = pd.concat([existing, new_df], axis=0, ignore_index=True)
        # drop duplicate series_id + date combos, keep last (more recent API pull)
        combined = combined.drop_duplicates(subset=["series_id","date"], keep="last")
        # sort and save
        combined = combined.sort_values(["series_id","date"]).reset_index(drop=True)
        combined.to_csv(DATA_FILE, index=False)
        print(f"Saved {len(combined)} total rows to {DATA_FILE}")

# ---------------------------
# Script entrypoint
# ---------------------------

def main():
    api_key = os.environ.get(API_ENV_VAR)
    if not api_key:
        sys.exit(f"Error: environment variable {API_ENV_VAR} not set. Please set it to your BLS API key before running.\n"
                 f"Example (Linux/macOS):\n  export {API_ENV_VAR}=\"YOURKEY\"\n"
                 f"Example (Windows PowerShell):\n  setx {API_ENV_VAR} \"YOURKEY\"\n")
    fetcher = BLSFetcher(api_key=api_key, series_ids=list(SERIES.keys()))
    print(f"Fetching BLS series for years {fetcher.start_year} to {fetcher.end_year} ...")
    resp = fetcher.fetch()
    df = fetcher.parse_to_df(resp)
    if df.empty:
        print("Warning: no data returned by BLS API.")
    else:
        fetcher.update_csv(df)
    print("Done.")

if __name__ == "__main__":
    main()

DATA_FILE = "data/bls_data.csv"

st.set_page_config(page_title="BLS Labor Statistics Dashboard", layout="wide")

st.title("US Labor Statistics — BLS (Auto-updating)")

# --- Load data ---
@st.cache_data
def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["series_id","series_title","year","period","date","value"])
    df = pd.read_csv(path, parse_dates=False)
    # ensure date column normalized to YYYY-MM for monthly series
    return df

df = load_data()

if df.empty:
    st.warning("No data found. Make sure you've run the fetch script at least once.")
    st.stop()

# --- controls ---
series_map = df[["series_id", "series_title"]].drop_duplicates().set_index("series_id")["series_title"].to_dict()
selected_series = st.multiselect("Choose series to display", options=list(series_map.keys()), format_func=lambda s: f"{series_map[s]} ({s})", default=list(series_map.keys())[:3])

min_date = df["date"].min()
max_date = df["date"].max()
st.sidebar.markdown(f"**Data range:** {min_date} → {max_date}")
start = st.sidebar.text_input("Start (YYYY-MM)", value=min_date)
end = st.sidebar.text_input("End (YYYY-MM)", value=max_date)

# --- prepare data for plotting ---
plot_df = df[df["series_id"].isin(selected_series)].copy()
# keep only rows between start and end (string compare works for YYYY-MM)
plot_df = plot_df[(plot_df["date"] >= start) & (plot_df["date"] <= end)]
plot_df["value"] = pd.to_numeric(plot_df["value"], errors="coerce")

# KPI row: show latest value for each selected series
st.subheader("Latest values")
kpi_cols = st.columns(len(selected_series) if len(selected_series) <= 4 else 4)
for i, sid in enumerate(selected_series[:4]):
    series_df = plot_df[plot_df["series_id"] == sid]
    if series_df.empty:
        kpi_cols[i].metric(label=series_map.get(sid, sid), value="N/A")
    else:
        latest_row = series_df.sort_values("date").iloc[-1]
        val = latest_row["value"]
        kpi_cols[i].metric(label=f"{series_map.get(sid)}", value=f"{val}")

# Time-series plot
st.subheader("Time series")
if plot_df.empty:
    st.info("No data in the selected date range/series.")
else:
    fig = px.line(plot_df, x="date", y="value", color="series_id", labels={"value":"Value","date":"Date"}, hover_data=["series_title"])
    st.plotly_chart(fig, use_container_width=True)

# Data table
with st.expander("Show underlying data"):
    st.dataframe(plot_df.sort_values(["series_id","date"]).reset_index(drop=True), use_container_width=True)

st.caption("This dashboard reads the processed CSV (data/bls_data.csv). The dataset is updated by the fetch script run monthly via GitHub Actions.")


#streamlit run app/app.py
