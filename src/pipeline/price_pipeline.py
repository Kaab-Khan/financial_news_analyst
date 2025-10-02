import os
from src.models.alpha_vintage_api import get_av_daily_data
from src.service.pre_processing import (
    filter_ohlcv_by_range,
    aggregate_price_change,
    format_av_daily_data,
)
from src.agent.us_resolver import resolve_us_ticker_basic as resolve_ticker
import time
from datetime import datetime
from logging_config import logger


from dotenv import load_dotenv

load_dotenv()


def price_pipeline(ticker, date_from, date_to, api_key=None, api_url=None):
    logger.debug(
        f"price_pipeline called with ticker: {ticker}, start_date: {date_from}, end_date: {date_to}"
    )
    av_api_key = api_key or os.getenv("ALPHA_VINTAGE_API_KEY")
    av_api_url = api_url or os.getenv("ALPHA_VINTAGE_API_URL")
    if not av_api_key or not av_api_url:
        raise ValueError(
            "Alpha Vantage API key or URL not set in environment variables."
        )
    resolved_ticker = resolve_ticker(ticker)
    logger.debug(f"Resolved ticker: {resolved_ticker}")
    ticker_to_search = (
        resolved_ticker.get("ticker")
        if isinstance(resolved_ticker, dict)
        else str(resolved_ticker)
    ).upper()

    # ticker_to_search = av_symbol_search(resolved_ticker, av_api_url, av_api_key)
    logger.debug(f"AlphaVantage symbol search result: {ticker_to_search}")

    delay = 5  # to respect rate limits
    time.sleep(delay)
    av_daily_data = get_av_daily_data(ticker_to_search, av_api_url, av_api_key)
    logger.debug(f"Got {len(av_daily_data)} days of data for {ticker_to_search}")
    formatted_daily_data = format_av_daily_data(av_daily_data)
    # Convert start_date and end_date to datetime.date
    start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
    end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

    result = filter_ohlcv_by_range(formatted_daily_data, start_date, end_date)
    percentage_change = aggregate_price_change(result)
    _percent_change = (
        percentage_change["percentage_change"] if percentage_change else 0.0
    )
    logger.debug(
        f"price_pipeline result: {{'first_day': {result[0]['date'] if result else None}, 'first_price': {result[0]['close'] if result else None}, 'last_day': {result[-1]['date'] if result else None}, 'last_price': {result[-1]['close'] if result else None}, 'percentage_change': {_percent_change}}}"
    )
    return {
        "first_day": result[0]["date"] if result else None,
        "first_price": result[0]["close"] if result else None,
        "last_day": result[-1]["date"] if result else None,
        "last_price": result[-1]["close"] if result else None,
        "percentage_change": _percent_change,
    }
