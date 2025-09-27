import pytest
import os, sys
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from unittest.mock import patch, MagicMock
from src.models.alpha_vintage_api import av_symbol_search, av_time_series_daily, get_av_daily_data
import datetime
from dotenv import load_dotenv
load_dotenv()

# Retrieve environment variables
ALPHA_VINTAGE_API_KEY = os.getenv("ALPHA_VINTAGE_API_KEY")  # Replace with a default for testing
ALPHA_VINTAGE_API_URL = os.getenv("ALPHA_VINTAGE_API_URL")  # Replace with a default for testing

@patch("src.models.alpha_vintage_api.requests.get")
def test_av_symbol_search(mock_get):
    """
    Test the av_symbol_search function with mocked API responses.
    """
    # Mock response data
    mock_response_data = {
        "bestMatches": [
            {
                "1. symbol": "AAPL",
                "2. name": "Apple Inc.",
                "3. type": "Equity",
                "4. region": "United States",
                "8. currency": "USD",
                "9. matchScore": "0.95",
            },
            {
                "1. symbol": "AAPL.L",
                "2. name": "Apple Inc.",
                "3. type": "Equity",
                "4. region": "United Kingdom",
                "8. currency": "GBP",
                "9. matchScore": "0.90",
            },
        ]
    }

    # Configure the mock to return the mock response data
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Call the function
    query = "AAPL"
    result = av_symbol_search(query, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)

    # Assertions
    assert result["symbol"] == "AAPL"
    assert result["name"] == "Apple Inc."
    assert result["type"] == "Equity"
    assert result["region"] == "United States"
    assert result["currency"] == "USD"
    assert result["matchScore"] == 0.95
    assert "raw" in result

    # Ensure the API was called with the correct parameters
    mock_get.assert_called_once_with(
        ALPHA_VINTAGE_API_URL,
        params={
            "function": "SYMBOL_SEARCH",
            "keywords": query,
            "apikey": ALPHA_VINTAGE_API_KEY,
        },
        timeout=15,
    )

from src.models.alpha_vintage_api import av_symbol_search

# ----- Marks to separate slow/network tests -----
pytestmark = [pytest.mark.integration, pytest.mark.network]

# def test_live_av_symbol_search_happy_path():
#     """
#     Live test against Alpha Vantage: verifies basic contract without hard-coding vendor result order.
#     """

#     # Check if the API key is set
#     if not ALPHA_VINTAGE_API_KEY:
#         pytest.fail("API key not set. Set APLHA_VINTAGE_API_KEY to run this test.")

#     # Call the function
#     result = av_symbol_search("AAPL", ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)

#     # Assertions
#     for k in ("symbol", "name", "type", "region", "currency", "matchScore", "raw"):
#         assert k in result, f"Missing key: {k}"
#         print(f"{k}: {result[k]}")

#     # Types
#     assert isinstance(result["symbol"], str) and result["symbol"], "symbol should be non-empty str"
#     assert isinstance(result["name"], str) and result["name"], "name should be non-empty str"
#     assert isinstance(result["type"], str) and result["type"], "type should be non-empty str"
#     assert isinstance(result["region"], str) and result["region"], "region should be non-empty str"
#     assert isinstance(result["currency"], str) and result["currency"], "currency should be non-empty str"
#     assert isinstance(result["matchScore"], float), "matchScore should be float"
#     assert isinstance(result["raw"], dict), "raw should contain original match dict"

#     # Reasonable value checks
#     assert 0.0 <= result["matchScore"] <= 1.0
#     assert re.search(r"apple", result["name"], re.IGNORECASE), f"name didn’t look like Apple: {result['name']}"
#     assert len(result["region"]) > 0
#     assert result["currency"] in {"USD", "GBP", "CAD", "EUR"}

def test_live_av_symbol_search_no_match_raises():
    """
    Live test negative case: a nonsense query should raise RuntimeError (no bestMatches).
    """


    # Check if the API key is set
    if not ALPHA_VINTAGE_API_KEY:
        pytest.fail("API key not set. Set APLHA_VINTAGE_API_KEY to run this test.")

    # Call the function with nonsense data
    nonsense = "zzzzzzzzzz-not-a-real-company-zzzzzzzzzz"
    with pytest.raises(RuntimeError):
        av_symbol_search(nonsense, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
pytest.mark.skip(reason="Skipping live test to avooid getting data again and again. It is working fine.")
def test_av_time_series_daily_happy_path():
    """
    Live test against Alpha Vantage TIME_SERIES_DAILY_ADJUSTED endpoint.
    """

    # Check if the API key is set
    if not ALPHA_VINTAGE_API_KEY:
        pytest.fail("API key not set. Set ALPHA_VINTAGE_API_KEY to run this test.")
    ticker = "AAPL"
    result = av_time_series_daily(ticker, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
    # print result 
    print(result)
    # Assertions
    assert "meta" in result and isinstance(result["meta"], dict), "meta should be present and a dict"
    assert "Monthly Time Series" in result and isinstance(result["Monthly Time Series"], dict), "time_series should be present and a dict"
    assert len(result["Monthly Time Series"]) > 0, "time_series should have at least one entry"

def test_get_av_daily_data_happy_path():
    """
    Test the get_av_daily_data wrapper function.
    """

    # Check if the API key is set
    if not ALPHA_VINTAGE_API_KEY:
        pytest.fail("API key not set. Set ALPHA_VINTAGE_API_KEY to run this test.")
    ticker = "AAPL"
    result = get_av_daily_data(ticker, ALPHA_VINTAGE_API_URL, ALPHA_VINTAGE_API_KEY)
    # print result
    print(result)
    # Assertions
    assert "meta" in result and isinstance(result["meta"], dict), "meta should be present and a dict"

    