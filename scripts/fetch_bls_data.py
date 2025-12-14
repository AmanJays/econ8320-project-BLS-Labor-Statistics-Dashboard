import requests
import json
import pandas as pd
from datetime import datetime
import os

OUTPUT_FILE = "../data/data.csv"

SERIES_KEYS = {
    'LNS14000000': 'Unemployment Rate',
    'CES0000000001': 'Employment Level',
    'CUUR0000SA0': 'CPI',
    'CES0500000003': 'Hourly Earnings',
    'CES0500000002': 'Hours Worked'
}

BLS_API = 'https://api.bls.gov/publicAPI/v1/timeseries/data/'

def fetch_bls(series_ids, start_year, end_year):
    payload = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    })
    headers = {"Content-type": "application/json"}
    response = requests.post(BLS_API, data=payload, headers=headers)
    return response.json()

def json_to_df(json_data):
    records = []
    for series in json_data['Results']['series']:
        series_id = series['seriesID']
        series_name = SERIES_KEYS.get(series_id, series_id)
        for item in series['data']:
            year = int(item['year'])
            period = item['period']
            if "M" in period:
                month = int(period.replace("M", ""))
                date_str = f"{year}-{month:02d}-01"
                records.append({"Date": date_str, "Series": series_name, "Value": float(item['value'])})
    df = pd.DataFrame(records).pivot(index="Date", columns="Series", values="Value").reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Weekly Income'] = df['Hourly Earnings'] * df['Hours Worked']
    return df

def save_data():
    start_year = 2008
    end_year = datetime.now().year
    series_ids = list(SERIES_KEYS.keys())
    df = pd.DataFrame()
    while start_year <= end_year:
        batch_end = min(start_year + 9, end_year)
        json_data = fetch_bls(series_ids, start_year, batch_end)
        df_batch = json_to_df(json_data)
        df = pd.concat([df, df_batch])
        start_year += 10
    df = df.drop_duplicates(subset=["Date"]).sort_values("Date")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    save_data()
