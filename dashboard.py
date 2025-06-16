import streamlit as st
import sqlite3
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(page_title="MariaDB | Bitcoin", layout="wide")

st_autorefresh(interval=120 * 1000, limit=None, key="refresh")

st.title("🟠 MariaDB")

def getLivePrice():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "cad"
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        return res.json()["bitcoin"]["cad"]
    except Exception as e:
        st.warning(f"Request error: {e}")
        return None

livePrice = getLivePrice()
satCAD = livePrice / 100_000_000 if livePrice else None
    

# Connect and load data
conn = sqlite3.connect("transactions.db")
df = pd.read_sql_query("SELECT date, cost, amount FROM transactions", conn)
conn.close()

df['cost per sat'] = df['cost'] / df['amount']
df['transaction PnL'] = ((satCAD - df['cost per sat'])/ df['cost per sat'])
df['current transaction $'] = satCAD * df['amount']
df['interest'] = df['current transaction $'] - df['cost']
totalPnl = (df['transaction PnL'].mean().round(2)) * 100
totalCost = df['cost'].sum()
totalCurrentValue = df['current transaction $'].sum().round(2)
totalInterest = df['interest'].sum().round(2)

col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 3])
with col1:
    st.metric(label="Bitcoin Price", value=f"${livePrice:,}")
with col2:
    st.metric(label="Sat/CAD", value=f"${satCAD}")
with col3:
    st.metric(label="Total PnL", value=f"{totalPnl}%")
with col4:
    st.metric(label="Total Cost", value=f"${totalCost:,}")
with col5:
    st.metric(label="Current Value", value=f"${totalCurrentValue:,}")
with col6:
    st.metric(label="Total Interest", value=f"${totalInterest:,}")
with col7:
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Display the data
st.dataframe(df, use_container_width=True)