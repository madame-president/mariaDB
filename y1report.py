from datetime import datetime, timedelta

import pandas as pd

from preparer import (
    preparedDf, 
    oldestBlockTime, 
    fundInception,
)

# -----------------------------
# FUND INCEPTION & YEAR 1 END DATE
# -----------------------------
fundInceptionDate = datetime.utcfromtimestamp(oldestBlockTime)
y1endDate = fundInceptionDate + timedelta(days=365)

# -----------------------------
# PREPARE DATA FOR YEAR 1
# -----------------------------
# Convert blockTime to datetime
preparedDf["blockDatetime"] = pd.to_datetime(preparedDf["blockTime"], unit="s")

# Filter transactions up to year 1 end date
y1Df = preparedDf[preparedDf["blockDatetime"] <= y1endDate]

# -----------------------------
# YEAR 1 METRICS
# -----------------------------
y1bitcoinHeld = y1Df["btcValue"].sum()
y1closingPrice = 120548  # fixed price: must be added manually for every year
y1closingFundValue = y1bitcoinHeld * y1closingPrice
y1closingFundCost = y1Df["costCAD"].sum()
y1annualReturn = ((y1closingFundValue - y1closingFundCost) / y1closingFundCost) * 100 if y1closingFundCost != 0 else 0

# -----------------------------
# PRINT RESULTS
# -----------------------------
# print(f"Fund inception: {fundInception}")
# print(f"Year 1 end date: {y1endDate.strftime('%Y-%m-%d')}")
# print(f"Year 1 BTC held: {y1bitcoinHeld}")
# print(f"Year 1 closing price: {y1closingPrice}")
# print(f"Year 1 closing fund value: {y1closingFundValue}")
# print(f"Year 1 closing fund cost: {y1closingFundCost}")
# print(f"Year 1 annual return (%): {y1annualReturn:.2f}%")