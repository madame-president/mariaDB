import os
import sqlite3

import pandas as pd
import requests
import streamlit as st


FUND_ADDRESS = st.secrets["FUND_ADDRESS"]
TX_API_URL = st.secrets["TX_API_URL"]
TX_API_PARAM = f"{TX_API_URL}/{FUND_ADDRESS}/txs"
HISTORICAL_PRICE_API_URL = st.secrets["HISTORICAL_PRICE_API_URL"]
LIVE_PRICE_API_URL = st.secrets["LIVE_PRICE_API_URL"]
TX_STORAGE = st.secrets["TX_STORAGE"]
PRICE_STORAGE = st.secrets["PRICE_STORAGE"]


# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def initializeDatabases():
    """Create necessary tables if they don't exist."""
    # Transactions DB
    with sqlite3.connect(TX_STORAGE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                txid TEXT PRIMARY KEY,
                blockHeight INTEGER,
                blockTime INTEGER,
                btcValue REAL
            )
        """)
    # Prices DB
    with sqlite3.connect(PRICE_STORAGE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                blockTime INTEGER PRIMARY KEY,
                priceCAD REAL
            )
        """)


# -----------------------------
# TRANSACTIONS FUNCTIONS
# -----------------------------
def getSeenTransactions():
    with sqlite3.connect(TX_STORAGE) as conn:
        return set(r[0] for r in conn.execute("SELECT txid FROM transactions"))


def getNewTransactions(seenTransactions):
    response = requests.get(TX_API_PARAM)
    if response.status_code != 200:
        raise Exception(f"[ERROR] Transaction request failed {response.status_code}: {response.text}")
    transactionData = response.json()
    return [tx for tx in transactionData if tx["txid"] not in seenTransactions]


def parseTransactions(newTransactions):
    parsed = []
    for tx in newTransactions:
        txid = tx["txid"]
        status = tx.get("status", {})
        blockHeight = status.get("block_height")
        blockTime = status.get("block_time")
        if not blockHeight or not blockTime:
            continue
        btcValue = sum(
            vout["value"]
            for vout in tx.get("vout", [])
            if vout.get("scriptpubkey_address") == FUND_ADDRESS
        ) / 1e8
        parsed.append((txid, blockHeight, blockTime, btcValue))
    return parsed


def insertTransactions(parsedTransactions):
    if not parsedTransactions:
        return
    with sqlite3.connect(TX_STORAGE) as conn:
        conn.executemany(
            "INSERT INTO transactions (txid, blockHeight, blockTime, btcValue) VALUES (?, ?, ?, ?)",
            parsedTransactions
        )


def getTransactions():
    """Fetch transactions, store new ones, and return as DataFrame."""
    initializeDatabases()
    seen = getSeenTransactions()
    newTx = getNewTransactions(seen)
    parsed = parseTransactions(newTx)
    insertTransactions(parsed)

    with sqlite3.connect(TX_STORAGE) as conn:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY blockTime DESC", conn)
    return df


# -----------------------------
# HISTORICAL PRICES FUNCTIONS
# -----------------------------
def getCachedPrice(blockTime):
    with sqlite3.connect(PRICE_STORAGE) as conn:
        row = conn.execute("SELECT priceCAD FROM prices WHERE blockTime = ?", (blockTime,)).fetchone()
    return row[0] if row else None


def fetchHistoricalPriceFromAPI(blockTime):
    """Fetch price from external API (no caching)."""
    url = f"{HISTORICAL_PRICE_API_URL}?currency=CAD&timestamp={blockTime}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"[ERROR] Historical price request failed {response.status_code}: {response.text}")
    try:
        return response.json()["prices"][0]["CAD"]
    except Exception as e:
        raise Exception(f"[ERROR] Failed to parse historical price: {e}")


def insertPrice(blockTime, priceCAD):
    with sqlite3.connect(PRICE_STORAGE) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO prices (blockTime, priceCAD) VALUES (?, ?)",
            (blockTime, priceCAD)
        )


def getHistoricalPrice(blockTime):
    """Return cached price or fetch from API if not cached."""
    cached = getCachedPrice(blockTime)
    if cached is not None:
        return cached
    priceCAD = fetchHistoricalPriceFromAPI(blockTime)
    insertPrice(blockTime, priceCAD)
    return priceCAD


def getAllPrices():
    """Fetch all historical prices for existing transactions."""
    initializeDatabases()
    transactionsDf = getTransactions()
    for blockTime in transactionsDf["blockTime"]:
        getHistoricalPrice(blockTime)
    with sqlite3.connect(PRICE_STORAGE) as conn:
        df = pd.read_sql_query("SELECT * FROM prices ORDER BY blockTime DESC", conn)
    return df

def currentPrice():
    currentPriceResponse = requests.get(LIVE_PRICE_API_URL)
    return currentPriceResponse.json()["CAD"]