import requests
import pandas as pd
import json
from datetime import datetime
import os

OUTPUT_FILE = "data/data.csv"

# Series IDs remain the same
BLS_SERIES = {
    'LNS14000000': 'Unemployment Rate',
    'CES0000000001': 'Employment Level',
    'CUUR0000SA0': 'CPI',
    'CES0500000003': 'Hourly Earnings',
    'CES0500000002': 'Hours Worked'
}

BLS_API_URL = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

# --- MODIFIED: Added parameter for start_year ---
def fetch_bls_data(series_ids, start_year=2008, end_year=None):
    # If end_year is None, it defaults to the current year, ensuring up-to-date data.
    if end_year is None:
        end_year = datetime.now().year
    
    headers = {"Content-type": "application/json"}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    })
    
    # Optional: You may want to check for the BLS API key here if you plan to use one for higher limits
    # data["registrationkey"] = "YOUR_KEY_HERE"
    
    resp = requests.post(BLS_API_URL, data=data, headers=headers)
    return resp.json()

# --- MODIFIED: json_to_df handles date format and calculates Weekly Income ---
def json_to_df(json_data):
    records = []
    
    # Handle API errors before processing
    if 'Results' not in json_data or 'series' not in json_data['Results']:
        print("BLS API Error or no data returned.")
        return pd.DataFrame() # Return empty DataFrame on failure

    for series in json_data['Results']['series']:
        series_name = BLS_SERIES.get(series['seriesID'], series['seriesID'])
        for item in series['data']:
            year = int(item['year'])
            period = item['period']
            
            # We only care about monthly data (M01 to M12)
            if period.startswith('M'):
                month = int(period[1:])
                date = f"{year}-{month:02d}-01"
                value = float(item['value'])
                records.append({"Date": date, "Series": series_name, "Value": value})
                
    if not records:
        return pd.DataFrame()
        
    df = pd.DataFrame(records)
    # Pivot the data
    df = df.pivot(index="Date", columns="Series", values="Value").reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Calculate derived metric
    if 'Hourly Earnings' in df.columns and 'Hours Worked' in df.columns:
        df['Weekly Income'] = df['Hourly Earnings'] * df['Hours Worked']
        
    return df.sort_values(by='Date').reset_index(drop=True)

# --- MODIFIED: collect_data now implements the intelligent refresh logic ---
def collect_data():
    os.makedirs("data", exist_ok=True)
    
    if os.path.isfile(OUTPUT_FILE):
        print("Data file exists. Checking for new data...")
        
        # Load existing data
        df_old = pd.read_csv(OUTPUT_FILE)
        df_old['Date'] = pd.to_datetime(df_old['Date'])
        
        # Determine the year from which to start fetching new data
        latest_date = df_old['Date'].max()
        start_year_fetch = latest_date.year
        
        # Fetch new data starting from the year of the last recorded date
        print(f"Fetching data from BLS starting {start_year_fetch} to ensure completeness...")
        json_data = fetch_bls_data(list(BLS_SERIES.keys()), start_year=start_year_fetch)
        df_new = json_to_df(json_data)
        
        if df_new.empty:
            print("No new data available from BLS or an error occurred.")
            return df_old
        
        # Combine old and new data, keeping the most recent entry for any given date
        # This handles cases where old data might be slightly revised by the API
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        # Drop duplicates based on the 'Date' column, keeping the last (newest) record
        df_combined.drop_duplicates(subset=['Date'], keep='last', inplace=True)
        df = df_combined.sort_values(by='Date').reset_index(drop=True)
        
        if len(df) > len(df_old):
            print(f"Successfully appended {len(df) - len(df_old)} new month(s) of data.")
            df.to_csv(OUTPUT_FILE, index=False)
        else:
            print("No new data to append or file is up to date.")
            
        return df

    else:
        # Initial fetch if no file exists
        print("Data file does not exist. Performing initial fetch from 2008...")
        json_data = fetch_bls_data(list(BLS_SERIES.keys()))
        df = json_to_df(json_data)
        
        if not df.empty:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Initial data fetch complete. Data saved to {OUTPUT_FILE}")
        
        return df

if __name__ == "__main__":
    # Ensure data folder exists before running the script
    os.makedirs("data", exist_ok=True)
    collect_data()
