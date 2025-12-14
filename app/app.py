import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import os

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="US Labor Dashboard")
st.title("🇺🇸 U.S. Labor Statistics Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# --- Sidebar: Timeframe ---
st.sidebar.header("📅 Timeframe")
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
start_date, end_date = st.sidebar.slider(
    "Select Timeframe",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="MMM YYYY"
)
start_date = start_date.replace(day=1)

# Reset slider button
if st.sidebar.button("🔄 Reset Timeframe"):
    start_date, end_date = min_date, max_date

# Last updated
file_timestamp = os.path.getmtime("data/data.csv")
updated_time = pd.to_datetime(file_timestamp, unit='s', utc=True).tz_convert('US/Central')
st.sidebar.caption(f"Last updated: {updated_time.strftime('%b %d, %Y %I:%M %p')}")

# --- Filter Data ---
df_plot = df.query("Date >= @start_date and Date <= @end_date").copy()
start_row, end_row = df_plot.iloc[0], df_plot.iloc[-1]

# --- Calculated Columns ---
df_plot['Inflation'] = (df_plot["CPI"] - start_row["CPI"]) / start_row["CPI"] * 100
df_plot['Wage Growth'] = (df_plot["Weekly Income"] - start_row["Weekly Income"]) / start_row["Weekly Income"] * 100
df_plot['Adj Hourly Earnings'] = round(df_plot["Hourly Earnings"] / df_plot["CPI"] * start_row["CPI"], 2)

# --- Tabs ---
tabs = st.tabs(["💼 Employment", "📈 Wage vs Inflation", "💵 Work Hours & Pay"])

# --- Tab 1: Employment ---
with tabs[0]:
    st.subheader(f"💼 Employment Statistics ({start_date:%b %Y} – {end_date:%b %Y})")
    emp_growth = end_row['Employment Level'] - start_row['Employment Level']
    unemp_change = end_row['Unemployment Rate'] - start_row['Unemployment Rate']

    col1, col2 = st.columns(2)
    col1.metric("Employment Level", f"{round(end_row['Employment Level']/1000,1):,}M", f"{emp_growth:,}k")
    col2.metric("Unemployment Rate", f"{end_row['Unemployment Rate']}%", f"{unemp_change:+.2f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Employment Level'], name='Employment Level', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Unemployment Rate'], name='Unemployment Rate', line=dict(color='red'), yaxis='y2'))
    fig.update_layout(
        yaxis=dict(title="Employment Level (000s)"),
        yaxis2=dict(title="Unemployment Rate (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.02, x=1, xanchor='right'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Wage vs Inflation ---
with tabs[1]:
    st.subheader(f"📈 Wage Growth vs Inflation ({start_date:%b %Y} – {end_date:%b %Y})")
    wage_growth = round((end_row['Weekly Income'] - start_row['Weekly Income']) / start_row['Weekly Income'] * 100, 1)
    cpi_change = round((end_row['CPI'] - start_row['CPI']) / start_row['CPI'] * 100, 1)

    col1, col2 = st.columns(2)
    col1.metric("Weekly Income", f"${end_row['Weekly Income']:,}", f"{wage_growth:+.1f}%")
    col2.metric("CPI", f"{end_row['CPI']}", f"{cpi_change:+.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Wage Growth'], name='Wage Growth', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Inflation'], name='Inflation', line=dict(color='orange')))
    fig.update_layout(yaxis=dict(title="Cumulative Growth (%)"), legend=dict(orientation="h", y=1.02, x=1, xanchor='right'), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 3: Work Hours & Pay ---
with tabs[2]:
    st.subheader(f"💵 Work Hours & Pay ({start_date:%b %Y} – {end_date:%b %Y})")
    hr_growth = round((end_row["Hourly Earnings"] - start_row["Hourly Earnings"]) / start_row["Hourly Earnings"] * 100 , 1)
    adjhr = round(end_row["Hourly Earnings"] / end_row["CPI"] * start_row["CPI"], 2)
    adjhr_growth = round((adjhr - start_row["Hourly Earnings"]) / start_row["Hourly Earnings"] * 100, 1)

    col1, col2 = st.columns(2)
    col1.metric("Hourly Earnings", f"${end_row['Hourly Earnings']:,}", f"{hr_growth:+.1f}%")
    col2.metric("Adj. Hourly Earnings", f"${adjhr:,}", f"{adjhr_growth:+.1f}%")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Hourly Earnings'], name='Hourly Earnings', line=dict(color='hotpink'), yaxis='y'))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Adj Hourly Earnings'], name='Adj Hourly Earnings', line=dict(color='purple'), yaxis='y'))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Hours Worked'], name='Hours Worked', line=dict(color='gold'), yaxis='y2'))
    fig.update_layout(
        yaxis=dict(title="Wage ($)"),
        yaxis2=dict(title="Weekly Hours", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.02, x=1, xanchor='right'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
