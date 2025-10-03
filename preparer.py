from datetime import datetime

import pandas as pd

from loader import (
    getTransactions, 
    getAllPrices, 
    currentPrice,
)

# -----------------------------
# FETCH DATA
# -----------------------------
transactionsDf = getTransactions()
pricesDf = getAllPrices()

# Merge transactions and prices
preparedDf = transactionsDf.merge(pricesDf, on="blockTime", how="left")
preparedDf["costCAD"] = preparedDf["btcValue"] * preparedDf["priceCAD"]
preparedDf = preparedDf.sort_values("blockTime", ascending=False)  # newest first

# -----------------------------
# LIVE PRICE
# -----------------------------
liveBitcoinPrice = currentPrice()

# -----------------------------
# AGGREGATED CALCULATIONS
# -----------------------------
totalBitcoinHeld = preparedDf["btcValue"].sum()
totalFiatCost = preparedDf["costCAD"].sum()
currentFundValue = totalBitcoinHeld * liveBitcoinPrice

# -----------------------------
# NEW METRICS
# -----------------------------
# Fund inception = oldest transaction
oldestBlockTime = preparedDf["blockTime"].min()
fundInception = datetime.utcfromtimestamp(oldestBlockTime).strftime("%Y-%m-%d")

# Fund age in days
today = datetime.utcnow()
fundAge = (today - datetime.utcfromtimestamp(oldestBlockTime)).days

# Fund PnL
fundPnLFiat = currentFundValue - totalFiatCost
fundPnLPercentage = (fundPnLFiat / totalFiatCost) * 100 if totalFiatCost != 0 else 0