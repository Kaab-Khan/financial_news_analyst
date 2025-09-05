import pytest
import os
import csv
import pathlib
from src.agent.us_resolver import (
    _norm,
    _load_rows,
    _build_index,
    resolve_us_ticker_basic,
)

# Path to your actual CSV file
ACTUAL_CSV_PATH = os.getenv("ticker_us", "resources/tickers_us.csv")

def _assert_csv_present():
    p = pathlib.Path(ACTUAL_CSV_PATH)
    if not p.exists():
        pytest.skip(f"CSV not found at {ACTUAL_CSV_PATH}. Set US_TICKERS_CSV env var to your real file.")

def test_norm():
    """Test the _norm function."""
    assert _norm("Apple Inc.") == "apple inc"
    assert _norm("Microsoft Corp.") == "microsoft corp"
    assert _norm("Google!") == "google"
    assert _norm("  Alphabet Inc.  ") == "alphabet inc"
    assert _norm("") == ""

def test_load_rows():
    """Test the _load_rows function with the actual CSV file."""
    # Ensure the file exists
    assert os.path.exists(ACTUAL_CSV_PATH), f"CSV file not found at {ACTUAL_CSV_PATH}"

    # Load rows from the actual file
    rows = _load_rows()
    assert len(rows) > 0, "No rows found in the CSV file."

    # Check the structure of the first row
    first_row = rows[0]
    assert "ticker" in first_row
    assert "company_name" in first_row
    assert "exchange" in first_row
    assert "aliases" in first_row

def test_build_index():
    """Test the _build_index function with the actual CSV file."""
    by_ticker, name_index, alias_index = _build_index()

    # Ensure the index is not empty
    assert len(by_ticker) > 0, "by_ticker index is empty."
    assert len(name_index) > 0, "name_index is empty."
    assert len(alias_index) > 0, "alias_index is empty."

    # Check for a specific ticker (e.g., AAPL)
    if "AAPL" in by_ticker:
        assert by_ticker["AAPL"]["company_name"] == "Apple Inc."

def test_resolve_us_ticker_basic():
    """Test the resolve_us_ticker_basic function with the actual CSV file."""
    # Valid ticker
    result = resolve_us_ticker_basic("AAPL")
    if result["status"] == "ok":
        assert result["ticker"] == "AAPL"
        assert result["source"] == "ticker"
        assert "meta" in result
        assert result["meta"]["company_name"] == "Apple Inc."

    # Exact company name
    result = resolve_us_ticker_basic("Apple Inc.")
    if result["status"] == "ok":
        assert result["ticker"] == "AAPL"
        assert result["source"] == "exact"

    # Alias match
    result = resolve_us_ticker_basic("Apple Computers")
    if result["status"] == "ok":
        assert result["ticker"] == "AAPL"
        assert result["source"] == "alias"

    # Invalid ticker
    result = resolve_us_ticker_basic("INVALID")
    assert result == {"status": "not_found"}

    # Empty query
    result = resolve_us_ticker_basic("")
    assert result == {"status": "not_found"}

    # None query
    result = resolve_us_ticker_basic(None)
    assert result == {"status": "not_found"}