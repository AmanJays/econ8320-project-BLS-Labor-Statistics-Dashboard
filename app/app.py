# app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scripts.fetch_bls_data import collect_data # Import the collector

st.set_page_config(layout="wide", page_title="U.S. Labor Dashboard")
st.title("🇺🇸 U.S. Labor Statistics Dashboard — BLS")
st.markdown("---")

# --- 1. Load Data (uses cache/local file first) ---
# Use st.cache_data to speed up the dashboard after the initial run
@st.cache_data(ttl=3600, show_spinner="Loading and preparing labor data...")
def load_data():
    """Loads and preprocesses data for the dashboard."""
    df = collect_data()
    # Calculate global base CPI for consistent real wage adjustments
    if not df.empty:
        # Base CPI is the value from the oldest date in the entire dataset
        df = df.sort_values(by='Date')
        st.session_state['base_cpi_global'] = df["CPI"].iloc[0]
    return df

df = load_data()

if df.empty:
    st.error("Failed to load data. Please check the BLS API connection or 'data/data.csv'.")
    st.stop()

# --- 2. Sidebar Navigation and Filtering ---
st.sidebar.header("🧭 Navigation")
page = st.sidebar.radio("Select Page", ["Employment", "Wage & Inflation", "Work Hours & Pay"])
st.sidebar.markdown("---")
st.sidebar.header("📅 Timeframe")

min_date = df["Date"].min()
max_date = df["Date"].max()

start_date, end_date = st.sidebar.slider(
    "Date Range", 
    min_value=min_date.date(), 
    max_value=max_date.date(), 
    value=(min_date.date(), max_date.date()),
    format="YYYY-MM"
)

# Convert slider dates back to datetime objects
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date)

df_filtered = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)].copy()

# --- 3. Pre-Calculations for Metrics and Plots ---
if not df_filtered.empty:
    start_row = df_filtered.iloc[0]
    end_row = df_filtered.iloc[-1]
    
    # Cumulative Growth Calculations (relative to start_date in filter)
    base_cpi_filter = start_row["CPI"]
    base_income_filter = start_row["Weekly Income"]
    
    df_filtered["Inflation %"] = (df_filtered["CPI"] - base_cpi_filter) / base_cpi_filter * 100
    df_filtered["Wage Growth %"] = (df_filtered["Weekly Income"] - base_income_filter) / base_income_filter * 100
    
    # Real Wage Calculation (relative to constant global base)
    base_cpi_global = st.session_state['base_cpi_global']
    df_filtered['Real Hourly Earnings'] = (df_filtered["Hourly Earnings"] / df_filtered["CPI"]) * base_cpi_global

    # KPI Change Calculations (Start vs. End of Filter)
    def calc_change(start, end, is_rate=False):
        if is_rate:
            # Change in percentage points
            return round(end - start, 2)
        else:
            # Percentage change
            return round((end - start) / start * 100, 1)

    unemp_change = calc_change(start_row['Unemployment Rate'], end_row['Unemployment Rate'], is_rate=True)
    emp_change_k = round((end_row['Employment Level'] - start_row['Employment Level']) / 1000, 1) # In thousands
    
    cpi_change = calc_change(start_row['CPI'], end_row['CPI'])
    wage_change = calc_change(start_row['Weekly Income'], end_row['Weekly Income'])

    real_hourly_change = calc_change(start_row['Hourly Earnings'], end_row['Real Hourly Earnings'])
    
    
# --- 4. Dashboard Pages ---

if page == "Employment":
    st.subheader(f"Employment Metrics ({start_dt.strftime('%b %Y')} - {end_dt.strftime('%b %Y')})")
    k1, k2 = st.columns(2)
    k1.metric(
        "Employment Level (000s)", 
        f"{end_row['Employment Level']:,.0f}", 
        f"{emp_change_k:,.1f}k", 
        delta_color = 'normal'
    )
    k2.metric(
        "Unemployment Rate (%)", 
        f"{end_row['Unemployment Rate']:.1f}%", 
        f"{unemp_change:.2f} pp", 
        delta_color = 'inverse'
    )

    fig = go.Figure()
    # Employment Level (Left Axis)
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Employment Level"],
                             name="Employment Level", line=dict(color="blue"), yaxis="y"))
    # Unemployment Rate (Right Axis)
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Unemployment Rate"],
                             name="Unemployment Rate", line=dict(color="red"), yaxis="y2"))
    
    fig.update_layout(
        yaxis=dict(title="Employment Level (000s)"),
        yaxis2=dict(title="Unemployment Rate (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Raw Data"):
        st.dataframe(df_filtered[['Date', 'Employment Level', 'Unemployment Rate']].tail(12).style.format({'Date': "{:%b %Y}", "Employment Level": "{:,.0f}k", "Unemployment Rate": "{:.1f}%"}))

elif page == "Wage & Inflation":
    st.subheader(f"Wage Growth vs. Inflation ({start_dt.strftime('%b %Y')} - {end_dt.strftime('%b %Y')})")
    st.caption(f"Growth is calculated cumulatively relative to the start date: {start_dt.strftime('%b %Y')}")
    
    k1, k2 = st.columns(2)
    k1.metric("Weekly Income", f"${end_row['Weekly Income']:,.2f}", f"{wage_change:,.1f}%", delta_color = 'normal')
    k2.metric("CPI", f"{end_row['CPI']:.2f}", f"{cpi_change:,.1f}%", delta_color = 'inverse')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Wage Growth %"],
                             name="Wage Growth %", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Inflation %"],
                             name="Inflation %", line=dict(color="orange")))
    
    fig.update_layout(yaxis=dict(title="Cumulative Growth (%)"), 
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("View Raw Data"):
        st.dataframe(df_filtered[['Date', 'Weekly Income', 'Wage Growth %', 'CPI', 'Inflation %']].tail(12).style.format({'Date': "{:%b %Y}", 'Weekly Income': "${:,.2f}", 'Wage Growth %': "{:.1f}%", 'CPI': "{:.2f}", 'Inflation %': "{:.1f}%"}))


elif page == "Work Hours & Pay":
    st.subheader(f"Work Hours, Nominal & Real Pay ({start_dt.strftime('%b %Y')} - {end_dt.strftime('%b %Y')})")
    st.caption(f"Real Hourly Earnings are adjusted for inflation based on the CPI from {df['Date'].min().strftime('%b %Y')}.")

    k1, k2 = st.columns(2)
    k1.metric("Nominal Hourly Earnings", f"${end_row['Hourly Earnings']:,.2f}", f"{calc_change(start_row['Hourly Earnings'], end_row['Hourly Earnings']):,.1f}%", delta_color = 'normal')
    k2.metric("Real Hourly Earnings", f"${end_row['Real Hourly Earnings']:,.2f}", f"{real_hourly_change:,.1f}%", delta_color = 'normal')

    fig = go.Figure()
    # Nominal and Real Hourly Earnings (Left Axis)
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Hourly Earnings"],
                             name="Nominal Earnings", line=dict(color="hotpink"), yaxis="y"))
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Real Hourly Earnings"],
                             name="Real Earnings", line=dict(color="purple"), yaxis="y"))

    # Hours Worked (Right Axis)
    fig.add_trace(go.Scatter(x=df_filtered["Date"], y=df_filtered["Hours Worked"],
                             name="Hours Worked", line=dict(color="gold"), yaxis="y2"))
    
    fig.update_layout(
        yaxis=dict(title="Earnings ($)"),
        yaxis2=dict(title="Weekly Hours", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Raw Data"):
        st.dataframe(df_filtered[['Date', 'Hourly Earnings', 'Real Hourly Earnings', 'Hours Worked']].tail(12).style.format({'Date': "{:%b %Y}", 'Hourly Earnings': "${:,.2f}", 'Real Hourly Earnings': "${:,.2f}", 'Hours Worked': "{:.1f}"}))
