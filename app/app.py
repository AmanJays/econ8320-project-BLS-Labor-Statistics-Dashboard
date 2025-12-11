# app.py
import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

DATA_FILE = "data/bls_data.csv"

st.set_page_config(page_title="BLS Labor Statistics Dashboard", layout="wide")

st.title("US Labor Statistics — BLS (Auto-updating)")

# --- Load data ---
@st.cache_data
def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        return pd.DataFrame(columns=["series_id", "series_title", "year", "period", "date", "value"])
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
