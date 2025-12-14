import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(
    page_title="U.S. Labor Market Dashboard",
    layout="wide"
)

st.title("🇺🇸 U.S. Labor Market Overview")

st.markdown(
    """
    This dashboard combines **short-run labor market conditions**
    (unemployment rate) with **long-run structural change**
    (manufacturing's share of employment).
    """
)

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/labor_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# --- Sidebar ---
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

df_plot = df.query("Date >= @start_date and Date <= @end_date").copy()

# --- Manufacturing Share ---
df_plot["Manufacturing Share (%)"] = (
    df_plot["Manufacturing Employment"]
    / df_plot["Total Nonfarm Payrolls"]
    * 100
)

# --- Metrics ---
start_unemp = df_plot.iloc[0]["Unemployment Rate"]
end_unemp = df_plot.iloc[-1]["Unemployment Rate"]

start_share = df_plot.iloc[0]["Manufacturing Share (%)"]
end_share = df_plot.iloc[-1]["Manufacturing Share (%)"]

col1, col2 = st.columns(2)

col1.metric(
    "Unemployment Rate (Latest)",
    f"{end_unemp:.1f}%",
    delta=f"{end_unemp - start_unemp:+.1f} pts"
)

col2.metric(
    "Manufacturing Share (Latest)",
    f"{end_share:.2f}%",
    delta=f"{end_share - start_share:+.2f} pts"
)

# --- Tabs ---
tab1, tab2 = st.tabs(["📉 Unemployment Rate", "🏭 Manufacturing Share"])

# --- Tab 1: Unemployment ---
with tab1:
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=df_plot["Date"],
            y=df_plot["Unemployment Rate"],
            mode="lines",
            name="Unemployment Rate"
        )
    )

    fig1.update_layout(
        yaxis_title="Unemployment Rate (%)",
        xaxis_title="Date",
        hovermode="x unified"
    )

    st.plotly_chart(fig1, use_container_width=True)

# --- Tab 2: Manufacturing Share ---
with tab2:
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=df_plot["Date"],
            y=df_plot["Manufacturing Share (%)"],
            mode="lines",
            name="Manufacturing Share"
        )
    )

    fig2.update_layout(
        yaxis_title="Share of Total Employment (%)",
        xaxis_title="Date",
        hovermode="x unified"
    )

    st.plotly_chart(fig2, use_container_width=True)

# --- Data ---
with st.expander("📄 View data"):
    st.dataframe(
        df_plot.style.format({
            "Date": "{:%b %Y}",
            "Unemployment Rate": "{:.1f}%",
            "Total Nonfarm Payrolls": "{:,.0f}",
            "Manufacturing Employment": "{:,.0f}",
            "Manufacturing Share (%)": "{:.2f}%"
        })
    )


#streamlit run app/app.py