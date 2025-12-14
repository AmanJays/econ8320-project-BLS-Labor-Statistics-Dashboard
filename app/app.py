import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.fetch_bls_data import OUTPUT_FILE
import os

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="U.S. Labor Statistics Dashboard")
st.title("🇺🇸 U.S. Labor Statistics Dashboard")

# --- Load Data ---
if not os.path.isfile(OUTPUT_FILE):
    st.warning("Data not found. Run `fetch_bls_data.py` first.")
    st.stop()

df = pd.read_csv(OUTPUT_FILE)
df['Date'] = pd.to_datetime(df['Date'])

# --- Sidebar Navigation ---
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Employment Stats", "Wage vs Inflation", "Hours & Pay"])

# --- Filter Date Range ---
min_date, max_date = df['Date'].min(), df['Date'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
df_filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]

# --- Charts ---
fig = go.Figure()

if page == "Employment Stats":
    st.header("💼 Employment & Unemployment")
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Employment Level'], name="Employment Level"))
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Unemployment Rate'], name="Unemployment Rate", yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Employment Level"),
        yaxis2=dict(title="Unemployment Rate", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )

elif page == "Wage vs Inflation":
    st.header("📈 Wage Growth vs Inflation")
    base_cpi = df_filtered['CPI'].iloc[0]
    df_filtered['Inflation'] = (df_filtered['CPI'] - base_cpi)/base_cpi * 100
    base_wage = df_filtered['Weekly Income'].iloc[0]
    df_filtered['Wage Growth'] = (df_filtered['Weekly Income'] - base_wage)/base_wage * 100
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Wage Growth'], name="Wage Growth"))
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Inflation'], name="Inflation"))
    fig.update_layout(yaxis=dict(title="Cumulative Growth (%)"), legend=dict(orientation="h"))

else:
    st.header("💵 Hours & Pay")
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Hourly Earnings'], name="Hourly Earnings"))
    fig.add_trace(go.Scatter(x=df_filtered['Date'], y=df_filtered['Hours Worked'], name="Hours Worked", yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Wage ($)"),
        yaxis2=dict(title="Hours Worked", overlaying="y", side="right"),
        legend=dict(orientation="h")
    )

st.plotly_chart(fig, use_container_width=True)

# --- Show Raw Data ---
with st.expander("View Raw Data"):
    st.dataframe(df_filtered)
