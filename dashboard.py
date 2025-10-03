import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from preparer import (
    currentFundValue,
    fundAge,
    fundInception,
    fundPnLFiat,
    fundPnLPercentage,
    liveBitcoinPrice,
    preparedDf,
    totalBitcoinHeld,
    totalFiatCost,
)
from y1report import (
    y1annualReturn,
    y1bitcoinHeld,
    y1closingFundCost,
    y1closingFundValue,
    y1closingPrice,
    y1endDate,
)


st.set_page_config(
    page_title="MariaDB Bitcoin",
    layout="centered"
)

# -----------------------------
# Load environment variables
# -----------------------------
FUND_ADDRESS = st.secrets["FUND_ADDRESS"]

# -----------------------------
# CSS for badge
# -----------------------------
st.markdown(
    """
    <style>
    .fund-badge {
        display: inline-block;
        background-color: #89A2BC;  /* primary accent color */
        color: #05060B;              /* dark text on light badge */
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Header container
# -----------------------------
with st.container():
    st.markdown("## 🟠 MariaDB")

    st.markdown('<div class="fund-badge">Fund Address</div>', unsafe_allow_html=True)
    st.code(FUND_ADDRESS, language="text")

# -----------------------------
# Fund Overview container
# -----------------------------
with st.container():
    st.markdown("### Fund Overview")
    
    row1_col1, row1_col2 = st.columns(2, gap="medium")
    row1_col1.metric(
        label="BTC Held",
        value=f"{totalBitcoinHeld:.4f} BTC"
    )
    row1_col2.metric(
        label="Total Cost (CAD)",
        value=f"${totalFiatCost:,.2f}"
    )
    
    row2_col1, row2_col2 = st.columns(2, gap="medium")
    row2_col1.metric(
        label="Current Fund Value (CAD)",
        value=f"${currentFundValue:,.2f}"
    )
    row2_col2.metric(
        label="Live BTC Price (CAD)",
        value=f"${liveBitcoinPrice:,.2f}"
    )

# -----------------------------
# Fund Growth Over Time Container
# -----------------------------
with st.container():
    st.markdown("### Fund Growth Over Time")

    # Convert blockTime to datetime and sort
    preparedDf["blockDatetime"] = pd.to_datetime(preparedDf["blockTime"], unit="s")
    preparedDf = preparedDf.sort_values("blockDatetime")

    # Cumulative cost invested over time
    preparedDf["cumulativeCostCAD"] = preparedDf["costCAD"].cumsum()

    # Cumulative BTC held over time
    preparedDf["cumulativeBTC"] = preparedDf["btcValue"].cumsum()

    # Fund value over time using live BTC price
    preparedDf["fundValueCAD"] = preparedDf["cumulativeBTC"] * liveBitcoinPrice

    # Create Plotly figure
    fig = go.Figure()

    # Cumulative Cost line
    fig.add_trace(go.Scatter(
        x=preparedDf["blockDatetime"],
        y=preparedDf["cumulativeCostCAD"],
        mode="lines",
        name="Cumulative Cost (CAD)",
        line=dict(color="#ffffff", width=2)
    ))

    # Fund Value line
    fig.add_trace(go.Scatter(
        x=preparedDf["blockDatetime"],
        y=preparedDf["fundValueCAD"],
        mode="lines",
        name="Fund Value (CAD)",
        line=dict(color="#89A2BC", width=3)  # primary color for fund value
    ))

    # Shaded area between cost and fund value
    fig.add_trace(go.Scatter(
        x=pd.concat([preparedDf["blockDatetime"], preparedDf["blockDatetime"][::-1]]),
        y=pd.concat([preparedDf["fundValueCAD"], preparedDf["cumulativeCostCAD"][::-1]]),
        fill='toself',
        fillcolor='rgba(137, 162, 188, 0.2)',  # primary color with transparency
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    ))

    # Layout adjustments
    fig.update_layout(
        paper_bgcolor="#05060b",
        plot_bgcolor="#05060b",
        font=dict(color="#ffffff", family="sans-serif"),
        xaxis=dict(title="Date"),
        yaxis=dict(title="Value (CAD)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# Year 1 Performance Container
# -----------------------------
with st.container():
    st.markdown("### Year 1 Performance")

    y1_data = pd.DataFrame({
        "Metric": [
            "Year 1 End Date",
            "Bitcoin Closing Price",
            "Bitcoin Held",
            "Fund Value (CAD)",
            "Fund Cost (CAD)",
            "Annual Return"
        ],
        "Value": [
            y1endDate.strftime("%Y-%m-%d"),
            f"${y1closingPrice:,.2f}",
            f"{y1bitcoinHeld:.4f} BTC",
            f"${y1closingFundValue:,.2f}",
            f"${y1closingFundCost:,.2f}",
            f"{y1annualReturn:.2f}%"
        ]
    })

    st.dataframe(y1_data, hide_index=True)

# -----------------------------
# Fund History Container
# -----------------------------
with st.container():
    st.markdown("### Fund History")

    row1_col1, row1_col2 = st.columns(2, gap="medium")
    row1_col1.metric(
        label="Fund Inception",
        value=f"{fundInception}"
    )
    row1_col2.metric(
        label="Fund Age (days)",
        value=f"{fundAge}"
    )

    row2_col1, row2_col2 = st.columns(2, gap="medium")
    row2_col1.metric(
        label="Fund PnL (CAD)",
        value=f"${fundPnLFiat:,.2f}"
    )
    row2_col2.metric(
        label="Fund PnL (%)",
        value=f"{fundPnLPercentage:.2f}%"
    )