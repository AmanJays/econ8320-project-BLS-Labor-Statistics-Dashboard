import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.fetch_bls_data import collect_data

st.set_page_config(layout="wide", page_title="U.S. Labor Dashboard")
st.title("🇺🇸 U.S. Labor Statistics Dashboard")

# Load data
df = collect_data()

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Select Page", ["Employment", "Wage & Inflation", "Work Hours"])

# Date range filter
min_date = df["Date"].min()
max_date = df["Date"].max()
start_date, end_date = st.sidebar.slider(
    "Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date)
)
df_filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()

# Metrics
if page == "Employment":
    st.subheader("Employment Metrics")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Employment Level"],
                             name="Employment Level", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Unemployment Rate"],
                             name="Unemployment Rate", line=dict(color="red"), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Employment Level"),
        yaxis2=dict(title="Unemployment Rate (%)", overlaying="y", side="right"),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Wage & Inflation":
    st.subheader("Wage Growth vs Inflation")
    base_cpi = df_filtered["CPI"].iloc[0]
    base_income = df_filtered["Weekly Income"].iloc[0]
    df_filtered["Inflation %"] = (df_filtered["CPI"] - base_cpi)/base_cpi*100
    df_filtered["Wage Growth %"] = (df_filtered["Weekly Income"] - base_income)/base_income*100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Wage Growth %"],
                             name="Wage Growth %", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Inflation %"],
                             name="Inflation %", line=dict(color="orange")))
    fig.update_layout(yaxis=dict(title="Cumulative Growth %"), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Work Hours":
    st.subheader("Work Hours & Pay")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Hourly Earnings"],
                             name="Hourly Earnings", line=dict(color="pink")))
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Hours Worked"],
                             name="Hours Worked", line=dict(color="gold"), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Hourly Earnings ($)"),
        yaxis2=dict(title="Hours Worked", overlaying="y", side="right"),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
