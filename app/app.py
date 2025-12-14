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

# --- Helper Function: Trend Arrows ---
def format_metric(value, delta):
    """Return formatted value with arrow; delta_color compatible with Streamlit"""
    arrow = "🔼" if delta > 0 else ("🔽" if delta < 0 else "")
    delta_color = "normal"  # Streamlit automatically handles green/red
    return f"{value} {arrow}", delta_color

# --- Tabs ---
tabs = st.tabs(["💼 Employment", "📈 Wage vs Inflation", "💵 Work Hours & Pay"])

# --- Tab 1: Employment ---
with tabs[0]:
    st.subheader(f"💼 Employment Statistics ({start_date:%b %Y} – {end_date:%b %Y})")
    emp_growth = end_row['Employment Level'] - start_row['Employment Level']
    unemp_change = end_row['Unemployment Rate'] - start_row['Unemployment Rate']

    emp_val, emp_color = format_metric(f"{round(end_row['Employment Level']/1000,1):,}M", emp_growth)
    unemp_val, unemp_color = format_metric(f"{end_row['Unemployment Rate']}%", unemp_change)

    col1, col2 = st.columns(2)
    col1.metric("Employment Level", emp_val, delta_color=emp_color)
    col2.metric("Unemployment Rate", unemp_val, delta_color=unemp_color)

    selection = st.multiselect("Select metrics", ["Employment Level", "Unemployment Rate"],
                               default=["Employment Level", "Unemployment Rate"])

    fig = go.Figure()
    if "Employment Level" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Employment Level'], name='Employment Level', line=dict(color='blue')))
    if "Unemployment Rate" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Unemployment Rate'], name='Unemployment Rate', line=dict(color='red'), yaxis='y2'))

    fig.update_layout(
        yaxis=dict(title="Employment Level (000s)"),
        yaxis2=dict(title="Unemployment Rate (%)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.02, x=1, xanchor='right'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 View Raw Data"):
        st.dataframe(df_plot[['Date', 'Employment Level', 'Unemployment Rate']].style.format({
            'Date': "{:%b %Y}",
            'Employment Level': "{:,.0f}",
            'Unemployment Rate': "{:.1f}%"
        }))

# --- Tab 2: Wage vs Inflation ---
with tabs[1]:
    st.subheader(f"📈 Wage Growth vs Inflation ({start_date:%b %Y} – {end_date:%b %Y})")
    wage_growth_val = round((end_row['Weekly Income'] - start_row['Weekly Income']) / start_row['Weekly Income'] * 100, 1)
    cpi_change_val = round((end_row['CPI'] - start_row['CPI']) / start_row['CPI'] * 100, 1)

    wage_val, wage_color = format_metric(f"${end_row['Weekly Income']:,}", wage_growth_val)
    cpi_val, cpi_color = format_metric(f"{end_row['CPI']}", cpi_change_val)

    col1, col2 = st.columns(2)
    col1.metric("Weekly Income", wage_val, delta_color=wage_color)
    col2.metric("CPI", cpi_val, delta_color=cpi_color)

    selection = st.multiselect("Select metrics", ["Wage Growth", "Inflation"], default=["Wage Growth", "Inflation"])

    fig = go.Figure()
    if "Wage Growth" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Wage Growth'], name='Wage Growth', line=dict(color='green'), hovertemplate='%{y:.1f}%'))
    if "Inflation" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Inflation'], name='Inflation', line=dict(color='orange'), hovertemplate='%{y:.1f}%'))

    fig.update_layout(yaxis=dict(title="Cumulative Growth (%)"), legend=dict(orientation="h", y=1.02, x=1, xanchor='right'), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 View Raw Data"):
        st.dataframe(df_plot[['Date', 'Weekly Income', 'Wage Growth', 'CPI', 'Inflation']].style.format({
            'Date': "{:%b %Y}",
            'Weekly Income': "${:,.1f}",
            'Wage Growth': "{:.1f}%",
            'CPI': "{:.1f}",
            'Inflation': "{:.1f}%"
        }))

# --- Tab 3: Work Hours & Pay ---
with tabs[2]:
    st.subheader(f"💵 Work Hours & Pay ({start_date:%b %Y} – {end_date:%b %Y})")
    hr_growth_val = round((end_row["Hourly Earnings"] - start_row["Hourly Earnings"]) / start_row["Hourly Earnings"] * 100 , 1)
    adjhr_val = round(end_row["Hourly Earnings"] / end_row["CPI"] * start_row["CPI"], 2)
    adjhr_growth_val = round((adjhr_val - start_row["Hourly Earnings"]) / start_row["Hourly Earnings"] * 100, 1)

    hr_val, hr_color = format_metric(f"${end_row['Hourly Earnings']:,}", hr_growth_val)
    adj_val, adj_color = format_metric(f"${adjhr_val:,}", adjhr_growth_val)

    col1, col2 = st.columns(2)
    col1.metric("Hourly Earnings", hr_val, delta_color=hr_color)
    col2.metric("Adj. Hourly Earnings", adj_val, delta_color=adj_color)

    selection = st.multiselect("Select metrics", ["Hourly Earnings", "Adj. Hourly Earnings", "Hours Worked"],
                               default=["Hourly Earnings", "Adj. Hourly Earnings", "Hours Worked"])

    fig = go.Figure()
    if "Hourly Earnings" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Hourly Earnings'], name='Hourly Earnings', line=dict(color='hotpink'), yaxis='y'))
    if "Adj. Hourly Earnings" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Adj Hourly Earnings'], name='Adj. Hourly Earnings', line=dict(color='purple'), yaxis='y'))
    if "Hours Worked" in selection:
        fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Hours Worked'], name='Hours Worked', line=dict(color='gold'), yaxis='y2'))

    fig.update_layout(
        yaxis=dict(title="Wage ($)"),
        yaxis2=dict(title="Weekly Hours", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.02, x=1, xanchor='right'),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 View Raw Data"):
        st.dataframe(df_plot[['Date', 'Hourly Earnings', 'Adj Hourly Earnings', 'Hours Worked']].style.format({
            'Date': "{:%b %Y}",
            'Hourly Earnings': "${:.1f}",
            'Adj Hourly Earnings': "${:.1f}",
            'Hours Worked': "{:.1f}"
        }))
#streamlit run app/app.py