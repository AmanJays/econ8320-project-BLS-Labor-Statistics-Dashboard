import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

# --- Page Setup ---
st.set_page_config(
    page_title="U.S. Unemployment Rate",
    layout="wide"
)

st.title("🇺🇸 U.S. Unemployment Rate Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/unemployment.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# --- Sidebar: Date Filter ---
st.sidebar.header("📅 Timeframe")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

start_date, end_date = st.sidebar.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="MMM YYYY"
)

df_plot = df.query("Date >= @start_date and Date <= @end_date")

start_rate = df_plot.iloc[0]["Unemployment Rate"]
end_rate = df_plot.iloc[-1]["Unemployment Rate"]
change = round(end_rate - start_rate, 2)

# --- Metrics ---
col1, col2 = st.columns(2)

col1.metric(
    "Current Unemployment Rate",
    f"{end_rate:.1f}%",
    delta=f"{change:+.1f} pts"
)

col2.metric(
    "Time Period",
    f"{start_date:%b %Y} – {end_date:%b %Y}"
)

# --- Line Chart ---
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_plot["Date"],
        y=df_plot["Unemployment Rate"],
        mode="lines",
        name="Unemployment Rate"
    )
)

fig.update_layout(
    yaxis_title="Unemployment Rate (%)",
    xaxis_title="Date",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# --- Data Table ---
with st.expander("📄 View raw data"):
    st.dataframe(
        df_plot.style.format({
            "Date": "{:%b %Y}",
            "Unemployment Rate": "{:.1f}%"
        })
    )

#streamlit run app/app.py