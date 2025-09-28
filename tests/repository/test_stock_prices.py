import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from unittest.mock import patch, MagicMock
from datetime import date
from src.repository.stock_prices import OhlcvRepository

@pytest.fixture
def ohlcv_repo():
    """Fixture to create an instance of OhlcvRepository."""
    return OhlcvRepository()

@patch("src.repository.stock_prices.DatabaseConfig.get_connection")
def test_add_or_update_ohlcv(mock_get_connection, ohlcv_repo):
    """Test the add_or_update_ohlcv method."""
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Test data
    symbol = "AAPL"
    rows = [
        {
            "date": date(2025, 9, 28),
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 154.0,
            "adjusted_close": 154.0,
            "volume": 1000000,
        }
    ]

    # Call the method
    ohlcv_repo.add_or_update_ohlcv(symbol, rows)

    # Assertions
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("src.repository.stock_prices.DatabaseConfig.get_connection")
def test_get_range(mock_get_connection, ohlcv_repo):
    """Test the get_range method."""
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the cursor's fetchall method
    mock_cursor.fetchall.return_value = [
        {
            "symbol": "AAPL",
            "date": date(2025, 9, 28),
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "close": 154.0,
            "adjusted_close": 154.0,
            "volume": 1000000,
        }
    ]

    # Call the method
    result = ohlcv_repo.get_range("AAPL", date(2025, 9, 1), date(2025, 9, 30))

    # Assertions
    mock_cursor.execute.assert_called_once()
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("src.repository.stock_prices.DatabaseConfig.get_connection")
def test_get_last_entry_date(mock_get_connection, ohlcv_repo):
    """Test the get_last_entry_date method."""
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the cursor's fetchone method
    mock_cursor.fetchone.return_value = [date(2025, 9, 28)]

    # Call the method
    result = ohlcv_repo.get_last_entry_date("AAPL")

    # Assertions
    mock_cursor.execute.assert_called_once()
    assert result == date(2025, 9, 28)
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("src.repository.stock_prices.DatabaseConfig.get_connection")
def test_delete_symbol(mock_get_connection, ohlcv_repo):
    """Test the delete_symbol method."""
    # Mock the database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Call the method
    ohlcv_repo.delete_symbol("AAPL")

    # Assertions
    mock_cursor.execute.assert_called_once_with("DELETE FROM ohlcv_daily WHERE symbol = %s;", ("AAPL",))
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()