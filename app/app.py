# app.py

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from scripts.fetch_bls_data import main as fetch_data_main 

# Configuration from the fetch script (must match)
DATA_FILE = "data/bls_data.csv"
DEFAULT_SERIES = ["LNS14000000", "CES0000000001", "LNS11300000"] # Default series to show

st.set_page_config(page_title="BLS Labor Statistics Dashboard", layout="wide")

st.title("🇺🇸 U.S. Labor Statistics — BLS (Auto-updating)")
st.caption("Data is pulled directly from the BLS API and committed monthly via GitHub Actions.")

# --- Load data ---
# Use st.cache_data so the CSV is only read once per session
@st.cache_data(ttl=3600, show_spinner="Loading and preparing labor data...")
def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        st.error("Data file not found. Please run the fetch script first.")
        # If the file doesn't exist, try to create the folder but don't stop the app
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        return pd.DataFrame() 

    df = pd.read_csv(path, parse_dates=False)
    # Convert 'date' column to datetime objects
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df.dropna(subset=['date']).sort_values('date')

df = load_data()

if df.empty:
    st.warning("No data found or load failed. Please check the `data/bls_data.csv` file.")
    st.stop()

# --- Controls ---
# Map series ID to title for human-readable selection
series_map = df[["series_id", "series_title"]].drop_duplicates().set_index("series_id")["series_title"].to_dict()

st.sidebar.header("Filter & View")
selected_series_ids = st.sidebar.multiselect(
    "Series to Display", 
    options=list(series_map.keys()), 
    format_func=lambda s: f"{series_map[s]}", 
    default=DEFAULT_SERIES
)

# Date Range Filtering
min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.sidebar.slider(
    "Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM"
)

# --- Prepare data for plotting ---
plot_df = df[df["series_id"].isin(selected_series_ids)].copy()

# Filter by selected date range
plot_df = plot_df[(plot_df["date"].dt.date >= start_date) & (plot_df["date"].dt.date <= end_date)].copy()

# --- KPI row: show latest value and change ---
st.subheader("Latest Market Indicators")

# Calculate Delta (Change vs. Previous Month/Period)
def calculate_delta(series_df):
    if len(series_df) < 2:
        return "N/A", "off"
    
    # Get the last two unique values
    latest_val = series_df.iloc[-1]['value']
    prev_val = series_df.iloc[-2]['value']
    
    delta = latest_val - prev_val
    
    # Determine color for rate (Unemployment) vs. level (Payrolls)
    sid = series_df.iloc[0]['series_id']
    if sid == "LNS14000000": # Unemployment Rate: lower is better ('inverse')
        color = 'inverse'
    elif sid == "LNS11300000": # Participation Rate: higher is better ('normal')
        color = 'normal'
    else: # Levels: higher is generally better ('normal')
        color = 'normal'

    if abs(delta) < 0.01 and delta != 0: # Small changes for rates
        delta_str = f"{delta:+.2f} pp"
    elif abs(delta) >= 1000: # For large numbers (Payrolls)
        delta_str = f"{delta/1000:+.1f}k"
    else: # Default format
        delta_str = f"{delta:+.2f}"
        
    return delta_str, color

kpi_cols = st.columns(len(selected_series_ids) if len(selected_series_ids) <= 4 else 4)

for i, sid in enumerate(selected_series_ids[:4]):
    series_df = plot_df[plot_df["series_id"] == sid].sort_values("date")
    if series_df.empty:
        kpi_cols[i].metric(label=series_map.get(sid, sid), value="N/A")
    else:
        latest_row = series_df.iloc[-1]
        delta_str, color = calculate_delta(series_df)
        
        # Format based on series type
        if sid == "LNS14000000" or sid == "LNS11300000":
            val_str = f"{latest_row['value']:.1f}%"
        elif sid == "CES0000000001":
            val_str = f"{latest_row['value']:,.0f}"
        else:
            val_str = f"{latest_row['value']:,.2f}"
            
        kpi_cols[i].metric(label=f"{series_map.get(sid)}", value=val_str, delta=delta_str, delta_color=color)

# --- Time-series plot ---
st.subheader("Time Series Visualization")
if plot_df.empty:
    st.info("No data in the selected date range/series.")
else:
    # Use Plotly Express for simplicity
    fig = px.line(
        plot_df, 
        x="date", 
        y="value", 
        color="series_title", 
        labels={"value":"Value","date":"Date", "series_title": "Metric"}, 
        hover_data={"value": ':.2f', "date": "|%Y-%m"},
        title="Labor Statistics Trends Over Time"
    )
    
    # Improve hover and layout
    fig.update_traces(mode='lines', line=dict(width=2))
    fig.update_layout(
        hovermode="x unified",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- Data table ---
with st.expander("Show Underlying Data"):
    # Pivot for better readability
    table_df = plot_df.pivot(index='date', columns='series_title', values='value').tail(24)
    st.dataframe(table_df.style.format("{:,.2f}"), use_container_width=True)
