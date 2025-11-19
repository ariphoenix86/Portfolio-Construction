import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# --- PostgreSQL Connection ---
conn = psycopg2.connect(
    host="localhost",             # Change if hosted elsewhere
    database="etf_sandbox",       # Replace with your actual DB name
    user="postgres",              # Replace with your DB username
    password="Cleopatra@12"       # Your provided password
)

# --- Load Data ---
etfs = pd.read_sql("SELECT * FROM etfs", conn)
returns = pd.read_sql("SELECT * FROM etf_monthly_returns", conn)

# --- Merge for visuals ---
merged = returns.merge(etfs, on="etf_id")

# --- Streamlit UI ---
st.title("📊 ETF Performance Dashboard")

# ETF Selector
selected_etfs = st.multiselect("Select ETFs", etfs["etf_name"].unique(), default=etfs["etf_name"].unique())

filtered = merged[merged["etf_name"].isin(selected_etfs)]

# --- Monthly Return Trend ---
fig1 = px.line(filtered, x="date", y="monthly_return", color="etf_name", title="Monthly Return Trend")
st.plotly_chart(fig1)

# --- Rolling 12-Month Return ---
returns["Rolling12MReturn"] = returns.groupby("etf_id")["monthly_return"].transform(lambda x: x.rolling(12).sum())
rolling = returns.merge(etfs, on="etf_id")
rolling = rolling[rolling["etf_name"].isin(selected_etfs)]
fig2 = px.line(rolling, x="date", y="Rolling12MReturn", color="etf_name", title="Rolling 12-Month Return")
st.plotly_chart(fig2)

# --- Volatility by ETF ---
vol_df = filtered.groupby("etf_name")["monthly_return"].std().reset_index()
fig3 = px.bar(vol_df, x="etf_name", y="monthly_return", title="Volatility by ETF")
st.plotly_chart(fig3)

# --- Cumulative Return ---
filtered["CumulativeReturn"] = filtered.groupby("etf_id")["monthly_return"].cumsum()
fig4 = px.line(filtered, x="date", y="CumulativeReturn", color="etf_name", title="Cumulative Return Since Inception")
st.plotly_chart(fig4)