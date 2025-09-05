
from __future__ import annotations
import datetime as dt
import pandas as pd
# import yfinance as yf

'''
Fetch historical stock price data using yfinance.
'''

def fetch_price_df(ticker: str, date_from: dt.date, date_to: dt.date) -> pd.DataFrame:
    """
    Download daily adjusted OHLCV for [date_from, date_to] inclusive.
    Returns index 'date' with columns: Open, High, Low, Close, Adj Close, Volume.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("ticker must be a non-empty string")

    end_plus_one = date_to + dt.timedelta(days=1)  # yfinance end is exclusive
    df = yf.download(
        tickers=ticker.strip(),
        start=date_from.isoformat(),
        end=end_plus_one.isoformat(),
        interval="1d",
        auto_adjust=True,   # Close is adjusted
        progress=False,
    )
    if df.empty:
        return df
    df = df.reset_index().rename(columns={"Date": "date"}).set_index("date")
    return df
