import os
import streamlit as st
import pandas as pd
import plotly.express as px

DATA_FILE = "data/bls_data.csv"

st.set_page_config(
    page_title="US Labor Statistics — BLS",
    layout="wide"
)

st.title("US Labor Statistics — BLS (Auto-updating)")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()
    return pd.read_csv(DATA_FILE, dtype={"date": str})


df = load_data()

if df.empty:
    st.error("Data file not found. Run scripts/fetch_bls_data.py first.")
    st.stop()

# Sidebar controls
series_map = (
    df[["series_id", "series_title"]]
    .drop_duplicates()
    .set_index("series_id")["series_title"]
    .to_dict()
)

selected = st.multiselect(
    "Choose series to display",
    options=list(series_map.keys()),
    default=list(series_map.keys()),
    format_func=lambda s: f"{series_map[s]} ({s})",
)

min_date, max_date = df["date"].min(), df["date"].max()

st.sidebar.markdown(f"**Data range:** {min_date} → {max_date}")
start = st.sidebar.text_input("Start (YYYY-MM)", min_date)
end = st.sidebar.text_input("End (YYYY-MM)", max_date)

plot_df = df[df["series_id"].isin(selected)]
plot_df = plot_df[(plot_df["date"] >= start) & (plot_df["date"] <= end)]

# KPIs
st.subheader("Latest values")
cols = st.columns(min(len(selected), 4))
for i, sid in enumerate(selected[:4]):
    s = plot_df[plot_df["series_id"] == sid]
    if not s.empty:
        val = s.sort_values("date").iloc[-1]["value"]
        cols[i].metric(series_map[sid], f"{val}")
    else:
        cols[i].metric(series_map[sid], "N/A")

# Chart
st.subheader("Time series")
fig = px.line(
    plot_df,
    x="date",
    y="value",
    color="series_title",
    labels={"date": "Date", "value": "Value"},
)
st.plotly_chart(fig, use_container_width=True)

# Data table
with st.expander("Show underlying data"):
    st.dataframe(plot_df.sort_values(["series_title", "date"]), use_container_width=True)

st.caption(
    "Data sourced from the U.S. Bureau of Labor Statistics (BLS). "
    "Updated locally via API and visualized with Streamlit."
)
