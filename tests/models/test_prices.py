import os, sys
import datetime as dt
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.models.prices import fetch_price_df


def test_fetch_price_df_basic():
    """Fetches a few days of TSLA and ensures OHLCV data is returned."""
    ticker = "TSLA"
    end = dt.date.today()
    start = end - dt.timedelta(days=7)

    df = fetch_price_df(ticker, start, end)

    # Print out a preview so we can inspect in pytest -s
    print("\n=== Price Data (TSLA) ===")
    if df is not None and not df.empty:
        print(df.head().to_string())
    else:
        print("No data returned.")

    # Assert DataFrame is returned
    assert df is not None, "No DataFrame returned"
    assert hasattr(df, "columns"), "Return is not a DataFrame"

    # If empty, skip instead of failing (sometimes Yahoo returns empty temporarily)
    if df.empty:
        pytest.skip("Yahoo returned empty data (likely transient)")

    # Check expected columns
    expected_cols = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
    assert expected_cols.issubset(set(df.columns)), f"Missing columns: {expected_cols - set(df.columns)}"

    # Ensure we got at least 1 row
    assert len(df) > 0, "No rows of price data returned"
