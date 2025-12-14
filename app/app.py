import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="US Labor Statistics Dashboard (BLS)", layout="wide")

DATA_FILE = "data/bls_data.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE, dtype={"date": str})

df = load_data()

st.title("US Labor Statistics Dashboard (BLS)")

series_map = (
    df[["series_id", "series_title"]]
    .drop_duplicates()
    .set_index("series_id")["series_title"]
    .to_dict()
)

selected = st.multiselect(
    "Select series",
    options=list(series_map.keys()),
    default=list(series_map.keys())[:3],
    format_func=lambda x: series_map[x]
)

min_date, max_date = df["date"].min(), df["date"].max()

start = st.sidebar.text_input("Start (YYYY-MM)", min_date)
end = st.sidebar.text_input("End (YYYY-MM)", max_date)

plot_df = df[
    (df["series_id"].isin(selected)) &
    (df["date"] >= start) &
    (df["date"] <= end)
]

st.subheader("Latest values")
cols = st.columns(len(selected))
for i, sid in enumerate(selected):
    latest = plot_df[plot_df["series_id"] == sid].sort_values("date").iloc[-1]
    cols[i].metric(series_map[sid], f"{latest['value']}")

fig = px.line(
    plot_df,
    x="date",
    y="value",
    color="series_title",
    labels={"value": "Value", "date": "Date"}
)

st.plotly_chart(fig, use_container_width=True)
