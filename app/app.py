import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# --------------------------------------------------
# Page Setup
# --------------------------------------------------
st.set_page_config(
    page_title="U.S. Labor Market Dashboard",
    layout="wide"
)

st.title("🇺🇸 U.S. Labor Market Overview")

st.markdown(
    """
    This dashboard combines **short-run labor market conditions**
    (unemployment rate) with **long-run structural change**
    (manufacturing’s share of employment).
    """
)

# --------------------------------------------------
# Helper Function: Trend Emoji
# --------------------------------------------------
def trend_emoji(value):
    if value > 0:
        return "🔼"
    elif value < 0:
        return "🔽"
    else:
        return "➖"

# --------------------------------------------------
# Load Data
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/labor_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df["Year"] = df["Date"].dt.year
    return df

df = load_data()

# --------------------------------------------------
# Sidebar: Year Selection
# --------------------------------------------------
st.sidebar.header("📅 Select Time Period")

years = sorted(df["Year"].unique())

start_year = st.sidebar.selectbox("Start Year", years, index=0)
end_year = st.sidebar.selectbox("End Year", years, index=len(years) - 1)

if start_year > end_year:
    st.sidebar.error("Start year must be before end year.")

df_plot = df.query("Year >= @start_year and Year <= @end_year").copy()

# --------------------------------------------------
# Calculations
# --------------------------------------------------
# Manufacturing Share
df_plot["Manufacturing Share (%)"] = (
    df_plot["Manufacturing Employment"]
    / df_plot["Total Nonfarm Payrolls"]
    * 100
)

# Unemployment change
start_unemp = df_plot.iloc[0]["Unemployment Rate"]
end_unemp = df_plot.iloc[-1]["Unemployment Rate"]
unemp_change = end_unemp - start_unemp

# Manufacturing share change
start_share = df_plot.iloc[0]["Manufacturing Share (%)"]
end_share = df_plot.iloc[-1]["Manufacturing Share (%)"]
share_change = end_share - start_share

# --------------------------------------------------
# Metrics
# --------------------------------------------------
col1, col2 = st.columns(2)

col1.metric(
    "Change in Unemployment Rate",
    f"{unemp_change:+.2f} percentage points {trend_emoji(unemp_change)}"
)

col2.metric(
    "Change in Manufacturing Employment Share",
    f"{share_change:+.2f} percentage points {trend_emoji(share_change)}"
)

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab1, tab2 = st.tabs(["📉 Unemployment Rate", "🏭 Manufacturing Share"])

# --------------------------------------------------
# Tab 1: Unemployment Rate
# --------------------------------------------------
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

# --------------------------------------------------
# Tab 2: Manufacturing Share
# --------------------------------------------------
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

    # Formula (work shown)
    st.latex(
        r"""
        \text{Manufacturing Share (\%)} =
        \frac{\text{Manufacturing Employment}}
        {\text{Total Nonfarm Payrolls}}
        \times 100
        """
    )

# --------------------------------------------------
# Data Table
# --------------------------------------------------
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