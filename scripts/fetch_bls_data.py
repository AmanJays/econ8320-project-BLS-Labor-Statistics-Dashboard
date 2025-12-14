import requests
import pandas as pd
import json
from datetime import datetime
import os

OUTPUT_FILE = "data/data.csv"

BLS_SERIES = {
    'LNS14000000': 'Unemployment Rate',
    'CES0000000001': 'Employment Level',
    'CUUR0000SA0': 'CPI',
    'CES0500000003': 'Hourly Earnings',
    'CES0500000002': 'Hours Worked'
}

BLS_API_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

def fetch_bls_data(series_ids, start_year=2008, end_year=None):
    if end_year is None:
        end_year = datetime.now().year
    headers = {"Content-type": "application/json"}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    })
    resp = requests.post(BLS_API_URL, data=data, headers=headers)
    return resp.json()

def json_to_df(json_data):
    records = []
    for series in json_data['Results']['series']:
        series_name = BLS_SERIES.get(series['seriesID'], series['seriesID'])
        for item in series['data']:
            year = int(item['year'])
            period = item['period']
            if period.startswith('M'):
                month = int(period[1:])
                date = f"{year}-{month:02d}-01"
                value = float(item['value'])
                records.append({"Date": date, "Series": series_name, "Value": value})
    df = pd.DataFrame(records)
    df = df.pivot(index="Date", columns="Series", values="Value").reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Weekly Income'] = df['Hourly Earnings'] * df['Hours Worked']
    return df

def collect_data():
    os.makedirs("data", exist_ok=True)
    if not os.path.isfile(OUTPUT_FILE):
        print("Fetching initial data from BLS...")
        json_data = fetch_bls_data(list(BLS_SERIES.keys()))
        df = json_to_df(json_data)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Data saved to {OUTPUT_FILE}")
    else:
        print("Data already exists. Loading existing data...")
        df = pd.read_csv(OUTPUT_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
    return df

if __name__ == "__main__":
    collect_data()
