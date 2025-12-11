import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Load Data ----
data_path = "data/bls_data.csv"
data = pd.read_csv(data_path)

# ---- Fix year_month column ----
if 'year' in data.columns and 'period' in data.columns:
    data['year_month'] = pd.to_datetime(
        data['year'].astype(str) + '-' + data['period'].astype(str).str.zfill(2)
    )
elif 'year' in data.columns and 'month' in data.columns:
    data['year_month'] = pd.to_datetime(
        data['year'].astype(str) + '-' + data['month'].astype(str).str.zfill(2)
    )
else:
    st.error("CSV does not have recognizable year/month columns. Please include 'year' and 'period' or 'month'.")
    st.stop()

# ---- Streamlit UI ----
st.title("US Labor Statistics Dashboard")
st.markdown("Data range: 2020-01 → 2025-09")

# Sidebar - select series
series_options = {
    "Total Nonfarm Payrolls": "CES0000000001",
    "Avg Hourly Earnings, Total Private": "CES0500000003",
    "Manufacturing Employment": "CES3000000001",
    "Labor Force Participation Rate": "LNS11300000"
}

selected_series = st.sidebar.multiselect(
    "Choose series to display", options=list(series_options.keys()), default=list(series_options.keys())
)

# Filter data
filtered_data = data[data['series_id'].isin([series_options[s] for s in selected_series])]

# Pivot to have series as columns
df_pivot = filtered_data.pivot(index='year_month', columns='series_id', values='value')
df_pivot = df_pivot.rename(columns={v: k for k, v in series_options.items()})

# ---- Display latest values ----
st.subheader("Latest values")
latest = df_pivot.iloc[-1]
for name, val in latest.items():
    st.write(f"**{name}:** {val}")

# ---- Plot time series ----
st.subheader("Time Series")
fig = px.line(df_pivot, x=df_pivot.index, y=df_pivot.columns, markers=True)
fig.update_layout(xaxis_title="Date", yaxis_title="Value")
st.plotly_chart(fig, use_container_width=True)

# ---- Show underlying data ----
with st.expander("Show underlying data"):
    st.dataframe(filtered_data)
